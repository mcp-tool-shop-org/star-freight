"""Tests for crew specialization — roles, roster, effects, and save."""

import random
from pathlib import Path

from portlight.engine.models import (
    CrewRole,
    CrewRoster,
)
from portlight.content.crew_roles import (
    ROLE_SPECS,
    get_role_count,
    set_role_count,
)
from portlight.content.ships import SHIPS, create_ship_from_template
from portlight.content.world import new_game
from portlight.engine.ship_stats import (
    compute_daily_wages,
    gunner_damage_mult,
    marine_boarding_bonus,
    navigator_speed_bonus,
    navigator_storm_resist_bonus,
    quartermaster_sell_bonus,
    quartermaster_wage_discount,
    select_casualty,
    surgeon_death_reduction,
)
from portlight.engine.save import (
    CURRENT_SAVE_VERSION,
    load_game,
    migrate_save,
    save_game,
)
from portlight.app.session import GameSession


# ---------------------------------------------------------------------------
# Role specs
# ---------------------------------------------------------------------------

class TestRoleSpecs:
    def test_all_roles_have_specs(self):
        for role in CrewRole:
            assert role in ROLE_SPECS

    def test_sailor_unlimited(self):
        assert ROLE_SPECS[CrewRole.SAILOR].max_per_ship is None

    def test_navigator_max_1(self):
        assert ROLE_SPECS[CrewRole.NAVIGATOR].max_per_ship == 1

    def test_surgeon_max_1(self):
        assert ROLE_SPECS[CrewRole.SURGEON].max_per_ship == 1

    def test_quartermaster_max_1(self):
        assert ROLE_SPECS[CrewRole.QUARTERMASTER].max_per_ship == 1

    def test_gunner_max_3(self):
        assert ROLE_SPECS[CrewRole.GUNNER].max_per_ship == 3

    def test_marine_max_4(self):
        assert ROLE_SPECS[CrewRole.MARINE].max_per_ship == 4


# ---------------------------------------------------------------------------
# Roster model
# ---------------------------------------------------------------------------

class TestCrewRoster:
    def test_total_sums_all_roles(self):
        r = CrewRoster(sailors=5, gunners=2, navigators=1, marines=3)
        assert r.total == 11

    def test_empty_roster(self):
        r = CrewRoster()
        assert r.total == 0

    def test_get_and_set_role_count(self):
        r = CrewRoster()
        set_role_count(r, CrewRole.GUNNER, 3)
        assert get_role_count(r, CrewRole.GUNNER) == 3
        assert r.total == 3


# ---------------------------------------------------------------------------
# Ship crew sync
# ---------------------------------------------------------------------------

class TestShipCrewSync:
    def test_sync_crew_matches_roster(self):
        ship = create_ship_from_template(SHIPS["trade_brigantine"])
        ship.roster.gunners = 2
        ship.sync_crew()
        assert ship.crew == ship.roster.total

    def test_new_ship_has_sailors_roster(self):
        ship = create_ship_from_template(SHIPS["coastal_sloop"])
        assert ship.roster.sailors == 3  # crew_min for sloop
        assert ship.roster.total == ship.crew


# ---------------------------------------------------------------------------
# Role effects
# ---------------------------------------------------------------------------

class TestRoleEffects:
    def test_gunner_damage_mult_none(self):
        assert gunner_damage_mult(CrewRoster()) == 1.0

    def test_gunner_damage_mult_3(self):
        assert gunner_damage_mult(CrewRoster(gunners=3)) == 1.3

    def test_gunner_capped_at_3(self):
        assert gunner_damage_mult(CrewRoster(gunners=5)) == 1.3

    def test_navigator_speed_bonus_present(self):
        assert navigator_speed_bonus(CrewRoster(navigators=1)) == 0.5

    def test_navigator_speed_bonus_absent(self):
        assert navigator_speed_bonus(CrewRoster()) == 0.0

    def test_navigator_storm_resist(self):
        assert navigator_storm_resist_bonus(CrewRoster(navigators=1)) == 0.05

    def test_surgeon_death_reduction_present(self):
        assert surgeon_death_reduction(CrewRoster(surgeons=1)) == 0.30

    def test_marine_boarding_bonus(self):
        assert marine_boarding_bonus(CrewRoster(marines=4)) == 0.80

    def test_marine_capped_at_4(self):
        assert marine_boarding_bonus(CrewRoster(marines=6)) == 0.80

    def test_quartermaster_wage_discount(self):
        assert quartermaster_wage_discount(CrewRoster(quartermasters=1)) == 0.10

    def test_quartermaster_sell_bonus(self):
        assert quartermaster_sell_bonus(CrewRoster(quartermasters=1)) == 0.05


# ---------------------------------------------------------------------------
# Wage computation
# ---------------------------------------------------------------------------

class TestWages:
    def test_all_sailors(self):
        r = CrewRoster(sailors=10)
        assert compute_daily_wages(r) == 10  # 10 * 1

    def test_mixed_roster(self):
        r = CrewRoster(sailors=5, gunners=2, navigators=1)
        # 5*1 + 2*2 + 1*3 = 12
        assert compute_daily_wages(r) == 12

    def test_quartermaster_discount(self):
        r = CrewRoster(sailors=10, quartermasters=1)
        # Base: 10*1 + 1*2 = 12, discount 10% = 10 (int(12*0.9))
        assert compute_daily_wages(r) == int(12 * 0.90)


# ---------------------------------------------------------------------------
# Casualty selection
# ---------------------------------------------------------------------------

