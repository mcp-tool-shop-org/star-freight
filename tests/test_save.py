"""Tests for save/load round-trip and migration."""

import json
from pathlib import Path

import pytest

from portlight.content.world import new_game
from portlight.engine.economy import execute_buy, recalculate_prices
from portlight.engine.save import (
    CURRENT_SAVE_VERSION,
    SaveVersionError,
    load_game,
    migrate_save,
    save_game,
    world_to_dict,
)
from portlight.content.goods import GOODS
from portlight.receipts.models import ReceiptLedger, TradeReceipt, TradeAction


class TestSaveLoad:
    def test_round_trip_fresh_game(self, tmp_path: Path):
        world = new_game("Hawk")
        save_game(world, base_path=tmp_path)
        result = load_game(base_path=tmp_path)
        assert result is not None
        loaded, ledger, _board, _infra, _campaign, _narrative = result
        assert loaded.captain.name == "Hawk"
        assert loaded.captain.silver == 550  # Merchant starting silver
        assert loaded.day == 1
        assert len(loaded.ports) == 20

    def test_round_trip_with_cargo(self, tmp_path: Path):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 5, GOODS)
        save_game(world, base_path=tmp_path)
        loaded, _, _board, _infra, _campaign, _narrative = load_game(base_path=tmp_path)
        assert len(loaded.captain.cargo) == 1
        assert loaded.captain.cargo[0].good_id == "grain"
        assert loaded.captain.cargo[0].quantity == 5

    def test_round_trip_with_ledger(self, tmp_path: Path):
        world = new_game()
        ledger = ReceiptLedger(run_id="test-run")
        ledger.append(TradeReceipt(
            receipt_id="abc",
            captain_name="Hawk",
            port_id="porto_novo",
            good_id="grain",
            action=TradeAction.BUY,
            quantity=10,
            unit_price=12,
            total_price=120,
            day=1,
        ))
        save_game(world, ledger, base_path=tmp_path)
        _, loaded_ledger, _board, _infra, _campaign, _narrative = load_game(base_path=tmp_path)
        assert loaded_ledger.run_id == "test-run"
        assert len(loaded_ledger.receipts) == 1
        assert loaded_ledger.total_buys == 120

    def test_no_save_returns_none(self, tmp_path: Path):
        assert load_game(base_path=tmp_path) is None

    def test_corrupt_save_returns_none(self, tmp_path: Path):
        save_dir = tmp_path / "saves"
        save_dir.mkdir()
        (save_dir / "portlight_save.json").write_text("{{broken", encoding="utf-8")
        assert load_game(base_path=tmp_path) is None

    def test_market_prices_preserved(self, tmp_path: Path):
        world = new_game()
        porto = world.ports["porto_novo"]
        grain = next(s for s in porto.market if s.good_id == "grain")
        original_buy = grain.buy_price
        save_game(world, base_path=tmp_path)
        loaded, _, _board, _infra, _campaign, _narrative = load_game(base_path=tmp_path)
        loaded_grain = next(s for s in loaded.ports["porto_novo"].market if s.good_id == "grain")
        assert loaded_grain.buy_price == original_buy

    def test_voyage_state_preserved(self, tmp_path: Path):
        from portlight.engine.voyage import depart
        world = new_game()
        depart(world, "al_manar")
        save_game(world, base_path=tmp_path)
        loaded, _, _board, _infra, _campaign, _narrative = load_game(base_path=tmp_path)
        assert loaded.voyage.destination_id == "al_manar"
        assert loaded.voyage.status.value == "at_sea"

    def test_ship_state_preserved(self, tmp_path: Path):
        world = new_game()
        world.captain.ship.hull = 42
        world.captain.ship.crew = 5
        save_game(world, base_path=tmp_path)
        loaded, _, _board, _infra, _campaign, _narrative = load_game(base_path=tmp_path)
        assert loaded.captain.ship.hull == 42
        assert loaded.captain.ship.crew == 5


class TestSaveMigration:
    def test_current_version_no_migration(self):
        world = new_game("Hawk")
        data = world_to_dict(world)
        assert data["version"] == CURRENT_SAVE_VERSION
        migrated = migrate_save(data)
        assert migrated["version"] == CURRENT_SAVE_VERSION

    def test_v1_migrates_to_current(self):
        """A v1 save (minimal fields) migrates to current version."""
        world = new_game("Hawk")
        from portlight.engine.campaign import CampaignState
        from portlight.engine.infrastructure import InfrastructureState
        from portlight.engine.contracts import ContractBoard
        data = world_to_dict(world, ReceiptLedger(), ContractBoard(), InfrastructureState(), CampaignState())
        # Simulate v1: strip optional sections and set version=1
        data["version"] = 1
        del data["campaign"]
        del data["infrastructure"]
        del data["contract_board"]
        del data["ledger"]
        migrated = migrate_save(data)
        assert migrated["version"] == CURRENT_SAVE_VERSION
        assert "campaign" in migrated
        assert "infrastructure" in migrated
        assert "contract_board" in migrated
        assert "ledger" in migrated

    def test_v1_save_loads_successfully(self, tmp_path: Path):
        """A v1 save file on disk loads through the migration chain."""
        world = new_game("Hawk")
        from portlight.engine.campaign import CampaignState
        from portlight.engine.infrastructure import InfrastructureState
        from portlight.engine.contracts import ContractBoard
        data = world_to_dict(world, ReceiptLedger(), ContractBoard(), InfrastructureState(), CampaignState())
        data["version"] = 1
        del data["campaign"]
        save_dir = tmp_path / "saves"
        save_dir.mkdir()
        (save_dir / "portlight_save.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8",
        )
        result = load_game(base_path=tmp_path)
        assert result is not None
        loaded, _ledger, _board, _infra, _campaign, _narrative = result
        assert loaded.captain.name == "Hawk"

    def test_future_version_raises_version_error(self, tmp_path: Path):
        """A save from a newer version raises SaveVersionError with descriptive message."""
        world = new_game("Hawk")
        data = world_to_dict(world)
        data["version"] = 999
        save_dir = tmp_path / "saves"
        save_dir.mkdir()
        (save_dir / "portlight_save.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8",
        )
        with pytest.raises(SaveVersionError, match="version 999 is newer"):
            load_game(base_path=tmp_path)
