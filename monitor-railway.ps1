# 🔄 Script de Monitoramento Railway

Write-Host "🔍 Monitorando Railway Backend..."
Write-Host "URL: https://todox-production.up.railway.app"
Write-Host "Frontend: https://todox-ps7kl945j-gustavos-projects-f036da2e.vercel.app"
Write-Host ""

$count = 0
$maxTries = 20
$waitSeconds = 30

while ($count -lt $maxTries) {
    $count++
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    try {
        $response = Invoke-WebRequest "https://todox-production.up.railway.app/" -TimeoutSec 10
        Write-Host "[$timestamp] ✅ SUCESSO! Backend online - Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 BACKEND FUNCIONANDO!" -ForegroundColor Green
        Write-Host "🎯 Teste o frontend agora: https://todox-ps7kl945j-gustavos-projects-f036da2e.vercel.app"
        break
    }
    catch {
        Write-Host "[$timestamp] ❌ Tentativa $count/$maxTries - Backend offline" -ForegroundColor Yellow
        if ($count -lt $maxTries) {
            Write-Host "   Aguardando $waitSeconds segundos..."
            Start-Sleep $waitSeconds
        }
    }
}

if ($count -eq $maxTries) {
    Write-Host ""
    Write-Host "⚠️  Railway não respondeu após $maxTries tentativas" -ForegroundColor Red
    Write-Host "🔧 Ações recomendadas:"
    Write-Host "   1. Acessar: https://railway.app/dashboard"
    Write-Host "   2. Projeto: todox → Restart Service"
    Write-Host "   3. Ou aguardar mais 10-15 minutos"
}