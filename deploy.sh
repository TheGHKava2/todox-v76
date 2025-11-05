#!/bin/bash

# 🚀 Script de Deploy TODOX_V76
# Este script automatiza o processo de deploy local ou em servidor

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker não está instalado!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose não está instalado!"
        exit 1
    fi
    
    log_success "Dependências verificadas"
}

# Deploy com Docker
deploy_docker() {
    log_info "Iniciando deploy com Docker..."
    
    # Parar containers existentes
    log_info "Parando containers existentes..."
    docker-compose down || true
    
    # Limpar imagens antigas
    log_info "Limpando imagens antigas..."
    docker system prune -f
    
    # Construir e iniciar
    log_info "Construindo e iniciando containers..."
    docker-compose up -d --build
    
    # Aguardar serviços
    log_info "Aguardando serviços ficarem prontos..."
    sleep 30
    
    # Health check
    check_health
}

# Deploy manual
deploy_manual() {
    log_info "Iniciando deploy manual..."
    
    # Backend
    log_info "Configurando backend..."
    cd backend
    
    if [ ! -d ".venv" ]; then
        log_info "Criando ambiente virtual..."
        python3 -m venv .venv
    fi
    
    source .venv/bin/activate
    pip install -r requirements.txt
    
    # Iniciar backend em background
    log_info "Iniciando backend..."
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
    echo $! > ../logs/backend.pid
    
    cd ..
    
    # Frontend
    log_info "Configurando frontend..."
    cd web
    npm install
    npm run build
    
    # Iniciar frontend em background
    log_info "Iniciando frontend..."
    nohup npm start > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid
    
    cd ..
    
    sleep 15
    check_health
}

# Verificar saúde dos serviços
check_health() {
    log_info "Verificando saúde dos serviços..."
    
    # Backend
    if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
        log_success "Backend está funcionando (http://localhost:8000)"
    else
        log_error "Backend não está respondendo!"
        return 1
    fi
    
    # Frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend está funcionando (http://localhost:3000)"
    else
        log_error "Frontend não está respondendo!"
        return 1
    fi
    
    if command -v docker &> /dev/null && docker ps | grep -q nginx; then
        if curl -f http://localhost > /dev/null 2>&1; then
            log_success "Nginx está funcionando (http://localhost)"
        fi
    fi
}

# Parar serviços
stop_services() {
    log_info "Parando serviços..."
    
    if [ "$1" == "docker" ]; then
        docker-compose down
    else
        # Parar processos manuais
        if [ -f "logs/backend.pid" ]; then
            kill $(cat logs/backend.pid) 2>/dev/null || true
            rm logs/backend.pid
        fi
        
        if [ -f "logs/frontend.pid" ]; then
            kill $(cat logs/frontend.pid) 2>/dev/null || true
            rm logs/frontend.pid
        fi
    fi
    
    log_success "Serviços parados"
}

# Mostrar logs
show_logs() {
    if [ "$1" == "docker" ]; then
        docker-compose logs -f
    else
        if [ "$2" == "backend" ]; then
            tail -f logs/backend.log
        elif [ "$2" == "frontend" ]; then
            tail -f logs/frontend.log
        else
            tail -f logs/*.log
        fi
    fi
}

# Backup do banco
backup_db() {
    log_info "Criando backup do banco de dados..."
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backups/db_backup_$timestamp.db"
    
    mkdir -p backups
    
    if [ -f "data/app.db" ]; then
        cp data/app.db "$backup_file"
        log_success "Backup criado: $backup_file"
    else
        log_warning "Banco de dados não encontrado"
    fi
}

# Menu principal
show_help() {
    echo "🚀 TODOX_V76 Deploy Script"
    echo ""
    echo "Uso: $0 [COMANDO] [OPÇÕES]"
    echo ""
    echo "Comandos:"
    echo "  deploy docker     - Deploy com Docker Compose"
    echo "  deploy manual     - Deploy manual (sem Docker)"
    echo "  stop [docker]     - Parar serviços"
    echo "  logs [docker] [service] - Mostrar logs"
    echo "  health            - Verificar saúde dos serviços"
    echo "  backup            - Backup do banco de dados"
    echo "  help              - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 deploy docker"
    echo "  $0 stop docker"
    echo "  $0 logs docker backend"
    echo "  $0 health"
}

# Criar diretórios necessários
mkdir -p logs data backups

# Processar argumentos
case "$1" in
    "deploy")
        check_dependencies
        backup_db
        if [ "$2" == "docker" ]; then
            deploy_docker
        else
            deploy_manual
        fi
        ;;
    "stop")
        stop_services "$2"
        ;;
    "logs")
        show_logs "$2" "$3"
        ;;
    "health")
        check_health
        ;;
    "backup")
        backup_db
        ;;
    "help"|"")
        show_help
        ;;
    *)
        log_error "Comando desconhecido: $1"
        show_help
        exit 1
        ;;
esac