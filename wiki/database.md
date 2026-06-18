# 데이터베이스

## 데이터 접근 구조

프로젝트는 두 가지 DB 접근 방식을 혼용합니다:

| 방식 | 대상 | 사용 모듈 |
|------|------|---------|
| pymssql 직접 연결 | MSSQL (운영 DB) | `core/mssql.py` |
| SQLAlchemy ORM | SQLite (로컬 세션) | `db/session.py` |

> **실질적으로** MSSQL이 운영 DB입니다. SQLite는 인증 세션용으로만 존재하며 실사용이 매우 낮습니다.

---

## MSSQL 주요 테이블

### MFS_USERS — 시스템 사용자

| 컬럼 | 설명 |
|------|------|
| EMP_NO (PK) | 사번 (예: BP12345) |
| KOR_NM | 한국어 성명 |
| PASSWORD_HASH | pbkdf2_sha256 해시 |
| IS_ADMIN | 관리자 여부 (0/1) |
| CREATED_AT | 등록일시 |

### MFS_NOTICES — 내부 공지사항

| 컬럼 | 설명 |
|------|------|
| ID (PK) | 공지 ID (AUTO) |
| SUBJECT | 제목 |
| CONTENT | 내용 |
| ERDAT | 작성일 (YYYYMMDD) |
| ERZET | 작성시각 |
| ERNAM | 작성자 |

### MFS_CONTACTS — 내부 연락처

| 컬럼 | 설명 |
|------|------|
| ID (PK) | 연락처 ID (AUTO) |
| DIVISION | 부서 |
| TITLE | 직책 |
| NAME | 성명 |
| TEL | 전화번호 |
| EMAIL | 이메일 |
| TASK | 담당업무 |
| REMARK | 비고 |

### SUPPORT.DBO.ALL_AMSTM_VIEW — 인사 정보 (크로스 DB)

| 컬럼 | 설명 |
|------|------|
| EMP_NO | 사번 |
| KOR_NM | 한국어 성명 |
| COMPANY | 회사 코드 |
| COMPANY_NM | 회사명 |
| OFFI_RES_NM | 직책명 |
| HLD_OFFI_GBN | 재직구분 (≠'3' 조건으로 재직자 필터) |

> 이 뷰는 외부 SUPPORT DB의 크로스 DB 조회입니다. `SUPPORT.DBO.ALL_AMSTM_VIEW` 형식으로 접근합니다.

---

## SQL 목록

### SELECT 쿼리

| ID | 파일 | 테이블 | 용도 |
|----|------|--------|------|
| `mssql.get_mssql_user_info` | core/mssql.py | SUPPORT.DBO.ALL_AMSTM_VIEW | 사번 → 성명/회사 조회 |
| `mssql.authenticate_mssql_user` | core/mssql.py | MFS_USERS | 로그인 인증 |
| `mssql.get_internal_notices` | core/mssql.py | MFS_NOTICES | 내부 공지사항 목록 |
| `mssql.get_internal_contacts` | core/mssql.py | MFS_CONTACTS | 내부 연락처 목록 |
| `admin.list_users` | api/admin.py | MFS_USERS | 관리자 사용자 목록 |
| `admin.list_notices` | api/admin.py | MFS_NOTICES | 관리자 공지 목록 |
| `admin.list_contacts` | api/admin.py | MFS_CONTACTS | 관리자 연락처 목록 |

### DML 쿼리

| ID | 파일 | 테이블 | 타입 |
|----|------|--------|------|
| `admin.create_user` | api/admin.py | MFS_USERS | INSERT |
| `admin.update_user` | api/admin.py | MFS_USERS | UPDATE (동적 SET) |
| `admin.delete_user` | api/admin.py | MFS_USERS | DELETE |
| `admin.create_notice` | api/admin.py | MFS_NOTICES | INSERT |
| `admin.update_notice` | api/admin.py | MFS_NOTICES | UPDATE |
| `admin.delete_notice` | api/admin.py | MFS_NOTICES | DELETE |
| `admin.create_contact` | api/admin.py | MFS_CONTACTS | INSERT |
| `admin.update_contact` | api/admin.py | MFS_CONTACTS | UPDATE |
| `admin.delete_contact` | api/admin.py | MFS_CONTACTS | DELETE |

