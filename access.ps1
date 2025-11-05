# 🌐 ACESSO RÁPIDO - ToDoX V76
# Este script abre automaticamente o ToDoX no seu navegador

Write-Host "🚀 ABRINDO ToDoX V76..." -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""

Write-Host "🔧 Verificando serviços..." -ForegroundColor Cyan

# Verificar se backend está rodando
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✅ Backend: ONLINE (http://localhost:8000)" -ForegroundColor Green
    $backendOnline = $true
} catch {
    Write-Host "   ❌ Backend: OFFLINE" -ForegroundColor Red
    Write-Host "      💡 Execute: cd backend; uvicorn main:app --reload" -ForegroundColor Yellow
    $backendOnline = $false
}

# Verificar se frontend está rodando
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✅ Frontend: ONLINE (http://localhost:3000)" -ForegroundColor Green
    $frontendOnline = $true
} catch {
    Write-Host "   ❌ Frontend: OFFLINE" -ForegroundColor Red
    Write-Host "      💡 Execute: cd web; npm run dev" -ForegroundColor Yellow
    $frontendOnline = $false
}

Write-Host ""

if ($backendOnline) {
    Write-Host "🌐 ABRINDO PÁGINAS DO ToDoX..." -ForegroundColor Green
    Write-Host ""
    
    # Abrir API Documentation
    Write-Host "📚 Abrindo API Documentation..." -ForegroundColor Cyan
    Start-Process "http://localhost:8000/docs"
    Start-Sleep 2
    
    if ($frontendOnline) {
        # Abrir Frontend
        Write-Host "🎨 Abrindo Interface Web..." -ForegroundColor Cyan
        Start-Process "http://localhost:3000"
    } else {
        # Abrir página de acesso local
        Write-Host "📋 Abrindo página de acesso..." -ForegroundColor Cyan
        $accessPath = "file:///" + (Get-Location).Path.Replace('\', '/') + "/access.html"
        Start-Process $accessPath
    }
    
    Write-Host ""
    Write-Host "✅ ToDoX V76 ABERTO NO NAVEGADOR!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 URLS DISPONÍVEIS:" -ForegroundColor Yellow
    Write-Host "   🌐 Frontend:  http://localhost:3000" -ForegroundColor White
    Write-Host "   🔧 Backend:   http://localhost:8000" -ForegroundColor White
    Write-Host "   📚 API Docs:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   📋 Swagger:   http://localhost:8000/redoc" -ForegroundColor White
    
} else {
    Write-Host "❌ BACKEND NÃO ESTÁ RODANDO!" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Para iniciar o ToDoX, execute:" -ForegroundColor Yellow
    Write-Host "   1. cd backend" -ForegroundColor White
    Write-Host "   2. uvicorn main:app --reload" -ForegroundColor White
    Write-Host "   3. .\access.ps1" -ForegroundColor White
}

Write-Host ""
Write-Host "🎉 DIVIRTA-SE USANDO O ToDoX V76!" -ForegroundColor Green