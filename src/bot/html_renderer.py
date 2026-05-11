from __future__ import annotations

from html import escape

from aiogram.types import Message, MessageEntity
from aiogram.utils.text_decorations import html_decoration


def extract_message_payload(message: Message) -> tuple[str, list[MessageEntity]]:
    if message.text is not None:
        return message.text, list(message.entities or [])
    if message.caption is not None:
        return message.caption, list(message.caption_entities or [])
    return "", []


def find_custom_emoji_entities(entities: list[MessageEntity]) -> list[MessageEntity]:
    return [
        entity
        for entity in sorted(entities, key=lambda item: item.offset)
        if entity.type == "custom_emoji" and entity.custom_emoji_id
    ]


def render_message_html(text: str, entities: list[MessageEntity]) -> str:
    if not entities:
        return escape(text)

    return html_decoration.unparse(text, entities)


def render_custom_emoji_html(text: str, entities: list[MessageEntity]) -> str:
    return render_message_html(text, entities)
