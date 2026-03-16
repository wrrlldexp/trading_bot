# 📋 Шпаргалка по Docker командам

## 🚀 Запуск/Остановка

```bash
# Запуск в фоне
docker-compose up -d

# Запуск с логами в консоль
docker-compose up

# Остановка
docker-compose down

# Перезапуск
docker-compose restart
```

## 📊 Статус и логи

```bash
# Статус всех сервисов
docker-compose ps

# Логи всех сервисов (последние 100 строк)
docker-compose logs --tail=100

# Следить за логами (live)
docker-compose logs -f

# Логи конкретного сервиса
docker logs -f trading-bot-backend
docker logs -f trading-bot-frontend
docker logs -f trading-bot-postgres
docker logs -f trading-bot-redis

# Количество строк логов
docker logs --tail=50 trading-bot-backend
```

## 🔍 Проверка здоровья

```bash
# API Health Check
curl http://localhost:8000/api/health

# Все endpoints
curl http://localhost:8000/api/strategies | jq .

# Через скрипт
./scripts/docker-manage.sh health

# Использование CPU/RAM
docker stats trading-bot-backend --no-stream
```

## 🛠️ Вход в контейнеры

```bash
# В Backend контейнер
docker exec -it trading-bot-backend bash

# В Frontend контейнер
docker exec -it trading-bot-frontend bash

# В PostgreSQL
docker exec -it trading-bot-postgres psql -U trader -d trading_bot

# В Redis
docker exec -it trading-bot-redis redis-cli
```

## 💾 PostgreSQL команды (внутри psql)

```sql
-- Список таблиц
\dt

-- Описание таблицы
\d strategies

-- Количество строк
SELECT COUNT(*) FROM strategies;

-- Все стратегии
SELECT id, name, pair, is_active FROM strategies;

-- Очистить данные
TRUNCATE TABLE orders CASCADE;

-- Выход
\q
```

## 🔴 Redis команды (внутри redis-cli)

```bash
# Проверка соединения
ping

# Все ключи
KEYS *

# Значение ключа
GET key_name

# Удалить ключ
DEL key_name

# Очистить весь redis
FLUSHALL

# Выход
EXIT
```

## 🚀 Скрипт docker-manage.sh

```bash
# Справка
./scripts/docker-manage.sh help

# Запуск
./scripts/docker-manage.sh up

# Остановка
./scripts/docker-manage.sh down

# Перезапуск backend
./scripts/docker-manage.sh restart backend

# Логи
./scripts/docker-manage.sh logs backend

# Здоровье
./scripts/docker-manage.sh health

# Вход в bash
./scripts/docker-manage.sh bash backend

# Вход в psql
./scripts/docker-manage.sh sql

# Вход в redis-cli
./scripts/docker-manage.sh redis

# Создать backup БД
./scripts/docker-manage.sh backup

# Восстановить БД
./scripts/docker-manage.sh restore backup.sql

# Статистика
./scripts/docker-manage.sh stats

# Очистить Docker
./scripts/docker-manage.sh clean

# Тестировать endpoints
./scripts/docker-manage.sh test-endpoints
```

## 📝 SQL миграции

```bash
# Добавить новый столбец
docker exec trading-bot-postgres psql -U trader -d trading_bot -c \
"ALTER TABLE strategies ADD COLUMN new_column VARCHAR(255);"

# Удалить столбец
docker exec trading-bot-postgres psql -U trader -d trading_bot -c \
"ALTER TABLE strategies DROP COLUMN old_column;"

# Создать backup
docker exec trading-bot-postgres pg_dump -U trader trading_bot > backup.sql

# Восстановить из backup
cat backup.sql | docker exec -i trading-bot-postgres psql -U trader trading_bot
```

## 🐛 Решение проблем

```bash
# Port уже в использовании
lsof -i :8000
kill -9 PID

# Перестроить образы
docker-compose build --no-cache

# Очистить все (осторожно!)
docker-compose down -v
docker image prune -f
docker container prune -f

# Просмотреть файлы в контейнере
docker exec trading-bot-backend ls -la /app

# Скопировать файл из контейнера
docker cp trading-bot-backend:/app/file.txt ./file.txt

# Скопировать файл в контейнер
docker cp ./file.txt trading-bot-backend:/app/file.txt
```

## 🔗 API Endpoints

```bash
# Health Check
curl http://localhost:8000/api/health

# Стратегии
curl http://localhost:8000/api/strategies
curl http://localhost:8000/api/strategies/1

# Ордеры
curl http://localhost:8000/api/strategies/1/orders

# Сделки
curl http://localhost:8000/api/strategies/1/trades

# Grid Management (NEW)
curl -X POST http://localhost:8000/api/grid/strategies/1/flip-orders
curl -X POST "http://localhost:8000/api/grid/strategies/1/check-adaptation?current_price=45000"
curl -X POST "http://localhost:8000/api/grid/strategies/1/rebuild-grid?current_price=45000"
curl http://localhost:8000/api/grid/strategies/1/status
curl http://localhost:8000/api/grid/strategies/1/should-rebuild

# Swagger Docs
open http://localhost:8000/docs
```

## 📊 Мониторинг

```bash
# CPU/RAM использование
docker stats

# Размер контейнеров
docker ps --size

# Размер образов
docker images

# Размер volumes
docker system df

# История команд
docker history trading-bot-backend:latest
```

## 🔐 Environment переменные

```bash
# Создать .env файл
cat > .env << 'EOF'
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
BINANCE_TESTNET=true
LOG_LEVEL=INFO
EOF

# Использовать .env
docker-compose --env-file .env up -d
```

## 🐳 Docker Compose override

```bash
# Создать docker-compose.override.yml
cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  backend:
    environment:
      LOG_LEVEL: DEBUG
    ports:
      - "8001:8000"
EOF

# Теперь используется override (автоматически при up)
docker-compose up -d
```

## 🔄 Частые операции

```bash
# Полная переинициализация
docker-compose down -v && docker-compose up -d

# Обновить один контейнер
docker-compose up -d backend

# Пересборить образ
docker-compose build --no-cache backend

# Запустить команду в контейнере
docker exec trading-bot-backend python script.py

# Проверить логи после ошибки
docker logs trading-bot-backend 2>&1 | tail -30
```

---

**Советы:**
- 💡 Используй `docker-compose logs -f` для отладки
- 💡 Добавь `--no-cache` если меняешь Dockerfile
- 💡 Используй `docker exec` для запуска команд в контейнерах
- 💡 Регулярно делай `docker system df` для очистки
- 💡 Keep `.env` в `.gitignore` для безопасности
