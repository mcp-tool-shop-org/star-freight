"""Tests for ship stat resolution with upgrades."""

from portlight.engine.models import InstalledUpgrade, Ship
from portlight.content.upgrades import UPGRADES
from portlight.content.ships import SHIPS, create_ship_from_template
from portlight.engine.ship_stats import (
    has_special,
    resolve_all,
    resolve_cannons,
    resolve_cargo_capacity,
    resolve_crew_max,
    resolve_hull_max,
    resolve_maneuver,
    resolve_speed,
    resolve_storm_resist,
    resolved_ship,
)


def _make_ship(template_id="trade_brigantine", **overrides) -> Ship:
    defaults = dict(
        template_id=template_id,
        name=f"Test {template_id}",
        hull=100, hull_max=100,
        cargo_capacity=80, speed=6.0,
        crew=15, crew_max=20,
        cannons=6, maneuver=0.5,
        upgrade_slots=4,
    )
    defaults.update(overrides)
    return Ship(**defaults)


# ---------------------------------------------------------------------------
# No upgrades — base values
# ---------------------------------------------------------------------------

class TestNoUpgrades:
    def test_speed_returns_base(self):
        ship = _make_ship(speed=6.0)
        assert resolve_speed(ship, UPGRADES) == 6.0

    def test_hull_max_returns_base(self):
        ship = _make_ship(hull_max=100)
        assert resolve_hull_max(ship, UPGRADES) == 100

    def test_cargo_returns_base(self):
        ship = _make_ship(cargo_capacity=80)
        assert resolve_cargo_capacity(ship, UPGRADES) == 80

    def test_cannons_returns_base(self):
        ship = _make_ship(cannons=6)
        assert resolve_cannons(ship, UPGRADES) == 6

    def test_maneuver_returns_base(self):
        ship = _make_ship(maneuver=0.5)
        assert resolve_maneuver(ship, UPGRADES) == 0.5

    def test_crew_max_returns_base(self):
        ship = _make_ship(crew_max=20)
        assert resolve_crew_max(ship, UPGRADES) == 20


# ---------------------------------------------------------------------------
# Single upgrade effects
# ---------------------------------------------------------------------------

class TestSingleUpgrade:
    def test_lateen_rigging_adds_speed(self):
        ship = _make_ship(speed=6.0, upgrades=[InstalledUpgrade("lateen_rigging")])
        assert resolve_speed(ship, UPGRADES) == 6.5

    def test_square_sails_adds_more_speed(self):
        ship = _make_ship(speed=6.0, upgrades=[InstalledUpgrade("square_sails")])
        assert resolve_speed(ship, UPGRADES) == 7.0

    def test_iron_strapping_adds_hull(self):
        ship = _make_ship(hull_max=100, upgrades=[InstalledUpgrade("iron_strapping")])
        assert resolve_hull_max(ship, UPGRADES) == 115

    def test_copper_sheathing_adds_hull_reduces_speed(self):
        ship = _make_ship(
            hull_max=100, speed=6.0,
            upgrades=[InstalledUpgrade("copper_sheathing")],
        )
        assert resolve_hull_max(ship, UPGRADES) == 125
        assert resolve_speed(ship, UPGRADES) == 5.9

    def test_lead_lined_heavy_penalty(self):
        ship = _make_ship(
            hull_max=100, speed=6.0,
            upgrades=[InstalledUpgrade("lead_lined")],
        )
        assert resolve_hull_max(ship, UPGRADES) == 140
        assert resolve_speed(ship, UPGRADES) == 5.7

    def test_extra_gun_ports(self):
        ship = _make_ship(cannons=6, upgrades=[InstalledUpgrade("extra_gun_ports")])
        assert resolve_cannons(ship, UPGRADES) == 8

    def test_extended_hold(self):
        ship = _make_ship(cargo_capacity=80, upgrades=[InstalledUpgrade("extended_hold")])
        assert resolve_cargo_capacity(ship, UPGRADES) == 90

    def test_improved_rudder(self):
        ship = _make_ship(maneuver=0.5, upgrades=[InstalledUpgrade("improved_rudder")])
        assert resolve_maneuver(ship, UPGRADES) == 0.6

    def test_hammock_deck(self):
        ship = _make_ship(crew_max=20, upgrades=[InstalledUpgrade("hammock_deck")])
        assert resolve_crew_max(ship, UPGRADES) == 25

    def test_storm_canvas_adds_speed_and_storm_resist(self):
        ship = _make_ship(speed=6.0, upgrades=[InstalledUpgrade("storm_canvas")])
        template = SHIPS["trade_brigantine"]
        assert resolve_speed(ship, UPGRADES) == 6.3
        sr = resolve_storm_resist(ship, template, UPGRADES)
        assert abs(sr - 0.4) < 0.01  # 0.3 base + 0.1 bonus


# ---------------------------------------------------------------------------
# Multiple upgrades stacking
# ---------------------------------------------------------------------------

class TestUpgradeStacking:
    def test_two_speed_upgrades_stack(self):
        ship = _make_ship(speed=6.0, upgrades=[
            InstalledUpgrade("lateen_rigging"),
            InstalledUpgrade("square_sails"),
        ])
        assert resolve_speed(ship, UPGRADES) == 7.5

    def test_speed_bonus_minus_penalty(self):
        ship = _make_ship(speed=6.0, upgrades=[
            InstalledUpgrade("square_sails"),       # +1.0
            InstalledUpgrade("copper_sheathing"),    # -0.1
        ])
        assert abs(resolve_speed(ship, UPGRADES) - 6.9) < 0.01

    def test_multiple_hull_bonuses(self):
        ship = _make_ship(hull_max=100, upgrades=[
            InstalledUpgrade("iron_strapping"),   # +15
            InstalledUpgrade("lead_lined"),       # +40
        ])
        assert resolve_hull_max(ship, UPGRADES) == 155


