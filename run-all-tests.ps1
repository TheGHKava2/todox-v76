# Script para executar todos os testes do ToDoX
# Backend (pytest) + Frontend (vitest)

Write-Host "🧪 Executando Suite Completa de Testes - ToDoX" -ForegroundColor Green

# Verificar se backend está rodando
Write-Host "`n1️⃣ Verificando Backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend OK: $($health.service)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend não está rodando!" -ForegroundColor Red
    Write-Host "   Inicie o backend: cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor Gray
    exit 1
}

# Testes do Backend
Write-Host "`n2️⃣ Executando Testes Backend (pytest)..." -ForegroundColor Yellow
Set-Location backend
$backendResult = & python -m pytest test_api.py -v
$backendExitCode = $LASTEXITCODE

if ($backendExitCode -eq 0) {
    Write-Host "✅ Testes Backend: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Testes Backend: FALHOU" -ForegroundColor Red
}

# Testes do Frontend  
Write-Host "`n3️⃣ Executando Testes Frontend (vitest)..." -ForegroundColor Yellow
Set-Location ..\web
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
$frontendResult = & npm test
$frontendExitCode = $LASTEXITCODE

if ($frontendExitCode -eq 0) {
    Write-Host "✅ Testes Frontend: PASSOU" -ForegroundColor Green
} else {
    Write-Host "❌ Testes Frontend: FALHOU" -ForegroundColor Red
}

# Resumo
Write-Host "`n📊 RESUMO DOS TESTES:" -ForegroundColor Cyan
Write-Host "Backend:  $(if($backendExitCode -eq 0){'✅ PASSOU'}else{'❌ FALHOU'})" -ForegroundColor $(if($backendExitCode -eq 0){'Green'}else{'Red'})
Write-Host "Frontend: $(if($frontendExitCode -eq 0){'✅ PASSOU'}else{'❌ FALHOU'})" -ForegroundColor $(if($frontendExitCode -eq 0){'Green'}else{'Red'})

if ($backendExitCode -eq 0 -and $frontendExitCode -eq 0) {
    Write-Host "`n🎉 TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n💥 ALGUNS TESTES FALHARAM!" -ForegroundColor Red
    exit 1
}

Set-Location ..