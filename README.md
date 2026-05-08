# meowned подручный

Telegram-бот в Docker для утилит "meowned подручный".

Пока реализована одна функция:
- принимает сообщение с `custom_emoji`;
- возвращает `custom_emoji_id` для каждого кастомного эмоджи;
- возвращает HTML-разметку;
- если вместе с эмоджи есть текст, показывает итоговую HTML-строку и превью.

## Запуск

```bash
cd /opt/ | git clone https://github.com/darkneeed/mwnd_tools.git
cd mwnd_tools
cp .env.example .env && nano .env
docker compose up --build -d
```

## ENV

```env
BOT_TOKEN=...
ADMIN_IDS=...
```

`ADMIN_IDS` задаются через запятую.
