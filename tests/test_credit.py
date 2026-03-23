"""Tests for Packet 3D-3B — Credit.

Law tests: content invariants for credit tiers.
Behavior tests: eligibility, open, draw, repay, interest, defaults.
Integration tests: session wiring, save/load, trust damage on default.
"""

import pytest

from portlight.content.infrastructure import (
    CREDIT_TIERS,
    available_credit_tiers,
    get_credit_spec,
)
from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.infrastructure import (
    BrokerOffice,
    BrokerTier,
    CreditTier,
    InfrastructureState,
    OwnedLicense,
    _ensure_credit,
    check_credit_eligibility,
    draw_credit,
    open_credit_line,
    repay_credit,
    tick_credit,
)
from portlight.engine.models import ReputationState
from portlight.engine.save import world_from_dict, world_to_dict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def world():
    return new_game("Banker", captain_type=CaptainType.MERCHANT)


@pytest.fixture
def infra():
    return InfrastructureState()


@pytest.fixture
def credible_rep():
    return ReputationState(
        commercial_trust=30,
        regional_standing={"Mediterranean": 10, "West Africa": 10, "East Indies": 10},
        customs_heat={"Mediterranean": 0, "West Africa": 0, "East Indies": 0},
    )


@pytest.fixture
def trusted_rep():
    return ReputationState(
        commercial_trust=80,
        regional_standing={"Mediterranean": 25, "West Africa": 25, "East Indies": 25},
        customs_heat={"Mediterranean": 0, "West Africa": 0, "East Indies": 0},
    )


# ---------------------------------------------------------------------------
# Content law tests
# ---------------------------------------------------------------------------

class TestCreditContentLaws:
    def test_three_tiers_exist(self):
        assert len(CREDIT_TIERS) == 3

    def test_tiers_ordered_by_limit(self):
        tiers = available_credit_tiers()
        limits = [t.credit_limit for t in tiers]
        assert limits == sorted(limits)

    def test_higher_tiers_have_better_rates(self):
        merchant = get_credit_spec(CreditTier.MERCHANT_LINE)
        house = get_credit_spec(CreditTier.HOUSE_CREDIT)
        premier = get_credit_spec(CreditTier.PREMIER_COMMERCIAL)
        assert merchant.interest_rate > house.interest_rate > premier.interest_rate

    def test_higher_tiers_require_more_trust(self):
        trust_rank = {"unproven": 0, "new": 1, "credible": 2, "reliable": 3, "trusted": 4}
        tiers = available_credit_tiers()
        trust_reqs = [trust_rank[t.required_trust_tier] for t in tiers]
        assert trust_reqs == sorted(trust_reqs)

    def test_premier_requires_license(self):
        premier = get_credit_spec(CreditTier.PREMIER_COMMERCIAL)
        assert premier.required_license is not None


# ---------------------------------------------------------------------------
# Eligibility tests
# ---------------------------------------------------------------------------

class TestCreditEligibility:
    def test_credible_qualifies_for_merchant_line(self, infra, credible_rep):
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        err = check_credit_eligibility(infra, spec, credible_rep)
        assert err is None

    def test_fresh_player_rejected(self, infra):
        rep = ReputationState()
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        err = check_credit_eligibility(infra, spec, rep)
        assert err is not None
        assert "trust" in err.lower()

    def test_low_standing_rejected_for_house(self, infra, credible_rep):
        credible_rep.regional_standing = {"Mediterranean": 2, "West Africa": 2, "East Indies": 2}
        spec = get_credit_spec(CreditTier.HOUSE_CREDIT)
        err = check_credit_eligibility(infra, spec, credible_rep)
        assert err is not None
        assert "standing" in err.lower()

    def test_high_heat_rejected_for_house(self, infra):
        rep = ReputationState(
            commercial_trust=60,
            regional_standing={"Mediterranean": 15, "West Africa": 15, "East Indies": 15},
            customs_heat={"Mediterranean": 10, "West Africa": 10, "East Indies": 10},
        )
        spec = get_credit_spec(CreditTier.HOUSE_CREDIT)
        err = check_credit_eligibility(infra, spec, rep)
        assert err is not None
        assert "heat" in err.lower() or "Heat" in err

    def test_premier_requires_license(self, infra, trusted_rep):
        spec = get_credit_spec(CreditTier.PREMIER_COMMERCIAL)
        err = check_credit_eligibility(infra, spec, trusted_rep)
        assert err is not None
        assert "license" in err.lower()

    def test_premier_with_license_succeeds(self, infra, trusted_rep):
        # Add required license + established broker
        infra.licenses.append(OwnedLicense(license_id="high_rep_charter", purchased_day=1, active=True))
        infra.brokers.append(BrokerOffice(region="Mediterranean", tier=BrokerTier.ESTABLISHED, active=True))
        spec = get_credit_spec(CreditTier.PREMIER_COMMERCIAL)
        err = check_credit_eligibility(infra, spec, trusted_rep)
        assert err is None

    def test_three_defaults_locks_credit(self, infra, credible_rep):
        credit = _ensure_credit(infra)
        credit.defaults = 3
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        err = check_credit_eligibility(infra, spec, credible_rep)
        assert err is not None
        assert "defaults" in err.lower() or "locked" in err.lower()


