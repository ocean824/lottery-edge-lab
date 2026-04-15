from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from lottery_edge_lab.config import PROCESSED_ROOT
from lottery_edge_lab.services import frequency_table



def save_frequency_chart(game_slug: str, top_n: int = 15) -> Path:
    df = frequency_table(game_slug).head(top_n).sort_values("number")
    output_dir = PROCESSED_ROOT / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{game_slug}_frequency.png"

    plt.style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df["number"].astype(str), df["frequency"], color="#2563eb", label="All draws")
    ax.plot(df["number"].astype(str), df["recent_frequency"], color="#dc2626", marker="o", label="Recent draws")
    ax.set_title(f"Historical Frequency Snapshot: {game_slug}")
    ax.set_xlabel("Number")
    ax.set_ylabel("Occurrences")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path
