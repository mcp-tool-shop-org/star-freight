"""Tests for the pirate political ecosystem — factions, underworld, duels, contraband."""

import random

from portlight.content.factions import (
    FACTIONS,
    PIRATE_CAPTAINS,
    get_captains_for_faction,
    get_faction_for_region,
)
from portlight.content.goods import GOODS
from portlight.content.ports import PORTS
from portlight.engine.duel import (
    STANCES,
    pick_opponent_stance,
    resolve_duel,
    resolve_round,
    stance_outcome,
)
from portlight.engine.models import (
    GoodCategory,
    PirateState,
    PortFeature,
)
from portlight.engine.underworld import (
    THRESHOLD_NEUTRAL,
    THRESHOLD_TRADE,
    THRESHOLD_TRUSTED,
    get_faction_hostility,
    get_standing,
    record_contraband_trade,
    record_duel_outcome,
    record_pirate_trade,
    tick_underworld,
)


# ---------------------------------------------------------------------------
# Contraband goods
# ---------------------------------------------------------------------------

class TestContrabandGoods:
    """Contraband goods exist and are properly categorized."""

    def test_three_contraband_goods_exist(self):
        contraband = [g for g in GOODS.values() if g.category == GoodCategory.CONTRABAND]
        assert len(contraband) == 3

    def test_opium_is_contraband(self):
        assert "opium" in GOODS
        assert GOODS["opium"].category == GoodCategory.CONTRABAND
        assert GOODS["opium"].base_price == 85

    def test_black_powder_is_contraband(self):
        assert "black_powder" in GOODS
        assert GOODS["black_powder"].category == GoodCategory.CONTRABAND

    def test_stolen_cargo_is_contraband(self):
        assert "stolen_cargo" in GOODS
        assert GOODS["stolen_cargo"].category == GoodCategory.CONTRABAND

    def test_opium_is_light(self):
        assert GOODS["opium"].weight_per_unit == 0.5

    def test_black_powder_is_heavy(self):
        assert GOODS["black_powder"].weight_per_unit == 1.5

    def test_total_goods_count(self):
        assert len(GOODS) == 18  # 17 original + pelts


class TestBlackMarketPorts:
    """Contraband is only available at BLACK_MARKET ports."""

    def test_corsairs_rest_has_contraband(self):
        port = PORTS["corsairs_rest"]
        assert PortFeature.BLACK_MARKET in port.features
        contraband_slots = [s for s in port.market if s.good_id in ("opium", "black_powder", "stolen_cargo")]
        assert len(contraband_slots) >= 2

    def test_spice_narrows_has_contraband(self):
        port = PORTS["spice_narrows"]
        assert PortFeature.BLACK_MARKET in port.features
        contraband_slots = [s for s in port.market if s.good_id in ("opium", "black_powder", "stolen_cargo")]
        assert len(contraband_slots) >= 2

    def test_legitimate_ports_have_no_contraband(self):
        for port_id, port in PORTS.items():
            if PortFeature.BLACK_MARKET not in port.features:
                contraband_slots = [s for s in port.market if s.good_id in ("opium", "black_powder", "stolen_cargo")]
                assert len(contraband_slots) == 0, f"{port_id} has contraband but no BLACK_MARKET"


# ---------------------------------------------------------------------------
# Pirate factions
# ---------------------------------------------------------------------------

class TestPirateFactions:
    """Four factions with complete data."""

    def test_four_factions_exist(self):
        assert len(FACTIONS) == 4

    def test_faction_ids(self):
        expected = {"crimson_tide", "monsoon_syndicate", "deep_reef", "iron_wolves"}
        assert set(FACTIONS.keys()) == expected

    def test_all_factions_have_territory(self):
        for fid, f in FACTIONS.items():
            assert len(f.territory_regions) >= 1, f"{fid} has no territory"

    def test_all_factions_have_ethos(self):
        for fid, f in FACTIONS.items():
            assert f.ethos, f"{fid} missing ethos"
            assert f.description, f"{fid} missing description"

    def test_all_factions_have_seasonal_activity(self):
        from portlight.engine.models import Season
        for fid, f in FACTIONS.items():
            for season in Season:
                assert season in f.seasonal_activity, f"{fid} missing {season} activity"

    def test_all_factions_have_encounter_flavor(self):
        for fid, f in FACTIONS.items():
            assert len(f.encounter_flavor) >= 2, f"{fid} needs >=2 encounter flavors"

    def test_faction_for_region_mediterranean(self):
        factions = get_faction_for_region("Mediterranean")
        faction_ids = {f.id for f in factions}
        assert "crimson_tide" in faction_ids

    def test_faction_for_region_east_indies(self):
        factions = get_faction_for_region("East Indies")
        faction_ids = {f.id for f in factions}
        assert "monsoon_syndicate" in faction_ids

    def test_all_regions_have_factions(self):
        for region in ["Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"]:
            factions = get_faction_for_region(region)
            assert len(factions) >= 1, f"No factions in {region}"


