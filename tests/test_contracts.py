"""Tests for Packet 3C — Contract Board and Obligation Engine.

Law tests: structural invariants that must always hold.
Behavior tests: gameplay outcomes under specific conditions.
Balance tests: captain divergence in contract opportunity sets.
Integration tests: session-level wiring (accept, deliver, complete, abandon, save/load).
"""

import random

import pytest

from portlight.content.contracts import TEMPLATES
from portlight.content.goods import GOODS
from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.contracts import (
    ActiveContract,
    ContractBoard,
    ContractFamily,
    ContractOffer,
    ContractOutcome,
    abandon_contract,
    accept_offer,
    check_delivery,
    generate_offers,
    resolve_completed,
    tick_contracts,
)
from portlight.engine.economy import execute_buy, recalculate_prices
from portlight.engine.models import ReputationState
from portlight.engine.save import world_from_dict, world_to_dict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def world():
    return new_game("Tester", captain_type=CaptainType.MERCHANT)


@pytest.fixture
def world_nav():
    return new_game("NavTester", captain_type=CaptainType.NAVIGATOR)


@pytest.fixture
def world_smug():
    return new_game("SmugTester", captain_type=CaptainType.SMUGGLER)


@pytest.fixture
def board():
    return ContractBoard()


@pytest.fixture
def rng():
    return random.Random(42)


# ---------------------------------------------------------------------------
# Template law tests
# ---------------------------------------------------------------------------

class TestTemplateLaws:
    def test_enough_templates(self):
        assert len(TEMPLATES) >= 12

    def test_all_six_families_covered(self):
        families = {t.family for t in TEMPLATES}
        for fam in ContractFamily:
            assert fam in families, f"Missing family: {fam}"

    def test_all_goods_exist(self):
        for t in TEMPLATES:
            for g in t.goods_pool:
                assert g in GOODS, f"Template {t.id} references unknown good: {g}"

    def test_quantity_range_valid(self):
        for t in TEMPLATES:
            assert t.quantity_min > 0
            assert t.quantity_max >= t.quantity_min

    def test_reward_positive(self):
        for t in TEMPLATES:
            assert t.reward_per_unit > 0

    def test_deadline_positive(self):
        for t in TEMPLATES:
            assert t.deadline_days > 0

    def test_at_least_3_trust_gated(self):
        gated = [t for t in TEMPLATES if t.trust_requirement not in ("unproven",)]
        assert len(gated) >= 3

    def test_at_least_3_high_scrutiny(self):
        scrutiny = [t for t in TEMPLATES if t.inspection_modifier > 0 or t.heat_ceiling is not None]
        assert len(scrutiny) >= 3

    def test_at_least_2_circuit(self):
        circuits = [t for t in TEMPLATES if t.family == ContractFamily.CIRCUIT]
        assert len(circuits) >= 2

    def test_ids_unique(self):
        ids = [t.id for t in TEMPLATES]
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Generation law tests
# ---------------------------------------------------------------------------

