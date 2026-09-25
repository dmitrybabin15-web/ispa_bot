#!/bin/bash

# Скрипт для деплоя Telegram бота на Beget VPS
# Использование: ./deploy-beget.sh

set -e  # Выход при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# Переменные
BOT_HOME="${BOT_HOME:=$(pwd)}"
VENV_DIR="$BOT_HOME/venv"
LOGS_DIR="$BOT_HOME/logs"
SYSTEMD_SERVICE="telegram-bot"
SERVICE_FILE="/etc/systemd/system/${SYSTEMD_SERVICE}.service"

echo -e "${YELLOW}Telegram Bot Deployment on Beget VPS${NC}"
echo "======================================="
echo "Bot directory: $BOT_HOME"
echo "Venv directory: $VENV_DIR"

# Шаг 1: Проверка зависимостей
echo -e "\n${YELLOW}[1/7] Проверка зависимостей...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 не найден. Установите Python3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python версия: $PYTHON_VERSION"

# Шаг 2: Создание виртуального окружения
echo -e "\n${YELLOW}[2/7] Создание виртуального окружения...${NC}"
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo -e "${YELLOW}Найдено повреждённое venv (нет bin/activate). Пересоздаю...${NC}"
    rm -rf "$VENV_DIR"
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}Виртуальное окружение создано${NC}"
else
    echo -e "${GREEN}Виртуальное окружение уже существует${NC}"
fi

# Активируем venv
source "$VENV_DIR/bin/activate"

# Шаг 3: Установка зависимостей
echo -e "\n${YELLOW}[3/7] Установка зависимостей Python...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r "$BOT_HOME/requirements.txt"
echo -e "${GREEN}Зависимости установлены${NC}"

# Шаг 4: Создание директории логов
echo -e "\n${YELLOW}[4/7] Создание директории логов...${NC}"
mkdir -p "$LOGS_DIR"
touch "$LOGS_DIR/access.log" "$LOGS_DIR/error.log" "$LOGS_DIR/stdout.log" "$LOGS_DIR/stderr.log"
echo -e "${GREEN}Директория логов: $LOGS_DIR${NC}"

# Шаг 5: Проверка .env
echo -e "\n${YELLOW}[5/7] Проверка конфигурации .env...${NC}"
if [ ! -f "$BOT_HOME/.env" ]; then
    if [ -f "$BOT_HOME/.env.example" ]; then
        cp "$BOT_HOME/.env.example" "$BOT_HOME/.env"
        echo -e "${YELLOW}Создан .env из .env.example${NC}"
        echo -e "${RED}⚠️  Не забудьте заполнить .env файл!${NC}"
    else
        echo -e "${RED}.env файл не найден${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}.env файл найден${NC}"
fi

# Проверяем BOT_TOKEN
if grep -q "BOT_TOKEN=need_change_xz_maybe" "$BOT_HOME/.env"; then
    echo -e "${RED}❌ BOT_TOKEN не установлен в .env файле!${NC}"
    echo "Отредактируйте: $BOT_HOME/.env"
    exit 1
fi

# Шаг 6: Подготовка systemd service
echo -e "\n${YELLOW}[6/7] Подготовка systemd service...${NC}"

# Получаем текущего пользователя
CURRENT_USER=$(whoami)

# Создаём временный файл service с правильными путями
SERVICE_TEMP=$(mktemp)
sed \
  -e "s|your_beget_user|$CURRENT_USER|g" \
  -e "s|%h/bot|$BOT_HOME|g" \
  -e "s|/home/your_beget_user/bot|$BOT_HOME|g" \
  "$BOT_HOME/telegram-bot.service" > "$SERVICE_TEMP"

# Проверяем, нужны ли права sudo
if [ "$CURRENT_USER" != "root" ]; then
    echo -e "${YELLOW}Для установки systemd service требуются права sudo${NC}"
    echo "Установка системного сервиса..."
    sudo cp "$SERVICE_TEMP" "$SERVICE_FILE"
    sudo chown root:root "$SERVICE_FILE"
    sudo chmod 644 "$SERVICE_FILE"
    sudo systemctl daemon-reload
    echo -e "${GREEN}Systemd service установлен${NC}"
else
    cp "$SERVICE_TEMP" "$SERVICE_FILE"
    chmod 644 "$SERVICE_FILE"
    systemctl daemon-reload
    echo -e "${GREEN}Systemd service установлен${NC}"
fi

rm "$SERVICE_TEMP"

# Шаг 7: Информация о включении сервиса
echo -e "\n${YELLOW}[7/7] Окончательная настройка...${NC}"

echo ""
echo -e "${GREEN}✅ Деплой завершён!${NC}"
echo ""
echo "Следующие шаги:"
echo ""
echo "1️⃣  Отредактируйте .env если нужно:"
echo "    nano $BOT_HOME/.env"
echo ""
echo "2️⃣  Включите и запустите сервис:"
if [ "$CURRENT_USER" != "root" ]; then
    echo "    sudo systemctl enable $SYSTEMD_SERVICE"
    echo "    sudo systemctl start $SYSTEMD_SERVICE"
else
    echo "    systemctl enable $SYSTEMD_SERVICE"
    echo "    systemctl start $SYSTEMD_SERVICE"
fi
echo ""
echo "3️⃣  Проверьте статус:"
if [ "$CURRENT_USER" != "root" ]; then
    echo "    sudo systemctl status $SYSTEMD_SERVICE"
    echo "    sudo journalctl -u $SYSTEMD_SERVICE -f"
else
    echo "    systemctl status $SYSTEMD_SERVICE"
    echo "    journalctl -u $SYSTEMD_SERVICE -f"
fi
echo ""
echo "4️⃣  Установите Telegram webhook:"
echo "    Используйте команду ниже (замените DOMAIN и BOT_TOKEN):"
echo "    curl -X POST https://api.telegram.org/botBOT_TOKEN/setWebhook?url=https://DOMAIN/webhook"
echo ""
echo "5️⃣  Проверьте здоровье приложения:"
echo "    curl https://DOMAIN/health"
echo ""
echo "Логи находятся в: $LOGS_DIR/"
