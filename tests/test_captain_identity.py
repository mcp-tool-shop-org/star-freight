"""Tests for captain identity system — proves three captains create different games.

Each captain must produce:
  - Different opening economics (silver, prices)
  - Different voyage characteristics (speed, provision burn, damage)
  - Different inspection/risk profiles
  - Proper reputation seeding
"""

import random
from pathlib import Path

from portlight.app.session import GameSession
from portlight.content.goods import GOODS
from portlight.content.world import new_game
from portlight.engine.captain_identity import (
    CAPTAIN_TEMPLATES,
    CaptainType,
    get_captain_template,
)
from portlight.engine.economy import recalculate_prices
from portlight.engine.models import ReputationState
from portlight.engine.save import world_from_dict, world_to_dict
from portlight.engine.voyage import advance_day


class TestCaptainTemplates:
    """All three captain types exist and are distinct."""

    def test_nine_types_exist(self):
        assert len(CAPTAIN_TEMPLATES) == 9  # 8 original + bounty_hunter
        assert CaptainType.MERCHANT in CAPTAIN_TEMPLATES
        assert CaptainType.SMUGGLER in CAPTAIN_TEMPLATES
        assert CaptainType.NAVIGATOR in CAPTAIN_TEMPLATES
        assert CaptainType.PRIVATEER in CAPTAIN_TEMPLATES
        assert CaptainType.CORSAIR in CAPTAIN_TEMPLATES
        assert CaptainType.SCHOLAR in CAPTAIN_TEMPLATES
        assert CaptainType.MERCHANT_PRINCE in CAPTAIN_TEMPLATES
        assert CaptainType.DOCKHAND in CAPTAIN_TEMPLATES
        assert CaptainType.BOUNTY_HUNTER in CAPTAIN_TEMPLATES

    def test_get_captain_template(self):
        t = get_captain_template(CaptainType.MERCHANT)
        assert t.name == "The Merchant"
        assert t.home_port_id == "porto_novo"

    def test_each_has_home_port(self):
        for ct, t in CAPTAIN_TEMPLATES.items():
            assert t.home_port_id, f"{ct.value} missing home_port_id"

    def test_each_has_starting_silver(self):
        for ct, t in CAPTAIN_TEMPLATES.items():
            assert t.starting_silver > 0, f"{ct.value} has no starting silver"

    def test_all_starting_ports_valid(self):
        from portlight.content.ports import PORTS
        for ct, t in CAPTAIN_TEMPLATES.items():
            assert t.home_port_id in PORTS, f"{ct.value} home port '{t.home_port_id}' not in PORTS"

    def test_templates_have_strengths_and_weaknesses(self):
        for ct in CAPTAIN_TEMPLATES:
            t = CAPTAIN_TEMPLATES[ct]
            assert len(t.strengths) >= 2
            assert len(t.weaknesses) >= 2


class TestCaptainCreation:
    """new_game() applies captain template correctly."""

    def test_merchant_starts_at_porto_novo(self):
        world = new_game(captain_type=CaptainType.MERCHANT)
        assert world.voyage.destination_id == "porto_novo"
        assert world.captain.captain_type == "merchant"

    def test_smuggler_starts_at_palm_cove(self):
        world = new_game(captain_type=CaptainType.SMUGGLER)
        assert world.voyage.destination_id == "palm_cove"
        assert world.captain.captain_type == "smuggler"

    def test_navigator_starts_at_silva_bay(self):
        world = new_game(captain_type=CaptainType.NAVIGATOR)
        assert world.voyage.destination_id == "silva_bay"
        assert world.captain.captain_type == "navigator"

    def test_starting_silver_matches_template(self):
        for ct in CAPTAIN_TEMPLATES:
            t = CAPTAIN_TEMPLATES[ct]
            world = new_game(captain_type=ct)
            assert world.captain.silver == t.starting_silver

    def test_starting_provisions_matches_template(self):
        for ct in CAPTAIN_TEMPLATES:
            t = CAPTAIN_TEMPLATES[ct]
            world = new_game(captain_type=ct)
            assert world.captain.provisions == t.starting_provisions

    def test_custom_starting_port_overrides_template(self):
        world = new_game(starting_port="al_manar", captain_type=CaptainType.SMUGGLER)
        assert world.voyage.destination_id == "al_manar"
        assert world.captain.captain_type == "smuggler"


class TestReputationSeeding:
    """Captain templates seed different reputation states."""

    def test_merchant_starts_with_trust(self):
        world = new_game(captain_type=CaptainType.MERCHANT)
        assert world.captain.standing.commercial_trust == 15

    def test_smuggler_starts_with_heat(self):
        world = new_game(captain_type=CaptainType.SMUGGLER)
        assert world.captain.standing.customs_heat["Mediterranean"] == 8

    def test_navigator_starts_with_east_indies_standing(self):
        world = new_game(captain_type=CaptainType.NAVIGATOR)
        assert world.captain.standing.regional_standing["East Indies"] == 5

    def test_merchant_med_standing(self):
        world = new_game(captain_type=CaptainType.MERCHANT)
        assert world.captain.standing.regional_standing["Mediterranean"] == 10

    def test_default_reputation_is_zeroed(self):
        """A plain ReputationState starts at zero everywhere."""
        rep = ReputationState()
        assert rep.commercial_trust == 0
        for v in rep.regional_standing.values():
            assert v == 0
        for v in rep.customs_heat.values():
            assert v == 0


