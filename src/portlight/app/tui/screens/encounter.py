"""Encounter screen -- continuous multi-phase combat experience.

Flows through: approach -> naval -> boarding -> duel -> victory/defeat.
A single RichLog persists across all phases as a scrollable encounter journal.
Panel visibility toggles per phase. Action keys change per phase.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static, RichLog

if TYPE_CHECKING:
    from portlight.app.session import GameSession
    from portlight.engine.models import EncounterState


# Phase-specific action bar text
_APPROACH_ACTIONS = (
    "  [bold #2a9d8f]N[/bold #2a9d8f].Negotiate  "
    "[bold #e76f51]F[/bold #e76f51].Flee  "
    "[bold #e9c46a]G[/bold #e9c46a].Fight"
)
_NAVAL_ACTIONS = (
    "  [bold #2a9d8f]B[/bold #2a9d8f].Broadside  "
    "[bold #2a9d8f]C[/bold #2a9d8f].Close  "
    "[bold #2a9d8f]E[/bold #2a9d8f].Evade  "
    "[bold #2a9d8f]R[/bold #2a9d8f].Rake  "
    "[bold #e76f51]F[/bold #e76f51].Flee"
)
_DUEL_ACTIONS = (
    "  [bold #2a9d8f]T[/bold #2a9d8f].Thrust  "
    "[bold #2a9d8f]Z[/bold #2a9d8f].Slash  "
    "[bold #2a9d8f]X[/bold #2a9d8f].Parry  "
    "[bold #2a9d8f]E[/bold #2a9d8f].Dodge  "
    "[bold #2a9d8f]O[/bold #2a9d8f].Shoot  "
    "[bold #2a9d8f]W[/bold #2a9d8f].Throw"
)
_VICTORY_ACTIONS = (
    "  [bold #2a9d8f]S[/bold #2a9d8f].Spare  "
    "[bold #e76f51]A[/bold #e76f51].Take All  "
    "[dim]Esc.Leave[/dim]"
)
_DEFEAT_ACTIONS = "  [dim]Esc.Leave[/dim]"


class EncounterScreen(Screen):
    """Multi-phase pirate encounter -- approach, naval, boarding, duel, resolution."""

    BINDINGS = [
        # Keys not bound by the App — handled directly by the Screen.
        # Keys that conflict with App bindings (g/f/b/c/r/s/a/e) are
        # intercepted by App.action_* methods which delegate to this screen
        # via action_encounter_key() when an EncounterScreen is active.
        Binding("n", "encounter_key('negotiate')", "Negotiate", priority=True),
        Binding("t", "encounter_key('thrust')", "Thrust", priority=True),
        Binding("z", "encounter_key('slash')", "Slash", priority=True),
        Binding("x", "encounter_key('parry')", "Parry", priority=True),
        Binding("o", "encounter_key('shoot')", "Shoot", priority=True),
        Binding("w", "encounter_key('throw')", "Throw", priority=True),
        Binding("escape", "encounter_escape", "Leave", priority=True),
    ]

    def __init__(self, session: "GameSession", encounter: "EncounterState") -> None:
        super().__init__()
        self.session = session
        self.encounter = encounter
        self._phase = encounter.phase  # approach | naval | boarding | duel | victory | defeat
        self._player_combatant = None
        self._opponent_combatant = None
        self._transitioning = False

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("", id="encounter-header")
            with Horizontal(id="ship-panels", classes="hidden"):
                yield Static("", id="ship-player")
                yield Static("", id="ship-enemy")
            with Horizontal(id="combatant-panels", classes="hidden"):
                yield Static("", id="combatant-player")
                yield Static("", id="combatant-enemy")
            yield RichLog(id="encounter-log", wrap=True, highlight=True)
            yield Static(_APPROACH_ACTIONS, id="encounter-actions")

    def on_mount(self) -> None:
        self._enter_approach()

    # ------------------------------------------------------------------
    # Key dispatcher
    # ------------------------------------------------------------------

    def action_encounter_escape(self) -> None:
        """Handle Escape key — exit only if encounter is resolved."""
        if self._phase in ("victory", "defeat", "resolved"):
            self._exit_encounter()
        else:
            self.app.notify("Resolve the encounter first!", severity="warning")

    def action_encounter_key(self, key: str) -> None:
        if self._transitioning:
            return

        phase = self._phase

        if phase == "approach":
            if key == "negotiate":
                self._handle_negotiate()
            elif key == "flee":
                self._handle_flee()
            elif key == "fight":
                self._handle_fight()
            return

        if phase == "naval":
            if key in ("broadside", "close", "evade", "rake", "flee"):
                self._handle_naval_action(key)
            return

        if phase == "duel":
            if key in ("thrust", "slash", "parry", "evade", "shoot", "throw"):
                action = "dodge" if key == "evade" else key
                self._handle_duel_action(action)
            return

        if phase == "victory":
            if key == "spare":
                self._handle_spare()
            elif key == "take_all":
                self._handle_take_all()
            return

    # ------------------------------------------------------------------
    # Approach phase
    # ------------------------------------------------------------------

    def _enter_approach(self) -> None:
        from portlight.app.combat_views import _strength_indicator
        from portlight.content.factions import FACTIONS, PIRATE_CAPTAINS

        enc = self.encounter
        faction = FACTIONS.get(enc.enemy_faction_id)
        faction_name = faction.name if faction else enc.enemy_faction_id
        captain_data = PIRATE_CAPTAINS.get(enc.enemy_captain_id)

        # Header
        header_text = (
            f"[bold red]Sails on the horizon![/bold red]\n\n"
            f"  Captain:  [bold]{enc.enemy_captain_name}[/bold]\n"
            f"  Faction:  {faction_name}\n"
            f"  Demeanor: [italic]{enc.enemy_personality}[/italic]\n"
            f"  Strength: {_strength_indicator(enc.enemy_strength)}"
        )
        self.query_one("#encounter-header", Static).update(header_text)

        # Log
        log = self.query_one("#encounter-log", RichLog)
        if captain_data:
            log.write(f"[italic]{captain_data.duel_opening}[/italic]")
        log.write("")
        log.write("[bold]What will you do?[/bold]  Negotiate, Flee, or Fight?")
        log.write("")

        # Weapon recognition
        self._check_weapon_recognition(log)

    def _check_weapon_recognition(self, log: RichLog) -> None:
        gear = self.session.captain.combat_gear
        if not gear.melee_weapon:
            return
        try:
            from portlight.engine.weapon_provenance import WeaponProvenance, check_recognition
            prov = gear.weapon_provenance.get(gear.melee_weapon)
            if not isinstance(prov, WeaponProvenance):
                return
            enc = self.encounter
            memories = self.session.world.pirates.captain_memories
            familiarity = 0
            mem = memories.get(enc.enemy_captain_id)
            if mem and hasattr(mem, "familiarity"):
                familiarity = mem.familiarity
            from portlight.content.weapons import MELEE_WEAPONS
            weapon_def = MELEE_WEAPONS.get(gear.melee_weapon)
            weapon_name = weapon_def.name if weapon_def else gear.melee_weapon
            result = check_recognition(prov, weapon_name, enc.enemy_captain_id, familiarity, self._rng())
            if result.recognized:
                log.write(f"[bold magenta]{enc.enemy_captain_name} eyes your {weapon_name} -- {result.flavor}[/bold magenta]")
                log.write("")
        except (ImportError, AttributeError, Exception):
            pass

    # ------------------------------------------------------------------
    # Approach handlers
    # ------------------------------------------------------------------

    def _handle_negotiate(self) -> None:
        from portlight.engine.encounter import resolve_negotiate
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)

        standing = {}
        if hasattr(self.session.captain, "standing"):
            standing = self.session.captain.standing.underworld_standing
        captain_type = self.session.captain.captain_type

        success, msg = resolve_negotiate(enc, standing, captain_type, self._rng())
        log.write(f"[bold]Negotiate:[/bold] {msg}")
        log.write("")

        if success:
            self._phase = "resolved"
            log.write("[green]The encounter ends peacefully.[/green]")
            self.app.notify("Encounter resolved -- safe passage.", severity="information", timeout=4)
            self._clear_pending()
            self._update_actions(_DEFEAT_ACTIONS)  # just Esc
        else:
            log.write("[yellow]Negotiation failed -- battle is joined![/yellow]")
            self._handle_fight()

    def _handle_flee(self) -> None:
        if self._phase == "naval":
            self._handle_naval_action("flee")
            return

        from portlight.engine.encounter import resolve_flee
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)
        ship = self.session.captain.ship

        escaped, damage, msg = resolve_flee(enc, ship, self._rng())
        log.write(f"[bold]Flee:[/bold] {msg}")

        if damage > 0:
            ship.hull = max(0, ship.hull - damage)

        if escaped:
            self._phase = "resolved"
            log.write("[green]You escape into open water.[/green]")
            self.app.notify("Escaped!", severity="information", timeout=4)
            self._clear_pending()
            self._update_actions(_DEFEAT_ACTIONS)
        else:
            log.write("[yellow]Can't escape -- fight![/yellow]")
            self._handle_fight()

    def _handle_fight(self) -> None:
        from portlight.engine.encounter import begin_fight
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)
        ship = self.session.captain.ship

        msg = begin_fight(enc, ship)
        self._phase = "naval"

        log.write("")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write("[bold red]NAVAL COMBAT[/bold red]")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write(f"  {msg}")
        log.write("")

        # Show ship panels
        self.query_one("#ship-panels").remove_class("hidden")
        self._refresh_ship_panels()
        self._update_actions(_NAVAL_ACTIONS)

    # ------------------------------------------------------------------
    # Naval phase
    # ------------------------------------------------------------------

    def _handle_naval_action(self, action: str) -> None:
        from portlight.engine.encounter import resolve_naval_turn
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)
        ship = self.session.captain.ship

        if action == "broadside" and ship.cannons <= 0:
            self.app.notify("No cannons! Use Close to board.", severity="warning")
            return

        result = resolve_naval_turn(enc, action, ship, self._rng())

        # Apply damage to player ship
        ship.hull = max(0, ship.hull + result["player_hull_delta"])
        ship.crew = max(0, ship.crew + result["player_crew_delta"])

        # Log the round
        log.write(f"[bold #264653]-- Naval Turn {result['turn']} --[/bold #264653]")
        log.write(f"  You: [cyan]{action}[/cyan]  Enemy: [red]{result['enemy_action']}[/red]")
        if result["player_hull_delta"] != 0:
            log.write(f"  Your hull: [red]{result['player_hull_delta']}[/red]")
        if result["enemy_hull_delta"] != 0:
            log.write(f"  Enemy hull: [green]{result['enemy_hull_delta']}[/green]")
        if result["player_crew_delta"] != 0:
            log.write(f"  Crew lost: [red]{result['player_crew_delta']}[/red]")
        if result.get("flavor"):
            log.write(f"  [italic]{result['flavor']}[/italic]")
        log.write("")

        self._refresh_ship_panels()

        # Check player defeat
        if ship.hull <= 0 or ship.crew <= 0:
            self._enter_defeat("Your ship is lost!")
            return

        # Check transitions
        if result["enemy_sunk"]:
            log.write("[bold green]Enemy ship destroyed![/bold green]")
            self.session.world.pirates.naval_victories += 1
            self._enter_victory()
        elif result["boarding_triggered"]:
            log.write("[bold yellow]Boarding threshold reached![/bold yellow]")
            self._auto_boarding()

    def _refresh_ship_panels(self) -> None:
        from portlight.app.tui.theme import render_bar
        enc = self.encounter
        ship = self.session.captain.ship

        player_text = (
            f"[bold #2a9d8f]Your Ship[/bold #2a9d8f]\n\n"
            f"  Hull  {render_bar(ship.hull, ship.hull_max, 10)} {ship.hull}/{ship.hull_max}\n"
            f"  Crew  [bold]{ship.crew}[/bold]\n"
            f"  Guns  [bold]{ship.cannons}[/bold]"
        )
        enemy_text = (
            f"[bold #e76f51]{enc.enemy_captain_name}'s Ship[/bold #e76f51]\n\n"
            f"  Hull  {render_bar(enc.enemy_ship_hull, enc.enemy_ship_hull_max, 10)} {enc.enemy_ship_hull}/{enc.enemy_ship_hull_max}\n"
            f"  Crew  [bold]{enc.enemy_ship_crew}[/bold]\n"
            f"  Guns  [bold]{enc.enemy_ship_cannons}[/bold]\n\n"
            f"  Board {render_bar(enc.boarding_progress, enc.boarding_threshold, 8)} {enc.boarding_progress}/{enc.boarding_threshold}"
        )

        self.query_one("#ship-player", Static).update(player_text)
        self.query_one("#ship-enemy", Static).update(enemy_text)

    # ------------------------------------------------------------------
    # Boarding (auto-resolve with brief pause)
    # ------------------------------------------------------------------

    def _auto_boarding(self) -> None:
        from portlight.engine.encounter import resolve_boarding_phase
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)
        ship = self.session.captain.ship

        self._transitioning = True

        result = resolve_boarding_phase(enc, ship.crew, self._rng())
        ship.crew = max(1, ship.crew - result["player_crew_lost"])

        log.write("")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write("[bold yellow]BOARDING![/bold yellow]")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write(f"  {result['flavor']}")
        log.write("")

        # Brief pause then transition to duel
        self.set_timer(1.0, self._begin_duel)

    def _begin_duel(self) -> None:
        from portlight.engine.encounter import create_duel_combatants
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)
        captain = self.session.captain
        gear = captain.combat_gear

        # Create combatants
        throwing_count = sum(gear.throwing_weapons.values()) if isinstance(gear.throwing_weapons, dict) else 0
        self._player_combatant, self._opponent_combatant = create_duel_combatants(
            enc,
            player_crew=captain.ship.crew,
            player_style=captain.active_style,
            player_injury_ids=list(captain.injuries) if hasattr(captain, "injuries") and captain.injuries else [],
            player_firearm=gear.firearm,
            player_ammo=gear.firearm_ammo,
            player_throwing=throwing_count,
            player_mechanical=gear.mechanical_weapon,
            player_mechanical_ammo=gear.mechanical_ammo,
        )

        # Apply armor/melee weapon to combatant
        if gear.armor:
            try:
                from portlight.content.weapons import ARMOR
                armor_def = ARMOR.get(gear.armor)
                if armor_def:
                    self._player_combatant.armor_dr = armor_def.damage_reduction
                    self._player_combatant.dodge_stamina_penalty = armor_def.dodge_penalty
            except ImportError:
                pass

        if gear.melee_weapon:
            self._player_combatant.melee_weapon_id = gear.melee_weapon

        # Set opponent name for display
        self._opponent_combatant.name = enc.enemy_captain_name
        self._player_combatant.name = captain.name

        self._phase = "duel"
        self._transitioning = False

        # Swap panels
        self.query_one("#ship-panels").add_class("hidden")
        self.query_one("#combatant-panels").remove_class("hidden")

        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write(f"[bold red]DUEL: {captain.name} vs {enc.enemy_captain_name}[/bold red]")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write("")

        self._refresh_combatant_panels()
        self._update_actions(_DUEL_ACTIONS)

    # ------------------------------------------------------------------
    # Duel phase
    # ------------------------------------------------------------------

    def _handle_duel_action(self, action: str) -> None:
        from portlight.engine.encounter import resolve_duel_turn
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)
        p = self._player_combatant
        o = self._opponent_combatant

        if p is None or o is None:
            return

        # Stamina check
        if p.stamina <= 0 and action not in ("parry",):
            self.app.notify("No stamina! Parry to recover.", severity="warning")
            return

        result = resolve_duel_turn(enc, action, p, o, self._rng())

        log.write(f"[bold #264653]-- Round {result.turn} --[/bold #264653]")
        log.write(f"  You: [cyan]{result.player_action}[/cyan]  Enemy: [red]{result.opponent_action}[/red]")
        if result.damage_to_opponent > 0:
            log.write(f"  You deal [green]{result.damage_to_opponent}[/green] damage!")
        if result.damage_to_player > 0:
            log.write(f"  You take [red]{result.damage_to_player}[/red] damage!")
        if result.injury_inflicted:
            log.write(f"  [bold red]Injury: {result.injury_inflicted}![/bold red]")
        if result.opponent_injury:
            log.write(f"  [bold green]Enemy injured: {result.opponent_injury}![/bold green]")
        if result.flavor:
            log.write(f"  [italic]{result.flavor}[/italic]")
        log.write("")

        self._refresh_combatant_panels()

        # Check resolution
        if o.hp <= 0 and p.hp > 0:
            log.write("[bold green]Victory! The captain falls![/bold green]")
            self._enter_victory()
        elif p.hp <= 0:
            self._enter_defeat(f"{enc.enemy_captain_name} defeats you.")
        elif o.hp <= 0 and p.hp <= 0:
            log.write("[bold yellow]Mutual defeat -- both fall.[/bold yellow]")
            self._enter_defeat("A draw. Both combatants collapse.")

    def _refresh_combatant_panels(self) -> None:
        from portlight.app.tui.theme import render_bar
        p = self._player_combatant
        o = self._opponent_combatant
        if p is None or o is None:
            return

        p_name = getattr(p, "name", "You")
        o_name = getattr(o, "name", "Enemy")

        player_text = (
            f"[bold #2a9d8f]{p_name}[/bold #2a9d8f]\n\n"
            f"  HP  {render_bar(p.hp, p.hp_max, 10)} {p.hp}/{p.hp_max}\n"
            f"  STA {render_bar(p.stamina, p.stamina_max, 10)} {p.stamina}/{p.stamina_max}"
        )
        if p.ammo > 0:
            player_text += f"\n  Ammo: {p.ammo}"
        if p.throwing_weapons > 0:
            player_text += f"\n  Throw: {p.throwing_weapons}"

        enemy_text = (
            f"[bold #e76f51]{o_name}[/bold #e76f51]\n\n"
            f"  HP  {render_bar(o.hp, o.hp_max, 10)} {o.hp}/{o.hp_max}\n"
            f"  STA {render_bar(o.stamina, o.stamina_max, 10)} {o.stamina}/{o.stamina_max}"
        )

        self.query_one("#combatant-player", Static).update(player_text)
        self.query_one("#combatant-enemy", Static).update(enemy_text)

    # ------------------------------------------------------------------
    # Victory
    # ------------------------------------------------------------------

    def _enter_victory(self) -> None:
        self._phase = "victory"
        log = self.query_one("#encounter-log", RichLog)
        log.write("")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write("[bold #e9c46a]VICTORY[/bold #e9c46a]")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write("")
        log.write("[bold]Show mercy or take everything?[/bold]")
        log.write("  [green]S - Spare[/green]: +respect, -grudge, less silver, no loot")
        log.write("  [red]A - Take All[/red]: +fear, +grudge, more silver, full loot")
        log.write("")
        self._update_actions(_VICTORY_ACTIONS)

    def _handle_spare(self) -> None:
        self._finalize_victory(spared=True)

    def _handle_take_all(self) -> None:
        self._finalize_victory(spared=False)

    def _finalize_victory(self, spared: bool) -> None:
        """Apply all victory consequences -- ported from CLI _finalize_victory."""
        enc = self.encounter
        log = self.query_one("#encounter-log", RichLog)
        captain = self.session.captain
        gear = captain.combat_gear

        # Silver reward
        if spared:
            silver_gain = 20 + enc.enemy_strength * 3
        else:
            silver_gain = 20 + enc.enemy_strength * 7
        captain.silver += silver_gain
        self.session.world.pirates.duels_won += 1

        log.write(f"[green]+{silver_gain} silver[/green]")

        # Captain memory
        try:
            from portlight.engine.captain_memory import get_or_create_memory, record_encounter
            memory = get_or_create_memory(self.session.world.pirates.captain_memories, enc.enemy_captain_id)
            record_encounter(
                memory, self.session.world.day, enc.enemy_region, "player_won",
                player_spared=spared, player_used_firearm=False,
                crew_killed=max(0, enc.enemy_ship_crew_max - enc.enemy_ship_crew),
            )
        except (ImportError, Exception):
            pass

        # Underworld standing
        try:
            from portlight.engine.underworld import record_duel_outcome
            uw_standing = captain.standing.underworld_standing
            standing_delta = record_duel_outcome(uw_standing, enc.enemy_faction_id, player_won=True, spared=spared)
            if standing_delta > 0:
                log.write(f"[green]+{standing_delta} underworld standing ({enc.enemy_faction_id})[/green]")
            elif standing_delta < 0:
                log.write(f"[red]{standing_delta} underworld standing ({enc.enemy_faction_id})[/red]")
        except (ImportError, Exception):
            pass

        # Weapon provenance
        if gear.melee_weapon:
            try:
                from portlight.engine.weapon_provenance import (
                    RELIC_COLORS, RELIC_LABELS, WeaponProvenance,
                    create_provenance, record_kill,
                )
                prov = gear.weapon_provenance.get(gear.melee_weapon)
                if not isinstance(prov, WeaponProvenance):
                    prov = create_provenance(gear.melee_weapon)
                    gear.weapon_provenance[gear.melee_weapon] = prov
                tier_change, new_epithet = record_kill(prov, enc.enemy_captain_id, enc.enemy_captain_name)
                if new_epithet:
                    log.write(f"[bold magenta]Your weapon is now known as \"{new_epithet}\"![/bold magenta]")
                if tier_change:
                    label = RELIC_LABELS.get(tier_change, tier_change)
                    color = RELIC_COLORS.get(tier_change, "white")
                    log.write(f"[{color}]Weapon reached {label} status -- {prov.kills} kills.[/{color}]")
            except (ImportError, Exception):
                pass

        # Loot
        try:
            from portlight.engine.loot import apply_loot, roll_loot
            loot = roll_loot(enc.enemy_strength, enc.enemy_captain_id, self._rng())
            if loot and not spared:
                messages = apply_loot(captain, loot)
                for msg in messages:
                    log.write(f"  [green]{msg}[/green]")
            elif spared:
                log.write("[dim]You leave their possessions untouched.[/dim]")
        except (ImportError, Exception):
            pass

        # Companion morale
        try:
            from portlight.engine.companion_engine import CompanionState, PartyState, apply_morale_trigger, check_departures
            party_data = captain.party
            if isinstance(party_data, dict) and party_data.get("companions"):
                companions = [
                    CompanionState(
                        companion_id=c["companion_id"], role_id=c["role_id"],
                        morale=c.get("morale", 70), joined_day=c.get("joined_day", 0),
                        personality=c.get("personality", "pragmatic"),
                    ) for c in party_data["companions"]
                ]
                party = PartyState(
                    companions=companions,
                    max_size=party_data.get("max_size", 2),
                    departed=party_data.get("departed", []),
                )
                trigger = "spared_enemy" if spared else "took_all"
                reactions = apply_morale_trigger(party, trigger)
                for _comp_id, _delta, flavor in reactions:
                    log.write(f"  [dim]{flavor}[/dim]")
                departures = check_departures(party)
                for dep in departures:
                    log.write(f"[bold red]{dep.companion_name} leaves: \"{dep.departure_line}\"[/bold red]")
                captain.party = {
                    "companions": [
                        {"companion_id": c.companion_id, "role_id": c.role_id,
                         "morale": c.morale, "joined_day": c.joined_day, "personality": c.personality}
                        for c in party.companions
                    ],
                    "max_size": party.max_size, "departed": party.departed,
                }
        except (ImportError, Exception):
            pass

        # Captain flavor
        try:
            from portlight.content.factions import PIRATE_CAPTAINS
            captain_data = PIRATE_CAPTAINS.get(enc.enemy_captain_id)
            if captain_data:
                flavor = captain_data.duel_defeat if spared else captain_data.duel_victory
                log.write(f"\n[italic]{flavor}[/italic]")
        except (ImportError, Exception):
            pass

        log.write("")
        choice = "showed mercy" if spared else "took everything"
        log.write(f"[dim]You {choice}. The encounter is over.[/dim]")

        # Weapon degradation
        try:
            from portlight.engine.weapon_quality import tick_melee_degradation, tick_firearm_degradation
            if gear.melee_weapon:
                tick_melee_degradation(gear, gear.melee_weapon)
            if gear.firearm and self._player_combatant and self._player_combatant.ammo < gear.firearm_ammo:
                tick_firearm_degradation(gear, gear.firearm)
                gear.firearm_ammo = self._player_combatant.ammo
        except (ImportError, Exception):
            pass

        self._phase = "resolved"
        self._clear_pending()
        self.session._save()
        self._update_actions(_DEFEAT_ACTIONS)
        self.app.notify("Encounter resolved.", severity="information", timeout=4)

    # ------------------------------------------------------------------
    # Defeat
    # ------------------------------------------------------------------

    def _enter_defeat(self, message: str) -> None:
        self._phase = "defeat"
        log = self.query_one("#encounter-log", RichLog)
        log.write("")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write("[bold red]DEFEAT[/bold red]")
        log.write(f"[bold #264653]{'=' * 40}[/bold #264653]")
        log.write(f"  {message}")
        log.write("")

        # Record defeat
        self.session.world.pirates.duels_lost += 1
        try:
            from portlight.engine.captain_memory import get_or_create_memory, record_encounter
            enc = self.encounter
            memory = get_or_create_memory(self.session.world.pirates.captain_memories, enc.enemy_captain_id)
            record_encounter(memory, self.session.world.day, enc.enemy_region, "player_lost")
        except (ImportError, Exception):
            pass

        self._clear_pending()
        self.session._save()
        self._update_actions(_DEFEAT_ACTIONS)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _rng(self) -> random.Random:
        seed = self.session.world.seed + self.session.world.day * 1000
        seed += self.encounter.naval_turns + self.encounter.duel_turns
        return random.Random(seed)

    def _update_actions(self, text: str) -> None:
        self.query_one("#encounter-actions", Static).update(text)

    def _clear_pending(self) -> None:
        """Clear encounter from world state so voyage can resume."""
        self.session.world.pirates.pending_duel = None
        self.session.world.pirates.encounter_phase = ""
        self.session.world.pirates.encounter_state = {}

    def _exit_encounter(self) -> None:
        self.session._save()
        self.app.pop_screen()
        self.app.refresh_views()
