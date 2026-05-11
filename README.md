# meowned podruchny

Telegram-бот в Docker для утилит "meowned подручный".

Пока реализована одна функция:
- принимает текст или подпись с Telegram-разметкой;
- конвертирует Telegram entities в HTML-разметку;
- поддерживает `custom_emoji` / premium emoji через тег `<tg-emoji>`;
- возвращает `custom_emoji_id` для каждого кастомного эмоджи;
- показывает итоговую HTML-строку и превью.

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
