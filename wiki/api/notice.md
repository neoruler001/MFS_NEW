# 공지사항 API

**Base path:** `/api/v1/notices`  
**파일:** `backend/app/api/notice.py`  
**데이터 소스:** MSSQL `MFS_NOTICES` + SAP XFI00320 (하이브리드)

> JWT 인증 필요

---

## GET /notices

공지사항 목록 조회. 내부(MSSQL)와 SAP 공지를 병합하여 반환한다.

### 내부 처리

```python
async def read_notices(current_user=Depends(get_current_user)):
    # 1. MSSQL 내부 공지 조회
    internal = mssql.get_internal_notices()
    # → SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC

    # 2. SAP 공지 조회
    sap_notices = soap_client.call_xfi00320()

    # 3. 내부 공지를 앞에 배치하여 병합
    return internal + sap_notices
```

### 응답

```json
[
  {
    "source": "internal",
    "ID": 1,
    "SUBJECT": "시스템 점검 안내",
    "CONTENT": "...",
    "ERDAT": "20260610",
    "ERNAM": "admin"
  },
  {
    "source": "sap",
    "SUBJECT": "SAP 공지사항",
    ...
  }
]
```

---

## MSSQL 스키마

```sql
MFS_NOTICES (
    ID       INT IDENTITY PRIMARY KEY,
    SUBJECT  NVARCHAR,
    CONTENT  NVARCHAR,
    ERDAT    VARCHAR(8),   -- 생성일 YYYYMMDD
    ERZET    VARCHAR(6),   -- 생성시각 HHMMSS
    ERNAM    VARCHAR(20)   -- 작성자 사번
)
```

공지 CRUD는 [관리자 API](admin.md)를 통해 처리된다.
