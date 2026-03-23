"""Tests for Packet 3D-3A — Insurance.

Law tests: content invariants for policy catalog.
Behavior tests: purchase, claims, exclusions, caps, heat gating, expiry.
Integration tests: session wiring, save/load round-trip, voyage event claims.
"""

import pytest

from portlight.content.infrastructure import (
    POLICY_CATALOG,
    available_policies,
    get_policy_spec,
)
from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.infrastructure import (
    ActivePolicy,
    InfrastructureState,
    PolicyFamily,
    PolicyScope,
    expire_voyage_policies,
    purchase_policy,
    resolve_claim,
)
from portlight.engine.save import world_from_dict, world_to_dict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def world():
    return new_game("Insurer", captain_type=CaptainType.MERCHANT)


@pytest.fixture
def infra():
    return InfrastructureState()


# ---------------------------------------------------------------------------
# Content law tests
# ---------------------------------------------------------------------------

class TestPolicyCatalogLaws:
    def test_six_policies_exist(self):
        assert len(POLICY_CATALOG) == 6

    def test_all_families_represented(self):
        families = {s.family for s in POLICY_CATALOG.values()}
        assert PolicyFamily.HULL in families
        assert PolicyFamily.PREMIUM_CARGO in families
        assert PolicyFamily.CONTRACT_GUARANTEE in families

    def test_all_have_positive_premium(self):
        for spec in POLICY_CATALOG.values():
            assert spec.premium > 0

    def test_coverage_pct_in_range(self):
        for spec in POLICY_CATALOG.values():
            assert 0 < spec.coverage_pct <= 1.0

    def test_comprehensive_covers_more_than_basic(self):
        basic = get_policy_spec("hull_basic")
        comp = get_policy_spec("hull_comprehensive")
        assert comp.coverage_pct > basic.coverage_pct
        assert comp.coverage_cap > basic.coverage_cap
        assert comp.premium > basic.premium

    def test_cargo_premium_covers_more_than_standard(self):
        std = get_policy_spec("cargo_standard")
        prem = get_policy_spec("cargo_premium")
        assert prem.coverage_pct > std.coverage_pct
        assert prem.coverage_cap > std.coverage_cap

    def test_contract_full_covers_more_than_basic(self):
        basic = get_policy_spec("contract_basic")
        full = get_policy_spec("contract_full")
        assert full.coverage_pct > basic.coverage_pct
        assert full.coverage_cap > basic.coverage_cap

    def test_all_hull_policies_cover_storm_and_pirates(self):
        for spec in POLICY_CATALOG.values():
            if spec.family == PolicyFamily.HULL:
                assert "storm" in spec.covered_risks
                assert "pirates" in spec.covered_risks

    def test_cargo_policies_exclude_contraband(self):
        for spec in POLICY_CATALOG.values():
            if spec.family == PolicyFamily.PREMIUM_CARGO:
                assert "contraband" in spec.exclusions

    def test_available_policies_sorted_by_premium(self):
        specs = available_policies()
        premiums = [s.premium for s in specs]
        assert premiums == sorted(premiums)

    def test_available_policies_filter_by_family(self):
        hull = available_policies(PolicyFamily.HULL)
        assert all(s.family == PolicyFamily.HULL for s in hull)
        assert len(hull) == 2


# ---------------------------------------------------------------------------
# Purchase tests
# ---------------------------------------------------------------------------

