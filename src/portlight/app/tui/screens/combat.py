"""Grid combat screen — ship is the unit, crew grant abilities.

Static verbs (C1): M move, T attack, A then 1–4 abilities, V defend, X retreat.
Captain bar stays visible. Log is memory; the grid carries cover/range.
Does not remap D/C/R/F — those are no-ops while this screen is up.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, RichLog, Static

from portlight.app.tui.screens.dashboard import CaptainBar

if TYPE_CHECKING:
    from portlight.app.session import GameSession
    from portlight.engine.grid_combat import CombatState, CombatAbility, Pos


ABILITY_SLOTS = 4


class CombatScreen(Screen):
    """Interactive 8×6 overlay combat. Bindings match TUI_SURFACE_SPEC §5."""

    BINDINGS = [
        Binding("m", "move", "Move", priority=True),
        Binding("t", "attack", "Attack", priority=True),
        Binding("a", "ability", "Ability", priority=True),
        Binding("v", "defend", "Defend", priority=True),
        Binding("x", "retreat", "Retreat", priority=True),
        Binding("1", "pick('1')", "1", show=False, priority=True),
        Binding("2", "pick('2')", "2", show=False, priority=True),
        Binding("3", "pick('3')", "3", show=False, priority=True),
        Binding("4", "pick('4')", "4", show=False, priority=True),
        Binding("5", "pick('5')", "5", show=False, priority=True),
        Binding("6", "pick('6')", "6", show=False, priority=True),
        Binding("7", "pick('7')", "7", show=False, priority=True),
        Binding("8", "pick('8')", "8", show=False, priority=True),
        Binding("9", "pick('9')", "9", show=False, priority=True),
        Binding("escape", "cancel_pick", "Cancel", priority=True),
    ]

    def __init__(
        self,
        session: "GameSession",
        combat: "CombatState",
        encounter: dict,
    ) -> None:
        super().__init__()
        self.session = session
        self.combat = combat
        self.encounter = encounter
        self._pick: str | None = None  # "move" | "attack" | "ability"
        self._moves: list[Pos] = []
        self._targets: list[str] = []
        self._logged = 0
        self._finished = False

    def compose(self) -> ComposeResult:
        yield CaptainBar(self.session)
        with Horizontal():
            with Vertical():
                yield Static("", id="combat-grid")
                yield Static("", id="combat-status")
            yield RichLog(id="combat-log", wrap=True, highlight=True, markup=True)
        yield Static("", id="combat-actions")
        yield Footer()

    def on_mount(self) -> None:
        title = self.encounter.get("archetype", "combat").replace("_", " ").title()
        log = self.query_one("#combat-log", RichLog)
        log.write(f"[bold #e05050]Interdiction — {title}[/bold #e05050]")
        log.write("[dim]Ship is the unit. Crew grant the abilities.[/dim]")
        self._drain_log()
        self._refresh()
        self._run_until_player()

    # ------------------------------------------------------------------ HUD

    def _refresh(self) -> None:
        from portlight.app.sf_views import _render_grid, _bar
        from portlight.app.sf_views import C_GREEN, C_RED, C_DIM
        from rich.text import Text
        from rich.console import Group

        self.query_one("#combat-grid", Static).update(_render_grid(self.combat))

        parts = []
        current = self.combat.current_actor
        turn = Text()
        turn.append(f"Turn {self.combat.turn}", style="bold")
        if current:
            side = "YOUR TURN" if current.team.value == "player" else "ENEMY TURN"
            style = C_GREEN if current.team.value == "player" else C_RED
            turn.append(f"  │  {side}: {current.name}", style=style)
            turn.append(
                f"  │  AP {current.actions_remaining}/{current.actions_per_turn}"
            )
        parts.append(turn)

        for c in self.combat.combatants.values():
            if not c.alive:
                continue
            row = Text()
            style = C_GREEN if c.team.value == "player" else C_RED
            row.append(f"{c.name}  ", style=style)
            row.append("HP ")
            row.append_text(_bar(c.hp, c.hp_max, 8))
            row.append(f" {c.hp}/{c.hp_max}")
            if c.shield_max > 0:
                row.append("  Sh ")
                row.append_text(_bar(c.shield, c.shield_max, 5))
                row.append(f" {c.shield}")
            if c.retreating:
                row.append(f"  RETREAT {c.retreat_progress}/2", style="yellow")
            parts.append(row)
        parts.append(Text("# asteroid  ~ cover  ≈ nebula  N you  E enemy", style=C_DIM))
        self.query_one("#combat-status", Static).update(Group(*parts))
        self.query_one("#combat-actions", Static).update(self._action_strip())
        bar = self.query_one("#captain-bar", CaptainBar)
        bar.refresh_status()

    def _action_strip(self) -> str:
        if self._finished:
            return "[dim]Combat resolved.[/dim]"
        if self._pick == "move":
            bits = [
                f"[cyan]{i}[/cyan] ({p.x},{p.y})"
                for i, p in enumerate(self._moves[:9], 1)
            ]
            return (
                "[bold #f0c040]Move[/bold #f0c040]  "
                + "  ".join(bits)
                + "  [dim]Esc cancel[/dim]"
            )
        if self._pick == "attack":
            names = []
            for i, tid in enumerate(self._targets[:9], 1):
                t = self.combat.combatants[tid]
                names.append(f"[cyan]{i}[/cyan] {t.name}")
            return (
                "[bold #f0c040]Attack[/bold #f0c040]  "
                + "  ".join(names)
                + "  [dim]Esc cancel[/dim]"
            )
        if self._pick == "ability":
            return self._ability_strip(picking=True)
        return (
            f"{self._ability_strip(picking=False)}  "
            "[bold cyan]M[/bold cyan]·Move  "
            "[bold cyan]T[/bold cyan]·Attack  "
            "[bold cyan]V[/bold cyan]·Defend  "
            "[bold yellow]X[/bold yellow]·Retreat"
        )

    def _ability_strip(self, picking: bool) -> str:
        slots = self._slots()
        bits = []
        for i, slot in enumerate(slots, 1):
            if slot["ability"] is None:
                bits.append(f"[dim]{i} — no crew[/dim]")
            elif slot["available"]:
                ab = slot["ability"]
                src = f" — {ab.crew_source}" if ab.crew_source else ""
                bits.append(f"[bold cyan]{i}[/bold cyan] {ab.name}{src}")
            else:
                bits.append(f"[dim]{i} {slot['label']} — {slot['reason']}[/dim]")
        prefix = (
            "[bold #f0c040]Ability[/bold #f0c040]  "
            if picking
            else "[bold cyan]A[/bold cyan]·"
        )
        return prefix + "  ".join(bits)

    def _slots(self) -> list[dict]:
        from portlight.engine.grid_combat import get_available_abilities

        player = next((c for c in self.combat.player_ships()), None)
        slots: list[dict] = []
        if player is None:
            return [
                {"ability": None, "available": False, "label": "", "reason": "no ship"}
            ] * ABILITY_SLOTS

        available = {a.id: a for a in get_available_abilities(self.combat, player.id)}
        for ab in player.abilities[:ABILITY_SLOTS]:
            if ab.id in available and player.actions_remaining >= ab.action_cost:
                slots.append(
                    {"ability": ab, "available": True, "label": ab.name, "reason": ""}
                )
            else:
                cd = player.ability_cooldowns.get(ab.id, 0)
                if cd > 0:
                    reason = f"cooldown {cd}"
                elif ab.degraded and player.actions_remaining < ab.action_cost:
                    reason = "injured, no AP"
                elif player.actions_remaining < ab.action_cost:
                    reason = "no AP"
                elif ab.degraded:
                    reason = (
                        f"{ab.crew_source} injured" if ab.crew_source else "injured"
                    )
                else:
                    reason = "unavailable"
                slots.append(
                    {
                        "ability": ab,
                        "available": False,
                        "label": ab.name,
                        "reason": reason,
                    }
                )
        while len(slots) < ABILITY_SLOTS:
            slots.append(
                {"ability": None, "available": False, "label": "", "reason": "no crew"}
            )
        return slots

    # ------------------------------------------------------------------ log / turns

    def _drain_log(self) -> None:
        log = self.query_one("#combat-log", RichLog)
        events = self.combat.events
        for ev in events[self._logged :]:
            log.write(f"  {ev.description}")
        self._logged = len(events)

    def _note(self, msg: str) -> None:
        self.query_one("#combat-log", RichLog).write(f"[dim]{msg}[/dim]")

    def _player(self):
        if self._finished or self.combat.phase.value != "active":
            return None
        current = self.combat.current_actor
        if current is None or current.team.value != "player":
            return None
        return current

    def _run_until_player(self) -> None:
        from portlight.engine.grid_combat import CombatPhase, Team, enemy_act, end_turn

        for _ in range(100):
            if self.combat.phase != CombatPhase.ACTIVE:
                self._drain_log()
                self._refresh()
                self._finish()
                return
            current = self.combat.current_actor
            if current is None:
                break
            if current.team == Team.PLAYER:
                if current.actions_remaining <= 0:
                    end_turn(self.combat)
                    self._drain_log()
                    continue
                self._drain_log()
                self._refresh()
                return
            enemy_act(self.combat, current.id)
            end_turn(self.combat)
            self._drain_log()
        self._drain_log()
        self._refresh()
        if self.combat.phase.value != "active":
            self._finish()

    def _after_player(self) -> None:
        from portlight.engine.grid_combat import end_turn

        self._pick = None
        self._drain_log()
        actor = self._player()
        if actor is not None and actor.actions_remaining > 0:
            self._refresh()
            return
        if self.combat.phase.value == "active":
            end_turn(self.combat)
        self._run_until_player()

    def _finish(self) -> None:
        from portlight.engine.sf_campaign import finish_combat, resolve_transit
        from portlight.content.star_freight import SLICE_STATIONS

        if self._finished:
            return
        self._finished = True
        state = self.session.sf_campaign
        result = finish_combat(state, self.combat, self.encounter)
        dest = ""
        if state.in_transit:
            arrive = resolve_transit(state)
            if not arrive.get("error"):
                st = SLICE_STATIONS.get(state.current_station)
                dest = st.name if st else state.current_station
        self.session._save()

        # C3: one contrastive toast, then the writeback overlay (not a reset).
        from portlight.app.sf_views import contrastive_aftermath_line

        line = contrastive_aftermath_line(result, state)
        if dest:
            line += f"; docked {dest}"
        self.app.notify(line, timeout=8)

        from portlight.app.tui.screens.aftermath import AftermathScreen

        # Replace the grid with the aftermath overlay so it pops back to the
        # dashboard, not onto a dead combat screen.
        self.app.switch_screen(AftermathScreen(self.session, result))
        if hasattr(self.app, "refresh_views"):
            self.app.refresh_views()

    # ------------------------------------------------------------------ actions

    def action_cancel_pick(self) -> None:
        if self._pick:
            self._pick = None
            self._refresh()
            return
        self._note("X retreats. Esc only cancels a pick.")

    def action_move(self) -> None:
        from portlight.engine.grid_combat import get_valid_moves

        player = self._player()
        if player is None:
            return
        moves = get_valid_moves(self.combat, player.id)
        if not moves:
            self._note("No legal moves.")
            return
        if len(moves) == 1:
            self._do_move(moves[0])
            return
        self._pick = "move"
        self._moves = moves[:9]
        self._refresh()

    def action_attack(self) -> None:
        from portlight.engine.grid_combat import get_valid_targets

        player = self._player()
        if player is None:
            return
        targets = get_valid_targets(self.combat, player.id)
        if not targets:
            self._note("No target in range / line of sight.")
            return
        if len(targets) == 1:
            self._do_attack(targets[0])
            return
        self._pick = "attack"
        self._targets = targets[:9]
        self._refresh()

    def action_ability(self) -> None:
        if self._player() is None:
            return
        self._pick = "ability"
        self._refresh()

    def action_defend(self) -> None:
        from portlight.engine.grid_combat import action_defend

        player = self._player()
        if player is None:
            return
        action_defend(self.combat, player.id)
        self._after_player()

    def action_retreat(self) -> None:
        from portlight.engine.grid_combat import action_retreat

        player = self._player()
        if player is None:
            return
        action_retreat(self.combat, player.id)
        self._after_player()

    def action_pick(self, digit: str) -> None:
        idx = int(digit) - 1
        if self._pick == "move":
            if 0 <= idx < len(self._moves):
                self._do_move(self._moves[idx])
            return
        if self._pick == "attack":
            if 0 <= idx < len(self._targets):
                self._do_attack(self._targets[idx])
            return
        if self._pick == "ability":
            slots = self._slots()
            if 0 <= idx < len(slots):
                slot = slots[idx]
                if not slot["available"] or slot["ability"] is None:
                    self._note(slot["reason"] or "no crew")
                    return
                self._do_ability(slot["ability"])
            return

    def _do_move(self, pos: "Pos") -> None:
        from portlight.engine.grid_combat import action_move

        player = self._player()
        if player is None:
            return
        action_move(self.combat, player.id, pos)
        self._after_player()

    def _do_attack(self, target_id: str) -> None:
        from portlight.engine.grid_combat import action_attack

        player = self._player()
        if player is None:
            return
        action_attack(self.combat, player.id, target_id)
        self._after_player()

    def _do_ability(self, ab: "CombatAbility") -> None:
        from portlight.engine.grid_combat import action_ability, get_valid_targets

        player = self._player()
        if player is None:
            return
        target = player.id if ab.effect_type == "heal" else ""
        if ab.effect_type == "damage":
            targets = get_valid_targets(self.combat, player.id)
            if not targets:
                self._note("No target for that ability.")
                return
            target = targets[0]
        action_ability(self.combat, player.id, ab.id, target)
        self._after_player()
