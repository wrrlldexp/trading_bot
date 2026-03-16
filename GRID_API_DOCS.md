# 🔄 НОВЫЕ API ЭНДПОИНТЫ - УПРАВЛЕНИЕ СЕТКОЙ

## 📊 Обзор

Добавлены новые API endpoints для управления сеткой ордеров согласно требуемой стратегии:

1. **Переворот исполненных ордеров** — BUY → SELL, SELL → BUY
2. **Адаптация сетки** — проверка крайних позиций
3. **Перестройка сетки** — каждые 60 минут при необходимости
4. **Статус сетки** — мониторинг состояния

---

## 📡 API Endpoints

### 1️⃣ Переворот исполненных ордеров

#### Endpoint
```http
POST /api/grid/strategies/{strategy_id}/flip-orders
```

#### Описание
Переворачивает все исполненные ордера на противоположные:
- Исполненный **BUY** → новый **SELL** на том же уровне цены
- Исполненный **SELL** → новый **BUY** на том же уровне цены

#### Параметры
- `strategy_id` (path): ID стратегии

#### Пример запроса
```bash
curl -X POST http://localhost:8000/api/grid/strategies/1/flip-orders
```

#### Пример ответа
```json
{
  "strategy_id": 1,
  "flipped_orders": 3,
  "status": "success"
}
```

#### Когда вызывать
- После изменения статуса ордера на "filled"
- Автоматически в scheduled job каждую минуту
- Вручную при необходимости пересинхронизации

---

### 2️⃣ Проверка адаптации сетки

#### Endpoint
```http
POST /api/grid/strategies/{strategy_id}/check-adaptation?current_price=45000.5
```

#### Описание
Проверяет крайние позиции сетки (верхнюю и нижнюю).
Если цена прошла за границы сетки, отмечает необходимость перестройки через 60 минут.

#### Параметры
- `strategy_id` (path): ID стратегии
- `current_price` (query): Текущая цена криптовалюты

#### Логика
```
Если current_price < min_grid_price ИЛИ current_price > max_grid_price:
  → Установить extreme_position_detected = now()
  → Установить needs_rebuild = true
  → Запустить таймер на 60 минут
```

#### Пример запроса
```bash
curl -X POST "http://localhost:8000/api/grid/strategies/1/check-adaptation?current_price=45000.5"
```

#### Пример ответа
```json
{
  "strategy_id": 1,
  "current_price": 45000.5,
  "extreme_position_detected": true,
  "needs_rebuild": true
}
```

#### Когда вызывать
- Каждый раз при получении новой цены (WebSocket)
- В цикле polling ~каждую секунду

---

### 3️⃣ Перестройка сетки

#### Endpoint
```http
POST /api/grid/strategies/{strategy_id}/rebuild-grid?current_price=45000.5
```

#### Описание
Перестраивает сетку ордеров по текущей цене:

1. Отменяет все активные ордера старой сетки
2. Создает новую сетку с центром по текущей цене
3. Обновляет статус стратегии

#### Параметры
- `strategy_id` (path): ID стратегии
- `current_price` (query): Текущая цена для центра новой сетки

#### Логика
```
1. Отменить все open ордера
2. Генерировать новую сетку по current_price
3. Создать новые ордера
4. Установить:
   - needs_rebuild = false
   - extreme_position_detected = null
   - last_grid_rebuild = now()
```

#### Пример запроса
```bash
curl -X POST "http://localhost:8000/api/grid/strategies/1/rebuild-grid?current_price=45000.5"
```

#### Пример ответа
```json
{
  "strategy_id": 1,
  "created_orders": 10,
  "center_price": 45000.5,
  "status": "success"
}
```

#### Когда вызывать
- Когда `should_rebuild()` вернул true
- Через 60 минут после обнаружения крайней позиции
- Вручную при необходимости рефреша сетки

---

### 4️⃣ Получить статус сетки

