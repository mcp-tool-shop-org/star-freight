"""Combat screen — maritime-themed duel and naval combat.

Deprecated: replaced by EncounterScreen which handles all combat phases
(approach, naval, boarding, duel, victory/defeat) in a single continuous
screen. This file is kept for backward compatibility.

Features:
- Visual HP/stamina bars with block characters
- Color-coded combatant panels (green for player, red for enemy)
- Scrolling combat log with round-by-round narration
- Per-turn action keys with clear feedback
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static, RichLog

if TYPE_CHECKING:
    from portlight.app.session import GameSession


class CombatScreen(Screen):
    """Interactive combat screen with visual bars and action keybindings."""

    BINDINGS = [
        Binding("t", "combat_action('thrust')", "Thrust", priority=True),
        Binding("z", "combat_action('slash')", "Slash", priority=True),
        Binding("x", "combat_action('parry')", "Parry", priority=True),
        Binding("e", "combat_action('dodge')", "Dodge", priority=True),
        Binding("o", "combat_action('shoot')", "Shoot", priority=True),
        Binding("escape", "end_combat", "Leave", priority=True),
    ]

    def __init__(
        self,
        session: "GameSession",
        player_combatant,
        opponent_combatant,
        encounter,
    ) -> None:
        super().__init__()
        self.session = session
        self.player = player_combatant
        self.opponent = opponent_combatant
        self.encounter = encounter
        self._turn = 0
        self._finished = False

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Static(self._player_panel(), id="combat-you")
                yield Static(self._opponent_panel(), id="combat-enemy")
            yield RichLog(id="combat-log", wrap=True, highlight=True)
            yield Static(
                "  [bold #2a9d8f]T[/bold #2a9d8f]\u00b7Thrust  "
                "[bold #2a9d8f]Z[/bold #2a9d8f]\u00b7Slash  "
                "[bold #2a9d8f]X[/bold #2a9d8f]\u00b7Parry  "
                "[bold #2a9d8f]E[/bold #2a9d8f]\u00b7Dodge  "
                "[bold #2a9d8f]O[/bold #2a9d8f]\u00b7Shoot  "
                "[dim]Esc\u00b7Leave[/dim]",
                id="footer-bar",
            )

    def on_mount(self) -> None:
        log = self.query_one("#combat-log", RichLog)
        name = getattr(self.opponent, "name", "Opponent")
        log.write(f"[bold #e9c46a]\u2694 Combat: {self.session.world.captain.name} vs {name}[/bold #e9c46a]")
        log.write("")
        log.write("[dim]Choose your action...[/dim]")
        log.write("")

    def _player_panel(self) -> str:
        from portlight.app.tui.theme import render_bar
        p = self.player
        name = self.session.world.captain.name

        lines = [
            f"[bold #2a9d8f]\u2694 {name}[/bold #2a9d8f]",
            "",
            f"  HP  {render_bar(p.hp, p.hp_max, 10)} {p.hp}/{p.hp_max}",
            f"  STA {render_bar(p.stamina, p.stamina_max, 10)} {p.stamina}/{p.stamina_max}",
        ]
        if hasattr(p, "ammo") and p.ammo > 0:
            lines.append(f"  Ammo: {p.ammo}")
        if hasattr(p, "style_name") and p.style_name:
            lines.append(f"  Style: [italic]{p.style_name}[/italic]")
        return "\n".join(lines)

    def _opponent_panel(self) -> str:
        from portlight.app.tui.theme import render_bar
        o = self.opponent
        name = getattr(o, "name", "Opponent")

        lines = [
            f"[bold #e76f51]\u2620 {name}[/bold #e76f51]",
            "",
            f"  HP  {render_bar(o.hp, o.hp_max, 10)} {o.hp}/{o.hp_max}",
            f"  STA {render_bar(o.stamina, o.stamina_max, 10)} {o.stamina}/{o.stamina_max}",
        ]
        if hasattr(o, "style_name") and o.style_name:
            lines.append(f"  Style: [italic]{o.style_name}[/italic]")
        return "\n".join(lines)

    def _refresh_panels(self) -> None:
        self.query_one("#combat-you", Static).update(self._player_panel())
        self.query_one("#combat-enemy", Static).update(self._opponent_panel())

    def action_combat_action(self, action: str) -> None:
        if self._finished:
            return

        self._turn += 1
        log = self.query_one("#combat-log", RichLog)

        try:
            from portlight.engine.combat import resolve_combat_round
            round_data = resolve_combat_round(
                self.player, self.opponent, action, self._turn
            )

            log.write(f"[bold #264653]\u2500\u2500 Round {self._turn} \u2500\u2500[/bold #264653]")
            for msg in round_data.get("messages", []):
                log.write(f"  {msg}")
            log.write("")

            self._refresh_panels()

            if self.opponent.hp <= 0:
                self._finished = True
                log.write("[bold green]\u2694 Victory! The enemy falls![/bold green]")
                self.app.notify("\u2694 Victory!", severity="information", timeout=5)
            elif self.player.hp <= 0:
                self._finished = True
                log.write("[bold red]\u2620 Defeated! You fall in combat.[/bold red]")
                self.app.notify("\u2620 Defeated!", severity="error", timeout=5)

        except Exception as e:
            log.write(f"[red]Combat error: {e}[/red]")

    def action_end_combat(self) -> None:
        self.app.pop_screen()
        self.app.refresh_views()
