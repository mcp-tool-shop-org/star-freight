"""Save/load crisis tests — compound state survives round-trip without invariant violations.

These tests build up complex game states (credit + insurance + warehouse +
contracts + heat) then save, reload, and verify that all invariants still hold
and that the state is semantically equivalent.
"""

from __future__ import annotations

from pathlib import Path


from portlight.app.session import GameSession
from portlight.engine.campaign import MilestoneCompletion, VictoryCompletion
from portlight.engine.contracts import ActiveContract, ContractFamily, ContractOutcome
from portlight.engine.infrastructure import (
    ActivePolicy,
    CreditState,
    CreditTier,
    InsuranceClaim,
    OwnedLicense,
    PolicyFamily,
    PolicyScope,
    StoredLot,
    WarehouseLease,
    WarehouseTier,
)
from portlight.stress.invariants import check_all_invariants


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_session(tmp_path: Path, captain_type: str = "merchant") -> GameSession:
    s = GameSession(base_path=tmp_path)
    s.new("CrisisBot", captain_type=captain_type)
    return s


def _reload_session(tmp_path: Path) -> GameSession:
    s = GameSession(base_path=tmp_path)
    loaded = s.load()
    assert loaded, "Failed to load saved game"
    return s


# ---------------------------------------------------------------------------
# Credit + insurance round-trip
# ---------------------------------------------------------------------------

