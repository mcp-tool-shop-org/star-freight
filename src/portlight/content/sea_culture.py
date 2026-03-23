"""Sea culture — route encounters, NPC sightings, lore, weather, crew voice.

The sea between ports should feel as alive as the ports themselves. This module
provides route-specific flavor text, encounters unique to specific trade lanes,
NPC sightings from the 134 port characters, sea superstitions, and crew morale.

Design principle: every voyage should feel like it happens in a SPECIFIC place,
not in "generic ocean." The Grain Road should smell like wheat. The Smuggler's
Run should feel like held breath. Typhoon Alley should terrify.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RouteEncounter:
    """A flavor encounter specific to a named route or region."""
    text: str                        # what happens / what you see
    category: str                    # sighting / lore / weather / crew / encounter
    mechanical_effect: str = ""      # optional: "speed+10%", "morale+1", etc.


@dataclass(frozen=True)
class RouteEncounterTable:
    """Encounter table for a specific route or region."""
    route_key: str                   # lore_name or region name
    encounters: list[RouteEncounter] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Route-Specific Encounters (15 named routes)
# ---------------------------------------------------------------------------

ROUTE_ENCOUNTERS: dict[str, RouteEncounterTable] = {

    "The Grain Road": RouteEncounterTable(
        route_key="The Grain Road",
        encounters=[
            # Sightings
            RouteEncounter("A grain convoy from Porto Novo passes — six barges in formation, hulls riding low. The Exchange Guild flag snaps in the breeze.", "sighting"),
            RouteEncounter("A felucca from Al-Manar crosses your wake, its deck stacked with brass-bound spice chests. The crew waves.", "sighting"),
            RouteEncounter("You pass the marker buoy where the old coast road meets the sea. Grain ships have used this lane since before the Exchange was built.", "sighting"),
            # Lore
            RouteEncounter("Your bosun points at the coastline. 'See that cliff? They say the first Grain Exchange was carved into it — before Porto Novo even had a harbor.'", "lore"),
            RouteEncounter("An old sailor on deck murmurs a prayer as you pass a rocky outcrop. 'Every grain ship salutes the Stone. It's bad luck not to.' You can't see why the rock matters. He won't explain.", "lore"),
            # Weather
            RouteEncounter("The Mediterranean breeze carries the smell of baking bread from the coastal villages. The crew breathes deep.", "weather"),
            RouteEncounter("Calm water, clear sky. The Grain Road earns its reputation as the gentlest route in the Known World.", "weather"),
            # Crew
            RouteEncounter("The crew is relaxed — they know this route. Someone starts humming a Porto Novo dock song. Others join.", "crew"),
            RouteEncounter("Your navigator corrects course by a fraction. 'The current shifts here every spring,' he says. 'Old knowledge.'", "crew"),
        ],
    ),

    "The Timber Run": RouteEncounterTable(
        route_key="The Timber Run",
        encounters=[
            RouteEncounter("A timber barge from Silva Bay passes, logs lashed together and riding the current. The smell of fresh-cut oak carries across the water.", "sighting"),
            RouteEncounter("Sawdust floats on the surface — you're near Silva Bay. The entire harbor sheds wood dust like a forest sheds leaves.", "weather"),
            RouteEncounter("Your ship's carpenter examines the hull planking and nods. 'Silva Bay timber. Best in the Mediterranean. This wood will outlast all of us.'", "crew"),
            RouteEncounter("A fishing boat crosses your path. The fisherman shouts: 'Elena's building something big! Three masts! I saw the keel!'", "sighting"),
        ],
    ),

    "The Shadow Lane": RouteEncounterTable(
        route_key="The Shadow Lane",
        encounters=[
            RouteEncounter("A ship passes with no flag flying. The crew watches you. You watch them. Nobody waves. This is the Shadow Lane.", "sighting"),
            RouteEncounter("Your lookout spots a rowboat tucked into the cliff shadow. Empty. Or is it? On the Shadow Lane, the difference matters.", "encounter"),
            RouteEncounter("The coast here is riddled with coves — each one a potential anchorage, each one a potential ambush. Your helmsman hugs the deeper water.", "weather"),
            RouteEncounter("A crewman mutters: 'My cousin sailed this lane for years. Made a fortune. Then one day he didn't come back. Nobody asked questions. You don't, on the Shadow Lane.'", "lore"),
            RouteEncounter("You catch a whiff of torch smoke from a cliff face. Corsair's Rest is close — you can't see it, but you can smell it.", "sighting"),
        ],
    ),

    "The Iron Strait": RouteEncounterTable(
        route_key="The Iron Strait",
        encounters=[
            RouteEncounter("A Stormwall patrol ship passes — grey hull, no flag of welcome. The crew watches you with professional interest. They're always watching.", "sighting"),
            RouteEncounter("Iron barges from the foundry ride low in the water, sparks still drifting from the cargo. The Great Foundry's chimney glows on the horizon.", "sighting"),
            RouteEncounter("The water here is dark — iron runoff from the foundries. Your navigator says it's deeper than it looks. The iron goes all the way down.", "weather"),
            RouteEncounter("An old hand on deck says: 'I served at Stormwall once. The strait's the only thing between the north and... whatever's out there.' He doesn't finish.", "lore"),
        ],
    ),

    "The Tea and Tobacco Road": RouteEncounterTable(
        route_key="The Tea and Tobacco Road",
        encounters=[
            RouteEncounter("A Thornport whaler — converted to trading — passes with tea crates stacked on deck. The crew smokes pipes and waves cheerfully.", "sighting"),
            RouteEncounter("The Whale Arch is visible from here — a bleached jawbone spanning the harbor entrance. Even at this distance, you can see the names carved in it.", "sighting"),
            RouteEncounter("Your cook brews tea with leaves bought at Thornport. The crew gathers. For a moment, the northern sea feels almost warm.", "crew"),
            RouteEncounter("Fog rolls in. A horn sounds from somewhere ahead — Thornport's harbor signal. The old whalers' way of saying 'you're close.'", "weather"),
        ],
    ),

    "The Cotton Crossing": RouteEncounterTable(
        route_key="The Cotton Crossing",
        encounters=[
            RouteEncounter("The water changes color as you leave the Mediterranean — warmer, greener. The Gold Coast is ahead. The air carries the faintest scent of earth.", "weather"),
            RouteEncounter("A cotton trader's vessel passes, bales stacked so high the deck is barely visible. Women in indigo cloth stand at the rail, singing the count.", "sighting"),
            RouteEncounter("Your crew's mood shifts as the coast changes. The northern rigidity fades. Someone laughs. Someone else starts a story. The Gold Coast does this to people.", "crew"),
            RouteEncounter("A pod of dolphins escorts you for an hour. Your bosun says it's a sign of welcome from the coast. The crew believes him.", "encounter"),
            RouteEncounter("You pass a merchant vessel flying the Exchange Alliance flag, heading north. 'Cotton north, grain south,' your navigator says. 'Been this way for centuries.'", "sighting"),
        ],
    ),

    "The Long Crossing": RouteEncounterTable(
        route_key="The Long Crossing",
        encounters=[
            RouteEncounter("Open water. No land in any direction. The sky meets the sea in a circle that hasn't changed in three days. The crew goes quiet.", "weather"),
            RouteEncounter("Day twelve of the crossing. Your navigator takes star readings twice a night. The slightest error here means weeks of drift.", "crew"),
            RouteEncounter("A piece of driftwood with carved symbols floats past — a prayer marker from an island nobody's charted. Someone was here before you.", "lore"),
            RouteEncounter("The crew's conversation turns to home. Where they came from. Where they'll go when they're done. The Long Crossing forces these thoughts.", "crew"),
            RouteEncounter("Your water casks are half-empty. The navigator says two more days. The cook starts rationing without being asked. Everyone knows what's at stake.", "encounter"),
            RouteEncounter("A flying fish lands on deck. The crew takes it as a sign — land is close. Your navigator confirms: the current has shifted. The East Indies are near.", "weather"),
            RouteEncounter("You spot another ship on the same heading — impossibly far away, a speck of sail. Someone else is making the crossing. You'll never know who.", "sighting"),
        ],
    ),

    "The Porcelain Lane": RouteEncounterTable(
        route_key="The Porcelain Lane",
        encounters=[
            RouteEncounter("A junk with the Kiln Masters' guild mark on its sail passes — its hold padded with straw. Every piece of porcelain in the west passed through this lane.", "sighting"),
            RouteEncounter("Your crew handles the cargo more carefully here. In the East Indies, they've learned that porcelain commands respect — and that broken porcelain means broken trust.", "crew"),
            RouteEncounter("The water turns jade-green. Islands appear like scattered emeralds. You're in the Porcelain Lane — where the oldest trade in the East flows.", "weather"),
            RouteEncounter("A fishing sampan pulls alongside. The fisherman offers you a fresh catch in exchange for news. In the East Indies, information is currency.", "encounter"),
        ],
    ),

    "The Silk Road by Sea": RouteEncounterTable(
        route_key="The Silk Road by Sea",
        encounters=[
            RouteEncounter("A silk convoy glides past — three junks in formation, their sails painted with the Weavers' Guild pattern. The silk inside is worth more than your ship.", "sighting"),
            RouteEncounter("Incense drifts from a passing vessel. In the Silk Waters, even the cargo smells beautiful.", "weather"),
            RouteEncounter("Your crew folds their clothes more carefully after a few days in these waters. The East Indies changes how people treat fabric.", "crew"),
            RouteEncounter("A sampan merchant offers a bolt of silk through your porthole while you're anchored for the night. The price is suspiciously good. Your bosun advises caution.", "encounter"),
        ],
    ),

    "Typhoon Alley": RouteEncounterTable(
        route_key="Typhoon Alley",
        encounters=[
            RouteEncounter("The pressure drops. Your ears pop. The sky turns a color you've never seen — yellow-grey-green. Typhoon Alley earns its name.", "weather"),
            RouteEncounter("A wrecked hull drifts past — no mast, no crew, barnacles already growing. Someone's journey ended here. Your crew says nothing.", "lore"),
            RouteEncounter("A storm rider's outrigger appears from nowhere, surfs the leading wave, and vanishes behind a squall. You're in their territory.", "sighting"),
            RouteEncounter("Your ship groans. The hull flexes in ways the shipwright intended — if she's from Monsoon Reach or Typhoon Anchorage. If she's Mediterranean... you pray.", "crew"),
            RouteEncounter("Lightning illuminates something on the horizon — an island not on your charts. When dawn comes, it's gone. The crew doesn't discuss it.", "lore"),
            RouteEncounter("Rain so heavy it stings the skin. The crew works by touch. The compass spins. Your navigator switches to dead reckoning and doesn't sleep for two days.", "weather"),
        ],
    ),

    "The Volcanic Passage": RouteEncounterTable(
        route_key="The Volcanic Passage",
        encounters=[
            RouteEncounter("The water warms. Not from the sun — from below. Volcanic vents heat the current here. The hull temperature rises. Your crew shifts nervously.", "weather"),
            RouteEncounter("Sulfur. The air thickens with it. Your eyes water. Welcome to the Volcanic Passage — the sea itself is on fire underneath.", "weather"),
            RouteEncounter("A column of steam rises from the water ahead — an underwater vent. Your navigator routes around it. The crew watches the thermometer climb.", "encounter"),
            RouteEncounter("An Ember Isle medicine boat crosses your path, obsidian-hulled and silent. The herbalists wave. Their cargo smells of eucalyptus and volcanic earth.", "sighting"),
            RouteEncounter("Your cook heats water for tea using the sea itself — he drops a bucket into the volcanic current and it comes up warm. 'Free fuel,' he says.", "crew"),
        ],
    ),

    "The Monsoon Shortcut": RouteEncounterTable(
        route_key="The Monsoon Shortcut",
        encounters=[
            RouteEncounter("You catch the monsoon wind and FLY. The ship heels over, sails taut, crew bracing. This is why they call it the Shortcut — if you time it right, nothing's faster.", "weather"),
            RouteEncounter("The wind dies. Completely. You're becalmed in open water between the Mediterranean and the East Indies. The crew stares at limp sails.", "weather"),
            RouteEncounter("A merchant vessel that attempted the Shortcut last season drifts past. Abandoned. The log is gone. Whatever happened, nobody recorded it.", "lore"),
            RouteEncounter("Your navigator pulls out the monsoon charts — handwritten, passed down from Farouk in Al-Manar's tea house. 'He sailed this seven times,' your navigator says. 'Trust the charts.'", "lore"),
            RouteEncounter("Wind shifts. The monsoon is changing direction — a day early. Your navigator adjusts instantly. The margin between 'Shortcut' and 'death sentence' is measured in hours.", "encounter"),
        ],
    ),

    "The Smuggler's Run": RouteEncounterTable(
        route_key="The Smuggler's Run",
        encounters=[
            RouteEncounter("Darkness. You run without lights because on the Smuggler's Run, visibility is the enemy. Your crew communicates in whispers.", "encounter"),
            RouteEncounter("A Crimson Tide ship appears on the horizon — then another. Then a third. They're not pursuing you. They're watching. The Run belongs to them.", "sighting"),
            RouteEncounter("Your lookout spots a trail of floating debris — crates, barrels, a torn sail. Someone dumped cargo in a hurry. Navy patrol, probably. Your crew moves your contraband deeper into the hold.", "encounter"),
            RouteEncounter("Eighty leagues of open water between two black market ports. The longest, most dangerous route in the Known World. Your crew knows the stakes. Nobody complains. Nobody jokes.", "crew"),
            RouteEncounter("An old pirate shanty drifts from below deck — someone's singing about the Run. The lyrics are about a captain who made the crossing so many times, the navy thought he was a ghost. He stopped correcting them.", "lore"),
            RouteEncounter("The Syndicate's signal — a lantern flash from an unseen ship — briefly illuminates the darkness. Three short, one long. It means 'patrol ahead, alter course.' Your navigator adjusts without being told.", "encounter"),
        ],
    ),

    "The Northern Passage": RouteEncounterTable(
        route_key="The Northern Passage",
        encounters=[
            RouteEncounter("The longest profitable route in the world. Iron west, porcelain east. Your hold tells the story of two civilizations that need each other.", "lore"),
            RouteEncounter("Ice. Not dangerous — floating crystals from the northern edge of the passage. Beautiful and foreign. Your crew collects pieces as souvenirs.", "weather"),
            RouteEncounter("A whale surfaces alongside — massive, slow, unconcerned. It travels the same passage, following the same currents, and has done so longer than any ship.", "sighting"),
            RouteEncounter("Week three. The provisions are holding, the crew is tired, and the passage stretches on. Your navigator says halfway. He's been saying halfway for two days.", "crew"),
            RouteEncounter("You spot Ironhaven's foundry glow on the western horizon — or is it Jade Port's kilns on the eastern? On the Northern Passage, both ends look the same from the middle.", "weather"),
        ],
    ),

    "The Deep South Run": RouteEncounterTable(
        route_key="The Deep South Run",
        encounters=[
            RouteEncounter("Pearl to pearl. The divers of the shallows and the divers of the reef — same craft, different kingdoms. Your cargo carries the weight of both traditions.", "lore"),
            RouteEncounter("Turquoise water so clear you can see the reef twenty feet below. Beautiful and deadly. One wrong turn and the coral claims your hull.", "weather"),
            RouteEncounter("A war canoe from Coral Throne appears. Warriors in painted armor watch you pass. One raises a spear — not in threat but in salute. You've been recognized.", "sighting"),
            RouteEncounter("Your crew spots something glinting in the shallows — a pearl, dropped or thrown. Nobody dives for it. On the Deep South Run, taking what the reef didn't offer is bad luck.", "lore"),
            RouteEncounter("Ceremonial drums carry across the water from an island you can't see. The Coral Kingdom is celebrating something. Your crew listens. The rhythm is infectious.", "encounter"),
        ],
    ),
}


# ---------------------------------------------------------------------------
# Region-Default Encounters (for unnamed routes)
# ---------------------------------------------------------------------------

REGION_ENCOUNTERS: dict[str, RouteEncounterTable] = {
    "Mediterranean": RouteEncounterTable(
        route_key="Mediterranean",
        encounters=[
            RouteEncounter("A merchant galley passes flying the Exchange Alliance flag. Orderly, clean, professional. The Mediterranean way.", "sighting"),
            RouteEncounter("Fishing boats dot the horizon — small, colorful, and everywhere. The Mediterranean feeds itself.", "sighting"),
            RouteEncounter("The coast is never far. Villages, harbors, lighthouses — civilization lines every shore.", "weather"),
            RouteEncounter("Your crew discusses grain prices — the universal conversation on Mediterranean routes.", "crew"),
        ],
    ),
    "North Atlantic": RouteEncounterTable(
        route_key="North Atlantic",
        encounters=[
            RouteEncounter("Grey seas, grey sky. The North Atlantic doesn't waste energy on color.", "weather"),
            RouteEncounter("A Stormwall patrol passes without greeting. In the north, silence IS the greeting.", "sighting"),
            RouteEncounter("Your crew pulls collars tight. The Atlantic cold gets into your bones and stays.", "crew"),
            RouteEncounter("Fog banks drift like walls. Your lookout strains forward. In the North Atlantic, what you can't see is what kills you.", "weather"),
        ],
    ),
    "West Africa": RouteEncounterTable(
        route_key="West Africa",
        encounters=[
            RouteEncounter("Warm air carries the scent of earth — red earth, growing things. The Gold Coast is alive.", "weather"),
            RouteEncounter("A fishing fleet returns singing. The rhythm is centuries old and utterly joyful.", "sighting"),
            RouteEncounter("Your crew relaxes. Something about the Gold Coast waters changes the mood. Shoulders drop. Voices soften.", "crew"),
            RouteEncounter("Rain falls warm and brief. The crew stands on deck, faces upturned, laughing. The Gold Coast rains are gifts, not threats.", "weather"),
        ],
    ),
    "East Indies": RouteEncounterTable(
        route_key="East Indies",
        encounters=[
            RouteEncounter("Incense drifts from a passing junk. In the East Indies, even the air is cultivated.", "weather"),
            RouteEncounter("A fleet of sampans crosses your path — fishermen, traders, and families living on the water. The East Indies floats.", "sighting"),
            RouteEncounter("Your crew becomes more formal in Eastern waters. They bow instead of waving. The culture seeps in.", "crew"),
            RouteEncounter("Islands appear and vanish in the morning mist. A thousand islands hide in the haze. Your charts show a fraction of them.", "weather"),
        ],
    ),
    "South Seas": RouteEncounterTable(
        route_key="South Seas",
        encounters=[
            RouteEncounter("The reef glows beneath the surface — alive, colorful, dangerous. The South Seas are beautiful the way a blade is beautiful.", "weather"),
            RouteEncounter("An outrigger canoe appears, its crew watching you with calm interest. They've been watching ships pass for generations.", "sighting"),
            RouteEncounter("Your crew falls silent. The South Seas demand a different kind of attention — not the bustle of the Mediterranean but the focus of a diver reading the reef.", "crew"),
            RouteEncounter("Flying fish skip across the bow. Stars reflected in still water. The South Seas overwhelm through beauty, not force.", "weather"),
        ],
    ),
}


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def get_route_encounters(lore_name: str) -> RouteEncounterTable | None:
    """Get encounters specific to a named route."""
    return ROUTE_ENCOUNTERS.get(lore_name)


def get_region_encounters(region: str) -> RouteEncounterTable | None:
    """Get default encounters for a region (unnamed routes)."""
    return REGION_ENCOUNTERS.get(region)


# ---------------------------------------------------------------------------
# NPC Sightings at Sea
# ---------------------------------------------------------------------------
# When traveling through a region, you might spot NPCs from nearby ports
# going about their business. Non-interactive — passing ships, not meetings.
# Each sighting is region-locked so you only see local NPCs.

@dataclass(frozen=True)
class NPCSighting:
    """A named NPC spotted at sea — flavor, not interaction."""
    npc_name: str
    port_id: str
    region: str
    text: str


NPC_SIGHTINGS: dict[str, list[NPCSighting]] = {
    "Mediterranean": [
        NPCSighting("Dimitri Andros", "silva_bay", "Mediterranean",
            "A Silva Bay hull — unmistakable lines — cuts across your bow. Dimitri Andros stands at the prow, examining the waterline of a new build. He's testing it himself. He always does."),
        NPCSighting("Marta Soares", "porto_novo", "Mediterranean",
            "A Porto Novo grain barge passes with the Exchange Guild flag. On the quarterdeck, Marta Soares scans the horizon with a spyglass — checking the competition's cargo, no doubt."),
        NPCSighting("Scarlet Ana", "corsairs_rest", "Mediterranean",
            "Crimson pennants on the horizon. Scarlet Ana's flagship passes at distance — she sees you, tips her hat, and sails on. Business elsewhere today."),
        NPCSighting("Inspector Salva", "porto_novo", "Mediterranean",
            "A Porto Novo customs cutter crosses your wake. Inspector Salva stands at the rail with a manifest in hand, heading to intercept someone else. You're glad it's not you."),
        NPCSighting("Ghost", "corsairs_rest", "Mediterranean",
            "A ship passes in the early hours — no lights, no flag, loaded heavy. Ghost's crew, running cargo. By the time you blink, they've vanished into the dark."),
    ],
    "North Atlantic": [
        NPCSighting("The Smith", "ironhaven", "North Atlantic",
            "An Ironhaven supply boat passes carrying a crate marked with the Smith's personal seal. Whatever's inside, it was built by the best hands in the north. Someone ordered something special."),
        NPCSighting("Sergeant Kruze", "ironhaven", "North Atlantic",
            "A grey-hulled ship cuts through the fog — Iron Wolves. Sergeant Kruze stands at the helm, scanning methodically. He spots you, holds your gaze for three seconds, then turns away. Assessment complete."),
        NPCSighting("Siv Lindgren", "stormwall", "North Atlantic",
            "A small trade vessel flying Stormwall colors passes. Siv Lindgren waves energetically from the deck — she's heading to recruit merchants for the garrison's supply contracts. Her enthusiasm is visible from a league away."),
        NPCSighting("Bones Thorsen", "thornport", "North Atlantic",
            "A converted whaler — Bones Thorsen's fishing fleet — trawls the northern waters. The whale skeleton mounted on the bow catches the light. Bones raises a hand in silent greeting."),
    ],
    "West Africa": [
        NPCSighting("Ama Mensah", "sun_harbor", "West Africa",
            "A Gold Coast trading vessel passes with the Compact flag. On deck, Chief Weigher Ama stands with her counting staff, supervising a cotton shipment. Even at sea, her standards travel with her."),
        NPCSighting("Old Cassius", "palm_cove", "West Africa",
            "A Palm Cove rum boat passes close enough that you can smell the cargo. Old Cassius himself sits on a barrel, waving a bottle. 'BEST RUM ON THE COAST!' he shouts. Some things don't need a harbor."),
        NPCSighting("Yaa Acheampong", "iron_point", "West Africa",
            "An Iron Point ore barge passes, Yaa Acheampong standing on a crate of raw iron, negotiating by signal flag with a ship heading east. She's cutting deals even in transit."),
        NPCSighting("Elder Ama Diallo", "pearl_shallows", "West Africa",
            "A canoe of Breath-Holder divers glides past, heading for the outer reef. Elder Ama sits at the stern, eyes closed, breathing slowly. The morning dive is sacred. You pass in silence."),
    ],
    "East Indies": [
        NPCSighting("Factor Wu Jian", "jade_port", "East Indies",
            "A Jade Port silk-and-porcelain convoy passes — three junks in formation. Factor Wu stands on the lead ship, silk robes immaculate even at sea. He bows precisely as you pass. Fifteen degrees."),
        NPCSighting("Brother Anand", "monsoon_reach", "East Indies",
            "A small boat with a saffron sail drifts past the Wind Temple headland. Brother Anand sits cross-legged on the deck, eyes closed, reading the wind by feel. His forecast will be posted at dawn."),
        NPCSighting("Typhoon Mei", "spice_narrows", "East Indies",
            "A ship erupts from behind an island at impossible speed. Typhoon Mei stands on the bowsprit, laughing into the wind. She sees you, waves wildly, and vanishes around the next headland. Chaos in human form."),
        NPCSighting("Master Ink", "silk_haven", "East Indies",
            "A sampan drifts past Silk Haven's harbor. Master Ink sits cross-legged, painting the sea. He doesn't look up. A perfect brushstroke captures a wave that no longer exists. The painting will outlast the ocean."),
        NPCSighting("Apprentice Lin Yue", "jade_port", "East Indies",
            "A small kiln-boat from Jade Port passes — Apprentice Lin testing a new glaze in sea air. She holds a tile up to the light, frowns, adjusts something, holds it up again. Obsession at twenty-two."),
    ],
    "South Seas": [
        NPCSighting("Storm Chief Rangi", "typhoon_anchorage", "South Seas",
            "An outrigger war canoe slices through the swell — Storm Chief Rangi at the helm, reading the weather through the spray. Seven typhoons survived. She's watching the horizon for the eighth."),
        NPCSighting("Dive Boss Moana", "typhoon_anchorage", "South Seas",
            "A diving boat surfaces nearby — Moana's crew returning from the deep reef. Moana herself emerges glistening, a pouch of pearls tied to her wrist. She dives where others won't."),
        NPCSighting("Reef Pilot Iti", "coral_throne", "South Seas",
            "A pilot canoe approaches from the reef. Iti stands at the bow, reading the coral by water color. Twelve generations of reef knowledge in one pair of eyes."),
        NPCSighting("War Chief Tane", "coral_throne", "South Seas",
            "War canoes appear — painted to match the coral, nearly invisible until they're alongside. War Chief Tane's escort. They watch you pass. The spears stay lowered. Today."),
        NPCSighting("Healer Sera", "ember_isle", "South Seas",
            "An Ember Isle medicine boat passes, volcanic-stone hull and eucalyptus smoke trailing behind. Head Herbalist Sera waves from the deck, surrounded by crates of freshly harvested remedies."),
    ],
}


def get_npc_sightings(region: str) -> list[NPCSighting]:
    """Get possible NPC sightings for a region."""
    return NPC_SIGHTINGS.get(region, [])


# ---------------------------------------------------------------------------
# Sea Lore & Superstitions
# ---------------------------------------------------------------------------
# First-time experiences that trigger crew stories and beliefs.
# Each fires once per game — tracked by the narrative system.

@dataclass(frozen=True)
class SeaSuperstition:
    """A crew belief or story triggered by a specific condition."""
    id: str
    trigger: str                     # what triggers it: "first_region_X", "first_storm", etc.
    text: str
    crew_reaction: str               # how the crew responds


SEA_SUPERSTITIONS: list[SeaSuperstition] = [
    # First-time region entries
    SeaSuperstition("first_east_indies", "first_region_East Indies",
        "The old hands gather the new crew at the bow. 'The East Indies,' the bosun says. 'Everything here is older than us. Older than our ships. Older than our countries. Show respect and the waters will let you pass.'",
        "The crew moves more quietly. Voices lower. Something has shifted."),
    SeaSuperstition("first_south_seas", "first_region_South Seas",
        "The lookout calls 'Reef!' and the crew rushes to the rail. Below the hull, the coral glows in colors nobody has words for. Your navigator whispers: 'The charts are wrong here. The reef moves. Trust your eyes, not the paper.'",
        "Wonder. Genuine, wide-eyed wonder. Even the veterans stare."),
    SeaSuperstition("first_north_atlantic", "first_region_North Atlantic",
        "The temperature drops. The Mediterranean warmth fades like a memory. An old sailor wraps himself in a wool coat and says: 'The Atlantic doesn't warn you. It just hits. Keep your head down and your hull tight.'",
        "The crew gets serious. Joking stops. Preparation begins."),
    SeaSuperstition("first_west_africa", "first_region_West Africa",
        "Warm rain — the first the crew has felt. It tastes of earth and growing things. A sailor who's been here before says: 'The Gold Coast gives freely. But it remembers what you give back. Trade honestly here.'",
        "Relaxation. Shoulders drop. Someone laughs. The coast has a way."),

    # Voyage events
    SeaSuperstition("first_storm_survived", "survived_storm",
        "After the storm passes, the crew is silent for a long time. Then someone starts bailing, and everyone follows. The bosun says: 'She held. The ship held.' It sounds like a prayer.",
        "Bond. The crew who survives a storm together is a different crew afterward."),
    SeaSuperstition("first_pirate_encounter", "survived_pirates",
        "The pirate ship fades behind you. Hands are shaking. Someone laughs — the high, thin laugh of relief. 'That was close,' the helmsman says. Nobody disagrees.",
        "Alertness. Every sail on the horizon gets a long look from now on."),
    SeaSuperstition("passing_wreck", "wreck_sighted",
        "A wrecked hull drifts past — no mast, no crew, barnacles thick on the waterline. The crew watches in silence. Someone removes their hat. 'Could've been us,' the bosun says. Nobody argues.",
        "Mortality. The sea reminds you what happens when luck runs out."),
    SeaSuperstition("becalmed_first", "first_calm",
        "No wind. The sails hang like wet laundry. The sea is a mirror. Time stops. After two hours, the crew starts making up games. After six, they start telling truths they'd never say on land.",
        "Honesty. There's nothing to do but wait and talk. The truths come out."),

    # Cargo and trade
    SeaSuperstition("sacred_cargo", "carrying_sacred_good",
        "The old hands treat the cargo differently — more carefully, more quietly. 'This is what they revere,' the bosun explains. 'Handle it with respect and the port will remember. Handle it badly and so will the sea.'",
        "Reverence. The cargo becomes more than weight. It becomes responsibility."),
    SeaSuperstition("contraband_nerves", "carrying_contraband",
        "Nobody says the word. They call it 'the special cargo' or 'the extra provisions' or just nod toward the hold. The crew avoids the inspector's eye even when there isn't one. Contraband changes how people breathe.",
        "Tension. Jokes become quieter. Laughter becomes shorter. Everyone watches the horizon."),

    # Milestones
    SeaSuperstition("hundredth_day", "day_100",
        "Day one hundred. The navigator marks it in the log with a small ceremony — a tradition older than anyone aboard can explain. A cup of the best drink is poured into the sea. 'For the water that carried us,' the navigator says.",
        "Pride. A hundred days of voyaging. Not everyone can say that."),
    SeaSuperstition("fifth_region", "visited_all_regions",
        "The crew realizes, quietly, that they've sailed every water the charts show. Mediterranean, Atlantic, Gold Coast, East Indies, South Seas. The Known World, all of it, beneath their keel. A sailor says: 'What's left?' Nobody answers. Nobody needs to.",
        "Completion. And the strange emptiness that follows. What do you seek when you've seen everything?"),
]


# ---------------------------------------------------------------------------
# Crew Morale & Voice
# ---------------------------------------------------------------------------
# Crew reactions based on game state — the emotional mirror of the voyage.

@dataclass(frozen=True)
class CrewMood:
    """Crew mood triggered by game state conditions."""
    id: str
    condition: str                   # what triggers this mood
    flavor_texts: list[str]          # random selection from these


CREW_MOODS: list[CrewMood] = [
    CrewMood("prosperous", "silver > 2000",
        ["The crew walks taller. When the hold is full and the silver heavy, even the sea looks friendly.",
         "Someone's whistling at the helm. The cook made extra tonight. Prosperity makes generous sailors.",
         "The crew discusses what they'll spend their shares on. Houses, farms, a boat of their own. Silver breeds dreams."]),

    CrewMood("struggling", "silver < 100",
        ["The crew eats quietly. Nobody complains — but nobody laughs either. Thin times make thin smiles.",
         "Whispered conversations below deck. 'How long can we keep sailing?' your bosun hears. He doesn't repeat it.",
         "The cook stretches the provisions. Watered rum, thinner stew. The crew notices but says nothing. Loyalty has limits."]),

    CrewMood("first_voyage", "day < 10",
        ["Everything is new. The crew leans over the rail watching the wake. Even the seagulls are fascinating. This won't last, but right now, the world is enormous.",
         "Your navigator explains the stars to a young sailor. The old hands pretend not to listen. They listen anyway.",
         "The smell of the sea — salt, kelp, distance. For the crew, this is the smell of possibility. For the captain, it's the smell of responsibility."]),

    CrewMood("veteran", "day > 200",
        ["The crew moves like a machine — sails adjusted before you call for it, rigging checked without orders. Two hundred days builds instinct.",
         "Your bosun can read your expression from the helm. You don't need to give orders anymore. A glance at the sails is enough.",
         "The crew has its own language now — gestures, looks, half-sentences that carry complete meanings. They're not a crew. They're a crew."]),

    CrewMood("after_big_trade", "recent_profit > 500",
        ["The hold is lighter and the silver heavier. The crew celebrates with an extra ration. Your bosun says: 'That's a trade they'll talk about at port.'",
         "Word travels fast on a ship. Everyone knows the margin you made. Respect comes in the form of sharper salutes and louder songs."]),

    CrewMood("after_loss", "recent_loss",
        ["Silence on deck. The cargo is gone — seized, sunk, or sold at a loss. The crew doesn't blame you. Not out loud. The sea takes what it takes.",
         "Your bosun finds you at the helm after dark. 'It happens to every captain,' he says. 'The ones who quit are the ones who deserved to.' Then he leaves."]),

    CrewMood("new_ship", "just_upgraded",
        ["The crew explores the new ship like children in a new house — opening every hatch, testing every line, arguing about which berth is best.",
         "The new ship creaks differently. The old hands listen, learning her voice. Every ship has one. This one hasn't told them yet."]),

    CrewMood("carrying_contraband", "has_contraband",
        ["Nobody talks about it. The hold is rearranged so the 'special cargo' is behind the legitimate goods. The crew avoids eye contact when inspectors are mentioned.",
         "Your lookout watches the horizon with unusual intensity. Every sail could be a patrol. Every sail probably isn't. But every sail gets watched.",
         "A nervous joke from the galley: 'What's the difference between a merchant and a smuggler? The smuggler knows when to shut up.' Nobody laughs. Then everyone laughs."]),

    CrewMood("in_storm", "during_storm",
        ["Rain. Wind. The deck tilts at angles that make standing an act of faith. The crew works in silence because the storm takes every word.",
         "The ship groans. The crew listens. You learn to read a hull's voice — complaint vs. warning vs. surrender. This groan is complaint. You hope.",
         "Someone prays. Someone else checks the bilge pump. Both are acts of faith."]),

    CrewMood("calm_seas", "extended_calm",
        ["The sea is glass. The sky is empty. The wind is a memory. Your crew invents entertainment: card games, fishing, arguments about whose home port has better food.",
         "Day three of calm. The cook runs a fishing line. The catch is better than anything in the provisions. 'I should do this for a living,' he says. Nobody points out that he does.",
         "Becalmed. The old hands say it's the sea's way of making you think. What you think about depends on what you carry — in the hold and in the heart."]),
]


def get_crew_moods() -> list[CrewMood]:
    """Get all crew mood definitions."""
    return CREW_MOODS


def get_superstitions() -> list[SeaSuperstition]:
    """Get all sea superstitions."""
    return SEA_SUPERSTITIONS


# ---------------------------------------------------------------------------
# Seasonal Weather Narratives
# ---------------------------------------------------------------------------
# Extended weather descriptions for each region × season combination.
# These are longer than the weather_flavor in seasons.py — full paragraphs
# that capture the sensory experience of sailing through that season.
# Each has: an opening (what you see when you set sail), a mid-voyage
# description, and a closing (what the weather is doing when you arrive).

@dataclass(frozen=True)
class WeatherNarrative:
    """Extended weather description for a specific region and season."""
    region: str
    season: str
    departure_text: str              # what the weather is like when you leave
    mid_voyage_texts: list[str]      # random mid-voyage atmosphere (pick one per day)
    arrival_text: str                # what greets you when you arrive
    night_text: str                  # what the nights are like
    crew_weather_reaction: str       # how the crew feels about the conditions


WEATHER_NARRATIVES: dict[tuple[str, str], WeatherNarrative] = {}

# --- MEDITERRANEAN ---

WEATHER_NARRATIVES[("Mediterranean", "spring")] = WeatherNarrative(
    region="Mediterranean", season="spring",
    departure_text="Spring morning on the Middle Sea. The harbor water is glass-still at dawn, and the first breeze arrives with the sun — gentle, warm, carrying the scent of wildflowers from the coastal hills. Perfect sailing weather.",
    mid_voyage_texts=[
        "The Mediterranean in spring is kind. Gentle swells, clear horizons, and a breeze that fills the sails without testing the rigging. The sea remembers how to be generous.",
        "Sunlight turns the water into hammered copper. Schools of fish dart beneath the hull, silver flashes in blue-green water. The coast is always visible — civilization lining every shore.",
        "A warm wind from the south carries the smell of olive groves and baking stone. The crew works with their sleeves rolled up, savoring the warmth after winter's grey.",
        "The sky is the Mediterranean's trademark blue — the blue that painters have tried to capture for centuries and never quite matched. Your sails look white against it, clean and proud.",
    ],
    arrival_text="The port appears through a golden haze — sun-warmed stone, terracotta roofs, and the sound of harbor life carrying across calm water. Spring arrivals in the Mediterranean feel like coming home, even when you've never been here before.",
    night_text="Stars so close they feel like lanterns. The sea reflects them, doubling the light. Mediterranean spring nights are warm enough to sleep on deck, and half the crew does — faces upturned, breathing salt air that smells faintly of flowers.",
    crew_weather_reaction="The crew is at ease. Spring in the Mediterranean is the reward for winter's hardship. Voices are relaxed, movements unhurried. This is the season they signed on for.",
)

WEATHER_NARRATIVES[("Mediterranean", "summer")] = WeatherNarrative(
    region="Mediterranean", season="summer",
    departure_text="Heat. The harbor shimmers before the sun is fully up. Tar softens on the deck. The sails hang limp until the afternoon breeze — and even then, it barely fills them. Summer in the Mediterranean is beautiful and motionless.",
    mid_voyage_texts=[
        "Becalmed. The sails droop. The sea is a mirror that reflects the sky back at itself. The crew strips to the waist and waits. In the Mediterranean summer, patience is the only wind.",
        "The afternoon breeze arrives like a gift — sudden, warm, and gone too soon. Your ship moves in bursts between long stretches of glassy calm. Every mile is earned.",
        "Heat haze on the horizon makes the coast dance. Distances are deceiving — that port that looks an hour away might be three. The summer Mediterranean plays tricks with light.",
        "The water is so warm your crew swims alongside the ship during calms. Someone dives to check the hull and comes up grinning. 'Clean as a whistle,' he says, dripping gold in the sunlight.",
    ],
    arrival_text="The port materializes through the heat shimmer — wavering, dreamlike, slowly solidifying as you approach. Summer arrivals feel like waking from a nap — slow, warm, slightly disoriented.",
    night_text="The heat doesn't release at sundown — it radiates from the deck, the sails, the water itself. The crew sleeps in shifts because the watches are short and nobody wants to be below deck. Fireflies on the coast look like fallen stars.",
    crew_weather_reaction="Sluggish but content. Nobody works fast in Mediterranean summer. The crew has adapted: slow mornings, brief intense work when the breeze arrives, long evenings. It's not laziness — it's survival.",
)

WEATHER_NARRATIVES[("Mediterranean", "autumn")] = WeatherNarrative(
    region="Mediterranean", season="autumn",
    departure_text="The light changes in autumn — gold where it was white, long shadows by mid-afternoon. The breeze has an edge it didn't have last month. The harbor is busy with harvest traffic, every ship racing to fill holds before the season turns.",
    mid_voyage_texts=[
        "Autumn swells — longer, deeper than summer's calm. The ship finds a rhythm, rising and falling with a cadence that the old hands find comforting and the new ones find unsettling.",
        "Clouds build on the western horizon. Not threatening — not yet — but the crew watches them the way you watch a dog you don't know. Autumn storms announce themselves before they arrive.",
        "The smell of grain on the wind. Somewhere on the coast, the harvest is in. Grain barges cross your path, riding low and heavy. The Mediterranean is feeding itself for winter.",
        "Rain — brief, warm, autumnal. It passes in twenty minutes and leaves the air clean. The crew catches rainwater in barrels. 'Free provisions,' the bosun says, and everyone agrees.",
    ],
    arrival_text="The port is alive with harvest energy — grain stacking on the docks, merchants shouting prices, the annual rush to store, sell, and ship before winter closes the best routes. Autumn arrivals feel urgent, purposeful.",
    night_text="Cool enough for a coat now. The stars are sharper than summer's haze allowed. Your navigator takes cleaner readings, works faster. Autumn nights are for navigation. The sky cooperates.",
    crew_weather_reaction="Energized. Autumn is harvest — for the coast and for the crew. The margins are best now, the cargo abundant, and the season's end adds urgency. Everyone works faster.",
)

WEATHER_NARRATIVES[("Mediterranean", "winter")] = WeatherNarrative(
    region="Mediterranean", season="winter",
    departure_text="Grey. The harbor is grey, the sky is grey, the water is grey. The Mediterranean's winter palette is monochrome and honest — no pretending the world is kind. The crew wraps up and says little. Departure in winter is an act of will.",
    mid_voyage_texts=[
        "Rain that doesn't stop. Not a storm — just persistent, cold, coastal rain that seeps through every seam and soaks every surface. The Mediterranean in winter is not dangerous. It's miserable.",
        "The coast disappears in fog. Your navigator works from dead reckoning and doesn't like it. The Mediterranean is supposed to be visible — coast in sight, landmarks familiar. Winter takes that away.",
        "Cold wind from the north — the tramontana. It cuts through wool, through timber, through the belief that the Mediterranean is a warm sea. In winter, it's not. It's a cold sea that remembers being warm.",
        "A winter swell catches the ship beam-on. Not dangerous — just uncomfortable. Everything shifts, slides, rattles. The cook's pots clang. Someone's hammock dumps them on the deck. Winter at sea is unglamorous.",
    ],
    arrival_text="The port appears through drizzle — wet stone, shuttered market stalls, smoke from chimneys. Winter arrivals in the Mediterranean are quiet, functional, and appreciated more for the docking than the destination.",
    night_text="Long nights. The crew retreats below deck, huddled around the galley fire. Stories get longer in winter — there's nothing else to do. The watch is cold, the stars are hidden, and the sea sounds different when you can't see it.",
    crew_weather_reaction="Stoic. Nobody complains because complaining doesn't change winter. The crew does the work, eats the stew, and waits for spring. Mediterranean winter is character-building, which is another word for unpleasant.",
)

# --- NORTH ATLANTIC ---

WEATHER_NARRATIVES[("North Atlantic", "spring")] = WeatherNarrative(
    region="North Atlantic", season="spring",
    departure_text="Ice breaks in the harbor with sounds like gunshots. The first ships of spring push out through grey water and grey sky, testing whether winter has truly released its grip. The air smells of thaw — iron, mud, and the first faint promise of warmth.",
    mid_voyage_texts=[
        "The Atlantic in spring is uncertain — moments of clarity broken by squalls that arrive from nowhere and vanish just as fast. Your ship is a cork between moods.",
        "An iceberg — small, already half-melted — drifts past on the current. Beautiful and wrong, like a wedding dress in a gutter. The crew watches it pass. Spring in the north still has winter's teeth.",
        "A berg the size of a chapel drifts silently to starboard. Beneath the waterline, its shadow stretches impossibly far. The helmsman gives it a wide berth without being told.",
        "Ice fragments crackle against the hull like broken glass. The water here is colder than it should be — somewhere north, a glacier is calving its children into the current.",
        "Fog banks drift like walls. Your lookout strains forward. In the North Atlantic, what you can't see is what kills you.",
        "The first real warmth of the year arrives in a patch of sunlight that hits the deck at noon. The crew stands in it like cats. Twenty minutes later, it's gone. They remember it for hours.",
        "A whale surfaces to port, blows once, and dives. The crew marks it as good luck. The bosun marks it as a navigational hazard. Both are right.",
        "The wind carries the smell of land — peat smoke and pine — though the charts say the coast is still two days east. The crew trusts their noses more than your charts.",
    ],
    arrival_text="The northern port emerges from persistent haze — stone walls, smoke, the sound of industry resuming after winter's pause. Spring arrivals feel like relief — you made it through another season.",
    night_text="Northern spring nights: cold but not killing. Stars appear in the gaps between racing clouds. The aurora occasionally shimmers on the horizon — green fire in a dark sky. The crew watches in silence. Some things are too large for words.",
    crew_weather_reaction="Cautious optimism. The worst is over. Probably. The crew is thawing along with the sea — muscles loosening, voices warming, the first jokes since autumn.",
)

WEATHER_NARRATIVES[("North Atlantic", "summer")] = WeatherNarrative(
    region="North Atlantic", season="summer",
    departure_text="The golden window opens. Clear sky, moderate wind, and the Atlantic transformed — blue instead of grey, welcoming instead of threatening. The crew can barely believe it. Northern summer is brief and must be seized.",
    mid_voyage_texts=[
        "Long days — the sun barely sets this far north. The crew works extended watches because the light allows it and the calm demands it. More can be done in a northern summer day than two Mediterranean ones.",
        "The sea sparkles. The wind is steady. The ship makes time. After months of fighting the Atlantic, suddenly it's helping. The crew sails with grins. Summer will be over too soon.",
        "Whales surface alongside — great grey shapes that blow and roll and vanish. The crew hangs over the rail like children. In summer, even the Atlantic's giants seem friendly.",
        "A fog bank drifts past — cool, momentary, and gone. Summer fog in the north is gentle, not the blinding winter kind. It passes like a thought and leaves the air clean.",
    ],
    arrival_text="The port in summer is unrecognizable — people outside, markets open, the fortress walls looking less like fortification and more like architecture. Northern ports in summer almost look happy.",
    night_text="Twilight that lasts for hours. The sky goes from blue to gold to rose to a deep violet that never quite reaches black. The crew plays cards on deck by the lingering light. Someone says, 'This is why we sail north.' Nobody disagrees.",
    crew_weather_reaction="Joy. Genuine, uncomplicated joy. The northern summer is the crew's reward for surviving everything else. They're louder, more physical, more alive. They know it won't last. They savor it.",
)

WEATHER_NARRATIVES[("North Atlantic", "autumn")] = WeatherNarrative(
    region="North Atlantic", season="autumn",
    departure_text="The wind shifts. You feel it before you see it — a cold edge that wasn't there yesterday, a grey line on the horizon that means the Atlantic is remembering what it is. The crew stows extra provisions without being told. Autumn in the north is a warning.",
    mid_voyage_texts=[
        "Autumn gales strip the warmth from the air in hours. The sails strain. The rigging sings a note that experienced sailors recognize as 'get ready.' The Atlantic is warming up for winter.",
        "Rain and wind in rotation — a squall, then calm, then another squall. The crew can't find a rhythm because the sea won't give them one. Autumn in the Atlantic is the sea being indecisive about how much it wants to hurt you.",
        "The light fails earlier each day. By mid-afternoon, the helmsman squints. By evening, the watch starts early. Autumn is a countdown to the dark months.",
        "A big swell rolls in from the northwest — the first winter storm passing far to the north, sending its echoes south. The ship rides it like a horse clearing a fence. The crew holds on and says nothing.",
    ],
    arrival_text="The port is battening down. Shutters close, mooring ropes double, and the harbor master's face says everything: winter is coming, and anyone still at sea in six weeks is either brave or foolish.",
    night_text="Cold and dark and close. The stars are sharp but the crew doesn't look up — they look down, at the deck, checking the lashings, tightening what the day's wind loosened. Autumn nights are for preparation.",
    crew_weather_reaction="Focused. No more summer ease. The crew is calculating: how many more voyages before winter? How much silver is enough to wait it out? Every autumn decision has winter's weight behind it.",
)

WEATHER_NARRATIVES[("North Atlantic", "winter")] = WeatherNarrative(
    region="North Atlantic", season="winter",
    departure_text="You should not be here. The harbor master said so. The crew's faces said so. The ice on the rigging says so. Winter in the North Atlantic is not a season — it's a dare. You're sailing anyway, because the medicine prices at Stormwall are worth the risk. Probably.",
    mid_voyage_texts=[
        "Walls of grey water. That's the Atlantic winter. Not waves — walls. They build, and build, and when they break, the sound is a cannon shot that the whole hull feels. Your ship is a splinter on an angry ocean.",
        "Ice forms on the rigging. The crew goes aloft with hammers — break it before the weight capsizes you. Their hands bleed. They don't mention it. Winter Atlantic sailing is not for the soft.",
        "Wind that cuts through oak. The crew can't feel their faces. The helmsman steers by body weight because his hands are too numb to grip the wheel. Navigation is instinct now, not science.",
        "A moment of calm — the eye of a passing system. The clouds open. Weak sunlight hits the deck for thirty seconds. The crew stares at it like a vision. Then the wind returns, harder than before.",
        "The ship groans. Not the casual complaint of rough seas — a deep, structural protest. Your ship is telling you it was not built for this. You listen. You adjust course. You pray the next port is close.",
    ],
    arrival_text="The port materializes through driving snow. It's the most beautiful thing you've ever seen — not because it's beautiful, but because it's THERE. Winter arrivals in the North Atlantic are measured in gratitude, not silver.",
    night_text="Darkness from mid-afternoon to mid-morning. The crew works by lantern and by memory. The watch is miserable, cold, and essential — because in winter, the thing that kills you arrives in the dark. Every sound is examined. Every shadow is questioned.",
    crew_weather_reaction="Grim. Not afraid — grim. The crew who sails the winter Atlantic has made a choice, and they know the price. They don't joke. They don't complain. They work, they eat, they watch. Survival is the only conversation.",
)

# --- WEST AFRICA ---

WEATHER_NARRATIVES[("West Africa", "spring")] = WeatherNarrative(
    region="West Africa", season="spring",
    departure_text="Dry season holds. The harbor bakes under a high white sky, and the offshore breeze carries the scent of red earth from the interior. The sails fill with steady trade winds — the Gold Coast in spring is the most reliable sailing in the Known World.",
    mid_voyage_texts=[
        "Steady wind, steady sun, steady sea. The Gold Coast in dry season is sailing as it should be — predictable, warm, and kind. Your ship makes good time without drama.",
        "The coast is a ribbon of gold sand and green jungle. Fishing boats dot the shallows, their crews waving as you pass. On the Gold Coast, every stranger is a potential friend.",
        "Heat haze makes the horizon shimmer, but the wind is constant. The crew works in easy rhythm — they've found the Gold Coast's tempo, and it's gentle.",
    ],
    arrival_text="The port welcomes you with color — indigo cloth, golden cotton, the red earth that stains everything it touches. Arrivals on the Gold Coast feel like being invited to a celebration you didn't know was happening.",
    night_text="Stars blazing in a clear sky. The Southern Cross visible on the horizon. Drums carry from the coast — distant, rhythmic, old. The crew listens. The music carries stories they don't understand but somehow feel.",
    crew_weather_reaction="Content. The Gold Coast's spring weather asks nothing of them — no storms to fight, no cold to endure. The crew relaxes into the warmth and the rhythm. Some of them don't want to leave.",
)

WEATHER_NARRATIVES[("West Africa", "summer")] = WeatherNarrative(
    region="West Africa", season="summer",
    departure_text="The rains come. Not gently — the sky opens like a faucet and the harbor turns into a river. Then, twenty minutes later, blazing sun. Then rain again. The Gold Coast's wet season is the sky changing its mind every hour.",
    mid_voyage_texts=[
        "Tropical rain — warm, heavy, and so dense you can't see the bow from the helm. The crew works blind for ten minutes, then the cloud passes and the sun returns, hotter than before. Everything steams.",
        "The coast turns green — impossibly green, every shade at once. The rivers flood, carrying red earth into the sea. The water near shore is brown and warm. The pearl divers are thriving.",
        "Humidity thick enough to drink. The crew strips to waist and pours seawater over their heads. Nothing dries. Cloth, rope, wood — everything is damp. The ship smells of wet timber and tropical growth.",
    ],
    arrival_text="The port is a puddle. Red mud everywhere, rivulets running between market stalls, and the Weighers working under canvas shelters. Nobody minds. The rains are life here — the cotton grows, the rivers flow, the earth gives.",
    night_text="Lightning on the horizon — constant, silent, illuminating clouds from within like lanterns. The crew watches nature's light show from the deck. Thunder rolls across the water an hour later. The Gold Coast night sky in summer is its own spectacle.",
    crew_weather_reaction="Wet but happy. There's something infectious about the Gold Coast's summer — the sheer vitality of it. Rain and sun and rain again. The crew can't stay dry but they can't stop smiling.",
)

WEATHER_NARRATIVES[("West Africa", "autumn")] = WeatherNarrative(
    region="West Africa", season="autumn",
    departure_text="The rains ease. The air clears. The second cotton harvest fills the warehouses, and the coast buzzes with the energy of abundance. The sailing is good — warm, moderate wind, and the visibility that the wet season denied.",
    mid_voyage_texts=[
        "Post-rain clarity. The horizon is sharp, the colors saturated, the air clean. The Gold Coast after the rains is the world freshly washed.",
        "Market day energy on the water — canoes loaded with cotton, dyes, provisions, all heading between ports. The coast is trading with itself, and you're invited to join.",
        "Cool evenings and warm days. The crew discovers that autumn on the Gold Coast is the perfect temperature — the one all other seasons are trying and failing to reach.",
    ],
    arrival_text="The port is abundant. Cotton stacked high, dye vats full, pearl divers returning with the season's best haul. Autumn arrivals on the Gold Coast feel like arriving at a feast.",
    night_text="Clear skies, warm air, and the smell of harvest fires from the interior. The coast celebrates the second harvest with drums and song that carry to sea. Your crew drifts to sleep listening to music from a place they'll never fully understand but deeply respect.",
    crew_weather_reaction="Grateful. The Gold Coast's autumn is generous, and the crew feels it. They eat well, sleep well, and trade well. Some of them start talking about retirement here. They're only half joking.",
)

WEATHER_NARRATIVES[("West Africa", "winter")] = WeatherNarrative(
    region="West Africa", season="winter",
    departure_text="The harmattan arrives — a dry wind from the Saharan interior that carries red dust, reduces visibility, and turns the sky the color of old brass. The harbor is dusty and warm. Your sails fill with wind that tastes like desert.",
    mid_voyage_texts=[
        "Red dust coats everything — deck, sails, skin. The crew coughs and squints. The harmattan is the Gold Coast's only difficult weather, and it's more annoying than dangerous.",
        "The sea is calm — the harmattan suppresses waves. Your ship glides through flat water under a hazy sky. Visibility is poor but the wind is steady. Trade-offs.",
        "Stars are invisible through the dust haze. Your navigator grumbles and uses dead reckoning. The Gold Coast in winter is the only season where the sky fails you.",
    ],
    arrival_text="The port materializes through dust haze — a ghostly outline that solidifies as you approach. The dockworkers are wrapped against the dust, voices muffled. Winter on the Gold Coast is quiet, dusty, and productive — the mines work double shifts in dry weather.",
    night_text="The harmattan wind doesn't stop at night. It whispers through the rigging, carrying fine red dust that infiltrates everything. The crew sleeps with cloth over their faces. The stars, when they occasionally appear through the haze, are the color of copper.",
    crew_weather_reaction="Patient. The harmattan is annoying but not threatening. The crew adapts — cloth masks, eye protection, more water. It's a sailor's inconvenience, not a sailor's enemy.",
)

# --- EAST INDIES ---

WEATHER_NARRATIVES[("East Indies", "spring")] = WeatherNarrative(
    region="East Indies", season="spring",
    departure_text="The monsoon retreats. You can feel it — the pressure lifts, the wind shifts, and the archipelago takes its first deep breath in months. Spring in the East Indies is resurrection. The kilns relight. The looms restart. The ports open like flowers.",
    mid_voyage_texts=[
        "Jade-green water and islands scattered like emeralds. The post-monsoon sea is calm, grateful, almost apologetic for what it did last season. The crew sails with their guard down for the first time in months.",
        "Incense drifts from a temple on a passing island. In the East Indies, even the air worships. The crew breathes deep and something in them quiets.",
        "Sampans and junks crowd the channels — trade resuming, routes reopening, the archipelago reconnecting after the monsoon divided it. The sea is full of purpose.",
        "The light in the East Indies is different from anywhere else — softer, greener, filtered through atmospheric moisture that hasn't quite dried. It makes everything look like a painting of itself.",
    ],
    arrival_text="The port is blooming. Literally — flowers on the docks, garlands on the warehouses, the scent of jasmine mixing with salt air. Spring arrivals in the East Indies feel like being invited to a celebration of survival.",
    night_text="Warm, humid, alive. The sound of insects and tree frogs from the nearby islands creates a wall of noise that the crew finds either maddening or hypnotic, depending on how long they've been in the East. Fireflies over the water look like fallen stars that decided to come back.",
    crew_weather_reaction="Enchanted. The East Indies in spring seduces every crew that sails it. The beauty, the calm, the sense that the world is more ancient and more alive here than anywhere they've been.",
)

WEATHER_NARRATIVES[("East Indies", "summer")] = WeatherNarrative(
    region="East Indies", season="summer",
    departure_text="The monsoon. You felt it building for days — pressure dropping, wind shifting, clouds massing on the horizon like an army. Now it arrives. The harbor master's face says what his words won't: you should not sail today. You sail anyway, because the spice prices demand it.",
    mid_voyage_texts=[
        "Rain so heavy it becomes a physical force — pushing down on the deck, pressing the crew to their knees, turning the sea into a churning brown soup. The monsoon doesn't rain. It ASSAULTS.",
        "The wind switches direction in seconds — from driving force to wall. Your ship heels, staggers, rights itself. The crew scrambles to reef sails that were full moments ago. The monsoon teaches humility in real time.",
        "Thunder so deep it vibrates in your chest. Lightning illuminates the sea in white snapshots — each one showing a world of chaos, waves, and spray. Between flashes, darkness so complete you forget you have eyes.",
        "A break in the monsoon — sudden, surreal calm. The clouds open for ten minutes. Sunlight hits the sea like a spotlight. The crew stares upward, blinking. Then the clouds close and the storm resumes. The mercy was temporary.",
        "The ship rides a wave that feels like a building falling. The hull flexes. The mast bends. Everything that isn't lashed down flies. And then the wave passes, and you're still floating. The monsoon decides whether you survive. You don't get a vote.",
    ],
    arrival_text="The port appears between squalls — there one moment, hidden the next. You dock in driving rain, the crew soaked, the ship groaning, and the harbor master nodding because he expected you wouldn't listen. But you're here. That's what matters.",
    night_text="Monsoon nights are the sea's darkest theatre. Rain, wind, the ship pitching in black water, and the navigational instruments spinning. Your crew trusts the ship, trusts each other, and doesn't trust anything else. Nobody sleeps. Sleep is for seasons that aren't trying to kill you.",
    crew_weather_reaction="Fear and pride, inseparably tangled. The crew who sails the monsoon is terrified and knows it. They sail anyway. That's not bravery — it's something deeper. It's the decision to be present for the worst the world can offer and keep working.",
)

WEATHER_NARRATIVES[("East Indies", "autumn")] = WeatherNarrative(
    region="East Indies", season="autumn",
    departure_text="Post-monsoon. The air is clean — cleaner than it's been in months, washed by weeks of rain. The harbor smells of wet wood and fresh spice. The monsoon left destruction and renewal in equal measure. Autumn in the East Indies is harvest time.",
    mid_voyage_texts=[
        "The spice harvest is in. You can smell it from the sea — clove, cinnamon, cardamom, carried by the post-monsoon breeze. The East Indies announces its wealth through your nose before your eyes confirm it.",
        "The sea is littered with debris from the monsoon — driftwood, broken boats, vegetation from flooded coasts. The crew picks through it for salvage. One man's storm is another man's flotsam.",
        "Post-monsoon swells — long, slow, rolling waves that carry the memory of the storm. Your ship rides them like breathing. In and out. In and out. The monsoon's ghost.",
    ],
    arrival_text="The port is frantic with harvest energy — spice being graded, weighed, packaged, shipped. Every captain in the East Indies is here for the same reason: post-monsoon spice at peak freshness. The competition is fierce. The margins are worth it.",
    night_text="Clear skies after the monsoon. The stars feel closer than they have in months — the atmosphere scrubbed clean by weeks of rain. Your navigator takes the most accurate readings of the year. The East Indies under autumn stars is navigational paradise.",
    crew_weather_reaction="Energized. The monsoon is over, the sailing is excellent, and the holds are filling with the most profitable cargo of the year. The crew works with the intensity of a team that survived something and now wants the reward.",
)

WEATHER_NARRATIVES[("East Indies", "winter")] = WeatherNarrative(
    region="East Indies", season="winter",
    departure_text="Dry season. The kilns burn bright, the looms run at full speed, and the East Indies settles into the quiet productivity that follows the monsoon's chaos. The harbor is orderly. The wind is gentle. Winter in the East Indies is not winter — it's the world exhaling.",
    mid_voyage_texts=[
        "Cool air from the mountains — the only time the East Indies feels anything less than tropical. The crew discovers that 'cool' in the East Indies is still warmer than summer in the North Atlantic. Perspective.",
        "Clear skies, gentle wind, jade-green water. The East Indies in dry season is the most pleasant sailing in the world. The crew debates this opinion loudly and at length. Nobody has a counterargument.",
        "The silk convoys are at peak volume — three, four at a time crossing the channels, their painted sails turning the sea into a parade. Winter in the East Indies is commerce as art.",
    ],
    arrival_text="The port is at its most beautiful — clean, productive, the markets stocked, the craftsmen at work. Winter arrivals feel privileged — you're seeing the East Indies at its best, doing what it does better than anywhere else in the world.",
    night_text="Cool, clear, still. The East Indies winter night is so quiet you can hear the looms working in Silk Haven from the water. The sound carries — click-clack-click-clack — a rhythm as old as the islands themselves. The crew sleeps well. The sea is gentle. The night belongs to the craftsmen.",
    crew_weather_reaction="Peaceful. The East Indies in winter is the least dramatic sailing any of them have experienced. After the monsoon, it feels unreal — as if the sea is apologizing. The crew accepts the apology. They'll forgive, but they won't forget.",
)

# --- SOUTH SEAS ---

WEATHER_NARRATIVES[("South Seas", "spring")] = WeatherNarrative(
    region="South Seas", season="spring",
    departure_text="Warm water, clear sky, and the reef glowing beneath the surface. Spring in the South Seas is an invitation — the diving season begins, the lagoons calm, and the islands reveal themselves as the most beautiful places on earth. Your crew falls silent at the beauty. Then somebody whistles.",
    mid_voyage_texts=[
        "Turquoise water so clear you can see the reef twenty feet below. Fish in colors that shouldn't exist — electric blue, neon yellow, impossible pink. The South Seas is nature's art gallery, and the entry fee is getting here alive.",
        "Flying fish skip across the bow in silver arcs. The crew counts them — an old sailor's game. More than twenty means good luck. More than fifty means the reef is thriving. Today there are seventy.",
        "A sea turtle surfaces beside the ship, ancient and unhurried. It looks at you with an eye that has seen more of the ocean than any captain. Then it submerges, returning to a world you can visit but never inhabit.",
    ],
    arrival_text="The island appears like a dream — palm trees, white sand, volcanic peaks wreathed in cloud. The harbor is a lagoon so perfectly sheltered it feels like sailing into a room. The water changes from blue to turquoise to glass. You've arrived at the edge of the world.",
    night_text="The Milky Way. You've seen it before, but not like this — not from the South Seas, where there are no cities, no foundries, no lanterns to compete. The sky is milk and fire and the crew lies on deck staring upward, humbled by the sheer scale of what's above them.",
    crew_weather_reaction="Awe. The South Seas in spring is the most beautiful thing most of them have ever seen. Even the veterans — even the ones who've sailed every water on the charts — go quiet. Some things earn silence.",
)

WEATHER_NARRATIVES[("South Seas", "summer")] = WeatherNarrative(
    region="South Seas", season="summer",
    departure_text="The sky darkens without warning. One moment, paradise. The next, a wall of black cloud on the horizon, moving faster than anything that size should move. Typhoon season in the South Seas. The harbor chains are out. The Storm Wall waits.",
    mid_voyage_texts=[
        "A typhoon — not nearby, but close enough that its outer bands rake your ship with rain and wind that change direction every twenty minutes. The crew is exhausted from adjusting sails that won't stay adjusted.",
        "The pressure drops so fast your ears pop. The sea rises. The sky descends. Between them, your ship — a splinter of wood and canvas in a space that's closing like a fist.",
        "Rain so heavy it stings the skin. Horizontal rain that the crew leans into like walking uphill. The ship is a submarine — water everywhere, above, below, in every hold and hatch. Dry is a memory.",
        "Calm. Sudden, terrifying calm. The eye. The crew looks up at a circle of blue sky surrounded by a wall of black cloud. Beautiful and wrong. 'Work fast,' the bosun says. 'The other side is coming.' It does.",
    ],
    arrival_text="The harbor is damaged. Roofs missing, boats beached, the Storm Wall rearranged by the typhoon's hand. But the port is alive — rebuilding already, because in the South Seas, typhoons are not disasters. They're seasons. You survive them and you rebuild.",
    night_text="Typhoon nights are absolute darkness punctuated by lightning that reveals, for one instant, the full horror and beauty of what the storm has done to the sea. Mountains of water. Valleys between them. Your ship, somehow, on top. Lightning fades. Darkness returns. You wait for the next flash.",
    crew_weather_reaction="Primal. The typhoon strips everything to essentials — hold on, work hard, trust the ship. The crew doesn't think about silver, cargo, or ports. They think about the next wave. Then the one after that. Then the one after that.",
)

WEATHER_NARRATIVES[("South Seas", "autumn")] = WeatherNarrative(
    region="South Seas", season="autumn",
    departure_text="The typhoons pass. The sea calms. The reef reveals its post-storm treasures — new formations, shifted channels, and the pearls that the violent water shook loose from the deep beds. Autumn in the South Seas is nature's apology after summer's violence.",
    mid_voyage_texts=[
        "Post-typhoon clarity. The air is washed clean, the water crystal, and the reef below seems closer than before — as if the storm lowered the sea level just for you. The divers are already working.",
        "Warm rain and warm sun in alternation. The South Seas' autumn is tropical — not the cold decline of northern autumns but a gentle softening. The light turns gold. The reef glows amber.",
        "Volcanic smoke drifts from Ember Isle — visible from leagues away, a thin grey line on the horizon. The mountain is always talking. In autumn, after the storms, people listen more carefully.",
    ],
    arrival_text="The island port is rebuilding and harvesting simultaneously — storm damage repaired with one hand, pearl and medicine hauls processed with the other. The South Seas doesn't pause between seasons. It overlaps them.",
    night_text="Clear skies, warm air, and the bioluminescent glow of the reef visible from the surface. The water itself shines — blue-green light pulsing with the current. The crew leans over the rail, watching the sea breathe light. Nobody speaks. Nobody needs to.",
    crew_weather_reaction="Renewed. After the typhoon, autumn feels like being born again. The crew moves differently — looser, more grateful, more aware that they're alive and the sea permitted it. Pearl diving season adds excitement. The hold will fill with treasures the storm revealed.",
)

WEATHER_NARRATIVES[("South Seas", "winter")] = WeatherNarrative(
    region="South Seas", season="winter",
    departure_text="The gentlest season. The harbor is calm, the wind soft, the sky that particular shade of blue that the South Seas does better than anywhere else. Winter here isn't cold — it's the sea taking a breath between typhoons. The Coral King holds court. Tribute flows. The world is at peace.",
    mid_voyage_texts=[
        "Still lagoons and soft winds. The South Seas in winter is the ocean's version of sleep — not unconscious but resting, dreaming, preparing for the next season's violence.",
        "The reef is at its most beautiful in winter — every color visible through still water, no storms to cloud it, no currents to disturb it. Your crew can't stop staring down. The world beneath the hull is more beautiful than the one above it.",
        "Ceremonial drums carry from Coral Throne — the Coral King's winter court is in session. The rhythm reaches you from leagues away, steady and ancient. The sea itself seems to pulse in time.",
    ],
    arrival_text="The lagoon is glass. The Coral Palace glitters in the low winter sun. War canoes escort you in with a rhythm that matches the drums from shore. Winter arrivals at the South Seas feel like arriving at the end of the world — and discovering it's beautiful.",
    night_text="Stars reflected in still water so perfectly that you can't tell up from down. The reef glows faintly beneath the surface. The crew lies on deck, suspended between two skies. Somewhere, the Drum Keeper plays the midnight rhythm. The sound carries over still water for miles. The crew doesn't understand it. They feel it.",
    crew_weather_reaction="At peace. For many of the crew, this is the first genuine peace they've felt since they left home — wherever home was. The South Seas in winter isn't exciting. It's something better. It's the world telling you it's okay to rest.",
)


def get_weather_narrative(region: str, season: str) -> WeatherNarrative | None:
    """Get the extended weather narrative for a region and season."""
    return WEATHER_NARRATIVES.get((region, season))
