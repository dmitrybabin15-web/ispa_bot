# 🤖 Telegram Bot - Готовый к деплою на Beget VPS

## ✅ Статус: Готово к деплою

Это полностью подготовленный Telegram бот, адаптированный для запуска на **Beget VPS** с использованием **Webhook** вместо Polling.

---

## 🎯 Что сделано

✅ Переделана архитектура с **polling на webhook** (экономит ресурсы)  
✅ Подготовлены **скрипты автоматизации** для деплоя  
✅ Созданы **конфиги для Nginx и Systemd**  
✅ Написаны **подробные инструкции**  
✅ Добавлена **обработка ошибок и логирование**  

---

## 📚 Документация

### 📖 Главная инструкция
- **[DEPLOY_BEGET.md](DEPLOY_BEGET.md)** ← **ЧИТАЙТЕ ЭТО ПЕРВЫМ!**
  - Пошаговая инструкция с примерами команд
  - 10 основных шагов деплоя
  - Решение проблем
  - Управление ботом

### 📝 Справочные материалы
- **[SETUP.md](SETUP.md)** — Резюме, архитектура, быстрый старт
- **[FILES_CHECKLIST.md](FILES_CHECKLIST.md)** — Список всех файлов и их назначение

### 🔧 Конфигурационные файлы
- **[.env.example](.env.example)** — Шаблон переменных (скопируйте в `.env` и заполните)

---

## 📁 Основные файлы

| Файл | Описание | Статус |
|------|---------|--------|
| `main_webhook.py` | 🆕 Точка входа с webhook | ⭐ НОВЫЙ |
| `deploy-beget.sh` | 🆕 Скрипт автоматизированного деплоя | ⭐ НОВЫЙ |
| `telegram-bot.service` | 🆕 Systemd сервис для автозапуска | ⭐ НОВЫЙ |
| `nginx-telegram-bot.conf` | 🆕 Конфиг Nginx для проксирования | ⭐ НОВЫЙ |
| `requirements.txt` | ✏️ Обновлён (добавлены aiohttp, gunicorn) | ✏️ ОБНОВЛЁН |
| `.env` | ⚙️ Переменные окружения (заполните!) | ⚠️ ВАЖНО |

---

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Подготовьте конфигурацию

```bash
# Скопируйте шаблон
cp .env.example .env

# Отредактируйте с вашими значениями
nano .env
```

**Минимум для заполнения:**
```env
BOT_TOKEN=YOUR_TOKEN_FROM_@BotFather
GROUP_ID=-1002948213273
ADMIN_IDS=123456789
```

### Шаг 2: Загрузите на Beget сервер

```bash
# С вашей машины:
scp -r ./* user@beget.server:~/bot/
```

### Шаг 3: Запустите деплой на сервере

```bash
# Подключитесь к серверу
ssh user@beget.server
cd ~/bot

# Запустите скрипт деплоя
chmod +x deploy-beget.sh
./deploy-beget.sh
```

### Шаг 4: Запустите бота

```bash
# Включите автозапуск
sudo systemctl enable telegram-bot

# Запустите
sudo systemctl start telegram-bot

# Проверьте статус
sudo systemctl status telegram-bot
```

---

## ⚠️ Важно: Beget “обычный” SSH без sudo/systemd

Если у вас **нет `sudo`** и `systemctl` недоступен (часто на shared-хостинге), используйте режим **polling** и управляйте ботом скриптами:

```bash
cd ~/ispa_host
chmod +x start.sh stop.sh status.sh cron-keepalive.sh
./start.sh
./status.sh
tail -200 logs/app.log
tail -200 logs/error.log
```

### Автоподъём (рекомендуется)

Добавьте в cron (через `crontab -e`) проверку раз в минуту:

```cron
* * * * * /home/USER/ispa_host/cron-keepalive.sh >/dev/null 2>&1
```

Замените `USER` на имя пользователя (`whoami`).

### Шаг 5: Установите Webhook

```bash
# Замените BOT_TOKEN и YOUR_DOMAIN
curl -X POST https://api.telegram.org/botBOT_TOKEN/setWebhook \
  -d "url=https://YOUR_DOMAIN/webhook"
```

**Всё! Бот готов к работе! 🎉**

---

## 🔍 Проверка работы

### Здоровье приложения
```bash
curl https://YOUR_DOMAIN/health
# Ответ: ok
```

### Статус webhook
```bash
curl https://api.telegram.org/botBOT_TOKEN/getWebhookInfo
```

### Логи в реальном времени
```bash
sudo journalctl -u telegram-bot -f
```

---

## 📋 Требования

- **Beget VPS** с SSH доступом
- **Python 3.9+** на сервере
- **Домен** на Beget (или другом хостинге)
- **BOT_TOKEN** от Telegram (@BotFather)
- **SSL сертификат** (Let's Encrypt или от Beget)

---

## 🛠️ Управление

### Основные команды

```bash
# Статус бота
sudo systemctl status telegram-bot

# Перезагрузить бота
sudo systemctl restart telegram-bot

# Остановить бота
sudo systemctl stop telegram-bot

# Включить автозапуск
sudo systemctl enable telegram-bot

# Просмотр логов
sudo journalctl -u telegram-bot -n 100 -f

# Просмотр файлов логов
tail -f ~/bot/logs/error.log
```

---

## 🎓 Архитектура

```
Telegram API (HTTPS)
       ↓
   Nginx (порт 443)
  - SSL/TLS
  - Балансировка нагрузки
       ↓
  Gunicorn (порт 8000)
  - WSGI сервер
  - 1+ workers
       ↓
  aiohttp приложение
  - Webhook обработчик
  - Асинхронные операции
       ↓
  Bot Handlers + Services
  - Обработка команд
  - Парсинг сайта
  - Публикация сообщений
       ↓
  SQLite Database
  - Хранение состояния
  - История сообщений
```

---

## 📞 Помощь и решение проблем

### Если бот не работает

1. **Проверьте статус:**
   ```bash
   sudo systemctl status telegram-bot
   ```

2. **Смотрите ошибки:**
   ```bash
   tail -100 ~/bot/logs/error.log
   sudo journalctl -u telegram-bot -n 50
   ```

3. **Перезагрузите:**
   ```bash
   sudo systemctl restart telegram-bot
   ```

4. **Читайте инструкцию:**
   - Раздел "Решение проблем" в [DEPLOY_BEGET.md](DEPLOY_BEGET.md)

---

## 🔗 Полезные ссылки

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Beget Support:** https://beget.com/
- **Let's Encrypt:** https://letsencrypt.org/
- **Aiogram Docs:** https://docs.aiogram.dev/
- **Nginx Docs:** https://nginx.org/

---

## 📝 Лицензия

MIT

---

## 🎉 Вы готовы!

Все файлы подготовлены. Просто следуйте инструкциям в [DEPLOY_BEGET.md](DEPLOY_BEGET.md).

**Успехов с деплоем! 🚀**

---

### 💡 Совет

Если это ваш первый раз:
1. Прочитайте [SETUP.md](SETUP.md) для понимания архитектуры
2. Следуйте [DEPLOY_BEGET.md](DEPLOY_BEGET.md) пошагово
3. Используйте [FILES_CHECKLIST.md](FILES_CHECKLIST.md) как справочник

Если у вас есть вопросы — проверьте раздел "Решение проблем" в документации или логи бота.
