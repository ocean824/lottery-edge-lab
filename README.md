# Lottery Edge Lab

**Lottery Edge Lab** is a private, research-oriented lottery analytics repository that now supports both a **command-line workflow** and a **desktop executable application**. Its purpose is to ingest lottery draw history, normalize data from official or structured sources, compute descriptive statistical signals, rank combinations with transparent heuristics, generate quick picks and wheel-style portfolios, and present those outputs through a user-friendly application interface. The project is intentionally framed as an **analysis and entertainment tool**, not as a guaranteed winning-number engine. The academic and official materials reviewed during setup consistently support a more careful conclusion: if any practical edge exists, it is more likely to come from structured coverage, collision reduction, and expected-value awareness than from proving deterministic foresight over a fair random draw.[1] [2] [3] [4]

## Why this repository exists

The market for lottery software is full of claims about AI prediction, secret formulas, hot numbers, overdue numbers, and mathematically inevitable picks. Those claims are often stronger than the underlying evidence. At the same time, official lottery archives, state open-data portals, and commercial results providers make it possible to build serious historical-analysis tooling around real draw histories.[5] [6] [7] [8] [9] This repository exists to turn that raw data availability into a cleaner, safer, and more defensible product architecture.

The upgraded version therefore focuses on four product goals. First, it makes draw history ingestion reproducible. Second, it exposes analysis features that users actually expect, such as results dashboards, historical lookups, frequency views, quick picks, smart picks, wheel generation, and jackpot context. Third, it places those features inside a desktop application that can be packaged as an executable file. Fourth, it surrounds the product with explicit compliance language so the user-facing experience remains aggressive in utility without becoming misleading in its claims.

## Research grounding

The repository design follows several research-backed observations and practical source findings.

| Observation | Product implication |
| --- | --- |
| Official archives and state data portals publish real historical lottery results.[5] [6] [7] [8] | The application should use connector-style ingestion and a canonical schema. |
| Expected value can change under some jackpot conditions, but ticket collisions matter.[1] [2] | The application should include jackpot context and collision-aware ranking rather than mystical prediction claims. |
| Lottery players choose numbers non-uniformly, often favoring dates or familiar patterns.[3] | The application should penalize collision-prone combinations and explain that logic clearly. |
| Wheeling is structurally useful as a coverage method, not proof of future draw prediction.[4] | The application should include wheel-building tools while describing them accurately. |
| Commercial providers advertise broad all-state lottery coverage, stats, and historical feeds.[9] | The architecture should remain pluggable so optional broad-coverage connectors can be added later. |

> “We find that choice is far from uniform, and exhibits some familiar and some new tendencies and biases. Players favor personally meaningful and situationally available numbers...” — *Number preferences in lotteries*[3]

> “Thus, the expected value of a lottery ticket decreases as the probability of collisions ... increase.” — *Maximizing the Expected Value of a Lottery Ticket: How to Sell and When to Buy*[1]

## Video-derived strategy review

The user-supplied video sources were analyzed as a source of **feature ideas**, not as proof that lottery prediction works. Across those videos, three recurring themes appeared.

| Theme | What the videos contributed | How the repository now uses it |
| --- | --- | --- |
| Roll-down and positive-EV monitoring | Rare cases where capped-jackpot games can create temporary positive expected value for high-volume play | Documented as an informational EV-watch concept, not as a general prediction engine |
| Heuristic filtering | Repeated use of sum windows, spread windows, odd/even balance, high/low balance, AC values, hot-number weighting, and anti-clustering rules | Implemented as configurable heuristic profiles in the scoring pipeline and desktop UI |
| LLM-assisted workflows | Structured prompts, spreadsheet-driven updates, and iterative filtering ideas | Reduced to optional implementation concepts and documentation; not treated as validated forecasting |

The important distinction is that the repository implements the **codeable mechanics** from those videos while refusing to present the videos’ stronger success claims as established fact. Claims about reliably hitting 4+1, discovering secret red-ball formulas, or making lottery prediction “feasible” remain unsupported by those sources themselves.[10] [11] [12] [13] [14] [15] [16] [17]

## Executable application scope

The repository has been upgraded so it can function as an **executable desktop application** rather than only as a backend toolkit. The new application is designed to resemble the workflow categories users expect from commercial lottery-analysis tools while using more accurate product language and stronger disclaimers.

| Feature area | Desktop application behavior |
| --- | --- |
| Jurisdiction and game browser | Browse national and state-oriented games from a registry-driven catalog |
| Latest results | View the latest normalized draw history records for the selected game |
| Smart Pick | Generate statistically ranked combinations using transparent heuristics |
| Quick Pick | Generate valid random combinations under the selected game rules |
| Frequency Chart | View top historical frequencies and export a chart image |
| Prize Matrix | Inspect game-structure metadata and prize-context notes |
| Jackpot Analysis | View combinatorial jackpot odds context and rule-aware notes |
| Strategy Profiles | Compare broad heuristic presets distilled from user-supplied source material |
| Wheel Builder | Generate abbreviated wheel-style ticket sets from a number pool |
| Compliance notices | See persistent short disclaimers and a full legal notice dialog |

