from __future__ import annotations

from itertools import combinations

import pandas as pd

from lottery_edge_lab.features.engineering import build_feature_snapshot, candidate_features



def collision_risk_score(candidate: list[int]) -> float:
    ordered = sorted(candidate)
    all_leq_31_penalty = 1.5 if all(number <= 31 for number in ordered) else 0.0
    date_heavy_penalty = sum(1 for number in ordered if number <= 12) * 0.15
    center_bias_penalty = sum(1 for number in ordered if 20 <= number <= 40) * 0.05
    repeated_terminal_penalty = 0.2 if len({number % 10 for number in ordered}) <= 3 else 0.0
    consecutive_penalty = sum(1 for a, b in zip(ordered[:-1], ordered[1:]) if b - a == 1) * 0.1
    return round(all_leq_31_penalty + date_heavy_penalty + center_bias_penalty + repeated_terminal_penalty + consecutive_penalty, 4)



def historical_pattern_score(candidate: list[int], snapshot: dict) -> float:
    features = candidate_features(candidate)
    main_frequency = snapshot["main_frequency"]
    pair_frequency = snapshot["pair_frequency"]
    recent_frequency = snapshot["recent_frequency"]
    draw_count = max(snapshot["draw_count"], 1)

    freq_score = sum(main_frequency.get(number, 0) / draw_count for number in candidate)
    pair_score = sum(pair_frequency.get(tuple(sorted(pair)), 0) / draw_count for pair in combinations(candidate, 2))
    recency_penalty = sum(recent_frequency.get(number, 0) / 10 for number in candidate) * 0.15
    structure_bonus = 0.0

    if 2 <= features["odd_count"] <= 3:
        structure_bonus += 0.4
    if features["consecutive_pairs"] <= 1:
        structure_bonus += 0.1
    if 100 <= features["sum"] <= 220:
        structure_bonus += 0.3
    if features["range"] >= 25:
        structure_bonus += 0.2

    return round(freq_score + pair_score + structure_bonus - recency_penalty, 6)



def rank_candidates(candidates: list[list[int]], history_df: pd.DataFrame) -> pd.DataFrame:
    snapshot = build_feature_snapshot(history_df)
    ranked_rows = []
    for candidate in candidates:
        ordered = sorted(candidate)
        pattern_score = historical_pattern_score(ordered, snapshot)
        collision_score = collision_risk_score(ordered)
        composite_score = round(pattern_score - collision_score, 6)
        ranked_rows.append(
            {
                "numbers": " ".join(map(str, ordered)),
                "pattern_score": pattern_score,
                "collision_score": collision_score,
                "composite_score": composite_score,
            }
        )
    ranked = pd.DataFrame(ranked_rows)
    return ranked.sort_values(["composite_score", "pattern_score"], ascending=False).reset_index(drop=True)
