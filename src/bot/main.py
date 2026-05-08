from __future__ import annotations

import asyncio
from html import escape
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from .config import Settings
from .html_renderer import (
    extract_message_payload,
    find_custom_emoji_entities,
    render_custom_emoji_html,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


settings = Settings.from_env()
dispatcher = Dispatcher()


def is_allowed(user_id: int) -> bool:
    return not settings.admin_ids or user_id in settings.admin_ids


def build_response(message: Message) -> str:
    text, entities = extract_message_payload(message)
    custom_entities = find_custom_emoji_entities(entities)
    rendered_html = render_custom_emoji_html(text, entities)

    emoji_lines = []
    for index, entity in enumerate(custom_entities, start=1):
        emoji_lines.append(
            f'{index}. <code>{escape(entity.custom_emoji_id)}</code>'
        )

    emoji_section = "\n".join(emoji_lines)
    raw_markup = escape(rendered_html)

    return (
        f"<b>Custom emoji ID</b>\n{emoji_section}\n\n"
        f"<b>HTML</b>\n<pre>{raw_markup}</pre>\n\n"
        f"<b>Preview</b>\n{rendered_html}"
    )


@dispatcher.message(Command("start"))
async def handle_start(message: Message) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    await message.answer(
        "Пришли сообщение с кастомным эмоджи. "
        "Бот вернет <code>custom_emoji_id</code> и HTML-разметку.",
    )


@dispatcher.message(Command("help"))
async def handle_help(message: Message) -> None:
    await handle_start(message)


@dispatcher.message(F.text | F.caption)
async def handle_message(message: Message) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    text, entities = extract_message_payload(message)
    custom_entities = find_custom_emoji_entities(entities)

    if not custom_entities:
        await message.answer(
            "Не вижу кастомных эмоджи. Пришли текст или подпись, где они есть."
        )
        return

    if not text.strip():
        await message.answer("Сообщение пустое.")
        return

    await message.answer(build_response(message))


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    logger.info("Starting bot")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
