# 🤖 ToDoX + VSCode + Copilot Integration Guide

## Como o Copilot vai trabalhar com o ToDoX

### 1. 🎯 Fluxo Automático de Trabalho

```bash
# 1. Copilot busca próxima tarefa
curl -X POST https://seu-projeto.up.railway.app/projects/1/claim-next \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 100}'

# Resposta:
{
  "task": {
    "id": 15,
    "title": "Implementar sistema de autenticação",
    "description_md": "Criar login/logout com JWT e bcrypt",
    "priority": 1
  },
  "run_id": 456
}

# 2. Copilot executa a tarefa no VSCode
# 3. Copilot finaliza e reporta resultado

curl -X POST https://seu-projeto.up.railway.app/tasks/15/finish \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": 456,
    "status": "SUCCESS",
    "summary_md": "✅ Sistema de auth implementado com JWT",
    "create_pr": true,
    "artifacts": [
      {
        "type": "file",
        "uri": "./auth/login.py",
        "hash": "abc123"
      }
    ]
  }'
```

### 2. 🔄 Comandos VSCode Integrados

Pressione `Ctrl+Shift+P` e digite:

- **"ToDoX: Próxima Tarefa"** - Busca tarefa para trabalhar
- **"ToDoX: Finalizar Tarefa"** - Marca como concluída
- **"ToDoX: Criar Tarefa"** - Adiciona nova tarefa
- **"ToDoX: Listar Projetos"** - Vê todos os projetos

### 3. 🎮 Workflow Exemplo

**Cenário**: Você quer que o Copilot implemente um sistema de chat

```yaml
# 1. Criar projeto no ToDoX (via interface web)
projeto: "Sistema de Chat"

# 2. Definir tarefas:
tasks:
  - title: "Configurar WebSocket server"
    priority: 1
    description: "Implementar servidor WebSocket com Socket.IO"

  - title: "Criar interface de chat"
    priority: 2
    description: "UI em React com input e lista de mensagens"

  - title: "Sistema de salas"
    priority: 3
    description: "Usuários podem criar/entrar em salas"
# 3. No VSCode, Copilot vai:
# - Buscar tarefa 1 automaticamente
# - Implementar o código
# - Fazer commit
# - Marcar como concluída
# - Pegar próxima tarefa
```

### 4. 🌍 Acesso Global

Depois do deploy:

✅ **Você** pode acessar de qualquer lugar:

- Seu notebook pessoal
- Computador do trabalho
- Tablet/celular
- Qualquer VSCode conectado

✅ **Time** pode colaborar:

- Cada dev tem seu agent_id
- Todos veem o mesmo projeto
- Tarefas distribuídas automaticamente

✅ **Monitoramento em tempo real**:

- WebSocket mostra quem está trabalhando em quê
- PRs criados automaticamente
- Histórico completo de execuções

### 5. 🔗 URLs que você vai ter:

Após deploy na Opção 1:

```
Frontend (Dashboard): https://todox-gustavo.vercel.app
Backend API:          https://todox-gustavo.up.railway.app
Documentação:         https://todox-gustavo.up.railway.app/docs
WebSocket:            wss://todox-gustavo.up.railway.app/ws/events
```

### 6. 📱 Acesso Mobile/Web

O ToDoX tem interface web completa:

- ✅ Dashboard de projetos
- ✅ Backlog visual (arrastar e soltar)
- ✅ Board estilo Kanban
- ✅ YAML Studio (editor de tarefas)
- ✅ Monitor de execuções em tempo real
- ✅ Visualização de PRs

### 7. 🤝 Integração com GitHub

```bash
# ToDoX pode criar PRs automaticamente
# Quando Copilot finaliza uma tarefa:

POST /tasks/15/finish
{
  "create_pr": true,
  "pr_title": "feat: Sistema de autenticação JWT",
  "pr_description": "Implementa login/logout com tokens JWT seguros"
}

# Resultado: PR criado automaticamente no GitHub
```

## 🚀 Vamos fazer o deploy?

O ToDoX vai te dar:

- 🌍 **Acesso global** via URLs públicas
- 🤖 **Integração total** com Copilot
- 📊 **Dashboard visual** para acompanhar tudo
- 🔄 **Automação completa** do workflow
- 👥 **Colaboração** em tempo real

**Quer que eu te ajude a fazer o deploy agora?**
