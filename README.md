# meowned подручный

Telegram-бот в Docker для различных утилит

Пока реализована одна функция:
- показывает меню с кнопкой `Авторазметка`;
- по кнопке принимает текст или подпись с Telegram-разметкой;
- конвертирует Telegram entities в HTML-разметку;
- поддерживает `custom_emoji` / premium emoji через тег `<tg-emoji>`;
- возвращает `custom_emoji_id` для каждого кастомного эмоджи;
- показывает итоговую HTML-строку и превью.

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
