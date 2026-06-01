---
name: MFS 백엔드 개발 표준
description: >
  MFS FastAPI 백엔드 개발 시 적용하는 표준이다.
  새 API 엔드포인트 추가, 라우터 수정, DB 모델 변경, 인증 로직 수정,
  MSSQL/SQLite 연동 작업에 반드시 이 스킬을 참조한다.
  backend-engineer 에이전트가 주로 사용하며, 백엔드 관련 작업을 직접 수행할 때도 적용한다.
---

# MFS 백엔드 개발 표준

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py          # FastAPI 앱 진입점 (포트 4101)
│   ├── api/             # 라우터 (auth, card_usage, budget, notice, contact, admin)
│   ├── core/            # config, security, mssql, soap_client
│   ├── db/              # DB 세션 관리
│   ├── models/          # SQLAlchemy ORM 모델
│   └── schemas/         # Pydantic 스키마 (요청/응답)
└── .env                 # 환경변수
```

## 라우터 작성 패턴

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas import {스키마}

router = APIRouter()

@router.get("/", response_model=list[{응답스키마}])
async def get_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 인증이 필요한 엔드포인트는 반드시 Depends(get_current_user) 포함
    ...
```

새 라우터 추가 시 `app/main.py`에 다음 형식으로 등록:
```python
from app.api import {새라우터모듈}
app.include_router({새라우터모듈}.router, prefix=f"{settings.API_V1_STR}/{경로}", tags=["{태그}"])
```

## Pydantic 스키마 패턴

- 요청/응답 스키마는 `app/schemas/` 하위 모듈별 파일에 정의한다.
- DB ORM 모델과 Pydantic 스키마를 혼용하지 않는다.
- 응답 스키마에는 `model_config = ConfigDict(from_attributes=True)` 설정.

```python
from pydantic import BaseModel, ConfigDict

class CardUsageResponse(BaseModel):
    id: int
    merchant_name: str
    amount: float
    model_config = ConfigDict(from_attributes=True)
```

## DB 세션 패턴

- SQLite(개발): `DATABASE_URL = "sqlite:///./mfs.db"`
- MSSQL(운영): `app/core/mssql.py` 활용
- 세션은 항상 `Depends(get_db)`로 주입받고, 직접 생성하지 않는다.

## 보안 원칙

1. **SQL Injection**: ORM 메서드(`db.query().filter()`)를 사용하고, raw SQL 사용 금지.
2. **인증 필수**: 인증이 필요한 모든 엔드포인트에 `Depends(get_current_user)` 추가.
3. **환경변수**: SECRET_KEY, DB 비밀번호는 `.env`에서 로드. `config.py`의 Settings 클래스 참조.
4. **CORS**: 현재 `allow_origins=["*"]` — 개발 전용. 운영 배포 시 특정 도메인으로 제한 필요.
5. **비밀번호**: bcrypt 해싱 적용 (`app/core/security.py` 참조).
6. **에러 노출 금지**: 500 에러에 스택 트레이스나 DB 쿼리를 노출하지 않는다.

## API Spec 기록

프론트엔드가 연동할 수 있도록 새 엔드포인트 구현 후 `_workspace/api-spec.md`에 기록:

```markdown
## {엔드포인트명}
- Method: GET/POST/PUT/DELETE
- Path: /api/v1/{경로}
- Auth: Bearer 토큰 필요
- Request: {요청 스키마 또는 query params}
- Response: {응답 JSON 예시}
- Error: {에러 코드 및 메시지}
```

## Python 환경

- 패키지 관리: `uv` 사용 (`uv add {패키지}`, `uv run {스크립트}`)
- 기존 `.venv` 활용: `backend/.venv/`
