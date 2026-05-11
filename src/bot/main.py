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
    render_message_html,
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
    rendered_html = render_message_html(text, entities)

    emoji_lines = []
    for index, entity in enumerate(custom_entities, start=1):
        emoji_lines.append(
            f'{index}. <code>{escape(entity.custom_emoji_id)}</code>'
        )

    emoji_section = ""
    if emoji_lines:
        emoji_body = "\n".join(emoji_lines)
        emoji_section = (
            f"<b>Custom emoji ID</b>\n{emoji_body}\n\n"
        )

    raw_markup = escape(rendered_html)

    return (
        f"{emoji_section}"
        f"<b>HTML</b>\n<pre>{raw_markup}</pre>\n\n"
        f"<b>Preview</b>\n{rendered_html}"
    )


@dispatcher.message(Command("start"))
async def handle_start(message: Message) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    await message.answer(
        "Пришли текст или подпись с Telegram-разметкой. "
        "Бот вернет HTML-представление, а для premium emoji еще и "
        "<code>custom_emoji_id</code>.",
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
