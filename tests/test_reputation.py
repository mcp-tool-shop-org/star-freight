"""Tests for the reputation engine — proves the world remembers commercial behavior.

Behavioral proofs:
  - Repeated same-lane dumping raises heat materially
  - Heat decays over time without falling off a cliff
  - Lawful stable trading raises standing/trust
  - Seizures and inspections damage reputation
  - Port standing improves local service terms
  - Regional standing improves fee tiers
  - High heat worsens inspection outcomes
  - Three captains diverge in reputation trajectory under similar trade behavior
"""

from pathlib import Path

from portlight.app.session import GameSession
from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.models import GoodCategory, ReputationIncident, ReputationState
from portlight.engine.reputation import (
    _compute_suspicion,
    get_fee_modifier,
    get_inspection_modifier,
    get_service_modifier,
    get_trust_tier,
    record_inspection_outcome,
    record_port_arrival,
    record_trade_outcome,
    tick_reputation,
)
from portlight.engine.save import world_from_dict, world_to_dict


class TestSuspicionScoring:
    """The suspicious-dump law produces legible, graduated heat."""

    def test_small_commodity_trade_low_suspicion(self):
        """Small grain sale at modest margin = near-zero suspicion."""
        score = _compute_suspicion(
            GoodCategory.COMMODITY, quantity=5, stock_target=35,
            margin_pct=30, flood_penalty=0.0, captain_type="merchant",
            region_heat=0,
        )
        assert score <= 1

    def test_large_luxury_dump_high_suspicion(self):
        """Big luxury dump at high margin = serious suspicion."""
        score = _compute_suspicion(
            GoodCategory.LUXURY, quantity=20, stock_target=15,
            margin_pct=250, flood_penalty=0.3, captain_type="smuggler",
            region_heat=15,
        )
        assert score >= 8

    def test_margin_severity_scales(self):
        """Higher margins generate more suspicion."""
        low = _compute_suspicion(GoodCategory.COMMODITY, 10, 30, 40, 0, "merchant", 0)
        high = _compute_suspicion(GoodCategory.COMMODITY, 10, 30, 200, 0, "merchant", 0)
        assert high > low

    def test_quantity_relative_to_target(self):
        """Flooding a small market is more suspicious than selling into a large one."""
        small = _compute_suspicion(GoodCategory.COMMODITY, 10, 12, 100, 0, "merchant", 0)
        large = _compute_suspicion(GoodCategory.COMMODITY, 10, 100, 100, 0, "merchant", 0)
        assert small > large

    def test_luxury_adds_suspicion(self):
        """Luxury goods inherently draw more heat."""
        commodity = _compute_suspicion(GoodCategory.COMMODITY, 10, 30, 100, 0, "merchant", 0)
        luxury = _compute_suspicion(GoodCategory.LUXURY, 10, 30, 100, 0, "merchant", 0)
        assert luxury > commodity

    def test_existing_heat_amplifies(self):
        """Being watched makes further activity more suspicious."""
        clean = _compute_suspicion(GoodCategory.COMMODITY, 10, 30, 150, 0, "merchant", 0)
        hot = _compute_suspicion(GoodCategory.COMMODITY, 10, 30, 150, 0, "merchant", 25)
        assert hot > clean

    def test_smuggler_inherent_suspicion(self):
        """Smuggler captain type adds baseline suspicion."""
        merchant = _compute_suspicion(GoodCategory.LUXURY, 10, 20, 150, 0, "merchant", 0)
        smuggler = _compute_suspicion(GoodCategory.LUXURY, 10, 20, 150, 0, "smuggler", 0)
        assert smuggler > merchant

    def test_flood_penalty_compounds(self):
        """Repeated dumps at same port compound suspicion."""
        fresh = _compute_suspicion(GoodCategory.COMMODITY, 10, 20, 150, 0.0, "merchant", 0)
        flooded = _compute_suspicion(GoodCategory.COMMODITY, 10, 20, 150, 0.4, "merchant", 0)
        assert flooded > fresh