class TestGenerationLaws:
    def test_generates_offers(self, world, rng):
        port = world.ports["porto_novo"]
        rep = world.captain.standing
        offers = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)
        assert len(offers) > 0
        assert len(offers) <= 5

    def test_offers_have_valid_fields(self, world, rng):
        port = world.ports["porto_novo"]
        rep = world.captain.standing
        offers = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)
        for o in offers:
            assert o.id
            assert o.good_id in GOODS
            assert o.quantity > 0
            assert o.reward_silver > 0
            assert o.deadline_day > world.day

    def test_no_self_destination(self, world, rng):
        port = world.ports["porto_novo"]
        rep = world.captain.standing
        offers = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)
        for o in offers:
            assert o.destination_port_id != port.id

    def test_trust_gates_filter(self, world, rng):
        """Unproven captain should not see trust-gated offers."""
        port = world.ports["porto_novo"]
        rep = ReputationState()  # fresh = unproven (trust 0)
        offers = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)
        for o in offers:
            assert o.required_trust_tier in ("unproven",), \
                f"Unproven captain got offer requiring {o.required_trust_tier}"

    def test_high_trust_sees_more(self, world, rng):
        """A trusted captain should see more templates."""
        port = world.ports["porto_novo"]
        rep = ReputationState(commercial_trust=50, regional_standing={
            "Mediterranean": 10, "West Africa": 10, "East Indies": 10,
        })
        offers_trusted = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)

        rng2 = random.Random(42)
        rep_low = ReputationState()
        offers_low = generate_offers(TEMPLATES, world, port, rep_low, "merchant", rng2)

        # Trusted captain should see at least as many unique templates
        templates_trusted = {o.template_id for o in offers_trusted}
        templates_low = {o.template_id for o in offers_low}
        # At minimum, the trusted set shouldn't be smaller
        assert len(templates_trusted) >= len(templates_low)

    def test_heat_ceiling_filters(self, world, rng):
        """High-heat captain should not see heat-ceilinged offers."""
        port = world.ports["porto_novo"]
        rep = ReputationState(
            commercial_trust=50,
            customs_heat={"Mediterranean": 30, "West Africa": 30, "East Indies": 30},
            regional_standing={"Mediterranean": 10, "West Africa": 10, "East Indies": 10},
        )
        offers = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)
        for o in offers:
            if o.heat_ceiling is not None:
                # The offer should only appear if heat was below ceiling
                # Since our heat is 30, offers with ceiling < 30 should be excluded
                assert o.heat_ceiling >= 30
    def test_destination_trades_contract_good(self, world, rng):
        """Every contract destination must trade the contract good."""
        for port in world.ports.values():
            rep = world.captain.standing
            offers = generate_offers(TEMPLATES, world, port, rep, "merchant", rng)
            for o in offers:
                dest = world.ports[o.destination_port_id]
                dest_goods = {slot.good_id for slot in dest.market}
                assert o.good_id in dest_goods, (
                    f"Contract '{o.title}' delivers {o.good_id} to "
                    f"{dest.name} which doesn't trade it "
                    f"(trades: {dest_goods})"
                )


# ---------------------------------------------------------------------------
# Acceptance tests
# ---------------------------------------------------------------------------

class TestAcceptance:
    def _make_offer(self, port_id="porto_novo"):
        return ContractOffer(
            id="test-offer-1",
            template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT,
            title="Test Grain Contract",
            description="Test",
            issuer_port_id=port_id,
            destination_port_id="al_manar",
            good_id="grain",
            quantity=10,
            created_day=1,
            deadline_day=30,
            reward_silver=160,
            bonus_reward=30,
            required_trust_tier="unproven",
            required_standing=0,
            heat_ceiling=None,
            inspection_modifier=0.0,
            source_region=None,
            source_port=None,
            offer_reason="Test offer",
        )

    def test_accept_success(self, board):
        offer = self._make_offer()
        board.offers.append(offer)
        result = accept_offer(board, "test-offer-1", day=5)
        assert isinstance(result, ActiveContract)
        assert result.good_id == "grain"
        assert result.required_quantity == 10
        assert result.accepted_day == 5
        assert len(board.offers) == 0
        assert len(board.active) == 1

    def test_accept_not_found(self, board):
        result = accept_offer(board, "nonexistent", day=1)
        assert result == "Offer not found"

    def test_accept_max_3(self, board):
        for i in range(3):
            offer = self._make_offer()
            offer.id = f"offer-{i}"
            board.offers.append(offer)
            accept_offer(board, f"offer-{i}", day=1)
        assert len(board.active) == 3

        extra = self._make_offer()
        extra.id = "offer-extra"
        board.offers.append(extra)
        result = accept_offer(board, "offer-extra", day=1)
        assert result == "Too many active contracts (max 3)"

    def test_offer_removed_after_accept(self, board):
        offer = self._make_offer()
        board.offers.append(offer)
        accept_offer(board, "test-offer-1", day=1)
        assert not any(o.id == "test-offer-1" for o in board.offers)


# ---------------------------------------------------------------------------
# Delivery tests
# ---------------------------------------------------------------------------

