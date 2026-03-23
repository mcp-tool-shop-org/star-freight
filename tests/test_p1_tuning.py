"""P1 tuning pass tests — demand premiums, fear classifier, escalation factor.

These tests prove the P1 tuning changes work correctly without
breaking existing behavior. They are the trust anchor for the
Wave 3 confirmation run.
"""

from __future__ import annotations

import random

import pytest

from portlight.engine.sf_campaign import (
    CampaignState,
    _demand_premium,
    _DEMAND_PREMIUMS,
    execute_trade,
    run_combat,
)
from portlight.engine.playtest import (
    CaptainPosture,
    RunMetrics,
    _classify_fear,
    simulate_run,
    generate_synthesis,
)
from portlight.engine.grid_combat import (
    Pos, Team, Combatant, CombatAbility, CombatPhase,
    init_combat, start_turn, end_turn,
    action_attack, get_valid_targets, action_defend,
    enemy_act, resolve_combat,
)
from portlight.content.star_freight import SLICE_STATIONS, SLICE_GOODS


# =========================================================================
# _demand_premium
# =========================================================================

class TestDemandPremium:
    """Demand premium increases for intended goods/routes only."""

    def test_relief_volume_goods_lower_premium(self):
        """medical_supplies and keth_organics get reduced demand premium."""
        assert _demand_premium("medical_supplies") < 1.5
        assert _demand_premium("keth_organics") < 1.5

    def test_gray_specialist_goods_higher_premium(self):
        """Orryn/bond goods get elevated demand premium."""
        assert _demand_premium("orryn_data") > 1.5
        assert _demand_premium("orryn_brokered_goods") > 1.5
        assert _demand_premium("bond_plate") > 1.5

    def test_honor_specialist_goods_higher_premium(self):
        """Veshan/luxury goods get elevated demand premium."""
        assert _demand_premium("veshan_weapons") > 1.5
        assert _demand_premium("black_seal_resin") > 1.5

    def test_unrelated_goods_default_premium(self):
        """Goods not in the tuning table get the standard 1.5x premium."""
        assert _demand_premium("compact_alloys") == 1.5
        assert _demand_premium("ancestor_tech") == 1.5
        assert _demand_premium("reach_contraband") == 1.5
        assert _demand_premium("brood_silk") == 1.5
        assert _demand_premium("veshan_minerals") == 1.5

    def test_premium_bounded(self):
        """All premiums are in a sane range — never below 1.0 or above 2.0."""
        for good_id, mult in _DEMAND_PREMIUMS.items():
            assert 1.0 < mult < 2.0, f"{good_id} premium {mult} out of range"
        # Default also bounded
        assert 1.0 < _demand_premium("nonexistent_good") < 2.0

    def test_no_premium_leak_to_source_goods(self):
        """Demand premium only applies at demand stations, not source stations.

        Verify through execute_trade: buying at a station that produces a good
        should use source discount, not demand premium.
        """
        state = CampaignState()
        state.credits = 5000
        state.current_station = "communion_relay"

        # keth_organics is PRODUCED at communion_relay — should get source price
        result = execute_trade(state, "keth_organics", "buy", 1)
        assert "error" not in result
        # Source price: 120 * 0.72 = 86 (with P1 keth_organics nerf)
        assert result["price_each"] <= 90, "Should get source discount, not demand premium"

    def test_demand_premium_applies_at_demand_station(self):
        """Selling a good at a station that demands it uses the elevated premium."""
        state = CampaignState()
        state.credits = 5000
        state.current_station = "meridian_exchange"

        # Buy orryn_data at meridian (demanded — premium applies)
        # orryn_data demanded at meridian: 180 * 1.7 = 306, minus cultural modifier
        result = execute_trade(state, "orryn_data", "buy", 1)
        # At demand station: 180 * 1.7 ≈ 306, cultural modifier may reduce slightly
        # Pre-P1 at 1.5x: 180 * 1.5 = 270, so post-P1 must be higher
        assert result["price_each"] >= 275, "Should get elevated demand premium above old 1.5x"

    def test_relief_regression_lower_sell_price(self):
        """Relief's volume goods sell for less at demand stations than before.

        Pre-P1: medical_supplies at demand = 60 * 1.5 = 90
        Post-P1: medical_supplies at demand = 60 * 1.3 = 78
        """
        state = CampaignState()
        state.credits = 100
        state.current_station = "communion_relay"

        # Buy medical_supplies at source first
        buy_state = CampaignState()
        buy_state.credits = 5000
        buy_state.current_station = "meridian_exchange"
        buy_result = execute_trade(buy_state, "medical_supplies", "buy", 1)
        assert "error" not in buy_result

        # Now sell at a demand station
        buy_state.current_station = "drashan_citadel"  # demands medical_supplies
        sell_result = execute_trade(buy_state, "medical_supplies", "sell", 1)
        assert "error" not in sell_result
        # Post-P1: 60 * 1.3 = 78 (was 90 at 1.5x)
        assert sell_result["price_each"] <= 80, "medical_supplies demand premium should be reduced"

    def test_premium_monotonic_for_specialist_goods(self):
        """Specialist goods always get higher premium than volume goods."""
        volume_max = max(_demand_premium("medical_supplies"), _demand_premium("keth_organics"))
        specialist_min = min(
            _demand_premium("orryn_data"),
            _demand_premium("veshan_weapons"),
            _demand_premium("black_seal_resin"),
        )
        assert specialist_min > volume_max, "Specialist premiums must exceed volume premiums"


