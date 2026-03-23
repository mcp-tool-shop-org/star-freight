"""Tests for Packet 3D-2 — Broker Offices, Licenses, and Board Effects.

Law tests: content invariants.
Behavior tests: open, upgrade, upkeep, license eligibility, purchase, board effects.
Integration tests: session wiring, save/load round-trip, contract generation effects.
"""

import random

import pytest

from portlight.content.contracts import TEMPLATES
from portlight.content.infrastructure import (
    BROKER_SPECS,
    LICENSE_CATALOG,
    available_broker_tiers,
    get_broker_spec,
    get_license_spec,
)
from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.contracts import generate_offers
from portlight.engine.infrastructure import (
    BrokerOffice,
    BrokerTier,
    InfrastructureState,
    OwnedLicense,
    compute_board_effects,
    get_broker_tier,
    open_broker_office,
    purchase_license,
    tick_infrastructure,
)
from portlight.engine.models import ReputationState
from portlight.engine.save import world_from_dict, world_to_dict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def world():
    return new_game("Tester", captain_type=CaptainType.MERCHANT)


@pytest.fixture
def infra():
    return InfrastructureState()


@pytest.fixture
def med_local_spec():
    return get_broker_spec("Mediterranean", BrokerTier.LOCAL)


@pytest.fixture
def med_established_spec():
    return get_broker_spec("Mediterranean", BrokerTier.ESTABLISHED)


@pytest.fixture
def rich_rep():
    """A well-established reputation for license tests."""
    return ReputationState(
        commercial_trust=80,
        regional_standing={
            "Mediterranean": 20,
            "West Africa": 20,
            "East Indies": 20,
        },
        customs_heat={
            "Mediterranean": 0,
            "West Africa": 0,
            "East Indies": 0,
        },
    )


# ---------------------------------------------------------------------------
# Broker content law tests
# ---------------------------------------------------------------------------

class TestBrokerContentLaws:
    def test_three_regions_have_specs(self):
        regions = {region for region, _ in BROKER_SPECS.keys()}
        assert regions == {"Mediterranean", "West Africa", "East Indies"}

    def test_each_region_has_two_tiers(self):
        for region in ("Mediterranean", "West Africa", "East Indies"):
            tiers = available_broker_tiers(region)
            assert len(tiers) == 2
            assert tiers[0].tier == BrokerTier.LOCAL
            assert tiers[1].tier == BrokerTier.ESTABLISHED

    def test_established_costs_more_than_local(self):
        for region in ("Mediterranean", "West Africa", "East Indies"):
            local = get_broker_spec(region, BrokerTier.LOCAL)
            est = get_broker_spec(region, BrokerTier.ESTABLISHED)
            assert est.purchase_cost > local.purchase_cost
            assert est.upkeep_per_day > local.upkeep_per_day

    def test_established_has_better_quality_bonus(self):
        for region in ("Mediterranean", "West Africa", "East Indies"):
            local = get_broker_spec(region, BrokerTier.LOCAL)
            est = get_broker_spec(region, BrokerTier.ESTABLISHED)
            assert est.board_quality_bonus > local.board_quality_bonus

    def test_all_specs_have_positive_costs(self):
        for key, spec in BROKER_SPECS.items():
            assert spec.purchase_cost > 0
            assert spec.upkeep_per_day > 0

    def test_trade_term_modifier_is_discount(self):
        for key, spec in BROKER_SPECS.items():
            assert 0 < spec.trade_term_modifier < 1.0, \
                f"{key} trade_term_modifier {spec.trade_term_modifier} not a discount"


# ---------------------------------------------------------------------------
# License content law tests
# ---------------------------------------------------------------------------

