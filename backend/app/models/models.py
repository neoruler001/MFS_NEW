from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)  # 사번
    hashed_password = Column(String)
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CardUsage(Base):
    __tablename__ = "card_usages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    card_number = Column(String)
    merchant_name = Column(String)
    amount = Column(Float)
    used_at = Column(DateTime)
    category = Column(String)
    
    owner = relationship("User", back_populates="usages")

User.usages = relationship("CardUsage", back_populates="owner")

class Notice(Base):
    __tablename__ = "notices"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_popup = Column(Boolean, default=False)
