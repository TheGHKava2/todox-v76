# 🚀 DEPLOY REAL - VERCEL CLI

Write-Host "🔧 INSTALANDO VERCEL CLI..." -ForegroundColor Yellow

# Verificar se npm está disponível
try {
    npm --version | Out-Null
    Write-Host "✅ NPM encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ NPM não encontrado. Instale Node.js primeiro." -ForegroundColor Red
    exit 1
}

# Instalar Vercel CLI globalmente
Write-Host "📦 Instalando Vercel CLI..." -ForegroundColor Cyan
npm install -g vercel

Write-Host ""
Write-Host "🌐 FAZENDO DEPLOY REAL NO VERCEL..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Navegar para o diretório do frontend
Set-Location "web"

Write-Host "📁 Diretório atual: web/" -ForegroundColor Cyan
Write-Host "🔧 Iniciando deploy com Vercel CLI..." -ForegroundColor Yellow

# Fazer deploy usando Vercel CLI
vercel --prod

Write-Host ""
Write-Host "✅ DEPLOY VERCEL REAL CONCLUÍDO!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Voltar ao diretório raiz
Set-Location ".."

Write-Host ""
Write-Host "🎯 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. O Vercel CLI deve ter mostrado a URL real do deploy" -ForegroundColor White
Write-Host "2. Configure essa URL no Railway como CORS_ORIGINS" -ForegroundColor White
Write-Host "3. Acesse a URL fornecida pelo Vercel" -ForegroundColor White