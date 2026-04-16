from __future__ import annotations

from pathlib import Path
import tkinter.messagebox as messagebox

import customtkinter as ctk

from lottery_edge_lab.charts import save_frequency_chart
from lottery_edge_lab.compliance import DISCLAIMER_TITLE, FULL_DISCLAIMER, SHORT_DISCLAIMER
from lottery_edge_lab.heuristics import list_profiles
from lottery_edge_lab.registry import get_game, list_games_by_state
from lottery_edge_lab.services import (
    analysis_availability,
    ev_watch_text,
    frequency_table,
    heuristic_profile_table,
    jackpot_context,
    latest_results_table,
    likely_number_explainer,
    likely_number_table,
    quick_pick,
    smart_pick,
    smart_pick_explainer,
    sync_and_summarize,
    wheel_tickets,
)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#07111f"
SURFACE = "#0f1c2e"
SURFACE_ALT = "#14253b"
BORDER = "#24344c"
ACCENT = "#22d3ee"
ACCENT_ALT = "#7c3aed"
TEXT = "#ecf4ff"
TEXT_MUTED = "#8ba3c7"
GOOD = "#34d399"
WARN = "#f59e0b"


class InfoCard(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, title: str, value: str = "—") -> None:
        super().__init__(master, fg_color=SURFACE, corner_radius=18, border_width=1, border_color=BORDER)
        self.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 2))
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            text_color=TEXT,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=280,
        )
        self.value_label.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))

    def set_value(self, value: str) -> None:
        self.value_label.configure(text=value)