class TestPolicyPurchase:
    def test_purchase_basic_hull(self, world, infra):
        captain = world.captain
        spec = get_policy_spec("hull_basic")
        silver_before = captain.silver
        result = purchase_policy(infra, captain, spec, day=1)
        assert isinstance(result, ActivePolicy)
        assert result.family == PolicyFamily.HULL
        assert result.active is True
        assert captain.silver == silver_before - spec.premium

    def test_purchase_insufficient_silver(self, world, infra):
        captain = world.captain
        captain.silver = 5
        spec = get_policy_spec("hull_basic")
        result = purchase_policy(infra, captain, spec, day=1)
        assert isinstance(result, str)
        assert "Need" in result

    def test_heat_blocks_purchase(self, world, infra):
        captain = world.captain
        spec = get_policy_spec("hull_comprehensive")  # heat_max=5
        result = purchase_policy(infra, captain, spec, day=1, heat=10)
        assert isinstance(result, str)
        assert "Heat" in result

    def test_heat_increases_premium(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")
        # Purchase with heat=0
        silver_before = captain.silver
        purchase_policy(infra, captain, spec, day=1, heat=0)
        cost_clean = silver_before - captain.silver

        # Purchase a different one with heat=5
        infra2 = InfrastructureState()
        captain.silver = 5000
        silver_before = captain.silver
        purchase_policy(infra2, captain, spec, day=2, heat=5)
        cost_heated = silver_before - captain.silver

        assert cost_heated > cost_clean

    def test_duplicate_purchase_rejected(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")
        purchase_policy(infra, captain, spec, day=1)
        result = purchase_policy(infra, captain, spec, day=1)
        assert isinstance(result, str)
        assert "Already" in result

    def test_contract_guarantee_with_target(self, world, infra):
        captain = world.captain
        spec = get_policy_spec("contract_basic")
        result = purchase_policy(
            infra, captain, spec, day=1, target_id="contract-abc",
        )
        assert isinstance(result, ActivePolicy)
        assert result.target_id == "contract-abc"
        assert result.scope == PolicyScope.NAMED_CONTRACT


# ---------------------------------------------------------------------------
# Claim resolution tests
# ---------------------------------------------------------------------------

class TestClaimResolution:
    def test_hull_claim_on_storm(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")
        purchase_policy(infra, captain, spec, day=1)
        silver_after_purchase = captain.silver

        claims = resolve_claim(
            infra, captain, "storm", loss_value=100, day=2,
        )
        assert len(claims) == 1
        assert claims[0].payout > 0
        assert claims[0].payout == int(100 * spec.coverage_pct)
        assert captain.silver == silver_after_purchase + claims[0].payout

    def test_hull_claim_capped(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")  # cap=150
        purchase_policy(infra, captain, spec, day=1)

        # Massive loss exceeds cap
        claims = resolve_claim(
            infra, captain, "storm", loss_value=1000, day=2,
        )
        assert len(claims) == 1
        assert claims[0].payout <= spec.coverage_cap

    def test_hull_claim_not_on_inspection(self, world, infra):
        """Hull policy doesn't cover inspection events."""
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")
        purchase_policy(infra, captain, spec, day=1)

        claims = resolve_claim(
            infra, captain, "inspection", loss_value=100, day=2,
        )
        assert len(claims) == 0

    def test_cargo_claim_on_pirates(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("cargo_standard")
        purchase_policy(infra, captain, spec, day=1)

        claims = resolve_claim(
            infra, captain, "pirates", loss_value=200, day=2,
            cargo_category="luxury",
        )
        assert len(claims) == 1
        assert claims[0].payout > 0

    def test_cargo_claim_denied_for_contraband(self, world, infra):
        """Contraband exclusion blocks payout."""
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("cargo_standard")
        purchase_policy(infra, captain, spec, day=1)

        claims = resolve_claim(
            infra, captain, "inspection", loss_value=200, day=2,
            cargo_category="contraband",
        )
        assert len(claims) == 1
        assert claims[0].denied is True
        assert claims[0].payout == 0
        assert "Contraband" in claims[0].denial_reason

    def test_contract_guarantee_on_failure(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("contract_basic")
        purchase_policy(
            infra, captain, spec, day=1, target_id="contract-xyz",
        )
        silver_after = captain.silver

        claims = resolve_claim(
            infra, captain, "contract_failure", loss_value=200, day=10,
            contract_id="contract-xyz",
        )
        assert len(claims) == 1
        assert claims[0].payout > 0
        assert captain.silver > silver_after

    def test_contract_guarantee_wrong_contract_no_match(self, world, infra):
        """Guarantee for contract A doesn't cover contract B failure."""
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("contract_basic")
        purchase_policy(
            infra, captain, spec, day=1, target_id="contract-aaa",
        )

        claims = resolve_claim(
            infra, captain, "contract_failure", loss_value=200, day=10,
            contract_id="contract-bbb",
        )
        assert len(claims) == 0

    def test_cumulative_claims_reduce_remaining_cap(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")  # cap=150
        purchase_policy(infra, captain, spec, day=1)

        # First claim
        resolve_claim(infra, captain, "storm", loss_value=200, day=2)
        policy = infra.policies[0]
        first_payout = policy.total_paid_out
        assert first_payout > 0

        # Second claim should have reduced cap
        resolve_claim(infra, captain, "pirates", loss_value=200, day=3)
        second_payout = policy.total_paid_out - first_payout
        assert second_payout < first_payout or second_payout == 0  # cap running out

    def test_inactive_policy_ignored(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")
        purchase_policy(infra, captain, spec, day=1)
        infra.policies[0].active = False

        claims = resolve_claim(infra, captain, "storm", loss_value=100, day=2)
        assert len(claims) == 0


# ---------------------------------------------------------------------------
# Policy expiry tests
# ---------------------------------------------------------------------------

class TestPolicyExpiry:
    def test_voyage_policies_expire_on_arrival(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")  # scope=NEXT_VOYAGE
        purchase_policy(infra, captain, spec, day=1)
        assert infra.policies[0].active is True

        msgs = expire_voyage_policies(infra)
        assert infra.policies[0].active is False
        assert len(msgs) > 0

    def test_contract_policy_survives_arrival(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("contract_basic")  # scope=NAMED_CONTRACT
        purchase_policy(infra, captain, spec, day=1, target_id="c1")
        assert infra.policies[0].active is True

        expire_voyage_policies(infra)
        assert infra.policies[0].active is True  # not expired


# ---------------------------------------------------------------------------
# Save/load round-trip
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_policy_round_trip(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")
        purchase_policy(infra, captain, spec, day=5)

        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)

        assert len(loaded_infra.policies) == 1
        p = loaded_infra.policies[0]
        assert p.spec_id == "hull_basic"
        assert p.family == PolicyFamily.HULL
        assert p.active is True

    def test_claim_round_trip(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        spec = get_policy_spec("hull_basic")
        purchase_policy(infra, captain, spec, day=5)
        resolve_claim(infra, captain, "storm", loss_value=100, day=6)

        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)

        assert len(loaded_infra.claims) == 1
        c = loaded_infra.claims[0]
        assert c.incident_type == "storm"
        assert c.payout > 0

    def test_old_save_without_policies_loads(self, world):
        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        infra = InfrastructureState()
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        del d["infrastructure"]["policies"]
        del d["infrastructure"]["claims"]
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)
        assert loaded_infra.policies == []
        assert loaded_infra.claims == []


# ---------------------------------------------------------------------------
# Session integration
# ---------------------------------------------------------------------------

class TestSessionIntegration:
    def test_purchase_policy_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Policy Tester")
        silver_before = s.captain.silver

        spec = get_policy_spec("hull_basic")
        err = s.purchase_policy_cmd(spec)
        assert err is None
        assert s.captain.silver < silver_before
        assert len(s.infra.policies) == 1

    def test_policy_survives_save_load(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Persist Tester")
        spec = get_policy_spec("hull_basic")
        s.purchase_policy_cmd(spec)

        s2 = GameSession(base_path=tmp_path)
        assert s2.load()
        assert len(s2.infra.policies) == 1
        assert s2.infra.policies[0].spec_id == "hull_basic"

    def test_voyage_event_triggers_claim(self, tmp_path):
        """Simulate a storm event and verify insurance resolves."""
        from portlight.app.session import GameSession
        from portlight.engine.voyage import EventType, VoyageEvent

        s = GameSession(base_path=tmp_path)
        s.new("Claim Tester")
        spec = get_policy_spec("hull_basic")
        s.purchase_policy_cmd(spec)
        silver_after_policy = s.captain.silver

        # Simulate a storm event manually via the helper
        storm_event = VoyageEvent(
            event_type=EventType.STORM,
            message="A fierce storm!",
            hull_delta=-10,
        )
        s._resolve_event_insurance(storm_event, voyage_destination="al_manar")

        # Should have received a payout
        assert s.captain.silver > silver_after_policy
        assert len(s.infra.claims) == 1

    def test_policies_expire_on_arrival_in_session(self, tmp_path):
        """Voyage policies should expire when ship arrives."""
        from portlight.app.session import GameSession

        s = GameSession(base_path=tmp_path)
        s.new("Arrival Tester")
        s.auto_resolve_duels = True
        spec = get_policy_spec("hull_basic")
        s.purchase_policy_cmd(spec)
        assert s.infra.policies[0].active is True

        # Sail somewhere and advance until arrival
        err = s.sail("al_manar")
        if err is None:
            for _ in range(30):
                s.advance()
                if s.current_port is not None:
                    break

        # After arrival, voyage policies should be expired
        if s.current_port is not None:
            assert s.infra.policies[0].active is False
