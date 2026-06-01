from fastapi import APIRouter, Depends, HTTPException
from app.core.soap_client import call_xfi00310
from app.core.auth import get_current_user

router = APIRouter()

from app.core.mssql import get_internal_contacts

@router.get("/list")
def read_contacts(current_user = Depends(get_current_user)):
    """
    담당자 연락처를 가져옵니다 (내부 MSSQL + SAP 연동).
    내부 DB 데이터를 우선적으로 상단에 배치합니다.
    """
    # 1. 내부 MSSQL 연락처 조회
    internal_data = get_internal_contacts()
    formatted_internal = []
    for c in internal_data:
        formatted_internal.append({
            "DIVISION": c['DIVISION'],
            "TITLE": c.get('TITLE') or "",
            "NAME": c['NAME'],
            "TEL": c['TEL'],
            "EMAIL": c.get('EMAIL') or "",
            "TASK": c.get('TASK') or "",
            "REMARK": c.get('REMARK') or "",
            "IS_INTERNAL": True
        })

    # 2. SAP 담당자 연락처 조회
    sap_contacts = []
    params = {"PERNR": current_user.target_pernr}
    try:
        result = call_xfi00310(params)
        if result and isinstance(result, dict) and "ZFIXT405" in result:
            sap_contacts = result["ZFIXT405"] or []
        elif isinstance(result, list):
            sap_contacts = result
    except Exception as e:
        print(f"SAP Contact Error: {e}")

    # 3. 데이터 병합
    return formatted_internal + sap_contacts
