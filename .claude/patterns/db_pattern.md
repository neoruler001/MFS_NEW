# DB Pattern — MFS MSSQL pymssql 쿼리 패턴

추출 시각: 2026-06-11
샘플 파일 수: 3 (core/mssql.py, api/admin.py, core/config.py)
신뢰도: HIGH (DML 패턴 100% 일관)

---

## 올바른 패턴

### 1. 연결 생성 — get_mssql_connection() (빈도: 100%)

모든 MSSQL 접근은 `get_mssql_connection()`을 통해 연결을 얻는다.  
연결 실패 시 `None` 반환 — 호출부에서 None 체크 후 처리.

```python
# core/mssql.py
import pymssql
import logging
from app.core.config import settings

def get_mssql_connection():
    """공통 MSSQL 연결 생성기"""
    try:
        conn = pymssql.connect(
            server=settings.MSSQL_HOST,
            port=settings.MSSQL_PORT,
            user=settings.MSSQL_USER,
            password=settings.MSSQL_PASSWORD,
            database=settings.MSSQL_DB,
            charset='UTF-8',
            login_timeout=10
        )
        return conn
    except Exception as e:
        logging.error(f"[MSSQL Connection Error] {e}")
        return None
```

연결 파라미터 설정 위치: `settings` 객체 (`.env` → `core/config.py`에서 로드).  
커넥션 풀 미사용 — 요청마다 신규 연결 생성.

---

### 2. SELECT 쿼리 패턴 (빈도: 100%, 4/4 SELECT 함수)

`cursor(as_dict=True)`로 딕셔너리 리스트 반환. `finally`에서 연결 close.

```python
# fetchall — 목록 조회 (core/mssql.py:67-75 패턴)
def get_internal_notices():
    conn = get_mssql_connection()
    if not conn: return []           # None 체크 — 빈 리스트 반환
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC")
        return cursor.fetchall()     # 딕셔너리 리스트
    finally:
        conn.close()                 # 예외 발생 여부 무관하게 항상 close

# fetchone — 단건 조회 (core/mssql.py:24-44 패턴)
def get_mssql_user_info(emp_no: str):
    conn = get_mssql_connection()
    if not conn: return None         # None 체크 — None 반환
    try:
        cursor = conn.cursor(as_dict=True)
        query = """
        SELECT COMPANY, COMPANY_NM, EMP_NO, KOR_NM
        FROM SUPPORT.DBO.ALL_AMSTM_VIEW
        WHERE HLD_OFFI_GBN <> '3' AND EMP_NO = %s
        """
        cursor.execute(query, (str(emp_no),))   # %s 바인딩
        return cursor.fetchone()
    except Exception as e:
        logging.error(f"MSSQL Error: {e}")
        return None
    finally:
        conn.close()
```

---

### 3. DML 트랜잭션 패턴 (빈도: 100%, 12/12 DML 엔드포인트)

INSERT/UPDATE/DELETE 는 반드시 `try/except/finally` 구조로 트랜잭션 처리.

```python
# INSERT 패턴 (admin.py:55-72)
conn = get_mssql_connection()
if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
try:
    cursor = conn.cursor()           # DML은 as_dict 불필요
    cursor.execute("""
        INSERT INTO MFS_USERS (EMP_NO, KOR_NM, PASSWORD_HASH, IS_ADMIN)
        VALUES (%s, %s, %s, %s)
    """, (user.emp_no.upper(), user.kor_nm, pwd_hash, 1 if user.is_admin else 0))
    conn.commit()
    return {"message": "사용자가 등록되었습니다."}
except Exception as e:
    conn.rollback()
    raise HTTPException(status_code=400, detail=str(e))
finally:
    conn.close()

# UPDATE 패턴 — 동적 SET 구성 (admin.py:74-106)
updates = []
params = []
if user.kor_nm is not None:
    updates.append("KOR_NM = %s")
    params.append(user.kor_nm)
if user.password:
    updates.append("PASSWORD_HASH = %s")
    params.append(get_password_hash(user.password))
if not updates:
    return {"message": "변경할 내용이 없습니다."}
params.append(emp_no.upper())
query = f"UPDATE MFS_USERS SET {', '.join(updates)} WHERE EMP_NO = %s"
cursor.execute(query, tuple(params))
conn.commit()

# DELETE 패턴 (admin.py:108-121)
cursor.execute("DELETE FROM MFS_USERS WHERE EMP_NO = %s", (emp_no.upper(),))
conn.commit()
```

트랜잭션 규칙:
- 성공 시: `conn.commit()`
- 예외 시: `conn.rollback()` + `HTTPException` raise
- 항상: `finally: conn.close()`

---

### 4. 파라미터 바인딩 방식 (빈도: 100%)

모든 쿼리에서 `%s` 플레이스홀더 + 튜플 방식으로 바인딩. SQL 인젝션 방지.

