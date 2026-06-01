import pymssql
from app.core.config import settings

# Web.config의 ConnectionString 참고 (최신: 10.100.37.178, XB04)
MSSQL_CONFIG = {
    "server": "10.100.37.178",
    "port": "3218",
    "user": "XB01",
    "password": "DNSdudCMsoft!(0709",
    "database": "XB01"
}

def get_mssql_connection():
    try:
        conn = pymssql.connect(
            server=MSSQL_CONFIG["server"],
            port=MSSQL_CONFIG["port"],
            user=MSSQL_CONFIG["user"],
            password=MSSQL_CONFIG["password"],
            database=MSSQL_CONFIG["database"],
            as_dict=True
        )
        return conn
    except Exception as e:
        print(f"MSSQL Connection Error: {e}")
        return None

def fetch_mssql_notices():
    """기존 MSSQL DB에서 공지사항 데이터를 조회합니다."""
    conn = get_mssql_connection()
    if not conn:
        return []
        
    try:
        cursor = conn.cursor()
        # 테이블명은 예상 파일/컨텍스트를 통해 유추 (IF_T_NOTICE 등이 일반적)
        # 실제 테이블명을 확인하지 못한 경우 에러가 발생할 수 있으므로 주의
        query = "SELECT TOP 50 * FROM IF_T_NOTICE ORDER BY REG_DATE DESC"
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"MSSQL Query Error: {e}")
        return []
