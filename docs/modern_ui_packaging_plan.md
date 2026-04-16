# Modern UI and Cross-Platform Packaging Plan

## Design goals

The next iteration should move the desktop application from a utility-style analyst tool toward a more polished product. The redesign should keep all existing workflows intact while improving visual hierarchy, discoverability, and confidence. The target style is a **dark, modern, sleek interface** with stronger contrast, consistent spacing, card-like content regions, friendlier control labels, and clearer presentation of ranked numbers and recommended tickets.

## UI strategy

The current `tkinter` / `ttk` approach should be upgraded to a modern themed layer. The recommended path is to migrate the main window to **CustomTkinter** while retaining the existing service layer and analytical workflow. That approach keeps the codebase Python-native and packaging-friendly while materially improving the visual result.

| Area | Current state | Planned upgrade |
| --- | --- | --- |
| App shell | Default window and stock widget styling | Dark appearance mode, modern color palette, consistent spacing, branded header |
| Navigation | Tree and notebook driven | Left rail with searchable game selection and segmented action controls |
| Summary | Plain labels | Dashboard cards for game, profile, prize, sync state, and odds context |
| Likely numbers | Text dump | Ranked number cards or structured table with score emphasis and explanation panel |
| Smart picks | Raw text table | Highlighted ticket cards with score and rationale summary |
| Strategy context | Dense text | Dedicated analysis panel with profile summary and model explanation |
| Status feedback | Single footer line | Top status banner and inline success / error messaging |

## Layout model

The redesigned app should use a three-zone layout.

| Zone | Purpose |
| --- | --- |
| Left rail | State filter, game picker, sync button, profile selection, primary controls |
| Center workspace | Dashboard header, likely-number view, smart picks, charts, results, strategy tabs |
| Right insight column | Compliance notice, game metadata, active model notes, jackpot context |

This structure makes the application feel more guided and easier to scan than the current full-width text-tab approach.

## Implementation approach

The analytical logic should remain in the existing service layer. The UI layer should be refactored to consume those services and render richer components instead of raw multiline text whenever practical. The first redesign pass should preserve these workflows:

| Workflow | Must remain supported |
| --- | --- |
| Sync selected game | Yes |
| Refresh views | Yes |
| View latest results | Yes |
| View likely-number ranking | Yes |
| Generate smart picks | Yes |
| Generate quick picks | Yes |
| Export frequency chart | Yes |
| View prize matrix and jackpot analysis | Yes |
| View heuristic strategies | Yes |
| Generate wheel tickets | Yes |
| View disclaimers | Yes |

## Packaging strategy

A true Windows `.exe` and a native macOS build should not be produced from this Linux environment using local PyInstaller because PyInstaller is not a cross-compiler.[1] The repository should therefore gain platform-specific build support through **GitHub Actions** so native artifacts can be built on hosted Windows and macOS runners.

| Target | Delivery method |
| --- | --- |
| Linux | Local build remains available in the sandbox via the existing build script |
| Windows | GitHub Actions workflow on `windows-latest`, package with PyInstaller, upload `.exe` artifact |
| macOS | GitHub Actions workflow on `macos-latest`, package `.app` or binary artifact, upload artifact |

## Repository changes to make

The implementation phase should add the following:

| File or area | Planned change |
| --- | --- |
| `src/lottery_edge_lab/desktop_app.py` | Replace utility-style layout with modern CustomTkinter UI |
| `pyproject.toml` and `requirements.txt` | Add modern UI dependency and any packaging support libraries |
| `build_desktop.sh` | Keep Linux build, but document Linux-only local output |
| `.github/workflows/` | Add native Windows and macOS build workflows |
| `README.md` | Explain the new UI, launch behavior, native build paths, and artifact expectations |
| `docs/ui_packaging_assessment.md` | Preserve assessment findings |

## Expected outcome

After implementation, the application should feel substantially more polished and user-friendly than the current version while remaining faithful to the existing analytical logic. The repository should also be ready to generate native Windows and macOS deliverables through its associated GitHub automation, even though those binaries are not expected to be built locally inside Linux.

## References

[1]: https://pyinstaller.org/en/stable/ "PyInstaller Manual"
