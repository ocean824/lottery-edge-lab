# Executable Application Upgrade Plan

## Product direction

The repository will be upgraded from a command-line research toolkit into a **desktop executable application** that can run as a self-contained tool for end users. The application will mirror the functional categories visible in the reference product while using more accurate and legally safer positioning. The core proposition is a lottery analytics workstation that ingests official or structured lottery data, presents game dashboards, analyzes historical results, generates ranked combinations, and provides informational jackpot and prize views.

## Functional scope

| Area | Planned executable behavior |
| --- | --- |
| Dashboard | Show jurisdictions, games, latest draw results, next draw fields when available, and quick action buttons |
| Data sync | Pull historical results from supported official or structured sources and cache them locally |
| Game browser | Let users select state or national games from a registry-driven catalog |
| Past results | Present sortable draw-history tables per game |
| Frequency charts | Show hot/cold counts and frequency distributions derived from real history |
| Smart pick | Generate ranked combinations using pattern scoring plus collision-risk penalties |
| Quick pick | Generate random valid combinations by game rules |
| Prize matrix | Show known prize structures and odds metadata when captured in the registry |
| Jackpot analysis | Surface current jackpot metadata and simple expected-value style context where supported |
| Compliance | Show persistent disclaimers in the UI and include a full legal notice window |

## Technical architecture

The executable should be built as a Python desktop application using a standard-library GUI stack so packaging is simple and reproducible. A `tkinter`-based interface is appropriate for version 1 because it avoids heavy runtime dependencies, can be packaged into a single executable with PyInstaller, and is adequate for dashboard, tabs, tables, and chart-launch actions.

The application should preserve the existing analysis modules where possible. The ingest, feature engineering, scoring, and optimization logic should remain as reusable backend services. A new desktop layer should orchestrate those modules and render results through a GUI.

## Planned module additions

| Module | Responsibility |
| --- | --- |
| `desktop_app.py` | Main application entry point and window lifecycle |
| `services.py` | High-level orchestration for sync, results loading, ranking, and quick-pick generation |
| `game_catalog.py` | Richer registry with state and game metadata for UI navigation |
| `compliance.py` | Disclaimer text, legal notices, and safe marketing labels |
| `charts.py` | Frequency chart creation and image export |
| `current_data.py` | Optional current-jackpot and next-draw loaders where structured sources exist |

## Executable packaging approach

The repository should support building an executable with PyInstaller. The primary deliverable for version 1 will be a packaged desktop binary generated from the desktop entry point. The repository will include a build script and packaging instructions. If full binary creation is environment-sensitive, the repository should still produce a deterministic build pipeline so the executable can be generated reliably.

## Compliance framework

The user-facing language should avoid claims that the software can guarantee or reliably force lottery wins. Acceptable labels include **Smart Pick**, **Ranked Pick**, **Quick Pick**, **Historical Frequency**, **Jackpot Context**, and **Prize Matrix**. The application should prominently disclose that lottery outcomes are random, the software does not alter official odds, results are for informational and entertainment use, and users must verify results, rules, and prizes with official lottery authorities.

## UX notes

The reference screenshots show a simple, button-forward interface. The desktop version should keep that simplicity. It should offer a jurisdiction selector, a game list, game cards or panels, and obvious action buttons for the primary functions. The first screen should also present the main disclaimer so the user sees the legal positioning before using any pick-generation feature.
