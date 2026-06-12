# 데이터베이스

---

## MSSQL (운영 DB)

**접속:** `10.100.37.178:3218`  
**드라이버:** pymssql (직접 연결, 커넥션 풀 없음)  
**연결 팩토리:** `backend/app/core/mssql.py` → `get_mssql_connection()`

> **⚠️ 커넥션 풀 없음** — 요청마다 신규 연결 생성. 부하 증가 시 성능 저하 위험.

---

### MFS_USERS

시스템 인증 및 권한 관리 테이블.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `EMP_NO` | VARCHAR (PK) | 사번 |
| `KOR_NM` | NVARCHAR | 한국어 성명 |
| `PASSWORD_HASH` | VARCHAR | pbkdf2_sha256 해시 |
| `IS_ADMIN` | BIT | 관리자 여부 |
| `CREATED_AT` | DATETIME | 등록일시 |

**사용 쿼리:**

```sql
-- 인증
SELECT * FROM MFS_USERS WHERE EMP_NO = %s

-- 목록
SELECT EMP_NO, KOR_NM, IS_ADMIN, CREATED_AT
FROM MFS_USERS ORDER BY CREATED_AT DESC

-- 등록
INSERT INTO MFS_USERS (EMP_NO, KOR_NM, PASSWORD_HASH, IS_ADMIN)
VALUES (%s, %s, %s, %s)

-- 삭제
DELETE FROM MFS_USERS WHERE EMP_NO = %s
```

---

### MFS_NOTICES

내부 공지사항 테이블.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `ID` | INT IDENTITY (PK) | 공지 ID |
| `SUBJECT` | NVARCHAR | 제목 |
| `CONTENT` | NVARCHAR | 내용 |
| `ERDAT` | VARCHAR(8) | 생성일 (YYYYMMDD) |
| `ERZET` | VARCHAR(6) | 생성시각 (HHMMSS) |
| `ERNAM` | VARCHAR(20) | 작성자 사번 |

**사용 쿼리:**

```sql
-- 목록 조회
SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC

-- 등록
INSERT INTO MFS_NOTICES (SUBJECT, CONTENT, ERDAT, ERZET, ERNAM)
VALUES (%s, %s, %s, %s, %s)

-- 수정
UPDATE MFS_NOTICES SET SUBJECT=%s, CONTENT=%s WHERE ID=%s

-- 삭제
DELETE FROM MFS_NOTICES WHERE ID=%s
```

---

### MFS_CONTACTS

내부 담당자 연락처 테이블.

| 컬럼 | 타입 | 설명 |
|------|------|------|
| `ID` | INT IDENTITY (PK) | 연락처 ID |
| `DIVISION` | NVARCHAR(100) | 부서/팀명 |
| `TITLE` | NVARCHAR(50) | 직급 |
| `NAME` | NVARCHAR(50) | 이름 |
| `TEL` | VARCHAR(30) | 전화번호 |
| `EMAIL` | VARCHAR(100) | 이메일 |
| `TASK` | NVARCHAR(200) | 담당 업무 |
| `REMARK` | NVARCHAR(500) | 비고 |

**정렬 기준:** `ORDER BY DIVISION, NAME`

---

### SUPPORT.DBO.ALL_AMSTM_VIEW

인사 정보 뷰 (크로스 DB 조회).

| 컬럼 | 설명 |
|------|------|
| `COMPANY` | 회사 코드 |
| `COMPANY_NM` | 회사명 |
| `EMP_NO` | 사번 |
| `KOR_NM` | 한국어 성명 |
| `OFFI_RES_NM` | 직책명 |
| `HLD_OFFI_GBN` | 재직 구분 (`'3'` = 퇴직) |

**사용 쿼리:**

```sql
SELECT COMPANY, COMPANY_NM, EMP_NO, KOR_NM, OFFI_RES_NM
FROM SUPPORT.DBO.ALL_AMSTM_VIEW
WHERE HLD_OFFI_GBN <> '3'   -- 재직자만
  AND EMP_NO = %s
```

---

## MSSQL 쿼리 패턴

```python
# SELECT 패턴
def get_internal_notices():
    conn = get_mssql_connection()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute("SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC")
        return cursor.fetchall()
    finally:
        conn.close()

# DML 패턴 (트랜잭션 포함)
def create_internal_notice(subject, content, erdat, erzet, ernam):
    conn = get_mssql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO MFS_NOTICES (SUBJECT, CONTENT, ERDAT, ERZET, ERNAM) VALUES (%s,%s,%s,%s,%s)",
            (subject, content, erdat, erzet, ernam)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
```

> **파라미터 바인딩:** pymssql `%s` 자리표시자 사용 → SQL 인젝션 방어됨.  
> **안티패턴 예외:** `admin.py`의 UPDATE 동적 쿼리는 f-string 조합 — 내부 신뢰 데이터에만 한정 사용.

---

## SQLite (로컬 세션 DB)

**파일:** `backend/mfs.db`  
**드라이버:** SQLAlchemy ORM  
**상태:** 실질적 활용 낮음 — `get_current_user`에서 조회하나 None이면 가상 User 객체로 우회

**ORM 모델 (`backend/app/models/models.py`):**

| 클래스 | 테이블 | 상태 |
|--------|--------|------|
| `User` | `users` | 세션 관리 (실사용 제한적) |
| `CardUsage` | `card_usages` | **데드 코드** — SAP로 대체 |
| `Notice` | `notices` | **데드 코드** — MSSQL로 대체 |

---

## 레거시 파일 (건드리지 말 것)

| 파일 | 상태 | 이유 |
|------|------|------|
| `backend/app/db/mssql_db.py` | 미사용 | `core/mssql.py`로 대체 |
| `models/models.py` `CardUsage`, `Notice` | 미사용 | SAP/MSSQL로 대체 |
| `schemas/schemas.py` `CardUsageSchema`, `NoticeSchema`, `TokenData` | 미사용 | 사용처 없음 |
