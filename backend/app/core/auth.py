from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.db.session import get_db
from app.models.models import User

from app.core.security import verify_password, get_password_hash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        target_pernr: str = payload.get("target_pernr")
        is_admin: bool = payload.get("is_admin", False)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # SQLite DB에서 조회 시도 (DB 세션이 있는 경우에만)
    user = None
    if db is not None:
        try:
            user = db.query(User).filter(User.username == username).first()
        except Exception as e:
            print(f"[DEBUG AUTH] DB Query Error: {e}")
            user = None
            
    if user is None:
        # DB에 등록되지 않았더라도 토큰 정보(is_admin 포함)를 가진 가상 객체 생성
        # (MSSQL MFS_USERS 인증 사용자가 이에 해당함)
        user = User(username=username, full_name="User", is_admin=is_admin)
    else:
        # DB에 있다면 토큰의 권한 정보를 우선 적용 (또는 DB 정보 동기화)
        user.is_admin = is_admin
    
    # 동적 사번 바인딩
    user.target_pernr = target_pernr if target_pernr else username
    print(f"[DEBUG AUTH] User: {username}, target_pernr: {user.target_pernr}, is_admin: {user.is_admin}")
    return user

