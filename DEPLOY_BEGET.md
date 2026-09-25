# 🚀 Инструкция деплоя Telegram бота на Beget VPS

## Требования

- **Beget VPS** с SSH доступом
- **Домен** на Beget (например `bot.example.com`)
- **BOT_TOKEN** от Telegram (@BotFather)
- **Python 3.9+** на сервере
- **Nginx** или Apache (для проксирования)
- **SSL сертификат** (Let's Encrypt или от Beget)

---

## 📋 Шаг 1: Подготовка на вашей машине

### 1.1 Клонируйте или скопируйте проект

```bash
# Если используете git:
git clone <ваш_репо> ispa_host
cd ispa_host

# Или распакуйте архив:
unzip ispa_host_deploy_ready.zip
cd ispa_host
```

### 1.2 Убедитесь, что все файлы на месте

```bash
ls -la
# Должны быть:
# - main_webhook.py
# - requirements.txt
# - deploy-beget.sh
# - telegram-bot.service
# - nginx-telegram-bot.conf
# - .env.example
# - handlers/
# - services/
# - db/
```

### 1.3 Заполните .env локально для тестирования

```bash
cp .env.example .env
nano .env  # отредактируйте BOT_TOKEN и другие переменные
```

---

## 🔑 Шаг 2: Подготовка на Beget сервере

### 2.1 Подключитесь к Beget по SSH

```bash
ssh username@your_beget_server.beget.ru
# или
ssh username@your_ip_address
```

### 2.2 Проверьте версию Python

```bash
python3 --version  # Должно быть 3.9 или выше
```

Если Python не установлен или старая версия:
```bash
# На Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2.3 Создайте директорию для бота

```bash
mkdir -p ~/bot
cd ~/bot
```

---

## 📤 Шаг 3: Загрузка файлов на сервер

### Вариант А: Через SCP (рекомендуется)

```bash
# На вашей локальной машине:
cd /path/to/ispa_host

# Загружаем весь проект
scp -r ./* username@your_beget_server.beget.ru:~/bot/

# Или конкретные файлы:
scp main_webhook.py requirements.txt deploy-beget.sh telegram-bot.service .env username@your_beget_server.beget.ru:~/bot/
scp -r handlers services db data utils username@your_beget_server.beget.ru:~/bot/
```

### Вариант Б: Через SFTP (через cPanel)

1. Откройте File Manager в cPanel
2. Перейдите в `/home/username/`
3. Создайте папку `bot`
4. Загрузите все файлы туда

### Вариант В: Через Git (если используете Git)

```bash
ssh username@your_beget_server.beget.ru
cd ~/bot
git clone <ваш_репо> .
```

---

## ⚙️ Шаг 4: Автоматизированный деплой

### 4.1 Сделайте скрипт деплоя исполняемым

```bash
ssh username@your_beget_server.beget.ru
cd ~/bot
chmod +x deploy-beget.sh
```

### 4.2 Запустите скрипт деплоя

```bash
./deploy-beget.sh
```

Скрипт:
- ✅ Создаст виртуальное окружение Python
- ✅ Установит все зависимости
- ✅ Создаст директорию логов
- ✅ Проверит .env
- ✅ Установит systemd service

---

## 🔧 Шаг 5: Заполнение конфигурации

### 5.1 Отредактируйте .env на сервере

```bash
nano ~/bot/.env
```

Измените следующие переменные:

```env
BOT_TOKEN=ВСТАВЬТЕ_ВАШЕ_ЗНАЧЕНИЕ_ОТ_@BotFather
GROUP_ID=-1002948213273
ADMIN_IDS=6068353947
TIMEZONE=Europe/Moscow
DAILY_PUBLICATION_HOUR=12
DAILY_PUBLICATION_MINUTE=30
BOT_MESSAGE_TTL_SECONDS=86399
SITE_URL=https://i-spa.su/girls/
BOOKING_URL=https://t.me/spa_spb78
ADDRESS_TEXT=СПБ. ул.Театральная пл. дом 8
TELEGRAM_CONTACT=@spa_spb78
PHONE_TEXT=+7-931-393-33-68
DB_FILE=db.sqlite3
```

**Сохраните:** Ctrl+O → Enter → Ctrl+X

---

## 🌐 Шаг 6: Настройка Nginx

### 6.1 Отредактируйте конфиг Nginx

```bash
# Замените домен на ваш
sed -i 's/ваш_домен.бегет.ру/ВАШ_РЕАЛЬНЫЙ_ДОМЕН/g' ~/bot/nginx-telegram-bot.conf
```

### 6.2 Скопируйте конфиг в Nginx

```bash
sudo cp ~/bot/nginx-telegram-bot.conf /etc/nginx/sites-available/telegram-bot
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/ 2>/dev/null || true
```

### 6.3 Проверьте конфиг Nginx

```bash
sudo nginx -t
```

Если ошибки — отредактируйте:
```bash
sudo nano /etc/nginx/sites-available/telegram-bot
```

### 6.4 Перезагрузите Nginx

```bash
sudo systemctl reload nginx
```

---

## 🔐 Шаг 7: SSL сертификат (Let's Encrypt)

### 7.1 Установите Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### 7.2 Получите сертификат

```bash
sudo certbot certonly --nginx -d ВАШ_ДОМЕН
```

**Следуйте подсказкам:**
- Введите email
- Согласитесь с Terms of Service (Y)
- Сертификат будет установлен в `/etc/letsencrypt/live/ВАШ_ДОМЕН/`

### 7.3 Обновите пути в конфиге Nginx

```bash
sudo nano /etc/nginx/sites-available/telegram-bot
```

Проверьте пути к сертификату:
```nginx
ssl_certificate /etc/letsencrypt/live/ВАШ_ДОМЕН/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/ВАШ_ДОМЕН/privkey.pem;
```

### 7.4 Перезагрузите Nginx

```bash
sudo systemctl reload nginx
```

---

## ▶️ Шаг 8: Запуск бота

### 8.1 Включите systemd сервис

```bash
sudo systemctl enable telegram-bot
```

### 8.2 Запустите сервис

```bash
sudo systemctl start telegram-bot
```

### 8.3 Проверьте статус

```bash
sudo systemctl status telegram-bot
```

Должно быть: `active (running)`

### 8.4 Смотрите логи

```bash
sudo journalctl -u telegram-bot -f
# Или:
tail -f ~/bot/logs/error.log
```

---

## 🔌 Шаг 9: Установка Webhook в Telegram

### 9.1 Получите информацию бота

```bash
# Замените BOT_TOKEN
BOT_TOKEN="ВАШ_BOT_TOKEN"
DOMAIN="ВАШ_ДОМЕН"
```

### 9.2 Установите Webhook

```bash
curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/setWebhook \
  -d "url=https://${DOMAIN}/webhook" \
  -d "allowed_updates=[]"
```

**Ожидаемый ответ:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### 9.3 Проверьте Webhook

```bash
curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo | python3 -m json.tool
```

Должно быть:
```json
{
  "ok": true,
  "result": {
    "url": "https://ВАШ_ДОМЕН/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## ✅ Шаг 10: Проверка работы

### 10.1 Проверьте здоровье приложения

```bash
curl -k https://ВАШ_ДОМЕН/health
# Ответ: ok
```

### 10.2 Протестируйте бота

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте команду `/start`
4. Проверьте ответ

### 10.3 Смотрите логи

```bash
sudo journalctl -u telegram-bot -n 50 -f
# Или:
tail -f ~/bot/logs/error.log
```

---

## 🔄 Управление ботом

### Перезагрузить бота

```bash
sudo systemctl restart telegram-bot
```

### Остановить бота

```bash
sudo systemctl stop telegram-bot
```

### Включить автозапуск при перезагрузке сервера

```bash
sudo systemctl enable telegram-bot
```

### Отключить автозапуск

```bash
sudo systemctl disable telegram-bot
```

### Просмотр логов

```bash
# Последние 100 строк:
tail -100 ~/bot/logs/error.log

# Слежение в реальном времени:
tail -f ~/bot/logs/error.log

# Через systemd:
sudo journalctl -u telegram-bot -f
```

---

## 🐛 Решение проблем

### Проблема: 502 Bad Gateway

**Решение:**
```bash
# Проверьте, запущен ли бот:
sudo systemctl status telegram-bot

# Перезагрузите:
sudo systemctl restart telegram-bot

# Проверьте логи:
tail -f ~/bot/logs/error.log
```

### Проблема: SSL сертификат не работает

**Решение:**
```bash
# Обновите сертификат:
sudo certbot renew

# Проверьте Nginx конфиг:
sudo nginx -t
sudo systemctl reload nginx
```

### Проблема: БД заблокирована

**Решение:**
```bash
# Удалите файл БД:
rm ~/bot/db.sqlite3

# Перезагрузите бота:
sudo systemctl restart telegram-bot
```

### Проблема: Бот не отвечает

**Решение:**
```bash
# Проверьте webhook:
curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo

# Переустановите webhook:
curl -X POST https://api.telegram.org/bot${BOT_TOKEN}/setWebhook \
  -d "url=https://ВАШ_ДОМЕН/webhook"
```

---

## 📊 Мониторинг

### Проверка ресурсов

```bash
# CPU и память:
top -p $(pgrep -f gunicorn)

# Использование диска:
df -h

# Размер БД:
du -sh ~/bot/db.sqlite3
```

---

## 🆘 Техподдержка Beget

Если нужна помощь:
- **Сайт:** https://beget.com/
- **Поддержка:** support@beget.com
- **Контрол-панель:** https://cp.beget.com/

---

## ✨ Готово!

Ваш Telegram бот теперь работает на Beget VPS с использованием Webhook вместо Polling! 🎉

Бот будет:
- ✅ Автоматически перезагружаться при падении
- ✅ Запускаться при перезагрузке сервера
- ✅ Логировать все события
- ✅ Работать с SSL (безопасно)
