"""Cultural identity for every region and port in the Known World.

Static reference data — looked up by region name or port_id at runtime.
Not serialized in save files (culture doesn't change, only the player's
engagement with it does, tracked in CulturalState).

Design principle: every line should make the player feel something.
The CLI is text-only — words are the graphics engine.
"""

from portlight.engine.models import Festival, PortCulture, RegionCulture

# ---------------------------------------------------------------------------
# Festivals
# ---------------------------------------------------------------------------

_MED_FESTIVALS = [
    Festival(
        id="harvest_of_plenty",
        name="Harvest of Plenty",
        description=(
            "The granaries open and the Exchange rings its great bell. "
            "For three days, grain flows freely and merchants feast in the columned halls."
        ),
        region="Mediterranean",
        frequency_days=60,
        market_effects={"grain": 1.8, "rum": 1.4},
        duration_days=3,
        standing_bonus=2,
    ),
    Festival(
        id="night_of_lanterns",
        name="Night of Lanterns",
        description=(
            "Paper lanterns drift on the harbor. The spice merchants display their "
            "rarest blends and the air thickens with cinnamon and clove."
        ),
        region="Mediterranean",
        frequency_days=90,
        market_effects={"spice": 2.0, "silk": 1.5, "dyes": 1.6},
        duration_days=3,
        standing_bonus=1,
    ),
]

_NA_FESTIVALS = [
    Festival(
        id="iron_days",
        name="The Iron Days",
        description=(
            "The foundries run day and night. Sparks light the harbor like fireflies. "
            "Ironhaven celebrates its smiths with contests of craft and endurance."
        ),
        region="North Atlantic",
        frequency_days=75,
        market_effects={"iron": 1.6, "weapons": 1.8, "timber": 1.3},
        duration_days=4,
        standing_bonus=2,
    ),
    Festival(
        id="midwinter_market",
        name="Midwinter Market",
        description=(
            "The northern ports huddle against the cold. Medicine sellers, tea blenders, "
            "and tobacco merchants crowd the covered bazaars."
        ),
        region="North Atlantic",
        frequency_days=90,
        market_effects={"medicines": 2.0, "tea": 1.7, "tobacco": 1.5},
        duration_days=3,
        standing_bonus=1,
    ),
]

_WA_FESTIVALS = [
    Festival(
        id="dyers_moon",
        name="Dyer's Moon",
        description=(
            "Under the full moon, the dye vats are blessed and new colors are revealed. "
            "Textile merchants from every port crowd the stalls, bidding for the freshest pigments."
        ),
        region="West Africa",
        frequency_days=60,
        market_effects={"dyes": 2.0, "cotton": 1.6},
        duration_days=3,
        standing_bonus=2,
    ),
    Festival(
        id="pearl_tide",
        name="Pearl Tide",
        description=(
            "The divers return from the deep shallows with the season's haul. "
            "Pearls are weighed, blessed by the elders, and offered first to those "
            "who have traded fairly with the coast."
        ),
        region="West Africa",
        frequency_days=90,
        market_effects={"pearls": 2.2, "rum": 1.3},
        duration_days=4,
        standing_bonus=3,
    ),
]

_EI_FESTIVALS = [
    Festival(
        id="silk_weavers_fair",
        name="Silk Weavers' Fair",
        description=(
            "The master weavers display their finest work. Bolts of silk in patterns "
            "a thousand years old hang from bamboo frames along the waterfront. "
            "Buyers come from every port in the East."
        ),
        region="East Indies",
        frequency_days=75,
        market_effects={"silk": 2.0, "porcelain": 1.5, "dyes": 1.4},
        duration_days=4,
        standing_bonus=2,
    ),
    Festival(
        id="monsoon_prayer",
        name="Monsoon Prayer",
        description=(
            "Incense burns on every pier. The captains pray for safe passage through "
            "the season of storms. Spice cargoes are blessed and the shipwrights "
            "inspect every hull."
        ),
        region="East Indies",
        frequency_days=90,
        market_effects={"spice": 1.8, "medicines": 1.6, "tea": 1.4},
        duration_days=3,
        standing_bonus=1,
    ),
]

