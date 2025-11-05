# 🚀 Script de Deploy TODOX_V76 - Windows PowerShell
# Este script automatiza o processo de deploy local ou em servidor

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("deploy", "stop", "logs", "health", "backup", "help")]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [string]$Mode = "manual",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = "all"
)

# Cores para output
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

# Verificar dependências
function Test-Dependencies {
    Write-Info "Verificando dependências..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker não está instalado!"
        exit 1
    }
    
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose não está instalado!"
        exit 1
    }
    
    Write-Success "Dependências verificadas"
}

# Deploy com Docker
function Start-DockerDeploy {
    Write-Info "Iniciando deploy com Docker..."
    
    # Parar containers existentes
    Write-Info "Parando containers existentes..."
    docker-compose down 2>$null
    
    # Limpar imagens antigas
    Write-Info "Limpando imagens antigas..."
    docker system prune -f
    
    # Construir e iniciar
    Write-Info "Construindo e iniciando containers..."
    docker-compose up -d --build
    
    # Aguardar serviços
    Write-Info "Aguardando serviços ficarem prontos..."
    Start-Sleep 30
    
    # Health check
    Test-ServiceHealth
}

# Deploy manual
function Start-ManualDeploy {
    Write-Info "Iniciando deploy manual..."
    
    # Backend
    Write-Info "Configurando backend..."
    Set-Location backend
    
    if (-not (Test-Path ".venv")) {
        Write-Info "Criando ambiente virtual..."
        python -m venv .venv
    }
    
    & .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    
    # Iniciar backend em background
    Write-Info "Iniciando backend..."
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
    }
    
    Set-Location ..
    
    # Frontend
    Write-Info "Configurando frontend..."
    Set-Location web
    npm install
    npm run build
    
    # Iniciar frontend em background
    Write-Info "Iniciando frontend..."
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npm start
    }
    
    Set-Location ..
    
    # Salvar job IDs
    New-Item -Path "logs" -ItemType Directory -Force | Out-Null
    $backendJob.Id | Out-File "logs\backend.pid" -Encoding UTF8
    $frontendJob.Id | Out-File "logs\frontend.pid" -Encoding UTF8
    
    Start-Sleep 15
    Test-ServiceHealth
}

# Verificar saúde dos serviços
function Test-ServiceHealth {
    Write-Info "Verificando saúde dos serviços..."
    
    # Backend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend está funcionando (http://localhost:8000)"
        }
    }
    catch {
        Write-Error "Backend não está respondendo!"
        return $false
    }
    
    # Frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Frontend está funcionando (http://localhost:3000)"
        }
    }
    catch {
        Write-Error "Frontend não está respondendo!"
        return $false
    }
    
    # Nginx (se Docker)
    if ((Get-Command docker -ErrorAction SilentlyContinue) -and (docker ps --format "table {{.Names}}" | Select-String "nginx")) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "Nginx está funcionando (http://localhost)"
            }
        }
        catch {
            Write-Warning "Nginx não está respondendo"
        }
    }
    
    return $true
}

# Parar serviços
function Stop-Services {
    param([string]$DeployMode)
    
    Write-Info "Parando serviços..."
    
    if ($DeployMode -eq "docker") {
        docker-compose down
    }
    else {
        # Parar jobs manuais
        if (Test-Path "logs\backend.pid") {
            $backendJobId = Get-Content "logs\backend.pid"
            Stop-Job -Id $backendJobId -ErrorAction SilentlyContinue
            Remove-Job -Id $backendJobId -ErrorAction SilentlyContinue
            Remove-Item "logs\backend.pid" -ErrorAction SilentlyContinue
        }
        
        if (Test-Path "logs\frontend.pid") {
            $frontendJobId = Get-Content "logs\frontend.pid"
            Stop-Job -Id $frontendJobId -ErrorAction SilentlyContinue
            Remove-Job -Id $frontendJobId -ErrorAction SilentlyContinue
            Remove-Item "logs\frontend.pid" -ErrorAction SilentlyContinue
        }
    }
    
    Write-Success "Serviços parados"
}

# Mostrar logs
function Show-Logs {
    param([string]$DeployMode, [string]$ServiceName)
    
    if ($DeployMode -eq "docker") {
        if ($ServiceName -ne "all") {
            docker-compose logs -f $ServiceName
        } else {
            docker-compose logs -f
        }
    }
    else {
        Write-Info "Logs dos serviços manuais:"
        if (Test-Path "logs\backend.pid") {
            $backendJobId = Get-Content "logs\backend.pid"
            Write-Host "Backend Job ID: $backendJobId" -ForegroundColor Cyan
            Receive-Job -Id $backendJobId -Keep
        }
        
        if (Test-Path "logs\frontend.pid") {
            $frontendJobId = Get-Content "logs\frontend.pid"
            Write-Host "Frontend Job ID: $frontendJobId" -ForegroundColor Cyan
            Receive-Job -Id $frontendJobId -Keep
        }
    }
}

# Backup do banco
function Backup-Database {
    Write-Info "Criando backup do banco de dados..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backups\db_backup_$timestamp.db"
    
    New-Item -Path "backups" -ItemType Directory -Force | Out-Null
    
    if (Test-Path "data\app.db") {
        Copy-Item "data\app.db" $backupFile
        Write-Success "Backup criado: $backupFile"
    }
    else {
        Write-Warning "Banco de dados não encontrado"
    }
}

# Menu de ajuda
function Show-Help {
    Write-Host "🚀 TODOX_V76 Deploy Script - PowerShell" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso: .\deploy.ps1 -Command <comando> [-Mode <modo>] [-Service <serviço>]" -ForegroundColor White
    Write-Host ""
    Write-Host "Comandos:" -ForegroundColor Yellow
    Write-Host "  deploy    - Fazer deploy (usar -Mode docker ou manual)"
    Write-Host "  stop      - Parar serviços"
    Write-Host "  logs      - Mostrar logs"
    Write-Host "  health    - Verificar saúde dos serviços"
    Write-Host "  backup    - Backup do banco de dados"
    Write-Host "  help      - Mostrar esta ajuda"
    Write-Host ""
    Write-Host "Exemplos:" -ForegroundColor Green
    Write-Host "  .\deploy.ps1 -Command deploy -Mode docker"
    Write-Host "  .\deploy.ps1 -Command deploy -Mode manual"
    Write-Host "  .\deploy.ps1 -Command stop"
    Write-Host "  .\deploy.ps1 -Command logs -Mode docker -Service backend"
    Write-Host "  .\deploy.ps1 -Command health"
    Write-Host "  .\deploy.ps1 -Command backup"
}

# Criar diretórios necessários
New-Item -Path "logs", "data", "backups" -ItemType Directory -Force | Out-Null

# Processar comandos
switch ($Command) {
    "deploy" {
        if ($Mode -eq "docker") {
            Test-Dependencies
        }
        Backup-Database
        
        if ($Mode -eq "docker") {
            Start-DockerDeploy
        }
        else {
            Start-ManualDeploy
        }
    }
    "stop" {
        Stop-Services $Mode
    }
    "logs" {
        Show-Logs $Mode $Service
    }
    "health" {
        Test-ServiceHealth
    }
    "backup" {
        Backup-Database
    }
    "help" {
        Show-Help
    }
}

Write-Success "Operação concluída!"