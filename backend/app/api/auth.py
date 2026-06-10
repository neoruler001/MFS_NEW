from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate
from app.core.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.core.config import settings

router = APIRouter()

from app.core.mssql import get_mssql_user_info, authenticate_mssql_user

class DelegateRequest(BaseModel):
    target_pernr: str

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 모든 입력 사번은 대문자로 처리 (대소문자 구분 없음)
    username_upper = form_data.username.upper()
    client_id_upper = form_data.client_id.upper() if form_data.client_id else None
    
    # 프론트엔드에서 client_id 매개변수 안에 대리 사번을 넣어 보냅니다.
    target_pernr = client_id_upper if client_id_upper else username_upper

    # 1. MSSQL(MFS_USERS) 기반 인증 수행 (관리자 및 등록된 사용자)
    # 로그인 시도하는 사번(username_upper)과 비밀번호로 인증
    mfs_user = authenticate_mssql_user(username_upper, form_data.password)
    
    # 관리자인지 확인 (테이블의 IS_ADMIN 필드)
    is_admin = False
    user_id_for_token = username_upper
    
    if mfs_user:
        # DB에 등록된 사용자 (관리자 등)
        is_admin = bool(mfs_user.get('IS_ADMIN'))
    else:
        # 인증 실패: 사번이 없거나 비밀번호가 틀린 경우
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사번 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. MSSQL에서 실제 조회 대상 사용자 정보(회사명, 성명) 조회
    # 보안: 조회할 대상 사번(target_pernr)을 전달합니다.
    target_info = get_mssql_user_info(target_pernr)
    
    # 인사 정보가 없는 경우(테스트 계정 등)를 위해 기본값 설정
    if not target_info:
        target_info = {
            "KOR_NM": "미등록 사용자",
            "COMPANY_NM": "MFS 시스템",
            "EMP_NO": target_pernr
        }

    # 3. 토큰 생성 및 사용자 정보 반환
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 토큰에 is_admin 정보 추가
    access_token = create_access_token(
        data={
            "sub": user_id_for_token, 
            "target_pernr": target_pernr,
            "is_admin": is_admin
        }, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "kor_nm": target_info.get("KOR_NM"),
        "company_nm": target_info.get("COMPANY_NM"),
        "is_admin": is_admin
    }


@router.post("/delegate")
async def delegate_target_user(
    body: DelegateRequest,
    current_user = Depends(get_current_user)
):
    """관리자 전용: 조회 대상 사번을 변경한 새 토큰을 발급합니다."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자만 사용할 수 있습니다.")

    pernr = body.target_pernr.strip().upper()
    target_info = get_mssql_user_info(pernr)
    if not target_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 사번의 사용자를 찾을 수 없습니다.")

    access_token = create_access_token(
        data={
            "sub": current_user.username,
            "target_pernr": pernr,
            "is_admin": True
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "kor_nm": target_info.get("KOR_NM"),
        "company_nm": target_info.get("COMPANY_NM"),
        "target_pernr": pernr,
        "is_admin": True
    }
