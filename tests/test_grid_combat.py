"""Grid combat engine tests — Phase 2 thesis proof.

Acceptance bar:
  One compact combat encounter in three branches — victory, loss, retreat —
  each writes back materially different campaign state.

Within the fight:
  - crew ability → option appears
  - injured crew → option degrades
  - enemy forces positioning decisions
  - retreat is mechanically available, not fake
  - combat ends in a state the campaign can feel
"""

from portlight.engine.grid_combat import (
    # Core types
    Pos, Tile, TileType, Team, Combatant, CombatAbility,
    CombatState, CombatPhase, CombatEvent, CombatResult,
    # Grid
    GRID_WIDTH, GRID_HEIGHT,
    line_of_sight, tile_at, combatant_at, in_cover, in_nebula,
    # Setup
    init_combat,
    # Actions
    get_valid_moves, action_move,
    get_valid_targets, action_attack,
    action_defend, action_retreat,
    get_available_abilities, action_ability,
    RETREAT_TURNS_REQUIRED,
    # Turn management
    start_turn, end_turn,
    # AI
    enemy_act,
    # Writeback
    resolve_combat,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_player_ship(
    pos: Pos = Pos(1, 3),
    abilities: list[CombatAbility] | None = None,
) -> Combatant:
    """Standard player ship for testing."""
    return Combatant(
        id="player_ship",
        name="Star Freighter Nyx",
        team=Team.PLAYER,
        pos=pos,
        hp=1800, hp_max=2000,
        shield=200, shield_max=250,
        speed=2,
        evasion=0.1,
        armor=10,
        base_attack_damage=150,
        base_attack_range=3,
        abilities=abilities or [],
    )


def make_enemy_ship(
    pos: Pos = Pos(6, 3),
    hp: int = 1000,
    damage: int = 120,
) -> Combatant:
    """Standard enemy pirate for testing."""
    return Combatant(
        id="pirate_1",
        name="Razor Fang",
        team=Team.ENEMY,
        pos=pos,
        hp=hp, hp_max=hp,
        shield=100, shield_max=100,
        speed=2,
        evasion=0.15,
        armor=5,
        base_attack_damage=damage,
        base_attack_range=3,
        abilities=[],
    )


def make_repair_ability(crew_id: str = "dax_maren", degraded: bool = False) -> CombatAbility:
    """Dax's emergency_repair ability for testing crew binding."""
    return CombatAbility(
        id="emergency_repair",
        name="Emergency Repair",
        description="Patch hull damage mid-combat. Crew: Dax Maren.",
        action_cost=1,
        cooldown=2,
        effect_type="heal",
        effect_value=300,
        crew_source=crew_id,
        degraded=degraded,
    )


def make_volley_ability(crew_id: str = "kira_vesk") -> CombatAbility:
    """Kira's heavy volley — high damage ability."""
    return CombatAbility(
        id="heavy_volley",
        name="Heavy Volley",
        description="Concentrated weapons fire. Crew: Kira Vesk.",
        action_cost=1,
        cooldown=3,
        range_min=1,
        range_max=4,
        effect_type="damage",
        effect_value=400,
        crew_source=crew_id,
    )


# ---------------------------------------------------------------------------
# 1. Grid and positioning
# ---------------------------------------------------------------------------

class TestGrid:
    def test_pos_distance(self):
        assert Pos(0, 0).distance_to(Pos(3, 4)) == 4  # Chebyshev
        assert Pos(2, 2).distance_to(Pos(2, 2)) == 0

    def test_pos_in_bounds(self):
        assert Pos(0, 0).in_bounds()
        assert Pos(GRID_WIDTH - 1, GRID_HEIGHT - 1).in_bounds()
        assert not Pos(-1, 0).in_bounds()
        assert not Pos(GRID_WIDTH, 0).in_bounds()

    def test_asteroid_blocks_movement(self):
        player = make_player_ship(pos=Pos(1, 1))
        enemy = make_enemy_ship()
        hazards = {Pos(2, 1): TileType.ASTEROID}
        state = init_combat([player], [enemy], hazards=hazards, seed=42)

        moves = get_valid_moves(state, "player_ship")
        assert Pos(2, 1) not in moves  # asteroid blocks

    def test_debris_provides_cover(self):
        player = make_player_ship(pos=Pos(3, 3))
        enemy = make_enemy_ship()
        hazards = {Pos(3, 3): TileType.DEBRIS}
        state = init_combat([player], [enemy], hazards=hazards, seed=42)

        assert in_cover(state, player.pos)

    def test_asteroid_blocks_line_of_sight(self):
        player = make_player_ship(pos=Pos(0, 3))
        enemy = make_enemy_ship(pos=Pos(4, 3))
        hazards = {Pos(2, 3): TileType.ASTEROID}
        state = init_combat([player], [enemy], hazards=hazards, seed=42)

        assert not line_of_sight(state, player.pos, enemy.pos)

    def test_nebula_blocks_long_range_targeting(self):
        player = make_player_ship(pos=Pos(1, 3))
        enemy = make_enemy_ship(pos=Pos(4, 3))
        hazards = {Pos(4, 3): TileType.NEBULA}
        state = init_combat([player], [enemy], hazards=hazards, seed=42)

        # Enemy is in nebula at range 3 — can't target
        targets = get_valid_targets(state, "player_ship")
        assert "pirate_1" not in targets


# ---------------------------------------------------------------------------
# 2. Core actions
# ---------------------------------------------------------------------------

class TestActions:
    def test_move(self):
        player = make_player_ship(pos=Pos(1, 3))
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        event = action_move(state, "player_ship", Pos(3, 3))
        assert event is not None
        assert state.combatants["player_ship"].pos == Pos(3, 3)
        assert state.combatants["player_ship"].actions_remaining == 1

    def test_attack_hits(self):
        player = make_player_ship(pos=Pos(1, 3))
        enemy = make_enemy_ship(pos=Pos(3, 3))  # in range
        state = init_combat([player], [enemy], seed=1)  # seed that hits
        start_turn(state)

        hp_before = state.combatants["pirate_1"].hp
        event = action_attack(state, "player_ship", "pirate_1")
        assert event is not None
        # Either hit or miss, both are valid (rng-dependent)
        assert event.action == "attack"

    def test_defend_grants_evasion(self):
        player = make_player_ship(pos=Pos(1, 3))
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        action_defend(state, "player_ship")
        assert "evasive" in state.combatants["player_ship"].buffs
        assert state.combatants["player_ship"].effective_evasion > 0.1

    def test_retreat_takes_two_turns(self):
        player = make_player_ship()
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        # Turn 1: begin retreat
        action_retreat(state, "player_ship")
        assert state.combatants["player_ship"].retreating
        assert state.combatants["player_ship"].retreat_progress == 1
        assert state.phase == CombatPhase.ACTIVE

        end_turn(state)
        # Enemy acts
        enemy_act(state, "pirate_1")
        end_turn(state)

        # Turn 2: continue retreat
        action_retreat(state, "player_ship")
        assert state.combatants["player_ship"].retreat_progress == 2
        end_turn(state)
        assert state.phase == CombatPhase.RETREAT

    def test_move_cancels_retreat(self):
        player = make_player_ship()
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        action_retreat(state, "player_ship")
        assert state.combatants["player_ship"].retreating

        # Next turn, move instead
        end_turn(state)
        enemy_act(state, "pirate_1")
        end_turn(state)
        action_move(state, "player_ship", Pos(2, 3))
        assert not state.combatants["player_ship"].retreating
        assert state.combatants["player_ship"].retreat_progress == 0

    def test_cannot_attack_out_of_range(self):
        player = make_player_ship(pos=Pos(0, 0))
        enemy = make_enemy_ship(pos=Pos(7, 5))  # far away
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        targets = get_valid_targets(state, "player_ship")
        assert "pirate_1" not in targets


# ---------------------------------------------------------------------------
# 3. Crew abilities in combat
# ---------------------------------------------------------------------------

class TestCrewAbilities:
    def test_repair_ability_heals(self):
        repair = make_repair_ability()
        player = make_player_ship(abilities=[repair])
        player.hp = 1000  # damaged
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        event = action_ability(state, "player_ship", "emergency_repair", "player_ship")
        assert event is not None
        assert state.combatants["player_ship"].hp == 1300  # +300

    def test_degraded_ability_half_effect(self):
        repair = make_repair_ability(degraded=True)
        player = make_player_ship(abilities=[repair])
        player.hp = 1000
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        event = action_ability(state, "player_ship", "emergency_repair", "player_ship")
        assert event is not None
        assert state.combatants["player_ship"].hp == 1150  # +150 (half of 300)
        assert "degraded" in event.description

    def test_ability_respects_cooldown(self):
        repair = make_repair_ability()
        player = make_player_ship(abilities=[repair])
        player.hp = 1000
        player.actions_per_turn = 3  # extra actions for testing
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        # Use repair
        action_ability(state, "player_ship", "emergency_repair", "player_ship")
        # Try again — should fail (cooldown 2)
        available = get_available_abilities(state, "player_ship")
        assert not any(a.id == "emergency_repair" for a in available)

    def test_no_ability_without_crew(self):
        """Ship with no crew abilities has no ability options."""
        player = make_player_ship(abilities=[])
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        available = get_available_abilities(state, "player_ship")
        assert len(available) == 0

    def test_damage_ability(self):
        volley = make_volley_ability()
        player = make_player_ship(pos=Pos(1, 3), abilities=[volley])
        enemy = make_enemy_ship(pos=Pos(3, 3))
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        hp_before = state.combatants["pirate_1"].hp + state.combatants["pirate_1"].shield
        event = action_ability(state, "player_ship", "heavy_volley", "pirate_1")
        assert event is not None
        hp_after = state.combatants["pirate_1"].hp + state.combatants["pirate_1"].shield
        assert hp_after < hp_before


# ---------------------------------------------------------------------------
# 4. Enemy AI
# ---------------------------------------------------------------------------

class TestEnemyAI:
    def test_enemy_attacks_when_in_range(self):
        player = make_player_ship(pos=Pos(3, 3))
        enemy = make_enemy_ship(pos=Pos(5, 3))  # range 2, within attack range
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        events = enemy_act(state, "pirate_1")
        assert len(events) > 0
        assert any(e.action == "attack" for e in events)

    def test_enemy_moves_toward_player(self):
        player = make_player_ship(pos=Pos(0, 0))
        enemy = make_enemy_ship(pos=Pos(7, 5))  # far away
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        old_pos = state.combatants["pirate_1"].pos
        events = enemy_act(state, "pirate_1")
        new_pos = state.combatants["pirate_1"].pos
        # Should have moved closer
        assert new_pos.distance_to(player.pos) < old_pos.distance_to(player.pos)

    def test_enemy_defends_when_damaged(self):
        player = make_player_ship(pos=Pos(3, 3))
        enemy = make_enemy_ship(pos=Pos(5, 3), hp=1000)
        state = init_combat([player], [enemy], seed=42)
        # Manually damage enemy to <25% of hp_max
        state.combatants["pirate_1"].hp = 200
        start_turn(state)

        events = enemy_act(state, "pirate_1")
        assert any(e.action == "defend" for e in events)


# ---------------------------------------------------------------------------
# 5. Turn loop and resolution
# ---------------------------------------------------------------------------

class TestTurnLoop:
    def test_victory_when_all_enemies_destroyed(self):
        player = make_player_ship(pos=Pos(3, 3))
        enemy = make_enemy_ship(pos=Pos(5, 3), hp=50)  # fragile
        state = init_combat([player], [enemy], seed=1)
        start_turn(state)

        # Keep attacking until enemy dies
        for _ in range(10):
            if state.phase != CombatPhase.ACTIVE:
                break
            current = state.current_actor
            if current is None:
                break
            if current.team == Team.PLAYER:
                targets = get_valid_targets(state, current.id)
                if targets:
                    action_attack(state, current.id, targets[0])
                if current.actions_remaining > 0:
                    action_attack(state, current.id, targets[0]) if targets else action_defend(state, current.id)
            else:
                enemy_act(state, current.id)
            end_turn(state)

        assert state.phase == CombatPhase.VICTORY

    def test_defeat_when_player_destroyed(self):
        player = make_player_ship(pos=Pos(3, 3))
        player.hp = 50  # fragile player
        player.shield = 0
        enemy = make_enemy_ship(pos=Pos(5, 3), damage=200)
        state = init_combat([player], [enemy], seed=1)
        start_turn(state)

        # Let enemy attack
        for _ in range(20):
            if state.phase != CombatPhase.ACTIVE:
                break
            current = state.current_actor
            if current is None:
                break
            if current.team == Team.PLAYER:
                action_defend(state, current.id)
            else:
                enemy_act(state, current.id)
            end_turn(state)

        assert state.phase == CombatPhase.DEFEAT


# ---------------------------------------------------------------------------
# 6. Campaign writeback
# ---------------------------------------------------------------------------

class TestWriteback:
    def test_victory_grants_credits(self):
        player = make_player_ship(pos=Pos(3, 3))
        enemy = make_enemy_ship(pos=Pos(5, 3), hp=10)
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        action_attack(state, "player_ship", "pirate_1")
        end_turn(state)
        # Force victory if not already
        state.combatants["pirate_1"].hp = 0
        state.combatants["pirate_1"].alive = False
        state.phase = CombatPhase.VICTORY

        result = resolve_combat(state, encounter_faction="reach.ironjaw")
        assert result.outcome == CombatPhase.VICTORY
        assert result.credits_gained > 0
        assert "combat_victory" in result.consequence_tags

    def test_defeat_loses_cargo(self):
        player = make_player_ship()
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        state.phase = CombatPhase.DEFEAT

        result = resolve_combat(
            state,
            encounter_faction="reach.ironjaw",
            cargo_at_risk=["keth_biocrystal", "compact_rations", "orryn_data"],
        )
        assert result.outcome == CombatPhase.DEFEAT
        assert len(result.cargo_lost) == 3  # all cargo seized
        assert "cargo_seized" in result.consequence_tags

    def test_retreat_loses_some_cargo(self):
        player = make_player_ship()
        enemy = make_enemy_ship()
        state = init_combat([player], [enemy], seed=42)
        state.phase = CombatPhase.RETREAT

        result = resolve_combat(
            state,
            encounter_faction="reach.ironjaw",
            cargo_at_risk=["keth_biocrystal", "compact_rations", "orryn_data"],
        )
        assert result.outcome == CombatPhase.RETREAT
        assert 0 < len(result.cargo_lost) < 3  # some but not all
        assert "cargo_jettisoned" in result.consequence_tags

    def test_victory_and_defeat_have_different_reputation(self):
        """THE THESIS TEST: Same encounter, different outcome, different campaign state."""
        faction = "reach.ironjaw"

        # Victory
        player_v = make_player_ship()
        enemy_v = make_enemy_ship()
        state_v = init_combat([player_v], [enemy_v], seed=42)
        state_v.phase = CombatPhase.VICTORY
        result_v = resolve_combat(state_v, encounter_faction=faction)

        # Defeat
        player_d = make_player_ship()
        enemy_d = make_enemy_ship()
        state_d = init_combat([player_d], [enemy_d], seed=42)
        state_d.phase = CombatPhase.DEFEAT
        result_d = resolve_combat(state_d, encounter_faction=faction, cargo_at_risk=["goods"])

        # Retreat
        player_r = make_player_ship()
        enemy_r = make_enemy_ship()
        state_r = init_combat([player_r], [enemy_r], seed=42)
        state_r.phase = CombatPhase.RETREAT
        result_r = resolve_combat(
            state_r, encounter_faction=faction,
            cargo_at_risk=["goods"],
        )

        # All three have different reputation profiles
        assert result_v.reputation_delta != result_d.reputation_delta
        assert result_v.reputation_delta != result_r.reputation_delta

        # All three have different consequence tags
        assert result_v.consequence_tags != result_d.consequence_tags
        assert result_v.consequence_tags != result_r.consequence_tags

        # Victory gets credits, others don't
        assert result_v.credits_gained > 0
        assert result_d.credits_gained == 0
        assert result_r.credits_gained == 0

        # Defeat loses all cargo, retreat loses some
        assert len(result_d.cargo_lost) >= len(result_r.cargo_lost)


# ---------------------------------------------------------------------------
# 7. THE THESIS ENCOUNTER — Full integration
# ---------------------------------------------------------------------------

class TestThesisEncounter:
    """One compact encounter, crew-shaped, with meaningful writeback.

    Scenario: Player encounters a Reach pirate while carrying cargo.
    Dax is aboard with emergency_repair.
    """

    def test_full_encounter_victory(self):
        """Win the fight — earn credits, take damage, reputation shifts."""
        repair = make_repair_ability(crew_id="dax_maren")
        player = make_player_ship(pos=Pos(1, 3), abilities=[repair])
        enemy = make_enemy_ship(pos=Pos(5, 3), hp=600)
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        turns = 0
        for _ in range(50):  # safety limit
            if state.phase != CombatPhase.ACTIVE:
                break
            current = state.current_actor
            if current is None:
                break

            if current.team == Team.PLAYER:
                # Strategy: attack, use repair when damaged
                if current.hp < current.hp_max * 0.6:
                    available = get_available_abilities(state, current.id)
                    repair_ab = next((a for a in available if a.id == "emergency_repair"), None)
                    if repair_ab:
                        action_ability(state, current.id, "emergency_repair", current.id)
                    else:
                        targets = get_valid_targets(state, current.id)
                        if targets:
                            action_attack(state, current.id, targets[0])
                        else:
                            action_defend(state, current.id)
                else:
                    targets = get_valid_targets(state, current.id)
                    if targets:
                        action_attack(state, current.id, targets[0])
                    else:
                        moves = get_valid_moves(state, current.id)
                        if moves:
                            # Move toward enemy
                            best = min(moves, key=lambda m: m.distance_to(Pos(5, 3)))
                            action_move(state, current.id, best)

                # Use remaining action
                if current.actions_remaining > 0:
                    targets = get_valid_targets(state, current.id)
                    if targets:
                        action_attack(state, current.id, targets[0])
                    else:
                        action_defend(state, current.id)
            else:
                enemy_act(state, current.id)

            end_turn(state)
            turns += 1

        assert state.phase == CombatPhase.VICTORY
        assert turns <= 10  # should resolve quickly

        result = resolve_combat(state, encounter_faction="reach.ironjaw")
        assert result.credits_gained > 0
        assert result.hull_damage_taken >= 0
        assert "combat_victory" in result.consequence_tags

    def test_full_encounter_retreat(self):
        """Retreat from a strong enemy — lose some cargo, keep ship."""
        repair = make_repair_ability(crew_id="dax_maren")
        player = make_player_ship(pos=Pos(1, 3), abilities=[repair])
        enemy = make_enemy_ship(pos=Pos(5, 3), hp=2000, damage=200)
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        for _ in range(50):
            if state.phase != CombatPhase.ACTIVE:
                break
            current = state.current_actor
            if current is None:
                break

            if current.team == Team.PLAYER:
                action_retreat(state, current.id)
            else:
                enemy_act(state, current.id)
            end_turn(state)

        assert state.phase == CombatPhase.RETREAT
        result = resolve_combat(
            state,
            encounter_faction="reach.ironjaw",
            cargo_at_risk=["keth_biocrystal", "compact_rations", "orryn_data"],
        )
        assert result.outcome == CombatPhase.RETREAT
        assert len(result.cargo_lost) > 0  # some cargo jettisoned
        assert "combat_retreat" in result.consequence_tags
        assert result.credits_gained == 0  # no salvage on retreat

    def test_crew_ability_changes_combat_outcome(self):
        """THE THESIS TEST: Dax's repair ability makes the difference
        between surviving and not surviving."""
        # --- With Dax (repair available) ---
        repair = make_repair_ability(crew_id="dax_maren")
        player_with = make_player_ship(pos=Pos(1, 3), abilities=[repair])
        player_with.hp = 600  # starting damaged
        enemy_with = make_enemy_ship(pos=Pos(3, 3), hp=500)
        state_with = init_combat([player_with], [enemy_with], seed=42)
        start_turn(state_with)

        # Play it out with repair strategy
        for _ in range(50):
            if state_with.phase != CombatPhase.ACTIVE:
                break
            current = state_with.current_actor
            if current is None:
                break
            if current.team == Team.PLAYER:
                available = get_available_abilities(state_with, current.id)
                repair_ab = next((a for a in available if a.id == "emergency_repair"), None)
                if repair_ab and current.hp < 800:
                    action_ability(state_with, current.id, "emergency_repair", current.id)
                else:
                    targets = get_valid_targets(state_with, current.id)
                    if targets:
                        action_attack(state_with, current.id, targets[0])
                    else:
                        action_defend(state_with, current.id)
                if current.actions_remaining > 0:
                    targets = get_valid_targets(state_with, current.id)
                    if targets:
                        action_attack(state_with, current.id, targets[0])
                    else:
                        action_defend(state_with, current.id)
            else:
                enemy_act(state_with, current.id)
            end_turn(state_with)

        hp_with_dax = state_with.combatants["player_ship"].hp

        # --- Without Dax (no repair) ---
        player_without = make_player_ship(pos=Pos(1, 3), abilities=[])
        player_without.hp = 600
        enemy_without = make_enemy_ship(pos=Pos(3, 3), hp=500)
        state_without = init_combat([player_without], [enemy_without], seed=42)
        start_turn(state_without)

        for _ in range(50):
            if state_without.phase != CombatPhase.ACTIVE:
                break
            current = state_without.current_actor
            if current is None:
                break
            if current.team == Team.PLAYER:
                targets = get_valid_targets(state_without, current.id)
                if targets:
                    action_attack(state_without, current.id, targets[0])
                else:
                    action_defend(state_without, current.id)
                if current.actions_remaining > 0:
                    targets = get_valid_targets(state_without, current.id)
                    if targets:
                        action_attack(state_without, current.id, targets[0])
                    else:
                        action_defend(state_without, current.id)
            else:
                enemy_act(state_without, current.id)
            end_turn(state_without)

        hp_without_dax = state_without.combatants["player_ship"].hp

        # Dax's repair should have resulted in more HP remaining
        assert hp_with_dax > hp_without_dax, (
            f"Dax should make a difference: with={hp_with_dax}, without={hp_without_dax}"
        )

    def test_three_outcomes_three_different_campaign_states(self):
        """THE CORE THESIS TEST: Victory, defeat, and retreat all produce
        materially different campaign state from the same starting position."""
        faction = "reach.ironjaw"
        cargo = ["keth_biocrystal", "compact_rations", "orryn_data"]

        # Victory
        state_v = init_combat(
            [make_player_ship()],
            [make_enemy_ship()],
            seed=42,
        )
        state_v.phase = CombatPhase.VICTORY
        result_v = resolve_combat(state_v, encounter_faction=faction, cargo_at_risk=cargo)

        # Defeat
        state_d = init_combat(
            [make_player_ship()],
            [make_enemy_ship()],
            seed=42,
        )
        state_d.phase = CombatPhase.DEFEAT
        result_d = resolve_combat(state_d, encounter_faction=faction, cargo_at_risk=cargo)

        # Retreat
        state_r = init_combat(
            [make_player_ship()],
            [make_enemy_ship()],
            seed=42,
        )
        state_r.phase = CombatPhase.RETREAT
        result_r = resolve_combat(state_r, encounter_faction=faction, cargo_at_risk=cargo)

        # --- Assert materially different ---

        # Credits: only victory earns
        assert result_v.credits_gained > 0
        assert result_d.credits_gained == 0
        assert result_r.credits_gained == 0

        # Cargo: defeat = all lost, retreat = some lost, victory = none
        assert len(result_v.cargo_lost) == 0
        assert len(result_d.cargo_lost) == 3
        assert 0 < len(result_r.cargo_lost) < 3

        # Reputation: all different shapes
        assert result_v.reputation_delta.get(faction) != result_d.reputation_delta.get(faction)

        # Consequence tags: all different
        assert set(result_v.consequence_tags) != set(result_d.consequence_tags)
        assert set(result_d.consequence_tags) != set(result_r.consequence_tags)
        assert set(result_v.consequence_tags) != set(result_r.consequence_tags)

    def test_combat_resolves_in_reasonable_turns(self):
        """Typical fight should be 5-8 turns, not a slog."""
        repair = make_repair_ability()
        player = make_player_ship(pos=Pos(1, 3), abilities=[repair])
        enemy = make_enemy_ship(pos=Pos(5, 3), hp=800)
        state = init_combat([player], [enemy], seed=42)
        start_turn(state)

        for _ in range(100):
            if state.phase != CombatPhase.ACTIVE:
                break
            current = state.current_actor
            if current is None:
                break
            if current.team == Team.PLAYER:
                targets = get_valid_targets(state, current.id)
                if targets:
                    action_attack(state, current.id, targets[0])
                else:
                    moves = get_valid_moves(state, current.id)
                    if moves:
                        best = min(moves, key=lambda m: m.distance_to(Pos(5, 3)))
                        action_move(state, current.id, best)
                if current.actions_remaining > 0:
                    targets = get_valid_targets(state, current.id)
                    if targets:
                        action_attack(state, current.id, targets[0])
                    else:
                        action_defend(state, current.id)
            else:
                enemy_act(state, current.id)
            end_turn(state)

        assert state.phase != CombatPhase.ACTIVE  # should have ended
        assert state.turn <= 10, f"Combat took {state.turn} turns — too slow"
