"""Cross-port NPC networks — the relationships that make the world coherent.

The 134 port NPCs don't exist in isolation. Merchants trade with each other.
Tavern keepers share intelligence. Brokers compete for the same captains.
Inspectors form a professional fraternity. These networks mean that your
reputation follows you — help Marta in Porto Novo, and Ama in Sun Harbor
hears about it. Cheat Fernanda, and Tariq in Al-Manar already knows.

Design principle: the world should feel SMALL where it matters. The people
who run these ports talk to each other. A captain who understands these
connections trades better than one who treats each port as an island.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrossPortRelationship:
    """A relationship between two NPCs at different ports."""
    npc_a_id: str
    npc_a_name: str
    npc_a_port: str
    npc_b_id: str
    npc_b_name: str
    npc_b_port: str
    network: str                     # merchant / tavern / broker / inspector
    disposition: str                 # allied / rival / professional / personal
    description: str                 # the nature of the relationship
    player_impact: str               # how this affects the player


@dataclass(frozen=True)
class NetworkNode:
    """A tavern keeper or merchant's position in the intelligence/trade web."""
    npc_id: str
    npc_name: str
    port_id: str
    network: str
    role: str                        # hub / spoke / bridge / outsider
    intelligence_flavor: str         # what kind of info they traffic in
    share_conditions: str            # under what conditions they share with the player


# =========================================================================
# MERCHANT TRADE NETWORKS
# =========================================================================
# Who trades with whom across ports, and what that means for the player.

