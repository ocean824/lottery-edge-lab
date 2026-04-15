from __future__ import annotations

from itertools import combinations

import pandas as pd



def diversified_top_tickets(ranked_df: pd.DataFrame, ticket_count: int = 5, max_overlap: int = 2) -> pd.DataFrame:
    selected_rows = []
    selected_sets: list[set[int]] = []
    for row in ranked_df.to_dict(orient="records"):
        numbers = {int(value) for value in str(row["numbers"]).split()}
        if any(len(numbers & existing) > max_overlap for existing in selected_sets):
            continue
        selected_rows.append(row)
        selected_sets.append(numbers)
        if len(selected_rows) >= ticket_count:
            break
    return pd.DataFrame(selected_rows)



def abbreviated_wheel(number_pool: list[int], ticket_size: int = 5, limit: int = 12) -> list[list[int]]:
    pool = sorted(set(int(n) for n in number_pool))
    combos = [list(combo) for combo in combinations(pool, ticket_size)]
    if len(combos) <= limit:
        return combos
    step = max(len(combos) // limit, 1)
    return combos[::step][:limit]
