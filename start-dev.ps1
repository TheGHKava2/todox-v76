# Script para iniciar ambiente de desenvolvimento ToDoX
# Inicia backend e frontend simultaneamente

param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

Write-Host "🚀 Iniciando ToDoX - Ambiente de Desenvolvimento" -ForegroundColor Green

if (-not $FrontendOnly) {
    Write-Host "📡 Iniciando Backend (FastAPI)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000; Write-Host 'Backend encerrado' -ForegroundColor Red"
    Start-Sleep -Seconds 3
}

if (-not $BackendOnly) {
    Write-Host "🌐 Iniciando Frontend (Next.js)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\web'; set PATH=C:\Program Files\nodejs;%PATH%; npm run dev; Write-Host 'Frontend encerrado' -ForegroundColor Red"
    Start-Sleep -Seconds 2
}

Write-Host "✅ Serviços iniciados!" -ForegroundColor Green
Write-Host "📡 Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "📖 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan

# Verificar conectividade
Write-Host "`n🔍 Verificando conectividade..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $healthCheck = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Backend OK (Status: $($healthCheck.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend não responde: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nPressione CTRL+C em ambas as janelas para parar os serviços" -ForegroundColor Gray