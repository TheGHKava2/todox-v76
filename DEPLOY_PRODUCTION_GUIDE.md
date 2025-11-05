# 🚀 Guia de Deploy em Produção - ToDoX V76

## ✅ Status Atual

- ✅ **Código:** Todas as melhorias comitadas e enviadas ao GitHub
- ✅ **Testes:** Backend (5/5) e Frontend (7/7) passando
- ✅ **UX:** Sistema completo de toast, loading states e validação
- ✅ **Configuração:** Arquivos de produção prontos
- ✅ **Repositório:** https://github.com/TheGHKava2/todox-v76

## 🎯 Plano de Deploy

### Fase 1: Deploy do Backend (Railway) ⏱️ ~5 minutos

1. **Acesse Railway**

   ```
   🌐 URL: https://railway.app/
   👤 Login: TheGHKava2 (GitHub)
   ```

2. **Criar Novo Projeto**

   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha: `TheGHKava2/todox-v76`

3. **Configuração do Serviço**

   ```
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Variáveis de Ambiente**

   ```
   PYTHONUNBUFFERED=1
   DATABASE_URL=sqlite:///app/data/app.db
   CORS_ORIGINS=https://localhost:3000
   LOG_LEVEL=INFO
   ```

5. **⚠️ IMPORTANTE: Anote a URL do Railway**
   - Exemplo: `https://todox-backend-production.up.railway.app`

### Fase 2: Deploy do Frontend (Vercel) ⏱️ ~3 minutos

1. **Acesse Vercel**

   ```
   🌐 URL: https://vercel.com/
   👤 Login: TheGHKava2 (GitHub)
   ```

2. **Criar Novo Projeto**

   - Clique em "New Project"
   - Import Git Repository
   - Escolha: `TheGHKava2/todox-v76`

3. **Configuração do Build**

   ```
   Framework Preset: Next.js
   Root Directory: web
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **Variável de Ambiente**
   ```
   NEXT_PUBLIC_API_URL=[URL_DO_RAILWAY_AQUI]
   NODE_ENV=production
   ```

### Fase 3: Conectar Serviços ⏱️ ~2 minutos

1. **Atualizar CORS no Railway**

   - Vá para as variáveis do Railway
   - Atualize `CORS_ORIGINS` com a URL do Vercel
   - Exemplo: `https://seu-app.vercel.app,http://localhost:3000`

2. **Redeploy ambos os serviços**
   - Railway: Force redeploy
   - Vercel: Force redeploy

## 🔧 Scripts de Verificação

Execute estes comandos para validar o deploy:

```powershell
# 1. Verificar backend
curl https://SEU-BACKEND.up.railway.app/docs

# 2. Verificar frontend
curl https://SEU-APP.vercel.app

# 3. Testar API integration
curl https://SEU-BACKEND.up.railway.app/api/projects
```

## 📋 Checklist de Deploy

### Pre-Deploy ✅

- [x] Código testado localmente
- [x] Testes backend passando (5/5)
- [x] Testes frontend passando (7/7)
- [x] Commit e push para GitHub
- [x] Arquivos de configuração validados

### Deploy Backend (Railway)

- [ ] Projeto criado no Railway
- [ ] Repositório conectado
- [ ] Root directory: `backend`
- [ ] Start command configurado
- [ ] Variáveis de ambiente definidas
- [ ] Deploy executado com sucesso
- [ ] URL do backend anotada
- [ ] Endpoint `/docs` acessível

### Deploy Frontend (Vercel)

- [ ] Projeto criado no Vercel
- [ ] Repositório conectado
- [ ] Root directory: `web`
- [ ] Framework Next.js detectado
- [ ] Variável `NEXT_PUBLIC_API_URL` configurada
- [ ] Deploy executado com sucesso
- [ ] Site acessível

### Integração

- [ ] CORS atualizado no Railway
- [ ] Ambos serviços redeployados
- [ ] Comunicação frontend ↔ backend funcionando
- [ ] Criação de projetos funcionando
- [ ] Sistema de tasks funcionando

## 🎉 URLs Finais

Após o deploy, você terá:

```
🌐 Frontend: https://[seu-app].vercel.app
🔧 Backend:  https://[seu-projeto].up.railway.app
📚 API Docs: https://[seu-projeto].up.railway.app/docs
```

## 🚨 Troubleshooting

### Railway Issues

- **Build falha:** Verifique se `requirements.txt` está correto
- **App não inicia:** Confirme start command
- **502 Error:** Verifique logs no Railway dashboard

### Vercel Issues

- **Build falha:** Verifique se `package.json` está correto
- **API não conecta:** Confirme `NEXT_PUBLIC_API_URL`
- **404 Error:** Verifique root directory `web`

### Integration Issues

- **CORS Error:** Confirme CORS_ORIGINS no Railway
- **Network Error:** Verifique se ambas URLs estão corretas

## 💰 Custos

- **Railway:** $5/mês (uso básico)
- **Vercel:** Gratuito (hobby plan)
- **Total:** ~$5/mês

## 🔄 Deploy Automático

Após configuração inicial:

- Todo `git push` para `main` fará redeploy automático
- Railway monitora o diretório `backend/`
- Vercel monitora o diretório `web/`

## 🎯 Próximos Passos

Após deploy bem-sucedido:

1. **Domínio personalizado** (opcional)
2. **Monitoramento** com uptime checks
3. **Analytics** no Vercel
4. **Database backup** strategy
5. **CI/CD** enhancements

---

## ⚡ Quick Start

Para executar imediatamente:

1. **Abra Railway:** https://railway.app/
2. **Abra Vercel:** https://vercel.com/
3. **Siga as 3 fases acima**
4. **Tempo total:** ~10 minutos
5. **Resultado:** ToDoX V76 na nuvem! 🚀

---

**💡 Dica:** Mantenha esta página aberta durante o deploy para referência rápida!
