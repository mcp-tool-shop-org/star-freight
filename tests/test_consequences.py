"""Tests for the consequence engine — past decisions shape future encounters."""

import random

from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.consequences import (
    Consequence,
    apply_consequence,
    check_port_consequences,
    check_sea_consequences,
)
from portlight.engine.contracts import ContractBoard, ContractOutcome
from portlight.engine.models import (
    VoyageState,
    VoyageStatus,
)
from portlight.receipts.models import ReceiptLedger, TradeAction, TradeReceipt


def _make_world(captain_type: str = "merchant"):
    ct = CaptainType(captain_type)
    world = new_game(captain_type=ct)
    world.voyage = VoyageState(
        origin_id="porto_novo", destination_id="al_manar",
        distance=24, progress=5, days_elapsed=2, status=VoyageStatus.AT_SEA,
    )
    return world


def _make_ledger_with_trades(port_id: str = "porto_novo", count: int = 10) -> ReceiptLedger:
    ledger = ReceiptLedger()
    for i in range(count):
        ledger.receipts.append(TradeReceipt(
            receipt_id=f"r{i}", captain_name="Test", port_id=port_id,
            good_id="grain", action=TradeAction.SELL, quantity=5,
            unit_price=15, total_price=75, day=i + 1,
        ))
    ledger.total_sells = count
    ledger.net_profit = count * 50
    return ledger


class TestSeaConsequences:
    """Sea consequences fire based on player history."""

    def test_fair_trader_reward(self):
        """High trust + many trades should trigger merchant gift."""
        world = _make_world()
        world.captain.standing.commercial_trust = 15
        ledger = _make_ledger_with_trades(count=15)
        board = ContractBoard()
        found_reward = False
        for seed in range(200):
            result = check_sea_consequences(world, None, ledger, board, random.Random(seed))
            for c in result:
                if c.id == "fair_trader_gift":
                    found_reward = True
                    assert c.silver_delta > 0
                    assert c.effect_type == "reward"
        assert found_reward, "Fair trader reward should fire with high trust and many trades"

    def test_faction_warning(self):
        """Low faction standing in their territory should trigger warning."""
        world = _make_world()
        world.captain.standing.underworld_standing["crimson_tide"] = 3
        world.voyage = VoyageState(
            origin_id="porto_novo", destination_id="corsairs_rest",
            distance=18, progress=5, days_elapsed=1, status=VoyageStatus.AT_SEA,
        )
        found_warning = False
        for seed in range(200):
            result = check_sea_consequences(world, None, ReceiptLedger(), ContractBoard(), random.Random(seed))
            for c in result:
                if c.id == "faction_warning":
                    found_warning = True
                    assert c.effect_type == "threat"
                    assert c.heat_delta > 0
        assert found_warning, "Faction warning should fire in faction territory with low standing"

    def test_broken_contract_haunts(self):
        """Failed contracts should trigger shame encounters."""
        world = _make_world()
        board = ContractBoard()
        board.completed.append(ContractOutcome(
            contract_id="test", outcome_type="expired",
            silver_delta=0, trust_delta=-2, standing_delta=-1,
            heat_delta=1, completion_day=5, summary="Failed to deliver grain",
        ))
        found_shame = False
        for seed in range(200):
            result = check_sea_consequences(world, None, ReceiptLedger(), board, random.Random(seed))
            for c in result:
                if c.id == "broken_contract_haunts":
                    found_shame = True
                    assert c.effect_type == "threat"
        assert found_shame, "Broken contract should haunt the player"

    def test_nemesis_shadow(self):
        """Active nemesis should trigger tracking encounters."""
        world = _make_world()
        world.pirates.nemesis_id = "the_butcher"
        found_nemesis = False
        for seed in range(200):
            result = check_sea_consequences(world, None, ReceiptLedger(), ContractBoard(), random.Random(seed))
            for c in result:
                if c.id == "nemesis_shadow":
                    found_nemesis = True
                    assert c.effect_type == "threat"
        assert found_nemesis, "Nemesis should stalk the player"


class TestPortConsequences:
    """Port consequences fire based on player history."""

    def test_loyal_customer_reward(self):
        """Repeated trading at a port should trigger loyalty reward."""
        world = _make_world()
        ledger = _make_ledger_with_trades("porto_novo", count=8)
        found_reward = False
        for seed in range(200):
            result = check_port_consequences(world, "porto_novo", ledger, ContractBoard(), random.Random(seed))
            for c in result:
                if c.id == "loyal_customer":
                    found_reward = True
                    assert c.silver_delta > 0
        assert found_reward, "Loyal customer reward should fire after many trades"

    def test_first_visit(self):
        """First visit to a port should trigger newcomer encounter."""
        world = _make_world()
        # Make sure we haven't visited al_manar
        world.culture.port_visits = {}
        found_first = False
        for seed in range(200):
            result = check_port_consequences(world, "al_manar", ReceiptLedger(), ContractBoard(), random.Random(seed))
            for c in result:
                if c.id == "first_visit":
                    found_first = True
                    assert c.effect_type == "neutral"
        assert found_first, "First visit should trigger newcomer encounter"

    def test_high_heat_scrutiny(self):
        """High customs heat should trigger extra scrutiny on arrival."""
        world = _make_world()
        world.captain.standing.customs_heat["Mediterranean"] = 25
        found_scrutiny = False
        for seed in range(200):
            result = check_port_consequences(world, "porto_novo", ReceiptLedger(), ContractBoard(), random.Random(seed))
            for c in result:
                if c.id == "heat_scrutiny":
                    found_scrutiny = True
                    assert c.effect_type == "threat"
                    assert c.heat_delta > 0
        assert found_scrutiny, "High heat should trigger port scrutiny"

    def test_network_gossip(self):
        """Cross-port network NPCs should share gossip about you."""
        world = _make_world()
        world.captain.standing.commercial_trust = 12
        found_gossip = False
        for seed in range(300):
            result = check_port_consequences(world, "porto_novo", ReceiptLedger(), ContractBoard(), random.Random(seed))
            for c in result:
                if c.id == "network_gossip":
                    found_gossip = True
                    assert c.effect_type == "information"
        assert found_gossip, "Network gossip should fire at ports with cross-port connections"


class TestApplyConsequence:
    """Mechanical effects apply correctly."""

    def test_silver_reward(self):
        world = _make_world()
        silver_before = world.captain.silver
        apply_consequence(world, Consequence(
            id="test", category="sea", trigger="test", text="test",
            effect_type="reward", silver_delta=50,
        ))
        assert world.captain.silver == silver_before + 50

    def test_heat_penalty(self):
        world = _make_world()
        heat_before = world.captain.standing.customs_heat["Mediterranean"]
        apply_consequence(world, Consequence(
            id="test", category="sea", trigger="test", text="test",
            effect_type="threat", heat_delta=5, region="Mediterranean",
        ))
        assert world.captain.standing.customs_heat["Mediterranean"] == heat_before + 5

    def test_trust_penalty(self):
        world = _make_world()
        trust_before = world.captain.standing.commercial_trust
        apply_consequence(world, Consequence(
            id="test", category="sea", trigger="test", text="test",
            effect_type="threat", trust_delta=-3,
        ))
        assert world.captain.standing.commercial_trust == max(0, trust_before - 3)

    def test_silver_never_negative(self):
        world = _make_world()
        world.captain.silver = 10
        apply_consequence(world, Consequence(
            id="test", category="sea", trigger="test", text="test",
            effect_type="threat", silver_delta=-100,
        ))
        assert world.captain.silver == 0
