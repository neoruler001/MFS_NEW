@echo off
echo MFS Wiki Server
echo ===============
echo http://localhost:4200
echo Ctrl+C 로 종료
echo.
python -m http.server 4200
