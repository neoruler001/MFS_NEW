# 연락처 API — /api/v1/contacts

**파일**: `backend/app/api/contact.py`  
**데이터 소스**: MSSQL MFS_CONTACTS + SAP XFI00310 (병합)

---

## GET /api/v1/contacts/list

내부 연락처(MSSQL)와 SAP 연락처를 병합하여 반환합니다.

**인증 필요**: 예

### 응답 (200 OK)

```json
[
  {
    "ID": 1,
    "DIVISION": "재경팀",
    "TITLE": "팀장",
    "NAME": "홍길동",
    "TEL": "010-1234-5678",
    "EMAIL": "hong@hhi.co.kr",
    "TASK": "법인카드 관리",
    "REMARK": ""
  }
]
```

### 처리 흐름

```
read_contacts()
  → get_current_user()
  → mssql.get_internal_contacts()            [MFS_CONTACTS 조회]
  → soap_client.call_xfi00310({PERNR: ...}) [SAP 연락처 조회]
  ← 내부 연락처 + SAP 연락처 병합 반환
```

### 데이터베이스 쿼리

```sql
SELECT * FROM MFS_CONTACTS ORDER BY DIVISION, NAME
```

### SAP XFI00310 응답

> ⚠️ 응답 키가 동적입니다 (`ZFIXT405`, `ET_DATA`, `T_DATA` 중 런타임 탐색).
