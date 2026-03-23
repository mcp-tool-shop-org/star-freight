"""Tests for cross-system invariants — prove that every law detects violations."""

from __future__ import annotations

from pathlib import Path


from portlight.app.session import GameSession
from portlight.engine.campaign import (
    MilestoneCompletion,
    VictoryCompletion,
)
from portlight.engine.contracts import ActiveContract, ContractFamily, ContractOutcome
from portlight.engine.infrastructure import (
    CreditState,
    CreditTier,  # NONE, MERCHANT_LINE, HOUSE_CREDIT, PREMIER_COMMERCIAL
    InsuranceClaim,
    StoredLot,
    WarehouseLease,
    WarehouseTier,
)
from portlight.engine.models import CargoItem
from portlight.stress.invariants import check_all_invariants, _ALL_CHECKS
from portlight.stress.types import InvariantResult, Subsystem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_session(tmp_path: Path, captain_type: str = "merchant") -> GameSession:
    """Create a clean session for invariant testing."""
    s = GameSession(base_path=tmp_path)
    s.new("Tester", captain_type=captain_type)
    return s


# ---------------------------------------------------------------------------
# Clean state — all invariants pass
# ---------------------------------------------------------------------------

class TestCleanState:
    def test_fresh_session_passes_all(self, tmp_path):
        s = _fresh_session(tmp_path)
        failures = check_all_invariants(s)
        assert failures == [], f"Fresh session has invariant failures: {failures}"

    def test_all_checks_registered(self):
        assert len(_ALL_CHECKS) == 19  # 14 original + 5 ship expansion

    def test_each_check_returns_invariant_result(self, tmp_path):
        s = _fresh_session(tmp_path)
        for checker in _ALL_CHECKS:
            result = checker(s)
            assert isinstance(result, InvariantResult)
            assert result.passed is True


# ---------------------------------------------------------------------------
# Economy invariant violations
# ---------------------------------------------------------------------------

class TestEconomyInvariants:
    def test_negative_silver_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.captain.silver = -10
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_negative_silver" in names
        assert failures[0].subsystem == Subsystem.ECONOMY

    def test_negative_cargo_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.captain.cargo.append(CargoItem(good_id="grain", quantity=-5))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_negative_cargo" in names

    def test_cargo_over_capacity_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        cap = s.captain.ship.cargo_capacity
        s.captain.cargo.append(CargoItem(good_id="grain", quantity=cap + 10))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "cargo_within_capacity" in names

    def test_cargo_at_capacity_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        cap = s.captain.ship.cargo_capacity
        s.captain.cargo.append(CargoItem(good_id="grain", quantity=cap))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "cargo_within_capacity" not in names

    def test_negative_market_stock_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        port = next(iter(s.world.ports.values()))
        port.market[0].stock_current = -1
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "market_stock_valid" in names


# ---------------------------------------------------------------------------
# Contract invariant violations
# ---------------------------------------------------------------------------

