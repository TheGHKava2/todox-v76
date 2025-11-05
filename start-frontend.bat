@echo off
cd /d "d:\todox_v76\web"
set "PATH=C:\Program Files\nodejs;%PATH%"
echo Iniciando servidor Next.js...
echo Node.js version:
node --version
echo NPM version:
npm --version
echo.
echo Frontend rodando em: http://localhost:3000
echo Backend rodando em: http://localhost:8000
echo.
npm run dev
pause