MERCHANT_RELATIONSHIPS: list[CrossPortRelationship] = [
    # === The Grain-Cotton Axis (Mediterranean <-> West Africa) ===
    CrossPortRelationship(
        "pn_marta", "Marta Soares", "porto_novo",
        "sh_ama", "Ama Mensah", "sun_harbor",
        network="merchant", disposition="professional",
        description=(
            "The two most powerful exchange factors in their respective blocs. "
            "Marta sets the Mediterranean grain price; Ama sets the Gold Coast cotton "
            "price. They've never met in person but exchange quarterly market reports "
            "through trusted captains. Each respects the other's authority — and each "
            "would undercut the other without hesitation if the margin justified it."
        ),
        player_impact="Captains who trade the grain-cotton route earn standing with both. Captains who play one against the other lose standing with both — they compare notes.",
    ),
    CrossPortRelationship(
        "sh_broker_fatou", "Fatou Ndiaye", "sun_harbor",
        "jp_factor_wu", "Factor Wu Jian", "jade_port",
        network="merchant", disposition="allied",
        description=(
            "The most important new trade relationship in the Known World. "
            "Fatou brokered the first direct Gold Coast-to-Silk Circle cotton-for-silk "
            "agreement. Wu provided the Eastern access. Together they've created a "
            "trade lane that bypasses Porto Novo entirely — which Marta knows and resents."
        ),
        player_impact="Captains who carry cotton east or silk west get premium prices from both. This route is the future of trade — early adopters earn loyalty.",
    ),

    # === The Iron Triangle (Ironhaven <-> Iron Point <-> Jade Port) ===
    CrossPortRelationship(
        "ip_broker_yaa", "Yaa Acheampong", "iron_point",
        "jp_factor_wu", "Factor Wu Jian", "jade_port",
        network="merchant", disposition="allied",
        description=(
            "The deal that could reshape the iron market. Yaa sells raw ore directly "
            "to Wu for the Kiln Masters' glazing needs, bypassing Ironhaven's markup "
            "entirely. Henrik Brandt knows and is furious. The deal is still small — "
            "but growing."
        ),
        player_impact="Captains who carry Iron Point ore to Jade Port earn standing with both Yaa and Wu. Captains who carry Ironhaven iron lose nothing — but they're supporting the old order.",
    ),
    CrossPortRelationship(
        "ih_forge_master", "Henrik Brandt", "ironhaven",
        "ip_foreman_kofi", "Foreman Kofi Mensah", "iron_point",
        network="merchant", disposition="rival",
        description=(
            "The bitterest trade rivalry on the seas. Henrik called Iron Point ore "
            "'unrefined swamp metal.' Kofi has an assay report proving his ore "
            "outgrades Ironhaven's refined product. The report is a weapon waiting "
            "to be deployed. When it drops, the iron market will never be the same."
        ),
        player_impact="Captains are CHOOSING SIDES whether they know it or not. Who you buy iron from signals your alliance. Both men remember.",
    ),

    # === The Tea-Medicine Circuit ===
    CrossPortRelationship(
        "tp_sigrid", "Sigrid Halvdan", "thornport",
        "dg_tea_merchant_liu", "Tea Merchant Liu", "dragons_gate",
        network="merchant", disposition="professional",
        description=(
            "Two tea experts on opposite sides of the world. Sigrid blends northern "
            "water tea at Thornport; Liu ages volcanic clay tea at Dragon's Gate. "
            "They've exchanged samples through trading captains and developed a "
            "mutual respect that neither culture would normally allow. Sigrid sailed "
            "the Monsoon Shortcut once, partly for tea buying, partly to meet Farouk."
        ),
        player_impact="Captains who carry tea between the North Atlantic and East Indies earn double reputation — both tea merchants track your reliability.",
    ),
    CrossPortRelationship(
        "ei_head_herbalist", "Herbalist Sera", "ember_isle",
        "sw_dr_halvorsen", "Dr. Halvorsen", "stormwall",
        network="merchant", disposition="allied",
        description=(
            "A medicine alliance across the entire Known World. Sera produces "
            "volcanic compounds at Ember Isle; Halvorsen produces northern herb "
            "cures at Stormwall. They've been exchanging recipes and ingredients "
            "through captains, and the compounds each has developed using the "
            "other's ingredients are better than either could make alone."
        ),
        player_impact="Medicine runs between Ember Isle and Stormwall are the most morally rewarding trade in the game. Both healers pay premium and remember captains who carry medicine.",
    ),

    # === The Rum Pipeline ===
    CrossPortRelationship(
        "pc_old_cassius", "Old Cassius", "palm_cove",
        "sw_quartermaster", "Quartermaster Maren", "stormwall",
        network="merchant", disposition="allied",
        description=(
            "Cassius's rum reaches Stormwall's garrison through Chioma's contracts "
            "and Maren's supply system. The soldiers love it. Maren buys above market "
            "because morale is a strategic asset. Cassius doesn't know his rum keeps "
            "a fortress functioning. He'd be delighted if he did."
        ),
        player_impact="Rum from Palm Cove to Stormwall is a reliable, well-paying route. Both ends remember captains who keep the pipeline flowing.",
    ),

    # === The Spice Power Struggle ===
    CrossPortRelationship(
        "am_yasmin", "Yasmin al-Nadir", "al_manar",
        "mr_spice_trader_priya", "Priya Sundaram", "monsoon_reach",
        network="merchant", disposition="rival",
        description=(
            "The Spice Mother of Al-Manar vs. the practical factor of Monsoon Reach. "
            "Yasmin wants to set global spice prices from Al-Manar's Bazaar. Priya "
            "sells to everyone at market rate and doesn't care about prestige. "
            "Yasmin considers Priya's neutrality an insult. Priya considers Yasmin's "
            "pricing a monopoly attempt."
        ),
        player_impact="Captains who buy spice at Monsoon Reach and sell at Al-Manar are playing both sides. Yasmin notices. Priya doesn't care — which is why Yasmin resents her.",
    ),

    # === The Silk Rivalry ===
    CrossPortRelationship(
        "slh_silk_merchant_feng", "Merchant Feng", "silk_haven",
        "jp_master_chen", "Kiln Master Chen", "jade_port",
        network="merchant", disposition="rival",
        description=(
            "Silk vs. porcelain — the eternal debate, played out through commerce. "
            "Feng wants silk to outsell porcelain in Western markets. Chen considers "
            "porcelain the superior art and silk merely... decorative. Their trade "
            "competition drives prices, quality, and a rivalry that's been running "
            "for longer than either man has been alive."
        ),
        player_impact="Captains carrying silk and porcelain together are balancing a cultural war in their hold. Both merchants track which you sell more of.",
    ),
]


# =========================================================================
# TAVERN INTELLIGENCE NETWORK
# =========================================================================
# The tavern keepers talk to each other through the captains who visit.
# A rumor in Porto Novo reaches Al-Manar in a week. Information is the
# invisible cargo that every ship carries.

