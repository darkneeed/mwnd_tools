from __future__ import annotations

import asyncio
from html import escape
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

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
AUTO_MARKUP_BUTTON = "Авторазметка"
CANCEL_BUTTON = "Назад в меню"


class MenuState(StatesGroup):
    awaiting_auto_markup = State()


def is_allowed(user_id: int) -> bool:
    return not settings.admin_ids or user_id in settings.admin_ids


def build_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=AUTO_MARKUP_BUTTON)],
        ],
        resize_keyboard=True,
    )


def build_auto_markup_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=AUTO_MARKUP_BUTTON)],
            [KeyboardButton(text=CANCEL_BUTTON)],
        ],
        resize_keyboard=True,
    )


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
async def handle_start(message: Message, state: FSMContext) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    await state.clear()
    await message.answer(
        "Выбери действие в меню.",
        reply_markup=build_main_menu(),
    )


@dispatcher.message(Command("help"))
async def handle_help(message: Message, state: FSMContext) -> None:
    await handle_start(message, state)


@dispatcher.message(F.text == AUTO_MARKUP_BUTTON)
async def handle_auto_markup_entry(message: Message, state: FSMContext) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    await state.set_state(MenuState.awaiting_auto_markup)
    await message.answer(
        "Пришли текст или подпись с Telegram-разметкой. "
        "Я верну HTML-представление, а для premium emoji еще и "
        "<code>custom_emoji_id</code>.",
        reply_markup=build_auto_markup_menu(),
    )


@dispatcher.message(F.text == CANCEL_BUTTON)
async def handle_cancel(message: Message, state: FSMContext) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    await state.clear()
    await message.answer(
        "Меню открыто.",
        reply_markup=build_main_menu(),
    )


@dispatcher.message(MenuState.awaiting_auto_markup, F.text | F.caption)
async def handle_auto_markup_message(message: Message) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    text, _ = extract_message_payload(message)
    if not text.strip():
        await message.answer("Сообщение пустое.")
        return

    await message.answer(build_response(message))


@dispatcher.message()
async def handle_fallback(message: Message, state: FSMContext) -> None:
    if not message.from_user or not is_allowed(message.from_user.id):
        await message.answer("Доступ закрыт.")
        return

    current_state = await state.get_state()
    if current_state == MenuState.awaiting_auto_markup.state:
        await message.answer(
            "Пришли текст или подпись с Telegram-разметкой, либо нажми "
            f"<code>{CANCEL_BUTTON}</code>.",
            reply_markup=build_auto_markup_menu(),
        )
        return

    await message.answer(
        "Выбери действие в меню.",
        reply_markup=build_main_menu(),
    )


async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    logger.info("Starting bot")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
