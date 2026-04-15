from __future__ import annotations

from pathlib import Path

import pandas as pd

from lottery_edge_lab.config import NORMALIZED_ROOT
from lottery_edge_lab.data_sources.official import fetch_game_history


REQUIRED_COLUMNS = [
    "country",
    "jurisdiction",
    "game_name",
    "game_slug",
    "draw_date",
    "main_numbers",
    "bonus_numbers",
    "multiplier",
    "source_name",
    "source_url",
    "ingested_at",
]


def normalized_path(game_slug: str) -> Path:
    return NORMALIZED_ROOT / f"{game_slug}_history.csv"



def sync_game_history(game_slug: str, limit: int | None = None) -> pd.DataFrame:
    df = fetch_game_history(game_slug, limit=limit)
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[REQUIRED_COLUMNS].copy()
    df.to_csv(normalized_path(game_slug), index=False)
    return df



def load_game_history(game_slug: str) -> pd.DataFrame:
    path = normalized_path(game_slug)
    if not path.exists():
        raise FileNotFoundError(
            f"Normalized dataset not found for '{game_slug}'. Run sync first to create {path}."
        )
    df = pd.read_csv(path)
    return df.sort_values("draw_date").reset_index(drop=True)
