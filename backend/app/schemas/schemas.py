from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    kor_nm: Optional[str] = None
    company_nm: Optional[str] = None
    is_admin: bool = False

class TokenData(BaseModel):
    username: Optional[str] = Field(None, max_length=50)

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=128)

class UserSchema(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CardUsageSchema(BaseModel):
    id: int
    merchant_name: str = Field(..., max_length=200)
    amount: float
    used_at: datetime
    category: str = Field(..., max_length=50)

    class Config:
        from_attributes = True

class NoticeSchema(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., max_length=50000)
    created_at: datetime
    is_popup: bool

    class Config:
        from_attributes = True