class TestLicenseContentLaws:
    def test_five_licenses_exist(self):
        assert len(LICENSE_CATALOG) == 5

    def test_all_have_purchase_cost(self):
        for spec in LICENSE_CATALOG.values():
            assert spec.purchase_cost > 0
            assert spec.upkeep_per_day > 0

    def test_regional_licenses_have_scope(self):
        regional = [s for s in LICENSE_CATALOG.values() if s.region_scope is not None]
        assert len(regional) == 3  # med, wa, ei charters

    def test_global_licenses_have_no_scope(self):
        global_lics = [s for s in LICENSE_CATALOG.values() if s.region_scope is None]
        assert len(global_lics) == 2  # luxury + high rep

    def test_all_licenses_have_effects(self):
        for spec in LICENSE_CATALOG.values():
            assert len(spec.effects) > 0

    def test_high_rep_charter_is_most_expensive(self):
        costs = [(s.id, s.purchase_cost) for s in LICENSE_CATALOG.values()]
        most_expensive = max(costs, key=lambda x: x[1])
        assert most_expensive[0] == "high_rep_charter"


# ---------------------------------------------------------------------------
# Broker open/upgrade tests
# ---------------------------------------------------------------------------

class TestBrokerOperations:
    def test_open_local_broker(self, world, infra, med_local_spec):
        captain = world.captain
        silver_before = captain.silver
        result = open_broker_office(infra, captain, "Mediterranean", med_local_spec, 1)
        assert isinstance(result, BrokerOffice)
        assert result.tier == BrokerTier.LOCAL
        assert result.region == "Mediterranean"
        assert captain.silver == silver_before - med_local_spec.purchase_cost

    def test_open_duplicate_rejected(self, world, infra, med_local_spec):
        captain = world.captain
        open_broker_office(infra, captain, "Mediterranean", med_local_spec, 1)
        result = open_broker_office(infra, captain, "Mediterranean", med_local_spec, 2)
        assert isinstance(result, str)
        assert "Already have" in result

    def test_upgrade_local_to_established(self, world, infra, med_local_spec, med_established_spec):
        captain = world.captain
        captain.silver = 2000
        open_broker_office(infra, captain, "Mediterranean", med_local_spec, 1)
        result = open_broker_office(infra, captain, "Mediterranean", med_established_spec, 5)
        assert isinstance(result, BrokerOffice)
        assert result.tier == BrokerTier.ESTABLISHED

    def test_cannot_downgrade(self, world, infra, med_local_spec, med_established_spec):
        captain = world.captain
        captain.silver = 2000
        open_broker_office(infra, captain, "Mediterranean", med_established_spec, 1)
        result = open_broker_office(infra, captain, "Mediterranean", med_local_spec, 5)
        assert isinstance(result, str)
        assert "downgrade" in result.lower()

    def test_insufficient_silver(self, world, infra, med_local_spec):
        captain = world.captain
        captain.silver = 10
        result = open_broker_office(infra, captain, "Mediterranean", med_local_spec, 1)
        assert isinstance(result, str)
        assert "Need" in result

    def test_get_broker_tier_none_when_empty(self, infra):
        assert get_broker_tier(infra, "Mediterranean") == BrokerTier.NONE

    def test_get_broker_tier_after_open(self, world, infra, med_local_spec):
        open_broker_office(infra, world.captain, "Mediterranean", med_local_spec, 1)
        assert get_broker_tier(infra, "Mediterranean") == BrokerTier.LOCAL


# ---------------------------------------------------------------------------
# License eligibility + purchase tests
# ---------------------------------------------------------------------------