TAVERN_NETWORK: list[CrossPortRelationship] = [
    CrossPortRelationship(
        "pn_old_enzo", "Old Enzo", "porto_novo",
        "am_old_farouk", "Old Farouk", "al_manar",
        network="tavern", disposition="personal",
        description=(
            "The oldest friendship in the tavern network. Enzo and Farouk have been "
            "exchanging gossip through visiting captains for thirty years. They argue "
            "about whether rum or tea is the superior social lubricant. Neither has "
            "conceded. The argument IS the friendship. Between them, they know "
            "everything happening in the Mediterranean."
        ),
        player_impact="Tell Enzo a rumor and Farouk hears it within a week. Tell Farouk and Enzo knows by next tide. The Mediterranean has no secrets between these two men.",
    ),
    CrossPortRelationship(
        "cr_mama_lucia", "Mama Lucia", "corsairs_rest",
        "sn_mama_smoke", "Mama Smoke", "spice_narrows",
        network="tavern", disposition="personal",
        description=(
            "Two mothers feeding the underworld's children. Mama Lucia in the "
            "Mediterranean cove, Mama Smoke in the Eastern cave — both providing "
            "the only warmth in lawless places. They've never met but they know OF "
            "each other through captains who've eaten at both tables. Each considers "
            "the other a sister in service."
        ),
        player_impact="Captains who are welcomed at both shadow kitchens are trusted by the underworld's most neutral institutions. Mama Lucia asks about Mama Smoke; Mama Smoke asks about Mama Lucia. Your answers shape their trust.",
    ),
    CrossPortRelationship(
        "pc_mama_joy", "Mama Joy", "palm_cove",
        "sh_yusuf", "Yusuf Diallo", "sun_harbor",
        network="tavern", disposition="allied",
        description=(
            "The Gold Coast's hospitality axis. Mama Joy's rum and Yusuf's cooking "
            "represent the Compact's philosophy in edible form: feed first, business "
            "later. They exchange recipes through captains and argue about whether "
            "rum or stew is the more important meal component. Yusuf says stew. "
            "Mama Joy laughs until she cries."
        ),
        player_impact="Captains welcomed at both tables carry the Gold Coast's trust. Refuse Mama Joy's rum or Yusuf's first plate, and the coast hears about it.",
    ),
    CrossPortRelationship(
        "ci_neutrality_keeper", "Mother Ko", "crosswind_isle",
        "pn_old_enzo", "Old Enzo", "porto_novo",
        network="tavern", disposition="professional",
        description=(
            "Mother Ko is the tavern network's neutral hub. Every tavern keeper "
            "trusts her because Crosswind Isle is neutral ground. She hears everything "
            "and filters it — sharing trade intelligence freely but never revealing "
            "personal information. Enzo respects this discipline. He wishes he had it."
        ),
        player_impact="Mother Ko knows what every tavern keeper knows. High standing with her is effectively high standing with the entire network.",
    ),
    CrossPortRelationship(
        "sb_rosa", "Rosa Carvalho", "silva_bay",
        "sw_ingrid", "Ingrid Norum", "stormwall",
        network="tavern", disposition="personal",
        description=(
            "Northern solidarity. Rosa lost her husband to the Smuggler's Run; "
            "Ingrid lost hers on Stormwall patrol. Two women who kept working because "
            "the people around them needed them. They've never met but exchange "
            "messages through northern trade captains. Short messages. Direct. "
            "The way northern women communicate."
        ),
        player_impact="Captains who are trusted at both the Dry Dock and the Watchtower carry a northern credibility that opens doors in the Atlantic.",
    ),
    CrossPortRelationship(
        "ta_cook_hine", "Cook Hine", "typhoon_anchorage",
        "ei_spring_keeper", "Spring Keeper Olo", "ember_isle",
        network="tavern", disposition="personal",
        description=(
            "Two women who keep fires burning in impossible conditions. Hine's "
            "volcanic grill at Typhoon Anchorage and Olo's sacred hot springs at "
            "Ember Isle — both powered by the earth's heat, both tended by women "
            "who consider the fire a sacred duty. They exchange herbs and techniques "
            "through South Seas trading canoes."
        ),
        player_impact="Captains who visit both carry the South Seas' deepest cultural connection — the fire-keepers' respect.",
    ),
]


# =========================================================================
# BROKER RIVALRY CHAIN
# =========================================================================
# The brokers are in direct competition for the best captains.

