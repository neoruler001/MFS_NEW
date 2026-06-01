import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models.models import User, CardUsage, Notice
from app.core.auth import get_password_hash
import datetime

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if user already exists
    if db.query(User).filter(User.username == "admin").first():
        db.close()
        return

    # Create Admin User
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="관리자",
        is_admin=True
    )
    db.add(admin_user)
    
    # Create Regular User
    test_user = User(
        username="test",
        hashed_password=get_password_hash("test123"),
        full_name="Neo",
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Create Sample Card Usages
    usages = [
        CardUsage(user_id=test_user.id, card_number="1234-****-****-5678", merchant_name="스타벅스 강남점", amount=5600.0, used_at=datetime.datetime.now() - datetime.timedelta(hours=2), category="식비"),
        CardUsage(user_id=test_user.id, card_number="1234-****-****-5678", merchant_name="카카오택시", amount=12400.0, used_at=datetime.datetime.now() - datetime.timedelta(days=1), category="교통비"),
        CardUsage(user_id=test_user.id, card_number="1234-****-****-5678", merchant_name="김밥천국", amount=8500.0, used_at=datetime.datetime.now() - datetime.timedelta(days=2), category="식비")
    ]
    db.add_all(usages)
    
    # Create Sample Notices
    notices = [
        Notice(title="시스템 점검 안내", content="2026년 4월 20일 새벽 시스템 점검이 예정되어 있습니다.", is_popup=True),
        Notice(title="법인카드 사용 규정 안내", content="야간 식대 영수증 제출 시 증빙 서류를 반드시 첨부해 주세요.", is_popup=False)
    ]
    db.add_all(notices)
    
    db.commit()
    db.close()
    print("Database initialized with sample data.")

if __name__ == "__main__":
    init_db()
