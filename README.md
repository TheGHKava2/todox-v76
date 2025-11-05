# 🚀 ToDoX v76 - Deploy Production

**Sistema de gerenciamento de tarefas com automação via IA/Copilot**

## 🌐 URLs de Produção

- **Frontend**: https://todox-v76.vercel.app
- **Backend API**: https://todox-v76.up.railway.app
- **Documentação**: https://todox-v76.up.railway.app/docs

## ⚡ Quick Start

1. **Acesse o Frontend**: [https://todox-v76.vercel.app](https://todox-v76.vercel.app)
2. **Clique em "Seed Demo"** para criar dados de teste
3. **Explore as funcionalidades**:
   - Dashboard de projetos
   - Backlog e Board de tarefas
   - YAML Studio
   - Sistema de Scaffold
   - Watcher para sync
   - PRs automáticos

## 🤖 Integração VSCode + Copilot

### Configuração Rápida:

1. Clone este repo
2. Abra no VSCode
3. As configurações já estão prontas em `.vscode/`
4. Use `Ctrl+Shift+P` → "ToDoX: Próxima Tarefa"

### Comandos Disponíveis:

- **ToDoX: Próxima Tarefa** - Busca tarefa para trabalhar
- **ToDoX: Finalizar Tarefa** - Marca como concluída
- **ToDoX: Criar Tarefa** - Adiciona nova tarefa
- **ToDoX: Listar Projetos** - Vê todos os projetos

## 📋 Funcionalidades

### ✅ Core

- [x] Gerenciamento de projetos
- [x] Sistema de tarefas com prioridades
- [x] Dependências entre tarefas
- [x] Claims automáticos por agentes
- [x] Estados: TODO → IN_PROGRESS → DONE

### ✅ Automação

- [x] Worker/Agent automático
- [x] Criação de PRs simulados
- [x] Execução de tarefas
- [x] Geração de artefatos

### ✅ Interfaces

- [x] Frontend Next.js completo
- [x] API REST documentada
- [x] WebSocket para tempo real
- [x] Interface simples HTML/JS

### ✅ Integrações

- [x] Import/Export YAML
- [x] Sistema de Scaffold
- [x] Watcher para sync bidirecional
- [x] VSCode Tasks integration

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │    Worker       │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│   (Optional)    │
│                 │    │                 │    │                 │
│ • Next.js 14    │    │ • FastAPI       │    │ • Python        │
│ • React         │    │ • SQLAlchemy    │    │ • Requests      │
│ • Tailwind      │    │ • SQLite        │    │ • Auto Tasks    │
│ • WebSocket     │    │ • SSE Events    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         └──────────────►│   VSCode +      │◄────────────┘
                        │   Copilot       │
                        │                 │
                        │ • Tasks API     │
                        │ • Auto Claims   │
                        │ • PR Creation   │
                        └─────────────────┘
```

## 🔧 Desenvolvimento Local

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd web
npm install
npm run dev

# Worker (opcional)
cd worker
pip install -r requirements.txt
python agent.py --api http://localhost:8000
```

## 🐳 Docker

```bash
docker-compose up -d
```

## 📊 Monitoramento

- **Health Check**: `/docs`
- **Logs**: Ver Railway/Vercel dashboards
- **WebSocket**: Conecta automaticamente
- **Database**: SQLite (Railway volume)

## 🔒 Segurança

- ✅ HTTPS automático (Railway + Vercel)
- ✅ CORS configurado
- ✅ Headers de segurança
- ✅ Environment variables

## 📞 Suporte

- **Documentação**: `/docs` endpoint
- **Issues**: GitHub Issues
- **Chat**: WebSocket `/ws/events`

## 🚀 Roadmap

- [ ] Autenticação JWT
- [ ] Multi-tenancy
- [ ] Integração GitHub real
- [ ] Notifications push
- [ ] Mobile app
- [ ] Analytics dashboard

---

**ToDoX v76** - Automação de tarefas com IA 🤖
