# 🚀 Guia de Deploy - TODOX_V76

Este guia cobre várias opções de deploy para o projeto TODOX_V76.

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 18+
- Git
- Conta em provedor de cloud (opcional)

## 🏗️ Estrutura do Projeto

```
todox_v76/
├── backend/           # FastAPI (Python)
├── web/              # Next.js (React)
├── worker/           # Python Worker (opcional)
├── data/             # SQLite database
└── scripts/          # Scripts utilitários
```

## 🐳 Opção 1: Deploy com Docker (Recomendado)

### 1.1 Criar Dockerfile para Backend

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY data/ data/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.2 Criar Dockerfile para Frontend

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder

WORKDIR /app
COPY web/package*.json ./
RUN npm ci

COPY web/ .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

### 1.3 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DB_PATH=/app/data/app.db
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

## ☁️ Opção 2: Deploy na Nuvem

### 2.1 Vercel (Frontend) + Railway/Render (Backend)

#### Frontend no Vercel:
1. Conecte seu repositório ao Vercel
2. Configure as variáveis de ambiente:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   ```
3. Deploy automático no push

#### Backend no Railway:
1. Conecte repositório ao Railway
2. Configure variáveis:
   ```
   PORT=8000
   DB_PATH=/app/data/app.db
   ```
3. Railway detecta automaticamente Python

### 2.2 AWS (EC2 + RDS)

#### EC2 Setup:
```bash
# Instalar dependências
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm nginx

# Clonar projeto
git clone https://github.com/seu-usuario/todox_v76.git
cd todox_v76

# Setup Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup Frontend
cd ../web
npm install
npm run build

# Configure Nginx
sudo nano /etc/nginx/sites-available/todox
```

#### Nginx Config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 2.3 DigitalOcean App Platform

#### app.yaml:
```yaml
name: todox-v76
services:
- name: backend
  source_dir: backend
  github:
    repo: seu-usuario/todox_v76
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  
- name: frontend
  source_dir: web
  github:
    repo: seu-usuario/todox_v76
    branch: main
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: NEXT_PUBLIC_API_URL
    value: ${backend.PUBLIC_URL}
```

## 🔧 Opção 3: VPS Manual

### 3.1 Setup do Servidor

```bash
# Conectar ao VPS
ssh user@your-server-ip

# Instalar dependências
sudo apt update
sudo apt install python3.11 python3-pip nodejs npm nginx git supervisor

# Clonar projeto
git clone https://github.com/seu-usuario/todox_v76.git
cd todox_v76
```

### 3.2 Configurar Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Teste
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 3.3 Configurar Frontend

```bash
cd ../web
npm install
npm run build

# Instalar PM2 para gerenciamento
npm install -g pm2
pm2 start npm --name "todox-frontend" -- start
```

### 3.4 Supervisor Config

```ini
# /etc/supervisor/conf.d/todox-backend.conf
[program:todox-backend]
command=/home/user/todox_v76/backend/.venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
directory=/home/user/todox_v76/backend
user=user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/todox-backend.log
```

## 🔒 Configurações de Segurança

### Variáveis de Ambiente
```bash
# .env.production
DB_PATH=/app/data/app.db
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-frontend-domain.com
```

### SSL/HTTPS com Certbot
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoramento

### Logs
```bash
# Backend logs
tail -f /var/log/todox-backend.log

# Frontend logs
pm2 logs todox-frontend

# Nginx logs
tail -f /var/log/nginx/access.log
```

### Health Checks
```bash
# Backend
curl http://localhost:8000/docs

# Frontend
curl http://localhost:3000
```

## 🔄 CI/CD com GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy TODOX_V76

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /home/user/todox_v76
          git pull
          cd backend && source .venv/bin/activate && pip install -r requirements.txt
          cd ../web && npm install && npm run build
          sudo supervisorctl restart todox-backend
          pm2 restart todox-frontend
          sudo nginx -s reload
```

## 🚀 Deploy Rápido

Para um deploy rápido local com Docker:

```bash
# 1. Criar os Dockerfiles (ver seção 1)
# 2. Construir e rodar
docker-compose up -d

# Verificar
curl http://localhost     # Frontend
curl http://localhost:8000/docs  # Backend API
```

## 📝 Notas Importantes

1. **Backup do Banco**: Sempre faça backup do arquivo `data/app.db`
2. **Variáveis de Ambiente**: Configure corretamente as URLs da API
3. **CORS**: Ajuste as origens permitidas no backend
4. **SSL**: Use HTTPS em produção
5. **Logs**: Configure rotação de logs
6. **Updates**: Implemente strategy de zero-downtime

## 🆘 Troubleshooting

- **Erro 502**: Verifique se backend está rodando na porta correta
- **CORS Error**: Configure `CORS_ORIGINS` no backend
- **Build Failed**: Verifique Node.js e Python versions
- **Database Error**: Verifique permissões do arquivo SQLite