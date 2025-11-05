# 🚀 Script de Preparação para Deploy - Vercel + Railway
# Execute este script antes de fazer o deploy

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("prepare", "test", "build", "help")]
    [string]$Action = "help"
)

function Write-Info { 
    Write-Host "ℹ️  $args" -ForegroundColor Blue 
}

function Write-Success { 
    Write-Host "✅ $args" -ForegroundColor Green 
}

function Write-Warning { 
    Write-Host "⚠️  $args" -ForegroundColor Yellow 
}

function Write-Error { 
    Write-Host "❌ $args" -ForegroundColor Red 
}

function Test-Prerequisites {
    Write-Info "Verificando pré-requisitos..."
    
    # Verificar Node.js
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Error "Node.js não está instalado!"
        return $false
    }
    
    # Verificar Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python não está instalado!"
        return $false
    }
    
    # Verificar Git
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "Git não está instalado!"
        return $false
    }
    
    Write-Success "Pré-requisitos verificados"
    return $true
}

function Prepare-Backend {
    Write-Info "Preparando backend para produção..."
    
    Set-Location backend
    
    # Verificar se o ambiente virtual existe
    if (-not (Test-Path ".venv")) {
        Write-Warning "Ambiente virtual não encontrado. Criando..."
        python -m venv .venv
    }
    
    # Ativar ambiente virtual
    & .\.venv\Scripts\Activate.ps1
    
    # Instalar dependências
    Write-Info "Instalando dependências do backend..."
    pip install -r requirements.txt
    
    # Testar importação
    Write-Info "Testando importação do main..."
    python -c "import main; print('✅ Import successful')"
    
    Set-Location ..
    Write-Success "Backend preparado"
}

function Prepare-Frontend {
    Write-Info "Preparando frontend para produção..."
    
    Set-Location web
    
    # Instalar dependências
    Write-Info "Instalando dependências do frontend..."
    npm install
    
    # Testar build
    Write-Info "Testando build de produção..."
    npm run build
    
    Set-Location ..
    Write-Success "Frontend preparado"
}

function Test-Production {
    Write-Info "Testando configuração de produção..."
    
    # Testar backend
    Write-Info "Testando backend..."
    Set-Location backend
    
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
    }
    
    Set-Location ..
    
    # Aguardar backend iniciar
    Start-Sleep 10
    
    # Testar se backend está respondendo
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend está funcionando"
        }
    }
    catch {
        Write-Error "Backend não está respondendo"
    }
    
    # Testar frontend
    Write-Info "Testando frontend..."
    Set-Location web
    
    $env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npm start
    }
    
    Set-Location ..
    
    # Aguardar frontend iniciar
    Start-Sleep 15
    
    # Testar se frontend está respondendo
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Frontend está funcionando"
        }
    }
    catch {
        Write-Error "Frontend não está respondendo"
    }
    
    # Limpar jobs
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
}

function Build-Production {
    Write-Info "Criando build de produção..."
    
    # Build backend (verificação)
    Write-Info "Verificando backend..."
    Set-Location backend
    python -c "import main; print('Backend OK')"
    Set-Location ..
    
    # Build frontend
    Write-Info "Criando build do frontend..."
    Set-Location web
    $env:NEXT_PUBLIC_API_URL = "https://your-railway-backend.railway.app"
    npm run build
    Set-Location ..
    
    Write-Success "Build de produção concluído"
}

function Show-DeployGuide {
    Write-Host ""
    Write-Host "🚀 Guia de Deploy - Vercel + Railway" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. RAILWAY (Backend):" -ForegroundColor Yellow
    Write-Host "   • Acesse: https://railway.app"
    Write-Host "   • New Project → Deploy from GitHub"
    Write-Host "   • Root Directory: backend/"
    Write-Host "   • Start Command: uvicorn main:app --host 0.0.0.0 --port `$PORT"
    Write-Host ""
    Write-Host "2. VARIÁVEIS RAILWAY:" -ForegroundColor Yellow
    Write-Host "   • PYTHONUNBUFFERED=1"
    Write-Host "   • DB_PATH=/app/data/app.db"
    Write-Host "   • CORS_ORIGINS=http://localhost:3000"
    Write-Host ""
    Write-Host "3. VERCEL (Frontend):" -ForegroundColor Yellow
    Write-Host "   • Acesse: https://vercel.com"
    Write-Host "   • New Project → Import from GitHub"
    Write-Host "   • Root Directory: web/"
    Write-Host "   • Framework: Next.js"
    Write-Host ""
    Write-Host "4. VARIÁVEIS VERCEL:" -ForegroundColor Yellow
    Write-Host "   • NEXT_PUBLIC_API_URL=https://seu-projeto.railway.app"
    Write-Host "   • NODE_ENV=production"
    Write-Host ""
    Write-Host "5. APÓS DEPLOY:" -ForegroundColor Yellow
    Write-Host "   • Atualize CORS_ORIGINS no Railway com URL do Vercel"
    Write-Host "   • Teste as URLs finais"
    Write-Host ""
    Write-Host "📖 Guia completo: DEPLOY_VERCEL_RAILWAY.md" -ForegroundColor Green
}

# Menu principal
switch ($Action) {
    "prepare" {
        if (Test-Prerequisites) {
            Prepare-Backend
            Prepare-Frontend
            Write-Success "Preparação concluída! Execute 'test' para verificar."
        }
    }
    "test" {
        Test-Production
    }
    "build" {
        Build-Production
    }
    "help" {
        Show-DeployGuide
        Write-Host ""
        Write-Host "Comandos disponíveis:" -ForegroundColor Cyan
        Write-Host "  .\deploy-cloud.ps1 -Action prepare  # Preparar para deploy"
        Write-Host "  .\deploy-cloud.ps1 -Action test     # Testar localmente"
        Write-Host "  .\deploy-cloud.ps1 -Action build    # Build de produção"
        Write-Host "  .\deploy-cloud.ps1 -Action help     # Mostrar este guia"
    }
}