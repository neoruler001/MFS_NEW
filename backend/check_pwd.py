
import pymssql
from app.core.config import settings
from app.core.security import verify_password, get_password_hash

def debug_login():
    emp_no = "BP26745"
    plain_password = "12"
    
    try:
        conn = pymssql.connect(
            server=settings.MSSQL_HOST,
            port=settings.MSSQL_PORT,
            user=settings.MSSQL_USER,
            password=settings.MSSQL_PASSWORD,
            database=settings.MSSQL_DB,
            charset='UTF-8',
            login_timeout=5
        )
        cursor = conn.cursor(as_dict=True)
        
        # 1. MFS_USERS 인증 확인
        cursor.execute("SELECT EMP_NO, PASSWORD_HASH FROM MFS_USERS WHERE EMP_NO = %s", (emp_no,))
        user = cursor.fetchone()
        
        if user:
            stored_hash = user['PASSWORD_HASH']
            is_valid = verify_password(plain_password, stored_hash)
            print(f"--- MFS_USERS Auth Check ---")
            print(f"User {emp_no} found.")
            print(f"Verify '12': {is_valid}")
        else:
            print(f"User {emp_no} not found in MFS_USERS table.")

        # 2. 인사 정보(SUPPORT.DBO.ALL_AMSTM_VIEW) 조회 확인
        print(f"\n--- HR Info Check (SUPPORT.DBO.ALL_AMSTM_VIEW) ---")
        query = """
        SELECT COMPANY, COMPANY_NM, EMP_NO, KOR_NM, OFFI_RES_NM
        FROM SUPPORT.DBO.ALL_AMSTM_VIEW
        WHERE HLD_OFFI_GBN <> '3' AND EMP_NO = %s
        """
        cursor.execute(query, (emp_no,))
        hr_info = cursor.fetchone()
        
        if hr_info:
            print(f"HR Info found: {hr_info['KOR_NM']} ({hr_info['EMP_NO']}) at {hr_info['COMPANY_NM']}")
        else:
            print(f"HR Info NOT found for EMP_NO: {emp_no}")
            # HLD_OFFI_GBN 조건 없이 다시 조회 시도
            cursor.execute("SELECT EMP_NO, HLD_OFFI_GBN FROM SUPPORT.DBO.ALL_AMSTM_VIEW WHERE EMP_NO = %s", (emp_no,))
            raw_info = cursor.fetchone()
            if raw_info:
                print(f"User exists but HLD_OFFI_GBN is '{raw_info['HLD_OFFI_GBN']}' (Expected not '3')")
            else:
                print(f"EMP_NO {emp_no} does not exist in SUPPORT.DBO.ALL_AMSTM_VIEW at all.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_login()
