import pymssql
from app.core.config import settings

def check_mssql_users():
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
        cursor.execute("SELECT EMP_NO, KOR_NM, IS_ADMIN FROM MFS_USERS")
        users = cursor.fetchall()
        print(f"Found {len(users)} users in MFS_USERS:")
        for user in users:
            print(f"- {user['KOR_NM']} ({user['EMP_NO']}) [Admin: {user['IS_ADMIN']}]")
        conn.close()
    except Exception as e:
        print(f"Error checking MSSQL: {e}")

if __name__ == "__main__":
    check_mssql_users()
