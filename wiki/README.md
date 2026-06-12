# MFS — 모바일 법인카드 관리 시스템

> HD현대 그룹 임직원 법인카드 비용처리 및 예산 관리 시스템

---

## 개요

| 항목 | 내용 |
|------|------|
| 백엔드 | Python 3.14 + FastAPI (포트 **4101**) |
| 프런트엔드 | Vue 3.3.4 + Vite 4.4.5 (포트 **4001**) |
| 운영 DB | MSSQL `10.100.37.178:3218` (pymssql) |
| 외부 시스템 | SAP PI SOAP `http://hipop.hhi.co.kr:50000` |
| 인증 | JWT HS256 · 20분 만료 · MSSQL `MFS_USERS` |

---

## 빠른 시작

```bash
# 백엔드
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 4101 --reload

# 프런트엔드
cd frontend
npm run dev
```

접속: http://localhost:4001

---

## 핵심 기능

| 기능 | 경로 | 데이터 소스 |
|------|------|------------|
| 카드 이용내역 조회 | `/cards/usages` | SAP XFI00250 |
| 비용처리 (전표 생성) | `POST /cards/process` | SAP XFI00260 |
| 처리취소 | `POST /cards/cancel` | SAP XFI00270 |
| 업무목록 조회 | `/cards/worklist` | SAP XFI00280 |
| 예산 조회 | `/budget/info` | SAP XFI00290 |
| 연락처 | `/contacts/list` | MSSQL + SAP XFI00310 |
| 공지사항 | `/notices/notices` | MSSQL + SAP XFI00320 |
| 관리자 CRUD | `/admin/*` | MSSQL |

---

## 시스템 구성도

```
┌─────────────────┐        ┌──────────────────┐        ┌──────────────┐
│   Vue 3 SPA     │──────→ │   FastAPI 4101   │──────→ │   MSSQL DB   │
│  (Vite :4001)   │ axios  │                  │ pymssql│  인증/공지/  │
└─────────────────┘  JWT   │                  │        │  연락처/관리 │
                           │                  │        └──────────────┘
                           │                  │        ┌──────────────┐
                           │                  │──────→ │   SAP PI     │
                           └──────────────────┘  SOAP  │  카드/예산   │
                                                        └──────────────┘
```

---

## 허브 함수 (변경 시 주의)

| 함수 | 파일 | 영향 범위 |
|------|------|----------|
| `get_current_user` | `core/auth.py` | 12개 엔드포인트 DI |
| `get_mssql_connection` | `core/mssql.py` | 모든 MSSQL 쿼리 진입점 |
| `_call_sap_soap` | `core/soap_client.py` | 7개 SAP 인터페이스 |

---

## ⚠️ 보안 주의사항

> **운영 배포 전 반드시 확인**

- `core/config.py` — MSSQL 자격증명 하드코딩 → `.env` 이관 필요
- `core/soap_client.py` — SAP PI 패스워드 하드코딩
- `api/admin.py:35-41` — `check_admin()` 미구현 → 관리자 API 무방비
- `config.py` — JWT SECRET_KEY 기본값 노출

자세한 내용은 [보안 이슈](security.md) 페이지 참조.

---

*최종 갱신: 2026-06-11 · harness-fin v1*