_SS_FESTIVALS = [
    Festival(
        id="coral_coronation",
        name="Coral Coronation",
        description=(
            "The Coral King renews his oath to the sea. Tribute is expected — "
            "weapons, silk, and pearls are presented at the reef throne. "
            "Those who give generously earn the kingdom's favor."
        ),
        region="South Seas",
        frequency_days=90,
        market_effects={"weapons": 2.5, "silk": 2.0, "pearls": 1.8},
        duration_days=5,
        standing_bonus=4,
    ),
    Festival(
        id="fire_walking",
        name="Fire Walking",
        description=(
            "Ember Isle's volcanic heart rumbles and the island celebrates with "
            "firewalking ceremonies. Medicine plants are harvested from the hot springs "
            "and dye pigments are drawn from volcanic earth."
        ),
        region="South Seas",
        frequency_days=75,
        market_effects={"medicines": 2.0, "dyes": 1.8},
        duration_days=3,
        standing_bonus=2,
    ),
]


# ---------------------------------------------------------------------------
# Regional Cultures
# ---------------------------------------------------------------------------

REGION_CULTURES: dict[str, RegionCulture] = {rc.region_name: rc for rc in [
    RegionCulture(
        id="mediterranean",
        region_name="Mediterranean",
        cultural_name="The Middle Sea",
        ethos=(
            "Civilization is commerce. The law of contract binds harder than iron, "
            "and a merchant's word, once given, is recorded in stone."
        ),
        trade_philosophy=(
            "Fair dealing above all. Prices are posted, weights are checked, "
            "and the Exchange arbitrates every dispute. Cheats are remembered."
        ),
        sacred_goods=["grain"],
        forbidden_goods=[],
        prized_goods=["spice", "silk"],
        greeting="Welcome to port, Captain. Your cargo manifest, if you please.",
        farewell="Fair winds and full holds. May your ledger balance.",
        proverb="A contract honored is worth more than gold hoarded.",
        festivals=_MED_FESTIVALS,
        weather_flavor=[
            "The sea is calm and blue. Sunlight dances on ancient waters.",
            "A warm breeze carries the smell of olive groves from the coast.",
            "Gulls wheel above the mast. The Mediterranean is kind today.",
            "Haze on the horizon. The old sea holds its secrets close.",
            "A gentle swell. These are the waters where trade was born.",
        ],
    ),

    RegionCulture(
        id="north_atlantic",
        region_name="North Atlantic",
        cultural_name="The Iron Coast",
        ethos=(
            "Strength is built, not born. The forge, the hull, the garrison — "
            "everything here is made to endure. Softness is a southern luxury."
        ),
        trade_philosophy=(
            "Trade is provision, not pleasure. The north needs what it needs: "
            "grain to eat, timber to build, medicine to survive. Luxuries are welcome "
            "but never essential."
        ),
        sacred_goods=["medicines"],
        forbidden_goods=[],
        prized_goods=["tea", "tobacco", "weapons"],
        greeting="State your business, Captain. These waters have little patience.",
        farewell="Keep your hull tight. The Atlantic forgives nothing.",
        proverb="The storm tests the hull, not the cargo.",
        festivals=_NA_FESTIVALS,
        weather_flavor=[
            "Grey skies press low. The Atlantic rolls in long, heavy swells.",
            "Wind bites through the rigging. Crew members pull their collars tight.",
            "Cold spray over the bow. The northern sea earns its reputation.",
            "Fog banks drift across the water like slow ghosts.",
            "A break in the clouds. Pale northern light falls on dark water.",
        ],
    ),

    RegionCulture(
        id="west_africa",
        region_name="West Africa",
        cultural_name="The Gold Coast",
        ethos=(
            "The land gives freely to those who give back. Trade is a relationship, "
            "not a transaction. The elders remember every ship that entered the harbor."
        ),
        trade_philosophy=(
            "Generosity first, then business. The first trade is always small — "
            "a gift, really. Trust is built in rum shared, not contracts signed. "
            "Return again and again, and the coast opens its treasure."
        ),
        sacred_goods=["pearls"],
        forbidden_goods=[],
        prized_goods=["dyes", "cotton", "rum"],
        greeting="You return! The coast remembers you, Captain.",
        farewell="Go well. The sea carries our memory of you.",
        proverb="The market remembers who gave, not who took.",
        festivals=_WA_FESTIVALS,
        weather_flavor=[
            "Warm air, heavy with moisture. The coast shimmers in the heat.",
            "Tropical rain drums on the deck and passes as quickly as it came.",
            "The sea is flat and green. Palm-fringed shores line the horizon.",
            "Hot wind from the interior carries the scent of red earth.",
            "Sunset turns the water gold. The Gold Coast earns its name tonight.",
        ],
    ),

    RegionCulture(
        id="east_indies",
        region_name="East Indies",
        cultural_name="The Silk Waters",
        ethos=(
            "Patience is mastery. The artisan who perfects one bolt of silk in a "
            "lifetime is honored above the merchant who trades a thousand. "
            "Everything here was old when your civilization was young."
        ),
        trade_philosophy=(
            "Hierarchy governs all. Know who you trade with and how to address them. "
            "Offer quality, never quantity. A single perfect porcelain bowl is worth "
            "more than a crate of adequate ones."
        ),
        sacred_goods=["porcelain", "silk"],
        forbidden_goods=["weapons"],
        prized_goods=["spice", "tea"],
        greeting="You honor us, Captain. Tea will be prepared while we discuss terms.",
        farewell="May your passage be swift and your cargo worthy.",
        proverb="A merchant who rushes drinks salt water.",
        festivals=_EI_FESTIVALS,
        weather_flavor=[
            "Incense drifts from a passing junk. The air is thick with spice.",
            "Jade-green water and islands like scattered emeralds on the horizon.",
            "Monsoon clouds build to the south. The wind carries distant rain.",
            "Sampans and fishing boats crowd the shallows. Commerce never sleeps here.",
            "Dawn mist on the archipelago. A thousand islands hide in the haze.",
        ],
    ),

    RegionCulture(
        id="south_seas",
        region_name="South Seas",
        cultural_name="The Reef Kingdoms",
        ethos=(
            "The sea gives life and the sea takes it back. The island kings answer "
            "to no empire. Trade here is tribute — offered willingly or not at all. "
            "Respect the reef, or it will tear your hull apart."
        ),
        trade_philosophy=(
            "Bring what we cannot make. Weapons, silk, porcelain — these are the "
            "currencies of respect. In return, we offer what no one else can: "
            "pearls from waters only our divers know, and medicines from plants "
            "that grow nowhere else on earth."
        ),
        sacred_goods=["pearls"],
        forbidden_goods=[],
        prized_goods=["weapons", "silk", "tea"],
        greeting="The Coral King permits you to anchor. State your tribute.",
        farewell="The reef remembers your passage. Return only if you mean to trade.",
        proverb="The reef welcomes the patient; it drowns the greedy.",
        festivals=_SS_FESTIVALS,
        weather_flavor=[
            "Turquoise water so clear you can see the reef below. Beautiful and deadly.",
            "Volcanic haze drifts from Ember Isle. The air tastes of sulfur.",
            "A sudden squall — warm rain and lightning, gone in minutes.",
            "Flying fish skip across the bow. The South Seas teem with life.",
            "Stars reflected in still water. The reef glows faintly beneath the surface.",
        ],
    ),
]}


