"""Tests for the contract breach tracking and wanted system."""

import random

from portlight.content.world import new_game
from portlight.engine.contracts import (
    abandon_contract,
    tick_contracts,
    _record_breach,
    get_breach_count_for_family,
    ContractBoard,
    ContractStatus,
    ActiveContract,
)


class TestBreachRecording:
    def test_abandon_records_breach(self):
        """Abandoning a contract should create a breach record."""
        world = new_game()
        board = ContractBoard()
        contract = ActiveContract(
            offer_id="test_01",
            template_id="t01",
            title="Test Contract",
            good_id="grain",
            required_quantity=10,
            reward_silver=200,
            bonus_reward=30,
            destination_port_id="ironhaven",
            source_region="North Atlantic",
            deadline_day=20,
            family="procurement",
            accepted_day=1,
        )
        contract.status = ContractStatus.ACCEPTED
        board.active.append(contract)

        outcome = abandon_contract(board, "test_01", day=5, captain=world.captain)
        assert not isinstance(outcome, str)
        assert len(world.captain.breach_records) == 1
        assert world.captain.breach_records[0]["contract_id"] == "test_01"

    def test_expired_contract_records_breach(self):
        """Expired contracts should create breach records."""
        world = new_game()
        board = ContractBoard()
        contract = ActiveContract(
            offer_id="test_02",
            template_id="t02",
            title="Expired Test",
            good_id="timber",
            required_quantity=5,
            reward_silver=100,
            bonus_reward=20,
            destination_port_id="stormwall",
            source_region="North Atlantic",
            deadline_day=10,
            family="procurement",
            accepted_day=1,
        )
        contract.status = ContractStatus.ACCEPTED
        board.active.append(contract)

        outcomes = tick_contracts(board, day=11, captain=world.captain)
        assert len(outcomes) == 1
        assert len(world.captain.breach_records) == 1


class TestWantedLevel:
    def test_two_breaches_sets_watched(self):
        world = new_game()
        _record_breach(world.captain, "c1", 5, "porto_novo", "procurement")
        assert world.captain.wanted_level == 0  # 1 breach = nothing
        _record_breach(world.captain, "c2", 10, "ironhaven", "procurement")
        assert world.captain.wanted_level == 1  # watched

    def test_three_breaches_sets_wanted(self):
        world = new_game()
        for i in range(3):
            _record_breach(world.captain, f"c{i}", i * 5, "porto_novo", "procurement")
        assert world.captain.wanted_level == 2  # wanted

    def test_five_breaches_sets_hunted(self):
        world = new_game()
        for i in range(5):
            _record_breach(world.captain, f"c{i}", i * 5, "porto_novo", "procurement")
        assert world.captain.wanted_level == 3  # hunted


class TestBountyHunterEncounter:
    def test_bounty_hunter_event_generated(self):
        """Bounty hunter events should be generated for wanted level 3 captains."""
        from portlight.engine.voyage import _bounty_hunter_event
        world = new_game()
        world.captain.wanted_level = 3
        _record_breach(world.captain, "c1", 5, "porto_novo", "procurement")
        event = _bounty_hunter_event(world.captain, random.Random(42))
        assert "Pact colors" in event.message or "commission" in event.message
        assert event._pending_duel is not None

    def test_bounty_hunter_not_at_low_wanted(self):
        """Bounty hunters should not appear at wanted level < 3."""
        from portlight.engine.voyage import advance_day, depart
        world = new_game()
        world.captain.wanted_level = 1  # watched, not hunted
        depart(world, "al_manar")
        # Run many days and check no bounty hunter appears
        bounty_events = 0
        for seed in range(50):
            events = advance_day(world, random.Random(seed))
            for e in events:
                if "commission" in e.message and "Pact" in e.message:
                    bounty_events += 1
            if world.voyage and world.voyage.status.value == "arrived":
                break
        assert bounty_events == 0


class TestBreachFamilyCounting:
    def test_count_breaches_by_family(self):
        world = new_game()
        _record_breach(world.captain, "c1", 5, "porto_novo", "procurement")
        _record_breach(world.captain, "c2", 10, "ironhaven", "luxury_discreet")
        _record_breach(world.captain, "c3", 15, "stormwall", "procurement")
        assert get_breach_count_for_family(world.captain, "procurement") == 2
        assert get_breach_count_for_family(world.captain, "luxury_discreet") == 1
        assert get_breach_count_for_family(world.captain, "smuggling") == 0