class TestCreditInsuranceRoundTrip:
    def test_active_credit_survives_save_load(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=500,
            outstanding=200,
            interest_accrued=15,
            last_interest_day=5,
            next_due_day=15,
            defaults=1,
            total_borrowed=300,
            total_repaid=100,
            active=True,
        )
        s._save()
        s2 = _reload_session(tmp_path)

        cred = s2.infra.credit
        assert cred is not None
        assert cred.outstanding == 200
        assert cred.interest_accrued == 15
        assert cred.defaults == 1
        assert cred.active is True

        failures = check_all_invariants(s2)
        assert failures == []

    def test_insurance_claims_survive_save_load(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.claims.append(InsuranceClaim(
            policy_id="hull_basic",
            day=3,
            incident_type="storm",
            loss_value=200,
            payout=100,
        ))
        s.infra.claims.append(InsuranceClaim(
            policy_id="cargo_basic",
            day=5,
            incident_type="pirates",
            loss_value=150,
            payout=0,
            denied=True,
            denial_reason="contraband",
        ))
        s._save()
        s2 = _reload_session(tmp_path)

        assert len(s2.infra.claims) == 2
        assert s2.infra.claims[0].payout == 100
        assert s2.infra.claims[1].denied is True

        failures = check_all_invariants(s2)
        assert failures == []

    def test_credit_plus_insurance_compound(self, tmp_path):
        """Active credit + outstanding debt + claims all round-trip together."""
        s = _fresh_session(tmp_path)
        s.infra.credit = CreditState(
            tier=CreditTier.HOUSE_CREDIT,
            credit_limit=1000,
            outstanding=500,
            defaults=0,
            active=True,
        )
        s.infra.policies.append(ActivePolicy(
            id="pol1",
            spec_id="hull_basic",
            family=PolicyFamily.HULL,
            scope=PolicyScope.ACTIVE_CARGO,
            purchased_day=1,
            coverage_pct=0.8,
            coverage_cap=200,
            premium_paid=50,
            active=True,
        ))
        s.infra.claims.append(InsuranceClaim(
            policy_id="hull_basic",
            day=5,
            incident_type="storm",
            loss_value=150,
            payout=120,
        ))
        s._save()
        s2 = _reload_session(tmp_path)

        assert s2.infra.credit.outstanding == 500
        assert len(s2.infra.policies) == 1
        assert len(s2.infra.claims) == 1
        failures = check_all_invariants(s2)
        assert failures == []


# ---------------------------------------------------------------------------
# Warehouse with partial upkeep
# ---------------------------------------------------------------------------

class TestWarehouseRoundTrip:
    def test_warehouse_with_inventory_survives(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.warehouses.append(WarehouseLease(
            id="wh_test",
            port_id="porto_novo",
            tier=WarehouseTier.DEPOT,
            capacity=50,
            lease_cost=100,
            upkeep_per_day=5,
            inventory=[StoredLot(
                good_id="grain", quantity=20,
                acquired_port="porto_novo", acquired_region="Mediterranean",
                acquired_day=1, deposited_day=2,
            )],
            active=True,
            upkeep_paid_through=3,
        ))
        s._save()
        s2 = _reload_session(tmp_path)

        assert len(s2.infra.warehouses) == 1
        wh = s2.infra.warehouses[0]
        assert wh.active is True
        assert len(wh.inventory) == 1
        assert wh.inventory[0].quantity == 20
        assert wh.upkeep_paid_through == 3

        failures = check_all_invariants(s2)
        assert failures == []

    def test_inactive_warehouse_empty_survives(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.infra.warehouses.append(WarehouseLease(
            id="wh_closed",
            port_id="silva_bay",
            tier=WarehouseTier.REGIONAL,
            capacity=100,
            lease_cost=200,
            upkeep_per_day=10,
            inventory=[],
            active=False,
        ))
        s._save()
        s2 = _reload_session(tmp_path)

        assert len(s2.infra.warehouses) == 1
        assert s2.infra.warehouses[0].active is False
        failures = check_all_invariants(s2)
        assert failures == []


# ---------------------------------------------------------------------------
# Contracts + heat round-trip
# ---------------------------------------------------------------------------

class TestContractsHeatRoundTrip:
    def test_active_contracts_with_partial_delivery(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.board.active.append(ActiveContract(
            offer_id="c1",
            template_id="t1",
            family=ContractFamily.PROCUREMENT,
            title="Grain to Porto Novo",
            accepted_day=1,
            deadline_day=20,
            destination_port_id="porto_novo",
            good_id="grain",
            required_quantity=20,
            delivered_quantity=8,
            reward_silver=500,
        ))
        # High heat
        s.captain.standing.customs_heat["Mediterranean"] = 20

        s._save()
        s2 = _reload_session(tmp_path)

        assert len(s2.board.active) == 1
        assert s2.board.active[0].delivered_quantity == 8
        assert s2.captain.standing.customs_heat["Mediterranean"] == 20

        failures = check_all_invariants(s2)
        assert failures == []

    def test_completed_contracts_survive(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.board.completed.append(ContractOutcome(
            contract_id="c_done",
            outcome_type="completed",
            silver_delta=300,
            trust_delta=2,
            standing_delta=1,
            heat_delta=0,
            completion_day=10,
            summary="Delivered grain",
        ))
        s._save()
        s2 = _reload_session(tmp_path)

        assert len(s2.board.completed) == 1
        assert s2.board.completed[0].contract_id == "c_done"
        failures = check_all_invariants(s2)
        assert failures == []


# ---------------------------------------------------------------------------
# Campaign state round-trip
# ---------------------------------------------------------------------------

class TestCampaignRoundTrip:
    def test_milestones_and_paths_survive(self, tmp_path):
        s = _fresh_session(tmp_path)
        s.campaign.completed = [
            MilestoneCompletion(milestone_id="m1", completed_day=10, evidence="traded 50 grain"),
            MilestoneCompletion(milestone_id="m2", completed_day=20, evidence="reached East Indies"),
        ]
        s.campaign.completed_paths = [
            VictoryCompletion(
                path_id="shadow_network", completion_day=50,
                summary="Built the network", is_first=True,
            ),
        ]
        s._save()
        s2 = _reload_session(tmp_path)

        assert len(s2.campaign.completed) == 2
        assert len(s2.campaign.completed_paths) == 1
        assert s2.campaign.completed_paths[0].is_first is True

        failures = check_all_invariants(s2)
        assert failures == []


# ---------------------------------------------------------------------------
# Full compound state — everything in flight
# ---------------------------------------------------------------------------

class TestFullCompoundState:
    def test_everything_in_flight_round_trips(self, tmp_path):
        """Credit + warehouse + contracts + insurance + campaign + heat."""
        s = _fresh_session(tmp_path)

        # Credit
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=500,
            outstanding=150,
            defaults=1,
            active=True,
        )

        # Warehouse with cargo
        s.infra.warehouses.append(WarehouseLease(
            id="wh_full",
            port_id="porto_novo",
            tier=WarehouseTier.DEPOT,
            capacity=50,
            lease_cost=100,
            upkeep_per_day=5,
            inventory=[StoredLot(
                good_id="silk", quantity=10,
                acquired_port="al_manar", acquired_region="East Indies",
                acquired_day=5, deposited_day=8,
            )],
            active=True,
        ))

        # License
        s.infra.licenses.append(OwnedLicense(
            license_id="general_trade",
            purchased_day=3,
            upkeep_paid_through=10,
            active=True,
        ))

        # Insurance
        s.infra.policies.append(ActivePolicy(
            id="pol2",
            spec_id="cargo_basic",
            family=PolicyFamily.PREMIUM_CARGO,
            scope=PolicyScope.ACTIVE_CARGO,
            purchased_day=2,
            coverage_pct=0.7,
            coverage_cap=300,
            premium_paid=40,
            active=True,
        ))

        # Active contract with partial delivery
        s.board.active.append(ActiveContract(
            offer_id="c_inflight",
            template_id="t1",
            family=ContractFamily.PROCUREMENT,
            title="Silk to Porto Novo",
            accepted_day=5,
            deadline_day=25,
            destination_port_id="porto_novo",
            good_id="silk",
            required_quantity=15,
            delivered_quantity=5,
            reward_silver=800,
        ))

        # Heat
        s.captain.standing.customs_heat["Mediterranean"] = 15
        s.captain.standing.customs_heat["West Africa"] = 8

        # Campaign progress
        s.campaign.completed = [
            MilestoneCompletion(milestone_id="m1", completed_day=10),
        ]

        s._save()
        s2 = _reload_session(tmp_path)

        # Verify all subsystems survived
        assert s2.infra.credit.outstanding == 150
        assert len(s2.infra.warehouses) == 1
        assert s2.infra.warehouses[0].inventory[0].good_id == "silk"
        assert len(s2.infra.licenses) == 1
        assert len(s2.infra.policies) == 1
        assert len(s2.board.active) == 1
        assert s2.board.active[0].delivered_quantity == 5
        assert s2.captain.standing.customs_heat["Mediterranean"] == 15
        assert len(s2.campaign.completed) == 1

        # Invariants hold after reload
        failures = check_all_invariants(s2)
        assert failures == [], f"Invariant failures after reload: {failures}"

    def test_stress_scenario_save_load(self, tmp_path):
        """Run a stress scenario partway, save, reload, check invariants."""
        from portlight.stress.runner import run_stress_scenario
        from portlight.stress.scenarios import STRESS_SCENARIOS

        scenario = STRESS_SCENARIOS["save_load_mid_crisis"]
        # Run the scenario (it already saves internally via session._save)
        report = run_stress_scenario(scenario)
        assert report.days_survived > 0
        # The runner already checks invariants every tick — if we got here,
        # invariants held throughout the run including saves
        assert report.passed, (
            f"save_load_mid_crisis violated invariants: "
            f"{[inv.name for inv in report.invariant_results]}"
        )
