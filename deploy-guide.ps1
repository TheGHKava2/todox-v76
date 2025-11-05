# 🚀 Script de Preparação para Deploy - Vercel + Railway

Write-Host "🚀 TODOX_V76 Deploy Preparation Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Função para mostrar mensagens coloridas
function Write-Info { Write-Host "ℹ️  $($args -join ' ')" -ForegroundColor Blue }
function Write-Success { Write-Host "✅ $($args -join ' ')" -ForegroundColor Green }
function Write-Warning { Write-Host "⚠️  $($args -join ' ')" -ForegroundColor Yellow }

Write-Info "Verificando pré-requisitos..."

# Verificar Node.js
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Success "Node.js: $nodeVersion"
} else {
    Write-Warning "Node.js não encontrado"
}

# Verificar Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Success "Python: $pythonVersion"
} else {
    Write-Warning "Python não encontrado"
}

Write-Host ""
Write-Host "📋 CHECKLIST DE DEPLOY:" -ForegroundColor Yellow
Write-Host "========================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. RAILWAY (Backend):" -ForegroundColor Cyan
Write-Host "   ✓ Acesse: https://railway.app"
Write-Host "   ✓ New Project → Deploy from GitHub"
Write-Host "   ✓ Conecte seu repositório todox_v76"
Write-Host "   ✓ Configure Root Directory: backend/"
Write-Host "   ✓ Start Command: uvicorn main:app --host 0.0.0.0 --port `$PORT"
Write-Host ""

Write-Host "2. VARIÁVEIS DE AMBIENTE - RAILWAY:" -ForegroundColor Cyan
Write-Host "   PYTHONUNBUFFERED=1"
Write-Host "   DB_PATH=/app/data/app.db"
Write-Host "   CORS_ORIGINS=http://localhost:3000"
Write-Host ""

Write-Host "3. VERCEL (Frontend):" -ForegroundColor Cyan
Write-Host "   ✓ Acesse: https://vercel.com"
Write-Host "   ✓ New Project → Import from GitHub"
Write-Host "   ✓ Selecione seu repositório todox_v76"
Write-Host "   ✓ Configure Root Directory: web/"
Write-Host "   ✓ Framework Preset: Next.js"
Write-Host ""

Write-Host "4. VARIÁVEIS DE AMBIENTE - VERCEL:" -ForegroundColor Cyan
Write-Host "   NEXT_PUBLIC_API_URL=https://seu-projeto.railway.app"
Write-Host "   NODE_ENV=production"
Write-Host ""

Write-Host "5. APÓS AMBOS OS DEPLOYS:" -ForegroundColor Yellow
Write-Host "   ✓ Copie a URL do Railway (ex: https://todox-backend.railway.app)"
Write-Host "   ✓ Atualize NEXT_PUBLIC_API_URL no Vercel"
Write-Host "   ✓ Copie a URL do Vercel (ex: https://todox.vercel.app)"
Write-Host "   ✓ Atualize CORS_ORIGINS no Railway"
Write-Host "   ✓ Force redeploy em ambos os serviços"
Write-Host ""

Write-Host "📖 GUIA DETALHADO:" -ForegroundColor Green
Write-Host "   Arquivo: DEPLOY_VERCEL_RAILWAY.md"
Write-Host ""

Write-Host "🔧 COMANDOS DE TESTE LOCAL:" -ForegroundColor Magenta
Write-Host "   cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
Write-Host "   cd web && npm run build && npm start"
Write-Host ""

Write-Success "Script concluído! Siga o checklist acima para fazer o deploy."