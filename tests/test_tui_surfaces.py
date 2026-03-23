"""TUI surface tests — Phase 9B.

Validates that every Star Freight screen renders without error and
contains the information the TUI Surface Spec requires.

These are not visual tests. They verify that:
- Screens render from real campaign state
- Required information is present in the output
- Crew dependency is visible at point of use
- Cultural gates are surfaced
- After-action shows all state deltas
"""

from rich.console import Console

from portlight.app.sf_views import (
    captains_view,
    crew_screen,
    after_action_summary,
    combat_screen,
    journal_screen,
    dashboard,
    station_screen,
    routes_screen,
    market_screen,
    faction_screen,
)
from portlight.engine.sf_campaign import (
    CampaignState,
    dock_at_station,
    travel_to,
    execute_trade,
    run_combat,
)
from portlight.engine.crew import (
    recruit,
    active_crew,
    injure,
    CrewStatus,
)
from portlight.engine.grid_combat import (
    CombatPhase,
    CombatResult,
    CombatEvent,
    Pos,
    Team,
    Combatant,
    CombatAbility,
    init_combat,
    start_turn,
)
from portlight.content.star_freight import (
    create_thal,
    create_varek,
    SLICE_STATIONS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_state() -> CampaignState:
    state = CampaignState()
    recruit(state.crew, create_thal())
    recruit(state.crew, create_varek())
    return state


def render_to_string(renderable) -> str:
    """Render a Rich object to plain text for assertions."""
    console = Console(width=120, force_terminal=True, no_color=True)
    with console.capture() as capture:
        console.print(renderable)
    return capture.get()


# ---------------------------------------------------------------------------
# 1. Captain's View
# ---------------------------------------------------------------------------

class TestCaptainsView:
    def test_renders_without_error(self):
        state = fresh_state()
        output = render_to_string(captains_view(state))
        assert len(output) > 0

    def test_shows_credits(self):
        state = fresh_state()
        output = render_to_string(captains_view(state))
        assert "500" in output  # starting credits

    def test_shows_hull(self):
        state = fresh_state()
        output = render_to_string(captains_view(state))
        assert "1800" in output or "Hull" in output

    def test_shows_fuel(self):
        state = fresh_state()
        output = render_to_string(captains_view(state))
        assert "Fuel" in output or "8d" in output

    def test_shows_crew_fitness(self):
        state = fresh_state()
        output = render_to_string(captains_view(state))
        assert "Crew" in output and "fit" in output

    def test_shows_day(self):
        state = fresh_state()
        output = render_to_string(captains_view(state))
        assert "Day" in output

    def test_shows_injured_crew_alert(self):
        state = fresh_state()
        injure(state.crew.members[0], 5)
        output = render_to_string(captains_view(state))
        assert "injured" in output.lower()


# ---------------------------------------------------------------------------
# 2. Crew Screen
# ---------------------------------------------------------------------------

class TestCrewScreen:
    def test_renders_without_error(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert len(output) > 0

    def test_shows_crew_names(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "Thal" in output
        assert "Varek" in output

    def test_shows_roles(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "ENGINEER" in output
        assert "GUNNER" in output

    def test_shows_civilizations(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "Keth" in output
        assert "Veshan" in output

    def test_shows_ship_abilities(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "Ship" in output
        assert "active" in output.lower() or "repair" in output.lower()

    def test_shows_cultural_contribution(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "Culture" in output or "access level" in output.lower()

    def test_shows_narrative_hooks(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "Plot" in output or "keth_medical_debt" in output

    def test_shows_injured_status(self):
        state = fresh_state()
        injure(state.crew.members[0], 5)
        output = render_to_string(crew_screen(state))
        assert "INJURED" in output
        assert "DEGRADED" in output

    def test_shows_roster_summary(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "crew slots" in output.lower() or "/6" in output

    def test_shows_monthly_cost(self):
        state = fresh_state()
        output = render_to_string(crew_screen(state))
        assert "Monthly" in output or "cost" in output.lower()


# ---------------------------------------------------------------------------
# 3. After-Action Summary
# ---------------------------------------------------------------------------

class TestAfterAction:
    def test_renders_victory(self):
        state = fresh_state()
        result = CombatResult(
            outcome=CombatPhase.VICTORY,
            turns_taken=5,
            player_hull_remaining=1500,
            player_hull_max=2000,
            player_shield_remaining=100,
            enemy_destroyed=True,
            hull_damage_taken=300,
            shield_damage_taken=100,
            crew_injuries=[],
            cargo_lost=[],
            reputation_delta={"reach.ironjaw": -5, "compact": 2},
            credits_gained=200,
            consequence_tags=["combat_victory"],
        )
        output = render_to_string(after_action_summary(result, state))
        assert "VICTORY" in output
        assert "200" in output  # credits
        assert "300" in output  # hull damage

    def test_renders_retreat_with_cargo_loss(self):
        state = fresh_state()
        state.ship_cargo = ["compact_alloys"]
        result = CombatResult(
            outcome=CombatPhase.RETREAT,
            turns_taken=3,
            player_hull_remaining=1600,
            player_hull_max=2000,
            player_shield_remaining=200,
            enemy_destroyed=False,
            hull_damage_taken=200,
            shield_damage_taken=50,
            crew_injuries=[],
            cargo_lost=["compact_alloys"],
            reputation_delta={"compact": -1},
            credits_gained=0,
            consequence_tags=["combat_retreat"],
        )
        output = render_to_string(after_action_summary(result, state))
        assert "RETREAT" in output
        assert "Cargo lost" in output or "Alloys" in output

    def test_shows_crew_injury_consequence(self):
        state = fresh_state()
        injure(state.crew.members[1], 5)  # Varek injured
        result = CombatResult(
            outcome=CombatPhase.VICTORY,
            turns_taken=6,
            player_hull_remaining=1400,
            player_hull_max=2000,
            player_shield_remaining=50,
            enemy_destroyed=True,
            hull_damage_taken=400,
            shield_damage_taken=200,
            crew_injuries=["varek_drashan"],
            cargo_lost=[],
            reputation_delta={},
            credits_gained=150,
            consequence_tags=["combat_victory"],
        )
        output = render_to_string(after_action_summary(result, state))
        assert "Varek" in output
        assert "INJURED" in output

    def test_shows_reputation_deltas(self):
        state = fresh_state()
        result = CombatResult(
            outcome=CombatPhase.VICTORY,
            turns_taken=4,
            player_hull_remaining=1800,
            player_hull_max=2000,
            player_shield_remaining=200,
            enemy_destroyed=True,
            hull_damage_taken=200,
            shield_damage_taken=50,
            crew_injuries=[],
            cargo_lost=[],
            reputation_delta={"reach.ironjaw": -5, "compact": 2},
            credits_gained=100,
            consequence_tags=[],
        )
        output = render_to_string(after_action_summary(result, state))
        assert "reach.ironjaw" in output
        assert "compact" in output


# ---------------------------------------------------------------------------
# 4. Combat Screen
# ---------------------------------------------------------------------------

class TestCombatScreen:
    def test_renders_without_error(self):
        player = Combatant(
            id="player_ship", name="Nyx", team=Team.PLAYER, pos=Pos(1, 3),
            hp=1800, hp_max=2000, shield=200, shield_max=250,
            speed=2, base_attack_damage=150, base_attack_range=3,
            abilities=[CombatAbility(
                id="repair", name="Emergency Repair", description="",
                action_cost=1, cooldown=2, effect_type="heal", effect_value=300,
                crew_source="thal_communion",
            )],
        )
        enemy = Combatant(
            id="enemy", name="Raider", team=Team.ENEMY, pos=Pos(6, 3),
            hp=1000, hp_max=1000, shield=100, shield_max=100,
            speed=2, base_attack_damage=120, base_attack_range=3,
        )
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)
        output = render_to_string(combat_screen(state))
        assert len(output) > 0

    def test_shows_grid(self):
        player = Combatant(
            id="p", name="Nyx", team=Team.PLAYER, pos=Pos(1, 3),
            hp=1800, hp_max=2000, speed=2, base_attack_damage=150, base_attack_range=3,
        )
        enemy = Combatant(
            id="e", name="Raider", team=Team.ENEMY, pos=Pos(6, 3),
            hp=1000, hp_max=1000, speed=2, base_attack_damage=120, base_attack_range=3,
        )
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)
        output = render_to_string(combat_screen(state))
        assert "N" in output  # player marker
        assert "E" in output  # enemy marker

    def test_shows_crew_ability_source(self):
        player = Combatant(
            id="aaa_player", name="Nyx", team=Team.PLAYER, pos=Pos(1, 3),
            hp=1800, hp_max=2000, speed=3, base_attack_damage=150, base_attack_range=3,
            abilities=[CombatAbility(
                id="repair", name="Emergency Repair", description="",
                action_cost=1, cooldown=2, effect_type="heal", effect_value=300,
                crew_source="thal_communion",
            )],
        )
        enemy = Combatant(
            id="zzz_enemy", name="Raider", team=Team.ENEMY, pos=Pos(3, 3),
            hp=1000, hp_max=1000, speed=1, base_attack_damage=120, base_attack_range=3,
        )
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)
        # Player should go first (higher speed, earlier ID sort)
        output = render_to_string(combat_screen(state))
        assert "thal_communion" in output or "Emergency Repair" in output


# ---------------------------------------------------------------------------
# 5. Journal Screen
# ---------------------------------------------------------------------------

class TestJournalScreen:
    def test_renders_empty(self):
        state = fresh_state()
        output = render_to_string(journal_screen(state))
        assert "No active" in output or "Journal" in output

    def test_renders_with_thread(self):
        state = fresh_state()
        from portlight.engine.investigation import discover_fragment, get_medical_cargo_fragments
        frag = get_medical_cargo_fragments()["med_dock_rumor"]
        frag.day_acquired = 10
        discover_fragment(state.investigation, "medical_cargo", frag)

        output = render_to_string(journal_screen(state))
        assert "Medical Shipment" in output
        assert "RUMOR" in output or "rumor" in output


# ---------------------------------------------------------------------------
# 6. Dashboard
# ---------------------------------------------------------------------------

class TestDashboard:
    def test_renders_without_error(self):
        state = fresh_state()
        output = render_to_string(dashboard(state))
        assert "Dashboard" in output

    def test_shows_pressure(self):
        state = fresh_state()
        output = render_to_string(dashboard(state))
        assert "Credits" in output or "500" in output
        assert "Fuel" in output or "Monthly" in output

    def test_shows_crew_summary(self):
        state = fresh_state()
        output = render_to_string(dashboard(state))
        assert "Thal" in output
        assert "Varek" in output


# ---------------------------------------------------------------------------
# 7. Station, Routes, Market, Faction
# ---------------------------------------------------------------------------

class TestWorldScreens:
    def test_station_renders(self):
        state = fresh_state()
        output = render_to_string(station_screen(state))
        assert "Meridian Exchange" in output or "Station" in output

    def test_routes_renders(self):
        state = fresh_state()
        output = render_to_string(routes_screen(state))
        assert "Routes" in output

    def test_routes_shows_danger(self):
        state = fresh_state()
        output = render_to_string(routes_screen(state))
        # Should have danger indicators
        assert "Danger" in output or "☠" in output or "✓" in output

    def test_market_renders(self):
        state = fresh_state()
        output = render_to_string(market_screen(state))
        assert "Market" in output

    def test_market_shows_access(self):
        state = fresh_state()
        output = render_to_string(market_screen(state))
        assert "Access" in output

    def test_faction_renders(self):
        state = fresh_state()
        output = render_to_string(faction_screen(state))
        assert "compact" in output or "Faction" in output


# ---------------------------------------------------------------------------
# 8. Integration: all screens render from one campaign state
# ---------------------------------------------------------------------------

class TestAllScreensRender:
    def test_every_screen_renders_from_fresh_state(self):
        """THE SURFACE TEST: Every screen must render without error
        from a real campaign state."""
        state = fresh_state()
        dock_at_station(state, "meridian_exchange")

        screens = {
            "captains_view": captains_view(state),
            "crew_screen": crew_screen(state),
            "dashboard": dashboard(state),
            "station_screen": station_screen(state),
            "routes_screen": routes_screen(state),
            "market_screen": market_screen(state),
            "faction_screen": faction_screen(state),
            "journal_screen": journal_screen(state),
        }

        for name, renderable in screens.items():
            output = render_to_string(renderable)
            assert len(output) > 10, f"{name} rendered empty"