class TestDelivery:
    def _make_active(self, **kwargs):
        defaults = dict(
            offer_id="active-1",
            template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT,
            title="Test Grain",
            accepted_day=1,
            deadline_day=30,
            destination_port_id="al_manar",
            good_id="grain",
            required_quantity=10,
        )
        defaults.update(kwargs)
        return ActiveContract(**defaults)

    def test_delivery_credits(self, board):
        contract = self._make_active()
        board.active.append(contract)
        credited = check_delivery(board, "al_manar", "grain", 5, "porto_novo", "Mediterranean")
        assert len(credited) == 1
        assert credited[0][1] == 5
        assert contract.delivered_quantity == 5

    def test_delivery_caps_at_required(self, board):
        contract = self._make_active(required_quantity=5)
        board.active.append(contract)
        credited = check_delivery(board, "al_manar", "grain", 10, "porto_novo", "Mediterranean")
        assert credited[0][1] == 5
        assert contract.delivered_quantity == 5

    def test_wrong_port_no_credit(self, board):
        contract = self._make_active()
        board.active.append(contract)
        credited = check_delivery(board, "porto_novo", "grain", 5, "porto_novo", "Mediterranean")
        assert len(credited) == 0

    def test_wrong_good_no_credit(self, board):
        contract = self._make_active()
        board.active.append(contract)
        credited = check_delivery(board, "al_manar", "silk", 5, "porto_novo", "Mediterranean")
        assert len(credited) == 0

    def test_source_region_validated(self, board):
        contract = self._make_active(source_region="East Indies")
        board.active.append(contract)
        credited = check_delivery(board, "al_manar", "grain", 5, "porto_novo", "Mediterranean")
        assert len(credited) == 0  # Wrong source region

    def test_source_port_validated(self, board):
        contract = self._make_active(source_port="jade_port")
        board.active.append(contract)
        credited = check_delivery(board, "al_manar", "grain", 5, "porto_novo", "Mediterranean")
        assert len(credited) == 0  # Wrong source port

    def test_source_region_match_credits(self, board):
        contract = self._make_active(source_region="Mediterranean")
        board.active.append(contract)
        credited = check_delivery(board, "al_manar", "grain", 5, "porto_novo", "Mediterranean")
        assert len(credited) == 1
        assert credited[0][1] == 5


# ---------------------------------------------------------------------------
# Completion tests
# ---------------------------------------------------------------------------

class TestCompletion:
    def _make_active(self, **kwargs):
        defaults = dict(
            offer_id="active-1",
            template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT,
            title="Test Grain",
            accepted_day=1,
            deadline_day=30,
            destination_port_id="al_manar",
            good_id="grain",
            required_quantity=10,
            reward_silver=160,
            bonus_reward=30,
        )
        defaults.update(kwargs)
        return ActiveContract(**defaults)

    def test_completion_on_full_delivery(self, board):
        contract = self._make_active()
        contract.delivered_quantity = 10
        board.active.append(contract)
        outcomes = resolve_completed(board, day=15)
        assert len(outcomes) == 1
        assert outcomes[0].outcome_type == "completed_bonus"  # early (day 15 < deadline 30 - 3)
        assert outcomes[0].silver_delta == 160 + 30  # reward + bonus
        assert len(board.active) == 0

    def test_completion_no_bonus_if_late(self, board):
        contract = self._make_active()
        contract.delivered_quantity = 10
        board.active.append(contract)
        outcomes = resolve_completed(board, day=28)  # Not early (28 >= 30-3)
        assert outcomes[0].outcome_type == "completed"
        assert outcomes[0].silver_delta == 160  # No bonus

    def test_partial_delivery_no_completion(self, board):
        contract = self._make_active()
        contract.delivered_quantity = 5  # Only half
        board.active.append(contract)
        outcomes = resolve_completed(board, day=15)
        assert len(outcomes) == 0
        assert len(board.active) == 1

    def test_completion_trust_delta(self, board):
        contract = self._make_active()
        contract.delivered_quantity = 10
        board.active.append(contract)
        outcomes = resolve_completed(board, day=15)
        assert outcomes[0].trust_delta > 0
        assert outcomes[0].standing_delta > 0
        assert outcomes[0].heat_delta < 0  # Clean delivery reduces heat


# ---------------------------------------------------------------------------
# Expiry tests
# ---------------------------------------------------------------------------

