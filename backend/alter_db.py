import pymssql
from app.core.config import settings

def alter_db():
    try:
        conn = pymssql.connect(
            server=settings.MSSQL_HOST, port=settings.MSSQL_PORT,
            user=settings.MSSQL_USER, password=settings.MSSQL_PASSWORD,
            database=None, charset='UTF-8'
        )
        cursor = conn.cursor()
        
        # Add TITLE, TASK columns to MFS_CONTACTS if they do not exist
        cursor.execute("""
        IF COL_LENGTH('MFS_CONTACTS', 'TITLE') IS NULL
        BEGIN
            ALTER TABLE MFS_CONTACTS ADD TITLE NVARCHAR(50) NULL;
        END
        """)

        cursor.execute("""
        IF COL_LENGTH('MFS_CONTACTS', 'TASK') IS NULL
        BEGIN
            ALTER TABLE MFS_CONTACTS ADD TASK NVARCHAR(200) NULL;
        END
        """)
        
        conn.commit()
        print("MFS_CONTACTS altered successfully")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    alter_db()