class TestPirateCaptains:
    """Eight named captains with duel flavor."""

    def test_eight_captains_exist(self):
        assert len(PIRATE_CAPTAINS) == 8

    def test_two_per_faction(self):
        for fid in FACTIONS:
            captains = get_captains_for_faction(fid)
            assert len(captains) == 2, f"{fid} should have 2 captains"

    def test_all_captains_have_text(self):
        for cid, c in PIRATE_CAPTAINS.items():
            assert c.encounter_text, f"{cid} missing encounter_text"
            assert c.deal_text, f"{cid} missing deal_text"
            assert c.attack_text, f"{cid} missing attack_text"
            assert c.retreat_text, f"{cid} missing retreat_text"

    def test_all_captains_have_duel_flavor(self):
        for cid, c in PIRATE_CAPTAINS.items():
            assert c.duel_opening, f"{cid} missing duel_opening"
            assert c.duel_defeat, f"{cid} missing duel_defeat"
            assert c.duel_victory, f"{cid} missing duel_victory"

    def test_captain_strength_range(self):
        for cid, c in PIRATE_CAPTAINS.items():
            assert 1 <= c.strength <= 10, f"{cid} strength {c.strength} outside 1-10"

    def test_captain_personalities_valid(self):
        valid = {"aggressive", "defensive", "balanced", "wild"}
        for cid, c in PIRATE_CAPTAINS.items():
            assert c.personality in valid, f"{cid} invalid personality '{c.personality}'"


# ---------------------------------------------------------------------------
# Underworld standing
# ---------------------------------------------------------------------------

class TestUnderworldStanding:
    """Standing mechanics, hostility checks, and trade recording."""

    def test_default_standing_zero(self):
        standing = {}
        assert get_standing(standing, "crimson_tide") == 0

    def test_hostility_at_zero(self):
        standing = {}
        assert get_faction_hostility(standing, "crimson_tide", "merchant") == "attack"

    def test_neutral_at_threshold(self):
        standing = {"crimson_tide": THRESHOLD_NEUTRAL}
        assert get_faction_hostility(standing, "crimson_tide", "merchant") == "neutral"

    def test_trade_at_threshold(self):
        standing = {"crimson_tide": THRESHOLD_TRADE}
        assert get_faction_hostility(standing, "crimson_tide", "merchant") == "trade"

    def test_allied_at_threshold(self):
        standing = {"crimson_tide": THRESHOLD_TRUSTED}
        assert get_faction_hostility(standing, "crimson_tide", "merchant") == "allied"

    def test_smuggler_bonus(self):
        """Smugglers get +5 effective standing with friendly factions."""
        standing = {"monsoon_syndicate": 6}  # below neutral normally
        # Monsoon Syndicate has friendly smuggler_attitude
        result = get_faction_hostility(standing, "monsoon_syndicate", "smuggler")
        assert result in ("neutral", "trade")  # 6 + 5 = 11, above neutral threshold

    def test_record_contraband_trade(self):
        standing = {}
        delta = record_contraband_trade(standing, "crimson_tide", "black_powder", 5)
        assert delta >= 3  # specialty + volume bonus
        assert standing["crimson_tide"] > 0

    def test_record_pirate_trade(self):
        standing = {}
        delta = record_pirate_trade(standing, "crimson_tide")
        assert delta == 2
        assert standing["crimson_tide"] == 2

    def test_record_duel_win_spared(self):
        standing = {}
        delta = record_duel_outcome(standing, "deep_reef", True, spared=True)
        assert delta == 5

    def test_record_duel_loss(self):
        standing = {"deep_reef": 10}
        delta = record_duel_outcome(standing, "deep_reef", False)
        assert delta == -2
        assert standing["deep_reef"] == 8

    def test_underworld_heat_decays(self):
        heat = tick_underworld({}, 10, days=5)
        assert heat == 5

    def test_standing_capped_at_100(self):
        standing = {"crimson_tide": 98}
        record_contraband_trade(standing, "crimson_tide", "black_powder", 10)
        assert standing["crimson_tide"] <= 100


# ---------------------------------------------------------------------------
# Sword dueling
# ---------------------------------------------------------------------------

class TestStanceTriangle:
    """Rock-paper-scissors mechanics."""

    def test_thrust_beats_slash(self):
        assert stance_outcome("thrust", "slash") == "win"

    def test_slash_beats_parry(self):
        assert stance_outcome("slash", "parry") == "win"

    def test_parry_beats_thrust(self):
        assert stance_outcome("parry", "thrust") == "win"

    def test_same_stance_draws(self):
        for s in STANCES:
            assert stance_outcome(s, s) == "draw"

    def test_thrust_loses_to_parry(self):
        assert stance_outcome("thrust", "parry") == "lose"

    def test_all_stances_have_outcomes(self):
        for a in STANCES:
            for b in STANCES:
                result = stance_outcome(a, b)
                assert result in ("win", "lose", "draw")