BROKER_NETWORK: list[CrossPortRelationship] = [
    CrossPortRelationship(
        "pn_broker_reis", "Fernanda Reis", "porto_novo",
        "am_broker_tariq", "Tariq Sayed", "al_manar",
        network="broker", disposition="rival",
        description=(
            "The Alliance's internal broker war. Fernanda controls Porto Novo's "
            "contract desk — the established center. Tariq wants Al-Manar's desk "
            "to replace it. He's courting Silk Circle traders for exclusive deals "
            "that bypass Porto Novo. If he succeeds, Fernanda loses the Alliance's "
            "best contracts. She knows. She's counter-bidding."
        ),
        player_impact="Captains are currency in the Fernanda-Tariq war. Working with one gets you better contracts there but signals disloyalty to the other. Playing both is possible but risky.",
    ),
    CrossPortRelationship(
        "pn_broker_reis", "Fernanda Reis", "porto_novo",
        "sb_broker_ana", "Ana Sousa", "silva_bay",
        network="broker", disposition="professional",
        description=(
            "Fernanda offered Ana a position at Porto Novo's desk. Ana turned it "
            "down to stay in Silva Bay. Fernanda respects this — it's the kind of "
            "loyalty she understands. They exchange referrals: Fernanda sends captains "
            "who need ships to Ana; Ana sends captains who need contracts to Fernanda."
        ),
        player_impact="Ana and Fernanda work as a pipeline. Completing contracts from one earns credibility with the other. A quiet alliance that benefits captains who notice it.",
    ),
    CrossPortRelationship(
        "mr_broker_kamala", "Kamala Nair", "monsoon_reach",
        "sh_broker_fatou", "Fatou Ndiaye", "sun_harbor",
        network="broker", disposition="allied",
        description=(
            "The bridge brokers. Kamala speaks four languages and trades with every "
            "bloc. Fatou is the Gold Coast's rising star. Together, they've created "
            "a contract network that connects the Gold Coast to the East Indies "
            "without going through the Mediterranean. This terrifies Porto Novo."
        ),
        player_impact="Captains who work the Kamala-Fatou route are building the future of trade. Both reward loyalty with increasingly premium contracts.",
    ),
    CrossPortRelationship(
        "slh_broker_chang", "Broker Chang", "silk_haven",
        "pn_broker_reis", "Fernanda Reis", "porto_novo",
        network="broker", disposition="professional",
        description=(
            "East meets West. Chang sells silk by story; Fernanda sells contracts by "
            "numbers. They coordinate on luxury shipments — Chang provides the product "
            "narrative, Fernanda provides the buyer network. Neither admits they need "
            "the other. Both do."
        ),
        player_impact="Luxury captains who carry silk from Chang and sell through Fernanda's network earn premium at both ends. The silk-to-silver pipeline.",
    ),
    CrossPortRelationship(
        "ct_broker_ariki", "Broker Ariki", "coral_throne",
        "ei_broker_tia", "Broker Tia", "ember_isle",
        network="broker", disposition="allied",
        description=(
            "The Coral Crown's internal contract network. Ariki handles trade "
            "at the Throne; Tia handles exports from Ember Isle. Together, they "
            "package South Seas goods — pearls, medicines, dyes — as a curated "
            "offering that commands premium in every Western market."
        ),
        player_impact="South Seas captains who work with both brokers get access to the Crown's best goods. The package deal is more valuable than the individual parts.",
    ),
    CrossPortRelationship(
        "cr_ghost", "Ghost", "corsairs_rest",
        "sn_ghost_broker", "The Ghost Broker", "spice_narrows",
        network="broker", disposition="allied",
        description=(
            "The shadow pipeline. Ghost moves the Crimson Tide's cargo from "
            "Corsair's Rest; the Ghost Broker posts Monsoon Syndicate contracts "
            "at Spice Narrows. Between them, the underworld's logistics network "
            "spans the entire Known World. They've never met in person. They may "
            "be the same person. Nobody knows."
        ),
        player_impact="Captains who work both shadow brokers are deep in the underworld. The smuggling contracts get better — and the danger multiplies.",
    ),
]


# =========================================================================
# INSPECTOR FRATERNITY
# =========================================================================
# The inspectors have their own professional network.

