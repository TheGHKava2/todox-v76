# 🚀 Script de Deploy Automatizado ToDoX V76
# Execute este script para orientações passo-a-passo

Write-Host "🎉 ToDoX V76 - Deploy Automatizado" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

Write-Host "✅ Código já está no GitHub:" -ForegroundColor Yellow
Write-Host "   https://github.com/TheGHKava2/todox-v76" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚂 PASSO 1: Deploy Backend (Railway)" -ForegroundColor Yellow
Write-Host "   1. Abra: https://railway.app/" -ForegroundColor White
Write-Host "   2. Login com GitHub (TheGHKava2)" -ForegroundColor White
Write-Host "   3. New Project → Deploy from GitHub repo" -ForegroundColor White
Write-Host "   4. Selecione: TheGHKava2/todox-v76" -ForegroundColor White
Write-Host "   5. Configure:" -ForegroundColor White
Write-Host "      - Root Directory: backend/" -ForegroundColor Gray
Write-Host "      - Start Command: uvicorn main:app --host 0.0.0.0 --port `$PORT" -ForegroundColor Gray
Write-Host "   6. Environment Variables:" -ForegroundColor White
Write-Host "      PORT=8000" -ForegroundColor Gray
Write-Host "      DATABASE_URL=sqlite:///./todox.db" -ForegroundColor Gray
Write-Host "      ENVIRONMENT=production" -ForegroundColor Gray
Write-Host ""

Write-Host "🌐 PASSO 2: Deploy Frontend (Vercel)" -ForegroundColor Yellow
Write-Host "   1. Abra: https://vercel.com/" -ForegroundColor White
Write-Host "   2. Login com GitHub (TheGHKava2)" -ForegroundColor White
Write-Host "   3. New Project → Import Git Repository" -ForegroundColor White
Write-Host "   4. Selecione: TheGHKava2/todox-v76" -ForegroundColor White
Write-Host "   5. Configure:" -ForegroundColor White
Write-Host "      - Framework: Next.js" -ForegroundColor Gray
Write-Host "      - Root Directory: web/" -ForegroundColor Gray
Write-Host "   6. Environment Variable:" -ForegroundColor White
Write-Host "      NEXT_PUBLIC_API_URL=https://SEU-BACKEND-URL.up.railway.app" -ForegroundColor Gray
Write-Host ""

Write-Host "🎯 RESULTADO:" -ForegroundColor Green
Write-Host "   ✅ Acesso global de qualquer lugar" -ForegroundColor White
Write-Host "   ✅ Integração VSCode/Copilot funcional" -ForegroundColor White
Write-Host "   ✅ Sistema completo na nuvem" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Pronto para começar o deploy?" -ForegroundColor Green
Write-Host "   Abra os links acima e siga as instruções!" -ForegroundColor Cyan
Write-Host ""

# Abrir os sites automaticamente
Write-Host "⚡ Abrindo sites automaticamente..." -ForegroundColor Yellow
Start-Process "https://railway.app/"
Start-Sleep 2
Start-Process "https://vercel.com/"
Start-Sleep 2
Start-Process "https://github.com/TheGHKava2/todox-v76"

Write-Host "✨ Sites abertos! Bom deploy! 🚀" -ForegroundColor Green