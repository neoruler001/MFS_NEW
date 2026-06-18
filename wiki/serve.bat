@echo off
echo MFS Wiki 서버 시작 중...
echo.

REM Python으로 간단한 HTTP 서버 실행
echo http://localhost:3000 에서 실행됩니다.
echo 종료하려면 Ctrl+C 를 누르세요.
echo.

python -m http.server 3000

pause
