from __future__ import annotations

import unittest

from aiogram.types import MessageEntity

from src.bot.html_renderer import render_message_html


class RenderMessageHtmlTests(unittest.TestCase):
    def test_renders_nested_entities(self) -> None:
        text = "Nested text"
        entities = [
            MessageEntity(type="bold", offset=0, length=11),
            MessageEntity(type="italic", offset=7, length=4),
        ]

        result = render_message_html(text, entities)

        self.assertEqual(result, "<b>Nested <i>text</i></b>")

    def test_renders_custom_emoji(self) -> None:
        text = "X🙂Y"
        entities = [
            MessageEntity(
                type="custom_emoji",
                offset=1,
                length=2,
                custom_emoji_id="1234567890",
            )
        ]

        result = render_message_html(text, entities)

        self.assertEqual(
            result,
            'X<tg-emoji emoji-id="1234567890">🙂</tg-emoji>Y',
        )

    def test_renders_pre_language_block(self) -> None:
        text = "print(1)"
        entities = [
            MessageEntity(type="pre", offset=0, length=8, language="python")
        ]

        result = render_message_html(text, entities)

        self.assertEqual(
            result,
            '<pre><code class="language-python">print(1)</code></pre>',
        )

    def test_renders_text_link(self) -> None:
        text = "Look at this"
        entities = [
            MessageEntity(
                type="text_link",
                offset=0,
                length=4,
                url="https://example.com",
            )
        ]

        result = render_message_html(text, entities)

        self.assertEqual(
            result,
            '<a href="https://example.com">Look</a> at this',
        )


if __name__ == "__main__":
    unittest.main()
