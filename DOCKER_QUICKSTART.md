# 🚀 Docker Quick Start Guide

## ⚡ 30 секунд до запуска

```bash
cd /Users/magomedkuriev/Desktop/Новая\ папка/trading_bot
docker-compose up -d
sleep 5
echo "✅ Готово! Откройте http://localhost:3000"
```

## 🎯 Основные команды

### Запуск
```bash
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Просмотр логов
```bash
docker-compose logs -f backend
```

### Проверка статуса
```bash
docker-compose ps
```

## 🌐 Доступ к сервисам

| Сервис | URL | Порт |
|--------|-----|------|
| 🎨 Dashboard | http://localhost:3000 | 3000 |
| 🔌 API | http://localhost:8000 | 8000 |
| 📚 API Docs | http://localhost:8000/docs | 8000 |
| 💾 Database | localhost:5432 | 5432 |
| 🔴 Redis | localhost:6379 | 6379 |

## 🛠️ Продвинутое управление

Используй скрипт для удобного управления:

```bash
# Просмотр справки
./scripts/docker-manage.sh help

# Проверить здоровье сервисов
./scripts/docker-manage.sh health

# Просмотр логов backend
./scripts/docker-manage.sh logs backend

# Вход в контейнер
./scripts/docker-manage.sh bash backend

# Вход в БД
./scripts/docker-manage.sh sql

# Статистика ресурсов
./scripts/docker-manage.sh stats

# Создать backup БД
./scripts/docker-manage.sh backup

# Перезапустить backend
./scripts/docker-manage.sh restart backend
```

## 🔍 Проверка что все работает

```bash
# 1. Проверить здоровье API
curl http://localhost:8000/api/health

# 2. Получить список стратегий
curl http://localhost:8000/api/strategies | jq .

# 3. Тестировать endpoints
./scripts/docker-manage.sh test-endpoints
```

## ⚠️ Проблемы?

**Backend не запускается?**
```bash
docker logs trading-bot-backend
```

**БД еще инициализируется?**
```bash
# Подожди 15 секунд, затем:
docker restart trading-bot-backend
```

**Port занят?**
```bash
# Найти процесс на порту 8000
lsof -i :8000

# Убить процесс (замени PID)
kill -9 12345
```

---

📖 Полный гайд: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
