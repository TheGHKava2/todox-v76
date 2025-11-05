# 🚀 Deploy ToDoX V76 - Instruções Completas

## ✅ Status: Código no GitHub

**Repositório:** https://github.com/TheGHKava2/todox-v76

## 🎯 Deploy Automatizado (Railway + Vercel)

### 1. 🚂 Deploy Backend no Railway

1. **Acesse:** https://railway.app/
2. **Login com GitHub** (use sua conta TheGHKava2)
3. **New Project** → **Deploy from GitHub repo**
4. **Selecione:** `TheGHKava2/todox-v76`
5. **Configure:**

   - **Root Directory:** `backend/`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. **Environment Variables:**

   ```
   PORT=8000
   DATABASE_URL=sqlite:///./todox.db
   ENVIRONMENT=production
   ```

7. **Deploy** → Aguarde conclusão
8. **Copie a URL do backend** (ex: `https://backend-production-xxxx.up.railway.app`)

### 2. 🌐 Deploy Frontend no Vercel

1. **Acesse:** https://vercel.com/
2. **Login com GitHub** (use sua conta TheGHKava2)
3. **New Project** → **Import Git Repository**
4. **Selecione:** `TheGHKava2/todox-v76`
5. **Configure:**

   - **Framework Preset:** Next.js
   - **Root Directory:** `web/`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

6. **Environment Variables:**

   ```
   NEXT_PUBLIC_API_URL=https://SEU-BACKEND-URL.up.railway.app
   ```

   (Substitua pela URL do Railway do passo anterior)

7. **Deploy** → Aguarde conclusão
8. **Sua aplicação estará disponível!** 🎉

### 3. 🔧 Teste Final

- **Frontend:** URL fornecida pelo Vercel
- **Backend API:** URL do Railway + `/docs`
- **Health Check:** URL do Railway + `/health`

## 🎯 Acesso Global e Integração VSCode

✅ **Sim! Você conseguirá:**

1. **Acessar de qualquer lugar** via URLs públicas
2. **Integrar com VSCode** usando os tasks em `.vscode/tasks.json`
3. **Usar com Copilot** através das APIs REST
4. **Automatizar tarefas** via worker/agent system

## 📋 Próximos Passos

1. Execute o deploy seguindo as instruções acima
2. Configure as URLs de produção
3. Teste todas as funcionalidades
4. Comece a usar no seu workflow VSCode + Copilot!

## 🆘 Suporte

Se precisar de ajuda durante o deploy, me avise e posso orientar cada passo!