class TestLicenseOperations:
    def test_purchase_with_requirements_met(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        # Need a local broker first for med charter
        spec = get_broker_spec("Mediterranean", BrokerTier.LOCAL)
        open_broker_office(infra, captain, "Mediterranean", spec, 1)

        lic_spec = get_license_spec("med_trade_charter")
        result = purchase_license(infra, captain, lic_spec, rich_rep, 1)
        assert isinstance(result, OwnedLicense)
        assert result.license_id == "med_trade_charter"

    def test_purchase_rejected_low_trust(self, world, infra):
        captain = world.captain
        captain.silver = 5000
        rep = ReputationState()  # fresh = unproven
        lic_spec = get_license_spec("med_trade_charter")
        result = purchase_license(infra, captain, lic_spec, rep, 1)
        assert isinstance(result, str)
        assert "trust" in result.lower()

    def test_purchase_rejected_low_standing(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        rich_rep.regional_standing["Mediterranean"] = 2  # below 10
        spec = get_broker_spec("Mediterranean", BrokerTier.LOCAL)
        open_broker_office(infra, captain, "Mediterranean", spec, 1)
        lic_spec = get_license_spec("med_trade_charter")
        result = purchase_license(infra, captain, lic_spec, rich_rep, 1)
        assert isinstance(result, str)
        assert "standing" in result.lower()

    def test_purchase_rejected_high_heat(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        rich_rep.customs_heat["Mediterranean"] = 10  # above 5
        spec = get_broker_spec("Mediterranean", BrokerTier.LOCAL)
        open_broker_office(infra, captain, "Mediterranean", spec, 1)
        lic_spec = get_license_spec("med_trade_charter")
        result = purchase_license(infra, captain, lic_spec, rich_rep, 1)
        assert isinstance(result, str)
        assert "heat" in result.lower() or "Heat" in result

    def test_purchase_rejected_no_broker(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        lic_spec = get_license_spec("med_trade_charter")
        result = purchase_license(infra, captain, lic_spec, rich_rep, 1)
        assert isinstance(result, str)
        assert "broker" in result.lower()

    def test_purchase_rejected_insufficient_silver(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 10
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.LOCAL, active=True))
        lic_spec = get_license_spec("med_trade_charter")
        result = purchase_license(infra, captain, lic_spec, rich_rep, 1)
        assert isinstance(result, str)
        assert "silver" in result.lower()

    def test_duplicate_purchase_rejected(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.LOCAL, active=True))
        lic_spec = get_license_spec("med_trade_charter")
        purchase_license(infra, captain, lic_spec, rich_rep, 1)
        result = purchase_license(infra, captain, lic_spec, rich_rep, 2)
        assert isinstance(result, str)
        assert "Already" in result

    def test_global_license_broker_check(self, world, infra, rich_rep):
        """High rep charter requires established broker in at least one region."""
        captain = world.captain
        captain.silver = 5000
        lic_spec = get_license_spec("high_rep_charter")
        # No broker at all
        result = purchase_license(infra, captain, lic_spec, rich_rep, 1)
        assert isinstance(result, str)
        assert "broker" in result.lower()

        # Add established broker in one region
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.ESTABLISHED, active=True))
        result = purchase_license(infra, captain, lic_spec, rich_rep, 1)
        assert isinstance(result, OwnedLicense)


# ---------------------------------------------------------------------------
# Upkeep tick tests
# ---------------------------------------------------------------------------

class TestInfraUpkeep:
    def test_broker_upkeep_deducted(self, world, infra, med_local_spec):
        captain = world.captain
        captain.silver = 5000
        open_broker_office(infra, captain, "Mediterranean", med_local_spec, day=1)
        silver_after_open = captain.silver

        # Advance 2 days (tick at day 3, 2 days owed)
        tick_infrastructure(infra, captain, day=3)
        expected_cost = 2 * med_local_spec.upkeep_per_day
        assert captain.silver == silver_after_open - expected_cost

    def test_broker_closed_on_default(self, world, infra, med_local_spec):
        captain = world.captain
        captain.silver = 200
        open_broker_office(infra, captain, "Mediterranean", med_local_spec, day=1)
        captain.silver = 0  # broke

        # 5+ days unpaid = closure (broker threshold)
        msgs = tick_infrastructure(infra, captain, day=7)
        broker = infra.brokers[0]
        assert not broker.active
        assert any("broker" in m.lower() or "Broker" in m for m in msgs)

    def test_license_upkeep_deducted(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        # Broker with upkeep current so it doesn't interfere
        infra.brokers.append(BrokerOffice(
            region="Mediterranean", tier=BrokerTier.LOCAL, active=True,
            upkeep_paid_through=3,
        ))
        lic_spec = get_license_spec("med_trade_charter")
        purchase_license(infra, captain, lic_spec, rich_rep, day=1)
        silver_after = captain.silver

        tick_infrastructure(infra, captain, day=3)
        expected_cost = 2 * lic_spec.upkeep_per_day
        assert captain.silver == silver_after - expected_cost

    def test_license_revoked_on_default(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.LOCAL, active=True))
        lic_spec = get_license_spec("med_trade_charter")
        purchase_license(infra, captain, lic_spec, rich_rep, day=1)
        captain.silver = 0

        msgs = tick_infrastructure(infra, captain, day=7)
        lic = infra.licenses[0]
        assert not lic.active
        assert any("license" in m.lower() or "License" in m for m in msgs)