## Heuristic profiles now implemented

The repository now includes a dedicated `heuristics.py` module and profile-aware ranking logic. These profiles operationalize common filtering rules seen in community lottery-analysis content without claiming predictive proof.

| Profile | Intended use | Main constraints |
| --- | --- | --- |
| `balanced` | General-purpose historical-shape filter | Sum 120-220, moderate spread, odd/even balance, low/high balance, AC 7-10 |
| `strict` | Narrower pattern filter based on the more restrictive video examples | Sum 150-200, spread 40-60, odd/even balance, low/high balance, AC 8-9, lower recent overlap |
| `coverage` | Multi-ticket diversification and broader structural coverage | Wider sum window, wider spread, more flexible parity and low/high counts, AC 6-10 |

These profiles influence ranking through transparent feature checks rather than opaque black-box promises. The desktop app exposes the selected profile and adds a **Strategy Profiles** tab so users can inspect the active logic.

## Current game coverage

Version 0.2.0 expands the registry beyond the original national-game prototype. Two games currently have live ingest connectors in the repository, while several additional games are represented in the registry so the application can present them, generate valid picks, and support future data connectors.

| Game | Coverage level | Current source strategy |
| --- | --- | --- |
| Powerball | Live historical sync | Official state archive ingestion |
| Mega Millions | Live historical sync | New York open-data CSV with official archive fallback |
| New York Lotto | Registry and rules support | Ready for manual or future source connector |
| Cash4Life | Registry and rules support | Ready for manual or future source connector |
| Take 5 Midday | Registry and rules support | Ready for manual or future source connector |
| Take 5 Evening | Registry and rules support | Ready for manual or future source connector |
| Pick 10 | Limited informational support | Ready for future source connector |
| Numbers 3 Midday | Registry and rules support | Ready for manual or future source connector |
| Numbers 3 Evening | Registry and rules support | Ready for manual or future source connector |

This means the product architecture is broader than the currently automated ingestion count. That is intentional. The software is now arranged so that the UI, compliance layer, scoring pipeline, and packaging pipeline do not have to be redesigned each time a new state or city lottery source is added.

## Repository layout

```text
lottery-edge-lab/
├── README.md
├── pyproject.toml
├── requirements.txt
├── build_desktop.sh
├── docs/
│   ├── architecture.md
│   └── executable_app_plan.md
├── research/
│   ├── video_strategy_synthesis.md
│   ├── video_strategy_classification.md
│   └── video_reviews/
├── src/lottery_edge_lab/
│   ├── cli.py
│   ├── desktop_app.py
│   ├── services.py
│   ├── charts.py
│   ├── compliance.py
│   ├── heuristics.py
│   ├── config.py
│   ├── ingest.py
│   ├── registry.py
│   ├── data_sources/
│   ├── features/
│   ├── scoring/
│   ├── optimization/
│   └── backtest/
├── data/
│   ├── raw/
│   ├── normalized/
│   └── processed/
└── tests/
    └── test_smoke.py
```

## Methodology

The analytical workflow is organized into several complementary layers.

### Historical-pattern ranking

The ranking engine computes descriptive features from historical draws, including single-number frequency, pair co-occurrence, recency pressure, odd-even balance, sum ranges, spacing, spread, and AC-style structural complexity. Those features do **not** prove that future fair draws become predictable. They are used as a transparent ranking heuristic that can be backtested and revised.

### Collision-risk scoring

The collision model downranks combinations that are more likely to be commonly chosen by other players. In the present implementation, it penalizes tickets that are date-heavy, excessively centered, repetitive in terminal digits, or visually conventional. That design is directly aligned with the research finding that lottery-number choice is not uniform across human players.[3]

### Portfolio and wheel optimization

The optimizer converts ranked candidates into diversified ticket sets or abbreviated wheel-style structures. This reflects the defensible mathematical core of wheeling systems: they can improve coverage efficiency once a number pool has already been selected, even though they do not change the official draw odds.[4]

### Jackpot context and EV-watch concepts

The desktop application also computes rule-based combination counts and presents prize-context notes. It now also includes text scaffolding for rare positive-EV or roll-down monitoring scenarios inspired by historical lottery-exploitation case studies. Those views are intended to help users understand when special-rule environments matter, not to imply that ordinary jackpot chasing becomes profitable by default.[1] [2] [10]

## Desktop application

