from fastapi import APIRouter, Depends
from app.db.mssql_db import fetch_mssql_notices
from app.core.soap_client import call_xfi00320
from app.core.auth import get_current_user

router = APIRouter()

from app.core.mssql import get_internal_notices

@router.get("/notices")
def read_notices(current_user = Depends(get_current_user)):
    """
    공지사항을 가져옵니다 (내부 MSSQL + SAP 연동).
    내부 DB 데이터를 우선적으로 상단에 배치합니다.
    """
    # 1. 내부 MSSQL 공지사항 조회
    internal_data = get_internal_notices()
    formatted_internal = []
    for n in internal_data:
        formatted_internal.append({
            "SUBJECT": f"[공지] {n['SUBJECT']}",
            "CONTENTS": n['CONTENT'],
            "ERDAT": n['ERDAT'],
            "ERZET": n['ERZET'],
            "ERNAM": n['ERNAM'],
            "IS_INTERNAL": True
        })

    # 2. SAP 공지사항 조회
    sap_notices = []
    params = {"PERNR": current_user.target_pernr}
    try:
        result = call_xfi00320(params)
        if result and isinstance(result, dict) and "ZFIXT405_1" in result:
            sap_notices = result["ZFIXT405_1"] or []
        elif isinstance(result, list):
            sap_notices = result
    except Exception as e:
        print(f"SAP Notice Error: {e}")

    # 3. 데이터 병합 (내부 데이터가 앞선 순서)
    return formatted_internal + sap_notices