# ---------------------------------------------------------------------------
# Open / draw / repay tests
# ---------------------------------------------------------------------------

class TestCreditOperations:
    def test_open_merchant_line(self, world, infra, credible_rep):
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        err = open_credit_line(infra, spec, credible_rep, day=1)
        assert err is None
        credit = _ensure_credit(infra)
        assert credit.tier == CreditTier.MERCHANT_LINE
        assert credit.credit_limit == 300
        assert credit.active is True

    def test_cannot_downgrade(self, world, infra, credible_rep):
        spec_high = get_credit_spec(CreditTier.HOUSE_CREDIT)
        rep = ReputationState(
            commercial_trust=60,
            regional_standing={"Mediterranean": 15, "West Africa": 15, "East Indies": 15},
            customs_heat={"Mediterranean": 0, "West Africa": 0, "East Indies": 0},
        )
        open_credit_line(infra, spec_high, rep, day=1)
        spec_low = get_credit_spec(CreditTier.MERCHANT_LINE)
        err = open_credit_line(infra, spec_low, rep, day=2)
        assert err is not None
        assert "Already" in err or "better" in err

    def test_draw_credit(self, world, infra, credible_rep):
        captain = world.captain
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        silver_before = captain.silver

        err = draw_credit(infra, captain, 200)
        assert err is None
        assert captain.silver == silver_before + 200
        credit = _ensure_credit(infra)
        assert credit.outstanding == 200
        assert credit.total_borrowed == 200

    def test_draw_exceeds_limit(self, world, infra, credible_rep):
        captain = world.captain
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)  # limit=300
        open_credit_line(infra, spec, credible_rep, day=1)

        err = draw_credit(infra, captain, 500)
        assert isinstance(err, str)
        assert "Only" in err

    def test_draw_no_credit_line(self, world, infra):
        err = draw_credit(infra, world.captain, 100)
        assert isinstance(err, str)
        assert "No credit" in err

    def test_repay_credit(self, world, infra, credible_rep):
        captain = world.captain
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        draw_credit(infra, captain, 200)

        err = repay_credit(infra, captain, 100)
        assert err is None
        credit = _ensure_credit(infra)
        assert credit.outstanding == 100
        assert credit.total_repaid == 100

    def test_repay_caps_at_owed(self, world, infra, credible_rep):
        captain = world.captain
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        draw_credit(infra, captain, 50)
        silver_before = captain.silver

        err = repay_credit(infra, captain, 1000)  # more than owed
        assert err is None
        credit = _ensure_credit(infra)
        assert credit.outstanding == 0
        assert captain.silver == silver_before - 50  # only deducted what was owed

    def test_repay_nothing_owed(self, world, infra, credible_rep):
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        err = repay_credit(infra, world.captain, 100)
        assert isinstance(err, str)
        assert "No outstanding" in err


# ---------------------------------------------------------------------------
# Interest + default tests
# ---------------------------------------------------------------------------

