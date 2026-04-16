from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

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


class LotteryEdgeDesktop(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Lottery Edge Lab")
        self.geometry("1280x820")
        self.minsize(1100, 740)

        self.selected_game = tk.StringVar(value="powerball")
        self.selected_profile = tk.StringVar(value="balanced")
        self.pool_size = tk.IntVar(value=12)
        self.ticket_count = tk.IntVar(value=6)
        self.max_overlap = tk.IntVar(value=2)
        self.quick_pick_count = tk.IntVar(value=5)
        self.wheel_pool = tk.StringVar(value="3,7,12,18,23,29,33")
        self.status_text = tk.StringVar(value="Ready. Choose a game and sync data to begin.")

        self._build_layout()
        self._populate_game_tree()
        self.refresh_game_summary()

    def _build_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=12)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Lottery Edge Lab", font=("TkDefaultFont", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=SHORT_DISCLAIMER, wraplength=780, justify="left").grid(row=0, column=1, sticky="w", padx=16)
        ttk.Button(header, text="View Full Disclaimer", command=self.show_disclaimer).grid(row=0, column=2, sticky="e")

        sidebar = ttk.Frame(self, padding=(12, 0, 12, 12))
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.rowconfigure(1, weight=1)

        ttk.Label(sidebar, text="Jurisdictions and Games", font=("TkDefaultFont", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.game_tree = ttk.Treeview(sidebar, show="tree", height=28)
        self.game_tree.grid(row=1, column=0, sticky="nsew")
        self.game_tree.bind("<<TreeviewSelect>>", self.on_game_selected)

        action_frame = ttk.LabelFrame(sidebar, text="Actions", padding=10)
        action_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        action_frame.columnconfigure(1, weight=1)
        ttk.Button(action_frame, text="Sync Selected Game", command=self.sync_selected).grid(row=0, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(action_frame, text="Refresh Views", command=self.refresh_all_views).grid(row=1, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(action_frame, text="Export Frequency Chart", command=self.export_frequency_chart).grid(row=2, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Label(action_frame, text="Profile").grid(row=3, column=0, sticky="w")
        ttk.Combobox(
            action_frame,
            textvariable=self.selected_profile,
            values=[profile.slug for profile in list_profiles()],
            state="readonly",
        ).grid(row=3, column=1, sticky="ew", pady=3)
        ttk.Label(action_frame, text="Pool Size").grid(row=4, column=0, sticky="w")
        ttk.Spinbox(action_frame, from_=6, to=25, textvariable=self.pool_size, width=8).grid(row=4, column=1, sticky="ew")
        ttk.Label(action_frame, text="Smart Picks").grid(row=5, column=0, sticky="w")
        ttk.Spinbox(action_frame, from_=1, to=20, textvariable=self.ticket_count, width=8).grid(row=5, column=1, sticky="ew")
        ttk.Label(action_frame, text="Max Overlap").grid(row=6, column=0, sticky="w")
        ttk.Spinbox(action_frame, from_=0, to=10, textvariable=self.max_overlap, width=8).grid(row=6, column=1, sticky="ew")
        ttk.Label(action_frame, text="Quick Picks").grid(row=7, column=0, sticky="w")
        ttk.Spinbox(action_frame, from_=1, to=20, textvariable=self.quick_pick_count, width=8).grid(row=7, column=1, sticky="ew")

        main = ttk.Frame(self, padding=(0, 0, 12, 12))
        main.grid(row=1, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        self.summary_frame = ttk.LabelFrame(main, text="Game Summary", padding=10)
        self.summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.summary_frame.columnconfigure(1, weight=1)
        self.summary_labels = {}
        for idx, label in enumerate(["Game", "Jurisdiction", "Draw Schedule", "Top Prize", "Analysis Mode", "Heuristic Profile"]):
            ttk.Label(self.summary_frame, text=f"{label}:", font=("TkDefaultFont", 10, "bold")).grid(row=idx, column=0, sticky="nw", padx=(0, 10), pady=2)
            value = ttk.Label(self.summary_frame, text="", wraplength=700, justify="left")
            value.grid(row=idx, column=1, sticky="w", pady=2)
            self.summary_labels[label] = value

        self.notebook = ttk.Notebook(main)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        self.history_text = self._make_text_tab("Latest Results")
        self.frequency_text = self._make_text_tab("Frequency Chart")
        self.likely_numbers_text = self._make_text_tab("Likely Numbers")
        self.smart_pick_text = self._make_text_tab("Smart Pick")
        self.quick_pick_text = self._make_text_tab("Quick Pick")
        self.prize_text = self._make_text_tab("Prize Matrix")
        self.jackpot_text = self._make_text_tab("Jackpot Analysis")
        self.strategy_text = self._make_text_tab("Strategy Profiles")
        self.wheel_text = self._make_text_tab("Wheel Builder")

        wheel_controls = ttk.Frame(self.notebook)
        wheel_controls.columnconfigure(1, weight=1)
        self.notebook.add(wheel_controls, text="Wheel Controls")
        ttk.Label(wheel_controls, text="Enter a comma-separated number pool for abbreviated wheeling.").grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 8))
        ttk.Label(wheel_controls, text="Number Pool").grid(row=1, column=0, sticky="w", padx=12)
        ttk.Entry(wheel_controls, textvariable=self.wheel_pool).grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=6)
        ttk.Button(wheel_controls, text="Generate Wheel Tickets", command=self.generate_wheel).grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=8)

        footer = ttk.Frame(self, padding=(12, 0, 12, 12))
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Label(footer, textvariable=self.status_text).grid(row=0, column=0, sticky="w")

    def _make_text_tab(self, title: str) -> tk.Text:
        frame = ttk.Frame(self.notebook)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.notebook.add(frame, text=title)
        widget = tk.Text(frame, wrap="word")
        widget.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=widget.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        widget.configure(yscrollcommand=scroll.set)
        return widget

    def _populate_game_tree(self) -> None:
        for state_name, games in list_games_by_state().items():
            state_id = self.game_tree.insert("", "end", text=state_name, open=(state_name in {"National", "New York"}))
            for game in games:
                self.game_tree.insert(state_id, "end", iid=game.game_slug, text=game.game_name)

    def on_game_selected(self, _event: object | None = None) -> None:
        selection = self.game_tree.selection()
        if not selection:
            return
        slug = selection[0]
        try:
            get_game(slug)
        except ValueError:
            return
        self.selected_game.set(slug)
        self.refresh_game_summary()
        self.refresh_all_views()

    def show_disclaimer(self) -> None:
        messagebox.showinfo(DISCLAIMER_TITLE, FULL_DISCLAIMER)

    def refresh_game_summary(self) -> None:
        game = get_game(self.selected_game.get())
        self.summary_labels["Game"].configure(text=game.game_name)
        self.summary_labels["Jurisdiction"].configure(text=f"{game.state_name} ({game.jurisdiction})")
        self.summary_labels["Draw Schedule"].configure(text=game.draw_schedule or "Not specified")
        self.summary_labels["Top Prize"].configure(text=game.top_prize_label or "Varies by game")
        mode = "Full statistical analysis" if analysis_availability(game.game_slug) == "full" else "Limited informational support"
        self.summary_labels["Analysis Mode"].configure(text=mode)
        self.summary_labels["Heuristic Profile"].configure(text=self.selected_profile.get())

    def sync_selected(self) -> None:
        slug = self.selected_game.get()
        try:
            summary = sync_and_summarize(slug)
            self.status_text.set(
                f"Synced {summary.game_slug}: {summary.row_count} rows. Latest draw: {summary.latest_draw_date or 'n/a'}. Source: {summary.source_name or 'n/a'}."
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
        except Exception as exc:
            self.status_text.set(f"Refresh issue for {slug}: {exc}")

    def _replace_text(self, widget: tk.Text, content: str) -> None:
        widget.delete("1.0", "end")
        widget.insert("1.0", content)

    def _render_history(self, slug: str) -> None:
        df = latest_results_table(slug)
        self._replace_text(self.history_text, df.to_string(index=False) if not df.empty else "No history available yet.")

    def _render_frequency(self, slug: str) -> None:
        df = frequency_table(slug).head(30)
        heading = "Top historical frequencies and recent appearances\n\n"
        self._replace_text(self.frequency_text, heading + (df.to_string(index=False) if not df.empty else "No frequency data available."))

    def _render_likely_numbers(self, slug: str) -> None:
        if analysis_availability(slug) != "full":
            self._replace_text(self.likely_numbers_text, "Weighted likely-number ranking is not enabled for this game yet. Add a structured history connector to unlock number-level scoring.")
            return
        profile_slug = self.selected_profile.get()
        df = likely_number_table(slug, top=max(self.pool_size.get(), 15))
        prefix = likely_number_explainer(profile_slug) + "\n\n"
        self._replace_text(self.likely_numbers_text, prefix + (df.to_string(index=False) if not df.empty else "No likely-number ranking available."))

    def _render_smart_pick(self, slug: str) -> None:
        if analysis_availability(slug) != "full":
            self._replace_text(self.smart_pick_text, "Full smart-pick ranking is not enabled for this game yet. Use Quick Pick or import structured history to extend support.")
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
        self._replace_text(self.smart_pick_text, prefix + (df.to_string(index=False) if not df.empty else "No ranked picks available."))

    def _render_quick_pick(self, slug: str) -> None:
        tickets = quick_pick(slug, ticket_count=self.quick_pick_count.get())
        self._replace_text(self.quick_pick_text, "\n".join(tickets))

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
        self._replace_text(self.prize_text, content)

    def _render_jackpot(self, slug: str) -> None:
        context = jackpot_context(slug)
        content = (
            f"Game: {get_game(slug).game_name}\n"
            f"Top-prize label: {context.jackpot_label}\n"
            f"Approximate jackpot odds: {context.odds_text}\n\n"
            f"{context.note}\n\n"
            f"EV watch: {ev_watch_text()}"
        )
        self._replace_text(self.jackpot_text, content)

    def _render_strategy(self, slug: str) -> None:
        profile_df = heuristic_profile_table()
        content = (
            f"Selected game: {get_game(slug).game_name}\n"
            f"Selected profile: {self.selected_profile.get()}\n\n"
            "The profiles below are distilled from common lottery-analysis heuristics seen in user-supplied research sources and community workflows. "
            "They are included as configurable filters and organizational tools, not as verified prediction guarantees.\n\n"
            + profile_df.to_string(index=False)
        )
        self._replace_text(self.strategy_text, content)

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
            self._replace_text(self.wheel_text, "\n".join(tickets))
            self.status_text.set(f"Generated {len(tickets)} wheel tickets for {game.game_name}.")
        except Exception as exc:
            messagebox.showerror("Wheel generation failed", str(exc))



def main() -> None:
    app = LotteryEdgeDesktop()
    app.mainloop()


if __name__ == "__main__":
    main()