class TestTradeReputation:
    """Trade outcomes mutate reputation correctly."""

    def test_profitable_clean_trade_builds_standing(self):
        rep = ReputationState()
        record_trade_outcome(
            rep, "merchant", day=5, port_id="porto_novo", region="Mediterranean",
            good_id="grain", good_category=GoodCategory.COMMODITY,
            quantity=10, margin_pct=80, stock_target=35, flood_penalty=0.0,
            is_sell=True,
        )
        assert rep.regional_standing["Mediterranean"] > 0
        assert rep.commercial_trust > 0

    def test_suspicious_dump_raises_heat(self):
        rep = ReputationState()
        record_trade_outcome(
            rep, "smuggler", day=5, port_id="al_manar", region="Mediterranean",
            good_id="silk", good_category=GoodCategory.LUXURY,
            quantity=15, margin_pct=300, stock_target=10, flood_penalty=0.3,
            is_sell=True,
        )
        assert rep.customs_heat["Mediterranean"] > 0

    def test_buy_is_neutral(self):
        rep = ReputationState()
        heat_delta = record_trade_outcome(
            rep, "merchant", day=1, port_id="porto_novo", region="Mediterranean",
            good_id="grain", good_category=GoodCategory.COMMODITY,
            quantity=10, margin_pct=0, stock_target=35, flood_penalty=0.0,
            is_sell=False,
        )
        assert heat_delta == 0

    def test_merchant_trust_bonus_on_clean_trade(self):
        """Merchant builds trust faster on clean trades."""
        rep_m = ReputationState()
        rep_s = ReputationState()
        for _ in range(5):
            record_trade_outcome(
                rep_m, "merchant", day=1, port_id="porto_novo", region="Mediterranean",
                good_id="grain", good_category=GoodCategory.COMMODITY,
                quantity=5, margin_pct=60, stock_target=35, flood_penalty=0.0,
                is_sell=True,
            )
            record_trade_outcome(
                rep_s, "smuggler", day=1, port_id="porto_novo", region="Mediterranean",
                good_id="grain", good_category=GoodCategory.COMMODITY,
                quantity=5, margin_pct=60, stock_target=35, flood_penalty=0.0,
                is_sell=True,
            )
        assert rep_m.commercial_trust > rep_s.commercial_trust

    def test_repeated_dumps_escalate_heat(self):
        """Same lane dumping produces escalating heat."""
        rep = ReputationState()
        heats = []
        for i in range(5):
            record_trade_outcome(
                rep, "merchant", day=i + 1, port_id="al_manar", region="Mediterranean",
                good_id="silk", good_category=GoodCategory.LUXURY,
                quantity=10, margin_pct=200, stock_target=12, flood_penalty=0.1 * (i + 1),
                is_sell=True,
            )
            heats.append(rep.customs_heat["Mediterranean"])
        # Heat should be monotonically increasing
        for i in range(1, len(heats)):
            assert heats[i] >= heats[i - 1]
        # Final heat should be substantial
        assert heats[-1] >= 10

    def test_very_suspicious_dump_damages_standing(self):
        """Extremely suspicious dumps damage regional standing."""
        rep = ReputationState()
        rep.regional_standing["Mediterranean"] = 20  # start with some standing
        record_trade_outcome(
            rep, "smuggler", day=1, port_id="al_manar", region="Mediterranean",
            good_id="silk", good_category=GoodCategory.LUXURY,
            quantity=20, margin_pct=400, stock_target=10, flood_penalty=0.5,
            is_sell=True,
        )
        assert rep.regional_standing["Mediterranean"] < 20


class TestPortArrival:
    """Arriving at ports builds familiarity and decays heat."""

    def test_arrival_builds_port_standing(self):
        rep = ReputationState()
        record_port_arrival(rep, day=1, port_id="porto_novo", region="Mediterranean")
        assert rep.port_standing.get("porto_novo", 0) > 0

    def test_arrival_builds_regional_standing(self):
        rep = ReputationState()
        record_port_arrival(rep, day=1, port_id="porto_novo", region="Mediterranean")
        assert rep.regional_standing["Mediterranean"] > 0

    def test_arrival_decays_heat(self):
        rep = ReputationState()
        rep.customs_heat["Mediterranean"] = 20
        record_port_arrival(rep, day=1, port_id="porto_novo", region="Mediterranean")
        assert rep.customs_heat["Mediterranean"] < 20

    def test_repeated_arrivals_build_standing(self):
        rep = ReputationState()
        for i in range(10):
            record_port_arrival(rep, day=i, port_id="porto_novo", region="Mediterranean")
        assert rep.port_standing["porto_novo"] >= 10


class TestInspection:
    """Inspections raise heat and damage reputation."""

    def test_routine_inspection_raises_heat(self):
        rep = ReputationState()
        record_inspection_outcome(rep, day=1, port_id="porto_novo", region="Mediterranean",
                                  fine_amount=10, cargo_seized=False)
        assert rep.customs_heat["Mediterranean"] > 0

    def test_seizure_spikes_heat(self):
        rep = ReputationState()
        record_inspection_outcome(rep, day=1, port_id="porto_novo", region="Mediterranean",
                                  fine_amount=20, cargo_seized=True)
        assert rep.customs_heat["Mediterranean"] >= 5

    def test_seizure_damages_standing(self):
        rep = ReputationState()
        rep.regional_standing["Mediterranean"] = 15
        record_inspection_outcome(rep, day=1, port_id="porto_novo", region="Mediterranean",
                                  fine_amount=20, cargo_seized=True)
        assert rep.regional_standing["Mediterranean"] < 15

    def test_seizure_damages_trust(self):
        rep = ReputationState()
        rep.commercial_trust = 20
        record_inspection_outcome(rep, day=1, port_id="porto_novo", region="Mediterranean",
                                  fine_amount=20, cargo_seized=True)
        assert rep.commercial_trust < 20

    def test_inspection_creates_incident(self):
        rep = ReputationState()
        record_inspection_outcome(rep, day=3, port_id="al_manar", region="Mediterranean",
                                  fine_amount=15, cargo_seized=False)
        assert len(rep.recent_incidents) == 1
        assert rep.recent_incidents[0].incident_type == "inspection"


