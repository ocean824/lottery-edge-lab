from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import combinations
from math import comb
from typing import Iterable

import pandas as pd

from lottery_edge_lab.cli import candidate_pool_from_history
from lottery_edge_lab.features.engineering import build_feature_snapshot, history_with_lists
from lottery_edge_lab.ingest import load_game_history, sync_game_history
from lottery_edge_lab.optimization.wheel import abbreviated_wheel, diversified_top_tickets
from lottery_edge_lab.registry import GameConfig, get_game
from lottery_edge_lab.scoring.model import rank_candidates


@dataclass
class SyncSummary:
    game_slug: str
    row_count: int
    latest_draw_date: str | None
    source_name: str | None


@dataclass
class JackpotContext:
    game_slug: str
    total_combinations: int
    jackpot_label: str
    odds_text: str
    note: str


@dataclass
class FrequencyRow:
    number: int
    frequency: int
    recent_frequency: int
    last_seen: str | None



def sync_and_summarize(game_slug: str, limit: int | None = None) -> SyncSummary:
    df = sync_game_history(game_slug, limit=limit)
    latest = df.iloc[-1] if not df.empty else None
    return SyncSummary(
        game_slug=game_slug,
        row_count=int(len(df)),
        latest_draw_date=None if latest is None else str(latest.get("draw_date", "")),
        source_name=None if latest is None else str(latest.get("source_name", "")),
    )



def load_or_sync_history(game_slug: str, limit: int | None = None) -> pd.DataFrame:
    try:
        return load_game_history(game_slug)
    except FileNotFoundError:
        return sync_game_history(game_slug, limit=limit)



def smart_pick(game_slug: str, pool_size: int = 12, top: int = 24, ticket_count: int = 6, max_overlap: int = 2) -> pd.DataFrame:
    history = load_or_sync_history(game_slug)
    game = get_game(game_slug)
    pool = candidate_pool_from_history(history, pool_size=max(pool_size, game.main_count + 1))
    candidates = [list(combo) for combo in combinations(sorted(set(pool)), game.main_count)]
    ranked = rank_candidates(candidates, history).head(top)
    if ranked.empty:
        return ranked
    diversified = diversified_top_tickets(ranked, ticket_count=ticket_count, max_overlap=max_overlap)
    return diversified.reset_index(drop=True)



def quick_pick(game_slug: str, ticket_count: int = 5, seed: int | None = None) -> list[str]:
    rng = random.Random(seed)
    game = get_game(game_slug)
    tickets: list[str] = []
    for _ in range(ticket_count):
        main = sorted(rng.sample(range(game.main_min, game.main_max + 1), game.main_count))
        numbers = [str(value) for value in main]
        if game.bonus_count and game.bonus_min is not None and game.bonus_max is not None:
            bonus = [rng.randint(game.bonus_min, game.bonus_max) for _ in range(game.bonus_count)]
            numbers.extend(f"B:{value}" for value in bonus)
        tickets.append(" ".join(numbers))
    return tickets



def wheel_tickets(number_pool: Iterable[int], ticket_size: int, limit: int = 12) -> list[str]:
    return [" ".join(map(str, row)) for row in abbreviated_wheel(list(number_pool), ticket_size=ticket_size, limit=limit)]



def frequency_table(game_slug: str) -> pd.DataFrame:
    history = history_with_lists(load_or_sync_history(game_slug))
    snapshot = build_feature_snapshot(history)
    rows: list[FrequencyRow] = []
    for number in range(get_game(game_slug).main_min, get_game(game_slug).main_max + 1):
        last_seen = None
        matching = history[history["main_numbers_list"].apply(lambda values: number in values)]
        if not matching.empty:
            last_seen = str(matching.iloc[-1]["draw_date"].date())
        rows.append(
            FrequencyRow(
                number=number,
                frequency=int(snapshot["main_frequency"].get(number, 0)),
                recent_frequency=int(snapshot["recent_frequency"].get(number, 0)),
                last_seen=last_seen,
            )
        )
    return pd.DataFrame([row.__dict__ for row in rows]).sort_values(["frequency", "recent_frequency", "number"], ascending=[False, False, True])



def latest_results_table(game_slug: str, rows: int = 25) -> pd.DataFrame:
    history = load_or_sync_history(game_slug)
    return history.sort_values("draw_date", ascending=False).head(rows).reset_index(drop=True)



def jackpot_context(game_slug: str) -> JackpotContext:
    game = get_game(game_slug)
    total = comb(game.main_max - game.main_min + 1, game.main_count)
    if game.bonus_count and game.bonus_min is not None and game.bonus_max is not None:
        total *= (game.bonus_max - game.bonus_min + 1) ** game.bonus_count
    odds_text = f"1 in {total:,}"
    label = game.top_prize_label or "Top prize"
    return JackpotContext(
        game_slug=game_slug,
        total_combinations=int(total),
        jackpot_label=label,
        odds_text=odds_text,
        note="This is a rules-based combinatorial estimate of jackpot odds under the configured game structure. Verify official odds and prize rules with the lottery authority.",
    )



def analysis_availability(game_slug: str) -> str:
    game = get_game(game_slug)
    if game.analysis_enabled:
        return "full"
    return "limited"