class LotteryEdgeDesktop(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Lottery Edge Lab")
        self.geometry("1600x980")
        self.minsize(1360, 840)
        self.configure(fg_color=BG)

        self.selected_game = ctk.StringVar(value="powerball")
        self.selected_profile = ctk.StringVar(value="balanced")
        self.selected_state = ctk.StringVar(value="National")
        self.pool_size = ctk.IntVar(value=12)
        self.ticket_count = ctk.IntVar(value=6)
        self.max_overlap = ctk.IntVar(value=2)
        self.quick_pick_count = ctk.IntVar(value=5)
        self.wheel_pool = ctk.StringVar(value="3,7,12,18,23,29,33")
        self.status_text = ctk.StringVar(value="Ready. Choose a game and sync data to begin.")

        self.game_buttons: dict[str, ctk.CTkButton] = {}
        self.top_number_cards: list[InfoCard] = []
        self.smart_pick_cards: list[InfoCard] = []

        self._build_layout()
        self._refresh_game_buttons()
        self.refresh_game_summary()
        self.refresh_all_views()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_left_rail()
        self._build_center_workspace()
        self._build_right_rail()
        self._build_footer()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=22, border_width=1, border_color=BORDER)
        header.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=18, pady=(18, 10))
        header.grid_columnconfigure(1, weight=1)

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w", padx=(18, 12), pady=16)
        ctk.CTkLabel(
            title_block,
            text="Lottery Edge Lab",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_block,
            text="Modern lottery analytics, ranking, and structured decision support.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(4, 0))

        disclaimer = ctk.CTkLabel(
            header,
            text=SHORT_DISCLAIMER,
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=760,
            font=ctk.CTkFont(size=12),
        )
        disclaimer.grid(row=0, column=1, sticky="w", padx=6, pady=16)

        ctk.CTkButton(
            header,
            text="Legal Notice",
            command=self.show_disclaimer,
            fg_color=ACCENT_ALT,
            hover_color="#6d28d9",
            corner_radius=14,
            width=140,
            height=40,
        ).grid(row=0, column=2, sticky="e", padx=(8, 18), pady=16)

    def _build_left_rail(self) -> None:
        rail = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=22, border_width=1, border_color=BORDER)
        rail.grid(row=1, column=0, sticky="nsew", padx=(18, 10), pady=(0, 12))
        rail.grid_rowconfigure(3, weight=1)
        rail.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(rail, text="Game Browser", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 6)
        )
        ctk.CTkLabel(rail, text="Choose a jurisdiction and game to sync and analyze.", text_color=TEXT_MUTED).grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 12)
        )

        state_names = list(list_games_by_state().keys())
        self.state_menu = ctk.CTkOptionMenu(
            rail,
            values=state_names,
            variable=self.selected_state,
            command=lambda _choice: self._refresh_game_buttons(),
            fg_color=SURFACE_ALT,
            button_color=ACCENT_ALT,
            button_hover_color="#6d28d9",
            dropdown_fg_color=SURFACE_ALT,
            corner_radius=14,
            height=36,
        )
        self.state_menu.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))

        self.game_scroll = ctk.CTkScrollableFrame(
            rail,
            fg_color=BG,
            corner_radius=18,
            border_width=1,
            border_color=BORDER,
            label_text="Available Games",
            label_font=ctk.CTkFont(size=14, weight="bold"),
            label_fg_color=SURFACE_ALT,
            label_text_color=TEXT,
        )
        self.game_scroll.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 16))
        self.game_scroll.grid_columnconfigure(0, weight=1)

        controls = ctk.CTkFrame(rail, fg_color=SURFACE_ALT, corner_radius=18, border_width=1, border_color=BORDER)
        controls.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 18))
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls, text="Control Deck", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 10)
        )
        self._add_labeled_option(controls, "Profile", 1, ctk.CTkOptionMenu(
            controls,
            variable=self.selected_profile,
            values=[profile.slug for profile in list_profiles()],
            command=lambda _choice: self.refresh_all_views(),
            fg_color=BG,
            button_color=ACCENT_ALT,
            button_hover_color="#6d28d9",
            dropdown_fg_color=SURFACE_ALT,
            corner_radius=12,
            height=34,
        ))
        self._add_labeled_option(controls, "Pool Size", 2, ctk.CTkEntry(controls, textvariable=self.pool_size, height=34))
        self._add_labeled_option(controls, "Smart Picks", 3, ctk.CTkEntry(controls, textvariable=self.ticket_count, height=34))
        self._add_labeled_option(controls, "Max Overlap", 4, ctk.CTkEntry(controls, textvariable=self.max_overlap, height=34))
        self._add_labeled_option(controls, "Quick Picks", 5, ctk.CTkEntry(controls, textvariable=self.quick_pick_count, height=34))

        ctk.CTkButton(
            controls,
            text="Sync Selected Game",
            command=self.sync_selected,
            fg_color=ACCENT,
            hover_color="#06b6d4",
            text_color="#04111d",
            corner_radius=14,
            height=38,
        ).grid(row=6, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 8))
        ctk.CTkButton(
            controls,
            text="Refresh Views",
            command=self.refresh_all_views,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            hover_color="#1d3550",
            corner_radius=14,
            height=38,
        ).grid(row=7, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 8))
        ctk.CTkButton(
            controls,
            text="Export Frequency Chart",
            command=self.export_frequency_chart,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            hover_color="#1d3550",
            corner_radius=14,
            height=38,
        ).grid(row=8, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14))

    def _build_center_workspace(self) -> None:
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.grid(row=1, column=1, sticky="nsew", pady=(0, 12))
        center.grid_rowconfigure(2, weight=1)
        center.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(center, fg_color=SURFACE, corner_radius=22, border_width=1, border_color=BORDER)
        hero.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        hero.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_game = InfoCard(hero, "Game")
        self.card_game.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=16)
        self.card_profile = InfoCard(hero, "Profile")
        self.card_profile.grid(row=0, column=1, sticky="ew", padx=8, pady=16)
        self.card_prize = InfoCard(hero, "Top Prize")
        self.card_prize.grid(row=0, column=2, sticky="ew", padx=8, pady=16)
        self.card_mode = InfoCard(hero, "Analysis")
        self.card_mode.grid(row=0, column=3, sticky="ew", padx=(8, 16), pady=16)

        rank_strip = ctk.CTkFrame(center, fg_color=SURFACE, corner_radius=22, border_width=1, border_color=BORDER)
        rank_strip.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        rank_strip.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkLabel(
            rank_strip,
            text="Top Ranked Numbers",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(14, 8))

        for idx in range(4):
            card = InfoCard(rank_strip, f"Rank {idx + 1}", "Sync data to view")
            card.grid(row=1, column=idx, sticky="ew", padx=(16 if idx == 0 else 8, 16 if idx == 3 else 8), pady=(0, 16))
            self.top_number_cards.append(card)

        body = ctk.CTkFrame(center, fg_color=SURFACE, corner_radius=22, border_width=1, border_color=BORDER)
        body.grid(row=2, column=0, sticky="nsew")
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        pick_header = ctk.CTkFrame(body, fg_color="transparent")
        pick_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        pick_header.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(pick_header, text="Featured Smart Picks", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )
        for idx in range(3):
            card = InfoCard(pick_header, f"Pick {idx + 1}", "Refresh analysis")
            card.grid(row=1, column=idx, sticky="ew", padx=(0 if idx == 0 else 8, 0 if idx == 2 else 8), pady=(0, 4))
            self.smart_pick_cards.append(card)

        self.tabview = ctk.CTkTabview(body, fg_color=BG, segmented_button_fg_color=SURFACE_ALT, segmented_button_selected_color=ACCENT_ALT)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=16, pady=(6, 16))
        for name in [
            "Latest Results",
            "Likely Numbers",
            "Smart Picks",
            "Quick Picks",
            "Frequency",
            "Prize Matrix",
            "Jackpot",
            "Strategy",
            "Wheel Builder",
        ]:
            self.tabview.add(name)
            self.tabview.tab(name).grid_columnconfigure(0, weight=1)
            self.tabview.tab(name).grid_rowconfigure(0, weight=1)

        self.history_text = self._make_textbox(self.tabview.tab("Latest Results"))
        self.likely_numbers_text = self._make_textbox(self.tabview.tab("Likely Numbers"))
        self.smart_pick_text = self._make_textbox(self.tabview.tab("Smart Picks"))
        self.quick_pick_text = self._make_textbox(self.tabview.tab("Quick Picks"))
        self.frequency_text = self._make_textbox(self.tabview.tab("Frequency"))
        self.prize_text = self._make_textbox(self.tabview.tab("Prize Matrix"))
        self.jackpot_text = self._make_textbox(self.tabview.tab("Jackpot"))
        self.strategy_text = self._make_textbox(self.tabview.tab("Strategy"))

        wheel_tab = self.tabview.tab("Wheel Builder")
        ctk.CTkLabel(
            wheel_tab,
            text="Enter a comma-separated number pool to generate abbreviated wheel tickets.",
            text_color=TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))
        self.wheel_entry = ctk.CTkEntry(wheel_tab, textvariable=self.wheel_pool, height=38)
        self.wheel_entry.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        ctk.CTkButton(
            wheel_tab,
            text="Generate Wheel Tickets",
            command=self.generate_wheel,
            fg_color=ACCENT,
            hover_color="#06b6d4",
            text_color="#04111d",
            corner_radius=14,
            height=38,
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.wheel_text = self._make_textbox(wheel_tab, row=3, pady=(0, 16))

    def _build_right_rail(self) -> None:
        rail = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=22, border_width=1, border_color=BORDER)
        rail.grid(row=1, column=2, sticky="nsew", padx=(10, 18), pady=(0, 12))
        rail.grid_columnconfigure(0, weight=1)
        rail.grid_rowconfigure(3, weight=1)

        self.status_banner = ctk.CTkLabel(
            rail,
            textvariable=self.status_text,
            text_color=GOOD,
            justify="left",
            wraplength=300,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.status_banner.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 12))

        self.model_notes = self._make_side_panel(rail, "Model Notes")
        self.model_notes.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.jackpot_notes = self._make_side_panel(rail, "Jackpot Context")
        self.jackpot_notes.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        self.compliance_notes = self._make_side_panel(rail, "Compliance")
        self.compliance_notes.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self._set_textbox(self.compliance_notes, SHORT_DISCLAIMER + "\n\nOpen the full legal notice for the complete disclaimer.")

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 16))
        ctk.CTkLabel(
            footer,
            text="Lottery Edge Lab is an analytics tool. Verify odds, prizes, and game rules with official lottery authorities.",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w")

    def _add_labeled_option(self, parent: ctk.CTkFrame, label: str, row: int, widget: ctk.CTkBaseClass) -> None:
        ctk.CTkLabel(parent, text=label, text_color=TEXT_MUTED).grid(row=row, column=0, sticky="w", padx=(14, 8), pady=6)
        widget.grid(row=row, column=1, sticky="ew", padx=(0, 14), pady=6)

    def _make_textbox(self, parent: ctk.CTkBaseClass, row: int = 0, pady: tuple[int, int] = (12, 12)) -> ctk.CTkTextbox:
        box = ctk.CTkTextbox(parent, fg_color=SURFACE_ALT, border_width=1, border_color=BORDER, corner_radius=16, text_color=TEXT)
        box.grid(row=row, column=0, sticky="nsew", padx=16, pady=pady)
        box.configure(font=("SF Pro Text", 13))
        return box

    def _make_side_panel(self, parent: ctk.CTkFrame, title: str) -> ctk.CTkTextbox:
        frame = ctk.CTkFrame(parent, fg_color=SURFACE_ALT, corner_radius=18, border_width=1, border_color=BORDER)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=title, text_color=TEXT, font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 8)
        )
        box = ctk.CTkTextbox(frame, fg_color=BG, border_width=1, border_color=BORDER, corner_radius=14, text_color=TEXT)
        box.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        box.configure(font=("SF Pro Text", 12))
        return box

    def _set_textbox(self, widget: ctk.CTkTextbox, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _refresh_game_buttons(self) -> None:
        for child in self.game_scroll.winfo_children():
            child.destroy()
        self.game_buttons.clear()

        selected_state = self.selected_state.get()
        games_by_state = list_games_by_state()
        games = games_by_state.get(selected_state, [])
        for idx, game in enumerate(games):
            button = ctk.CTkButton(
                self.game_scroll,
                text=game.game_name,
                anchor="w",
                height=38,
                corner_radius=12,
                fg_color=SURFACE_ALT if game.game_slug != self.selected_game.get() else ACCENT_ALT,
                hover_color="#1d3550" if game.game_slug != self.selected_game.get() else "#6d28d9",
                command=lambda slug=game.game_slug: self.on_game_selected(slug),
            )
            button.grid(row=idx, column=0, sticky="ew", padx=8, pady=5)
            self.game_buttons[game.game_slug] = button

    def on_game_selected(self, slug: str) -> None:
        get_game(slug)
        self.selected_game.set(slug)
        game = get_game(slug)
        self.selected_state.set(game.state_name)
        self._refresh_game_buttons()
        self.refresh_game_summary()
        self.refresh_all_views()

    def show_disclaimer(self) -> None:
        messagebox.showinfo(DISCLAIMER_TITLE, FULL_DISCLAIMER)

    def refresh_game_summary(self) -> None:
        game = get_game(self.selected_game.get())
        mode = "Full statistical analysis" if analysis_availability(game.game_slug) == "full" else "Limited informational support"
        self.card_game.set_value(game.game_name)
        self.card_profile.set_value(self.selected_profile.get())
        self.card_prize.set_value(game.top_prize_label or "Varies by game")
        self.card_mode.set_value(mode)
        self._refresh_game_buttons()

    def sync_selected(self) -> None:
        slug = self.selected_game.get()
        try:
            summary = sync_and_summarize(slug)
            self.status_text.set(
                f"Synced {summary.game_slug}: {summary.row_count} rows. Latest draw: {summary.latest_draw_date or 'n/a'}."
            )
            self.refresh_all_views()
        except Exception as exc:
            messagebox.showerror("Sync failed", str(exc))

    def refresh_all_views(self) -> None:
        slug = self.selected_game.get()
        try:
            self.refresh_game_summary()
            self._render_history(slug)
            self._render_frequency(slug)
            self._render_likely_numbers(slug)
            self._render_smart_pick(slug)
            self._render_quick_pick(slug)
            self._render_prize_matrix(slug)
            self._render_jackpot(slug)
            self._render_strategy(slug)
            self._refresh_right_rail(slug)
        except Exception as exc:
            self.status_text.set(f"Refresh issue for {slug}: {exc}")

    def _render_history(self, slug: str) -> None:
        df = latest_results_table(slug)
        content = df.to_string(index=False) if not df.empty else "No history available yet."
        self._set_textbox(self.history_text, content)

    def _render_frequency(self, slug: str) -> None:
        df = frequency_table(slug).head(30)
        heading = "Top historical frequencies and recent appearances\n\n"
        self._set_textbox(self.frequency_text, heading + (df.to_string(index=False) if not df.empty else "No frequency data available."))

    def _render_likely_numbers(self, slug: str) -> None:
        if analysis_availability(slug) != "full":
            message = "Weighted likely-number ranking is not enabled for this game yet. Add a structured history connector to unlock number-level scoring."
            self._set_textbox(self.likely_numbers_text, message)
            for idx, card in enumerate(self.top_number_cards):
                card.title_label.configure(text=f"Rank {idx + 1}")
                card.set_value("Unavailable")
            return

        profile_slug = self.selected_profile.get()
        df = likely_number_table(slug, top=max(self.pool_size.get(), 15))
        prefix = likely_number_explainer(profile_slug) + "\n\n"
        self._set_textbox(self.likely_numbers_text, prefix + (df.to_string(index=False) if not df.empty else "No likely-number ranking available."))

        top_df = df.head(4)
        for idx, card in enumerate(self.top_number_cards):
            if idx < len(top_df):
                row = top_df.iloc[idx]
                card.title_label.configure(text=f"Rank {idx + 1} • Score {row['weighted_score']:.2f}")
                card.set_value(f"{int(row['number'])}\n{row['notes']}")
            else:
                card.title_label.configure(text=f"Rank {idx + 1}")
                card.set_value("—")

    def _render_smart_pick(self, slug: str) -> None:
        if analysis_availability(slug) != "full":
            message = "Full smart-pick ranking is not enabled for this game yet. Use Quick Pick or import structured history to extend support."
            self._set_textbox(self.smart_pick_text, message)
            for idx, card in enumerate(self.smart_pick_cards):
                card.title_label.configure(text=f"Pick {idx + 1}")
                card.set_value("Unavailable")
            return

        profile_slug = self.selected_profile.get()
        df = smart_pick(
            slug,
            pool_size=self.pool_size.get(),
            ticket_count=self.ticket_count.get(),
            max_overlap=self.max_overlap.get(),
            profile_slug=profile_slug,
        )
        prefix = smart_pick_explainer(profile_slug) + "\n\n"
        self._set_textbox(self.smart_pick_text, prefix + (df.to_string(index=False) if not df.empty else "No ranked picks available."))

        for idx, card in enumerate(self.smart_pick_cards):
            if idx < len(df):
                row = df.iloc[idx]
                card.title_label.configure(text=f"Pick {idx + 1} • {row['composite_score']:.2f}")
                card.set_value(str(row["numbers"]))
            else:
                card.title_label.configure(text=f"Pick {idx + 1}")
                card.set_value("—")

    def _render_quick_pick(self, slug: str) -> None:
        tickets = quick_pick(slug, ticket_count=self.quick_pick_count.get())
        content = "\n".join(f"{idx + 1:02d}. {ticket}" for idx, ticket in enumerate(tickets))
        self._set_textbox(self.quick_pick_text, content)

    def _render_prize_matrix(self, slug: str) -> None:
        game = get_game(slug)
        content = (
            f"Game: {game.game_name}\n"
            f"Jurisdiction: {game.state_name}\n"
            f"Top prize label: {game.top_prize_label or 'Varies'}\n"
            f"Main field: choose {game.main_count} from {game.main_min}-{game.main_max}\n"
        )
        if game.bonus_count and game.bonus_min is not None and game.bonus_max is not None:
            content += f"Bonus field: choose {game.bonus_count} from {game.bonus_min}-{game.bonus_max}\n"
        if game.multiplier_name:
            content += f"Multiplier option: {game.multiplier_name}\n"
        content += "\nPrize details should be verified with the official lottery authority because matrix structures and add-on options can change."
        self._set_textbox(self.prize_text, content)

    def _render_jackpot(self, slug: str) -> None:
        context = jackpot_context(slug)
        content = (
            f"Game: {get_game(slug).game_name}\n"
            f"Top-prize label: {context.jackpot_label}\n"
            f"Approximate jackpot odds: {context.odds_text}\n\n"
            f"{context.note}\n\n"
            f"EV watch: {ev_watch_text()}"
        )
        self._set_textbox(self.jackpot_text, content)

    def _render_strategy(self, slug: str) -> None:
        profile_df = heuristic_profile_table()
        content = (
            f"Selected game: {get_game(slug).game_name}\n"
            f"Selected profile: {self.selected_profile.get()}\n\n"
            "The profiles below are distilled from common lottery-analysis heuristics seen in research and community workflows. "
            "They are included as configurable filters and organizational tools, not as verified prediction guarantees.\n\n"
            + profile_df.to_string(index=False)
        )
        self._set_textbox(self.strategy_text, content)

    def _refresh_right_rail(self, slug: str) -> None:
        game = get_game(slug)
        self._set_textbox(
            self.model_notes,
            likely_number_explainer(self.selected_profile.get())
            + "\n\n"
            + smart_pick_explainer(self.selected_profile.get()),
        )
        context = jackpot_context(slug)
        self._set_textbox(
            self.jackpot_notes,
            f"{game.game_name}\nOdds: {context.odds_text}\nTop prize: {context.jackpot_label}\n\n{ev_watch_text()}",
        )
        compliance_text = (
            SHORT_DISCLAIMER
            + "\n\n"
            + "The current build is designed to support ranking, organization, and analytics. It does not change official odds or guarantee outcomes."
        )
        self._set_textbox(self.compliance_notes, compliance_text)

    def export_frequency_chart(self) -> None:
        slug = self.selected_game.get()
        try:
            chart_path = save_frequency_chart(slug)
            self.status_text.set(f"Saved frequency chart to {chart_path}.")
        except Exception as exc:
            messagebox.showerror("Chart export failed", str(exc))

    def generate_wheel(self) -> None:
        slug = self.selected_game.get()
        game = get_game(slug)
        try:
            pool = [int(item.strip()) for item in self.wheel_pool.get().split(",") if item.strip()]
            tickets = wheel_tickets(pool, ticket_size=game.main_count, limit=12)
            content = "\n".join(f"{idx + 1:02d}. {ticket}" for idx, ticket in enumerate(tickets))
            self._set_textbox(self.wheel_text, content)
            self.status_text.set(f"Generated {len(tickets)} wheel tickets for {game.game_name}.")
        except Exception as exc:
            messagebox.showerror("Wheel generation failed", str(exc))


def main() -> None:
    app = LotteryEdgeDesktop()
    app.mainloop()


if __name__ == "__main__":
    main()
