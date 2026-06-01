from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.core.soap_client import call_xfi00250, call_xfi00260, call_xfi00270, call_xfi00280
from app.core.auth import get_current_user

router = APIRouter()

# ──────────────────────────────────────────────────────
# Pydantic 스키마 정의
# ──────────────────────────────────────────────────────

class CardItemSchema(BaseModel):
    """XFI00260 비용처리용 단일 카드 항목"""
    BUKRS: str
    APPR_DATE: str       # 승인일자 (BUDAT로도 사용)
    CARD_NUMC: str
    APPR_NUMC: str
    CANC_FLAG: str = ""
    SEQN_NUMC: str = ""
    DOCPR: str           # 업무코드
    PERNR: str           # 카드소유자 사번 (PERNR_O로 매핑)
    SGTXT: str = ""      # 적요

class ProcessRequestSchema(BaseModel):
    items: List[CardItemSchema]

class CancelItemSchema(BaseModel):
    """XFI00270 처리취소용 단일 카드 항목"""
    BUKRS: str
    BELNR: str = ""     # 전표번호
    GJAHR: str = ""     # 회계연도
    CARD_NUMC: str
    APPR_DATE: str
    APPR_NUMC: str
    CANC_FLAG: str = ""
    SEQN_NUMC: str = ""

class CancelRequestSchema(BaseModel):
    items: List[CancelItemSchema]

# ──────────────────────────────────────────────────────
# 엔드포인트: 이용내역 조회
# ──────────────────────────────────────────────────────

@router.get("/usages")
def read_card_usages(
    card_num: str = "", 
    fr_date: str = "", 
    to_date: str = "",
    pi_status: str = "A",
    current_user = Depends(get_current_user)
):
    """SAP XFI00250 서비스를 호출하여 카드 이용내역을 가져옵니다."""
    # JWT에 할당된 동적 대리 사번 사용
    pernr = current_user.target_pernr

    # 디폴트 기간: 한 달 전 ~ 오늘
    today = datetime.now()
    default_fr_date = (today - timedelta(days=30)).strftime("%Y%m%d")
    default_to_date = today.strftime("%Y%m%d")
    
    params = {
        "PI_CARD_NUMC": card_num if card_num else "",
        "PI_FR_DATE": fr_date.replace("-", "") if fr_date else default_fr_date,
        "PI_TO_DATE": to_date.replace("-", "") if to_date else default_to_date,
        "PI_STATUS": pi_status,
        "PI_PERNR_O": pernr,
        "PI_PERNR_R": pernr,
        "PI_CALLSYS": "P"
    }
    
    print(f"[DEBUG] Calling XFI00250 with: {params}")
    try:
        result = call_xfi00250(params)
        if result:
            rows = result.get('TE_CARD_USE', [])
            # 정렬 로직: 최근 사용일자(APPR_DATE) 기준 내림차순(최신순)
            rows.sort(key=lambda x: x.get('APPR_DATE', ''), reverse=True)
            print(f"[DEBUG] SAP Success. Rows: {len(rows)}")
            if len(rows) > 0:
                print(f"[DEBUG] First row sample: {rows[0]}")
            return rows
        print("[DEBUG] SAP returned empty/None")
        return []
    except Exception as e:
        print(f"[DEBUG] API Error: {e}")
        raise HTTPException(status_code=500, detail="요청 처리 중 서버 오류가 발생했습니다.")

@router.get("/card-info")
def get_card_info(current_user = Depends(get_current_user)):
    params = {
        "PI_CARD_NUMC": "X",
        "PI_FR_DATE": "",
        "PI_TO_DATE": "",
        "PI_STATUS": "A",
        "PI_PERNR_O": "",
        "PI_PERNR_R": current_user.target_pernr,
        "PI_CALLSYS": "P"
    }
    try:
        result = call_xfi00250(params)
        return result.get('TE_CARD_INFO', []) if result else []
    except Exception as e:
        raise HTTPException(status_code=500, detail="요청 처리 중 서버 오류가 발생했습니다.")

# ──────────────────────────────────────────────────────
# 엔드포인트: 업무목록 조회 (비용처리 팝업 드롭다운)
# ──────────────────────────────────────────────────────

