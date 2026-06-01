from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.core.mssql import get_mssql_connection
from app.core.security import get_password_hash
import datetime

router = APIRouter()

class UserCreate(BaseModel):
    emp_no: str
    kor_nm: str
    password: str
    is_admin: bool = False

class UserUpdate(BaseModel):
    kor_nm: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

class NoticeCreate(BaseModel):
    subject: str
    content: str

class ContactCreate(BaseModel):
    division: str
    title: Optional[str] = None
    name: str
    tel: str
    email: Optional[str] = None
    task: Optional[str] = None
    remark: Optional[str] = None

def check_admin(current_user: any):
    if not getattr(current_user, "is_admin", False):
        # JWT 토큰에서도 확인 가능하지만, 만약 가상 객체라면 is_admin 필드 확인
        # 현재 get_current_user는 SQLite User 객체를 반환하므로 주의
        # payload에서 is_admin을 꺼내오도록 수정하거나 명시적 체크 필요
        pass
    return True

@router.get("/users")
def list_admin_users(current_user = Depends(get_current_user)):
    # 관리자만 조회 가능 (임시 권한 체크는 프론트와 연동 후 강화)
    conn = get_mssql_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT EMP_NO, KOR_NM, IS_ADMIN, CREATED_AT FROM MFS_USERS ORDER BY CREATED_AT DESC")
        return cursor.fetchall()
    finally:
        conn.close()

@router.post("/users")
def create_admin_user(user: UserCreate, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        pwd_hash = get_password_hash(user.password)
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

@router.put("/users/{emp_no}")
def update_admin_user(emp_no: str, user: UserUpdate, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if user.kor_nm is not None:
            updates.append("KOR_NM = %s")
            params.append(user.kor_nm)
        if user.is_admin is not None:
            updates.append("IS_ADMIN = %s")
            params.append(1 if user.is_admin else 0)
        if user.password:
            updates.append("PASSWORD_HASH = %s")
            params.append(get_password_hash(user.password))
            
        if not updates:
            return {"message": "변경할 내용이 없습니다."}
            
        params.append(emp_no.upper())
        query = f"UPDATE MFS_USERS SET {', '.join(updates)} WHERE EMP_NO = %s"
        cursor.execute(query, tuple(params))
        conn.commit()
        return {"message": "사용자 정보가 수정되었습니다."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.delete("/users/{emp_no}")
def delete_admin_user(emp_no: str, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM MFS_USERS WHERE EMP_NO = %s", (emp_no.upper(),))
        conn.commit()
        return {"message": "사용자가 삭제되었습니다."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/notices")
def list_admin_notices(current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT ID, SUBJECT, CONTENT, ERDAT, ERZET, ERNAM FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC")
        return cursor.fetchall()
    finally:
        conn.close()

@router.post("/notices")
def create_internal_notice(notice: NoticeCreate, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        now = datetime.datetime.now()
        erdat = now.strftime("%Y%m%d")
        erzet = now.strftime("%H%M%S")
        cursor.execute("""
            INSERT INTO MFS_NOTICES (SUBJECT, CONTENT, ERDAT, ERZET, ERNAM)
            VALUES (%s, %s, %s, %s, %s)
        """, (notice.subject, notice.content, erdat, erzet, current_user.username))
        conn.commit()
        return {"message": "공지사항이 등록되었습니다."}
    finally:
        conn.close()

@router.put("/notices/{notice_id}")
def update_internal_notice(notice_id: int, notice: NoticeCreate, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE MFS_NOTICES 
            SET SUBJECT=%s, CONTENT=%s
            WHERE ID=%s
        """, (notice.subject, notice.content, notice_id))
        conn.commit()
        return {"message": "공지사항이 수정되었습니다."}
    finally:
        conn.close()

@router.delete("/notices/{notice_id}")
def delete_internal_notice(notice_id: int, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM MFS_NOTICES WHERE ID=%s", (notice_id,))
        conn.commit()
        return {"message": "공지사항이 삭제되었습니다."}
    finally:
        conn.close()

@router.get("/contacts")
def list_admin_contacts(current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT * FROM MFS_CONTACTS ORDER BY DIVISION, NAME")
        return cursor.fetchall()
    finally:
        conn.close()

@router.post("/contacts")
def create_internal_contact(contact: ContactCreate, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO MFS_CONTACTS (DIVISION, TITLE, NAME, TEL, EMAIL, TASK, REMARK)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (contact.division, contact.title, contact.name, contact.tel, contact.email, contact.task, contact.remark))
        conn.commit()
        return {"message": "연락처가 등록되었습니다."}
    finally:
        conn.close()

@router.put("/contacts/{contact_id}")
def update_internal_contact(contact_id: int, contact: ContactCreate, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE MFS_CONTACTS 
            SET DIVISION=%s, TITLE=%s, NAME=%s, TEL=%s, EMAIL=%s, TASK=%s, REMARK=%s
            WHERE ID=%s
        """, (contact.division, contact.title, contact.name, contact.tel, contact.email, contact.task, contact.remark, contact_id))
        conn.commit()
        return {"message": "연락처가 수정되었습니다."}
    finally:
        conn.close()

@router.delete("/contacts/{contact_id}")
def delete_internal_contact(contact_id: int, current_user = Depends(get_current_user)):
    conn = get_mssql_connection()
    if not conn: raise HTTPException(status_code=500, detail="DB 연결 실패")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM MFS_CONTACTS WHERE ID=%s", (contact_id,))
        conn.commit()
        return {"message": "연락처가 삭제되었습니다."}
    finally:
        conn.close()
