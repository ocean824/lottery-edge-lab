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



def arithmetic_complexity(candidate: list[int]) -> int:
    ordered = sorted(candidate)
    diffs = {abs(b - a) for a, b in combinations(ordered, 2) if b != a}
    expected_minimum = max(len(ordered) - 1, 1)
    return max(len(diffs) - expected_minimum, 0)



def candidate_features(candidate: list[int]) -> dict:
    ordered = sorted(candidate)
    odd_count = sum(1 for value in ordered if value % 2 == 1)
    number_midpoint = (ordered[0] + ordered[-1]) / 2 if ordered else 0
    low_count = sum(1 for value in ordered if value <= number_midpoint)
    gaps = [b - a for a, b in zip(ordered[:-1], ordered[1:])]
    terminal_diversity = len({value % 10 for value in ordered})
    return {
        "sum": sum(ordered),
        "range": ordered[-1] - ordered[0],
        "odd_count": odd_count,
        "even_count": len(ordered) - odd_count,
        "low_count": low_count,
        "high_count": len(ordered) - low_count,
        "consecutive_pairs": sum(1 for gap in gaps if gap == 1),
        "gap_variance_proxy": sum(abs(gap - (sum(gaps) / len(gaps))) for gap in gaps) if gaps else 0,
        "ac_value": arithmetic_complexity(ordered),
        "mean": round(sum(ordered) / len(ordered), 4) if ordered else 0.0,
        "terminal_diversity": terminal_diversity,
    }



def rolling_hit_series(history: pd.DataFrame, number: int, window: int = 10) -> list[float]:
    hits = [1.0 if number in values else 0.0 for values in history["main_numbers_list"]]
    if not hits:
        return []
    series = pd.Series(hits)
    return series.rolling(window=min(window, len(series)), min_periods=1).mean().tolist()



def linear_slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    x = list(range(len(values)))
    x_mean = sum(x) / len(x)
    y_mean = sum(values) / len(values)
    numerator = sum((x_i - x_mean) * (y_i - y_mean) for x_i, y_i in zip(x, values))
    denominator = sum((x_i - x_mean) ** 2 for x_i in x)
    if denominator == 0:
        return 0.0
    return numerator / denominator



def ewma_hits(history: pd.DataFrame, number: int, span: int = 8) -> float:
    hits = [1.0 if number in values else 0.0 for values in history["main_numbers_list"]]
    if not hits:
        return 0.0
    return float(pd.Series(hits).ewm(span=min(span, max(2, len(hits))), adjust=False).mean().iloc[-1])



def draws_since_last_hit(history: pd.DataFrame, number: int) -> int | None:
    reverse_lists = list(reversed(history["main_numbers_list"].tolist()))
    for offset, values in enumerate(reverse_lists):
        if number in values:
            return offset
    return None



def positional_tendency_score(history: pd.DataFrame, number: int) -> float:
    if history.empty:
        return 0.0
    positions: list[int] = []
    for values in history["main_numbers_list"]:
        ordered = sorted(values)
        if number in ordered:
            positions.append(ordered.index(number) + 1)
    if not positions:
        return 0.0
    average_position = sum(positions) / len(positions)
    return round(1.0 / average_position, 6)



def normalize_series(series: pd.Series, reverse: bool = False) -> pd.Series:
    if series.empty:
        return series
    numeric = series.astype(float)
    if numeric.nunique(dropna=False) <= 1:
        return pd.Series([0.0] * len(numeric), index=numeric.index)
    scaled = (numeric - numeric.min()) / (numeric.max() - numeric.min())
    return 1.0 - scaled if reverse else scaled