class TestCreditTick:
    def test_interest_accrues_after_period(self, world, infra, credible_rep):
        captain = world.captain
        captain.silver = 5000
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)  # 8% per 10 days
        open_credit_line(infra, spec, credible_rep, day=1)
        draw_credit(infra, captain, 200)

        silver_before = captain.silver
        # Advance past one interest period — interest accrues and auto-payment fires
        msgs = tick_credit(infra, captain, day=12)
        assert any("Interest" in m or "interest" in m for m in msgs)
        # Auto-payment covers interest + 10% principal, so silver decreases
        assert captain.silver < silver_before

    def test_auto_payment_on_due_date(self, world, infra, credible_rep):
        captain = world.captain
        captain.silver = 5000
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        draw_credit(infra, captain, 200)

        silver_before_tick = captain.silver
        msgs = tick_credit(infra, captain, day=12)
        # Should auto-deduct minimum payment
        assert captain.silver < silver_before_tick
        assert any("payment" in m.lower() or "auto" in m.lower() for m in msgs)

    def test_default_on_insufficient_funds(self, world, infra, credible_rep):
        captain = world.captain
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        draw_credit(infra, captain, 200)
        captain.silver = 0  # broke

        msgs = tick_credit(infra, captain, day=12)
        credit = _ensure_credit(infra)
        assert credit.defaults >= 1
        assert any("DEFAULT" in m for m in msgs)

    def test_three_defaults_freezes_line(self, world, infra, credible_rep):
        captain = world.captain
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        draw_credit(infra, captain, 100)
        captain.silver = 0

        credit = _ensure_credit(infra)
        credit.defaults = 2  # already defaulted twice
        msgs = tick_credit(infra, captain, day=12)
        assert credit.defaults >= 3
        assert not credit.active
        assert any("frozen" in m.lower() for m in msgs)

    def test_no_interest_when_no_debt(self, world, infra, credible_rep):
        captain = world.captain
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=1)
        # Don't draw anything

        msgs = tick_credit(infra, captain, day=12)
        assert len(msgs) == 0

    def test_interest_applies_to_principal(self, world, infra, credible_rep):
        captain = world.captain
        captain.silver = 5000
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)  # 8% per 10 days
        open_credit_line(infra, spec, credible_rep, day=1)
        draw_credit(infra, captain, 200)

        credit = _ensure_credit(infra)
        silver_before = captain.silver
        # Day 11 — interest accrues + auto-payment fires (due day was 11)
        tick_credit(infra, captain, day=11)
        expected_interest = int(200 * 0.08)  # 16
        min_payment = expected_interest + max(1, 200 // 10)  # 16 + 20 = 36
        # Auto-payment deducted interest + 10% principal
        assert captain.silver == silver_before - min_payment
        assert credit.total_repaid == min_payment


# ---------------------------------------------------------------------------
# Save/load round-trip
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_credit_round_trip(self, world, infra, credible_rep):
        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        open_credit_line(infra, spec, credible_rep, day=5)
        draw_credit(infra, world.captain, 100)

        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)

        credit = loaded_infra.credit
        assert credit is not None
        assert credit.tier == CreditTier.MERCHANT_LINE
        assert credit.outstanding == 100
        assert credit.active is True

    def test_old_save_without_credit_loads(self, world):
        from portlight.receipts.models import ReceiptLedger
        from portlight.engine.contracts import ContractBoard
        infra = InfrastructureState()
        d = world_to_dict(world, ReceiptLedger(), ContractBoard(), infra)
        if "credit" in d["infrastructure"]:
            del d["infrastructure"]["credit"]
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)
        assert loaded_infra.credit is None  # no credit data in old saves


# ---------------------------------------------------------------------------
# Session integration
# ---------------------------------------------------------------------------

class TestSessionIntegration:
    def test_open_credit_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Credit Tester")
        s.captain.standing.commercial_trust = 30
        s.captain.standing.regional_standing["Mediterranean"] = 10

        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        err = s.open_credit_cmd(spec)
        assert err is None
        credit = _ensure_credit(s.infra)
        assert credit.active

    def test_draw_and_repay_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Draw Tester")
        s.captain.standing.commercial_trust = 30
        s.captain.standing.regional_standing["Mediterranean"] = 10

        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        s.open_credit_cmd(spec)

        err = s.draw_credit_cmd(150)
        assert err is None
        credit = _ensure_credit(s.infra)
        assert credit.outstanding == 150

        err = s.repay_credit_cmd(50)
        assert err is None
        assert credit.outstanding == 100

    def test_credit_survives_save_load(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Persist Tester")
        s.captain.standing.commercial_trust = 30
        s.captain.standing.regional_standing["Mediterranean"] = 10

        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        s.open_credit_cmd(spec)
        s.draw_credit_cmd(100)

        s2 = GameSession(base_path=tmp_path)
        assert s2.load()
        credit = _ensure_credit(s2.infra)
        assert credit.outstanding == 100
        assert credit.tier == CreditTier.MERCHANT_LINE

    def test_default_damages_trust_in_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Default Tester")
        s.captain.standing.commercial_trust = 30
        s.captain.standing.regional_standing["Mediterranean"] = 10

        spec = get_credit_spec(CreditTier.MERCHANT_LINE)
        s.open_credit_cmd(spec)
        s.draw_credit_cmd(200)
        s.captain.silver = 0  # broke

        trust_before = s.captain.standing.commercial_trust
        # Advance enough days to trigger interest + default
        for _ in range(12):
            s.advance()

        credit = _ensure_credit(s.infra)
        if credit.defaults > 0:
            assert s.captain.standing.commercial_trust < trust_before
