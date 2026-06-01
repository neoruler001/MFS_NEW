import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api import auth, card_usage, notice, budget, contact, admin

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS 설정: 프론트엔드(localhost:6001)의 통신을 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 편의를 위해 전체 허용 (운영 시 특정 도메인으로 제한 권장)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(card_usage.router, prefix=f"{settings.API_V1_STR}/cards", tags=["cards"])
app.include_router(notice.router, prefix=f"{settings.API_V1_STR}/notices", tags=["notices"])
app.include_router(budget.router, prefix=f"{settings.API_V1_STR}/budget", tags=["budget"])
app.include_router(contact.router, prefix=f"{settings.API_V1_STR}/contacts", tags=["contacts"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Welcome to MFinanceSystem API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=4101, reload=True)