def build_number_score_table(df: pd.DataFrame, number_min: int, number_max: int, recent_window: int = 12) -> pd.DataFrame:
    history = history_with_lists(df)
    main_counter = Counter()
    pair_counter = Counter()
    for values in history["main_numbers_list"]:
        main_counter.update(values)
        pair_counter.update(tuple(sorted(pair)) for pair in combinations(values, 2))

    draw_count = max(len(history), 1)
    recent_history = history.tail(min(recent_window, len(history))) if not history.empty else history
    recent_counter = Counter()
    for values in recent_history["main_numbers_list"]:
        recent_counter.update(values)

    rows: list[dict[str, float | int | str]] = []
    for number in range(number_min, number_max + 1):
        total_frequency = int(main_counter.get(number, 0))
        recent_frequency = int(recent_counter.get(number, 0))
        since_hit = draws_since_last_hit(history, number)
        rolling_series = rolling_hit_series(history, number)
        slope = linear_slope(rolling_series)
        momentum = ewma_hits(history, number)
        pair_strength = 0.0
        if total_frequency:
            linked_pairs = [count for pair, count in pair_counter.items() if number in pair]
            pair_strength = sum(linked_pairs) / max(len(linked_pairs), 1)
        crowd_penalty = 0.0
        if number <= 12:
            crowd_penalty += 0.35
        if number <= 31:
            crowd_penalty += 0.15
        if number % 10 in {0, 5}:
            crowd_penalty += 0.05
        rows.append(
            {
                "number": number,
                "frequency": total_frequency,
                "frequency_rate": total_frequency / draw_count,
                "recent_frequency": recent_frequency,
                "recent_rate": recent_frequency / max(len(recent_history), 1) if len(recent_history) else 0.0,
                "draws_since_hit": draw_count if since_hit is None else since_hit,
                "trend_slope": slope,
                "momentum": momentum,
                "pair_strength": pair_strength,
                "position_score": positional_tendency_score(history, number),
                "crowd_penalty": crowd_penalty,
            }
        )

    score_df = pd.DataFrame(rows)
    score_df["frequency_score"] = normalize_series(score_df["frequency_rate"])
    score_df["recent_score"] = normalize_series(score_df["recent_rate"])
    score_df["overdue_score"] = normalize_series(score_df["draws_since_hit"])
    score_df["trend_score"] = normalize_series(score_df["trend_slope"])
    score_df["momentum_score"] = normalize_series(score_df["momentum"])
    score_df["pair_score"] = normalize_series(score_df["pair_strength"])
    score_df["position_rank_score"] = normalize_series(score_df["position_score"])
    score_df["crowd_risk_score"] = normalize_series(score_df["crowd_penalty"], reverse=True)

    score_df["weighted_score"] = (
        score_df["frequency_score"] * 0.24
        + score_df["recent_score"] * 0.18
        + score_df["overdue_score"] * 0.10
        + score_df["trend_score"] * 0.14
        + score_df["momentum_score"] * 0.14
        + score_df["pair_score"] * 0.12
        + score_df["position_rank_score"] * 0.03
        + score_df["crowd_risk_score"] * 0.05
    )

    score_df["notes"] = score_df.apply(_build_number_note, axis=1)
    return score_df.sort_values(["weighted_score", "frequency", "recent_frequency", "number"], ascending=[False, False, False, True]).reset_index(drop=True)



def _build_number_note(row: pd.Series) -> str:
    notes: list[str] = []
    if row["frequency_score"] >= 0.75:
        notes.append("high long-run frequency")
    if row["recent_score"] >= 0.75:
        notes.append("running hot recently")
    if row["trend_score"] >= 0.75:
        notes.append("positive trend")
    if row["momentum_score"] >= 0.75:
        notes.append("strong momentum")
    if row["overdue_score"] >= 0.75:
        notes.append("long gap since last hit")
    if row["crowd_risk_score"] >= 0.75 and row["crowd_penalty"] <= 0.1:
        notes.append("lower crowding risk")
    if not notes:
        notes.append("mixed signal profile")
    return ", ".join(notes)



def build_feature_snapshot(df: pd.DataFrame, number_min: int | None = None, number_max: int | None = None) -> dict:
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

    number_score_df = pd.DataFrame()
    if number_min is not None and number_max is not None:
        number_score_df = build_number_score_table(history, number_min=number_min, number_max=number_max)

    return {
        "draw_count": len(history),
        "main_frequency": main_counter,
        "pair_frequency": pair_counter,
        "recent_frequency": recent_counter,
        "latest_draw": history.iloc[-1]["main_numbers_list"] if not history.empty else [],
        "recent_draws": history.tail(10)["main_numbers_list"].tolist() if not history.empty else [],
        "history": history,
        "number_scores": number_score_df,
    }
