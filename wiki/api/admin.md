# 관리자 API

**Base path:** `/api/v1/admin`  
**파일:** `backend/app/api/admin.py`  
**데이터 소스:** MSSQL

> ⚠️ **보안 경고:** `check_admin()` 함수가 현재 빈 `pass`로 구현되어 있어 인증된 일반 사용자도 모든 관리자 API에 접근 가능한 상태. 즉시 수정 필요.

---

## 사용자 관리

### GET /users

전체 사용자 목록 조회.

```sql
SELECT EMP_NO, KOR_NM, IS_ADMIN, CREATED_AT
FROM MFS_USERS
ORDER BY CREATED_AT DESC
```

### POST /users

신규 사용자 등록.

**요청:**
```json
{
  "emp_no": "BP26745",
  "kor_nm": "김철수",
  "password": "초기비밀번호",
  "is_admin": false
}
```

**처리:**
```python
pwd_hash = security.get_password_hash(password)  # pbkdf2_sha256
# INSERT INTO MFS_USERS (EMP_NO, KOR_NM, PASSWORD_HASH, IS_ADMIN) VALUES (%s, %s, %s, %s)
```

### PUT /users/{emp_no}

사용자 정보 수정 (이름, 비밀번호, 관리자 여부).

> **주의:** 동적 f-string으로 SET 절을 조합하는 패턴 — 내부 신뢰 데이터만 사용.

### DELETE /users/{emp_no}

사용자 삭제.

```sql
DELETE FROM MFS_USERS WHERE EMP_NO = %s
```

---

## 공지사항 관리

### GET /notices

전체 공지 목록 (MSSQL 내부 공지만).

### POST /notices

공지 등록.

```json
{
  "subject": "점검 안내",
  "content": "내용"
}
```

### PUT /notices/{notice_id}

공지 수정.

### DELETE /notices/{notice_id}

공지 삭제.

---

## 연락처 관리

### GET /contacts

전체 연락처 목록.

### POST /contacts

연락처 등록.

```json
{
  "division": "IT본부",
  "title": "과장",
  "name": "홍길동",
  "tel": "02-1234-5678",
  "email": "hong@hhi.co.kr",
  "task": "시스템 개발",
  "remark": ""
}
```

### PUT /contacts/{contact_id}

연락처 수정.

### DELETE /contacts/{contact_id}

연락처 삭제.

---

## 트랜잭션 패턴

모든 DML은 pymssql의 수동 트랜잭션으로 처리된다:

```python
conn = get_mssql_connection()
cursor = conn.cursor()
try:
    cursor.execute(sql, params)
    conn.commit()
    return result
except Exception as e:
    conn.rollback()
    raise HTTPException(status_code=500, detail=str(e))
finally:
    conn.close()
```

---

## ⚠️ 알려진 보안 이슈

```python
# admin.py:35-41 현재 코드
def check_admin(current_user):
    pass  # ← 아무 검증 없음!

# 필요한 코드
def check_admin(current_user):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한 필요")
```

자세한 내용은 [보안 이슈](../security.md) 참조.
