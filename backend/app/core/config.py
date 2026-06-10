import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mobile Corporate Card System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SuperSecretKeyForDevelopmentOnly")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 20  # 20 minutes
    
    # Database (Local SQLITE)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mfs.db")

    # MSSQL Database
    MSSQL_HOST: str = "10.100.37.178"
    MSSQL_PORT: int = 3218
    MSSQL_USER: str = "XB01"
    MSSQL_PASSWORD: str = "DNSdudCMsoft!(0709"
    MSSQL_DB: Optional[str] = None  # 초기 접속 시 DB 지정을 생략해야 로그인이 가능합니다.
    
    class Config:
        case_sensitive = True

settings = Settings()
