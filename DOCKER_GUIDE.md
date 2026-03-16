# Docker Deployment Guide 🐳

## Быстрый старт

### Запуск всех сервисов в фоне
```bash
cd /Users/magomedkuriev/Desktop/Новая\ папка/trading_bot
docker-compose up -d
```

### Проверка статуса
```bash
docker-compose ps
```

**Результат:**
```
NAME                    STATUS
trading-bot-postgres    Running (Healthy)
trading-bot-redis       Running (Healthy)
trading-bot-backend     Running
trading-bot-frontend    Running
```

## Сервисы и порты

| Сервис | Порт | URL | Описание |
|--------|------|-----|---------|
| **Backend API** | 8000 | http://localhost:8000 | FastAPI REST API |
| **Frontend** | 3000 | http://localhost:3000 | Next.js Dashboard |
| **PostgreSQL** | 5432 | localhost:5432 | База данных |
| **Redis** | 6379 | localhost:6379 | Cache & Message Queue |

## Полезные команды

### Запуск в интерактивном режиме (с логами в консоль)
```bash
docker-compose up
# Нажми Ctrl+C для остановки
```

### Остановка сервисов
```bash
docker-compose down
```

### Просмотр логов

**Все логи:**
```bash
docker-compose logs -f
```

**Только backend:**
```bash
docker logs -f trading-bot-backend
```

**Только frontend:**
```bash
docker logs -f trading-bot-frontend
```

**Только последние 50 строк:**
```bash
docker logs --tail=50 trading-bot-backend
```

### Перезапуск сервиса

```bash
# Перезапустить backend
docker restart trading-bot-backend

# Перезапустить весь stack
docker-compose restart
```

### Вход в контейнер

**В backend контейнер:**
```bash
docker exec -it trading-bot-backend bash
# Затем:
python -c "import app; print('✅ Backend OK')"
```

**В PostgreSQL:**
```bash
docker exec -it trading-bot-postgres psql -U trader -d trading_bot
# Примеры SQL команд:
# \dt  - список всех таблиц
# SELECT COUNT(*) FROM strategies;  - количество стратегий
# \q  - выход из psql
```

**В Redis:**
```bash
docker exec -it trading-bot-redis redis-cli
# ping  - проверка соединения
# KEYS *  - все ключи в кеше
```

## Проверка здоровья приложения

### Health Check API
```bash
curl http://localhost:8000/api/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "service": "Adaptive Grid Trading Bot",
  "version": "1.0.0"
}
```

### Список стратегий
```bash
curl http://localhost:8000/api/strategies | jq .
```

### Статус конкретной стратегии
```bash
curl http://localhost:8000/api/strategies/1 | jq .
```

## Инициализация БД

### Если нужна миграция после обновления схемы
```bash
docker exec trading-bot-postgres psql -U trader -d trading_bot -c \
"ALTER TABLE strategies ADD COLUMN IF NOT EXISTS grid_step FLOAT DEFAULT 0.5;"
```

### Сброс данных (осторожно!)
```bash
# Удалить все данные (НО сохранить таблицы)
docker exec trading-bot-postgres psql -U trader -d trading_bot -c \
"TRUNCATE TABLE orders CASCADE; TRUNCATE TABLE trades CASCADE; TRUNCATE TABLE portfolio_snapshots CASCADE;"

# Полностью удалить контейнер и данные
docker-compose down -v
docker-compose up -d
```

## Проблемы и решения

### 🔴 Backend не стартует с ошибкой "database trading_bot does not exist"
```bash
# Решение: PostgreSQL еще не инициализирована
docker-compose down
docker-compose up -d
# Ждите 15 секунд, пока БД инициализируется
```

### 🔴 Ошибка "column ... does not exist"
```bash
# Решение: Нужно добавить новые колонки
docker exec trading-bot-postgres psql -U trader -d trading_bot << 'EOF'
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS grid_step FLOAT DEFAULT 0.5;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS lot_size FLOAT DEFAULT 0.0;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS last_grid_rebuild TIMESTAMP;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS extreme_position_detected TIMESTAMP;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS needs_rebuild BOOLEAN DEFAULT FALSE;
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS rebuild_interval_minutes INTEGER DEFAULT 60;
EOF
```

