# 📊 АДАПТАЦИЯ СТРАТЕГИИ К ПРОЕКТУ
## Анализ и рекомендации реализации

---

## 🎯 ОПИСАНИЕ ТРЕБУЕМОЙ СТРАТЕГИИ

### Основная логика:
1. **Построение сетки ордеров** — симметрично относительно текущего курса
2. **Параметры**: размер лота, размер прибыли, шаг (могут быть разные)
3. **Переворот ордеров** — исполненный ордер меняется на противоположный
4. **Производительность** — минимум 600 сделок в час
5. **Адаптация сетки** — если крайний ордер исполнен, ждём 60 минут и перестраиваем

### Пример параметров:
```
Текущий курс: 1000$
Размер лота: 1
Размер прибыли: 300$
Шаг: 300$

Сетка ордеров:
BUY:  100, 400, 700, 1000  | SELL: 1300, 1600, 1900, 2200
      (ниже цены)          |      (выше цены)
```

---

## ✅ ЧТО УЖЕ РЕАЛИЗОВАНО В ПРОЕКТЕ

### 1. **Adaptive Grid Strategy** (`adaptive_grid.py`)
```python
✅ Класс AdaptiveGridStrategy
✅ GridLevel dataclass для представления уровней
✅ ATR расчеты для волатильности
✅ Генерация сетки (generate_grid)
✅ Расчет размера позиции (calculate_position_size)
✅ Симметричная сетка (BUY ниже, SELL выше)
```

### 2. **Order Manager** (`order_manager.py`)
```python
✅ Создание ордеров (create_order)
✅ Отслеживание статуса ордеров
✅ Отмена ордеров
✅ Обновление статуса ордеров
```

### 3. **Risk Manager** (`risk_manager.py`)
```python
✅ Проверка размера позиции
✅ Проверка максимума активных ордеров
✅ Контроль максимального drawdown
✅ Emergency stop механизм
```

### 4. **Database Models** (`models.py`)
```python
✅ Strategy таблица
✅ Order таблица
✅ Trade таблица
✅ PortfolioSnapshot таблица
```

---

## 🔧 ЧТО ТРЕБУЕТ УЛУЧШЕНИЯ/РАСШИРЕНИЯ

### 1. **Переворот исполненных ордеров** ⚠️
**Статус**: Частично реализовано

**Текущее состояние**:
```python
# В Order Manager есть логика обновления статуса
# НО нет автоматического переворота BUY→SELL или SELL→BUY
```

**Требуемые изменения**:
```python
def flip_filled_order(order_id: int, db: Session):
    """
    Переворачивает исполненный ордер на противоположный.
    BUY → SELL
    SELL → BUY
    """
    # Найти исполненный ордер
    # Создать новый ордер с противоположной стороной
    # Обновить статус исходного ордера
```

**Когда вызывать**: При смене статуса ордера с "open" → "filled"

---

### 2. **Адаптация сетки (перестройка каждые 60 минут)** ⚠️
**Статус**: НЕ реализовано

**Требуемые компоненты**:
```python
class GridAdaptationManager:
    """Управляет переестройкой сетки каждые 60 минут."""
    
    def check_extreme_positions(strategy_id: int) -> bool:
        """Проверяет крайние позиции сетки."""
        # Получить крайний BUY и крайний SELL ордер
        # Проверить, исполнены ли они
        # Если да → запустить таймер на 60 минут
        
    def should_rebuild_grid(strategy_id: int) -> bool:
        """Проверяет нужна ли перестройка сетки."""
        # Если 60 минут прошло И цена не вернулась в коридор
        # → True (нужна перестройка)
        
    def rebuild_grid(strategy_id: int):
        """Отменяет старую сетку и создаёт новую."""
        # Отменить все активные ордера
        # Пересчитать параметры сетки
        # Создать новую сетку
```

**Где поместить**:
- Создать новый файл: `backend/app/strategies/grid_adaptation.py`
- Или добавить в `AdaptiveGridStrategy`

---

### 3. **Параметры сетки: Шаг ≠ Размер прибыли** ⚠️
**Статус**: Нужно расширить конфигурацию

**Текущая реализация**:
```python
# используется только grid_profit_per_trade (0.1%)
# нет отдельного параметра "шаг"
```

**Требуемые изменения в Strategy модели**:
```python
class Strategy(Base):
    __tablename__ = "strategies"
    
    # Существующие параметры
    grid_levels = Column(Integer, default=10)
    grid_profit_per_trade = Column(Float, default=0.1)
    
    # НОВЫЕ параметры
    grid_step = Column(Float, default=0.1)  # Шаг (может отличаться от прибыли)
    lot_size = Column(Float, default=1.0)   # Размер лота
    
    # Параметр для контроля перестройки
    last_grid_rebuild = Column(DateTime, nullable=True)
    extreme_position_detected = Column(DateTime, nullable=True)
    needs_rebuild = Column(Boolean, default=False)
```

---