The repository now contains a desktop entry point in `src/lottery_edge_lab/desktop_app.py`. The application uses a simple button-forward interface so users can choose a jurisdiction, pick a game, sync data, inspect results, generate smart picks, create quick picks, export a frequency chart, review strategy profiles, and view a compliance notice.

The desktop app is positioned to satisfy the user goal of a single executable file that ingests data and runs the computations internally. In practice, the app still depends on live internet access for source syncing unless a historical cache already exists locally. Once synced, the normalized datasets are stored under `data/normalized/`, and exported chart files are written under `data/processed/charts/`.

## Compliance and disclaimer framework

A commercial-facing lottery application needs more than feature parity. It also needs disciplined legal positioning. This repository therefore includes a dedicated compliance module and presents a persistent short disclaimer in the desktop window plus a full legal notice dialog.

| Compliance principle | Implementation in this repository |
| --- | --- |
| Do not imply guaranteed wins | The app describes outputs as ranked combinations, historical analysis, heuristic profiles, or random picks |
| Do not imply altered official odds | The disclaimer explicitly states that the software cannot change official game odds |
| Do not treat jackpots or charts as promises | Jackpot and chart views are presented as informational only |
| Require source verification | The app instructs users to verify results, rules, prizes, and odds with official lottery authorities |
| Avoid misleading income language | The disclaimer states that winnings and earnings are not promised, expected, or typical |
| Separate research claims from product claims | Video-source claims are documented as research notes, not user-facing guarantees |

The resulting language is more defensible than phrases such as “cheat the lottery,” “most likely winning numbers,” or “get rich,” which appeared in the reference material but should not be reused in a serious production product.

## Installation

Clone the repository, install the runtime dependencies, and export the source path.

```bash
git clone <your-private-repo-url>
cd lottery-edge-lab
python3.11 -m pip install -r requirements.txt
export PYTHONPATH=src
```

If your environment supports local project installation, you may also run `python3.11 -m pip install .`. The direct `PYTHONPATH=src` workflow is still documented as the default because it remains the most portable across restricted environments.

## Running the command-line workflow

The command-line entry point is still available and remains useful for scripted use.

| Command | Purpose | Example |
| --- | --- | --- |
| `sync` | Fetch and store normalized draw history | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli sync --game megamillions --limit 80` |
| `rank` | Rank candidate combinations from a historical pool | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli rank --game powerball --pool-size 10 --top 20` |
| `recommend` | Produce diversified recommended tickets | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli recommend --game megamillions --pool-size 10 --ticket-count 5` |
| `backtest` | Run a rolling backtest on ranked candidates | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli backtest --game megamillions --pool-size 10 --top-n 10 --train-window 30` |
| `wheel` | Build an abbreviated wheel from a custom number pool | `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli wheel --pool 3,7,12,18,23,29,33 --ticket-size 5 --limit 12` |

## Running the desktop application

Launch the desktop interface with either the module path or the installed script.

```bash
PYTHONPATH=src python3.11 -m lottery_edge_lab.desktop_app
```

or

```bash
PYTHONPATH=src lottery-edge-desktop
```

The application will open a desktop window that includes the game browser, actions panel, results tabs, smart-pick view, quick-pick view, prize matrix, jackpot analysis, strategy profile view, wheel builder, and compliance notice.

## Building the executable

The repository includes a build helper for creating a packaged executable.

```bash
chmod +x build_desktop.sh
./build_desktop.sh
```

This script uses PyInstaller to build a one-file desktop executable named `LotteryEdgeLab`. The output is written to `dist/LotteryEdgeLab`.

Because GUI packaging is platform-specific, a production Windows `.exe` should generally be built on Windows, and a production macOS app bundle should generally be built on macOS. The sandbox build created during development was a Linux binary.

## Example workflow

A practical first run uses the desktop app after syncing a live-supported game.

```bash
PYTHONPATH=src python3.11 -m lottery_edge_lab.cli sync --game megamillions --limit 80
PYTHONPATH=src python3.11 -m lottery_edge_lab.desktop_app
```

Inside the application, choose a supported game, select a heuristic profile, refresh the views, inspect the latest results, review the frequency panel, generate smart picks, and export the frequency chart if needed.

If you prefer a scripted workflow, sync and rank from the command line first, then use the desktop interface for presentation and additional actions.

## Validation snapshot

The upgraded repository was validated in practical ways during development, including after the new video-derived heuristics were integrated.

| Validation item | Result |
| --- | --- |
| Existing smoke tests | Passed |
| Desktop application import | Passed |
| Heuristic profile service smoke test | Passed |
| AC-value feature computation | Passed |
| Frequency-chart export | Passed in prior executable-upgrade validation |

## Limitations

The repository is deliberately explicit about its limits.