# ---------------------------------------------------------------------------
# Port Cultures (20 ports, one entry per port)
# ---------------------------------------------------------------------------

PORT_CULTURES: dict[str, PortCulture] = {pc.port_id: pc for pc in [
    # === MEDITERRANEAN ===
    PortCulture(
        port_id="porto_novo",
        landmark="The Grain Exchange — a columned hall where prices are read aloud at dawn.",
        local_custom="Captains ring the harbor bell on first arrival. It's bad luck not to.",
        atmosphere="Flour dust, sea salt, and the shouts of dockhands loading grain barges.",
        dock_scene=(
            "Grain barges jostle for position along the stone quays. Clerks with wax "
            "tablets tally every bushel while porters sweat under heavy sacks."
        ),
        tavern_rumor=(
            "They say the Grain Exchange is built on the ruins of an older temple. "
            "Some nights the clerks hear chanting from beneath the floor."
        ),
        cultural_group="The Exchange Guild",
        cultural_group_description="Keepers of the price — they set the dawn rates and arbitrate disputes.",
    ),
    PortCulture(
        port_id="al_manar",
        landmark="The Spice Bazaar — a covered market where a hundred aromas compete for your attention.",
        local_custom="Bargaining begins with tea. Refusing the first cup insults the seller.",
        atmosphere="Cinnamon, cardamom, and the murmur of a hundred negotiations conducted in whispers.",
        dock_scene=(
            "Feluccas with triangular sails crowd the harbor. Porters carry brass-bound "
            "chests of spice up marble steps worn smooth by centuries of trade."
        ),
        tavern_rumor=(
            "A merchant from the east claims to know a spice island no chart has ever shown. "
            "He's been buying a lot of rum and saying little else."
        ),
        cultural_group="The Spice Merchants' Circle",
        cultural_group_description="An ancient guild that controls the spice auctions and guards trade secrets.",
    ),
    PortCulture(
        port_id="silva_bay",
        landmark="The Master Shipyard — where the finest hulls in the Mediterranean take shape.",
        local_custom="Touching another captain's ship without permission is grounds for a duel.",
        atmosphere="Fresh-cut timber, hot pitch, and the rhythmic sound of adzes shaping keels.",
        dock_scene=(
            "Sawdust drifts like snow across the waterfront. Half-finished hulls rise "
            "on slipways, their ribs exposed like the skeletons of great fish."
        ),
        tavern_rumor=(
            "The master shipwright refuses to build for anyone who has lost a ship to storms. "
            "She says it's bad wood-luck."
        ),
        cultural_group="The Shipwrights' Brotherhood",
        cultural_group_description="Master builders who guard their hull designs like state secrets.",
    ),
    PortCulture(
        port_id="corsairs_rest",
        landmark="The Cliff Tavern — carved into the rock face, visible only from the sea.",
        local_custom="No names. Every captain here is 'friend' until proven otherwise.",
        atmosphere="Torch smoke, cheap rum, and the clink of coins changing hands under the table.",
        dock_scene=(
            "Ships anchor in the hidden cove with no flags flying. A boy in a rowboat "
            "approaches to collect the docking fee — payable in silver, no questions."
        ),
        tavern_rumor=(
            "There's a passage through the cliffs that leads to a second harbor. "
            "Only the oldest pirates know the way, and they aren't talking."
        ),
        cultural_group="The Brotherhood of the Cove",
        cultural_group_description="Not a guild — a silence. They protect each other by knowing nothing.",
    ),

    # === NORTH ATLANTIC ===
    PortCulture(
        port_id="ironhaven",
        landmark="The Great Foundry — its chimney visible twenty leagues at sea, glowing red at night.",
        local_custom="Greeting the harbor master with a nod, not words. The north wastes neither.",
        atmosphere="Coal smoke, ringing hammers, and the deep bass hum of bellows forcing air into furnaces.",
        dock_scene=(
            "Iron-hulled barges sit low in the water. Cranes swing overhead, loading "
            "ingots onto merchant vessels. Sparks drift from the foundry like orange snowflakes."
        ),
        tavern_rumor=(
            "The foundry master has been buying every scrap of timber that comes in. "
            "Some say he's building something in the deep sheds — something big."
        ),
        cultural_group="The Iron Guild",
        cultural_group_description="Masters of the forge. They set the iron price and every tool bears their mark.",
    ),
    PortCulture(
        port_id="stormwall",
        landmark="The Fortress — grey stone walls rising from the sea, older than anyone remembers.",
        local_custom="All cargo is inspected. Complaining about it marks you as a southerner.",
        atmosphere="Salt wind, military drums from the garrison, and the creak of heavy gates.",
        dock_scene=(
            "Navy vessels line the inner harbor. Soldiers in grey coats patrol the docks, "
            "checking manifests against sealed orders. Everything is orderly. Everything is watched."
        ),
        tavern_rumor=(
            "The garrison commander has doubled the night watch. Nobody says why, "
            "but the soldiers look north when they think no one's watching."
        ),
        cultural_group="The Northern Garrison",
        cultural_group_description="Military authority that governs the port. Trade is tolerated, not celebrated.",
    ),
    PortCulture(
        port_id="thornport",
        landmark="The Whale Arch — a jawbone arch spanning the harbor entrance, bleached white by decades of salt.",
        local_custom="Tea is offered before any negotiation. Tobacco is shared after a deal closes.",
        atmosphere="Wood smoke, drying fish, and the bitter-sweet scent of tobacco curing in the sheds.",
        dock_scene=(
            "Whaling boats line the pier, their harpoons cleaned and ready. "
            "Tea merchants squat beside wooden crates, brewing samples for prospective buyers."
        ),
        tavern_rumor=(
            "The whales are swimming further north each year. The old captains say "
            "the sea is warming. The young ones say the old ones talk too much."
        ),
        cultural_group="The Whaler-Merchants",
        cultural_group_description="Former whalers turned traders. They measure trust in shared hardship.",
    ),

    # === WEST AFRICA ===
    PortCulture(
        port_id="sun_harbor",
        landmark="The Cotton Steps — wide stone stairs where cotton bales are displayed and auctioned.",
        local_custom="The first trade of the day is blessed by an elder. Smart captains arrive early.",
        atmosphere="Warm earth, indigo dye, and the rhythmic singing of dockworkers loading bales.",
        dock_scene=(
            "Cotton bales stack three stories high along the waterfront. Women in indigo "
            "cloth oversee the weighing, their voices carrying the count in song."
        ),
        tavern_rumor=(
            "A ship arrived last month carrying nothing but empty crates — paid in full. "
            "The harbor master looked the other way. Nobody asks about empty crates here."
        ),
        cultural_group="The Weighers",
        cultural_group_description="The women who count and weigh every bale. Their word on quality is final.",
    ),
    PortCulture(
        port_id="palm_cove",
        landmark="The Distillery Row — seven rum houses, each with its own secret recipe and fierce pride.",
        local_custom="A cup of rum for every stranger. Refusing is an insult that lasts generations.",
        atmosphere="Sweet molasses, fermenting sugar cane, and the lazy hum of bees.",
        dock_scene=(
            "Small boats bob in the sheltered cove. Rum barrels roll down wooden ramps "
            "from the hilltop distilleries. Children dive for coins tossed by arriving crews."
        ),
        tavern_rumor=(
            "Old Cassius at the third distillery claims his rum can cure fever, heal wounds, "
            "and make you invisible to customs inspectors. Two of those are probably true."
        ),
        cultural_group="The Seven Houses",
        cultural_group_description="Seven distillery families who have been rivals for a century and allies for longer.",
    ),
    PortCulture(
        port_id="iron_point",
        landmark="The River Mouth Mines — tunnels carved into red cliffs where the river meets the sea.",
        local_custom="Miners spit on their hands before a deal. It means the ore is honest.",
        atmosphere="Red dust, the metallic tang of iron, and the echo of picks from the mine shafts.",
        dock_scene=(
            "Ore carts rattle down tracks to the loading docks. The river runs red with "
            "mine runoff. Everything here — the buildings, the clothes, the skin — is stained rust."
        ),
        tavern_rumor=(
            "The miners hit something in the deep shaft last week. Not iron — something older. "
            "The foreman sealed the tunnel and doubled the guard."
        ),
        cultural_group="The Red Hand",
        cultural_group_description="The mining collective. Their hands are permanently stained with iron oxide — a badge of honor.",
    ),
    PortCulture(
        port_id="pearl_shallows",
        landmark="The Blessing Pool — a tidal pool where divers pray before descending.",
        local_custom="Pearls are never haggled over. The diver names the price. You pay or you leave.",
        atmosphere="Warm shallow water, coral sand, and the silence of divers preparing their breath.",
        dock_scene=(
            "Canoes glide in from the reef. Divers emerge glistening, pouches of pearls "
            "tied to their wrists. An elder sits under a baobab tree, examining each pearl by sunlight."
        ),
        tavern_rumor=(
            "The oldest diver says there's a pearl the size of a fist somewhere in the deep reef. "
            "Three divers have gone looking. Two came back."
        ),
        cultural_group="The Breath-Holders",
        cultural_group_description="Pearl divers who can hold their breath for impossible minutes. Their craft is sacred.",
    ),

    # === EAST INDIES ===
    PortCulture(
        port_id="jade_port",
        landmark="The Porcelain Quarter — a district of workshops where master potters fire kilns day and night.",
        local_custom="Porcelain is presented on silk, never bare-handed. Fingerprints on porcelain void a sale.",
        atmosphere="Kiln heat, wet clay, and the delicate tap-tap-tap of artisans painting glaze patterns.",
        dock_scene=(
            "Bamboo cranes lift crates padded with straw from the hold. Each piece of porcelain "
            "is inspected by guild markers before it leaves the dock."
        ),
        tavern_rumor=(
            "A master potter smashed his entire year's work because he found a single flaw. "
            "The guild praised him. That kind of standard is why their porcelain costs what it does."
        ),
        cultural_group="The Kiln Masters",
        cultural_group_description="Porcelain artisans whose guild marks are more valued than the clay itself.",
    ),
    PortCulture(
        port_id="monsoon_reach",
        landmark="The Wind Temple — a pagoda on the headland where monks track the monsoon.",
        local_custom="Captains consult the monks before sailing. Their wind forecasts are uncannily accurate.",
        atmosphere="Salt spray, incense from the Wind Temple, and the creak of monsoon-tested rigging.",
        dock_scene=(
            "The harbor curves around a headland crowned by the Wind Temple. Ships here are built "
            "with deeper keels and stronger masts — the monsoon demands it."
        ),
        tavern_rumor=(
            "The monks say this monsoon season will be the worst in a generation. "
            "The shipwrights are quietly raising their prices."
        ),
        cultural_group="The Monsoon Brotherhood",
        cultural_group_description="Monks and sailors who read the wind. Their forecasts guide every departure.",
    ),
    PortCulture(
        port_id="silk_haven",
        landmark="The Loom Quarter — where silk is woven in patterns a thousand years old.",
        local_custom="Silk is presented folded, never rolled. Rolling insults the weaver's art.",
        atmosphere="The rhythmic clack of a hundred looms, the rustle of silk, and green tea steam.",
        dock_scene=(
            "Sampans glide between junks with crimson sails. Merchants in silk robes examine "
            "bolts of fabric with magnifying glasses, judging thread count by touch."
        ),
        tavern_rumor=(
            "The eldest weaver has created a pattern that changes color in different light. "
            "Three merchants have bid their entire fortunes for a single bolt."
        ),
        cultural_group="The Silk Weavers' Guild",
        cultural_group_description="Master artisans whose patterns are family secrets passed down for centuries.",
    ),
    PortCulture(
        port_id="crosswind_isle",
        landmark="The Free Port Bell — rung once for every ship that enters, never for one that leaves.",
        local_custom="All flags fly here. No nation claims the isle and all are welcome. That's the law.",
        atmosphere="A dozen languages, cooking smoke from every cuisine, and the constant negotiation of trade.",
        dock_scene=(
            "Ships from every region jostle for berth. The Free Port Bell tolls as you enter. "
            "Money-changers set up tables on the dock before your anchor hits bottom."
        ),
        tavern_rumor=(
            "Someone tried to claim the isle for an eastern dynasty last year. "
            "By morning, every captain in harbor had their guns trained on his ship. He left."
        ),
        cultural_group="The Free Port Council",
        cultural_group_description="An elected body of captains who enforce the one rule: no one rules.",
    ),
    PortCulture(
        port_id="dragons_gate",
        landmark="The Gate Fortress — twin stone towers flanking the strait, chains ready to close the passage.",
        local_custom="Weapons in cargo are declared or confiscated. There is no third option.",
        atmosphere="Military precision, jasmine tea, and the distant clank of the harbor chains.",
        dock_scene=(
            "Soldiers in lacquered armor inspect every ship that passes the twin towers. "
            "Tea merchants wait patiently on the inner docks, knowing inspection takes time."
        ),
        tavern_rumor=(
            "The fortress commander has not lowered the chains in fifteen years. "
            "The last captain who tried to run them is still chained to the seabed as a warning."
        ),
        cultural_group="The Gate Wardens",
        cultural_group_description="Military governors who control the strait. They are the law east of the gate.",
    ),
    PortCulture(
        port_id="spice_narrows",
        landmark="The Hanging Market — stalls suspended on ropes between cliff faces above the water.",
        local_custom="Prices are whispered, never spoken aloud. The walls have ears and the water carries sound.",
        atmosphere="Concentrated spice — overwhelming, intoxicating. The air itself burns your eyes.",
        dock_scene=(
            "The anchorage is hidden between volcanic cliffs. Rope ladders drop from the "
            "Hanging Market above. Commerce here is vertical — everything climbs."
        ),
        tavern_rumor=(
            "The Narrows have a second market, deeper in the cliffs, where things other than "
            "spice change hands. Finding the entrance is the first test of membership."
        ),
        cultural_group="The Spice Lords",
        cultural_group_description="They control access to the richest spice grounds in the world. Cross them once.",
    ),

    # === SOUTH SEAS ===
    PortCulture(
        port_id="ember_isle",
        landmark="Ember Peak — the smoldering volcano visible from fifty leagues, its glow a navigator's beacon.",
        local_custom="Visitors place a stone at the volcano's base. It's said to appease the mountain.",
        atmosphere="Sulfur, tropical flowers, and the low rumble of a volcano that never fully sleeps.",
        dock_scene=(
            "Black sand beaches and obsidian-sharp rocks frame the harbor. Steam rises from "
            "hot springs near the dock. Herbalists sort medicinal plants in the warm volcanic soil."
        ),
        tavern_rumor=(
            "The volcano speaks more often now. The islanders aren't worried — they say it "
            "always grumbles before a good harvest of medicine plants."
        ),
        cultural_group="The Ember Keepers",
        cultural_group_description="Herbalists and healers who know the volcanic plants. Their medicines are unmatched.",
    ),
    PortCulture(
        port_id="typhoon_anchorage",
        landmark="The Storm Wall — a massive breakwater built from the hulls of ships that didn't make it.",
        local_custom="Captains who survive a typhoon carve their ship's name into the Storm Wall. It's an honor.",
        atmosphere="Wind that never fully dies, salt-crusted everything, and the pride of survival.",
        dock_scene=(
            "The harbor is carved into the leeward cliff. Ships are chained, not anchored — "
            "anchors aren't enough here. Pearl divers work the outer reef between storms."
        ),
        tavern_rumor=(
            "A captain carved her name into the Storm Wall seven times — one for each typhoon "
            "survived. They call her the Unkillable. She drinks alone."
        ),
        cultural_group="The Storm Riders",
        cultural_group_description="Captains who have weathered the typhoons. Their stories are the price of entry.",
    ),
    PortCulture(
        port_id="coral_throne",
        landmark="The Coral Palace — grown over centuries from living reef, rising from the lagoon like a crown.",
        local_custom="All trade begins with tribute to the Coral King. Silk or weapons preferred. Refusal is exile.",
        atmosphere="Warm lagoon water, crushed coral underfoot, and the distant beat of ceremonial drums.",
        dock_scene=(
            "The lagoon entrance is narrow and treacherous — local pilots guide every ship "
            "through the reef. The Coral Palace rises ahead, its walls glittering with embedded "
            "shells and pearls. Warriors in war canoes escort you to the royal dock."
        ),
        tavern_rumor=(
            "The Coral King has no heir. Three princes compete for the throne, each courting "
            "foreign captains for weapons and alliances. Smart traders play all three."
        ),
        cultural_group="The Coral Court",
        cultural_group_description="The island kingdom's royal court. Tribute buys access. Generosity buys favor.",
    ),
]}