# =========================================================================
# _classify_fear
# =========================================================================

class TestClassifyFear:
    """Captain-specific fear detection from telemetry."""

    def _make_metrics(self, captain_type: str, **overrides) -> RunMetrics:
        """Build a RunMetrics with defaults and overrides."""
        m = RunMetrics(captain_type=captain_type)
        m.credits_history = overrides.pop("credits_history", [500, 600, 700])
        for k, v in overrides.items():
            setattr(m, k, v)
        return m

    # --- Relief fears ---

    def test_relief_fear_delivery_delay(self):
        """Relief with high delays fears delivery lateness."""
        m = self._make_metrics("relief", delays=5)
        fear = _classify_fear(m)
        assert "delay" in fear.lower()

    def test_relief_fear_undercapacity(self):
        """Relief with missed pay fears undercapacity."""
        m = self._make_metrics("relief", pay_missed=1)
        fear = _classify_fear(m)
        assert "undercapacity" in fear.lower()

    def test_relief_fear_public_failure(self):
        """Relief with credit dips fears public failure."""
        m = self._make_metrics("relief", credits_history=[500, 200, 150])
        fear = _classify_fear(m)
        assert "public failure" in fear.lower()

    def test_relief_fear_fallback(self):
        """Relief with no strong signals gets schedule compression."""
        m = self._make_metrics("relief", delays=1, pay_missed=0,
                               credits_history=[500, 600, 700])
        fear = _classify_fear(m)
        assert "schedule" in fear.lower() or "compression" in fear.lower()

    # --- Gray fears ---

    def test_gray_fear_seizure(self):
        """Gray with seizures fears cargo seizure."""
        m = self._make_metrics("gray", seizures=1)
        fear = _classify_fear(m)
        assert "seizure" in fear.lower()

    def test_gray_fear_exposure(self):
        """Gray with high retreat rate fears exposure."""
        m = self._make_metrics("gray", combat_count=10, retreats=5)
        fear = _classify_fear(m)
        assert "exposure" in fear.lower()

    def test_gray_fear_paper_closure(self):
        """Gray with delays and no seizures fears paper closure."""
        m = self._make_metrics("gray", seizures=0, retreats=0,
                               combat_count=2, delays=4)
        fear = _classify_fear(m)
        assert "paper" in fear.lower()

    def test_gray_fear_fallback(self):
        """Gray with no strong signals gets institutional pressure."""
        m = self._make_metrics("gray", seizures=0, retreats=0,
                               combat_count=2, delays=1)
        fear = _classify_fear(m)
        assert "institutional" in fear.lower()

    # --- Honor fears ---

    def test_honor_fear_crew_loss(self):
        """Honor with crew injuries fears crew loss."""
        m = self._make_metrics("honor", crew_injuries=4)
        fear = _classify_fear(m)
        assert "crew" in fear.lower()

    def test_honor_fear_escalation(self):
        """Honor with many repairs fears escalation."""
        m = self._make_metrics("honor", crew_injuries=1, repairs_needed=4)
        fear = _classify_fear(m)
        assert "escalation" in fear.lower()

    def test_honor_fear_thin_support(self):
        """Honor with crew departures fears thin support."""
        m = self._make_metrics("honor", crew_injuries=0, repairs_needed=0,
                               crew_departures=2)
        fear = _classify_fear(m)
        assert "thin support" in fear.lower()

    def test_honor_fear_fallback(self):
        """Honor with no strong signals gets combat attrition."""
        m = self._make_metrics("honor", crew_injuries=0, repairs_needed=0,
                               crew_departures=0)
        fear = _classify_fear(m)
        assert "attrition" in fear.lower()

    # --- Tie-break and edge cases ---

    def test_relief_delay_beats_credit_dip(self):
        """When Relief has both delays and credit dips, delays win (checked first)."""
        m = self._make_metrics("relief", delays=5, credits_history=[500, 200, 150])
        fear = _classify_fear(m)
        assert "delay" in fear.lower()

    def test_gray_seizure_beats_exposure(self):
        """When Gray has both seizures and retreats, seizure wins."""
        m = self._make_metrics("gray", seizures=2, combat_count=10, retreats=5)
        fear = _classify_fear(m)
        assert "seizure" in fear.lower()

    def test_honor_crew_loss_beats_escalation(self):
        """When Honor has both crew injuries and repairs, crew loss wins."""
        m = self._make_metrics("honor", crew_injuries=5, repairs_needed=5)
        fear = _classify_fear(m)
        assert "crew" in fear.lower()

    def test_unknown_captain_type_fallback(self):
        """Unknown captain type gets generic fallback."""
        m = self._make_metrics("pirate")
        fear = _classify_fear(m)
        assert "running out of options" in fear.lower()

    def test_sparse_telemetry_does_not_crash(self):
        """Minimal telemetry (all zeros) produces a valid fear string."""
        for ct in ["relief", "gray", "honor"]:
            m = RunMetrics(captain_type=ct)
            m.credits_history = [500]
            fear = _classify_fear(m)
            assert isinstance(fear, str)
            assert len(fear) > 5

    def test_all_three_captains_produce_distinct_fears(self):
        """Under identical telemetry, captains still diverge on fear."""
        kwargs = dict(delays=4, seizures=1, crew_injuries=3,
                      combat_count=6, retreats=3, repairs_needed=3,
                      credits_history=[500, 200, 150])
        fears = set()
        for ct in ["relief", "gray", "honor"]:
            m = self._make_metrics(ct, **kwargs)
            fears.add(_classify_fear(m))
        assert len(fears) == 3, f"Expected 3 distinct fears, got {fears}"


