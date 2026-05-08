# meowned podruchny

Telegram-бот в Docker для утилит "meowned подручный".

Пока реализована одна функция:
- принимает сообщение с `custom_emoji`;
- возвращает `custom_emoji_id` для каждого кастомного эмоджи;
- возвращает HTML-разметку;
- если вместе с эмоджи есть текст, показывает итоговую HTML-строку и превью.

## Запуск

```bash
docker compose up --build -d
```

## ENV

```env
BOT_TOKEN=...
ADMIN_IDS=1081950251
```

`ADMIN_IDS` задается через запятую.
