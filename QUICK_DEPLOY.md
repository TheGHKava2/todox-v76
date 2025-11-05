# 🚀 Deploy Rápido - TODOX_V76

## ⚡ Start Rápido

### Opção 1: Docker (Recomendado)
```bash
# 1. Clone e entre no diretório
git clone <seu-repo>
cd todox_v76

# 2. Execute o deploy
docker-compose up -d

# 3. Acesse a aplicação
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
# Nginx: http://localhost
```

### Opção 2: Deploy Manual
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (nova aba do terminal)
cd web
npm install
npm run build
npm start
```

### Opção 3: Scripts Automatizados

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh deploy docker    # Com Docker
./deploy.sh deploy manual    # Sem Docker
```

**Windows:**
```powershell
.\deploy.ps1 -Command deploy -Mode docker    # Com Docker
.\deploy.ps1 -Command deploy -Mode manual    # Sem Docker
```

## 🔧 Comandos Úteis

### Docker
```bash
# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Reconstruir
docker-compose up -d --build

# Health check
curl http://localhost/health
```

### Scripts
```bash
# Linux/Mac
./deploy.sh health    # Verificar status
./deploy.sh logs      # Ver logs
./deploy.sh stop      # Parar serviços
./deploy.sh backup    # Backup do banco

# Windows
.\deploy.ps1 -Command health
.\deploy.ps1 -Command logs
.\deploy.ps1 -Command stop
.\deploy.ps1 -Command backup
```

## 🌐 URLs da Aplicação

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentação:** http://localhost:8000/docs
- **Nginx (se Docker):** http://localhost

## 📊 Monitoramento

### Health Checks
```bash
# Backend
curl http://localhost:8000/docs

# Frontend  
curl http://localhost:3000

# Nginx
curl http://localhost/health
```

### Logs
```bash
# Docker
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# Manual
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 🛠️ Troubleshooting

### Problemas Comuns

**Porta ocupada:**
```bash
# Verificar quem está usando a porta
netstat -tulpn | grep :8000
# Matar processo
kill -9 <PID>
```

**Erro de permissão (Linux):**
```bash
sudo chown -R $USER:$USER .
chmod +x deploy.sh
```

**Erro de dependência:**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd web && npm install
```

**Banco de dados:**
```bash
# Verificar se existe
ls -la data/app.db

# Recriar se necessário
rm data/app.db
# Reiniciar backend para recriar
```

### Comandos de Debug

```bash
# Verificar containers Docker
docker ps -a

# Verificar imagens
docker images

# Limpar tudo
docker system prune -a

# Verificar espaço em disco
df -h
```

## 🚀 Deploy em Produção

Para deploy em servidor, consulte o arquivo `DEPLOY.md` para instruções completas incluindo:

- Deploy em VPS
- Configuração SSL
- CI/CD com GitHub Actions
- Deploy em AWS/DigitalOcean
- Configuração de domínio

## 📝 Variáveis de Ambiente

Crie `.env.local` para desenvolvimento:
```bash
# Backend
DB_PATH=./data/app.db
CORS_ORIGINS=http://localhost:3000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔒 Segurança

Para produção, configure:
- SSL/HTTPS
- Firewall
- Rate limiting
- Backup automático
- Monitoramento

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs
2. Execute health checks  
3. Consulte o troubleshooting
4. Verifique o arquivo `DEPLOY.md` completo