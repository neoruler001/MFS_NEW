import pymssql
from app.core.config import settings
from app.core.auth import get_password_hash

def init_mssql_tables():
    print("Connecting to MSSQL to initialize tables...")
    try:
        conn = pymssql.connect(
            server=settings.MSSQL_HOST,
            port=settings.MSSQL_PORT,
            user=settings.MSSQL_USER,
            password=settings.MSSQL_PASSWORD,
            database=None, # 초기 접속은 DB 없이
            charset='UTF-8',
            login_timeout=10
        )
        conn.autocommit(True)
        cursor = conn.cursor()
        
        # 1. MFS_USERS 테이블
        print("Creating MFS_USERS table...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='MFS_USERS' AND xtype='U')
        CREATE TABLE MFS_USERS (
            EMP_NO NVARCHAR(20) PRIMARY KEY,
            PASSWORD_HASH NVARCHAR(255) NOT NULL,
            IS_ADMIN BIT DEFAULT 0,
            KOR_NM NVARCHAR(50),
            CREATED_AT DATETIME DEFAULT GETDATE()
        )
        """)
        
        # 2. MFS_NOTICES 테이블
        print("Creating MFS_NOTICES table...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='MFS_NOTICES' AND xtype='U')
        CREATE TABLE MFS_NOTICES (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            SUBJECT NVARCHAR(255) NOT NULL,
            CONTENT NVARCHAR(MAX),
            ERDAT NVARCHAR(8),
            ERZET NVARCHAR(6),
            ERNAM NVARCHAR(50)
        )
        """)
        
        # 3. MFS_CONTACTS 테이블
        print("Creating MFS_CONTACTS table...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='MFS_CONTACTS' AND xtype='U')
        CREATE TABLE MFS_CONTACTS (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            SYSTEM_NAME NVARCHAR(200),
            SYSTEM_DESC NVARCHAR(500),
            DIVISION NVARCHAR(100),
            NAME NVARCHAR(50),
            TITLE NVARCHAR(50),
            TEL NVARCHAR(50),
            EMAIL NVARCHAR(100),
            REMARK NVARCHAR(255)
        )
        """)
        
        # 4. 초기 관리자 계정 생성 (BP26475)
        admin_id = "BP26475"
        admin_pwd_hash = get_password_hash("12")
        print(f"Registering Initial Admin: {admin_id}...")
        cursor.execute("SELECT * FROM MFS_USERS WHERE EMP_NO = %s", (admin_id,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO MFS_USERS (EMP_NO, PASSWORD_HASH, IS_ADMIN, KOR_NM)
            VALUES (%s, %s, 1, '관리자')
            """, (admin_id, admin_pwd_hash))
            print("Admin registered successfully.")
        else:
            print("Admin already exists.")
            
        conn.close()
        print("✅ MSSQL Table Initialization Complete!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize MSSQL tables: {e}")
        return False

if __name__ == "__main__":
    init_mssql_tables()
