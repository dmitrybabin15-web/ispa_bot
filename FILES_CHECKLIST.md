# 📦 Список подготовленных файлов для деплоя на Beget

## 📂 Структура проекта после подготовки

```
ispa_host/
├── 📄 main_webhook.py              ⭐ НОВЫЙ - Точка входа с webhook
├── 📄 main.py                       (старый файл - можно удалить)
├── 📄 requirements.txt              ✅ ОБНОВЛЁН - добавлены aiohttp, gunicorn
│
├── 🚀 deploy-beget.sh              ⭐ НОВЫЙ - Автоматизированный деплой
├── 📋 telegram-bot.service         ⭐ НОВЫЙ - Systemd сервис
├── 🔧 nginx-telegram-bot.conf      ⭐ НОВЫЙ - Конфиг Nginx
│
├── 📖 DEPLOY_BEGET.md              ⭐ НОВЫЙ - Подробная инструкция
├── 📖 SETUP.md                     ⭐ НОВЫЙ - Резюме и чек-лист
│
├── 📄 .env                         ✅ ЗАПОЛНИТЬ - Переменные окружения
├── 📄 .env.example                 (шаблон, не изменять)
│
├── 🗂️  handlers/                   (без изменений)
│   ├── __init__.py
│   └── users/
│       ├── __init__.py
│       └── start.py
│
├── 🗂️  services/                   (без изменений)
│   ├── __init__.py
│   ├── bot_messages.py
│   ├── publishing.py
│   ├── scheduler.py
│   └── spa_parser.py
│
├── 🗂️  db/                         (без изменений)
│   ├── __init__.py
│   ├── init.py
│   └── models.py
│
├── 🗂️  db-data/                    (БД, локально)
│   └── db.sqlite3
│
├── 🗂️  data/                       (без изменений)
│   ├── __init__.py
│   └── config.py
│
└── 🗂️  utils/                      (без изменений)
    ├── __init__.py
    ├── notify_admins.py
    └── set_bot_commands.py
```

---

## ⭐ Основные новые файлы

### 1. `main_webhook.py` 
**Назначение:** Точка входа приложения с webhook вместо polling
- ✅ Использует aiohttp для асинхронного веб-сервера
- ✅ Поддерживает масштабирование через Gunicorn
- ✅ Регистрирует обработчик `/webhook`
- ✅ Health check на `/health`
- **Использование:** `python main_webhook.py` (разработка) или `gunicorn --worker-class aiohttp.GunicornWebWorker --bind 0.0.0.0:8000 main_webhook:create_app` (production)

### 2. `deploy-beget.sh`
**Назначение:** Автоматизированный скрипт деплоя
- ✅ Создаёт виртуальное окружение Python
- ✅ Устанавливает зависимости
- ✅ Создаёт директорию логов
- ✅ Проверяет конфигурацию `.env`
- ✅ Устанавливает systemd сервис
- **Использование:** `chmod +x deploy-beget.sh && ./deploy-beget.sh`

### 3. `telegram-bot.service`
**Назначение:** Systemd сервис для автозапуска и управления
- ✅ Автоматический перезапуск при падении
- ✅ Запуск при загрузке системы
- ✅ Управление через `systemctl`
- **Использование:** Автоматически устанавливается скриптом `deploy-beget.sh`

### 4. `nginx-telegram-bot.conf`
**Назначение:** Конфиг Nginx для проксирования запросов на Gunicorn
- ✅ HTTPS перенаправление (443)
- ✅ SSL сертификат (Let's Encrypt)
- ✅ Проксирование на localhost:8000
- ✅ Headers для безопасности
- **Использование:** `sudo cp nginx-telegram-bot.conf /etc/nginx/sites-available/telegram-bot`

---

## 📖 Документация

### 1. `DEPLOY_BEGET.md`
**Подробная пошаговая инструкция:**
- 10 основных шагов деплоя
- Скриншоты и примеры команд
- Решение проблем
- Управление ботом
- Мониторинг

### 2. `SETUP.md`
**Быстрое резюме:**
- Архитектура решения
- Чек-лист перед деплоем
- Быстрые команды
- Решение типичных проблем

---

## 🔄 Обновленные файлы

### `requirements.txt`
**Что изменилось:**
```diff
  aiogram>=3.4,<4.0
  APScheduler>=3.10,<4.0
+ aiohttp>=3.8,<4.0        ← НОВАЯ (для webhook)
  beautifulsoup4>=4.12,<5.0
  python-dotenv>=1.0,<2.0
  requests>=2.31,<3.0
  tortoise-orm>=0.20,<1.0
+ gunicorn>=21.2,<22.0      ← НОВАЯ (для production)
```

---

## ✅ Что можно удалить (опционально)

После деплоя на Beget можете удалить:
- ❌ `main.py` (заменён на `main_webhook.py`)
- ❌ `Dockerfile` (не нужен без Docker)
- ❌ `docker-compose.yml` (не нужен без Docker)
- ❌ `.dockerignore` (не нужен без Docker)
- ❌ `DEPLOY.md` (заменён на `DEPLOY_BEGET.md`)

---

## 📤 Что скачать и загрузить на сервер

### Обязательные файлы:
```bash
# Основное приложение
main_webhook.py
requirements.txt

# Деплой и конфигурация
deploy-beget.sh
telegram-bot.service
nginx-telegram-bot.conf

# Конфигурация
.env (заполненный)

# Остальной код
handlers/
services/
db/
data/
utils/
```

### Опциональные файлы (для справки):
```bash
DEPLOY_BEGET.md   # Инструкция
SETUP.md          # Резюме
```

---

## 🚀 Быстрый старт (15 минут)

### На вашей машине:
```bash
# 1. Скачайте все файлы
cd ispa_host

# 2. Заполните .env
cp .env.example .env
nano .env  # Добавьте BOT_TOKEN

# 3. Загрузите на сервер
scp -r ./* user@beget.server:~/bot/
```

### На Beget сервере:
```bash
# 1. Подключитесь
ssh user@beget.server
cd ~/bot

# 2. Запустите деплой
chmod +x deploy-beget.sh
./deploy-beget.sh

# 3. Включите бота
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# 4. Установите webhook
curl -X POST https://api.telegram.org/bot$BOT_TOKEN/setWebhook \
  -d "url=https://YOUR_DOMAIN/webhook"

# 5. Проверьте
curl https://YOUR_DOMAIN/health
```

---

## 📞 Если что-то не работает

1. **Проверьте логи:**
   ```bash
   sudo journalctl -u telegram-bot -f
   tail -f ~/bot/logs/error.log
   ```

2. **Перезагрузите:**
   ```bash
   sudo systemctl restart telegram-bot
   ```

3. **Смотрите DEPLOY_BEGET.md:**
   ```bash
   less DEPLOY_BEGET.md
   # Раздел: "Решение проблем"
   ```

---

## 🎉 Готово!

Все файлы подготовлены для деплоя на Beget VPS.

**Следующий шаг:** Прочитайте `DEPLOY_BEGET.md` и запустите `deploy-beget.sh`

Успехов! 🚀
