from __future__ import annotations

from collections import Counter
from itertools import combinations

import pandas as pd

from lottery_edge_lab.utils.parsing import parse_int_list



def history_with_lists(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["main_numbers_list"] = out["main_numbers"].apply(parse_int_list)
    out["bonus_numbers_list"] = out["bonus_numbers"].fillna("").astype(str).apply(
        lambda value: parse_int_list(value) if value.strip() else []
    )
    out["draw_date"] = pd.to_datetime(out["draw_date"])
    return out.sort_values("draw_date").reset_index(drop=True)



def build_feature_snapshot(df: pd.DataFrame) -> dict:
    history = history_with_lists(df)
    main_counter = Counter()
    pair_counter = Counter()
    recent_counter = Counter()

    for idx, row in history.iterrows():
        numbers = row["main_numbers_list"]
        main_counter.update(numbers)
        pair_counter.update(tuple(sorted(pair)) for pair in combinations(numbers, 2))
        if idx >= max(0, len(history) - 10):
            recent_counter.update(numbers)

    return {
        "draw_count": len(history),
        "main_frequency": main_counter,
        "pair_frequency": pair_counter,
        "recent_frequency": recent_counter,
        "latest_draw": history.iloc[-1]["main_numbers_list"] if not history.empty else [],
    }



def candidate_features(candidate: list[int]) -> dict:
    ordered = sorted(candidate)
    odd_count = sum(1 for value in ordered if value % 2 == 1)
    low_count = sum(1 for value in ordered if value <= (max(ordered) / 2))
    gaps = [b - a for a, b in zip(ordered[:-1], ordered[1:])]
    return {
        "sum": sum(ordered),
        "range": ordered[-1] - ordered[0],
        "odd_count": odd_count,
        "even_count": len(ordered) - odd_count,
        "low_count": low_count,
        "high_count": len(ordered) - low_count,
        "consecutive_pairs": sum(1 for gap in gaps if gap == 1),
        "gap_variance_proxy": sum(abs(gap - (sum(gaps) / len(gaps))) for gap in gaps) if gaps else 0,
    }
