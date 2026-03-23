"""Tests for the seasonal system — cycle, profiles, and engine integration."""

from portlight.content.goods import GOODS
from portlight.content.seasons import SEASONAL_PROFILES, get_seasonal_profile
from portlight.engine.models import Season, get_season
from portlight.engine.narrative import _BEATS_BY_ID


class TestSeasonCycle:
    """Season derivation from game day."""

    def test_day_1_is_spring(self):
        assert get_season(1) == Season.SPRING

    def test_day_90_is_spring(self):
        assert get_season(90) == Season.SPRING

    def test_day_91_is_summer(self):
        assert get_season(91) == Season.SUMMER

    def test_day_180_is_summer(self):
        assert get_season(180) == Season.SUMMER

    def test_day_181_is_autumn(self):
        assert get_season(181) == Season.AUTUMN

    def test_day_270_is_autumn(self):
        assert get_season(270) == Season.AUTUMN

    def test_day_271_is_winter(self):
        assert get_season(271) == Season.WINTER

    def test_day_360_is_winter(self):
        assert get_season(360) == Season.WINTER

    def test_day_361_cycles_to_spring(self):
        assert get_season(361) == Season.SPRING

    def test_day_720_cycles_to_winter(self):
        assert get_season(720) == Season.WINTER

    def test_day_721_cycles_to_spring(self):
        assert get_season(721) == Season.SPRING


class TestSeasonalProfiles:
    """All 20 region×season combinations must exist and be valid."""

    REGIONS = ["Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"]
    SEASONS = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]

    def test_all_20_profiles_defined(self):
        for region in self.REGIONS:
            for season in self.SEASONS:
                key = (region, season)
                assert key in SEASONAL_PROFILES, f"Missing profile: {key}"

    def test_no_extra_profiles(self):
        assert len(SEASONAL_PROFILES) == 20

    def test_danger_mult_reasonable(self):
        for key, profile in SEASONAL_PROFILES.items():
            assert 0.5 <= profile.danger_mult <= 2.0, (
                f"{key} danger_mult {profile.danger_mult} outside 0.5-2.0"
            )

    def test_speed_mult_reasonable(self):
        for key, profile in SEASONAL_PROFILES.items():
            assert 0.5 <= profile.speed_mult <= 1.5, (
                f"{key} speed_mult {profile.speed_mult} outside 0.5-1.5"
            )

    def test_market_effects_reference_valid_goods(self):
        for key, profile in SEASONAL_PROFILES.items():
            for gid in profile.market_effects:
                assert gid in GOODS, f"{key} references unknown good '{gid}'"

    def test_market_effects_positive(self):
        for key, profile in SEASONAL_PROFILES.items():
            for gid, mult in profile.market_effects.items():
                assert mult > 0, f"{key} has non-positive multiplier for '{gid}'"

    def test_all_profiles_have_weather_flavor(self):
        for key, profile in SEASONAL_PROFILES.items():
            assert len(profile.weather_flavor) >= 2, (
                f"{key} needs >= 2 weather_flavor entries"
            )

    def test_all_profiles_have_travel_warning(self):
        for key, profile in SEASONAL_PROFILES.items():
            assert profile.travel_warning, f"{key} missing travel_warning"


class TestSeasonalDesign:
    """Verify key gameplay design decisions are encoded correctly."""

    def test_north_atlantic_winter_is_deadly(self):
        profile = SEASONAL_PROFILES[("North Atlantic", Season.WINTER)]
        assert profile.danger_mult >= 1.5, "NA winter should be very dangerous"
        assert profile.speed_mult <= 0.8, "NA winter should slow travel"

    def test_east_indies_monsoon_is_deadly(self):
        profile = SEASONAL_PROFILES[("East Indies", Season.SUMMER)]
        assert profile.danger_mult >= 1.5, "EI monsoon should be very dangerous"
        assert profile.speed_mult <= 0.8, "EI monsoon should slow travel"

    def test_south_seas_typhoon_season(self):
        profile = SEASONAL_PROFILES[("South Seas", Season.SUMMER)]
        assert profile.danger_mult >= 1.3, "SS typhoon should increase danger"

    def test_mediterranean_autumn_grain_harvest(self):
        profile = SEASONAL_PROFILES[("Mediterranean", Season.AUTUMN)]
        assert "grain" in profile.market_effects
        assert profile.market_effects["grain"] > 1.0, "Autumn harvest should increase grain supply"

    def test_north_atlantic_winter_medicine_demand(self):
        profile = SEASONAL_PROFILES[("North Atlantic", Season.WINTER)]
        assert "medicines" in profile.market_effects
        assert profile.market_effects["medicines"] >= 1.5, "Winter should spike medicine demand"

    def test_east_indies_winter_is_best_trading(self):
        profile = SEASONAL_PROFILES[("East Indies", Season.WINTER)]
        assert profile.danger_mult <= 1.0, "EI winter should be safe"
        assert profile.speed_mult >= 1.0, "EI winter should have good speed"

    def test_north_atlantic_summer_is_best_window(self):
        profile = SEASONAL_PROFILES[("North Atlantic", Season.SUMMER)]
        assert profile.danger_mult <= 0.8, "NA summer should be safest"
        assert profile.speed_mult >= 1.1, "NA summer should be fast"


class TestGetSeasonalProfile:
    """get_seasonal_profile lookup function."""

    def test_returns_correct_profile(self):
        profile = get_seasonal_profile("Mediterranean", 1)  # Spring
        assert profile is not None
        assert profile.season == Season.SPRING
        assert profile.region == "Mediterranean"

    def test_returns_none_for_unknown_region(self):
        profile = get_seasonal_profile("Atlantis", 1)
        assert profile is None

    def test_summer_monsoon_lookup(self):
        profile = get_seasonal_profile("East Indies", 150)  # Summer
        assert profile is not None
        assert profile.danger_mult >= 1.5


class TestSeasonalNarrativeBeats:
    """Seasonal narrative beats exist."""

    SEASONAL_BEAT_IDS = [
        "first_winter", "monsoon_survivor",
        "harvest_trader", "four_seasons_captain",
    ]

    def test_all_seasonal_beats_defined(self):
        for beat_id in self.SEASONAL_BEAT_IDS:
            assert beat_id in _BEATS_BY_ID, f"Missing seasonal beat: {beat_id}"

    def test_seasonal_beats_have_text(self):
        for beat_id in self.SEASONAL_BEAT_IDS:
            beat = _BEATS_BY_ID[beat_id]
            assert beat.title, f"{beat_id} missing title"
            assert beat.text, f"{beat_id} missing text"
