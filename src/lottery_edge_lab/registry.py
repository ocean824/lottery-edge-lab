from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GameConfig:
    game_slug: str
    game_name: str
    country: str
    jurisdiction: str
    state_code: str
    state_name: str
    main_count: int
    main_min: int
    main_max: int
    bonus_count: int
    bonus_min: int | None = None
    bonus_max: int | None = None
    multiplier_name: str | None = None
    draw_schedule: str | None = None
    top_prize_label: str | None = None
    analysis_enabled: bool = True
    source_key: str = "manual_import"


GAME_REGISTRY: Dict[str, GameConfig] = {
    "powerball": GameConfig(
        game_slug="powerball",
        game_name="Powerball",
        country="US",
        jurisdiction="national",
        state_code="US",
        state_name="National",
        main_count=5,
        main_min=1,
        main_max=69,
        bonus_count=1,
        bonus_min=1,
        bonus_max=26,
        multiplier_name="power_play",
        draw_schedule="Monday, Wednesday, Saturday",
        top_prize_label="Jackpot",
        analysis_enabled=True,
        source_key="powerball",
    ),
    "megamillions": GameConfig(
        game_slug="megamillions",
        game_name="Mega Millions",
        country="US",
        jurisdiction="national",
        state_code="US",
        state_name="National",
        main_count=5,
        main_min=1,
        main_max=70,
        bonus_count=1,
        bonus_min=1,
        bonus_max=25,
        multiplier_name="megaplier",
        draw_schedule="Tuesday, Friday",
        top_prize_label="Jackpot",
        analysis_enabled=True,
        source_key="megamillions",
    ),
    "ny_lotto": GameConfig(
        game_slug="ny_lotto",
        game_name="New York Lotto",
        country="US",
        jurisdiction="state",
        state_code="NY",
        state_name="New York",
        main_count=6,
        main_min=1,
        main_max=59,
        bonus_count=1,
        bonus_min=1,
        bonus_max=59,
        draw_schedule="Wednesday, Saturday",
        top_prize_label="Jackpot",
        analysis_enabled=True,
        source_key="manual_import",
    ),
    "cash4life": GameConfig(
        game_slug="cash4life",
        game_name="Cash4Life",
        country="US",
        jurisdiction="regional",
        state_code="US",
        state_name="Multi-State",
        main_count=5,
        main_min=1,
        main_max=60,
        bonus_count=1,
        bonus_min=1,
        bonus_max=4,
        draw_schedule="Daily",
        top_prize_label="$1,000 a day for life",
        analysis_enabled=True,
        source_key="manual_import",
    ),
    "take5_midday": GameConfig(
        game_slug="take5_midday",
        game_name="Take 5 Midday",
        country="US",
        jurisdiction="state",
        state_code="NY",
        state_name="New York",
        main_count=5,
        main_min=1,
        main_max=39,
        bonus_count=0,
        draw_schedule="Daily",
        top_prize_label="Pari-mutuel",
        analysis_enabled=True,
        source_key="manual_import",
    ),
    "take5_evening": GameConfig(
        game_slug="take5_evening",
        game_name="Take 5 Evening",
        country="US",
        jurisdiction="state",
        state_code="NY",
        state_name="New York",
        main_count=5,
        main_min=1,
        main_max=39,
        bonus_count=0,
        draw_schedule="Daily",
        top_prize_label="Pari-mutuel",
        analysis_enabled=True,
        source_key="manual_import",
    ),
    "pick10": GameConfig(
        game_slug="pick10",
        game_name="Pick 10",
        country="US",
        jurisdiction="state",
        state_code="NY",
        state_name="New York",
        main_count=20,
        main_min=1,
        main_max=80,
        bonus_count=0,
        draw_schedule="Daily",
        top_prize_label="Fixed prize",
        analysis_enabled=False,
        source_key="manual_import",
    ),
    "numbers3_midday": GameConfig(
        game_slug="numbers3_midday",
        game_name="Numbers 3 Midday",
        country="US",
        jurisdiction="state",
        state_code="NY",
        state_name="New York",
        main_count=3,
        main_min=0,
        main_max=9,
        bonus_count=0,
        draw_schedule="Daily",
        top_prize_label="Fixed prize",
        analysis_enabled=True,
        source_key="manual_import",
    ),
    "numbers3_evening": GameConfig(
        game_slug="numbers3_evening",
        game_name="Numbers 3 Evening",
        country="US",
        jurisdiction="state",
        state_code="NY",
        state_name="New York",
        main_count=3,
        main_min=0,
        main_max=9,
        bonus_count=0,
        draw_schedule="Daily",
        top_prize_label="Fixed prize",
        analysis_enabled=True,
        source_key="manual_import",
    ),
}


def get_game(game_slug: str) -> GameConfig:
    try:
        return GAME_REGISTRY[game_slug]
    except KeyError as exc:
        supported = ", ".join(sorted(GAME_REGISTRY))
        raise ValueError(f"Unsupported game '{game_slug}'. Supported games: {supported}") from exc



def list_games() -> List[GameConfig]:
    return list(GAME_REGISTRY.values())



def list_games_by_state() -> Dict[str, List[GameConfig]]:
    buckets: Dict[str, List[GameConfig]] = {}
    for game in sorted(GAME_REGISTRY.values(), key=lambda item: (item.state_name, item.game_name)):
        buckets.setdefault(game.state_name, []).append(game)
    return buckets



def supported_game_slugs(analysis_only: bool = False) -> List[str]:
    games = GAME_REGISTRY.values()
    if analysis_only:
        games = [game for game in games if game.analysis_enabled]
    return [game.game_slug for game in games]
