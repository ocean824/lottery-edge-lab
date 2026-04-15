from lottery_edge_lab.features.engineering import build_feature_snapshot
from lottery_edge_lab.optimization.wheel import abbreviated_wheel
from lottery_edge_lab.scoring.model import collision_risk_score, rank_candidates
import pandas as pd


def sample_history() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "country": "US",
                "jurisdiction": "test",
                "game_name": "Powerball",
                "game_slug": "powerball",
                "draw_date": "2026-01-01",
                "main_numbers": "1 5 12 23 40",
                "bonus_numbers": "10",
                "multiplier": "2",
                "source_name": "test",
                "source_url": "https://example.com",
                "ingested_at": "2026-01-01T00:00:00Z",
            },
            {
                "country": "US",
                "jurisdiction": "test",
                "game_name": "Powerball",
                "game_slug": "powerball",
                "draw_date": "2026-01-03",
                "main_numbers": "3 8 12 25 41",
                "bonus_numbers": "11",
                "multiplier": "2",
                "source_name": "test",
                "source_url": "https://example.com",
                "ingested_at": "2026-01-03T00:00:00Z",
            },
        ]
    )



def test_feature_snapshot_counts_draws() -> None:
    snapshot = build_feature_snapshot(sample_history())
    assert snapshot["draw_count"] == 2
    assert snapshot["main_frequency"][12] == 2



def test_collision_risk_penalizes_date_heavy_lines() -> None:
    risky = collision_risk_score([1, 5, 10, 12, 31])
    safer = collision_risk_score([37, 41, 52, 61, 68])
    assert risky > safer



def test_rank_candidates_returns_sorted_frame() -> None:
    history = sample_history()
    ranked = rank_candidates([[1, 5, 12, 23, 40], [7, 19, 35, 44, 51]], history)
    assert list(ranked.columns) == ["numbers", "pattern_score", "collision_score", "composite_score"]
    assert len(ranked) == 2



def test_abbreviated_wheel_respects_ticket_limit() -> None:
    tickets = abbreviated_wheel([1, 2, 3, 4, 5, 6, 7], ticket_size=5, limit=4)
    assert len(tickets) == 4
