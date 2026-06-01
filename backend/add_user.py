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
        pwd_hash = get_password_hash('12') # 관리자 공통 초기 비번
        
        admins = ["BP26475", "BP26745"]
        for pernr in admins:
            cursor.execute("SELECT * FROM MFS_USERS WHERE EMP_NO = %s", (pernr,))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO MFS_USERS (EMP_NO, PASSWORD_HASH, IS_ADMIN, KOR_NM)
                VALUES (%s, %s, 1, '관리자')
                """, (pernr, pwd_hash))
                print(f"✅ {pernr} 등록 완료")
            else:
                cursor.execute("UPDATE MFS_USERS SET IS_ADMIN=1, PASSWORD_HASH=%s WHERE EMP_NO=%s", (pwd_hash, pernr))
                print(f"✅ {pernr} 권한 업데이트 완료")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ 실패: {e}")

if __name__ == "__main__":
    register_admins()