class TestHeatDecay:
    """Heat decays over time without falling off a cliff."""

    def test_heat_decays_daily(self):
        rep = ReputationState()
        rep.customs_heat["Mediterranean"] = 30
        tick_reputation(rep)
        assert rep.customs_heat["Mediterranean"] < 30

    def test_heat_decays_faster_when_higher(self):
        rep = ReputationState()
        rep.customs_heat["Mediterranean"] = 30
        tick_reputation(rep)
        high_decay = 30 - rep.customs_heat["Mediterranean"]

        rep2 = ReputationState()
        rep2.customs_heat["Mediterranean"] = 10
        tick_reputation(rep2)
        low_decay = 10 - rep2.customs_heat["Mediterranean"]

        assert high_decay >= low_decay

    def test_low_heat_does_not_decay(self):
        """Below threshold 5, heat is stable (baseline friction)."""
        rep = ReputationState()
        rep.customs_heat["Mediterranean"] = 3
        tick_reputation(rep)
        assert rep.customs_heat["Mediterranean"] == 3

    def test_heat_decays_to_baseline_eventually(self):
        """Given enough time, heat decays to baseline (below 5)."""
        rep = ReputationState()
        rep.customs_heat["Mediterranean"] = 40
        for _ in range(100):
            tick_reputation(rep)
        assert rep.customs_heat["Mediterranean"] < 5

    def test_standing_does_not_decay(self):
        """Standing is stable — you don't lose it from inaction."""
        rep = ReputationState()
        rep.regional_standing["Mediterranean"] = 25
        for _ in range(20):
            tick_reputation(rep)
        assert rep.regional_standing["Mediterranean"] == 25


class TestAccessEffects:
    """Reputation produces real access modifications."""

    def test_high_standing_reduces_fees(self):
        rep = ReputationState()
        rep.regional_standing["Mediterranean"] = 30
        mod = get_fee_modifier(rep, "Mediterranean")
        assert mod < 1.0

    def test_high_heat_increases_fees(self):
        rep = ReputationState()
        rep.customs_heat["Mediterranean"] = 25
        mod = get_fee_modifier(rep, "Mediterranean")
        assert mod > 1.0

    def test_standing_and_heat_combine(self):
        """Standing discount and heat surcharge partially cancel."""
        rep = ReputationState()
        rep.regional_standing["Mediterranean"] = 30  # -0.2
        rep.customs_heat["Mediterranean"] = 25       # +0.2
        mod = get_fee_modifier(rep, "Mediterranean")
        assert 0.9 <= mod <= 1.1  # roughly cancel

    def test_port_standing_reduces_services(self):
        rep = ReputationState()
        rep.port_standing["porto_novo"] = 30
        mod = get_service_modifier(rep, "porto_novo")
        assert mod < 1.0

    def test_no_port_standing_neutral_services(self):
        rep = ReputationState()
        mod = get_service_modifier(rep, "porto_novo")
        assert mod == 1.0

    def test_heat_increases_inspections(self):
        rep = ReputationState()
        rep.customs_heat["Mediterranean"] = 25
        mod = get_inspection_modifier(rep, "Mediterranean")
        assert mod > 1.0

    def test_no_heat_neutral_inspections(self):
        rep = ReputationState()
        mod = get_inspection_modifier(rep, "Mediterranean")
        assert mod == 1.0


class TestTrustTiers:
    """Trust tiers gate future contract access."""

    def test_tiers_progress(self):
        assert get_trust_tier(ReputationState()) == "unproven"
        rep = ReputationState(commercial_trust=5)
        assert get_trust_tier(rep) == "new"
        rep.commercial_trust = 15
        assert get_trust_tier(rep) == "credible"
        rep.commercial_trust = 30
        assert get_trust_tier(rep) == "reliable"
        rep.commercial_trust = 50
        assert get_trust_tier(rep) == "trusted"