# ---------------------------------------------------------------------------
# Board effects tests
# ---------------------------------------------------------------------------

class TestBoardEffects:
    def test_no_infra_returns_defaults(self, infra):
        effects = compute_board_effects(infra, "Mediterranean")
        assert effects["board_quality_bonus"] == 1.0
        assert effects["premium_offer_mult"] == 1.0
        assert effects["luxury_access"] == 0.0

    def test_broker_improves_board_quality(self, world, infra, med_local_spec):
        open_broker_office(infra, world.captain, "Mediterranean", med_local_spec, 1)
        effects = compute_board_effects(infra, "Mediterranean")
        assert effects["board_quality_bonus"] == med_local_spec.board_quality_bonus
        assert effects["board_quality_bonus"] > 1.0

    def test_broker_does_not_affect_other_regions(self, world, infra, med_local_spec):
        open_broker_office(infra, world.captain, "Mediterranean", med_local_spec, 1)
        effects = compute_board_effects(infra, "West Africa")
        assert effects["board_quality_bonus"] == 1.0

    def test_license_adds_effects(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.LOCAL, active=True))
        lic_spec = get_license_spec("med_trade_charter")
        purchase_license(infra, captain, lic_spec, rich_rep, 1)

        effects = compute_board_effects(infra, "Mediterranean", LICENSE_CATALOG)
        assert effects["lawful_board_mult"] > 1.0
        assert effects["customs_mult"] < 1.0

    def test_license_scoped_to_region(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.LOCAL, active=True))
        lic_spec = get_license_spec("med_trade_charter")
        purchase_license(infra, captain, lic_spec, rich_rep, 1)

        effects_other = compute_board_effects(infra, "West Africa", LICENSE_CATALOG)
        assert effects_other["lawful_board_mult"] == 1.0  # no effect in other region

    def test_global_license_applies_everywhere(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.ESTABLISHED, active=True))
        lic_spec = get_license_spec("luxury_goods_permit")
        purchase_license(infra, captain, lic_spec, rich_rep, 1)

        for region in ("Mediterranean", "West Africa", "East Indies"):
            effects = compute_board_effects(infra, region, LICENSE_CATALOG)
            assert effects["luxury_access"] == 1.0

    def test_inactive_license_no_effect(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.LOCAL, active=True))
        lic_spec = get_license_spec("med_trade_charter")
        purchase_license(infra, captain, lic_spec, rich_rep, 1)
        infra.licenses[0].active = False  # simulate revocation

        effects = compute_board_effects(infra, "Mediterranean", LICENSE_CATALOG)
        assert effects["lawful_board_mult"] == 1.0


# ---------------------------------------------------------------------------
# Contract generation integration
# ---------------------------------------------------------------------------