class TestContractInvariants:
    def test_dual_resolution_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        shared_id = "contract_abc"
        s.board.active.append(ActiveContract(
            offer_id=shared_id,
            template_id="t1",
            family=ContractFamily.PROCUREMENT,
            title="Test",
            accepted_day=1,
            deadline_day=30,
            destination_port_id="porto_novo",
            good_id="grain",
            required_quantity=10,
        ))
        s.board.completed.append(ContractOutcome(
            contract_id=shared_id,
            outcome_type="completed",
            silver_delta=100,
            trust_delta=1,
            standing_delta=1,
            heat_delta=0,
            completion_day=15,
            summary="done",
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_dual_contract_resolution" in names

    def test_delivered_exceeds_required_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.board.active.append(ActiveContract(
            offer_id="c1",
            template_id="t1",
            family=ContractFamily.PROCUREMENT,
            title="Over-delivered",
            accepted_day=1,
            deadline_day=30,
            destination_port_id="porto_novo",
            good_id="grain",
            required_quantity=10,
            delivered_quantity=15,
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "delivered_within_required" in names

    def test_partial_delivery_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.board.active.append(ActiveContract(
            offer_id="c2",
            template_id="t1",
            family=ContractFamily.PROCUREMENT,
            title="Partial",
            accepted_day=1,
            deadline_day=30,
            destination_port_id="porto_novo",
            good_id="grain",
            required_quantity=10,
            delivered_quantity=5,
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "delivered_within_required" not in names


# ---------------------------------------------------------------------------
# Infrastructure invariant violations
# ---------------------------------------------------------------------------

class TestInfrastructureInvariants:
    def test_inactive_warehouse_with_inventory_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.warehouses.append(WarehouseLease(
            id="wh_test",
            port_id="porto_novo",
            tier=WarehouseTier.DEPOT,
            capacity=50,
            lease_cost=100,
            upkeep_per_day=5,
            inventory=[StoredLot(
                good_id="grain", quantity=10,
                acquired_port="porto_novo", acquired_region="Mediterranean",
                acquired_day=1, deposited_day=2,
            )],
            active=False,
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "inactive_warehouse_empty" in names

    def test_inactive_warehouse_empty_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.warehouses.append(WarehouseLease(
            id="wh_test2",
            port_id="porto_novo",
            tier=WarehouseTier.DEPOT,
            capacity=50,
            lease_cost=100,
            upkeep_per_day=5,
            inventory=[],
            active=False,
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "inactive_warehouse_empty" not in names

    def test_warehouse_over_capacity_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.warehouses.append(WarehouseLease(
            id="wh_over",
            port_id="porto_novo",
            tier=WarehouseTier.DEPOT,
            capacity=20,
            lease_cost=100,
            upkeep_per_day=5,
            inventory=[StoredLot(
                good_id="grain", quantity=30,
                acquired_port="porto_novo", acquired_region="Mediterranean",
                acquired_day=1, deposited_day=2,
            )],
            active=True,
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "warehouse_within_capacity" in names


# ---------------------------------------------------------------------------
# Insurance invariant violations
# ---------------------------------------------------------------------------

class TestInsuranceInvariants:
    def test_overclaimed_policy_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        # hull_basic has coverage_cap of 200 in content
        s.infra.claims.append(InsuranceClaim(
            policy_id="hull_basic",
            day=5,
            incident_type="storm",
            loss_value=500,
            payout=9999,  # way over any cap
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_overclaimed_policy" in names

    def test_claim_within_cap_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.claims.append(InsuranceClaim(
            policy_id="hull_basic",
            day=5,
            incident_type="storm",
            loss_value=100,
            payout=50,
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_overclaimed_policy" not in names

    def test_denied_claim_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.claims.append(InsuranceClaim(
            policy_id="hull_basic",
            day=5,
            incident_type="storm",
            loss_value=100,
            payout=0,
            denied=True,
            denial_reason="contraband",
        ))
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_overclaimed_policy" not in names


# ---------------------------------------------------------------------------
# Credit invariant violations
# ---------------------------------------------------------------------------

class TestCreditInvariants:
    def test_credit_overdraw_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=500,
            outstanding=600,
            active=True,
        )
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_credit_overdraw" in names

    def test_credit_at_limit_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=500,
            outstanding=500,
            active=True,
        )
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_credit_overdraw" not in names

    def test_frozen_credit_active_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=500,
            outstanding=100,
            defaults=3,
            active=True,  # should be frozen after 3 defaults
        )
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "frozen_credit_no_draw" in names

    def test_frozen_credit_inactive_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=500,
            outstanding=100,
            defaults=3,
            active=False,
        )
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "frozen_credit_no_draw" not in names

    def test_no_credit_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.credit = None
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "no_credit_overdraw" not in names
        assert "frozen_credit_no_draw" not in names


# ---------------------------------------------------------------------------
# Campaign invariant violations
# ---------------------------------------------------------------------------

class TestCampaignInvariants:
    def test_duplicate_milestones_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.campaign.completed = [
            MilestoneCompletion(milestone_id="m1", completed_day=5),
            MilestoneCompletion(milestone_id="m1", completed_day=10),
        ]
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "completed_milestones_no_dupes" in names

    def test_unique_milestones_pass(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.campaign.completed = [
            MilestoneCompletion(milestone_id="m1", completed_day=5),
            MilestoneCompletion(milestone_id="m2", completed_day=10),
        ]
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "completed_milestones_no_dupes" not in names

    def test_duplicate_paths_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.campaign.completed_paths = [
            VictoryCompletion(path_id="shadow_network", completion_day=50, summary="a", is_first=True),
            VictoryCompletion(path_id="shadow_network", completion_day=60, summary="b"),
        ]
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "completed_paths_no_dupes" in names

    def test_multiple_first_paths_detected(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.campaign.completed_paths = [
            VictoryCompletion(path_id="shadow_network", completion_day=50, summary="a", is_first=True),
            VictoryCompletion(path_id="oceanic_reach", completion_day=60, summary="b", is_first=True),
        ]
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "first_path_stays_first" in names

    def test_single_first_path_passes(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.campaign.completed_paths = [
            VictoryCompletion(path_id="shadow_network", completion_day=50, summary="a", is_first=True),
            VictoryCompletion(path_id="oceanic_reach", completion_day=60, summary="b", is_first=False),
        ]
        failures = check_all_invariants(s)
        names = [f.name for f in failures]
        assert "first_path_stays_first" not in names


# ---------------------------------------------------------------------------
# Compound violations — multiple invariants break at once
# ---------------------------------------------------------------------------

class TestCompoundViolations:
    def test_multiple_subsystem_failures(self, tmp_path):
        """Stack violations across economy + credit + campaign simultaneously."""
        s = _fresh_session(tmp_path)
        # Economy: negative silver
        s.captain.silver = -50
        # Credit: overdraw
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=100,
            outstanding=200,
            active=True,
        )
        # Campaign: duplicate milestones
        s.campaign.completed = [
            MilestoneCompletion(milestone_id="m1", completed_day=5),
            MilestoneCompletion(milestone_id="m1", completed_day=10),
        ]
        failures = check_all_invariants(s)
        subsystems = {f.subsystem for f in failures}
        assert Subsystem.ECONOMY in subsystems
        assert Subsystem.CREDIT in subsystems
        assert Subsystem.CAMPAIGN in subsystems
        assert len(failures) >= 3

    def test_failure_messages_are_informative(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.captain.silver = -42
        failures = check_all_invariants(s)
        silver_fail = next(f for f in failures if f.name == "no_negative_silver")
        assert "-42" in silver_fail.message
