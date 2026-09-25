# ispa_host bot

Deploy-ready Telegram-бот на aiogram 3.

## Быстрый запуск

```bash
./deploy.sh
```

Или:

```bash
docker compose up -d --build
```

## Логи

```bash
docker compose logs -f bot
```

## Автоудаление сообщений

Все сообщения, которые бот отправляет через `send_message_with_auto_delete`, записываются в таблицу `bot_messages` и удаляются через `BOT_MESSAGE_TTL_SECONDS=86399`, то есть через 23 часа 59 минут 59 секунд.

Удаляются именно сообщения бота. Пользовательские сообщения бот не трогает.
