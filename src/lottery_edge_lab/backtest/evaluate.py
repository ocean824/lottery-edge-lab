from __future__ import annotations

from itertools import combinations

import pandas as pd

from lottery_edge_lab.features.engineering import history_with_lists
from lottery_edge_lab.scoring.model import rank_candidates



def generate_candidates_from_pool(number_pool: list[int], ticket_size: int = 5, cap: int = 500) -> list[list[int]]:
    combos = [list(combo) for combo in combinations(sorted(set(number_pool)), ticket_size)]
    return combos[:cap]



def rolling_backtest(history_df: pd.DataFrame, candidate_pool: list[int], top_n: int = 10, train_window: int = 30) -> pd.DataFrame:
    history = history_with_lists(history_df)
    if len(history) <= train_window:
        raise ValueError("Not enough history for rolling backtest.")

    candidates = generate_candidates_from_pool(candidate_pool)
    rows = []
    for idx in range(train_window, len(history)):
        train_df = history.iloc[:idx].copy()
        actual = set(history.iloc[idx]["main_numbers_list"])
        ranked = rank_candidates(candidates, train_df)
        top = ranked.head(top_n).copy()
        best_match = 0
        top_hit = False
        for candidate_text in top["numbers"]:
            candidate_set = {int(value) for value in candidate_text.split()}
            overlap = len(candidate_set & actual)
            if overlap > best_match:
                best_match = overlap
            if overlap >= 3:
                top_hit = True
        rows.append(
            {
                "draw_date": history.iloc[idx]["draw_date"].date().isoformat(),
                "best_overlap_top_n": best_match,
                "any_top_n_hit_3plus": top_hit,
            }
        )
    return pd.DataFrame(rows)