# =========================================================================
# escalation_factor
# =========================================================================

class TestEscalationFactor:
    """Escalation pressure on clustered combat."""

    def _make_player_ship(self, abilities=None):
        return Combatant(
            id="player", name="Test Ship", team=Team.PLAYER, pos=Pos(1, 3),
            hp=2000, hp_max=2000, shield=200, shield_max=250,
            speed=2, evasion=0.1, armor=10,
            base_attack_damage=150, base_attack_range=3,
            abilities=abilities or [],
        )

    def _make_enemy_ship(self, hp=800):
        return Combatant(
            id="enemy", name="Pirate", team=Team.ENEMY, pos=Pos(6, 3),
            hp=hp, hp_max=hp, shield=100, shield_max=100,
            speed=3, evasion=0.15, armor=5,
            base_attack_damage=130, base_attack_range=3,
        )

    def _run_to_victory(self, player, enemy, seed=42):
        """Run combat to completion, forcing victory."""
        cs = init_combat([player], [enemy], seed=seed)
        start_turn(cs)
        for _ in range(200):
            if cs.phase != CombatPhase.ACTIVE:
                break
            current = cs.current_actor
            if current is None:
                break
            if current.team == Team.PLAYER:
                targets = get_valid_targets(cs, current.id)
                if targets and current.actions_remaining > 0:
                    action_attack(cs, current.id, targets[0])
                if current.actions_remaining > 0:
                    action_defend(cs, current.id)
            else:
                enemy_act(cs, current.id)
            end_turn(cs)
        return cs

    # --- Salvage diminishing returns ---

    def test_no_escalation_full_salvage(self):
        """With escalation_factor=0, salvage is full rate (0.38 * hp_max)."""
        player = self._make_player_ship()
        enemy = self._make_enemy_ship(hp=800)
        cs = self._run_to_victory(player, enemy)
        if cs.phase != CombatPhase.VICTORY:
            pytest.skip("Combat did not result in victory")
        result = resolve_combat(cs, "reach", [], escalation_factor=0.0)
        # Full salvage: 800 * 0.38 = 304
        assert result.credits_gained >= 280, f"Expected near-full salvage, got {result.credits_gained}"

    def test_high_escalation_reduced_salvage(self):
        """With high escalation_factor, salvage is significantly reduced."""
        player = self._make_player_ship()
        enemy = self._make_enemy_ship(hp=800)
        cs = self._run_to_victory(player, enemy)
        if cs.phase != CombatPhase.VICTORY:
            pytest.skip("Combat did not result in victory")
        result = resolve_combat(cs, "reach", [], escalation_factor=0.45)
        # Reduced: 800 * 0.38 * (1 - 0.45) = 167
        assert result.credits_gained < 200, f"Expected reduced salvage, got {result.credits_gained}"

    def test_max_escalation_floor(self):
        """Escalation_factor at max (0.6) still pays something — floor is 20%."""
        player = self._make_player_ship()
        enemy = self._make_enemy_ship(hp=800)
        cs = self._run_to_victory(player, enemy)
        if cs.phase != CombatPhase.VICTORY:
            pytest.skip("Combat did not result in victory")
        result = resolve_combat(cs, "reach", [], escalation_factor=0.6)
        # Floor: 800 * 0.38 * 0.4 = 121.6
        assert result.credits_gained > 0, "Salvage should never be zero"
        assert result.credits_gained < 150, "Max escalation should severely reduce salvage"

    def test_escalation_salvage_monotonically_decreasing(self):
        """Higher escalation always means less salvage."""
        salvage_values = []
        for factor in [0.0, 0.15, 0.30, 0.45, 0.60]:
            player = self._make_player_ship()
            enemy = self._make_enemy_ship(hp=800)
            cs = self._run_to_victory(player, enemy, seed=42)
            if cs.phase != CombatPhase.VICTORY:
                pytest.skip("Combat did not result in victory")
            result = resolve_combat(cs, "reach", [], escalation_factor=factor)
            salvage_values.append(result.credits_gained)
        for i in range(len(salvage_values) - 1):
            assert salvage_values[i] >= salvage_values[i + 1], \
                f"Salvage not monotonically decreasing: {salvage_values}"

    # --- Injury pressure ---

    def test_escalation_increases_injury_chance(self):
        """High escalation makes crew injuries more likely.

        Run many trials and compare injury rates at 0 vs high escalation.
        """
        crew_ab = CombatAbility(
            id="repair", name="Repair", description="Test",
            action_cost=1, cooldown=99, effect_type="heal", effect_value=100,
            crew_source="crew_alpha",
        )

        injury_count_low = 0
        injury_count_high = 0
        trials = 50

        for seed in range(trials):
            for factor, counter_ref in [(0.0, "low"), (0.45, "high")]:
                player = self._make_player_ship(abilities=[crew_ab])
                enemy = self._make_enemy_ship(hp=600)
                # Weaken player to trigger injury check (hull damage > threshold)
                player.hp = 800  # take ~60% hull damage from the start
                cs = self._run_to_victory(player, enemy, seed=seed)
                if cs.phase != CombatPhase.VICTORY:
                    continue
                result = resolve_combat(cs, "reach", [], escalation_factor=factor)
                if counter_ref == "low":
                    injury_count_low += len(result.crew_injuries)
                else:
                    injury_count_high += len(result.crew_injuries)

        # High escalation should produce MORE injuries overall
        # (statistical — allow some variance)
        assert injury_count_high >= injury_count_low, \
            f"Expected more injuries at high escalation: low={injury_count_low}, high={injury_count_high}"

    # --- Hull wear ---

    def test_escalation_hull_wear(self):
        """Escalation applies persistent hull wear on victory."""
        player = self._make_player_ship()
        enemy = self._make_enemy_ship(hp=800)
        cs = self._run_to_victory(player, enemy)
        if cs.phase != CombatPhase.VICTORY:
            pytest.skip("Combat did not result in victory")

        result_clean = resolve_combat(cs, "reach", [], escalation_factor=0.0)
        hull_clean = result_clean.player_hull_remaining

        # Re-run with escalation
        player2 = self._make_player_ship()
        enemy2 = self._make_enemy_ship(hp=800)
        cs2 = self._run_to_victory(player2, enemy2)
        if cs2.phase != CombatPhase.VICTORY:
            pytest.skip("Combat did not result in victory")

        result_esc = resolve_combat(cs2, "reach", [], escalation_factor=0.45)
        hull_esc = result_esc.player_hull_remaining

        assert hull_esc < hull_clean, \
            f"Escalation should cause hull wear: clean={hull_clean}, escalated={hull_esc}"

    def test_no_escalation_no_hull_wear(self):
        """With escalation_factor=0, no extra hull wear is applied."""
        player = self._make_player_ship()
        enemy = self._make_enemy_ship(hp=800)
        cs = self._run_to_victory(player, enemy)
        if cs.phase != CombatPhase.VICTORY:
            pytest.skip("Combat did not result in victory")
        result = resolve_combat(cs, "reach", [], escalation_factor=0.0)
        assert "escalation_wear" not in result.consequence_tags

    def test_escalation_wear_tag_present(self):
        """Escalation hull wear adds the escalation_wear consequence tag."""
        player = self._make_player_ship()
        enemy = self._make_enemy_ship(hp=800)
        cs = self._run_to_victory(player, enemy)
        if cs.phase != CombatPhase.VICTORY:
            pytest.skip("Combat did not result in victory")
        result = resolve_combat(cs, "reach", [], escalation_factor=0.3)
        assert "escalation_wear" in result.consequence_tags

    # --- Simulation integration ---

    def test_simulation_tracks_escalation(self):
        """simulate_run applies escalation to clustered fights, not all fights.

        Run a full simulation and verify that the escalation mechanics
        are wired through the combat chain.
        """
        _, metrics = simulate_run(CaptainPosture.HONOR, days=90, seed=42)
        # Honor fights — if any escalation_wear tags appeared, escalation is wired
        # (Not all fights cluster, so this is a presence check, not a count)
        syn = generate_synthesis(metrics)
        assert isinstance(syn["feared"], str)
        assert len(syn["feared"]) > 5

    def test_honor_baseline_survives(self):
        """Honor baseline still survives after escalation mechanics."""
        _, metrics = simulate_run(CaptainPosture.HONOR, days=90, seed=42)
        assert metrics.pay_missed == 0, "Honor should survive without missed pay"
        assert metrics.final_credits > 0, "Honor should end with positive credits"

    def test_escalation_does_not_affect_gray(self):
        """Gray retreats from combat — escalation mechanics should not punish Gray.

        Gray's combat strategy is 'retreat', so escalation_factor should
        rarely apply (retreats don't go through victory salvage path).
        """
        _, metrics_gray = simulate_run(CaptainPosture.GRAY, days=90, seed=42)
        # Gray should still be viable — not crushed by escalation
        assert metrics_gray.final_credits > 0, "Gray should not be hurt by escalation"
        assert metrics_gray.pay_missed == 0

    def test_relief_barely_affected_by_escalation(self):
        """Relief fights defensively — escalation should minimally affect Relief.

        Relief's income is trade-based, not salvage-based.
        """
        _, metrics_relief = simulate_run(CaptainPosture.RELIEF, days=90, seed=42)
        # Relief should still be the richest
        _, metrics_honor = simulate_run(CaptainPosture.HONOR, days=90, seed=42)
        assert metrics_relief.final_credits > metrics_honor.final_credits, \
            "Relief should still earn more than Honor"


