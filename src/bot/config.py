from __future__ import annotations

import os
from dataclasses import dataclass


def _parse_admin_ids(raw_value: str) -> tuple[int, ...]:
    parts = [part.strip() for part in raw_value.replace(";", ",").split(",")]
    return tuple(int(part) for part in parts if part)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: tuple[int, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        if not bot_token:
            raise RuntimeError("BOT_TOKEN is required")

        admin_ids = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
        return cls(bot_token=bot_token, admin_ids=admin_ids)
