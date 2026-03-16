#!/bin/bash
# Trading Bot Docker Management Script
# Использование: ./scripts/docker-manage.sh [команда] [параметры]

set -e

DOCKER_COMPOSE_FILE="docker-compose.yml"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для красивого вывода
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка что мы в правильной директории
if [ ! -f "$PROJECT_DIR/$DOCKER_COMPOSE_FILE" ]; then
    log_error "Файл $DOCKER_COMPOSE_FILE не найден в $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

case "${1:-help}" in
    up)
        log_info "🚀 Запуск всех сервисов в фоне..."
        docker-compose up -d
        log_success "Сервисы запущены!"
        sleep 3
        docker-compose ps
        ;;
    
    down)
        log_info "⛔ Остановка всех сервисов..."
        docker-compose down
        log_success "Сервисы остановлены"
        ;;
    
    restart)
        log_info "🔄 Перезапуск ${2:-всех сервисов}..."
        if [ -z "$2" ]; then
            docker-compose restart
            log_success "Все сервисы перезагружены"
        else
            docker-compose restart "$2"
            log_success "Сервис $2 перезагружен"
        fi
        ;;
    
    logs)
        if [ -z "$2" ]; then
            log_info "Логи всех сервисов (последние 100 строк):"
            docker-compose logs --tail=100 -f
        else
            log_info "Логи сервиса $2:"
            docker logs -f --tail=100 "trading-bot-$2"
        fi
        ;;
    
    ps|status)
        log_info "Статус сервисов:"
        docker-compose ps
        ;;
    
    health)
        log_info "🏥 Проверка здоровья сервисов..."
        echo ""
        
        log_info "Backend Health Check:"
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            curl -s http://localhost:8000/api/health | jq '.'
            log_success "Backend работает"
        else
            log_error "Backend недоступен"
        fi
        
        echo ""
        log_info "Frontend:"
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            log_success "Frontend доступен на http://localhost:3000"
        else
            log_error "Frontend недоступен"
        fi
        
        echo ""
        log_info "Database:"
        if docker exec trading-bot-postgres pg_isready -U trader > /dev/null 2>&1; then
            log_success "PostgreSQL работает"
        else
            log_error "PostgreSQL недоступна"
        fi
        
        echo ""
        log_info "Redis:"
        if docker exec trading-bot-redis redis-cli ping > /dev/null 2>&1; then
            log_success "Redis работает"
        else
            log_error "Redis недоступна"
        fi
        ;;
    
    bash|shell)
        SERVICE="${2:-backend}"
        log_info "Вход в контейнер trading-bot-$SERVICE..."
        docker exec -it "trading-bot-$SERVICE" bash
        ;;
    
    sql)
        log_info "Вход в PostgreSQL (psql)..."
        docker exec -it trading-bot-postgres psql -U trader -d trading_bot
        ;;
    
    redis)
        log_info "Вход в Redis (redis-cli)..."
        docker exec -it trading-bot-redis redis-cli
        ;;
    
    reset)
        log_warning "⚠️  Это удалит все данные из БД!"
        read -p "Вы уверены? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Очистка БД..."
            docker exec trading-bot-postgres psql -U trader -d trading_bot << 'SQL'
