from fastapi import APIRouter, Depends
from app.core.soap_client import call_xfi00310
from app.core.auth import get_current_user
from app.core.mssql import get_internal_contacts

router = APIRouter()


def _first(val: str) -> str:
    """'|' 구분자로 이어진 값에서 첫 번째 값만 추출"""
    if not val:
        return ""
    return str(val).split("|")[0].strip()


def _split_pipe(val: str) -> list:
    """'|' 구분자로 이어진 값을 리스트로 분리 (빈 항목 제거)"""
    if not val:
        return []
    return [v.strip() for v in str(val).split("|") if v.strip()]


@router.get("/list")
def read_contacts(current_user=Depends(get_current_user)):
    """
    담당자 연락처를 가져옵니다 (내부 MSSQL + SAP 연동).
    내부 DB 데이터를 우선적으로 상단에 배치합니다.
    SAP 응답: NAME/DEPT/POSI/TEL 등이 '|'로 구분된 값으로 오며, 
    PART(업무명)/COMT(업무설명)는 단일 업무 정보입니다.
    """
    # ── 1. 내부 MSSQL 연락처 조회 ──────────────────────────────
    internal_data = get_internal_contacts()
    formatted_internal = []
    for c in internal_data:
        task_name = c.get('TASK') or ""
        task_desc = c.get('REMARK') or ""
        tasks = []
        if task_name:
            tasks.append({"name": task_name, "desc": task_desc})
        formatted_internal.append({
            "DIVISION": c.get('DIVISION') or "",
            "TITLE":    c.get('TITLE') or "",
            "NAME":     c.get('NAME') or "",
            "TEL":      c.get('TEL') or "",
            "EMAIL":    c.get('EMAIL') or "",
            "WORK":     c.get('REMARK') or "업무",
            "TASKS":    tasks,
            "IS_INTERNAL": True
        })

    # ── 2. SAP 담당자 연락처 조회 (XFI00310) ────────────────────
    sap_contacts = []
    params = {"PERNR": current_user.target_pernr}
    try:
        result = call_xfi00310(params)
        print(f"[DEBUG SAP] result type={type(result)}")

        # SAP 응답이 list 혹은 dict 안의 list
        raw_list = []
        if isinstance(result, list):
            raw_list = result
        elif isinstance(result, dict):
            # 알려진 키 우선 탐색
            for key in ("ZFIXT405", "ET_DATA", "T_DATA", "ITEM", "RESULT"):
                if key in result:
                    val = result[key]
                    raw_list = val if isinstance(val, list) else ([val] if isinstance(val, dict) else [])
                    print(f"[DEBUG SAP] found key='{key}', rows={len(raw_list)}")
                    break
            # 위 키 없으면 첫 번째 list 값
            if not raw_list:
                for k, v in result.items():
                    if isinstance(v, list) and v:
                        raw_list = v
                        print(f"[DEBUG SAP] fallback key='{k}', rows={len(raw_list)}")
                        break
                    elif isinstance(v, dict) and v:
                        raw_list = [v]
                        break

        if raw_list:
            print(f"[DEBUG SAP] first row keys={list(raw_list[0].keys()) if isinstance(raw_list[0], dict) else 'N/A'}")
            print(f"[DEBUG SAP] first row={raw_list[0]}")

        # ── SAP 각 행 변환 ──
        # 실제 필드명: NAME, POSI(직위), DEPT(소속), TEL, PART(업무명), COMT(업무설명), WORK(업무구분)
        for s in raw_list:
            if not isinstance(s, dict):
                continue

            # '|' 구분값 → 첫 번째만 사용 (중복 방지)
            name     = _first(s.get('NAME') or s.get('ENAME') or "")
            division = _first(s.get('DEPT') or s.get('DIVISION') or s.get('ORGEH') or "")
            title    = _first(s.get('POSI') or s.get('TITLE') or s.get('PLANS') or "")
            tel      = _first(s.get('TEL') or s.get('TELNO') or "")
            email    = _first(s.get('EMAIL') or "")
            work_badge = _first(s.get('WORK') or "업무")

            # 업무명/설명은 단일 값
            part_name = str(s.get('PART') or s.get('TASK') or s.get('SYSNA') or "").strip()
            comt_desc = str(s.get('COMT') or s.get('SYSTEM_DESC') or s.get('SYSBS') or "").strip()
            if not comt_desc:
                comt_desc = part_name

            if not name:
                continue

            tasks = []
            if part_name:
                tasks.append({"name": part_name, "desc": comt_desc})

            sap_contacts.append({
                "DIVISION": division,
                "TITLE":    title,
                "NAME":     name,
                "TEL":      tel,
                "EMAIL":    email,
                "WORK":     work_badge,
                "TASKS":    tasks,
                "IS_INTERNAL": False
            })

        print(f"[DEBUG SAP] parsed contacts: {len(sap_contacts)}")

    except Exception as e:
        print(f"SAP Contact Error: {e}")
        import traceback
        traceback.print_exc()

    # ── 3. 병합 반환 ─────────────────────────────────────────────
    return formatted_internal + sap_contacts
