from __future__ import annotations

import argparse
import json
from itertools import combinations

import pandas as pd

from lottery_edge_lab.backtest.evaluate import rolling_backtest
from lottery_edge_lab.ingest import load_game_history, sync_game_history
from lottery_edge_lab.optimization.wheel import abbreviated_wheel, diversified_top_tickets
from lottery_edge_lab.registry import get_game
from lottery_edge_lab.scoring.model import rank_candidates



def candidate_pool_from_history(history_df: pd.DataFrame, pool_size: int = 12) -> list[int]:
    counts: dict[int, int] = {}
    for numbers in history_df["main_numbers"].astype(str):
        for value in map(int, numbers.split()):
            counts[value] = counts.get(value, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [number for number, _ in ordered[:pool_size]]



def command_sync(args: argparse.Namespace) -> None:
    df = sync_game_history(args.game, limit=args.limit)
    print(json.dumps({"game": args.game, "rows": len(df), "latest_draw": df.iloc[-1]["draw_date"] if not df.empty else None}, indent=2))



def command_rank(args: argparse.Namespace) -> None:
    history = load_game_history(args.game)
    pool = candidate_pool_from_history(history, pool_size=args.pool_size)
    candidates = [list(combo) for combo in combinations(pool, get_game(args.game).main_count)]
    ranked = rank_candidates(candidates, history).head(args.top)
    print(ranked.to_string(index=False))



def command_recommend(args: argparse.Namespace) -> None:
    history = load_game_history(args.game)
    pool = candidate_pool_from_history(history, pool_size=args.pool_size)
    candidates = [list(combo) for combo in combinations(pool, get_game(args.game).main_count)]
    ranked = rank_candidates(candidates, history)
    selected = diversified_top_tickets(ranked, ticket_count=args.ticket_count, max_overlap=args.max_overlap)
    print(selected.to_string(index=False))



def command_backtest(args: argparse.Namespace) -> None:
    history = load_game_history(args.game)
    pool = candidate_pool_from_history(history, pool_size=args.pool_size)
    effective_window = args.train_window
    if len(history) <= effective_window:
        effective_window = max(5, len(history) // 2)
    report = rolling_backtest(history, pool, top_n=args.top_n, train_window=effective_window)
    summary = {
        "rows": int(len(report)),
        "train_window": int(effective_window),
        "mean_best_overlap_top_n": float(report["best_overlap_top_n"].mean()),
        "top_n_hit_rate_3plus": float(report["any_top_n_hit_3plus"].mean()),
    }
    print(json.dumps(summary, indent=2))



def command_wheel(args: argparse.Namespace) -> None:
    number_pool = [int(value) for value in args.pool.split(",")]
    tickets = abbreviated_wheel(number_pool, ticket_size=args.ticket_size, limit=args.limit)
    for ticket in tickets:
        print(" ".join(map(str, ticket)))



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lottery-edge", description="Lottery Edge Lab CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Fetch and store normalized game history")
    sync_parser.add_argument("--game", required=True, choices=["powerball", "megamillions"])
    sync_parser.add_argument("--limit", type=int, default=None)
    sync_parser.set_defaults(func=command_sync)

    rank_parser = subparsers.add_parser("rank", help="Rank candidate combinations")
    rank_parser.add_argument("--game", required=True, choices=["powerball", "megamillions"])
    rank_parser.add_argument("--pool-size", type=int, default=12)
    rank_parser.add_argument("--top", type=int, default=20)
    rank_parser.set_defaults(func=command_rank)

    recommend_parser = subparsers.add_parser("recommend", help="Generate diversified recommended tickets")
    recommend_parser.add_argument("--game", required=True, choices=["powerball", "megamillions"])
    recommend_parser.add_argument("--pool-size", type=int, default=12)
    recommend_parser.add_argument("--ticket-count", type=int, default=5)
    recommend_parser.add_argument("--max-overlap", type=int, default=2)
    recommend_parser.set_defaults(func=command_recommend)

    backtest_parser = subparsers.add_parser("backtest", help="Run a simple rolling backtest")
    backtest_parser.add_argument("--game", required=True, choices=["powerball", "megamillions"])
    backtest_parser.add_argument("--pool-size", type=int, default=12)
    backtest_parser.add_argument("--top-n", type=int, default=10)
    backtest_parser.add_argument("--train-window", type=int, default=30)
    backtest_parser.set_defaults(func=command_backtest)

    wheel_parser = subparsers.add_parser("wheel", help="Generate abbreviated wheel tickets from a pool")
    wheel_parser.add_argument("--pool", required=True, help="Comma-separated number pool, e.g. 3,7,12,18,23,29,33")
    wheel_parser.add_argument("--ticket-size", type=int, default=5)
    wheel_parser.add_argument("--limit", type=int, default=12)
    wheel_parser.set_defaults(func=command_wheel)

    return parser



def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
