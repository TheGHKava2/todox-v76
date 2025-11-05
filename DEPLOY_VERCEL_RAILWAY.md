# 🚀 Guia de Deploy - Vercel + Railway

## 📋 Pré-requisitos Concluídos ✅
- ✅ Contas criadas no Vercel e Railway
- ✅ Código configurado para produção
- ✅ Arquivos de configuração criados

## 🚂 Parte 1: Deploy do Backend no Railway

### 1.1 Configuração Inicial
1. **Acesse Railway:** https://railway.app
2. **Novo Projeto:** Clique em "New Project"
3. **Conectar GitHub:** Escolha "Deploy from GitHub repo"
4. **Selecionar Repositório:** Escolha seu repositório `todox_v76`

### 1.2 Configuração do Serviço Backend
1. **Root Directory:** Configure para `backend/` (importante!)
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 1.3 Variáveis de Ambiente no Railway
Configure as seguintes variáveis na aba "Variables":

```bash
# Obrigatórias
PYTHONUNBUFFERED=1
DB_PATH=/app/data/app.db

# Será atualizada após deploy do Vercel
CORS_ORIGINS=http://localhost:3000

# Opcional (Railway fornece automaticamente)
PORT=8000
```

### 1.4 Configurar Volume (Banco de Dados)
1. **Aba "Data":** Adicione um volume
2. **Mount Path:** `/app/data`
3. **Isso garantirá persistência do SQLite**

## ▲ Parte 2: Deploy do Frontend no Vercel

### 2.1 Configuração Inicial
1. **Acesse Vercel:** https://vercel.com
2. **Novo Projeto:** Clique em "New Project"
3. **Import Git Repository:** Conecte seu GitHub
4. **Selecionar Repositório:** Escolha `todox_v76`

### 2.2 Configuração do Build
1. **Framework Preset:** Next.js
2. **Root Directory:** `web/`
3. **Build Command:** `npm run build`
4. **Output Directory:** `.next`
5. **Install Command:** `npm install`

### 2.3 Variáveis de Ambiente no Vercel
Configure na seção "Environment Variables":

```bash
# URL do seu backend Railway (obtenha após deploy do Railway)
NEXT_PUBLIC_API_URL=https://seu-projeto.railway.app
NODE_ENV=production
```

## 🔄 Parte 3: Conectar os Serviços

### 3.1 Obter URL do Railway
1. Após deploy do Railway, copie a URL do domínio
2. Exemplo: `https://todox-backend-production.railway.app`

### 3.2 Atualizar Vercel
1. **Variáveis:** Atualize `NEXT_PUBLIC_API_URL` com a URL do Railway
2. **Redeploy:** Force um novo deploy

### 3.3 Atualizar Railway
1. **Variáveis:** Atualize `CORS_ORIGINS` com a URL do Vercel
2. **Exemplo:** `https://seu-app.vercel.app,http://localhost:3000`
3. **Redeploy:** Force um novo deploy

## 📋 Comandos de Preparação

Execute estes comandos antes do deploy:

```powershell
# 1. Teste final local
cd d:\todox_v76\web
npm run build
npm start

# 2. Teste backend
cd d:\todox_v76\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Commit e push (se necessário)
git add .
git commit -m "feat: production config for Vercel + Railway"
git push origin main
```

## 🔧 Configurações Específicas

### Railway - nixpacks.toml (opcional)
```toml
[phases.setup]
nixPkgs = ['python311', 'pip']

[phases.install]
cmds = ['pip install -r requirements.txt']

[phases.build]
cmds = ['echo "No build step"']

[start]
cmd = 'uvicorn main:app --host 0.0.0.0 --port $PORT'
```

### Vercel - Headers de Segurança
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000"
        }
      ]
    }
  ]
}
```

## 🚨 Troubleshooting

### Problemas Comuns Railway:
```bash
# Build falha
- Verificar se requirements.txt está correto
- Conferir se root directory está como "backend/"

# App não inicia
- Verificar start command: uvicorn main:app --host 0.0.0.0 --port $PORT
- Conferir logs no Railway dashboard

# Banco não persiste
- Verificar se volume está montado em /app/data
- Verificar DB_PATH=/app/data/app.db
```

### Problemas Comuns Vercel:
```bash
# Build falha
- Verificar se root directory está como "web/"
- Conferir se todas as dependências estão no package.json

# API não conecta
- Verificar NEXT_PUBLIC_API_URL
- Conferir CORS no backend Railway
```

## 📊 Monitoramento

### URLs Finais:
- **Frontend:** `https://seu-app.vercel.app`
- **Backend:** `https://seu-projeto.railway.app`
- **API Docs:** `https://seu-projeto.railway.app/docs`

### Health Checks:
```bash
# Frontend
curl https://seu-app.vercel.app

# Backend
curl https://seu-projeto.railway.app/docs

# API Test
curl https://seu-projeto.railway.app/api/projects
```

## 💡 Próximos Passos

1. **Custom Domain:** Configure domínio personalizado
2. **SSL:** Ambos provêm SSL automático
3. **Analytics:** Configure Vercel Analytics
4. **Database:** Migre para PostgreSQL no Railway se necessário
5. **CI/CD:** Configure deploy automático no git push

## 💰 Custos Estimados

- **Vercel:** Gratuito (hobby plan)
- **Railway:** $5/mês (uso básico)
- **Total:** ~$5/mês

---

**🎯 Resultado Final:**
- Frontend Next.js rodando no Vercel
- Backend FastAPI rodando no Railway  
- Comunicação HTTPS segura entre ambos
- Deploy automático no git push
- SSL gratuito em ambos
- Domínios personalizados disponíveis