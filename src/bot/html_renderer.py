from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass
class EntityNode:
    entity: MessageEntity | None
    start: int
    end: int
    children: list["EntityNode"] = field(default_factory=list)


def _normalize_entities(text: str, entities: list[MessageEntity]) -> list[EntityNode]:
    nodes: list[EntityNode] = []

    for entity in entities:
        start, end = _slice_by_entity(text, entity)
        if start >= end:
            continue
        nodes.append(EntityNode(entity=entity, start=start, end=end))

    return sorted(nodes, key=lambda item: (item.start, -item.end))


def _build_entity_tree(text: str, entities: list[MessageEntity]) -> EntityNode:
    root = EntityNode(entity=None, start=0, end=len(text))
    stack = [root]

    for node in _normalize_entities(text, entities):
        while len(stack) > 1 and not (
            stack[-1].start <= node.start and node.end <= stack[-1].end
        ):
            stack.pop()

        stack[-1].children.append(node)
        stack.append(node)

    return root


def _wrap_entity_html(entity: MessageEntity, content: str, raw_text: str) -> str:
    if entity.type == "bold":
        return f"<b>{content}</b>"
    if entity.type == "italic":
        return f"<i>{content}</i>"
    if entity.type == "underline":
        return f"<u>{content}</u>"
    if entity.type == "strikethrough":
        return f"<s>{content}</s>"
    if entity.type == "spoiler":
        return f"<tg-spoiler>{content}</tg-spoiler>"
    if entity.type == "code":
        return f"<code>{content}</code>"
    if entity.type == "pre":
        language = escape(entity.language, quote=True) if entity.language else ""
        if language:
            return f'<pre><code class="language-{language}">{content}</code></pre>'
        return f"<pre>{content}</pre>"
    if entity.type == "text_link" and entity.url:
        href = escape(entity.url, quote=True)
        return f'<a href="{href}">{content}</a>'
    if entity.type == "text_mention" and entity.user:
        href = f"tg://user?id={entity.user.id}"
        return f'<a href="{href}">{content}</a>'
    if entity.type == "url":
        href = escape(raw_text, quote=True)
        return f'<a href="{href}">{content}</a>'
    if entity.type == "mention":
        username = raw_text[1:]
        href = escape(f"https://t.me/{username}", quote=True)
        return f'<a href="{href}">{content}</a>'
    if entity.type == "email":
        href = escape(f"mailto:{raw_text}", quote=True)
        return f'<a href="{href}">{content}</a>'
    if entity.type == "phone_number":
        href = escape(f"tel:{raw_text}", quote=True)
        return f'<a href="{href}">{content}</a>'
    if entity.type == "blockquote":
        return f"<blockquote>{content}</blockquote>"
    if entity.type == "expandable_blockquote":
        return f"<blockquote expandable>{content}</blockquote>"
    if entity.type == "custom_emoji" and entity.custom_emoji_id:
        emoji_id = escape(entity.custom_emoji_id, quote=True)
        emoji_text = content or escape(raw_text) or "?"
        return f'<tg-emoji emoji-id="{emoji_id}">{emoji_text}</tg-emoji>'

    return content


def _render_node(text: str, node: EntityNode) -> str:
    parts: list[str] = []
    cursor = node.start

    for child in sorted(node.children, key=lambda item: (item.start, item.end)):
        parts.append(escape(text[cursor:child.start]))
        child_content = _render_node(text, child)
        raw_text = text[child.start:child.end]
        parts.append(_wrap_entity_html(child.entity, child_content, raw_text))
        cursor = child.end

    parts.append(escape(text[cursor:node.end]))
    return "".join(parts)


def render_message_html(text: str, entities: list[MessageEntity]) -> str:
    if not entities:
        return escape(text)

    root = _build_entity_tree(text, entities)
    return _render_node(text, root)


def render_custom_emoji_html(text: str, entities: list[MessageEntity]) -> str:
    return render_message_html(text, entities)