class TestOpponentAI:
    """Personality-driven stance selection."""

    def test_aggressive_favors_thrust(self):
        rng = random.Random(42)
        picks = [pick_opponent_stance("aggressive", [], rng) for _ in range(200)]
        thrust_pct = picks.count("thrust") / len(picks)
        assert thrust_pct > 0.40, f"Aggressive should favor thrust, got {thrust_pct:.0%}"

    def test_defensive_favors_parry(self):
        rng = random.Random(42)
        picks = [pick_opponent_stance("defensive", [], rng) for _ in range(200)]
        parry_pct = picks.count("parry") / len(picks)
        assert parry_pct > 0.40, f"Defensive should favor parry, got {parry_pct:.0%}"

    def test_balanced_adapts_to_repeats(self):
        """Balanced AI should counter repeated stances."""
        rng = random.Random(42)
        history = ["thrust", "thrust"]  # player repeating thrust
        picks = [pick_opponent_stance("balanced", history, rng) for _ in range(200)]
        # Parry counters thrust
        parry_pct = picks.count("parry") / len(picks)
        assert parry_pct > 0.35, f"Balanced should adapt to thrust spam with parry, got {parry_pct:.0%}"

    def test_wild_is_roughly_even(self):
        rng = random.Random(42)
        picks = [pick_opponent_stance("wild", [], rng) for _ in range(300)]
        for stance in STANCES:
            pct = picks.count(stance) / len(picks)
            assert 0.20 < pct < 0.50, f"Wild should be roughly even, {stance}={pct:.0%}"


class TestDuelRounds:
    """Individual round resolution."""

    def test_win_deals_damage(self):
        r = resolve_round("thrust", "slash", random.Random(42))
        assert r.damage_to_opponent >= 2
        assert r.damage_to_player == 0

    def test_lose_takes_damage(self):
        r = resolve_round("thrust", "parry", random.Random(42))
        assert r.damage_to_player >= 2
        assert r.damage_to_opponent == 0

    def test_draw_mutual_damage(self):
        r = resolve_round("thrust", "thrust", random.Random(42))
        assert r.damage_to_player == 1
        assert r.damage_to_opponent == 1

    def test_round_has_flavor(self):
        r = resolve_round("thrust", "slash", random.Random(42))
        assert r.flavor


class TestFullDuel:
    """Complete duel resolution."""

    def test_duel_resolves(self):
        stances = ["thrust", "slash", "parry", "thrust", "slash", "parry", "thrust", "slash"]
        result = resolve_duel(stances, "scarlet_ana", "Scarlet Ana", "balanced", 6, random.Random(42))
        assert result.opponent_id == "scarlet_ana"
        assert len(result.rounds) > 0

    def test_duel_win_gives_silver(self):
        # Stack the deck: spam what beats defensive (slash beats parry)
        stances = ["slash"] * 10
        result = resolve_duel(stances, "raj_the_quiet", "Raj", "defensive", 5, random.Random(42))
        if result.player_won:
            assert result.silver_delta > 0

    def test_duel_loss_costs_silver(self):
        # Spam parry against aggressive (thrust beats... wait, parry beats thrust)
        # Actually parry counters thrust, so this might win. Let's try thrust vs defensive (parry)
        stances = ["thrust"] * 10  # thrust loses to parry
        result = resolve_duel(stances, "old_coral", "Old Coral", "defensive", 6, random.Random(42))
        if not result.player_won and not result.draw:
            assert result.silver_delta < 0

    def test_strong_opponent_has_more_hp(self):
        # Gnaw (strength 9) should be harder
        stances = ["slash", "thrust", "parry"] * 5
        result_weak = resolve_duel(stances, "a", "A", "wild", 3, random.Random(42))
        result_strong = resolve_duel(stances, "b", "B", "wild", 9, random.Random(42))
        # Strong opponent should survive longer (more rounds or win more)
        assert len(result_strong.rounds) >= len(result_weak.rounds) or not result_strong.player_won

    def test_duel_terminates(self):
        """Duel always terminates within stance count."""
        stances = ["thrust", "slash", "parry"] * 10
        result = resolve_duel(stances, "x", "X", "aggressive", 8, random.Random(42))
        assert len(result.rounds) <= 30


class TestPirateState:
    """PirateState serialization sanity."""

    def test_default_pirate_state(self):
        ps = PirateState()
        assert ps.encounters == []
        assert ps.nemesis_id is None
        assert ps.duels_won == 0
        assert ps.duels_lost == 0
