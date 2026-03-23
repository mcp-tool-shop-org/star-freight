"""Seasonal profiles for every region — how weather, trade, and danger shift.

Design principles:
  - Seasons create TIMING decisions, not just flavor
  - A captain who reads the calendar trades better than one who doesn't
  - North Atlantic winter is deadly. East Indies monsoon is deadly. Plan around them.
  - Harvest/abundance seasons flood certain goods, creating buy windows
  - Scarcity seasons create sell windows at destination
  - The best captains trade counter-cyclically

360-day year cycle:
  Spring (1-90):   Calm seas, trade lanes reopen, provisions cheap
  Summer (91-180): Peak activity, monsoon in East Indies, piracy peaks
  Autumn (181-270): Harvest, storms build, prices shift
  Winter (271-360): Harsh, North Atlantic deadly, Mediterranean tightens
"""

from portlight.engine.models import Season, SeasonalProfile

# ---------------------------------------------------------------------------
# MEDITERRANEAN — mild seasons, harvest-driven
# ---------------------------------------------------------------------------

_MED_SPRING = SeasonalProfile(
    season=Season.SPRING, region="Mediterranean",
    danger_mult=0.8, speed_mult=1.1,
    market_effects={"grain": 0.8, "timber": 0.9},  # pre-harvest, stocks low
    weather_flavor=[
        "Spring winds fill the sails. The Mediterranean wakes from winter.",
        "Wildflowers bloom on the coastal hills. The sailing season has begun.",
        "Gentle swells and clear skies. The old sea is kind in spring.",
    ],
    travel_warning="Fair spring weather. Good sailing conditions.",
)

_MED_SUMMER = SeasonalProfile(
    season=Season.SUMMER, region="Mediterranean",
    danger_mult=0.9, speed_mult=1.0,
    market_effects={"spice": 1.3, "silk": 1.2},  # summer luxury demand
    weather_flavor=[
        "Hot sun on the deck. The Mediterranean shimmers like hammered bronze.",
        "Becalmed in the summer heat. The crew sweats and the sails hang limp.",
        "Warm nights. The stars are close enough to touch.",
    ],
    travel_warning="Summer heat. Watch for becalming on longer routes.",
)

_MED_AUTUMN = SeasonalProfile(
    season=Season.AUTUMN, region="Mediterranean",
    danger_mult=1.1, speed_mult=1.0,
    market_effects={"grain": 1.5, "rum": 1.3, "dyes": 1.2},  # harvest floods grain
    weather_flavor=[
        "Autumn storms gather on the horizon. The harvest fleet races home.",
        "The wind shifts. Autumn is the trader's friend and the sailor's warning.",
        "Golden light on ancient stone harbors. The season of plenty.",
    ],
    travel_warning="Autumn storms building. Grain harvest drives prices down.",
)

_MED_WINTER = SeasonalProfile(
    season=Season.WINTER, region="Mediterranean",
    danger_mult=1.3, speed_mult=0.9,
    market_effects={"grain": 0.7, "medicines": 1.4, "tea": 1.3},  # winter scarcity
    weather_flavor=[
        "Cold rain and grey seas. The Mediterranean is not kind in winter.",
        "Winter swells rock the harbor. Fewer ships venture out.",
        "Fog clings to the coast. Navigation by landmark fails.",
    ],
    travel_warning="Winter seas. Increased storm danger. Medicine demand rises.",
)

# ---------------------------------------------------------------------------
# NORTH ATLANTIC — brutal winter, short summer window
# ---------------------------------------------------------------------------

_NA_SPRING = SeasonalProfile(
    season=Season.SPRING, region="North Atlantic",
    danger_mult=1.0, speed_mult=1.0,
    market_effects={"timber": 1.3, "iron": 1.2},  # construction season begins
    weather_flavor=[
        "Ice breaks in the harbors. The north stirs back to life.",
        "The first ships of spring push through grey seas. Trade resumes.",
        "Cold but calming. The Atlantic's fury fades with the winter.",
    ],
    travel_warning="Spring thaw. Ice hazards in northern passages.",
)

_NA_SUMMER = SeasonalProfile(
    season=Season.SUMMER, region="North Atlantic",
    danger_mult=0.7, speed_mult=1.15,
    market_effects={"weapons": 1.3, "tobacco": 1.2},  # military campaigns, good sailing
    weather_flavor=[
        "The brief northern summer. Long days, calm seas, and the foundries running hot.",
        "Warm enough to work the deck without gloves. The north savors these months.",
        "Clear skies over Ironhaven. The Great Foundry chimney is visible for leagues.",
    ],
    travel_warning="Best sailing window. Take advantage of calm northern waters.",
)

