"""Tests for Packet 3D-1 — Warehouse Infrastructure.

Law tests: structural invariants.
Behavior tests: deposit, withdraw, provenance, capacity, upkeep.
Integration tests: session-level wiring, save/load.
"""

import pytest

from portlight.content.goods import GOODS
from portlight.content.infrastructure import (
    PORT_WAREHOUSE_TIERS,
    WAREHOUSE_TIERS,
    available_tiers,
)
from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.economy import execute_buy, recalculate_prices
from portlight.engine.infrastructure import (
    InfrastructureState,
    StoredLot,
    WarehouseLease,
    WarehouseTier,
    deposit_cargo,
    get_warehouse,
    lease_warehouse,
    tick_infrastructure,
    warehouse_summary,
    withdraw_cargo,
)
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
def depot_spec():
    return WAREHOUSE_TIERS[WarehouseTier.DEPOT]


@pytest.fixture
def regional_spec():
    return WAREHOUSE_TIERS[WarehouseTier.REGIONAL]


# ---------------------------------------------------------------------------
# Content law tests
# ---------------------------------------------------------------------------

class TestContentLaws:
    def test_three_tiers_exist(self):
        assert len(WAREHOUSE_TIERS) == 3

    def test_all_ports_have_at_least_depot(self):
        for port_id, tiers in PORT_WAREHOUSE_TIERS.items():
            assert WarehouseTier.DEPOT in tiers, f"{port_id} missing depot"

    def test_capacity_increases_with_tier(self):
        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        regional = WAREHOUSE_TIERS[WarehouseTier.REGIONAL]
        commercial = WAREHOUSE_TIERS[WarehouseTier.COMMERCIAL]
        assert depot.capacity < regional.capacity < commercial.capacity

    def test_upkeep_increases_with_tier(self):
        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        regional = WAREHOUSE_TIERS[WarehouseTier.REGIONAL]
        commercial = WAREHOUSE_TIERS[WarehouseTier.COMMERCIAL]
        assert depot.upkeep_per_day < regional.upkeep_per_day < commercial.upkeep_per_day

    def test_lease_cost_increases_with_tier(self):
        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        regional = WAREHOUSE_TIERS[WarehouseTier.REGIONAL]
        commercial = WAREHOUSE_TIERS[WarehouseTier.COMMERCIAL]
        assert depot.lease_cost < regional.lease_cost < commercial.lease_cost

    def test_commercial_only_at_major_ports(self):
        for port_id, tiers in PORT_WAREHOUSE_TIERS.items():
            if WarehouseTier.COMMERCIAL in tiers:
                # Should also have depot and regional
                assert WarehouseTier.DEPOT in tiers
                assert WarehouseTier.REGIONAL in tiers

    def test_available_tiers_returns_specs(self):
        tiers = available_tiers("porto_novo")
        assert len(tiers) == 3
        assert tiers[0].tier == WarehouseTier.DEPOT


# ---------------------------------------------------------------------------
# Lease tests
# ---------------------------------------------------------------------------