# ---------------------------------------------------------------------------
# Clamping and edge cases
# ---------------------------------------------------------------------------

class TestClamping:
    def test_maneuver_capped_at_1(self):
        ship = _make_ship(maneuver=0.9, upgrades=[
            InstalledUpgrade("improved_rudder"),  # +0.1
            InstalledUpgrade("swivel_guns"),       # +0.05
        ])
        assert resolve_maneuver(ship, UPGRADES) == 1.0

    def test_storm_resist_capped_at_09(self):
        ship = _make_ship(upgrades=[
            InstalledUpgrade("storm_canvas"),   # +0.1
            InstalledUpgrade("compass_rose"),   # +0.1
        ])
        template = SHIPS["royal_man_of_war"]  # 0.8 base
        sr = resolve_storm_resist(ship, template, UPGRADES)
        assert sr == 0.9  # capped

    def test_speed_minimum_05(self):
        ship = _make_ship(speed=0.5, upgrades=[
            InstalledUpgrade("lead_lined"),           # -0.3
            InstalledUpgrade("reinforced_bulkheads"),  # -0.1
        ])
        assert resolve_speed(ship, UPGRADES) == 0.5  # clamped floor

    def test_unknown_upgrade_id_ignored(self):
        ship = _make_ship(speed=6.0, upgrades=[InstalledUpgrade("nonexistent")])
        assert resolve_speed(ship, UPGRADES) == 6.0


# ---------------------------------------------------------------------------
# Special tag detection
# ---------------------------------------------------------------------------

class TestSpecialTags:
    def test_contraband_immune_detected(self):
        ship = _make_ship(upgrades=[InstalledUpgrade("hidden_compartments")])
        assert has_special(ship, "contraband_immune", UPGRADES)

    def test_chain_shot_detected(self):
        ship = _make_ship(upgrades=[InstalledUpgrade("chain_shot_racks")])
        assert has_special(ship, "chain_shot", UPGRADES)

    def test_no_special_when_absent(self):
        ship = _make_ship(upgrades=[InstalledUpgrade("iron_strapping")])
        assert not has_special(ship, "contraband_immune", UPGRADES)

    def test_no_special_on_empty_upgrades(self):
        ship = _make_ship()
        assert not has_special(ship, "chain_shot", UPGRADES)


# ---------------------------------------------------------------------------
# Resolved ship copy
# ---------------------------------------------------------------------------

class TestResolvedShip:
    def test_resolved_ship_has_effective_stats(self):
        ship = _make_ship(
            speed=6.0, hull_max=100, cannons=6, maneuver=0.5,
            cargo_capacity=80, crew_max=20,
            upgrades=[
                InstalledUpgrade("square_sails"),       # +1.0 speed
                InstalledUpgrade("iron_strapping"),      # +15 hull
                InstalledUpgrade("extra_gun_ports"),     # +2 cannons
            ],
        )
        rs = resolved_ship(ship, UPGRADES)
        assert rs.speed == 7.0
        assert rs.hull_max == 115
        assert rs.cannons == 8
        assert rs.maneuver == 0.5  # unchanged
        assert rs.cargo_capacity == 80  # unchanged
        assert rs.crew_max == 20  # unchanged

    def test_resolved_ship_preserves_mutable_state(self):
        ship = _make_ship(hull=42, crew=10)
        rs = resolved_ship(ship, UPGRADES)
        assert rs.hull == 42
        assert rs.crew == 10
        assert rs.template_id == ship.template_id

    def test_resolved_ship_does_not_mutate_original(self):
        ship = _make_ship(speed=6.0, upgrades=[InstalledUpgrade("square_sails")])
        rs = resolved_ship(ship, UPGRADES)
        assert rs.speed == 7.0
        assert ship.speed == 6.0  # original unchanged


# ---------------------------------------------------------------------------
# resolve_all dict
# ---------------------------------------------------------------------------

class TestResolveAll:
    def test_returns_all_stats(self):
        ship = _make_ship(upgrades=[InstalledUpgrade("lateen_rigging")])
        template = SHIPS["trade_brigantine"]
        stats = resolve_all(ship, template, UPGRADES)
        assert "speed" in stats
        assert "hull_max" in stats
        assert "cargo_capacity" in stats
        assert "cannons" in stats
        assert "maneuver" in stats
        assert "storm_resist" in stats
        assert "crew_max" in stats
        assert stats["speed"] == 6.5


# ---------------------------------------------------------------------------
# Integration: create_ship_from_template + resolve
# ---------------------------------------------------------------------------

class TestTemplateIntegration:
    def test_all_ships_resolve_cleanly_without_upgrades(self):
        for tid, tmpl in SHIPS.items():
            ship = create_ship_from_template(tmpl)
            stats = resolve_all(ship, tmpl, UPGRADES)
            assert stats["speed"] == tmpl.speed
            assert stats["hull_max"] == tmpl.hull_max
            assert stats["cargo_capacity"] == tmpl.cargo_capacity
            assert stats["cannons"] == tmpl.cannons
            assert stats["maneuver"] == tmpl.maneuver
            assert stats["storm_resist"] == tmpl.storm_resist
            assert stats["crew_max"] == tmpl.crew_max