#### Endpoint
```http
GET /api/grid/strategies/{strategy_id}/status
```

#### Описание
Получает полную информацию о состоянии сетки:
- Количество активных ордеров
- Диапазон цен (min-max)
- Статус адаптации
- Время до следующей перестройки

#### Параметры
- `strategy_id` (path): ID стратегии

#### Пример запроса
```bash
curl http://localhost:8000/api/grid/strategies/1/status
```

#### Пример ответа
```json
{
  "strategy_id": 1,
  "pair": "BTCUSDT",
  "grid_levels": 10,
  "active_orders": 10,
  "total_orders": 23,
  "min_price": 44000.0,
  "max_price": 46000.0,
  "needs_rebuild": true,
  "extreme_position_detected": "2026-03-16T10:30:00",
  "last_grid_rebuild": "2026-03-16T08:00:00",
  "time_until_rebuild_seconds": 1800.0,
  "rebuild_interval_minutes": 60
}
```

#### Когда вызывать
- На dashboard для отображения информации
- В мониторинг системы
- Для отладки

---

### 5️⃣ Проверить нужна ли перестройка

#### Endpoint
```http
GET /api/grid/strategies/{strategy_id}/should-rebuild
```

#### Описание
Проверяет, пришло ли время для перестройки сетки.

Возвращает true если:
- `needs_rebuild` = true И
- Прошло >= 60 минут с момента обнаружения крайней позиции

#### Параметры
- `strategy_id` (path): ID стратегии

#### Пример запроса
```bash
curl http://localhost:8000/api/grid/strategies/1/should-rebuild
```

#### Пример ответа
```json
{
  "strategy_id": 1,
  "should_rebuild": true,
  "grid_status": {
    "strategy_id": 1,
    "pair": "BTCUSDT",
    "grid_levels": 10,
    "active_orders": 10,
    "total_orders": 23,
    "min_price": 44000.0,
    "max_price": 46000.0,
    "needs_rebuild": true,
    "extreme_position_detected": "2026-03-16T09:30:00",
    "last_grid_rebuild": "2026-03-16T08:00:00",
    "time_until_rebuild_seconds": 0.0,
    "rebuild_interval_minutes": 60
  }
}
```

#### Когда вызывать
- В main loop приложения (~каждую минуту)
- При получении нового события от WebSocket
- Перед перестройкой сетки

---

## 🔄 Рекомендуемый workflow

### 1. Инициализация стратегии
```bash
POST /api/strategies
{
  "name": "BTC Grid Bot",
  "pair": "BTCUSDT",
  "grid_levels": 10,
  "grid_step": 0.5,              # % шаг между уровнями
  "grid_profit_per_trade": 1.0,  # % прибыль за сделку
  "lot_size": 1.0
}
```

### 2. Основной цикл (run every 1 second)
```
1. Получить текущую цену (WebSocket)
2. POST /api/grid/strategies/{id}/check-adaptation?current_price=XXX
   → Проверить нужна ли перестройка
3. Если extreme_position_detected:
   → Запустить таймер на 60 минут
4. Обновить UI с статусом
```

### 3. Цикл перестройки (run every 10 seconds)
```
1. GET /api/grid/strategies/{id}/should-rebuild
   → Проверить пришло ли время
2. Если should_rebuild = true:
   → POST /api/grid/strategies/{id}/rebuild-grid?current_price=XXX
   → Пересоздать сетку
```

### 4. Цикл переворота ордеров (run every 1 second)
```
1. Слушать WebSocket обновления статуса ордеров
2. Когда ордер переходит в "filled":
   → POST /api/grid/strategies/{id}/flip-orders
   → Создать противоположный ордер
```

---

## 💾 Обновленные модели

