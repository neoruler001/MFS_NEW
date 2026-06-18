# 관리자 API — /api/v1/admin

**파일**: `backend/app/api/admin.py`

> ⚠️ **보안 경고**: 현재 `check_admin()` 함수가 실질적인 권한 검증을 하지 않습니다.  
> 인증된 **일반 사용자**도 이 API 전체에 접근 가능합니다. [보안 이슈 #3](/security) 참고.

모든 엔드포인트는 JWT 인증이 필요합니다.

---

## 사용자 관리

### GET /api/v1/admin/users

시스템 사용자 목록을 조회합니다.

**응답 (200 OK)**

```json
[
  {
    "EMP_NO": "BP12345",
    "KOR_NM": "홍길동",
    "IS_ADMIN": 0,
    "CREATED_AT": "2026-01-15 10:30:00"
  }
]
```

**쿼리**:
```sql
SELECT EMP_NO, KOR_NM, IS_ADMIN, CREATED_AT FROM MFS_USERS ORDER BY CREATED_AT DESC
```

---

### POST /api/v1/admin/users

새 사용자를 등록합니다.

**요청 Body**:

```json
{
  "emp_no": "BP12345",
  "kor_nm": "홍길동",
  "password": "초기비밀번호",
  "is_admin": false
}
```

**응답 (200 OK)**:
```json
{ "message": "사용자가 등록되었습니다." }
```

비밀번호는 `pbkdf2_sha256`으로 해시하여 저장됩니다.  
사번은 대문자로 정규화됩니다 (`emp_no.upper()`).

---

### PUT /api/v1/admin/users/{emp_no}

사용자 정보를 수정합니다.

**요청 Body** (변경할 필드만 포함):

```json
{
  "kor_nm": "홍길동",
  "password": "새비밀번호",
  "is_admin": true
}
```

필드를 생략하면 해당 값은 변경되지 않습니다 (PATCH 방식).

**응답 (200 OK)**:
```json
{ "message": "사용자 정보가 수정되었습니다." }
```

---

### DELETE /api/v1/admin/users/{emp_no}

사용자를 삭제합니다.

**응답 (200 OK)**:
```json
{ "message": "사용자가 삭제되었습니다." }
```

---

## 공지사항 관리

### GET /api/v1/admin/notices

내부 공지사항 전체 목록을 조회합니다.

**쿼리**:
```sql
SELECT ID, SUBJECT, CONTENT, ERDAT, ERZET, ERNAM FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC
```

---

### POST /api/v1/admin/notices

새 공지사항을 등록합니다.

**요청 Body**:

```json
{
  "subject": "공지 제목",
  "content": "공지 내용"
}
```

등록일시(`ERDAT`, `ERZET`)는 서버에서 자동 생성됩니다.  
작성자(`ERNAM`)는 현재 로그인 사용자의 사번이 기록됩니다.

---

### PUT /api/v1/admin/notices/{notice_id}

공지사항을 수정합니다.

**요청 Body**:

```json
{
  "subject": "수정된 제목",
  "content": "수정된 내용"
}
```

---

### DELETE /api/v1/admin/notices/{notice_id}

공지사항을 삭제합니다.

---

## 연락처 관리

### GET /api/v1/admin/contacts

내부 연락처 목록을 조회합니다.

**쿼리**:
```sql
SELECT * FROM MFS_CONTACTS ORDER BY DIVISION, NAME
```

---

### POST /api/v1/admin/contacts

새 연락처를 등록합니다.

**요청 Body**:

```json
{
  "division": "재경팀",
  "title": "팀장",
  "name": "홍길동",
  "tel": "010-1234-5678",
  "email": "hong@hhi.co.kr",
  "task": "법인카드 관리",
  "remark": ""
}
```

---

### PUT /api/v1/admin/contacts/{contact_id}

연락처를 수정합니다 (전체 필드 교체).

---

### DELETE /api/v1/admin/contacts/{contact_id}

연락처를 삭제합니다.

---

## Vue 호출 예시 (AdminView.vue)

```javascript
// 사용자 목록 조회
const fetchUsers = async () => {
  try {
    const res = await axios.get('/api/v1/admin/users')
    users.value = res.data
  } catch (err) {
    showMsg('조회 실패', true)
  }
}

// 사용자 등록/수정
const handleUserSubmit = async () => {
  try {
    if (editMode.value) {
      await axios.put(`/api/v1/admin/users/${form.value.emp_no}`, form.value)
      showMsg('수정되었습니다.')
    } else {
      await axios.post('/api/v1/admin/users', form.value)
      showMsg('등록되었습니다.')
    }
    resetForm()
    fetchUsers()
  } catch (err) {
    showMsg('오류: ' + (err.response?.data?.detail || '저장 실패'), true)
  }
}

// 사용자 삭제
const deleteUser = async (empNo) => {
  if (!confirm(`${empNo} 사용자를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/v1/admin/users/${empNo}`)
    showMsg('삭제되었습니다.')
    fetchUsers()
  } catch (err) {
    showMsg('삭제 실패', true)
  }
}
```
