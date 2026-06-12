# 연락처 API

**Base path:** `/api/v1/contacts`  
**파일:** `backend/app/api/contact.py`  
**데이터 소스:** MSSQL `MFS_CONTACTS` + SAP XFI00310 (하이브리드)

> JWT 인증 필요

---

## GET /list

내부 담당자 연락처 목록 조회.

### 내부 처리

```python
# MSSQL 연락처 조회
internal = mssql.get_internal_contacts()
# → SELECT * FROM MFS_CONTACTS ORDER BY DIVISION, NAME

# SAP 연락처 조회
sap_contacts = soap_client.call_xfi00310()
```

### 응답

```json
[
  {
    "source": "internal",
    "DIVISION": "IT본부",
    "TITLE": "과장",
    "NAME": "홍길동",
    "TEL": "02-1234-5678",
    "EMAIL": "hong@hhi.co.kr",
    "TASK": "시스템 개발"
  }
]
```

---

## MSSQL 스키마

```sql
MFS_CONTACTS (
    ID        INT IDENTITY PRIMARY KEY,
    DIVISION  NVARCHAR(100),  -- 부서/팀명
    TITLE     NVARCHAR(50),   -- 직급
    NAME      NVARCHAR(50),   -- 이름
    TEL       VARCHAR(30),    -- 전화번호
    EMAIL     VARCHAR(100),   -- 이메일
    TASK      NVARCHAR(200),  -- 담당 업무
    REMARK    NVARCHAR(500)   -- 비고
)
```

연락처 CRUD는 [관리자 API](admin.md)를 통해 처리된다.