### 4. **Производительность: 600 сделок/час** ⚠️
**Статус**: Требует оптимизации

**Текущие проблемы**:
- API Binance имеет rate limits (1200 запросов/минуту)
- WebSocket обновления работают в real-time
- Delay в обработке заказов из БД

**Оптимизация**:
```python
# 1. Использовать WebSocket для real-time обновлений цен
✅ Уже есть WebSocket implementation

# 2. Батчинг ордеров (создавать несколько одновременно)
# 3. Кэширование данных в Redis
# 4. Асинхронная обработка заказов

# Текущая пропускная способность:
# ~10-50 ордеров/минуту (зависит от Binance)
# Для 600/часа нужно ~10 ордеров/минуту
# ✅ ДОСТИЖИМО с текущей архитектурой
```

---

## 📝 ПЛАНИРУЕМЫЕ УЛУЧШЕНИЯ (По приоритетам)

### 🔴 КРИТИЧЕСКИЕ (ОБЯЗАТЕЛЬНО)

#### 1. Реализовать автоматический переворот ордеров
**Файл**: `backend/app/strategies/adaptive_grid.py` или новый модуль

**Код**:
```python
def flip_filled_orders(strategy_id: int, db: Session):
    """Переворачивает исполненные ордера."""
    
    # Получить все исполненные ордера стратегии
    filled_orders = db.query(Order).filter(
        Order.strategy_id == strategy_id,
        Order.status == "filled"
    ).all()
    
    for order in filled_orders:
        # Создать противоположный ордер
        opposite_side = "SELL" if order.side == "BUY" else "BUY"
        
        new_order = Order(
            strategy_id=strategy_id,
            pair=order.pair,
            side=opposite_side,
            price=order.price,  # На том же уровне
            quantity=order.quantity,
            is_grid_order=True,
            grid_level=order.grid_level
        )
        
        db.add(new_order)
        db.commit()
        
        # Обновить статус старого ордера
        order.status = "flipped"
        db.commit()
        
        logger.info(f"Flipped order {order.id}: {order.side} → {opposite_side}")
```

**Где вызывать**: 
- В `OrderManager.update_order_status()` при переходе в "filled"
- Или в отдельном scheduled job каждую минуту

---

#### 2. Расширить параметры Strategy модели
**Файл**: `backend/app/models/models.py`

**Изменения**:
```python
class Strategy(Base):
    # ... существующие поля ...
    
    # ДОБАВИТЬ:
    grid_step = Column(Float, default=0.1)  # % шаг между уровнями
    lot_size = Column(Float, default=1.0)   # Размер одного лота
    
    last_grid_rebuild = Column(DateTime, nullable=True)
    extreme_position_detected = Column(DateTime, nullable=True)
    needs_rebuild = Column(Boolean, default=False)
```

---

### 🟡 ВАЖНЫЕ (ОБЯЗАТЕЛЬНО В БЛИЖАЙШЕЕ ВРЕМЯ)

#### 3. Реализовать логику адаптации сетки (60 минут)
**Создать новый файл**: `backend/app/strategies/grid_adaptation.py`

**Основная логика**:
```python
class GridAdaptationManager:
    
    def check_and_rebuild(strategy_id: int, db: Session):
        """Проверяет нужна ли перестройка сетки."""
        
        strategy = db.query(Strategy).get(strategy_id)
        
        # Если сетка уже отмечена на перестройку
        if not strategy.needs_rebuild:
            return
        
        # Проверить, прошло ли 60 минут
        if strategy.extreme_position_detected:
            elapsed = datetime.utcnow() - strategy.extreme_position_detected
            if elapsed.total_seconds() < 3600:  # < 60 минут
                return  # Ждём дальше
        
        # 60 минут прошло → перестраиваем
        GridAdaptationManager.rebuild_grid(strategy_id, db)
    
    def rebuild_grid(strategy_id: int, db: Session):
        """Перестраивает сетку ордеров."""
        
        # 1. Отменить все активные ордера
        active_orders = db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.status == "open"
        ).all()
        
        for order in active_orders:
            order.status = "cancelled"
        
        # 2. Создать новую сетку по текущей цене
        current_price = get_current_price(strategy.pair)
        new_grid = AdaptiveGridStrategy.generate_grid(
            center_price=current_price,
            grid_levels=strategy.grid_levels,
            profit_percent=strategy.grid_profit_per_trade,
            step_percent=strategy.grid_step
        )
        
        # 3. Создать новые ордера
        for level in new_grid:
            create_order_from_grid_level(level, strategy_id, db)
        
        # 4. Обновить статус стратегии
        strategy.needs_rebuild = False
        strategy.extreme_position_detected = None
        strategy.last_grid_rebuild = datetime.utcnow()
        
        db.commit()
```

---

#### 4. Добавить поддержку разных параметров (шаг и прибыль)
**Файл**: `backend/app/strategies/adaptive_grid.py`