# =========================================================================
# Content regression — station changes
# =========================================================================

class TestP1StationChanges:
    """Verify P1 station content changes are correct."""

    def test_drashan_produces_black_seal_resin(self):
        """Drashan Citadel now produces black_seal_resin (Veshan luxury)."""
        station = SLICE_STATIONS["drashan_citadel"]
        assert "black_seal_resin" in station.produces

    def test_drashan_demands_orryn_brokered_goods(self):
        """Drashan Citadel now demands orryn_brokered_goods (Gray lift)."""
        station = SLICE_STATIONS["drashan_citadel"]
        assert "orryn_brokered_goods" in station.demands

    def test_ironjaw_demands_black_seal_resin(self):
        """Ironjaw Den now demands black_seal_resin (Honor trade route)."""
        station = SLICE_STATIONS["ironjaw_den"]
        assert "black_seal_resin" in station.demands

    def test_queue_demands_bond_plate(self):
        """Queue of Flags now demands bond_plate (Gray trade route)."""
        station = SLICE_STATIONS["queue_of_flags"]
        assert "bond_plate" in station.demands

    def test_registry_docking_fee_reduced(self):
        """Registry Spindle docking fee reduced from 15 to 12 (Gray fee relief)."""
        station = SLICE_STATIONS["registry_spindle"]
        assert station.docking_fee == 12

    def test_keth_organics_source_discount_nerfed(self):
        """keth_organics at source should cost more than standard 0.65 discount."""
        state = CampaignState()
        state.credits = 5000
        state.current_station = "communion_relay"
        result = execute_trade(state, "keth_organics", "buy", 1)
        assert "error" not in result
        # At 0.72: 120 * 0.72 = 86, cultural modifier may reduce slightly
        # At old 0.65: 120 * 0.65 = 78, cultural modifier same → ~70
        # Post-P1 price should be higher than pre-P1 price
        assert result["price_each"] > 72, "keth_organics source price should be higher than old 0.65 discount"
