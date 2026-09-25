# 📝 Резюме: Перенос Telegram бота на Beget VPS

## ✅ Что было сделано

### 1. **Переделка архитектуры: Polling → Webhook**

**Было:** `main.py` использовал `dispatcher.start_polling()` (long-polling)
- ❌ Требует постоянного соединения
- ❌ Потребляет больше ресурсов
- ❌ Не подходит для shared hosting

**Стало:** `main_webhook.py` использует **aiohttp** webhook
- ✅ Stateless архитектура (идеально для VPS)
- ✅ Экономнее по ресурсам
- ✅ Масштабируемо через Nginx + Gunicorn
- ✅ SSL/HTTPS безопасность

### 2. **Подготовленные файлы**

| Файл | Описание |
|------|---------|
| `main_webhook.py` | Новая точка входа с aiohttp webhooks |
| `requirements.txt` | Обновлены (добавлены `aiohttp`, `gunicorn`) |
| `deploy-beget.sh` | Автоматизированный скрипт деплоя |
| `telegram-bot.service` | Systemd сервис для автозапуска |
| `nginx-telegram-bot.conf` | Конфигурация Nginx для проксирования |
| `DEPLOY_BEGET.md` | Подробная пошаговая инструкция |

### 3. **Архитектура на Beget VPS**

```
Telegram API (HTTPS)
       ↓
   Nginx (порт 443)
       ↓
 Gunicorn (8000)
  ↙          ↖
Worker 1   Worker N
       ↓
  aiohttp
       ↓
   Bot App
       ↓
  Handlers + Services
       ↓
  SQLite DB
```

---

## 🚀 Быстрый старт

### Для локального тестирования:

```bash
# 1. Заполните .env
cp .env.example .env
nano .env  # Добавьте BOT_TOKEN

# 2. Установите зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Запустите локально
python main_webhook.py
# Бот будет слушать на http://localhost:8000
```

### Для деплоя на Beget:

```bash
# 1. Загрузите файлы на сервер через SCP
scp -r ./* user@beget.server:~/bot/

# 2. Подключитесь по SSH
ssh user@beget.server
cd ~/bot

# 3. Запустите деплой
chmod +x deploy-beget.sh
./deploy-beget.sh

# 4. Включите сервис
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# 5. Установите webhook
curl -X POST https://api.telegram.org/botBOT_TOKEN/setWebhook \
  -d "url=https://YOUR_DOMAIN/webhook"
```

---

## 📋 Чек-лист перед деплоем

- [ ] Получили **BOT_TOKEN** от @BotFather
- [ ] Имеете **SSH доступ** к Beget VPS
- [ ] Имеете **домен** на Beget или другом хостинге
- [ ] Python 3.9+ установлен на сервере
- [ ] Заполнили все переменные в `.env`
- [ ] Скопировали файлы на сервер
- [ ] Запустили `deploy-beget.sh`
- [ ] Установили SSL сертификат (Let's Encrypt)
- [ ] Установили webhook в Telegram API
- [ ] Проверили логи: `sudo journalctl -u telegram-bot -f`

---

## 🔑 Ключевые переменные .env

```env
# Обязательно заполните:
BOT_TOKEN=YOUR_TOKEN_FROM_BOTFATHER
GROUP_ID=-1002948213273          # ID группы, где постить
ADMIN_IDS=6068353947,123456789   # ID администраторов (через запятую)

# Опционально (есть значения по умолчанию):
TIMEZONE=Europe/Moscow
DAILY_PUBLICATION_HOUR=12
DAILY_PUBLICATION_MINUTE=30
SITE_URL=https://i-spa.su/girls/
BOOKING_URL=https://t.me/spa_spb78
ADDRESS_TEXT=СПБ. ул.Театральная пл. дом 8
TELEGRAM_CONTACT=@spa_spb78
PHONE_TEXT=+7-931-393-33-68
```

---

## 🔧 Команды для управления

```bash
# Статус:
sudo systemctl status telegram-bot

# Логи (последние 50 строк):
sudo journalctl -u telegram-bot -n 50

# Логи в реальном времени:
sudo journalctl -u telegram-bot -f

# Перезагрузить:
sudo systemctl restart telegram-bot

# Остановить:
sudo systemctl stop telegram-bot

# Включить автозапуск:
sudo systemctl enable telegram-bot

# Отключить автозапуск:
sudo systemctl disable telegram-bot
```

---

## 🧪 Проверка работы

### 1. Проверьте здоровье приложения

```bash
curl https://YOUR_DOMAIN/health
# Ответ: ok
```

### 2. Проверьте webhook в Telegram

```bash
BOT_TOKEN="YOUR_TOKEN"
curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo | python3 -m json.tool
```

Должно быть:
```json
{
  "ok": true,
  "result": {
    "url": "https://YOUR_DOMAIN/webhook",
    "pending_update_count": 0
  }
}
```

### 3. Протестируйте бота

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте `/start`
4. Проверьте ответ в чате

### 4. Смотрите логи

```bash
sudo journalctl -u telegram-bot -f
```

---

## 📚 Документация

- **`DEPLOY_BEGET.md`** — Подробная пошаговая инструкция деплоя
- **`nginx-telegram-bot.conf`** — Конфиг для Nginx
- **`telegram-bot.service`** — Systemd сервис
- **`deploy-beget.sh`** — Автоматизированный скрипт
- **`.env.example`** — Шаблон переменных окружения

---

## 🆘 Решение проблем

### Бот не отвечает

```bash
# 1. Проверьте статус
sudo systemctl status telegram-bot

# 2. Смотрите ошибки
tail -100 ~/bot/logs/error.log

# 3. Перезагрузите
sudo systemctl restart telegram-bot

# 4. Переустановите webhook
curl -X POST https://api.telegram.org/botBOT_TOKEN/setWebhook \
  -d "url=https://YOUR_DOMAIN/webhook"
```

### Ошибка 502 Bad Gateway

```bash
# Проверьте, запущен ли gunicorn
ps aux | grep gunicorn

# Перезагрузите Nginx
sudo systemctl reload nginx
sudo systemctl restart telegram-bot
```

### Проблемы с SSL

```bash
# Обновите сертификат
sudo certbot renew

# Проверьте Nginx конфиг
sudo nginx -t

# Перезагрузите Nginx
sudo systemctl reload nginx
```

---

## 📞 Контакты и ссылки

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Beget.com:** https://beget.com/
- **Let's Encrypt:** https://letsencrypt.org/
- **Aiogram документация:** https://docs.aiogram.dev/

---

## 🎉 Готово!

Ваш бот теперь готов к деплою на Beget VPS!

**Успехов с деплоем! 🚀**