INSPECTOR_NETWORK: list[CrossPortRelationship] = [
    CrossPortRelationship(
        "pn_inspector_salva", "Inspector Salva", "porto_novo",
        "am_inspector_zara", "Inspector Zara", "al_manar",
        network="inspector", disposition="professional",
        description=(
            "Former partners who split over method. Salva hunts smugglers — follow "
            "the cargo, find the crime. Zara hunts frauds — follow the quality, "
            "find the lie. They respect each other enormously and couldn't work "
            "together because their obsessions pointed in different directions. "
            "They still exchange case notes by letter."
        ),
        player_impact="Captains flagged by one are watched by the other. Clean records at Porto Novo earn faster processing at Al-Manar. Fraud at Al-Manar triggers extra inspection at Porto Novo.",
    ),
    CrossPortRelationship(
        "jp_inspector_zhao", "Inspector Zhao Min", "jade_port",
        "slh_inspector_yuki", "Inspector Yuki", "silk_haven",
        network="inspector", disposition="professional",
        description=(
            "Trained under the same master — the legendary quality inspector "
            "whose name neither will share. They competed fiercely as students and "
            "now respect each other as the two finest inspectors in the East. "
            "They exchange notes on new counterfeiting techniques by letter. "
            "The letters are, themselves, works of precision."
        ),
        player_impact="The Eastern inspection fraternity is tighter than the Western one. Counterfeit goods detected at Jade Port trigger alerts at Silk Haven, and vice versa.",
    ),
    CrossPortRelationship(
        "ih_inspector_kross", "Inspector Kross", "ironhaven",
        "sw_inspector_berg", "Inspector Berg", "stormwall",
        network="inspector", disposition="allied",
        description=(
            "The Iron Pact's enforcement axis. Kross tracks weapons serial marks; "
            "Berg tracks security threats. Together, they maintain the most comprehensive "
            "weapons tracking system in the Known World. Every blade, every barrel, "
            "every crate of iron that leaves the North Atlantic is documented."
        ),
        player_impact="Weapons diverted from legitimate channels are traced through the Kross-Berg system. Captains who sell Pact weapons to pirates are caught by the chain, not by luck.",
    ),
    CrossPortRelationship(
        "dg_weapons_inspector_sun", "Inspector Sun", "dragons_gate",
        "ih_inspector_kross", "Inspector Kross", "ironhaven",
        network="inspector", disposition="professional",
        description=(
            "Opposite ends of the weapons pipeline. Kross logs every weapon that "
            "leaves Ironhaven. Sun logs every weapon that enters the Eastern strait. "
            "The gap between their logs is where the smugglers operate. They've been "
            "narrowing the gap for years. The smugglers feel it."
        ),
        player_impact="The Sun-Kross pipeline is the reason weapons smuggling to the East Indies is the highest-risk run in the game. Their combined intelligence is formidable.",
    ),
    CrossPortRelationship(
        "pn_inspector_salva", "Inspector Salva", "porto_novo",
        "dg_weapons_inspector_sun", "Inspector Sun", "dragons_gate",
        network="inspector", disposition="respected",
        description=(
            "The two legends. Salva — relentless, never bribed, brother killed by "
            "smuggled powder. Sun — zero unauthorized passages in fifteen years, "
            "found weapons dissolved in acid. They've never met but each considers "
            "the other the standard they measure themselves against. The smuggling "
            "world fears both equally."
        ),
        player_impact="Captains with clean records at BOTH Porto Novo and Dragon's Gate carry the gold standard of inspection credibility. The two hardest stamps to earn — and the most valuable.",
    ),
]


# =========================================================================
# Lookup helpers
# =========================================================================

ALL_CROSS_PORT_RELATIONSHIPS: list[CrossPortRelationship] = (
    MERCHANT_RELATIONSHIPS + TAVERN_NETWORK + BROKER_NETWORK + INSPECTOR_NETWORK
)


def get_network_relationships(network: str) -> list[CrossPortRelationship]:
    """Get all relationships for a given network type."""
    return [r for r in ALL_CROSS_PORT_RELATIONSHIPS if r.network == network]


def get_relationships_for_npc(npc_id: str) -> list[CrossPortRelationship]:
    """Get all cross-port relationships involving a specific NPC."""
    return [r for r in ALL_CROSS_PORT_RELATIONSHIPS
            if r.npc_a_id == npc_id or r.npc_b_id == npc_id]


def get_relationships_for_port(port_id: str) -> list[CrossPortRelationship]:
    """Get all cross-port relationships involving NPCs at a specific port."""
    return [r for r in ALL_CROSS_PORT_RELATIONSHIPS
            if r.npc_a_port == port_id or r.npc_b_port == port_id]
