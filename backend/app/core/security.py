from passlib.context import CryptContext

# bcrypt 대신 환경 호환성이 높은 pbkdf2_sha256을 사용합니다.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