| Limitation | Practical meaning |
| --- | --- |
| Fair drawings remain close to random | No module in this repository can honestly guarantee future winning numbers |
| Current live adapters are not exhaustive | The application architecture is broad, but not every local or city lottery source has been connected yet |
| Some games are informational only for now | Registry coverage is broader than fully automated ingest coverage |
| Historical features may overfit | Backtests and cross-validation should be expanded before confidence is increased |
| Collision-risk modeling is approximate | It uses behavioral heuristics, not proprietary population-scale ticket-purchase data |
| Video-derived rules are heuristic | They are implemented because they are codeable and popular, not because they are proven predictors |
| Executable packaging is platform-specific | A binary should generally be built on the target operating system |

## Next expansion path

If you want the product to move closer to full all-state and local-lottery coverage, the next steps are clear. Add more game definitions to the registry. Implement new source adapters for each jurisdiction. Normalize them into the existing schema. Add official prize-matrix loaders where possible. Optionally add support for a licensed broad-coverage feed if you secure access to a provider that covers all states and territories.[9] The current repository structure is now prepared for that trajectory.

## Documentation

The architectural and product-scope decisions are documented in [`docs/architecture.md`](docs/architecture.md), [`docs/executable_app_plan.md`](docs/executable_app_plan.md), [`research/video_strategy_synthesis.md`](research/video_strategy_synthesis.md), and [`research/video_strategy_classification.md`](research/video_strategy_classification.md).

## TL;DR

If you want to get the upgraded version running quickly, use the following sequence.

| Step | Action |
| --- | --- |
| 1 | Clone the private repository and install dependencies with `python3.11 -m pip install -r requirements.txt` |
| 2 | Export `PYTHONPATH=src` |
| 3 | Sync a live-supported game such as Mega Millions with `PYTHONPATH=src python3.11 -m lottery_edge_lab.cli sync --game megamillions --limit 80` |
| 4 | Launch the app with `PYTHONPATH=src python3.11 -m lottery_edge_lab.desktop_app` |
| 5 | In the app, choose a game, pick a heuristic profile, and review the disclaimer |
| 6 | Use **Smart Pick**, **Quick Pick**, **Frequency Chart**, **Prize Matrix**, **Jackpot Analysis**, **Strategy Profiles**, and **Wheel Builder** as needed |
| 7 | When ready to package it, run `chmod +x build_desktop.sh && ./build_desktop.sh` to generate the desktop executable |
| 8 | Add more source adapters over time to expand from national games toward broader state and local coverage |

## References

[1]: https://arxiv.org/abs/2101.04242 "Maximizing the Expected Value of a Lottery Ticket: How to Sell and When to Buy"
[2]: https://web.williams.edu/Economics/wp/mathesonlottery.pdf "In Search of a Fair Bet in the Lottery"
[3]: https://www.cambridge.org/core/journals/judgment-and-decision-making/article/number-preferences-in-lotteries/47BA27051627CEED421AD3AEE255521E "Number preferences in lotteries"
[4]: https://lottoexpert.net/picking-winning-numbers/lottery-wheeling-systems "Lottery Wheeling Systems | Structured Coverage Explained Clearly"
[5]: https://www.powerball.com/previous-results "Previous Results | Powerball"
[6]: https://www.megamillions.com/winning-numbers/previous-drawings.aspx "Previous Drawings | Mega Millions"
[7]: https://nclottery.com/powerball-past-draws "Powerball - Past Draws | NC Education Lottery"
[8]: https://catalog.data.gov/dataset/lottery-mega-millions-winning-numbers-beginning-2002 "Lottery Mega Millions Winning Numbers: Beginning 2002"
[9]: https://downtack.com/en/us-lottery-api.html "US Lotteries API & widgets"
[10]: https://youtu.be/dnD9UciyiUY?si=i6cN8QSbEyDzKOQ4 "User-supplied YouTube source 1"
[11]: https://youtu.be/Jiwc80UkPKQ?si=adckmE9qJX424TTG "User-supplied YouTube source 2"
[12]: https://youtu.be/xmWxL0821E8?si=Gr9QDq-MTVmVmSNv "User-supplied YouTube source 3"
[13]: https://youtu.be/eOX7acjkGv0?si=FZOoSkPtRcpobTr6 "User-supplied YouTube source 4"
[14]: https://youtube.com/shorts/LffA9kPACQ4?si=bzfuaz_iJy2PJBt2 "User-supplied YouTube short 1"
[15]: https://youtube.com/shorts/18otQ2YenUg?si=KXckmF2-TljE40eV "User-supplied YouTube short 2"
[16]: https://youtube.com/shorts/jUAkNmO43aU?si=b7Su2QzW65fq0QDd "User-supplied YouTube short 3"
[17]: https://youtube.com/shorts/9hOBiIFPXNU?si=1tS5Xd2atfJXt9-J "User-supplied YouTube short 4"