class TestCasualtySelection:
    def test_returns_none_empty_roster(self):
        r = CrewRoster()
        assert select_casualty(r, "storm", random.Random(42)) is None

    def test_selects_from_available(self):
        r = CrewRoster(sailors=5)
        result = select_casualty(r, "storm", random.Random(42))
        assert result == CrewRole.SAILOR

    def test_storm_favors_sailors(self):
        r = CrewRoster(sailors=5, navigators=1, surgeons=1)
        counts = {CrewRole.SAILOR: 0, CrewRole.NAVIGATOR: 0, CrewRole.SURGEON: 0}
        for seed in range(100):
            role = select_casualty(r, "storm", random.Random(seed))
            counts[role] += 1
        # Sailors should die most often in storms
        assert counts[CrewRole.SAILOR] > counts[CrewRole.NAVIGATOR]
        assert counts[CrewRole.SAILOR] > counts[CrewRole.SURGEON]

    def test_boarding_favors_marines(self):
        r = CrewRoster(sailors=5, marines=3)
        counts = {CrewRole.SAILOR: 0, CrewRole.MARINE: 0}
        for seed in range(100):
            role = select_casualty(r, "boarding", random.Random(seed))
            counts[role] += 1
        # Marines should die more in boarding
        assert counts[CrewRole.MARINE] > counts[CrewRole.SAILOR]


# ---------------------------------------------------------------------------
# Session hire/fire
# ---------------------------------------------------------------------------

class TestSessionCrewManagement:
    def test_hire_sailor(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new()
        s.captain.silver = 500
        err = s.hire_crew(3, "sailor")
        assert err is None
        assert s.captain.ship.roster.sailors == 6  # 3 starting + 3

    def test_hire_gunner(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new()
        s.captain.silver = 500
        err = s.hire_crew(1, "gunner")
        assert err is None
        assert s.captain.ship.roster.gunners == 1

    def test_hire_navigator_limit(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new()
        s.captain.silver = 500
        s.hire_crew(1, "navigator")
        err = s.hire_crew(1, "navigator")
        assert err is not None
        assert "maximum" in err.lower()

    def test_fire_crew(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new()
        s.captain.silver = 500
        s.hire_crew(2, "gunner")
        assert s.captain.ship.roster.gunners == 2
        err = s.fire_crew(1, "gunner")
        assert err is None
        assert s.captain.ship.roster.gunners == 1

    def test_fire_nonexistent_role(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new()
        err = s.fire_crew(role="surgeon")
        assert err is not None

    def test_crew_sync_after_hire(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new()
        s.captain.silver = 500
        initial_crew = s.captain.ship.crew
        s.hire_crew(2, "marine")
        assert s.captain.ship.crew == initial_crew + 2
        assert s.captain.ship.roster.marines == 2


# ---------------------------------------------------------------------------
# Save/load with roster
# ---------------------------------------------------------------------------

class TestRosterSave:
    def test_round_trip_with_roster(self, tmp_path: Path):
        world = new_game("Admiral")
        world.captain.ship.roster = CrewRoster(
            sailors=5, gunners=2, navigators=1, marines=3,
        )
        world.captain.ship.sync_crew()
        save_game(world, base_path=tmp_path)
        loaded, *_ = load_game(base_path=tmp_path)
        r = loaded.captain.ship.roster
        assert r.sailors == 5
        assert r.gunners == 2
        assert r.navigators == 1
        assert r.marines == 3
        assert loaded.captain.ship.crew == r.total

    def test_save_version_is_current(self):
        assert CURRENT_SAVE_VERSION >= 9


# ---------------------------------------------------------------------------
# Migration v8 → v9
# ---------------------------------------------------------------------------

class TestMigrationV8ToV9:
    def test_v8_gets_roster_from_crew(self):
        data = {
            "version": 8,
            "captain": {
                "fleet": [],
                "ship": {
                    "template_id": "coastal_sloop",
                    "name": "Test", "hull": 60, "hull_max": 60,
                    "cargo_capacity": 30, "speed": 8,
                    "crew": 5, "crew_max": 8,
                    "cannons": 0, "maneuver": 0.9,
                    "upgrades": [], "upgrade_slots": 2,
                },
            },
        }
        migrated = migrate_save(data)
        assert migrated["version"] == CURRENT_SAVE_VERSION
        roster = migrated["captain"]["ship"]["roster"]
        assert roster["sailors"] == 5
        assert roster["gunners"] == 0

    def test_v8_fleet_ships_get_roster(self):
        data = {
            "version": 8,
            "captain": {
                "fleet": [{
                    "ship": {
                        "template_id": "trade_brigantine",
                        "name": "Docked", "hull": 100, "hull_max": 100,
                        "cargo_capacity": 80, "speed": 6,
                        "crew": 10, "crew_max": 20,
                        "cannons": 6, "maneuver": 0.5,
                        "upgrades": [], "upgrade_slots": 4,
                    },
                    "docked_port_id": "porto_novo",
                    "cargo": [],
                }],
                "ship": {
                    "template_id": "coastal_sloop",
                    "name": "Test", "hull": 60, "hull_max": 60,
                    "cargo_capacity": 30, "speed": 8,
                    "crew": 5, "crew_max": 8,
                    "cannons": 0, "maneuver": 0.9,
                    "upgrades": [], "upgrade_slots": 2,
                },
            },
        }
        migrated = migrate_save(data)
        fleet_roster = migrated["captain"]["fleet"][0]["ship"]["roster"]
        assert fleet_roster["sailors"] == 10
