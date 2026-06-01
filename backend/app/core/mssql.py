import pymssql
import logging
from app.core.config import settings

from app.core.security import verify_password

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

def get_mssql_user_info(emp_no: str):
    """
    사번(EMP_NO)을 기반으로 MSSQL(SUPPORT.DBO.ALL_AMSTM_VIEW)에서 인사 정보를 조회합니다.
    """
    conn = get_mssql_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(as_dict=True)
        query = """
        SELECT COMPANY, COMPANY_NM, EMP_NO, KOR_NM, OFFI_RES_NM
        FROM SUPPORT.DBO.ALL_AMSTM_VIEW
        WHERE HLD_OFFI_GBN <> '3' AND EMP_NO = %s
        """
        cursor.execute(query, (str(emp_no),))
        row = cursor.fetchone()
        return row
    except Exception as e:
        logging.error(f"MSSQL Error: {e}")
        return None
    finally:
        conn.close()

def authenticate_mssql_user(emp_no: str, password: str):
    """
    MFS_USERS 테이블에서 관리자/사용자 인증을 수행합니다.
    """
    conn = get_mssql_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(as_dict=True)
        query = "SELECT * FROM MFS_USERS WHERE EMP_NO = %s"
        cursor.execute(query, (str(emp_no),))
        user = cursor.fetchone()
        if user and verify_password(password, user['PASSWORD_HASH']):
            return user
        return None
    except Exception as e:
        logging.error(f"Auth MSSQL Error: {e}")
        return None
    finally:
        conn.close()

# 신규 데이터 추가/조회용 함수들 (Notice, Contact)
def get_internal_notices():
    conn = get_mssql_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT * FROM MFS_NOTICES ORDER BY ERDAT DESC, ERZET DESC")
        return cursor.fetchall()
    finally:
        conn.close()

def get_internal_contacts():
    conn = get_mssql_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT * FROM MFS_CONTACTS ORDER BY DIVISION, NAME")
        return cursor.fetchall()
    finally:
        conn.close()