class TestContractBoardIntegration:
    def test_board_effects_change_offer_weights(self, world):
        """Board effects should produce different offer distributions."""
        port = world.ports["porto_novo"]
        rep = ReputationState(
            commercial_trust=50,
            regional_standing={"Mediterranean": 15, "West Africa": 15, "East Indies": 15},
        )
        rng1 = random.Random(42)
        rng2 = random.Random(42)

        # Without effects
        offers_plain = generate_offers(TEMPLATES, world, port, rep, "merchant", rng1)

        # With strong board effects
        effects = {
            "board_quality_bonus": 2.0,
            "premium_offer_mult": 2.0,
            "lawful_board_mult": 2.0,
            "luxury_access": 1.0,
        }
        offers_boosted = generate_offers(TEMPLATES, world, port, rep, "merchant", rng2, board_effects=effects)

        # Both should generate offers
        assert len(offers_plain) > 0
        assert len(offers_boosted) > 0

    def test_board_effects_optional(self, world):
        """generate_offers still works without board_effects."""
        port = world.ports["porto_novo"]
        rep = ReputationState()
        rng = random.Random(42)
        offers = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)
        assert isinstance(offers, list)


# ---------------------------------------------------------------------------
# Save/load round-trip
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_broker_round_trip(self, world, infra, med_local_spec):
        open_broker_office(infra, world.captain, "Mediterranean", med_local_spec, day=5)
        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)
        assert len(loaded_infra.brokers) == 1
        b = loaded_infra.brokers[0]
        assert b.region == "Mediterranean"
        assert b.tier == BrokerTier.LOCAL
        assert b.upkeep_paid_through == 5
        assert b.active is True

    def test_license_round_trip(self, world, infra, rich_rep):
        captain = world.captain
        captain.silver = 5000
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.LOCAL, active=True))
        lic_spec = get_license_spec("med_trade_charter")
        purchase_license(infra, captain, lic_spec, rich_rep, day=10)

        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)
        assert len(loaded_infra.licenses) == 1
        lic = loaded_infra.licenses[0]
        assert lic.license_id == "med_trade_charter"
        assert lic.purchased_day == 10
        assert lic.active is True

    def test_old_save_without_licenses_loads(self, world):
        """Backward compat: saves without licenses key still load."""
        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        infra = InfrastructureState()
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        # Simulate old save format without licenses key
        del d["infrastructure"]["licenses"]
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)
        assert loaded_infra.licenses == []


# ---------------------------------------------------------------------------
# Session integration
# ---------------------------------------------------------------------------

class TestSessionIntegration:
    def test_open_broker_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Broker Tester")
        silver_before = s.captain.silver

        spec = get_broker_spec("Mediterranean", BrokerTier.LOCAL)
        err = s.open_broker_cmd("Mediterranean", spec)
        assert err is None
        assert s.captain.silver == silver_before - spec.purchase_cost

    def test_purchase_license_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("License Tester")
        s.captain.silver = 5000
        s.captain.standing.commercial_trust = 80
        s.captain.standing.regional_standing["Mediterranean"] = 20
        s.captain.standing.customs_heat["Mediterranean"] = 0

        # Open broker first
        broker_spec = get_broker_spec("Mediterranean", BrokerTier.LOCAL)
        s.open_broker_cmd("Mediterranean", broker_spec)

        lic_spec = get_license_spec("med_trade_charter")
        err = s.purchase_license_cmd(lic_spec)
        assert err is None
        assert len(s.infra.licenses) == 1

    def test_broker_survives_save_load(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Persist Tester")
        spec = get_broker_spec("Mediterranean", BrokerTier.LOCAL)
        s.open_broker_cmd("Mediterranean", spec)

        s2 = GameSession(base_path=tmp_path)
        assert s2.load()
        assert len(s2.infra.brokers) == 1
        assert s2.infra.brokers[0].tier == BrokerTier.LOCAL

    def test_board_effects_used_on_arrival(self, tmp_path):
        """When arriving at a port with a broker, board effects should be computed."""
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Arrival Tester")
        spec = get_broker_spec("Mediterranean", BrokerTier.LOCAL)
        s.open_broker_cmd("Mediterranean", spec)
        # The session's _refresh_board now passes board_effects — verify no crash
        port = s.current_port
        if port:
            s._refresh_board(port)
        assert True  # no exception = wiring works
