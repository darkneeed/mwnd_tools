from __future__ import annotations

from html import escape

from aiogram.types import Message, MessageEntity


def _utf16_to_py_index(text: str, utf16_offset: int) -> int:
    consumed = 0
    for index, char in enumerate(text):
        if consumed >= utf16_offset:
            return index
        consumed += len(char.encode("utf-16-le")) // 2
    return len(text)


def _slice_by_entity(text: str, entity: MessageEntity) -> tuple[int, int]:
    start = _utf16_to_py_index(text, entity.offset)
    end = _utf16_to_py_index(text, entity.offset + entity.length)
    return start, end


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


def render_custom_emoji_html(text: str, entities: list[MessageEntity]) -> str:
    custom_entities = find_custom_emoji_entities(entities)
    if not custom_entities:
        return escape(text)

    parts: list[str] = []
    last_py_index = 0

    for entity in custom_entities:
        start, end = _slice_by_entity(text, entity)
        parts.append(escape(text[last_py_index:start]))

        emoji_text = text[start:end] or "?"
        emoji_id = escape(entity.custom_emoji_id, quote=True)
        parts.append(f'<tg-emoji emoji-id="{emoji_id}">{escape(emoji_text)}</tg-emoji>')
        last_py_index = end

    parts.append(escape(text[last_py_index:]))
    return "".join(parts)
