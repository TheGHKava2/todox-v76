# ☁️ Configurações para Provedores de Cloud

## 🌊 DigitalOcean App Platform

### app.yaml
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
  envs:
  - key: DB_PATH
    value: /app/data/app.db
  - key: CORS_ORIGINS
    value: ${frontend.PUBLIC_URL}

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

databases:
- engine: PG
  name: todox-db
  num_nodes: 1
  size: db-s-dev-database
  version: "14"
```

## ▲ Vercel + Railway

### Vercel (Frontend)
```bash
# vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-railway-app.railway.app"
  }
}
```

### Railway (Backend)
```bash
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/docs"
  }
}
```

## 🚀 Heroku

### Procfile
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### heroku.yml
```yaml
build:
  docker:
    web: Dockerfile.backend
run:
  web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Configuração
```bash
heroku create todox-backend
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set CORS_ORIGINS=https://your-frontend-domain.vercel.app
git push heroku main
```

## ☁️ AWS (Elastic Beanstalk)

### .ebextensions/python.config
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /opt/python/current/app
    DB_PATH: /opt/python/current/app/data/app.db
```

### requirements.txt (adicionar)
```
gunicorn==21.2.0
```

## 🐳 Docker Swarm

### docker-stack.yml
```yaml
version: '3.8'

services:
  backend:
    image: your-registry/todox-backend:latest
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    environment:
      - DB_PATH=/app/data/app.db
    volumes:
      - backend_data:/app/data
    networks:
      - todox_network

  frontend:
    image: your-registry/todox-frontend:latest
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    networks:
      - todox_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
    configs:
      - source: nginx_config
        target: /etc/nginx/nginx.conf
    networks:
      - todox_network

volumes:
  backend_data:

networks:
  todox_network:
    driver: overlay

configs:
  nginx_config:
    external: true
```

## 🎯 Google Cloud Run

### Backend
```yaml
# backend/cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/todox-backend', '-f', 'Dockerfile.backend', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/todox-backend']
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'todox-backend', '--image', 'gcr.io/$PROJECT_ID/todox-backend', '--region', 'us-central1', '--platform', 'managed']
```

### Frontend
```yaml
# web/cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/todox-frontend', '-f', 'Dockerfile.frontend', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/todox-frontend']
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'todox-frontend', '--image', 'gcr.io/$PROJECT_ID/todox-frontend', '--region', 'us-central1', '--platform', 'managed']
```

## 💙 Azure Container Instances

### azure-container.yaml
```yaml
apiVersion: 2021-03-01
location: eastus
name: todox-v76
properties:
  containers:
  - name: backend
    properties:
      image: your-registry/todox-backend:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1.5
      ports:
      - port: 8000
      environmentVariables:
      - name: DB_PATH
        value: /app/data/app.db
      
  - name: frontend
    properties:
      image: your-registry/todox-frontend:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1.5
      ports:
      - port: 3000
      environmentVariables:
      - name: NEXT_PUBLIC_API_URL
        value: http://localhost:8000

  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 80
    - protocol: tcp
      port: 3000
    - protocol: tcp
      port: 8000
```

## 🔄 GitHub Actions para Múltiplos Provedores

### .github/workflows/multi-deploy.yml
```yaml
name: Multi-Platform Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-vercel:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        working-directory: ./web

  deploy-railway:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: bervProject/railway-deploy@v1.0.0
      with:
        railway_token: ${{ secrets.RAILWAY_TOKEN }}
        service: "backend"

  deploy-docker-hub:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: docker/build-push-action@v5
      with:
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/todox-backend:latest
          ${{ secrets.DOCKER_USERNAME }}/todox-frontend:latest
```

## 📊 Monitoramento Multi-Cloud

### Prometheus + Grafana
```yaml
# monitoring/docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  alertmanager:
    image: prom/alertmanager
    ports:
      - "9093:9093"
```

## 🔧 Configurações por Ambiente

### Development
```bash
# .env.development
NEXT_PUBLIC_API_URL=http://localhost:8000
DB_PATH=./data/dev.db
DEBUG=true
```

### Staging
```bash
# .env.staging
NEXT_PUBLIC_API_URL=https://api-staging.yourdomain.com
DB_PATH=/app/data/staging.db
DEBUG=false
```

### Production
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
DB_PATH=/app/data/production.db
DEBUG=false
SSL_REDIRECT=true
```

## 💰 Estimativa de Custos

### Tier Gratuito
- **Vercel:** Frontend gratuito
- **Railway:** $5/mês backend
- **Total:** ~$5/mês

### Pequeno Negócio
- **DigitalOcean App Platform:** $12/mês
- **Domain + SSL:** $15/ano
- **Total:** ~$13/mês

### Empresa
- **AWS/GCP:** $50-200/mês
- **CDN + Monitoring:** $20/mês
- **Total:** $70-220/mês