TRUNCATE TABLE portfolio_snapshots CASCADE;
TRUNCATE TABLE trades CASCADE;
TRUNCATE TABLE orders CASCADE;
DELETE FROM strategies;
SQL
            log_success "БД очищена"
        fi
        ;;
    
    backup)
        BACKUP_FILE="db_backup_$(date +%Y%m%d_%H%M%S).sql"
        log_info "📦 Создание backup БД в $BACKUP_FILE..."
        docker exec trading-bot-postgres pg_dump -U trader trading_bot > "$BACKUP_FILE"
        log_success "Backup создан: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
        ;;
    
    restore)
        if [ -z "$2" ]; then
            log_error "Укажите файл backup: docker-manage.sh restore backup.sql"
            exit 1
        fi
        if [ ! -f "$2" ]; then
            log_error "Файл $2 не найден"
            exit 1
        fi
        log_warning "⚠️  Это перезапишет текущую БД!"
        read -p "Вы уверены? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Восстановление из $2..."
            cat "$2" | docker exec -i trading-bot-postgres psql -U trader trading_bot
            log_success "БД восстановлена"
        fi
        ;;
    
    stats)
        log_info "📊 Статистика использования ресурсов:"
        docker stats trading-bot-backend trading-bot-frontend trading-bot-postgres trading-bot-redis --no-stream
        ;;
    
    clean)
        log_info "🧹 Очистка Docker (образы, контейнеры, volumes)..."
        docker-compose down -v
        log_warning "Удаление неиспользуемых образов..."
        docker image prune -f
        docker container prune -f
        log_success "Docker очищен"
        ;;
    
    rebuild)
        log_info "🔨 Пересборка Docker образов..."
        docker-compose build --no-cache
        log_success "Образы пересобраны"
        ;;
    
    demo-data)
        log_info "📊 Загрузка демо-данных..."
        docker exec trading-bot-backend python << 'PYTHON'
from app.core.database import SessionLocal
from app.core.demo_data import load_demo_data
load_demo_data(SessionLocal())
print("✅ Демо-данные загружены")
PYTHON
        ;;
    
    test-endpoints)
        log_info "🧪 Тестирование API endpoints..."
        
        ENDPOINTS=(
            "http://localhost:8000/api/health"
            "http://localhost:8000/api/strategies"
            "http://localhost:8000/api/strategies/1"
            "http://localhost:8000/api/strategies/1/orders"
            "http://localhost:8000/api/strategies/1/trades"
            "http://localhost:8000/api/grid/strategies/1/status"
        )
        
        for endpoint in "${ENDPOINTS[@]}"; do
            if curl -s "$endpoint" > /dev/null 2>&1; then
                log_success "✓ $endpoint"
            else
                log_error "✗ $endpoint"
            fi
        done
        ;;
    
    help)
        cat << 'HELP'
Trading Bot Docker Manager

ИСПОЛЬЗОВАНИЕ:
  ./scripts/docker-manage.sh [команда] [параметры]

КОМАНДЫ:
  up                    - Запустить все сервисы в фоне
  down                  - Остановить все сервисы
  restart [сервис]     - Перезапустить сервис (или все если не указан)
  logs [сервис]        - Показать логи (backend/frontend/postgres/redis)
  ps, status            - Показать статус сервисов
  health                - Проверить здоровье всех сервисов
  bash [сервис]        - Вход в контейнер (по умолчанию backend)
  sql                   - Вход в PostgreSQL (psql)
  redis                 - Вход в Redis (redis-cli)
  reset                 - Очистить все данные из БД ⚠️
  backup                - Создать backup БД
  restore <файл>       - Восстановить БД из backup ⚠️
  stats                 - Показать использование ресурсов
  clean                 - Удалить контейнеры и очистить volumes ⚠️
  rebuild               - Пересобрать Docker образы
  demo-data             - Загрузить демо-данные
  test-endpoints        - Протестировать API endpoints
  help                  - Показать эту справку

ПРИМЕРЫ:
  ./scripts/docker-manage.sh up
  ./scripts/docker-manage.sh logs backend
  ./scripts/docker-manage.sh restart
  ./scripts/docker-manage.sh health
  ./scripts/docker-manage.sh bash frontend
  ./scripts/docker-manage.sh sql
  ./scripts/docker-manage.sh backup
  ./scripts/docker-manage.sh restore db_backup_20260316_100000.sql

URL СЕРВИСОВ:
  Backend API: http://localhost:8000
  Frontend:    http://localhost:3000
  Swagger Docs: http://localhost:8000/docs

ДЛЯ РАЗРАБОТКИ:
  Посмотреть logс while разрабатываешь:
    ./scripts/docker-manage.sh logs backend -f
  
  Перезагрузить backend после изменений:
    ./scripts/docker-manage.sh restart backend
  
  Проверить статус:
    ./scripts/docker-manage.sh health
HELP
        ;;
    
    *)
        log_error "Неизвестная команда: $1"
        echo "Введите './scripts/docker-manage.sh help' для справки"
        exit 1
        ;;
esac