class TestCaptainDivergence:
    """Three captains diverge in reputation trajectory under similar trading."""

    def test_merchants_build_trust_fastest(self):
        """Under identical clean trades, Merchant builds trust fastest."""
        reps = {}
        for ct in ["merchant", "smuggler", "navigator"]:
            rep = ReputationState()
            for i in range(10):
                record_trade_outcome(
                    rep, ct, day=i + 1, port_id="porto_novo", region="Mediterranean",
                    good_id="grain", good_category=GoodCategory.COMMODITY,
                    quantity=5, margin_pct=60, stock_target=35, flood_penalty=0.0,
                    is_sell=True,
                )
            reps[ct] = rep.commercial_trust
        assert reps["merchant"] > reps["smuggler"]
        assert reps["merchant"] > reps["navigator"]

    def test_smuggler_accumulates_more_heat(self):
        """Under identical luxury trades, Smuggler accumulates more heat."""
        reps = {}
        for ct in ["merchant", "smuggler", "navigator"]:
            rep = ReputationState()
            for i in range(5):
                record_trade_outcome(
                    rep, ct, day=i + 1, port_id="al_manar", region="Mediterranean",
                    good_id="silk", good_category=GoodCategory.LUXURY,
                    quantity=8, margin_pct=180, stock_target=12, flood_penalty=0.1,
                    is_sell=True,
                )
            reps[ct] = rep.customs_heat["Mediterranean"]
        assert reps["smuggler"] > reps["merchant"]


class TestIncidentLog:
    """Recent incidents are recorded and capped."""

    def test_incidents_recorded(self):
        rep = ReputationState()
        record_trade_outcome(
            rep, "merchant", day=1, port_id="porto_novo", region="Mediterranean",
            good_id="grain", good_category=GoodCategory.COMMODITY,
            quantity=10, margin_pct=100, stock_target=35, flood_penalty=0.0,
            is_sell=True,
        )
        assert len(rep.recent_incidents) >= 1

    def test_incidents_capped_at_20(self):
        rep = ReputationState()
        for i in range(30):
            record_trade_outcome(
                rep, "merchant", day=i, port_id="porto_novo", region="Mediterranean",
                good_id="grain", good_category=GoodCategory.COMMODITY,
                quantity=10, margin_pct=150, stock_target=35, flood_penalty=0.0,
                is_sell=True,
            )
        assert len(rep.recent_incidents) <= 20

    def test_newest_incident_first(self):
        rep = ReputationState()
        for i in range(3):
            record_trade_outcome(
                rep, "merchant", day=i + 1, port_id="porto_novo", region="Mediterranean",
                good_id="grain", good_category=GoodCategory.COMMODITY,
                quantity=10, margin_pct=100, stock_target=35, flood_penalty=0.0,
                is_sell=True,
            )
        if len(rep.recent_incidents) >= 2:
            assert rep.recent_incidents[0].day >= rep.recent_incidents[1].day


class TestSaveLoadReputation:
    """Reputation state including incidents survives save/load."""

    def test_incidents_roundtrip(self):
        world = new_game(captain_type=CaptainType.MERCHANT)
        world.captain.standing.recent_incidents = [
            ReputationIncident(
                day=3, port_id="al_manar", region="Mediterranean",
                incident_type="trade", description="Test trade",
                heat_delta=2, standing_delta=1, trust_delta=1,
            ),
        ]
        d = world_to_dict(world)
        world2, _, _board, _infra, _campaign, _narrative = world_from_dict(d)
        assert len(world2.captain.standing.recent_incidents) == 1
        inc = world2.captain.standing.recent_incidents[0]
        assert inc.day == 3
        assert inc.heat_delta == 2
        assert inc.description == "Test trade"

    def test_full_reputation_roundtrip(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Trader", captain_type="merchant")
        # Do some trading to generate reputation
        s.captain.standing.customs_heat["West Africa"] = 15
        s.captain.standing.port_standing["porto_novo"] = 12
        s.captain.standing.commercial_trust = 20
        s._save()

        s2 = GameSession(tmp_path)
        assert s2.load()
        assert s2.captain.standing.customs_heat["West Africa"] == 15
        assert s2.captain.standing.port_standing["porto_novo"] == 12
        assert s2.captain.standing.commercial_trust == 20


class TestSessionReputation:
    """Session correctly triggers reputation mutations."""

    def test_sell_mutates_reputation(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Trader", captain_type="merchant")
        # Buy grain, sell it to trigger reputation mutation
        s.buy("grain", 10)
        # Sell at same port (low margin, should be clean)
        s.sell("grain", 10)
        # After a sell, some reputation state should have changed
        # Either trust went up (clean trade) or heat went up (suspicious)
        # At minimum, port standing should exist
        assert "porto_novo" in s.captain.standing.port_standing

    def test_reputation_ticks_on_advance(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Trader", captain_type="merchant")
        s.captain.standing.customs_heat["Mediterranean"] = 20
        s.advance()  # advance one day in port
        # Heat should have decayed
        assert s.captain.standing.customs_heat["Mediterranean"] < 20
