# 🚀 DEPLOY FINAL - Conectando Frontend ao Backend

Write-Host "🔗 CONECTANDO FRONTEND AO BACKEND" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

$backendUrl = "https://todox-production.up.railway.app"
$frontendUrl = "https://todox-r8tp7xyk9-gustavos-projects-f036da2e.vercel.app"

Write-Host "🌐 URLs IDENTIFICADAS:" -ForegroundColor Cyan
Write-Host "   Backend:  $backendUrl" -ForegroundColor White
Write-Host "   Frontend: $frontendUrl" -ForegroundColor White
Write-Host ""

# Configurar CORS no Railway
Write-Host "🔧 CONFIGURANDO CORS NO RAILWAY..." -ForegroundColor Yellow
Set-Location "..\backend"
railway variables set CORS_ORIGINS="$frontendUrl,http://localhost:3000"

Write-Host "✅ CORS configurado!" -ForegroundColor Green
Write-Host ""

# Configurar variável de ambiente no Vercel
Write-Host "🔧 CONFIGURANDO API URL NO VERCEL..." -ForegroundColor Yellow
Set-Location "..\web"

# Usar a CLI do Vercel para definir a variável
$env:VERCEL_ENV_VALUE = $backendUrl
vercel env add NEXT_PUBLIC_API_URL --value $backendUrl --environment production --yes

Write-Host "✅ API URL configurada!" -ForegroundColor Green
Write-Host ""

# Fazer redeploy do frontend
Write-Host "🚀 FAZENDO REDEPLOY DO FRONTEND..." -ForegroundColor Yellow
vercel --prod

Write-Host ""
Write-Host "🎉 DEPLOY COMPLETO!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 SEUS LINKS FINAIS:" -ForegroundColor Cyan
Write-Host "   Frontend: $frontendUrl" -ForegroundColor White
Write-Host "   Backend:  $backendUrl" -ForegroundColor White
Write-Host "   API Docs: $backendUrl/docs" -ForegroundColor White
Write-Host ""

# Abrir aplicação
Write-Host "🌐 Abrindo aplicação..." -ForegroundColor Cyan
Start-Process $frontendUrl
Start-Process "$backendUrl/docs"

Write-Host "✨ MISSÃO CUMPRIDA! ✨" -ForegroundColor Green