import pymssql
from app.core.config import settings
from app.core.security import get_password_hash

def register_admins():
    print("Connecting to MSSQL...")
    try:
        conn = pymssql.connect(
            server=settings.MSSQL_HOST, port=settings.MSSQL_PORT,
            user=settings.MSSQL_USER, password=settings.MSSQL_PASSWORD,
            database=None, charset='UTF-8'
        )
        cursor = conn.cursor()
        # 비밀번호 '12'에 대한 해시 생성
        pwd_hash = get_password_hash('12') 
        
        admins = ["BP26475", "BP26745"]
        for pernr in admins:
            # MFS_USERS 테이블에 해당 사번이 있는지 확인
            cursor.execute("SELECT * FROM MFS_USERS WHERE EMP_NO = %s", (pernr,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                INSERT INTO MFS_USERS (EMP_NO, PASSWORD_HASH, IS_ADMIN, KOR_NM)
                VALUES (%s, %s, 1, 'Admin')
                """, (pernr, pwd_hash))
                print(f"User {pernr} registered.")
            else:
                cursor.execute("UPDATE MFS_USERS SET IS_ADMIN=1, PASSWORD_HASH=%s WHERE EMP_NO=%s", (pwd_hash, pernr))
                print(f"User {pernr} updated (password reset to 12).")
        
        conn.commit()
        conn.close()
        print("All operations completed successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    register_admins()