### Strategy (новые поля)
```python
class Strategy(Base):
    # Существующие параметры
    grid_levels: int = 10
    grid_profit_per_trade: float = 0.1  # % прибыль
    
    # НОВЫЕ параметры
    grid_step: float = 0.1  # % шаг между уровнями
    lot_size: float = 1.0   # размер лота
    
    # Адаптация сетки
    last_grid_rebuild: Optional[datetime] = None
    extreme_position_detected: Optional[datetime] = None
    needs_rebuild: bool = False
    rebuild_interval_minutes: int = 60
```

---

## 🧪 Примеры использования (Python)

### Пример 1: Полный цикл перестройки
```python
import requests
import time

BASE_URL = "http://localhost:8000"
STRATEGY_ID = 1

def manage_grid():
    # Получить текущую цену (из WebSocket)
    current_price = 45000.5
    
    # Проверить нужна ли адаптация
    check_response = requests.post(
        f"{BASE_URL}/api/grid/strategies/{STRATEGY_ID}/check-adaptation",
        params={"current_price": current_price}
    )
    
    if check_response.json()["extreme_position_detected"]:
        print("Extreme position detected! Will rebuild in 60 minutes...")
        
        # Подождать 60 минут
        time.sleep(3600)
        
        # Проверить нужна ли перестройка
        rebuild_check = requests.get(
            f"{BASE_URL}/api/grid/strategies/{STRATEGY_ID}/should-rebuild"
        )
        
        if rebuild_check.json()["should_rebuild"]:
            # Перестроить сетку
            rebuild_response = requests.post(
                f"{BASE_URL}/api/grid/strategies/{STRATEGY_ID}/rebuild-grid",
                params={"current_price": current_price}
            )
            print(f"Grid rebuilt: {rebuild_response.json()}")

# Запустить в цикле
while True:
    manage_grid()
    time.sleep(1)
```

### Пример 2: Мониторинг сетки
```python
import requests

def monitor_grid(strategy_id):
    response = requests.get(
        f"http://localhost:8000/api/grid/strategies/{strategy_id}/status"
    )
    
    status = response.json()
    
    print(f"Grid Status for Strategy {strategy_id}:")
    print(f"  Active Orders: {status['active_orders']}")
    print(f"  Price Range: {status['min_price']} - {status['max_price']}")
    print(f"  Needs Rebuild: {status['needs_rebuild']}")
    
    if status['time_until_rebuild_seconds']:
        minutes = status['time_until_rebuild_seconds'] / 60
        print(f"  Time until rebuild: {minutes:.1f} minutes")

monitor_grid(1)
```

---

## 🎯 Дополнительные функции

### Автоматический scheduled job

Рекомендуется добавить background task для автоматической перестройки:

```python
# В main.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def check_all_grids():
    """Check all strategies for rebuild necessity."""
    db = SessionLocal()
    try:
        strategies = db.query(Strategy).filter(
            Strategy.is_active == True,
            Strategy.needs_rebuild == True
        ).all()
        
        for strategy in strategies:
            if GridAdaptationManager.should_rebuild_grid(strategy.id, db):
                current_price = get_current_price(strategy.pair)  # из WebSocket
                GridAdaptationManager.rebuild_grid(strategy.id, current_price, db)
    finally:
        db.close()

scheduler.add_job(check_all_grids, 'interval', minutes=1)
scheduler.start()
```

---

## 📊 Статус реализации

| Компонент | Статус | Готовность |
|-----------|--------|-----------|
| Flip Orders API | ✅ | 100% |
| Check Adaptation API | ✅ | 100% |
| Rebuild Grid API | ✅ | 100% |
| Get Grid Status API | ✅ | 100% |
| Should Rebuild API | ✅ | 100% |
| Backend логика | ✅ | 100% |
| Frontend интеграция | 🔄 | 40% |
| Scheduled jobs | ⚠️ | 30% |

---

## ✅ Следующие шаги

1. ✅ Реализованы все API endpoints
2. 🔄 Нужно добавить frontend для отображения статуса сетки
3. ⚠️ Нужны unit тесты
4. ⚠️ Нужна интеграция с WebSocket для real-time обновлений