_NA_AUTUMN = SeasonalProfile(
    season=Season.AUTUMN, region="North Atlantic",
    danger_mult=1.3, speed_mult=0.9,
    market_effects={"medicines": 1.5, "grain": 1.3, "tea": 1.4},  # pre-winter stockpiling
    weather_flavor=[
        "The storms return early. Captains race to complete autumn runs.",
        "Grey skies darken. The Atlantic remembers what it is.",
        "Autumn gales strip the last warmth from the air.",
    ],
    travel_warning="Autumn storms intensifying. Stock up before winter closes routes.",
)

_NA_WINTER = SeasonalProfile(
    season=Season.WINTER, region="North Atlantic",
    danger_mult=1.8, speed_mult=0.7,
    market_effects={"medicines": 2.0, "tea": 1.8, "grain": 1.5, "tobacco": 1.5},  # desperate demand
    weather_flavor=[
        "The Atlantic in winter. Walls of grey water and wind that cuts through oak.",
        "Ice forms on the rigging. The crew works with numb hands.",
        "A winter crossing is a gamble with your hull and your crew.",
    ],
    travel_warning="DANGEROUS: Winter Atlantic. 80% increased storm danger. Only attempt with brigantine or better.",
)

# ---------------------------------------------------------------------------
# WEST AFRICA — wet/dry cycle, mild seas
# ---------------------------------------------------------------------------

_WA_SPRING = SeasonalProfile(
    season=Season.SPRING, region="West Africa",
    danger_mult=0.9, speed_mult=1.05,
    market_effects={"cotton": 1.3, "dyes": 1.2},  # dry season harvest
    weather_flavor=[
        "The dry season holds. Clear skies and steady trade winds.",
        "Warm air carries the scent of red earth from the interior.",
        "The Gold Coast shimmers. Good weather for loading cotton.",
    ],
    travel_warning="Dry season. Excellent coastal sailing.",
)

_WA_SUMMER = SeasonalProfile(
    season=Season.SUMMER, region="West Africa",
    danger_mult=1.2, speed_mult=0.9,
    market_effects={"rum": 1.4, "pearls": 1.3},  # rainy season begins, pearl diving peaks
    weather_flavor=[
        "The rains come. Warm downpours that last hours, then blazing sun.",
        "Rivers flood and the coast turns green. Trade slows but the divers thrive.",
        "Humidity thick enough to drink. The crew strips to the waist.",
    ],
    travel_warning="Rainy season beginning. Coastal visibility reduced.",
)

_WA_AUTUMN = SeasonalProfile(
    season=Season.AUTUMN, region="West Africa",
    danger_mult=1.0, speed_mult=1.0,
    market_effects={"cotton": 1.4, "dyes": 1.5, "pearls": 1.2},  # second harvest
    weather_flavor=[
        "The rains ease. The second cotton harvest fills the warehouses.",
        "Cool evenings and warm days. The best time to trade on the Gold Coast.",
        "Market day energy. The coast is alive with commerce.",
    ],
    travel_warning="Post-rains. Good trading season.",
)

_WA_WINTER = SeasonalProfile(
    season=Season.WINTER, region="West Africa",
    danger_mult=0.85, speed_mult=1.1,
    market_effects={"iron": 1.3, "weapons": 1.2},  # dry season, mining ramps up
    weather_flavor=[
        "Dry harmattan wind from the interior. Visibility drops but seas are calm.",
        "Cool, dusty air. The mines work double shifts in the dry season.",
        "Stars blaze overhead in the clear winter sky. Navigation is easy.",
    ],
    travel_warning="Dry harmattan season. Calm seas, dusty air.",
)

# ---------------------------------------------------------------------------
# EAST INDIES — monsoon-dominated, extreme seasonal swing
# ---------------------------------------------------------------------------

_EI_SPRING = SeasonalProfile(
    season=Season.SPRING, region="East Indies",
    danger_mult=0.9, speed_mult=1.1,
    market_effects={"silk": 1.2, "porcelain": 1.2, "tea": 1.3},  # production ramps up
    weather_flavor=[
        "The monsoon retreats. Calm waters return to the archipelago.",
        "Kiln fires restart in Jade Port. The silk looms in Silk Haven resume.",
        "Incense drifts across still water. The East Indies breathe again.",
    ],
    travel_warning="Post-monsoon calm. Excellent trading window.",
)

_EI_SUMMER = SeasonalProfile(
    season=Season.SUMMER, region="East Indies",
    danger_mult=1.7, speed_mult=0.75,
    market_effects={"spice": 1.8, "medicines": 1.5, "silk": 0.7},  # monsoon: spice demand surges, silk production drops
    weather_flavor=[
        "The monsoon strikes. Walls of rain and wind that last for days.",
        "The sea churns brown with river mud. Ships shelter in harbor or drown.",
        "Thunder rolls across the archipelago. The monsoon is merciless.",
    ],
    travel_warning="MONSOON SEASON: 70% increased danger. Routes through East Indies are extremely hazardous.",
)