@router.get("/worklist")
def get_work_list(
    bukrs: str,
    current_user = Depends(get_current_user)
):
    """XFI00280: 비용처리 팝업용 업무목록(TE_TEMPLATE), 적요(TE_SGTXT), DOCPR별 적요(TE_DOCPR_SGTXT) 반환"""
    pernr = current_user.target_pernr
    try:
        result = call_xfi00280(bukrs=bukrs, pernr=pernr)
        return {
            "PE_RESULT": result.get("PE_RESULT", ""),
            "PE_MESSAGE": result.get("PE_MESSAGE", ""),
            "TE_TEMPLATE": result.get("TE_TEMPLATE", []) or [],
            "TE_SGTXT": result.get("TE_SGTXT", []) or [],
            "TE_DOCPR_SGTXT": result.get("TE_DOCPR_SGTXT", []) or [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="요청 처리 중 서버 오류가 발생했습니다.")

# ──────────────────────────────────────────────────────
# 엔드포인트: 비용처리 (XFI00260)
# ──────────────────────────────────────────────────────

@router.post("/process")
def process_expenses(
    req: ProcessRequestSchema,
    current_user = Depends(get_current_user)
):
    """XFI00260: 선택한 카드 이용내역을 비용처리(전표 생성)합니다.
    
    레거시 MF001.aspx.cs SetData1 동작과 동일:
    - STATUS=='A' (이미처리) → 프런트에서 사전 차단
    - STATUS=='D' (모바일처리불가) → 프런트에서 사전 차단
    - STATUS=='E' (호텔실적미수신) → 프런트에서 사전 차단
    """
    pernr_r = current_user.target_pernr

    # [보안] 입력 항목 수 제한 (과도한 배치 요청 방지)
    if len(req.items) == 0:
        raise HTTPException(status_code=400, detail="처리할 항목을 선택해주세요.")
    if len(req.items) > 100:
        raise HTTPException(status_code=400, detail="한 번에 최대 100건까지만 처리 가능합니다.")

    t_data = []
    for item in req.items:
        t_data.append({
            "BUKRS":     item.BUKRS,
            "BUDAT":     item.APPR_DATE,   # 레거시: BUDAT = APPR_DATE (승인일자)
            "CARD_NUMC": item.CARD_NUMC,
            "APPR_DATE": item.APPR_DATE,
            "APPR_NUMC": item.APPR_NUMC,
            "CANC_FLAG": item.CANC_FLAG,
            "SEQN_NUMC": item.SEQN_NUMC,
            "DOCPR":     item.DOCPR,
            "PERNR_O":   item.PERNR,       # 카드소유자 사번
            "PERNR_R":   pernr_r,          # 처리자(로그인 사번)
            "SGTXT":     item.SGTXT,
            "MSG_TYPE":  "",
            "MSG_TXT":   "",
        })

    try:
        result = call_xfi00260(items=t_data)
        return {
            "PE_RESULT": result.get("PE_RESULT", ""),
            "PE_MESSAGE": result.get("PE_MESSAGE", "처리가 완료되었습니다."),
            "T_DATA": result.get("T_DATA", []) or [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="요청 처리 중 서버 오류가 발생했습니다.")

# ──────────────────────────────────────────────────────
# 엔드포인트: 처리취소 (XFI00270)
# ──────────────────────────────────────────────────────

@router.post("/cancel")
def cancel_expenses(
    req: CancelRequestSchema,
    current_user = Depends(get_current_user)
):
    """XFI00270: 선택한 카드 이용내역의 비용처리를 취소(전표 취소)합니다.
    
    레거시 MF001.aspx.cs SetData2 동작과 동일:
    - STATUS=='B' (미처리) → 프런트에서 사전 차단 ("비용처리진행중인 내역만 처리취소 가능")
    - BUCOD.length > 0 (부대사업장) → 프런트에서 사전 차단
    """
    pernr = current_user.target_pernr

    # [보안] 입력 항목 수 제한
    if len(req.items) == 0:
        raise HTTPException(status_code=400, detail="취소할 항목을 선택해주세요.")
    if len(req.items) > 100:
        raise HTTPException(status_code=400, detail="한 번에 최대 100건까지만 처리 가능합니다.")

    t_data = []
    for item in req.items:
        t_data.append({
            "BUKRS":     item.BUKRS,
            "BELNR":     item.BELNR,
            "GJAHR":     item.GJAHR,
            "CARD_NUMC": item.CARD_NUMC,
            "APPR_DATE": item.APPR_DATE,
            "APPR_NUMC": item.APPR_NUMC,
            "CANC_FLAG": item.CANC_FLAG,
            "SEQN_NUMC": item.SEQN_NUMC,
            "PERNR":     pernr,            # 처리자(로그인 사번) 전달
            "MSG_TYPE":  "",
            "MSG_TXT":   "",
        })

    try:
        result = call_xfi00270(items=t_data)
        return {
            "PE_RESULT": result.get("PE_RESULT", ""),
            "PE_MESSAGE": result.get("PE_MESSAGE", "취소 처리가 완료되었습니다."),
            "T_DATA": result.get("T_DATA", []) or [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="요청 처리 중 서버 오류가 발생했습니다.")