class TestPricingModifiers:
    """Captain identity changes effective prices."""

    def test_merchant_gets_cheaper_buys(self):
        """Merchant buy_price_mult < 1.0 means cheaper."""
        world_m = new_game(captain_type=CaptainType.MERCHANT)
        world_n = new_game(captain_type=CaptainType.NAVIGATOR)
        port_m = world_m.ports["porto_novo"]
        port_n = world_n.ports["porto_novo"]

        # Recalculate with captain modifiers
        pricing_m = CAPTAIN_TEMPLATES[CaptainType.MERCHANT].pricing
        pricing_n = CAPTAIN_TEMPLATES[CaptainType.NAVIGATOR].pricing
        recalculate_prices(port_m, GOODS, pricing_m)
        recalculate_prices(port_n, GOODS, pricing_n)

        grain_m = next(s for s in port_m.market if s.good_id == "grain")
        grain_n = next(s for s in port_n.market if s.good_id == "grain")
        # Merchant should pay less than navigator
        assert grain_m.buy_price < grain_n.buy_price

    def test_smuggler_luxury_sell_bonus(self):
        """Smuggler gets better sell prices on luxury goods."""
        world = new_game(captain_type=CaptainType.SMUGGLER)
        port = world.ports["al_manar"]  # has spice (luxury)

        pricing_s = CAPTAIN_TEMPLATES[CaptainType.SMUGGLER].pricing
        pricing_m = CAPTAIN_TEMPLATES[CaptainType.MERCHANT].pricing

        recalculate_prices(port, GOODS, pricing_s)
        spice_smug = next(s for s in port.market if s.good_id == "spice").sell_price

        recalculate_prices(port, GOODS, pricing_m)
        spice_merc = next(s for s in port.market if s.good_id == "spice").sell_price

        # Smuggler should get better luxury sell
        assert spice_smug > spice_merc

    def test_merchant_cheaper_port_fees(self):
        """Merchant port_fee_mult < 1.0 means cheaper departures."""
        t = CAPTAIN_TEMPLATES[CaptainType.MERCHANT]
        assert t.pricing.port_fee_mult < 1.0

    def test_navigator_more_expensive_buys(self):
        """Navigator buy_price_mult > 1.0 means more expensive."""
        t = CAPTAIN_TEMPLATES[CaptainType.NAVIGATOR]
        assert t.pricing.buy_price_mult > 1.0


class TestVoyageModifiers:
    """Captain identity changes voyage behavior."""

    def test_navigator_has_speed_bonus(self):
        t = CAPTAIN_TEMPLATES[CaptainType.NAVIGATOR]
        assert t.voyage.speed_bonus > 0

    def test_navigator_lower_provision_burn(self):
        t = CAPTAIN_TEMPLATES[CaptainType.NAVIGATOR]
        assert t.voyage.provision_burn < 1.0

    def test_smuggler_lower_cargo_damage(self):
        t = CAPTAIN_TEMPLATES[CaptainType.SMUGGLER]
        assert t.voyage.cargo_damage_mult < 1.0

    def test_navigator_extra_storm_resist(self):
        t = CAPTAIN_TEMPLATES[CaptainType.NAVIGATOR]
        assert t.voyage.storm_resist_bonus > 0

    def test_navigator_arrives_faster(self):
        """Navigator's speed bonus should produce faster voyages."""
        world_nav = new_game(captain_type=CaptainType.NAVIGATOR, starting_port="silva_bay")
        world_mer = new_game(captain_type=CaptainType.MERCHANT, starting_port="silva_bay")

        # Use same seed for determinism
        world_nav.seed = 42
        world_mer.seed = 42

        # Sail to same destination (silva_bay -> porto_novo)
        from portlight.engine.voyage import depart
        depart(world_nav, "porto_novo")
        depart(world_mer, "porto_novo")

        rng_nav = random.Random(42)
        rng_mer = random.Random(42)

        nav_days = 0
        mer_days = 0
        for _ in range(30):
            advance_day(world_nav, rng_nav)
            nav_days += 1
            if world_nav.voyage.status.value == "arrived" or world_nav.voyage.status.value == "in_port":
                break

        for _ in range(30):
            advance_day(world_mer, rng_mer)
            mer_days += 1
            if world_mer.voyage.status.value == "arrived" or world_mer.voyage.status.value == "in_port":
                break

        # Navigator should arrive in fewer or equal days (speed bonus)
        assert nav_days <= mer_days