class TestExpiry:
    def _make_active(self, **kwargs):
        defaults = dict(
            offer_id="active-1",
            template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT,
            title="Test Grain",
            accepted_day=1,
            deadline_day=10,
            destination_port_id="al_manar",
            good_id="grain",
            required_quantity=10,
            reward_silver=160,
        )
        defaults.update(kwargs)
        return ActiveContract(**defaults)

    def test_expiry_after_deadline(self, board):
        contract = self._make_active()
        board.active.append(contract)
        outcomes = tick_contracts(board, day=11)
        assert len(outcomes) == 1
        assert outcomes[0].outcome_type == "expired"
        assert outcomes[0].trust_delta < 0
        assert len(board.active) == 0

    def test_partial_payout_on_expiry(self, board):
        contract = self._make_active(reward_silver=200)
        contract.delivered_quantity = 5  # Half delivered
        board.active.append(contract)
        outcomes = tick_contracts(board, day=11)
        assert outcomes[0].silver_delta > 0  # Partial payout
        # 50% pro-rata at 50% = 50
        expected = int(200 * 0.5 * 0.5)
        assert outcomes[0].silver_delta == expected

    def test_zero_payout_no_delivery(self, board):
        contract = self._make_active()
        board.active.append(contract)
        outcomes = tick_contracts(board, day=11)
        assert outcomes[0].silver_delta == 0
        assert outcomes[0].trust_delta == -3  # Harsher penalty

    def test_not_expired_before_deadline(self, board):
        contract = self._make_active()
        board.active.append(contract)
        outcomes = tick_contracts(board, day=10)  # Exactly on deadline
        assert len(outcomes) == 0

    def test_stale_offers_removed(self, board):
        offer = ContractOffer(
            id="stale-1", template_id="t", family=ContractFamily.PROCUREMENT,
            title="Stale", description="", issuer_port_id="p",
            destination_port_id="d", good_id="grain", quantity=5,
            created_day=1, deadline_day=30, reward_silver=100,
            bonus_reward=0, required_trust_tier="unproven",
            required_standing=0, heat_ceiling=None, inspection_modifier=0.0,
            source_region=None, source_port=None, offer_reason="test",
            acceptance_window=10,
        )
        board.offers.append(offer)
        tick_contracts(board, day=12)  # created_day 1 + window 10 = 11
        assert len(board.offers) == 0


# ---------------------------------------------------------------------------
# Abandonment tests
# ---------------------------------------------------------------------------

class TestAbandonment:
    def test_abandon_success(self, board):
        contract = ActiveContract(
            offer_id="active-1", template_id="t", family=ContractFamily.PROCUREMENT,
            title="Test", accepted_day=1, deadline_day=30,
            destination_port_id="d", good_id="grain", required_quantity=10,
        )
        board.active.append(contract)
        result = abandon_contract(board, "active-1", day=5)
        assert isinstance(result, ContractOutcome)
        assert result.outcome_type == "abandoned"
        assert result.trust_delta == -2
        assert len(board.active) == 0
        assert len(board.completed) == 1

    def test_abandon_not_found(self, board):
        result = abandon_contract(board, "nonexistent", day=1)
        assert result == "No active contract with that ID"


# ---------------------------------------------------------------------------
# Captain divergence tests
# ---------------------------------------------------------------------------

class TestCaptainDivergence:
    def test_smuggler_sees_luxury_offers(self, world_smug, rng):
        """Smuggler with enough trust should see luxury_discreet offers."""
        port = world_smug.ports["porto_novo"]
        rep = ReputationState(
            commercial_trust=30,
            customs_heat={"Mediterranean": 0, "West Africa": 0, "East Indies": 0},
            regional_standing={"Mediterranean": 5, "West Africa": 5, "East Indies": 5},
        )
        # Run many times to check bias
        luxury_count = 0
        for seed in range(50):
            offers = generate_offers(TEMPLATES, world_smug, port, rep, "smuggler", random.Random(seed))
            luxury_count += sum(1 for o in offers if o.family == ContractFamily.LUXURY_DISCREET)

        # Smuggler should see some luxury offers
        assert luxury_count > 0

    def test_navigator_sees_circuit_offers(self, world_nav, rng):
        """Navigator with standing should see circuit offers more often."""
        port = world_nav.ports["silva_bay"]
        rep = ReputationState(
            commercial_trust=20,
            regional_standing={"Mediterranean": 5, "West Africa": 5, "East Indies": 5},
        )
        circuit_count = 0
        for seed in range(50):
            offers = generate_offers(TEMPLATES, world_nav, port, rep, "navigator", random.Random(seed))
            circuit_count += sum(1 for o in offers if o.family == ContractFamily.CIRCUIT)

        assert circuit_count > 0