```python
# 단일 파라미터 — 튜플로 감싸기 (콤마 필수)
cursor.execute("SELECT * FROM MFS_USERS WHERE EMP_NO = %s", (emp_no,))

# 다중 파라미터
cursor.execute("""
    INSERT INTO MFS_NOTICES (SUBJECT, CONTENT, ERDAT, ERZET, ERNAM)
    VALUES (%s, %s, %s, %s, %s)
""", (notice.subject, notice.content, erdat, erzet, current_user.username))
```

---

### 5. 크로스 DB 쿼리 패턴

외부 인사 정보 조회 시 `SUPPORT.DBO.{뷰이름}` 형식으로 크로스 DB 접근.

```python
# core/mssql.py:32-36
query = """
SELECT COMPANY, COMPANY_NM, EMP_NO, KOR_NM, OFFI_RES_NM
FROM SUPPORT.DBO.ALL_AMSTM_VIEW
WHERE HLD_OFFI_GBN <> '3' AND EMP_NO = %s
"""
```

크로스 DB 대상: `SUPPORT.DBO.ALL_AMSTM_VIEW` (인사 정보 뷰, 외부 DB)

---

### 6. 함수 위치 규칙

| 역할 | 위치 |
|------|------|
| 공통 연결 생성기 | `backend/app/core/mssql.py` |
| SELECT 공통 함수 | `backend/app/core/mssql.py` |
| DML (INSERT/UPDATE/DELETE) | `backend/app/api/admin.py` 엔드포인트 내 인라인 |
| SQLAlchemy SQLite (인증 세션) | `backend/app/db/session.py` — 별도 용도 |

주의: `backend/app/db/mssql_db.py`는 레거시 파일 — 신규 코드에서 사용 금지. `core/mssql.py`가 실사용 모듈.

---

## 안티패턴 (하지 말 것)

### A1. f-string SQL 직접 삽입 — SQL 인젝션 위험

```python
# 절대 금지 — 사용자 입력을 f-string으로 SQL에 직접 삽입
query = f"SELECT * FROM MFS_USERS WHERE EMP_NO = '{emp_no}'"
cursor.execute(query)

# 올바른 방식 — %s 바인딩
cursor.execute("SELECT * FROM MFS_USERS WHERE EMP_NO = %s", (emp_no,))
```

현재 코드베이스에서 f-string SQL은 admin.py:98의 동적 UPDATE에서 SET 절 구성에만 사용되며, 이 경우 컬럼명은 코드 내 고정값이고 값은 `%s` 바인딩으로 처리되어 안전하다.

---

### A2. 연결 None 체크 누락

```python
# 위험 — None 체크 없이 바로 사용
conn = get_mssql_connection()
cursor = conn.cursor()  # conn이 None이면 AttributeError

# 올바른 패턴
conn = get_mssql_connection()
if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
# 또는 조회용: if not conn: return []
```

---

### A3. finally 없이 close 호출

```python
# 위험 — 예외 발생 시 conn.close() 호출 안 됨 (연결 누수)
try:
    cursor.execute(...)
    conn.commit()
    conn.close()   # <- 예외 발생하면 실행 안 됨
except:
    conn.rollback()

# 올바른 패턴
try:
    cursor.execute(...)
    conn.commit()
except Exception as e:
    conn.rollback()
    raise HTTPException(...)
finally:
    conn.close()   # <- 항상 실행됨
```

---

### A4. `db/mssql_db.py` 레거시 모듈 사용

`backend/app/db/mssql_db.py`는 구형 파일. 신규 코드에서 import 금지.

```python
# 금지
from app.db.mssql_db import fetch_mssql_notices   # 레거시

# 올바른 import
from app.core.mssql import get_internal_notices    # 실사용 모듈
```

---

## 실제 코드 샘플

- `backend/app/core/mssql.py:7-22` — get_mssql_connection() 구현
- `backend/app/core/mssql.py:24-44` — fetchone + %s 바인딩 패턴
- `backend/app/core/mssql.py:67-75` — fetchall + finally close 패턴
- `backend/app/api/admin.py:55-72` — INSERT 트랜잭션 표준 패턴
- `backend/app/api/admin.py:74-106` — 동적 UPDATE SET 구성 패턴
- `backend/app/api/admin.py:108-121` — DELETE 패턴
- `backend/app/api/admin.py:43-53` — SELECT + finally close (rollback 없는 패턴)

---

## 신규 DB 쿼리 작성 가이드

1. SELECT 공통 함수 추가 시 → `backend/app/core/mssql.py`에 함수 추가
2. DML은 API 엔드포인트 내 인라인으로 작성
3. 반드시 `%s` 플레이스홀더 바인딩 사용 — f-string SQL 금지
4. 연결 생성 후 즉시 `if not conn:` 체크
5. DML: `try/except(rollback)/finally(close)` 구조 준수
6. SELECT: `try/finally(close)` 구조 (rollback 불필요)
7. 결과가 딕셔너리 필요 시 `cursor(as_dict=True)` 사용