### 🔴 Port уже в использовании
```bash
# Узнать, какой процесс занимает порт 8000
lsof -i :8000
lsof -i :3000
lsof -i :5432

# Убить процесс (замени PID на реальный)
kill -9 12345
```

### 🔴 Frontend не видит API
**Проверка:**
```bash
curl http://localhost:8000/api/health
```

**Если не ответит - перезапустить backend:**
```bash
docker restart trading-bot-backend
```

### 🔴 Memory/Storage issues
```bash
# Очистить неиспользуемые образы
docker image prune -f

# Очистить все контейнеры (осторожно!)
docker container prune -f

# Посмотреть размер volumes
docker system df
```

## Мониторинг производительности

### Использование CPU/RAM
```bash
docker stats trading-bot-backend trading-bot-frontend trading-bot-postgres
```

### Статистика сети
```bash
docker network inspect trading-bot-network
```

## Продвинутые команды

### Скопировать файл из контейнера
```bash
docker cp trading-bot-backend:/app/main.py ./main_backup.py
```

### Запустить одноразовую команду в backend
```bash
docker exec trading-bot-backend python -c "from app.core.logger import get_logger; print(get_logger('test'))"
```

### Создать backup БД
```bash
docker exec trading-bot-postgres pg_dump -U trader trading_bot > db_backup.sql
```

### Восстановить БД из backup
```bash
cat db_backup.sql | docker exec -i trading-bot-postgres psql -U trader trading_bot
```

## API endpoints для новых функций

### Flip Orders (переворот ордеров)
```bash
curl -X POST http://localhost:8000/api/grid/strategies/1/flip-orders
```

### Check Grid Adaptation (проверка адаптации)
```bash
curl -X POST "http://localhost:8000/api/grid/strategies/1/check-adaptation?current_price=45000"
```

### Rebuild Grid (пересоздание сетки)
```bash
curl -X POST "http://localhost:8000/api/grid/strategies/1/rebuild-grid?current_price=45000"
```

### Get Grid Status (статус сетки)
```bash
curl http://localhost:8000/api/grid/strategies/1/status | jq .
```

### Should Rebuild Check (нужна ли пересоздание)
```bash
curl http://localhost:8000/api/grid/strategies/1/should-rebuild
```

## Переменные окружения

### Установить через .env файл
```bash
# Создать .env в корне проекта
cat > .env << 'EOF'
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
BINANCE_TESTNET=true
LOG_LEVEL=INFO
EOF

docker-compose --env-file .env up -d
```

### Через docker-compose override
```bash
cat > docker-compose.override.yml << 'EOF'
services:
  backend:
    environment:
      LOG_LEVEL: DEBUG
      BINANCE_TESTNET: false
EOF

docker-compose up -d
```

## Развертывание на Production

### Сценарий 1: Использовать разные .env для разных сред
```bash
# Development
docker-compose -f docker-compose.yml --env-file .env.dev up -d

# Production
docker-compose -f docker-compose.yml --env-file .env.prod up -d
```

### Сценарий 2: Изменить порты
```bash
cat > docker-compose.override.yml << 'EOF'
services:
  backend:
    ports:
      - "8001:8000"
  frontend:
    ports:
      - "3001:3000"
EOF

docker-compose up -d
```

## Версионирование контейнеров

### Создать и запустить определенную версию
```bash
# Собрать новый образ
docker build -f docker/Dockerfile.backend -t trading-bot-backend:v1.1.0 ./backend

# Обновить docker-compose.yml с новым тегом
# Затем запустить
docker-compose up -d
```

---

**Последнее обновление:** 16 Марта 2026  
**Версия:** 1.0.0  
**Статус:** ✅ Все сервисы работают