class TestInspectionProfile:
    """Captain identity changes inspection behavior."""

    def test_merchant_fewer_inspections(self):
        t = CAPTAIN_TEMPLATES[CaptainType.MERCHANT]
        assert t.inspection.inspection_chance_mult < 1.0

    def test_smuggler_more_inspections(self):
        t = CAPTAIN_TEMPLATES[CaptainType.SMUGGLER]
        assert t.inspection.inspection_chance_mult > 1.0

    def test_smuggler_has_seizure_risk(self):
        t = CAPTAIN_TEMPLATES[CaptainType.SMUGGLER]
        assert t.inspection.seizure_risk > 0

    def test_merchant_lower_fines(self):
        t = CAPTAIN_TEMPLATES[CaptainType.MERCHANT]
        assert t.inspection.fine_mult < 1.0

    def test_smuggler_higher_fines(self):
        t = CAPTAIN_TEMPLATES[CaptainType.SMUGGLER]
        assert t.inspection.fine_mult > 1.0


class TestSessionCaptainType:
    """GameSession correctly passes captain type through."""

    def test_session_new_merchant(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Hawk", captain_type="merchant")
        assert s.captain.captain_type == "merchant"
        assert s.captain_template.name == "The Merchant"

    def test_session_new_smuggler(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Shadow", captain_type="smuggler")
        assert s.captain.captain_type == "smuggler"
        assert s.current_port_id == "palm_cove"

    def test_session_new_navigator(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Charts", captain_type="navigator")
        assert s.captain.captain_type == "navigator"
        assert s.current_port_id == "silva_bay"

    def test_session_default_is_merchant(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new()
        assert s.captain.captain_type == "merchant"


class TestSaveLoadCaptainState:
    """Captain type and reputation survive save/load."""

    def test_captain_type_roundtrips(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Tester", captain_type="smuggler")
        # Reload
        s2 = GameSession(tmp_path)
        assert s2.load()
        assert s2.captain.captain_type == "smuggler"

    def test_reputation_roundtrips(self, tmp_path: Path):
        s = GameSession(tmp_path)
        s.new("Tester", captain_type="merchant")
        s.captain.standing.commercial_trust = 25
        s.captain.standing.regional_standing["East Indies"] = 15
        s.captain.standing.customs_heat["West Africa"] = 8
        s._save()

        s2 = GameSession(tmp_path)
        assert s2.load()
        assert s2.captain.standing.commercial_trust == 25
        assert s2.captain.standing.regional_standing["East Indies"] == 15
        assert s2.captain.standing.customs_heat["West Africa"] == 8

    def test_dict_roundtrip(self):
        world = new_game(captain_type=CaptainType.NAVIGATOR)
        world.captain.standing.commercial_trust = 42
        d = world_to_dict(world)
        world2, _, _board, _infra, _campaign, _narrative = world_from_dict(d)
        assert world2.captain.captain_type == "navigator"
        assert world2.captain.standing.commercial_trust == 42

    def test_legacy_save_compat(self):
        """A save without captain_type defaults to merchant."""
        d = world_to_dict(new_game())
        del d["captain"]["captain_type"]  # simulate old save
        del d["captain"]["standing"]      # simulate old save
        world, _, _board, _infra, _campaign, _narrative = world_from_dict(d)
        assert world.captain.captain_type == "merchant"
        assert world.captain.standing.commercial_trust == 0


class TestCaptainEconomicDifference:
    """Three captains produce meaningfully different opening games."""

    def test_merchant_prince_has_most_silver(self):
        silvers = {}
        for ct in CAPTAIN_TEMPLATES:
            world = new_game(captain_type=ct)
            silvers[ct] = world.captain.silver
        assert silvers[CaptainType.MERCHANT_PRINCE] == max(silvers.values())

    def test_smuggler_has_less_silver_than_merchant(self):
        """Smuggler starts with less capital than Merchant but more than Navigator."""
        silvers = {}
        for ct in CAPTAIN_TEMPLATES:
            world = new_game(captain_type=ct)
            silvers[ct] = world.captain.silver
        assert silvers[CaptainType.SMUGGLER] < silvers[CaptainType.MERCHANT]
        assert silvers[CaptainType.SMUGGLER] > silvers[CaptainType.NAVIGATOR]

    def test_different_effective_grain_prices(self):
        """Each captain sees different grain prices at the same port."""
        prices = {}
        for ct in CAPTAIN_TEMPLATES:
            world = new_game(starting_port="porto_novo", captain_type=ct)
            port = world.ports["porto_novo"]
            pricing = CAPTAIN_TEMPLATES[ct].pricing
            recalculate_prices(port, GOODS, pricing)
            prices[ct] = next(s for s in port.market if s.good_id == "grain").buy_price
        # At least two should differ
        assert len(set(prices.values())) >= 2