# ---------------------------------------------------------------------------
# Save/load round-trip tests
# ---------------------------------------------------------------------------

class TestContractSaveLoad:
    def test_board_roundtrip(self, world):
        from portlight.engine.contracts import ContractBoard
        from portlight.engine.save import world_to_dict, world_from_dict

        board = ContractBoard()
        offer = ContractOffer(
            id="save-test", template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT, title="Save Test",
            description="desc", issuer_port_id="porto_novo",
            destination_port_id="al_manar", good_id="grain",
            quantity=10, created_day=1, deadline_day=30,
            reward_silver=160, bonus_reward=30,
            required_trust_tier="unproven", required_standing=0,
            heat_ceiling=None, inspection_modifier=0.0,
            source_region=None, source_port=None,
            offer_reason="test",
        )
        board.offers.append(offer)

        contract = ActiveContract(
            offer_id="active-save", template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT, title="Active Save",
            accepted_day=2, deadline_day=30,
            destination_port_id="al_manar", good_id="grain",
            required_quantity=10, delivered_quantity=3,
            reward_silver=160, bonus_reward=30,
        )
        board.active.append(contract)

        outcome = ContractOutcome(
            contract_id="done-1", outcome_type="completed",
            silver_delta=160, trust_delta=1, standing_delta=1,
            heat_delta=-1, completion_day=15, summary="Test completion",
        )
        board.completed.append(outcome)

        d = world_to_dict(world, board=board)
        _, _, loaded_board, _infra, _campaign, _narrative = world_from_dict(d)

        assert len(loaded_board.offers) == 1
        assert loaded_board.offers[0].id == "save-test"
        assert loaded_board.offers[0].family == ContractFamily.PROCUREMENT

        assert len(loaded_board.active) == 1
        assert loaded_board.active[0].delivered_quantity == 3
        assert loaded_board.active[0].family == ContractFamily.PROCUREMENT

        assert len(loaded_board.completed) == 1
        assert loaded_board.completed[0].silver_delta == 160

    def test_empty_board_roundtrip(self, world):
        from portlight.engine.save import world_to_dict, world_from_dict
        d = world_to_dict(world)
        _, _, loaded_board, _infra, _campaign, _narrative = world_from_dict(d)
        assert len(loaded_board.offers) == 0
        assert len(loaded_board.active) == 0

    def test_save_load_with_board(self, tmp_path, world):
        from portlight.engine.contracts import ContractBoard
        from portlight.engine.save import save_game, load_game

        board = ContractBoard()
        board.last_refresh_day = 5
        save_game(world, board=board, base_path=tmp_path)
        result = load_game(base_path=tmp_path)
        assert result is not None
        _, _, loaded_board, _infra, _campaign, _narrative = result
        assert loaded_board.last_refresh_day == 5


# ---------------------------------------------------------------------------
# Session integration tests
# ---------------------------------------------------------------------------

