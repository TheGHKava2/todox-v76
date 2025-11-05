# Quick Test Script - ToDoX Validation
# Executa testes automatizados básicos

Write-Host "🧪 Iniciando Validação Automatizada - ToDoX" -ForegroundColor Green

# Test 1: Backend Health
Write-Host "`n1️⃣ Testando Backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET
    Write-Host "✅ Backend OK: $($health.service)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend falhou: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Projects API
Write-Host "`n2️⃣ Testando API de Projetos..." -ForegroundColor Yellow
try {
    $projects = Invoke-RestMethod -Uri "http://127.0.0.1:8000/projects" -Method GET
    Write-Host "✅ Projetos carregados: $($projects.Count) projetos encontrados" -ForegroundColor Green
} catch {
    Write-Host "❌ API de projetos falhou: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Create Test Project
Write-Host "`n3️⃣ Criando Projeto de Teste..." -ForegroundColor Yellow
try {
    $newProject = @{
        name = "Projeto Validação Automática $(Get-Date -Format 'HHmmss')"
    } | ConvertTo-Json

    $created = Invoke-RestMethod -Uri "http://127.0.0.1:8000/projects" -Method POST -Body $newProject -ContentType "application/json"
    Write-Host "✅ Projeto criado: ID $($created.id) - $($created.name)" -ForegroundColor Green
    
    # Test 4: Create Tasks for the project
    Write-Host "`n4️⃣ Adicionando Tarefas..." -ForegroundColor Yellow
    
    $tasks = @(
        "Tarefa 1 - Teste Automático",
        "Tarefa 2 - Validação API", 
        "Tarefa 3 - Verificação Sistema"
    )
    
    foreach ($taskTitle in $tasks) {
        $newTask = @{
            title = $taskTitle
            priority = 3
            description_md = "Tarefa criada automaticamente para validação"
        } | ConvertTo-Json
        
        $taskCreated = Invoke-RestMethod -Uri "http://127.0.0.1:8000/projects/$($created.id)/tasks" -Method POST -Body $newTask -ContentType "application/json"
        Write-Host "  ✅ Tarefa criada: $($taskCreated.title)" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Criação de projeto/tarefas falhou: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Frontend Check
Write-Host "`n5️⃣ Verificando Frontend..." -ForegroundColor Yellow
try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3001" -Method GET -TimeoutSec 10
    if ($frontendCheck.StatusCode -eq 200) {
        Write-Host "✅ Frontend respondendo (Status: $($frontendCheck.StatusCode))" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend não responde: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Próximos Passos Manuais:" -ForegroundColor Cyan
Write-Host "1. Abrir http://localhost:3001" -ForegroundColor White
Write-Host "2. Verificar se o projeto criado aparece na lista" -ForegroundColor White
Write-Host "3. Clicar no projeto e verificar as tarefas" -ForegroundColor White
Write-Host "4. Testar drag & drop em http://localhost:3001/board" -ForegroundColor White
Write-Host "5. Verificar outras páginas (backlog, scaffold, etc.)" -ForegroundColor White

Write-Host "`n📋 Para guia completo:" -ForegroundColor Cyan
Write-Host "   Consulte: .\GUIA_VALIDACAO.md" -ForegroundColor White

Write-Host "`n✅ Validação automatizada concluída!" -ForegroundColor Green