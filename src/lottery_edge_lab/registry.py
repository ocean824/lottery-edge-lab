from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class GameConfig:
    game_slug: str
    game_name: str
    country: str
    jurisdiction: str
    main_count: int
    main_min: int
    main_max: int
    bonus_count: int
    bonus_min: int | None = None
    bonus_max: int | None = None
    multiplier_name: str | None = None


GAME_REGISTRY: Dict[str, GameConfig] = {
    "powerball": GameConfig(
        game_slug="powerball",
        game_name="Powerball",
        country="US",
        jurisdiction="national",
        main_count=5,
        main_min=1,
        main_max=69,
        bonus_count=1,
        bonus_min=1,
        bonus_max=26,
        multiplier_name="power_play",
    ),
    "megamillions": GameConfig(
        game_slug="megamillions",
        game_name="Mega Millions",
        country="US",
        jurisdiction="national",
        main_count=5,
        main_min=1,
        main_max=70,
        bonus_count=1,
        bonus_min=1,
        bonus_max=25,
        multiplier_name="megaplier",
    ),
}


def get_game(game_slug: str) -> GameConfig:
    try:
        return GAME_REGISTRY[game_slug]
    except KeyError as exc:
        supported = ", ".join(sorted(GAME_REGISTRY))
        raise ValueError(f"Unsupported game '{game_slug}'. Supported games: {supported}") from exc