class TestSessionIntegration:
    def test_session_has_board(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")
        assert s.board is not None
        assert isinstance(s.board, ContractBoard)

    def test_session_board_persists(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")
        s.board.last_refresh_day = 99
        s._save()

        s2 = GameSession(base_path=tmp_path)
        s2.load()
        assert s2.board.last_refresh_day == 99

    def test_accept_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")

        # Clear auto-generated offers and add our test offer
        s.board.offers.clear()
        offer = ContractOffer(
            id="session-test", template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT, title="Session Test",
            description="test", issuer_port_id="porto_novo",
            destination_port_id="al_manar", good_id="grain",
            quantity=5, created_day=1, deadline_day=30,
            reward_silver=80, bonus_reward=0,
            required_trust_tier="unproven", required_standing=0,
            heat_ceiling=None, inspection_modifier=0.0,
            source_region=None, source_port=None,
            offer_reason="test",
        )
        s.board.offers.append(offer)

        err = s.accept_contract("session-test")
        assert err is None
        assert len(s.board.active) == 1
        assert len(s.board.offers) == 0

    def test_abandon_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")

        contract = ActiveContract(
            offer_id="abandon-test", template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT, title="Abandon Test",
            accepted_day=1, deadline_day=30,
            destination_port_id="al_manar", good_id="grain",
            required_quantity=10,
        )
        s.board.active.append(contract)

        err = s.abandon_contract_cmd("abandon-test")
        assert err is None
        assert len(s.board.active) == 0
        assert len(s.board.completed) == 1

    def test_sell_credits_contract(self, tmp_path):
        """Selling goods at the right port credits an active contract."""
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")

        # Set up: buy grain at porto_novo, sail to al_manar, sell
        # We'll simulate by teleporting
        port = s.world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(s.world.captain, port, "grain", 10, GOODS)

        # Create a contract for grain at al_manar
        contract = ActiveContract(
            offer_id="sell-test", template_id="proc_grain_feed",
            family=ContractFamily.PROCUREMENT, title="Sell Test",
            accepted_day=1, deadline_day=30,
            destination_port_id="al_manar", good_id="grain",
            required_quantity=10, reward_silver=160,
        )
        s.board.active.append(contract)

        # Teleport to al_manar
        from portlight.engine.models import VoyageState, VoyageStatus
        s.world.voyage = VoyageState(
            origin_id="porto_novo", destination_id="al_manar",
            distance=100, progress=100, status=VoyageStatus.IN_PORT,
        )
        al_manar = s.world.ports["al_manar"]
        recalculate_prices(al_manar, GOODS)

        silver_before = s.world.captain.silver
        result = s.sell("grain", 10)
        assert not isinstance(result, str), f"Sell failed: {result}"

        # Contract should be credited
        assert s.board.active[0].delivered_quantity == 10 if s.board.active else True
        # If completed, reward should be paid
        if not s.board.active:
            assert s.world.captain.silver > silver_before  # Got reward


# ---------------------------------------------------------------------------
# Cargo provenance tests
# ---------------------------------------------------------------------------

class TestCargoProvenance:
    def test_buy_stamps_provenance(self, world):
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        result = execute_buy(world.captain, port, "grain", 5, GOODS)
        assert not isinstance(result, str)
        cargo = world.captain.cargo[-1]
        assert cargo.acquired_port == "porto_novo"
        assert cargo.acquired_region == "Mediterranean"
        assert cargo.acquired_day == world.captain.day

    def test_different_ports_separate_lots(self, world):
        porto = world.ports["porto_novo"]
        recalculate_prices(porto, GOODS)
        execute_buy(world.captain, porto, "grain", 3, GOODS)

        # Simulate buying at a different port
        al_manar = world.ports["al_manar"]
        recalculate_prices(al_manar, GOODS)
        result = execute_buy(world.captain, al_manar, "grain", 2, GOODS)
        assert not isinstance(result, str)

        # Should have two separate grain lots
        grain_lots = [c for c in world.captain.cargo if c.good_id == "grain"]
        assert len(grain_lots) == 2
        assert grain_lots[0].acquired_port == "porto_novo"
        assert grain_lots[1].acquired_port == "al_manar"

    def test_same_port_merges(self, world):
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 3, GOODS)
        execute_buy(world.captain, port, "grain", 2, GOODS)

        grain_lots = [c for c in world.captain.cargo if c.good_id == "grain"]
        assert len(grain_lots) == 1
        assert grain_lots[0].quantity == 5

    def test_provenance_survives_save(self, world):
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 5, GOODS)

        d = world_to_dict(world)
        loaded, _, _, _infra, _campaign, _narrative = world_from_dict(d)
        cargo = loaded.captain.cargo[-1]
        assert cargo.acquired_port == "porto_novo"
        assert cargo.acquired_region == "Mediterranean"