class TestLease:
    def test_lease_success(self, world, infra, depot_spec):
        captain = world.captain
        silver_before = captain.silver
        result = lease_warehouse(infra, captain, "porto_novo", depot_spec, day=5)
        assert isinstance(result, WarehouseLease)
        assert result.port_id == "porto_novo"
        assert result.tier == WarehouseTier.DEPOT
        assert result.active is True
        assert captain.silver == silver_before - depot_spec.lease_cost
        assert len(infra.warehouses) == 1

    def test_lease_insufficient_silver(self, world, infra):
        spec = WAREHOUSE_TIERS[WarehouseTier.COMMERCIAL]
        world.captain.silver = 100  # Not enough for 500
        result = lease_warehouse(infra, world.captain, "porto_novo", spec, day=1)
        assert isinstance(result, str)
        assert "Need" in result

    def test_lease_duplicate_same_tier(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        result = lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=2)
        assert isinstance(result, str)
        assert "Already have" in result

    def test_upgrade_closes_old(self, world, infra, depot_spec, regional_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        result = lease_warehouse(infra, world.captain, "porto_novo", regional_spec, day=5)
        assert isinstance(result, WarehouseLease)
        assert result.tier == WarehouseTier.REGIONAL
        active = [w for w in infra.warehouses if w.active]
        assert len(active) == 1
        assert active[0].tier == WarehouseTier.REGIONAL

    def test_upgrade_preserves_inventory(self, world, infra, depot_spec, regional_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        wh = get_warehouse(infra, "porto_novo")
        wh.inventory.append(StoredLot(
            good_id="grain", quantity=5,
            acquired_port="porto_novo", acquired_region="Mediterranean",
            acquired_day=1, deposited_day=2,
        ))
        lease_warehouse(infra, world.captain, "porto_novo", regional_spec, day=5)
        new_wh = get_warehouse(infra, "porto_novo")
        assert len(new_wh.inventory) == 1
        assert new_wh.inventory[0].good_id == "grain"
        assert new_wh.inventory[0].quantity == 5

    def test_different_ports(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        lease_warehouse(infra, world.captain, "al_manar", depot_spec, day=1)
        active = warehouse_summary(infra)
        assert len(active) == 2


# ---------------------------------------------------------------------------
# Deposit tests
# ---------------------------------------------------------------------------

class TestDeposit:
    def _setup_warehouse(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 10, GOODS)

    def test_deposit_success(self, world, infra, depot_spec):
        self._setup_warehouse(world, infra, depot_spec)
        result = deposit_cargo(infra, "porto_novo", world.captain, "grain", 5, day=2)
        assert result == 5
        wh = get_warehouse(infra, "porto_novo")
        assert wh.used_capacity == 5
        # Ship should have 5 less
        grain = next(c for c in world.captain.cargo if c.good_id == "grain")
        assert grain.quantity == 5

    def test_deposit_all_removes_from_ship(self, world, infra, depot_spec):
        self._setup_warehouse(world, infra, depot_spec)
        deposit_cargo(infra, "porto_novo", world.captain, "grain", 10, day=2)
        assert not any(c.good_id == "grain" for c in world.captain.cargo)

    def test_deposit_preserves_provenance(self, world, infra, depot_spec):
        self._setup_warehouse(world, infra, depot_spec)
        deposit_cargo(infra, "porto_novo", world.captain, "grain", 5, day=2)
        wh = get_warehouse(infra, "porto_novo")
        lot = wh.inventory[0]
        assert lot.acquired_port == "porto_novo"
        assert lot.acquired_region == "Mediterranean"

    def test_deposit_no_warehouse(self, world, infra):
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 5, GOODS)
        result = deposit_cargo(infra, "porto_novo", world.captain, "grain", 5, day=1)
        assert isinstance(result, str)
        assert "No warehouse" in result

    def test_deposit_exceeds_capacity(self, world, infra, depot_spec):
        self._setup_warehouse(world, infra, depot_spec)
        # Depot capacity is 20, buy more grain
        port = world.ports["porto_novo"]
        execute_buy(world.captain, port, "grain", 15, GOODS)
        # Now have 25 grain, try to deposit all
        result = deposit_cargo(infra, "porto_novo", world.captain, "grain", 25, day=2)
        assert isinstance(result, str)
        assert "space" in result

    def test_deposit_insufficient_cargo(self, world, infra, depot_spec):
        self._setup_warehouse(world, infra, depot_spec)
        result = deposit_cargo(infra, "porto_novo", world.captain, "grain", 50, day=2)
        assert isinstance(result, str)
        assert "Only have" in result

    def test_deposit_merges_same_provenance(self, world, infra, depot_spec):
        self._setup_warehouse(world, infra, depot_spec)
        deposit_cargo(infra, "porto_novo", world.captain, "grain", 3, day=2)
        # Buy more grain from same port, deposit again
        port = world.ports["porto_novo"]
        execute_buy(world.captain, port, "grain", 5, GOODS)
        deposit_cargo(infra, "porto_novo", world.captain, "grain", 5, day=3)
        wh = get_warehouse(infra, "porto_novo")
        # Should merge into single lot (same provenance)
        grain_lots = [lot for lot in wh.inventory if lot.good_id == "grain"]
        assert len(grain_lots) == 1
        assert grain_lots[0].quantity == 8  # 3 + 5


# ---------------------------------------------------------------------------
# Withdraw tests
# ---------------------------------------------------------------------------

class TestWithdraw:
    def _setup_with_stored(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        wh = get_warehouse(infra, "porto_novo")
        wh.inventory.append(StoredLot(
            good_id="grain", quantity=10,
            acquired_port="porto_novo", acquired_region="Mediterranean",
            acquired_day=1, deposited_day=2,
        ))

    def test_withdraw_success(self, world, infra, depot_spec):
        self._setup_with_stored(world, infra, depot_spec)
        result = withdraw_cargo(infra, "porto_novo", world.captain, "grain", 5)
        assert result == 5
        wh = get_warehouse(infra, "porto_novo")
        assert wh.inventory[0].quantity == 5
        grain = next(c for c in world.captain.cargo if c.good_id == "grain")
        assert grain.quantity == 5

    def test_withdraw_all_clears_lot(self, world, infra, depot_spec):
        self._setup_with_stored(world, infra, depot_spec)
        withdraw_cargo(infra, "porto_novo", world.captain, "grain", 10)
        wh = get_warehouse(infra, "porto_novo")
        assert len(wh.inventory) == 0

    def test_withdraw_preserves_provenance(self, world, infra, depot_spec):
        self._setup_with_stored(world, infra, depot_spec)
        withdraw_cargo(infra, "porto_novo", world.captain, "grain", 5)
        grain = next(c for c in world.captain.cargo if c.good_id == "grain")
        assert grain.acquired_port == "porto_novo"
        assert grain.acquired_region == "Mediterranean"

    def test_withdraw_no_warehouse(self, world, infra):
        result = withdraw_cargo(infra, "porto_novo", world.captain, "grain", 5)
        assert isinstance(result, str)
        assert "No warehouse" in result

    def test_withdraw_insufficient_stock(self, world, infra, depot_spec):
        self._setup_with_stored(world, infra, depot_spec)
        # Request more than stored (10) but within ship capacity
        result = withdraw_cargo(infra, "porto_novo", world.captain, "grain", 15)
        assert isinstance(result, str)
        assert "Only" in result

    def test_withdraw_exceeds_ship_capacity(self, world, infra, depot_spec):
        self._setup_with_stored(world, infra, depot_spec)
        # Fill ship cargo to near capacity
        world.captain.ship.cargo_capacity = 12
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 10, GOODS)
        result = withdraw_cargo(infra, "porto_novo", world.captain, "grain", 10)
        assert isinstance(result, str)
        assert "cargo space" in result

    def test_withdraw_source_filter(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        wh = get_warehouse(infra, "porto_novo")
        wh.inventory.append(StoredLot(
            good_id="grain", quantity=5,
            acquired_port="porto_novo", acquired_region="Mediterranean",
            acquired_day=1, deposited_day=2,
        ))
        wh.inventory.append(StoredLot(
            good_id="grain", quantity=5,
            acquired_port="al_manar", acquired_region="Mediterranean",
            acquired_day=1, deposited_day=2,
        ))
        result = withdraw_cargo(infra, "porto_novo", world.captain, "grain", 3, source_port="al_manar")
        assert result == 3
        # Should only take from al_manar lot
        al_lot = next(lot for lot in wh.inventory if lot.acquired_port == "al_manar")
        assert al_lot.quantity == 2
        porto_lot = next(lot for lot in wh.inventory if lot.acquired_port == "porto_novo")
        assert porto_lot.quantity == 5  # Untouched


# ---------------------------------------------------------------------------
# Upkeep tests
# ---------------------------------------------------------------------------

class TestUpkeep:
    def test_upkeep_deducts_silver(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        silver_before = world.captain.silver
        tick_infrastructure(infra, world.captain, day=2)
        assert world.captain.silver == silver_before - depot_spec.upkeep_per_day

    def test_multi_day_upkeep(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        silver_before = world.captain.silver
        tick_infrastructure(infra, world.captain, day=4)  # 3 days owed
        assert world.captain.silver == silver_before - depot_spec.upkeep_per_day * 3

    def test_closure_on_default(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        world.captain.silver = 0  # Can't pay
        messages = tick_infrastructure(infra, world.captain, day=5)  # 4 days unpaid >= 3
        wh = infra.warehouses[-1]
        assert wh.active is False
        assert len(messages) > 0
        assert "closed" in messages[0].lower()

    def test_closure_seizes_goods(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        wh = get_warehouse(infra, "porto_novo")
        wh.inventory.append(StoredLot(
            good_id="silk", quantity=5,
            acquired_port="jade_port", acquired_region="East Indies",
            acquired_day=1, deposited_day=2,
        ))
        world.captain.silver = 0
        messages = tick_infrastructure(infra, world.captain, day=5)
        assert wh.active is False
        assert len(wh.inventory) == 0
        assert "silk" in messages[0].lower() or "seized" in messages[0].lower()

    def test_no_upkeep_when_paid(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        tick_infrastructure(infra, world.captain, day=2)
        silver_after = world.captain.silver
        tick_infrastructure(infra, world.captain, day=2)  # Same day, no additional charge
        assert world.captain.silver == silver_after

    def test_inactive_warehouse_no_upkeep(self, world, infra, depot_spec):
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        wh = infra.warehouses[-1]
        wh.active = False
        silver_before = world.captain.silver
        tick_infrastructure(infra, world.captain, day=10)
        assert world.captain.silver == silver_before


# ---------------------------------------------------------------------------
# Save/load round-trip tests
# ---------------------------------------------------------------------------

class TestInfraSaveLoad:
    def test_warehouse_roundtrip(self, world):
        infra = InfrastructureState()
        lease = WarehouseLease(
            id="test-wh", port_id="porto_novo",
            tier=WarehouseTier.DEPOT, capacity=20,
            lease_cost=50, upkeep_per_day=1,
            opened_day=3, upkeep_paid_through=5, active=True,
        )
        lease.inventory.append(StoredLot(
            good_id="grain", quantity=8,
            acquired_port="porto_novo", acquired_region="Mediterranean",
            acquired_day=1, deposited_day=3,
        ))
        infra.warehouses.append(lease)

        d = world_to_dict(world, infra=infra)
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)

        assert len(loaded_infra.warehouses) == 1
        wh = loaded_infra.warehouses[0]
        assert wh.id == "test-wh"
        assert wh.tier == WarehouseTier.DEPOT
        assert wh.capacity == 20
        assert wh.active is True
        assert len(wh.inventory) == 1
        assert wh.inventory[0].good_id == "grain"
        assert wh.inventory[0].quantity == 8
        assert wh.inventory[0].acquired_port == "porto_novo"

    def test_empty_infra_roundtrip(self, world):
        d = world_to_dict(world)
        _, _, _, loaded_infra, _campaign, _narrative = world_from_dict(d)
        assert len(loaded_infra.warehouses) == 0

    def test_save_load_with_infra(self, tmp_path, world):
        from portlight.engine.save import save_game, load_game

        infra = InfrastructureState()
        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        lease_warehouse(infra, world.captain, "porto_novo", depot, day=1)

        save_game(world, infra=infra, base_path=tmp_path)
        result = load_game(base_path=tmp_path)
        assert result is not None
        _, _, _, loaded_infra, _campaign, _narrative = result
        assert len(loaded_infra.warehouses) == 1
        assert loaded_infra.warehouses[0].port_id == "porto_novo"


# ---------------------------------------------------------------------------
# Session integration tests
# ---------------------------------------------------------------------------

class TestSessionIntegration:
    def test_session_has_infra(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")
        assert s.infra is not None
        assert isinstance(s.infra, InfrastructureState)

    def test_session_infra_persists(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")

        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        s.lease_warehouse_cmd(depot)
        assert len(s.infra.warehouses) == 1

        s2 = GameSession(base_path=tmp_path)
        s2.load()
        assert len(s2.infra.warehouses) == 1

    def test_deposit_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")

        # Lease warehouse
        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        s.lease_warehouse_cmd(depot)

        # Buy grain
        s.buy("grain", 5)

        # Deposit
        result = s.deposit_cmd("grain", 3)
        assert result == 3
        wh = get_warehouse(s.infra, "porto_novo")
        assert wh.used_capacity == 3

    def test_withdraw_via_session(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")

        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        s.lease_warehouse_cmd(depot)

        # Buy, deposit, then withdraw
        s.buy("grain", 5)
        s.deposit_cmd("grain", 5)
        result = s.withdraw_cmd("grain", 3)
        assert result == 3

    def test_upkeep_on_advance(self, tmp_path):
        from portlight.app.session import GameSession
        s = GameSession(base_path=tmp_path)
        s.new("Tester", captain_type="merchant")

        depot = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        s.lease_warehouse_cmd(depot)

        # First advance: day goes from 1→2, tick fires at day 1 (0 owed since paid_through=1)
        s.advance()
        silver_before = s.captain.silver

        # Second advance: day goes from 2→3, tick fires at day 2 (1 day owed)
        s.advance()
        assert s.captain.silver < silver_before


# ---------------------------------------------------------------------------
# Contract + warehouse interaction test
# ---------------------------------------------------------------------------

class TestWarehouseContractInteraction:
    def test_withdrawn_cargo_preserves_provenance_for_contracts(self, world, infra, depot_spec):
        """Cargo withdrawn from warehouse preserves source provenance for contract validation."""
        lease_warehouse(infra, world.captain, "porto_novo", depot_spec, day=1)
        wh = get_warehouse(infra, "porto_novo")
        wh.inventory.append(StoredLot(
            good_id="silk", quantity=5,
            acquired_port="silk_haven", acquired_region="East Indies",
            acquired_day=1, deposited_day=3,
        ))

        withdraw_cargo(infra, "porto_novo", world.captain, "silk", 5)
        cargo = next(c for c in world.captain.cargo if c.good_id == "silk")
        assert cargo.acquired_port == "silk_haven"
        assert cargo.acquired_region == "East Indies"
        # This provenance would satisfy a contract requiring source_region="East Indies"
