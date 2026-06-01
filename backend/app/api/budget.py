from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.soap_client import call_xfi00290
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/budget")
def read_budget(
    bukrs: str = "",
    objnr: str = "",
    objty: str = "",
    kstar: str = "",
    gjahr: str = "",
    system: str = "",
    callsys: str = "M",
    current_user = Depends(get_current_user)
):
    """SAP XFI00290 서비스를 호출하여 예산 정보를 가져옵니다."""
    # JWT Token 안의 target_pernr를 전역 할당 (대리 사번 동적 처리)
    pernr = current_user.target_pernr

    params = {
        "PI_BUKRS": bukrs if bukrs else "",
        "PI_PERNR": pernr,
        "PI_OBJNR": objnr if objnr else "",
        "PI_OBJTY": objty if objty else "",
        "PI_KSTAR": kstar if kstar else "",
        "PI_GJAHR": gjahr if gjahr else "2026",
        "I_SYSTEM": system if system else "M",
        "PI_CALLSYS": callsys if callsys else "P"
    }
    
    try:
        result = call_xfi00290(params)
        return result if result else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail="예산 조회 중 서버 오류가 발생했습니다.")
