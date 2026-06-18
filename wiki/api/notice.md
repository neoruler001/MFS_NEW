# 공지사항 API — /api/v1/notices

**파일**: `backend/app/api/notice.py`  
**데이터 소스**: MSSQL MFS_NOTICES + SAP XFI00320 (병합)

---

## GET /api/v1/notices/notices

내부 공지사항(MSSQL)과 SAP 공지사항을 병합하여 반환합니다.

**인증 필요**: 예

### 응답 (200 OK)

```json
[
  {
    "source": "internal",
    "SUBJECT": "6월 법인카드 마감 안내",
    "CONTENT": "6월 30일까지 비용처리를 완료해 주세요.",
    "ERDAT": "20260615",
    "ERZET": "100000",
    "ERNAM": "관리자"
  },
  {
    "ZFIXT405_1": "SAP 공지 제목",
    ...
  }
]
```

내부 공지사항이 앞에, SAP 공지사항이 뒤에 배치됩니다.

### 처리 흐름

```
read_notices()
  → get_current_user()                      [JWT 검증]
  → mssql.get_internal_notices()            [MFS_NOTICES 조회]
  → soap_client.call_xfi00320({PERNR: ...}) [SAP 공지 조회]
  ← 내부 공지 + SAP 공지 병합 반환
```

SAP 조회 실패 시 내부 공지사항만 반환됩니다 (try/except 처리).

### 데이터베이스 쿼리

```sql
SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC
```

### SAP XFI00320 응답

```json
{
  "ZFIXT405_1": [
    {
      "MANDT": "100",
      "ZFITEXT": "SAP 공지 내용..."
    }
  ]
}
```