---

## MSSQL 접근 패턴

### 연결 생성

모든 MSSQL 접근은 `get_mssql_connection()`을 통해 연결을 얻습니다.

```python
# core/mssql.py
def get_mssql_connection():
    try:
        conn = pymssql.connect(
            server=settings.MSSQL_HOST,
            port=settings.MSSQL_PORT,
            user=settings.MSSQL_USER,
            password=settings.MSSQL_PASSWORD,
            charset='UTF-8',
            login_timeout=10
        )
        return conn
    except Exception as e:
        logging.error(f"[MSSQL Connection Error] {e}")
        return None  # None 반환 — 호출부에서 체크 필요
```

> 커넥션 풀 미사용 — 요청마다 신규 연결 생성. 부하 증가 시 성능 저하 위험이 있습니다.

### SELECT 패턴

```python
def get_internal_notices():
    conn = get_mssql_connection()
    if not conn: return []        # None 체크 필수
    try:
        cursor = conn.cursor(as_dict=True)   # dict 반환
        cursor.execute("SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC")
        return cursor.fetchall()
    finally:
        conn.close()              # 항상 close
```

### DML (INSERT/UPDATE/DELETE) 패턴

```python
conn = get_mssql_connection()
if not conn:
    raise HTTPException(status_code=500, detail="DB 연결 실패")
try:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO MFS_USERS (EMP_NO, KOR_NM, PASSWORD_HASH, IS_ADMIN) VALUES (%s, %s, %s, %s)",
        (user.emp_no.upper(), user.kor_nm, pwd_hash, 1 if user.is_admin else 0)
    )
    conn.commit()
    return {"message": "사용자가 등록되었습니다."}
except Exception as e:
    conn.rollback()               # 예외 시 롤백
    raise HTTPException(status_code=400, detail=str(e))
finally:
    conn.close()                  # 항상 close
```

### 파라미터 바인딩

모든 쿼리는 `%s` 플레이스홀더를 사용합니다. SQL 인젝션을 방지합니다.

```python
# 단일 파라미터 — 튜플로 감싸기 (콤마 필수)
cursor.execute("SELECT * FROM MFS_USERS WHERE EMP_NO = %s", (emp_no,))

# 다중 파라미터
cursor.execute(
    "INSERT INTO MFS_CONTACTS (DIVISION, NAME, TEL) VALUES (%s, %s, %s)",
    (division, name, tel)
)
```

---

## 트랜잭션 경계

| 패턴 | 위치 | 설명 |
|------|------|------|
| `commit()` | DML 성공 시 | `conn.commit()` |
| `rollback()` | 예외 발생 시 | `conn.rollback()` + `HTTPException` raise |
| `close()` | `finally` | 항상 연결 해제 |

명시적 트랜잭션: **5개** (admin.py의 사용자/공지/연락처 DML 작업)

---

## 주의사항

### 레거시 파일 — `backend/app/db/mssql_db.py`

이 파일은 레거시입니다. **신규 코드에서 사용 금지.**

- `core/mssql.py`와 `get_mssql_connection()` 중복 정의
- `fetch_mssql_notices()` — 호출처 없는 데드 코드
- `notice.py`에 import 구문만 남아있고 실제 호출 없음

```python
# 금지 — 레거시
from app.db.mssql_db import fetch_mssql_notices

# 올바른 import
from app.core.mssql import get_internal_notices
```

### 크로스 DB 쿼리

외부 인사 정보 조회 시 `SUPPORT.DBO.{뷰이름}` 형식으로 접근합니다.  
DB 접속 계정(`XB01`)에 SUPPORT DB 조회 권한이 부여되어 있어야 합니다.

```python
SELECT COMPANY, COMPANY_NM, EMP_NO, KOR_NM
FROM SUPPORT.DBO.ALL_AMSTM_VIEW
WHERE HLD_OFFI_GBN <> '3' AND EMP_NO = %s
```

`HLD_OFFI_GBN <> '3'` 조건이 재직자 필터입니다 (3 = 퇴직).