_EI_AUTUMN = SeasonalProfile(
    season=Season.AUTUMN, region="East Indies",
    danger_mult=1.1, speed_mult=1.0,
    market_effects={"spice": 1.5, "tea": 1.4, "porcelain": 1.3},  # post-monsoon spice harvest
    weather_flavor=[
        "The monsoon fades. Spice harvests begin across the archipelago.",
        "Ships emerge from shelter. The race to fill holds with fresh spice begins.",
        "Autumn in the East — the best spice, the freshest tea, the finest porcelain.",
    ],
    travel_warning="Post-monsoon. Spice harvest drives prices. Good trading window.",
)

_EI_WINTER = SeasonalProfile(
    season=Season.WINTER, region="East Indies",
    danger_mult=0.8, speed_mult=1.1,
    market_effects={"silk": 1.4, "porcelain": 1.3, "tea": 1.2},  # dry season production peak
    weather_flavor=[
        "Dry season. The kilns burn bright and the looms never stop.",
        "Cool air from the mountains. The best silk is woven in winter.",
        "Clear skies over the archipelago. Navigation is easy, trade is brisk.",
    ],
    travel_warning="Dry season. Peak production of silk and porcelain.",
)

# ---------------------------------------------------------------------------
# SOUTH SEAS — typhoon season, volcanic unpredictability
# ---------------------------------------------------------------------------

_SS_SPRING = SeasonalProfile(
    season=Season.SPRING, region="South Seas",
    danger_mult=0.9, speed_mult=1.05,
    market_effects={"pearls": 1.3, "medicines": 1.2},  # diving season begins
    weather_flavor=[
        "Calm lagoons. The pearl divers return to the reef.",
        "Warm water, clear skies. The South Seas at their most inviting.",
        "Flying fish skip across the bow. The reef glows beneath clear water.",
    ],
    travel_warning="Good season. Pearl diving begins.",
)

_SS_SUMMER = SeasonalProfile(
    season=Season.SUMMER, region="South Seas",
    danger_mult=1.5, speed_mult=0.85,
    market_effects={"weapons": 1.5, "timber": 1.3},  # typhoon season, fortress repair demand
    weather_flavor=[
        "Typhoon season. The sky darkens without warning.",
        "A wall of black cloud on the horizon. The crew prays to whatever gods they carry.",
        "Rain so heavy it stings the skin. The South Seas remind you who rules here.",
    ],
    travel_warning="TYPHOON SEASON: 50% increased danger. The Coral King's waters are treacherous.",
)

_SS_AUTUMN = SeasonalProfile(
    season=Season.AUTUMN, region="South Seas",
    danger_mult=1.1, speed_mult=1.0,
    market_effects={"pearls": 1.5, "medicines": 1.4, "dyes": 1.3},  # peak harvest
    weather_flavor=[
        "The typhoons pass. The reef reveals its treasures to the patient.",
        "Volcanic soil yields its bounty. Medicine plants and dye pigments abound.",
        "Warm rain and warm sun. The islands exhale after the storms.",
    ],
    travel_warning="Post-typhoon. Peak pearl and medicine harvest.",
)

_SS_WINTER = SeasonalProfile(
    season=Season.WINTER, region="South Seas",
    danger_mult=0.85, speed_mult=1.1,
    market_effects={"pearls": 1.2, "tobacco": 1.3, "rum": 1.2},  # calm season, social trade
    weather_flavor=[
        "The gentlest season. Warm, calm, and full of stars.",
        "The Coral King holds court in winter. Tribute flows. Favor is earned.",
        "Still lagoons and soft winds. The South Seas forgive everything in winter.",
    ],
    travel_warning="Calm season. Best window for South Seas trade.",
)


# ---------------------------------------------------------------------------
# Lookup table: (region, season) -> SeasonalProfile
# ---------------------------------------------------------------------------

SEASONAL_PROFILES: dict[tuple[str, Season], SeasonalProfile] = {}

for _profile in [
    # Mediterranean
    _MED_SPRING, _MED_SUMMER, _MED_AUTUMN, _MED_WINTER,
    # North Atlantic
    _NA_SPRING, _NA_SUMMER, _NA_AUTUMN, _NA_WINTER,
    # West Africa
    _WA_SPRING, _WA_SUMMER, _WA_AUTUMN, _WA_WINTER,
    # East Indies
    _EI_SPRING, _EI_SUMMER, _EI_AUTUMN, _EI_WINTER,
    # South Seas
    _SS_SPRING, _SS_SUMMER, _SS_AUTUMN, _SS_WINTER,
]:
    SEASONAL_PROFILES[(_profile.region, _profile.season)] = _profile


def get_seasonal_profile(region: str, day: int) -> SeasonalProfile | None:
    """Get the seasonal profile for a region on a given day."""
    from portlight.engine.models import get_season
    season = get_season(day)
    return SEASONAL_PROFILES.get((region, season))