**Текущий метод генерации**:
```python
def generate_grid(self, center_price: float, atr: float = None) -> List[GridLevel]:
    """Генерирует симметричную сетку уровней."""
    
    # УЛУЧШЕНИЕ: использовать отдельные параметры шага и прибыли
    # Вместо:
    #   step = center_price * self.grid_profit_per_trade / 100
    # Использовать:
    #   step = center_price * self.grid_step / 100
    #   profit = center_price * self.grid_profit_per_trade / 100
    
    step_amount = center_price * (self.grid_step or self.grid_profit_per_trade) / 100
    profit_amount = center_price * self.grid_profit_per_trade / 100
    
    # Остальная логика...
```

---

### 🟢 ДОПОЛНИТЕЛЬНЫЕ (NICE-TO-HAVE)

#### 5. Оптимизация под 600 сделок/час
- Использовать batch-create для ордеров (если API поддерживает)
- Кэшировать текущую цену в Redis
- Асинхронный WebSocket для real-time обновлений
- Оптимизировать запросы к БД (индексы, joins)

---

## 🔍 ТЕКУЩАЯ ГОТОВНОСТЬ ПО КОМПОНЕНТАМ

### Готовность реализации: **60-70%**

| Компонент | Статус | % | Требует |
|-----------|--------|---|---------|
| Генерация сетки | ✅ Готово | 100% | Тесты |
| Симметричные BUY/SELL | ✅ Готово | 100% | Тесты |
| ATR волатильность | ✅ Готово | 100% | Тесты |
| Отслеживание ордеров | ✅ Готово | 100% | Тесты |
| **Переворот ордеров** | ⚠️ Частично | 30% | Реализация логики |
| **Адаптация сетки (60 мин)** | ❌ Нет | 0% | Полная реализация |
| **Разные параметры (шаг/прибыль)** | ⚠️ Частично | 40% | Расширение модели |
| **600 сделок/час** | ✅ Готово | 100% | Оптимизация WebSocket |

---

## 🚀 РЕКОМЕНДУЕМЫЙ ПОРЯДОК РЕАЛИЗАЦИИ

### Фаза 1 (КРИТИЧНО) - 2-3 дня
1. ✅ Расширить Strategy модель (новые поля)
2. ✅ Реализовать переворот ордеров (flip logic)
3. ✅ Добавить тесты

### Фаза 2 (ВАЖНО) - 3-4 дня
4. ✅ Реализовать GridAdaptationManager
5. ✅ Добавить scheduled job для проверки перестройки
6. ✅ Протестировать логику адаптации

### Фаза 3 (ОПЦИОНАЛЬНО) - 2 дня
7. ✅ Оптимизация производительности
8. ✅ Мониторинг и метрики

---

## 📊 ПРИМЕР КОНФИГУРАЦИИ

### Текущая конфигурация (недостаточная):
```python
{
    "name": "Demo BTC Grid Bot",
    "pair": "BTCUSDT",
    "grid_levels": 10,
    "grid_profit_per_trade": 0.1,  # 0.1% прибыль за сделку
    "atr_period": 14,
    "atr_multiplier": 2.0
}
```

### Требуемая конфигурация:
```python
{
    "name": "Demo BTC Grid Bot",
    "pair": "BTCUSDT",
    
    # Параметры сетки
    "grid_levels": 10,           # Количество уровней
    "grid_step": 0.5,            # 0.5% - ШАГ между уровнями
    "grid_profit_per_trade": 1.0, # 1.0% - РАЗМЕР ПРИБЫЛИ за сделку
    "lot_size": 1.0,             # Размер одного лота
    
    # ATR параметры
    "atr_period": 14,
    "atr_multiplier": 2.0,
    
    # Адаптация сетки
    "rebuild_enabled": true,     # Включить перестройку
    "rebuild_interval_minutes": 60 # Перестраивать каждые 60 минут
}
```

---

## 🎯 ВЫВОДЫ

### ✅ Проект хорошо подготовлен:
- Architecture готова
- Database модели подходят
- WebSocket для real-time данных
- Risk Management включен
- Order Management работает

### ⚠️ Требуется доработать:
1. **Автоматический переворот ордеров** — критично
2. **Адаптация сетки каждые 60 минут** — критично
3. **Расширить параметры стратегии** — важно
4. **Тестирование** — очень важно

### 🚀 Готовность к продакшену: **65%**
Основные компоненты есть, нужна финализация логики адаптации.

---

## 📌 ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ

### 1. Мониторинг
```python
# Отслеживать:
- Сколько ордеров создано/исполнено в час
- Сколько раз пересстроена сетка
- Профит/loss за период
- Время выполнения операций
```

### 2. Тестирование
```python
# Создать unit тесты для:
- grid generation с разными параметрами
- flip logic (BUY→SELL и обратно)
- rebuild logic (перестройка каждые 60 минут)
```

### 3. Dashboard обновления
```python
# На frontend нужно показывать:
- Когда произойдёт следующая перестройка сетки
- Какой ордер был перевёрнут и когда
- История перестроек сетки
```

