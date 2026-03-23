"""Port institutions — East Indies + South Seas continuation.

Split from port_institutions.py for maintainability (the main file exceeded
4000 lines). Same dataclasses, same patterns, imported by the main module.

Ports in this file:
  East Indies: Silk Haven, Crosswind Isle, Dragon's Gate, Spice Narrows
  South Seas: Ember Isle, Typhoon Anchorage, Coral Throne
"""

from portlight.content.port_institutions import (
    PortInstitution,
    PortInstitutionalProfile,
    PortNPC,
)


# =========================================================================
# SILK HAVEN — The Loom Quarter
# =========================================================================

_SILK_HAVEN_NPCS = [
    PortNPC(
        id="slh_harbor_jun", name="Harbor Keeper Jun", title="Harbor Keeper",
        port_id="silk_haven", institution="harbor_master", personality="graceful",
        description="A man who manages ships the way a weaver manages threads — each vessel placed precisely. Jun runs Silk Haven's small harbor with an aesthete's eye: berths arranged to look beautiful from the Loom Quarter above.",
        agenda="Elegance. Jun wants Silk Haven's harbor to reflect the silk it exports. Every arriving ship is an opportunity for visual composition.",
        greeting_neutral="\"Welcome to Silk Haven. Your berth is port-side, third position. Please keep your rigging tidy.\"",
        greeting_friendly="\"Captain! Inner quay, first position — where the morning light catches your sails. I've been saving it.\"",
        greeting_hostile="\"Outer anchorage. Your vessel's condition does not meet the harbor's aesthetic standards.\"",
        rumor="Jun once rearranged every ship in harbor because a junk's crimson sails clashed with a brig's blue hull. The captains were baffled. The Loom Quarter artists applauded.",
        relationship_notes={"slh_grand_weaver": "He serves her vision. The harbor is the first thread visitors see.", "slh_lady_sato": "Coordinates with the magistrate. Prefers coordinating with the view.", "slh_master_ink": "Ink's studio overlooks the harbor. Jun arranges ships as compositions for Ink to paint.", "slh_silk_merchant_feng": "Feng needs fast loading. Jun needs beauty. They compromise.", "slh_inspector_yuki": "Yuki inspects inside. Jun inspects outside. Non-overlapping aesthetics.", "slh_broker_chang": "Chang brings captains. Jun presents the harbor."},
    ),
    PortNPC(
        id="slh_grand_weaver", name="Grand Weaver Seo-yeon", title="Guild Matriarch",
        port_id="silk_haven", institution="exchange", personality="proud",
        description="Fingers that have woven silk for fifty years without a single broken thread. Seo-yeon is the Silk Weavers' Guild matriarch — her patterns are family secrets passed down for centuries. She presents bolts folded, never rolled, because rolling insults the weaver's art.",
        agenda="Silk's supremacy. Seo-yeon believes silk is the highest art form. Her rivalry with Chen Bai in Jade Port is personal: he called silk 'decorated thread.' She responded with a tapestry depicting the Kiln Masters' ancestors as monkeys. It still hangs in the Loom Quarter.",
        greeting_neutral="\"You wish to see the silk? Come. Touch nothing until I have unfolded the bolt. The weave speaks first.\"",
        greeting_friendly="\"Captain — I have woven something no living eye has seen. For trusted friends only. Come to the inner loom. Bring clean hands.\"",
        greeting_hostile="\"Standard bolts at posted prices. The master weaves are not for your hands. The silk decides its buyer.\"",
        rumor="Seo-yeon's eldest daughter wove a bolt she declared 'adequate.' In the Guild, 'adequate' from the Grand Weaver is the highest praise. The daughter wept with pride.",
        relationship_notes={"slh_harbor_jun": "He arranges ships to complement the Quarter. She approves.", "slh_lady_sato": "Allies. Sato protects the Guild; Seo-yeon provides the art.", "slh_master_ink": "Fellow artists. They disagree about everything and respect each other deeply because of it.", "slh_silk_merchant_feng": "He sells her silk. She tolerates commerce as a necessary evil.", "slh_inspector_yuki": "Sacred work. Yuki protects the Grand Weaver's mark.", "slh_broker_chang": "The only merchant she doesn't despise. He presents silk as art."},
    ),
    PortNPC(
        id="slh_lady_sato", name="Lady Sato Hana", title="Circle Magistrate",
        port_id="silk_haven", institution="governor", personality="subtle",
        description="Silk robes in patterns so complex they appear to move, and a political mind that weaves with equal intricacy. Lady Sato governs Silk Haven as the Circle's magistrate — less imperious than Jade Port's Mei, more culturally engaged.",
        agenda="The Guild's independence within the Circle. Sato wants Silk Haven to remain artistically sovereign — not subordinate to Jade Port. She supports the rivalry with Chen because decentralization protects independence.",
        greeting_neutral="\"Silk Haven welcomes those who appreciate craft. Our silk speaks for itself — as does our hospitality.\"",
        greeting_friendly="\"Captain — you return with appreciation in your eyes. That is the only currency we value above silver.\"",
        greeting_hostile="\"Your visit is noted. Standard trade is available. The inner Quarter is closed to you today.\"",
        rumor="Lady Sato once wore a robe to a meeting with Jade Port that contained a pattern depicting their porcelain as inferior. Chen pretended not to notice. Everyone else did.",
        relationship_notes={"slh_harbor_jun": "He serves the aesthetic; she serves the politics.", "slh_grand_weaver": "Symbiotic. Sato protects; Seo-yeon creates.", "slh_master_ink": "Commissions his calligraphy for diplomacy.", "slh_silk_merchant_feng": "Monitors his trade to protect the Guild.", "slh_inspector_yuki": "Values her quality enforcement.", "slh_broker_chang": "He operates within her parameters."},
    ),
    PortNPC(
        id="slh_master_ink", name="Master Ink", title="Calligrapher",
        port_id="silk_haven", institution="tavern", personality="eccentric",
        description="Nobody uses his real name. He runs the Brush and Bowl — a calligraphy studio that serves rice wine, where sailors watch him paint while they drink. His calligraphy is the most beautiful in the East. His social skills are the worst.",
        agenda="Perfection of line. Ink doesn't care about trade or politics. He paints trade agreements that Sato sends to other ports — his calligraphy turns contracts into art.",
        greeting_neutral="He doesn't look up. After a long pause: \"...Wine is there. Sit quietly or leave. I'm working.\"",
        greeting_friendly="He looks up. A rare event. \"Ah. You. Sit. I painted something yesterday and your face was in it. I don't know why. Look.\"",
        greeting_hostile="Complete silence. He turns his back. The wine is still available.",
        rumor="Master Ink painted a scroll for Scarlet Ana — the only pirate who sat in his studio. She didn't move for four hours. She paid in pearls. The scroll hangs in Corsair's Rest. It's the most valuable object in the cove.",
        relationship_notes={"slh_harbor_jun": "Jun arranges ships for Ink to paint. Neither has discussed this.", "slh_grand_weaver": "Fellow artists who disagree about everything. The disagreement IS the respect.", "slh_lady_sato": "She commissions his calligraphy. He ignores her politics.", "slh_silk_merchant_feng": "Once asked Ink for a logo. Was stared at for 30 seconds. Never asked again.", "slh_inspector_yuki": "She visits on difficult days. He pours wine. Neither speaks.", "slh_broker_chang": "Invisible to each other. By mutual choice."},
    ),
    PortNPC(
        id="slh_silk_merchant_feng", name="Merchant Feng", title="Silk Factor",
        port_id="silk_haven", institution="shipyard", personality="commercial",
        description="The only person in Silk Haven who thinks about silk in terms of bales and margins. Feng manages silk exports — grading, packaging, shipping. The weavers consider him necessary. He considers himself unappreciated.",
        agenda="Volume. Feng wants more silk sold at higher margins. He respects the Guild's quality but wishes they'd produce faster. Art doesn't scale, which is his permanent frustration.",
        greeting_neutral="\"Silk? Guild-marked, Seo-yeon approved. The finest in the Known World. The price reflects that.\"",
        greeting_friendly="\"Captain! A new collection just cleared the Guild. Three bolts of a pattern not seen in fifty years. I held one for you.\"",
        greeting_hostile="\"Standard export bolts. Posted prices. The collector pieces are not available for your standing.\"",
        rumor="Feng once tried to hire weavers from a rival province to increase production. Seo-yeon found out and threatened to rescind his license. He never tried again. He still mutters about 'scalability.'",
        relationship_notes={"slh_harbor_jun": "They compromise between fast loading and beautiful placement.", "slh_grand_weaver": "She tolerates him. He funds the Guild. Necessary, not warm.", "slh_lady_sato": "She monitors his trade. He complies.", "slh_master_ink": "Once asked for a logo. Was stared at. Never again.", "slh_inspector_yuki": "She checks his lots. He keeps them genuine.", "slh_broker_chang": "Commercial allies. Different markets, shared margins."},
    ),
    PortNPC(
        id="slh_inspector_yuki", name="Inspector Yuki", title="Silk Inspector",
        port_id="silk_haven", institution="customs", personality="meticulous",
        description="Can identify counterfeit silk by touch alone — thread count, weave tension, dye saturation, all through trained fingertips. Protects the Guild's marks from forgery the way Zhao in Jade Port protects the Kiln Masters'.",
        agenda="Authenticity. Every bolt must be genuine. Counterfeit silk insults the weaver. Yuki takes both offenses personally.",
        greeting_neutral="\"All silk exports require authentication. I inspect by touch — it takes longer but misses nothing.\"",
        greeting_friendly="\"Captain — your shipments are always genuine. Quick authentication. You respect the Guild's work.\"",
        greeting_hostile="\"Full authentication. Every bolt, every thread. I've found patterns in your route's shipments that concern me.\"",
        rumor="Yuki and Zhao Min in Jade Port trained under the same master. They now respect each other as the two finest inspectors in the East, and exchange notes by letter on new counterfeiting techniques.",
        relationship_notes={"slh_harbor_jun": "Non-overlapping domains.", "slh_grand_weaver": "Sacred work — protects Seo-yeon's mark.", "slh_lady_sato": "Values her quality enforcement.", "slh_master_ink": "Visits his studio on hard days. Wine. Silence.", "slh_silk_merchant_feng": "Checks his lots. Self-interest aligned with quality.", "slh_broker_chang": "Her seal authenticates his exports."},
    ),
    PortNPC(
        id="slh_broker_chang", name="Broker Chang", title="Silk Broker",
        port_id="silk_haven", institution="broker", personality="refined",
        description="A broker who speaks the language of art to sell the products of commerce. Chang presents silk as acquisition — each bolt with provenance, history, and meaning. He prices by story, not weight.",
        agenda="Premium positioning. A bolt with a thousand-year pattern costs more than one with fifty years, regardless of thread count.",
        greeting_neutral="\"Each bolt has a history — the pattern, the weaver, the tradition. Shall I tell it?\"",
        greeting_friendly="\"Captain! Seo-yeon wove this personally — her hands, her pattern, her mark. This hasn't happened in three years.\"",
        greeting_hostile="\"Standard bolts through Merchant Feng. The curated collection requires a different relationship.\"",
        rumor="Chang sold a single bolt for more silver than most captains earn in a season. The collector didn't ask the price — he asked the story. Chang told it for an hour. The collector paid without negotiating.",
        relationship_notes={"slh_harbor_jun": "Aesthetics aligned.", "slh_grand_weaver": "The only merchant she doesn't despise.", "slh_lady_sato": "He operates within her parameters.", "slh_master_ink": "Invisible to each other. By mutual choice.", "slh_silk_merchant_feng": "Different markets, shared margins.", "slh_inspector_yuki": "Her seal authenticates his premium."},
    ),
]

_SILK_HAVEN_INSTITUTIONS = [
    PortInstitution(id="slh_harbor", name="The Arranged Harbor", port_id="silk_haven", institution_type="harbor_master",
        description="A small harbor where berths are assigned for visual composition. Ships are part of the Loom Quarter's view.",
        function="Aesthetic-first berthing. Function serves form.", political_leaning="Silk Circle, artistically.", npc_id="slh_harbor_jun"),
    PortInstitution(id="slh_loom", name="The Loom Quarter", port_id="silk_haven", institution_type="exchange",
        description="A district where a hundred looms never stop. Silk in thousand-year patterns. Green tea steam and the clack of threads.",
        function="Silk production, Guild marking, pattern guardianship.", political_leaning="Guild sovereignty.", npc_id="slh_grand_weaver"),
    PortInstitution(id="slh_court", name="The Silk Court", port_id="silk_haven", institution_type="governor",
        description="A hall draped in silk — walls, ceiling, cushions. Every surface woven. Sato governs from within the art.",
        function="Political governance, Guild protection, Circle diplomacy.", political_leaning="Artistic independence.", npc_id="slh_lady_sato"),
    PortInstitution(id="slh_brush", name="The Brush and Bowl", port_id="silk_haven", institution_type="tavern",
        description="A calligraphy studio that serves rice wine. Sailors watch Ink paint. Beauty changes how they see the world.",
        function="Social hub through art. Ink's calligraphy turns contracts into art.", political_leaning="Above politics.", npc_id="slh_master_ink"),
    PortInstitution(id="slh_warehouse", name="The Silk Warehouse", port_id="silk_haven", institution_type="shipyard",
        description="Climate-controlled silk storage. Humidity, temperature, light managed. Feng runs it with Guild-demanded precision.",
        function="Export packaging. The practical bridge between loom and ship.", political_leaning="Commercial.", npc_id="slh_silk_merchant_feng"),
    PortInstitution(id="slh_touch", name="The Touch Room", port_id="silk_haven", institution_type="customs",
        description="A silent room where Yuki inspects silk by touch. No instruments — trained fingertips only.",
        function="Silk authentication. Thread count, tension, dye saturation by hand.", political_leaning="Quality enforcement.", npc_id="slh_inspector_yuki"),
    PortInstitution(id="slh_story", name="The Story Room", port_id="silk_haven", institution_type="broker",
        description="A curtained alcove where Chang tells each bolt's story. Buyers don't negotiate. They listen.",
        function="Premium brokering by narrative. Story, not weight.", political_leaning="Artistic commerce.", npc_id="slh_broker_chang"),
]

SILK_HAVEN_PROFILE = PortInstitutionalProfile(
    port_id="silk_haven", governor_title="Circle Magistrate",
    power_structure="Silk Haven is governed by art. Seo-yeon's Guild produces the silk. Sato protects independence from Jade Port. Master Ink creates beauty that transcends commerce. Jun arranges the harbor as poetry. Chang sells meaning. Yuki guards authenticity. Feng moves volume and resents the pace of art.",
    internal_tension="Surface: Silk Haven vs. Jade Port — the monkey tapestry vs. 'decorated thread.' Sato encourages the rivalry because decentralization protects independence. Internal: Feng vs. the Guild on scaling production. Deep thread: Yuki and Zhao (Jade Port) trained under the same master — the inspectors are closer to each other than to their own ports. Master Ink painted a scroll for Scarlet Ana that hangs in Corsair's Rest — art connecting the pirate cove to the silk capital.",
    institutions=_SILK_HAVEN_INSTITUTIONS, npcs=_SILK_HAVEN_NPCS,
)


# =========================================================================
# Export all profiles from this file
# =========================================================================


# =========================================================================
# CROSSWIND ISLE — The Free Port
# =========================================================================

_CROSSWIND_ISLE_NPCS = [
    PortNPC(
        id="ci_captain_council", name="The Captain's Table", title="Governing Council",
        port_id="crosswind_isle", institution="governor", personality="democratic",
        description="Not a person — a rotating council of five captains elected monthly by whoever happens to be in harbor. No permanent government, no bureaucracy, no taxes beyond the docking fee. The only rule: no one rules. A bell is rung when votes are needed. Whoever shows up, votes.",
        agenda="Freedom. The Captain's Table exists to prevent governance, not to provide it. They settle disputes, maintain the dock, and ensure no nation ever claims the isle. That's it.",
        greeting_neutral="\"Crosswind Isle welcomes all flags. Dock where you find space. The only rule: no one claims authority here. Understood?\"",
        greeting_friendly="\"Captain — your voice is welcome at the Table this month. Stay for the vote. Your experience matters.\"",
        greeting_hostile="\"You may dock. You may trade. You may NOT attempt to impose order, recruit for factions, or claim territory. We've thrown out better than you.\"",
        rumor="Someone tried to claim the isle for an eastern dynasty last year. By morning, every captain in harbor had their guns trained on his ship. He left before breakfast. The Table didn't even need to vote.",
        relationship_notes={"ci_dock_master_tao": "Tao keeps the dock working. The Table keeps governance from happening.", "ci_every_merchant": "Every Merchant runs the exchange. The Table lets them.", "ci_neutrality_keeper": "Mother Ko enforces the one rule. The Table backs her.", "ci_money_changer_hassan": "Hassan changes currency. The Table doesn't regulate it.", "ci_inspector_nobody": "No customs. The Table considers this a feature.", "ci_broker_various": "Brokers come and go. The Table doesn't license them."},
    ),
    PortNPC(
        id="ci_dock_master_tao", name="Dock Master Tao", title="Dock Master",
        port_id="crosswind_isle", institution="harbor_master", personality="efficient",
        description="The only permanent employee of Crosswind Isle — Tao has maintained the dock for twelve years through elected councils, trade wars, and one attempted invasion. He assigns berths by first-come-first-served and considers this the purest form of justice.",
        agenda="A working dock. Tao doesn't care about politics, factions, or who's fighting whom. He cares about moorings, tides, and keeping the dock from falling into the sea.",
        greeting_neutral="\"Berth's open. Tie up, stay or go. First come, first served. Nobody gets priority here.\"",
        greeting_friendly="\"Captain! Good to see you again. Berth six — the mooring's been fixed since last time. I remembered your complaint.\"",
        greeting_hostile="\"You can dock. But I'm watching your crew. Last time they left a mess. This time, you clean it or you pay.\"",
        rumor="Tao once repaired the entire dock by himself during a typhoon because nobody else would help. It took four days. The dock held. He doesn't talk about it because he considers dock maintenance self-explanatory.",
        relationship_notes={"ci_captain_council": "The Table comes and goes. Tao stays. That's the arrangement.", "ci_every_merchant": "They share dock space. Professional.", "ci_neutrality_keeper": "Mother Ko maintains order. Tao maintains infrastructure. Both essential.", "ci_money_changer_hassan": "Hassan's table is on Tao's dock. They've been neighbors for a decade.", "ci_inspector_nobody": "Nobody inspects. Tao doesn't mind.", "ci_broker_various": "The brokers need dock access. Tao provides it."},
    ),
    PortNPC(
        id="ci_every_merchant", name="Every Merchant", title="Exchange Keeper",
        port_id="crosswind_isle", institution="exchange", personality="chaotic",
        description="Not a single person — a rotating cast of merchants who set up stalls on the dock every morning and take them down every night. No permanent exchange, no posted prices, no Guild marks. Crosswind Isle's 'exchange' is pure chaos: shouted prices, competing offers, and the only quality control is reputation.",
        agenda="Profit through chaos. The merchants like it this way — no regulation means no fees, no inspectors, and no restrictions. The good merchants thrive on reputation. The bad ones get shouted off the dock.",
        greeting_neutral="\"BUYING! SELLING! Everything at once! Name your price, Captain — someone here has what you need!\"",
        greeting_friendly="\"Captain! Good to see an honest face! Come to my stall — I have what you want before you know you want it!\"",
        greeting_hostile="\"...Your silver's good? Then your history doesn't matter here. That's the point of Crosswind Isle.\"",
        rumor="The merchants once collectively boycotted a captain who sold counterfeit spice. No Guild forced it — the merchants just stopped selling to him. He left within the day. Self-regulation by shame.",
        relationship_notes={"ci_captain_council": "The Table lets them trade. They let the Table pretend to govern.", "ci_dock_master_tao": "Professional. They share dock space.", "ci_neutrality_keeper": "Mother Ko keeps fights from escalating. The merchants appreciate this.", "ci_money_changer_hassan": "Essential — Hassan converts the dozen currencies that flow through.", "ci_inspector_nobody": "No inspection is the merchants' favorite policy.", "ci_broker_various": "The brokers formalize what the merchants shout. Different styles, same trades."},
    ),
    PortNPC(
        id="ci_neutrality_keeper", name="Mother Ko", title="Keeper of the Peace",
        port_id="crosswind_isle", institution="tavern", personality="iron",
        description="A massive woman who runs the Bell and Board — Crosswind Isle's only permanent tavern — and who enforces the isle's one rule with a voice that can stop a brawl at forty paces. Mother Ko doesn't care about your faction, your flag, or your grudge. Inside her tavern and within the isle's boundaries, you are NEUTRAL or you are GONE.",
        agenda="The rule. No one claims authority. No one fights about politics. No one recruits for factions on the isle. Mother Ko is the immune system — she identifies threats to neutrality and eliminates them with a word, a look, or if necessary, a thrown stool.",
        greeting_neutral="\"Welcome to the Bell and Board. All flags fly. All tongues speak. One rule: neutrality or the door. Drink?\"",
        greeting_friendly="\"Captain! Your table's empty — that means it's been too long. Sit. Drink. Tell me who's trying to ruin the world today.\"",
        greeting_hostile="\"You're welcome to drink. You're NOT welcome to start trouble. I've thrown out admirals and pirate kings. Don't test me.\"",
        rumor="Mother Ko once threw a Silk Circle official and an Iron Pact officer out of her tavern simultaneously — one through each door — because they were arguing about trade policy at the bar. She said, 'Take your politics to the sea. The isle doesn't serve it.' Neither came back. Both sent flowers.",
        relationship_notes={"ci_captain_council": "The Table enforces the rule politically. Mother Ko enforces it physically.", "ci_dock_master_tao": "Mutual respect. Two permanent fixtures on a transient isle.", "ci_every_merchant": "She stops fights from spilling into the market.", "ci_money_changer_hassan": "Hassan drinks quietly. She appreciates quiet drinkers.", "ci_inspector_nobody": "No customs means no arguments about customs. Mother Ko approves.", "ci_broker_various": "Brokers keep their voices down in her tavern. This is wisdom."},
    ),
    PortNPC(
        id="ci_money_changer_hassan", name="Hassan al-Farsi", title="Money Changer",
        port_id="crosswind_isle", institution="customs", personality="precise",
        description="Crosswind Isle has no customs — but it does have Hassan, who sits at a small table with scales, abacus, and stacks of every currency in the Known World. He converts Mediterranean silver to Eastern brass to Gold Coast cowries without blinking. He IS the customs system: not inspecting cargo but lubricating the twelve currencies that flow through.",
        agenda="Fair rates. Hassan's exchange rates are the most trusted in the East because he's survived fifteen years at Crosswind Isle by never cheating anyone. His table is the only institution on the isle that everyone — pirates, merchants, officials — trusts absolutely.",
        greeting_neutral="\"What currency are you carrying? I exchange all at fair rates. Posted on the board. No negotiation — the rate is the rate.\"",
        greeting_friendly="\"Captain! I've been tracking exchange rates for your route — you'll want to convert now. The eastern brass is strong this week.\"",
        greeting_hostile="\"I exchange currency for all. My rates don't change based on who you are. That's why I'm still alive after fifteen years.\"",
        rumor="Hassan keeps a personal ledger of every transaction he's ever made — fifteen years, twelve currencies, hundreds of thousands of exchanges. He says the ledger tells the story of the Known World's economy better than any market report. Nobody has seen it except him.",
        relationship_notes={"ci_captain_council": "They don't regulate him. He doesn't need regulation.", "ci_dock_master_tao": "Neighbors for a decade. Tao fixed Hassan's table once. Hassan never forgot.", "ci_every_merchant": "Essential — converts the dozen currencies flowing through.", "ci_neutrality_keeper": "Drinks quietly at Mother Ko's. She appreciates quiet.", "ci_inspector_nobody": "No inspection. Hassan's precision IS the quality control.", "ci_broker_various": "Brokers use his rates. He uses their volume. Symbiotic."},
    ),
    PortNPC(
        id="ci_inspector_nobody", name="(Nobody)", title="(No Customs)",
        port_id="crosswind_isle", institution="apothecary", personality="absent",
        description="Crosswind Isle has no customs inspector. This is deliberate. The absence is the policy. Where other ports have an inspector, Crosswind Isle has an empty chair with a sign: 'THIS SEAT INTENTIONALLY LEFT VACANT.' It's the isle's most photographed landmark.",
        agenda="None. The empty chair's agenda is being empty. This is, arguably, the most powerful statement any institution has ever made.",
        greeting_neutral="The chair is empty. A seagull sits on it. The seagull does not check your manifest.",
        greeting_friendly="The chair is empty. The sign has been polished recently. Someone cares.",
        greeting_hostile="The chair is still empty. Whatever you're carrying, nobody is checking it. That's the point.",
        rumor="Three different alliances have offered to station an inspector at Crosswind Isle. Each time, the Captain's Table voted unanimously to decline. The chair remains empty. The seagull remains.",
        relationship_notes={"ci_captain_council": "The Table voted for this vacancy. Three times.", "ci_dock_master_tao": "Tao built the chair. He's proud of it.", "ci_every_merchant": "The merchants' favorite institution is the one that doesn't exist.", "ci_neutrality_keeper": "Mother Ko considers the empty chair her best ally.", "ci_money_changer_hassan": "Hassan's precision is the only quality control needed.", "ci_broker_various": "No inspection means no delays. Brokers approve."},
    ),
    PortNPC(
        id="ci_broker_various", name="The Dock Brokers", title="Freelance Brokers",
        port_id="crosswind_isle", institution="broker", personality="competitive",
        description="Not one broker — a dozen freelancers who compete for contracts on the dock every morning. No licensing, no territory, no regulation. The best broker wins. Today it might be a Silk Circle agent; tomorrow a Gold Coast trader; next week a retired pirate. Crosswind Isle doesn't curate its brokers. It lets them fight.",
        agenda="Each broker has their own agenda. Collectively, they ensure that every cargo finds a buyer and every buyer finds a cargo — pure market efficiency through unregulated competition.",
        greeting_neutral="\"Captain! I have — \" \"No, THIS captain, MY contract is better — \" \"Ignore them both, I know the REAL prices — \" The dock brokers compete for your attention.",
        greeting_friendly="\"Captain! I saved this one for you — don't tell the others. Quick, before they notice.\"",
        greeting_hostile="\"...Even here, reputation matters. The best contracts go to the captains the brokers trust. You'll need to earn that.\"",
        rumor="The dock brokers once held an informal competition: who could broker the most contracts in a single day. The winner brokered seventeen. The runner-up brokered fifteen but argues that three of the winner's were technically the same contract repackaged. The debate continues.",
        relationship_notes={"ci_captain_council": "The Table doesn't license them. They prefer it that way.", "ci_dock_master_tao": "They need dock access. Tao provides it.", "ci_every_merchant": "The merchants shout; the brokers formalize. Different styles.", "ci_neutrality_keeper": "Mother Ko keeps broker arguments from becoming broker fights.", "ci_money_changer_hassan": "Brokers use Hassan's rates. Essential.", "ci_inspector_nobody": "No inspection means no delays. Brokers approve."},
    ),
]

_CROSSWIND_ISLE_INSTITUTIONS = [
    PortInstitution(id="ci_dock", name="The Free Dock", port_id="crosswind_isle", institution_type="harbor_master",
        description="First-come-first-served. No priority, no hierarchy. Tao maintains it. The democracy starts at the mooring.", function="Pure first-come berthing. Nobody gets priority.", political_leaning="Aggressively neutral.", npc_id="ci_dock_master_tao"),
    PortInstitution(id="ci_market", name="The Open Market", port_id="crosswind_isle", institution_type="exchange",
        description="Stalls set up every morning, taken down every night. Shouted prices, competing offers. Pure market chaos.", function="Unregulated exchange. Quality control by reputation only.", political_leaning="Anti-regulation.", npc_id="ci_every_merchant"),
    PortInstitution(id="ci_table", name="The Captain's Table", port_id="crosswind_isle", institution_type="governor",
        description="A round table at the dock where elected captains vote. No building. The government is a piece of furniture.", function="Preventing governance. Settling disputes. Maintaining the dock. That's all.", political_leaning="Anti-authority.", npc_id="ci_captain_council"),
    PortInstitution(id="ci_bell", name="The Bell and Board", port_id="crosswind_isle", institution_type="tavern",
        description="The only permanent building on the isle. Mother Ko's domain. The bell rings for votes and for last call.", function="Neutral ground enforced by Mother Ko. All flags, all tongues, one rule.", political_leaning="Neutrality as religion.", npc_id="ci_neutrality_keeper"),
    PortInstitution(id="ci_empty_chair", name="The Empty Chair", port_id="crosswind_isle", institution_type="apothecary",
        description="An empty chair with a sign: 'THIS SEAT INTENTIONALLY LEFT VACANT.' Where other ports have customs. The most powerful non-institution in the Known World.", function="Nothing. Deliberately. The absence IS the policy.", political_leaning="The absence of politics.", npc_id="ci_inspector_nobody"),
    PortInstitution(id="ci_exchange_table", name="Hassan's Table", port_id="crosswind_isle", institution_type="customs",
        description="A small table with scales, abacus, and every currency. Hassan converts twelve currencies without blinking. The only 'customs' Crosswind Isle needs.", function="Currency exchange. Fair rates, no negotiation. The rate is the rate.", political_leaning="Neutral by profession.", npc_id="ci_money_changer_hassan"),
    PortInstitution(id="ci_brokers", name="The Dock Scrum", port_id="crosswind_isle", institution_type="broker",
        description="A dozen freelance brokers competing on the dock every morning. No licensing, no territory. The best wins.", function="Unregulated brokering. Pure competition. Every cargo finds a buyer.", political_leaning="Market anarchy.", npc_id="ci_broker_various"),
]

CROSSWIND_ISLE_PROFILE = PortInstitutionalProfile(
    port_id="crosswind_isle", governor_title="Captain's Table",
    power_structure="Crosswind Isle has no permanent government — the Captain's Table rotates monthly. Tao maintains the dock. Mother Ko enforces neutrality. Hassan changes money. The merchants shout. The brokers compete. The customs chair is empty. It's the closest thing to anarchy that actually works.",
    internal_tension="The tension IS the system. Crosswind Isle works because everyone agrees on one thing: no one rules. The moment someone tries, the system activates — Mother Ko throws them out, the Table votes them down, and every captain in harbor trains their guns. The real vulnerability: what happens when the trade blocs get desperate enough to claim the isle by force? The Table has no navy. Mother Ko has a stool.",
    institutions=_CROSSWIND_ISLE_INSTITUTIONS, npcs=_CROSSWIND_ISLE_NPCS,
)


# =========================================================================
# DRAGON'S GATE — The Fortress Strait
# =========================================================================

_DRAGONS_GATE_NPCS = [
    PortNPC(
        id="dg_commander_zhang", name="Commander Zhang Wei", title="Gate Commander",
        port_id="dragons_gate", institution="governor", personality="absolute",
        description="A man whose authority is measured in chains — the harbor chains that can close the eastern strait in under a minute. Commander Zhang governs Dragon's Gate as both military commander and civil authority. His word is law, his chains are persuasion, and his fifteen-year record of zero unauthorized passages speaks for itself.",
        agenda="Control. Zhang controls the strait. Ships pass when he permits. Weapons do not pass — ever. His fortress exists to prevent armed escalation in the East Indies, and he considers every weapon that enters the strait a personal failure.",
        greeting_neutral="\"State your cargo. All weapons must be declared. Failure to declare is treated as hostile intent. These are the terms of passage.\"",
        greeting_friendly="\"Captain — your record is clean. Passage is granted. But I will still inspect the weapons hold. Protocol serves everyone.\"",
        greeting_hostile="\"Full inspection. Full chain deployment. Your ship will not leave this harbor until I am satisfied that no weapons pass through my strait.\"",
        rumor="The last captain who tried to run Zhang's chains is still chained to the seabed as a warning. Zhang considers this proportionate. The strait has been quiet ever since.",
        relationship_notes={"dg_harbor_captain_li": "His harbor officer. Runs the dock under Zhang's absolute authority.", "dg_tea_merchant_liu": "The tea trade funds the fortress. Zhang tolerates commerce because he must.", "dg_weapons_inspector_sun": "His most trusted officer. Sun finds the weapons Zhang can't allow.", "dg_healer_chen_ling": "The fortress healer. Zhang respects medicine — soldiers need it.", "dg_inn_keeper_wu": "Wu's inn is where soldiers decompress. Zhang allows it because the alternative is desertion.", "dg_broker_ming": "Ming brokers what Zhang permits. The boundary is absolute."},
    ),
    PortNPC(
        id="dg_harbor_captain_li", name="Harbor Captain Li Jun", title="Harbor Captain",
        port_id="dragons_gate", institution="harbor_master", personality="precise",
        description="A military officer who runs the harbor like a military operation — because it is one. Li Jun coordinates inspections, manages the chain deployment mechanism, and ensures that no ship docks, departs, or moves within the strait without Zhang's approval.",
        agenda="The chain. Li Jun's job is ensuring the chains work — that they can close the strait in under sixty seconds. Everything else is secondary to this capability.",
        greeting_neutral="\"Berth assignment pending inspection. Anchor in the holding area. Inspector Sun will board within the hour.\"",
        greeting_friendly="\"Captain — clean record, priority passage. Inspector Sun will do an abbreviated check. You'll be through within two hours.\"",
        greeting_hostile="\"Holding area. Indefinite. Commander Zhang has flagged your vessel. Cooperation will determine how long this takes.\"",
        rumor="Li Jun can deploy the harbor chains from memory — he's memorized every winch, every link, every anchor point. In a drill last year, he closed the strait in forty-three seconds. Zhang said 'acceptable.' Li Jun is trying for thirty-five.",
        relationship_notes={"dg_commander_zhang": "His commander. Absolute loyalty.", "dg_tea_merchant_liu": "Tea ships get efficient processing. The fortress needs revenue.", "dg_weapons_inspector_sun": "Sun inspects; Li Jun manages the dock flow around inspections.", "dg_healer_chen_ling": "No strong connection. Different jurisdictions.", "dg_inn_keeper_wu": "Li Jun drinks there. Quietly. Officers' corner.", "dg_broker_ming": "Ming's contracts must be approved by Li Jun before loading begins."},
    ),
    PortNPC(
        id="dg_tea_merchant_liu", name="Tea Merchant Liu", title="Tea Factor",
        port_id="dragons_gate", institution="exchange", personality="patient",
        description="A woman who has learned to trade tea within the framework of a military fortress — which means patience, paperwork, and the understanding that Commander Zhang's approval is required for everything, including breathing. Liu manages Dragon's Gate's tea trade, which is the fortress's economic lifeline.",
        agenda="Tea. Liu wants to export the finest tea in the East Indies — and Dragon's Gate's volcanic soil produces extraordinary leaves. She's patient because she has to be, and shrewd because patience alone doesn't pay the fortress's bills.",
        greeting_neutral="\"Tea? Dragon's Gate produces the finest in the East. I have varieties you won't find elsewhere. The inspection will take time — shall I brew a sample while you wait?\"",
        greeting_friendly="\"Captain! I've been aging a special batch — eighteen months in volcanic clay jars. The flavor is... remarkable. Worth waiting for the inspection.\"",
        greeting_hostile="\"Standard tea at posted prices. The premium lots require Commander Zhang's approval. Which requires your record to improve.\"",
        rumor="Liu's volcanic-aged tea was served at a Silk Circle diplomatic banquet. The Circle's magistrates called it the finest they'd ever tasted. Liu didn't mention she ages it in old weapons crates — the iron residue gives it a mineral finish Zhang would definitely not approve of.",
        relationship_notes={"dg_commander_zhang": "The tea funds the fortress. He tolerates her commerce.", "dg_harbor_captain_li": "Tea ships get efficient processing.", "dg_weapons_inspector_sun": "Sun once accidentally detained a tea shipment for three days. Liu hasn't forgiven him.", "dg_healer_chen_ling": "They exchange ingredients. Tea and medicine share more than people think.", "dg_inn_keeper_wu": "Wu serves Liu's tea. The soldiers drink it. The cycle funds everything.", "dg_broker_ming": "Ming brokers Liu's export contracts. A necessary partnership."},
    ),
    PortNPC(
        id="dg_weapons_inspector_sun", name="Inspector Sun", title="Weapons Inspector",
        port_id="dragons_gate", institution="customs", personality="relentless",
        description="The man who finds weapons. Inspector Sun has a reputation that extends across the entire East Indies — if you're smuggling weapons through the Gate, Sun will find them. He's found weapons hidden in grain barrels, sewn into sail canvas, disguised as ship's hardware, and once, memorably, dissolved in acid and stored as liquid iron. He found that too.",
        agenda="Zero tolerance. Sun doesn't inspect for tariffs or quality. He inspects for weapons. Every blade, every barrel, every ingot of iron that could be reforged. His fifteen-year record of zero unauthorized passages is Commander Zhang's greatest pride and Sun's only motivation.",
        greeting_neutral="\"Weapons declaration. Full manifest. I will inspect the hold personally. Cooperation determines speed.\"",
        greeting_friendly="\"Captain — your record is clean. Abbreviated inspection. But I will still check the forward hold. Protocol respects no friendship.\"",
        greeting_hostile="\"Full strip inspection. Every hold, every compartment, every barrel. I've found weapons in places you can't imagine. Don't test me.\"",
        rumor="Sun found weapons dissolved in acid and stored as liquid iron. The smuggler was a chemist. Sun is not a chemist — but he noticed the acid smell was wrong for the declared cargo of vinegar. He tested one drop. The smuggler is in chains. Sun considers this a normal Tuesday.",
        relationship_notes={"dg_commander_zhang": "His commander and the man whose record he protects with every inspection.", "dg_harbor_captain_li": "They coordinate: Sun inspects, Li Jun manages the queue.", "dg_tea_merchant_liu": "He once detained her tea for three days. She hasn't forgiven him. He doesn't care.", "dg_healer_chen_ling": "Medicine shipments pass quickly — Sun has no quarrel with healing.", "dg_inn_keeper_wu": "Sun doesn't drink. He watches the inn for weapons deals. Wu knows. It keeps both honest.", "dg_broker_ming": "Every contract Ming brokers must pass Sun's review. No exceptions."},
    ),
    PortNPC(
        id="dg_healer_chen_ling", name="Healer Chen Ling", title="Fortress Healer",
        port_id="dragons_gate", institution="apothecary", personality="dedicated",
        description="A woman whose gentle hands have tended fortress soldiers and civilian sailors alike for twenty years. Chen Ling runs Dragon's Gate's infirmary — a small but well-equipped facility that serves as the eastern strait's only reliable medical care. She buys medicines desperately — Dragon's Gate's remoteness makes supplies scarce.",
        agenda="Medicine for the fortress. Chen Ling needs medicines more than any other port in the East Indies. She'll pay above market for anything — herbs, compounds, surgical supplies. Her infirmary keeps the garrison functional and visiting captains alive.",
        greeting_neutral="\"Are you carrying medicines? I will pay premium — Dragon's Gate is always in need. And if you need healing yourself, my infirmary is open to all.\"",
        greeting_friendly="\"Captain! You brought medicines! You may have saved lives today — I mean that literally. Come, let me show you what I need most.\"",
        greeting_hostile="\"I heal all who ask. My oath outranks the Commander's displeasure. If you're wounded or sick, come to the infirmary. Politics stops at my door.\"",
        rumor="Chen Ling once treated an Iron Wolf sailor who washed up near the fortress. Zhang ordered her to interrogate the prisoner. She treated him and refused to interrogate. Zhang backed down. The Wolves returned the favor by not raiding the strait for six months.",
        relationship_notes={"dg_commander_zhang": "Respects her dedication. Knows better than to override her medical judgment.", "dg_harbor_captain_li": "No strong connection.", "dg_tea_merchant_liu": "They exchange ingredients — tea and medicine share secrets.", "dg_weapons_inspector_sun": "Medicine passes quickly. Sun has no quarrel with healing.", "dg_inn_keeper_wu": "Sends her the soldiers who've drunk too much. A familiar cycle.", "dg_broker_ming": "Ming sources rare medicines through his contracts. Chen Ling is grateful."},
    ),
    PortNPC(
        id="dg_inn_keeper_wu", name="Inn Keeper Wu", title="Inn Keeper",
        port_id="dragons_gate", institution="tavern", personality="discreet",
        description="A quiet man who runs the Gate's only inn — a stone building inside the fortress walls where soldiers, sailors, and merchants drink jasmine tea and, after dark, something stronger. Wu has mastered the art of being invisible: he sees everything, hears everything, and says nothing. The fortress runs on his discretion.",
        agenda="A functioning inn within a military fortress. Wu provides the social lubrication that keeps the garrison from cracking under Zhang's rigid discipline. He also provides information — to Zhang, to Liu, to anyone who asks the right question in the right way.",
        greeting_neutral="\"Tea? Or the evening menu? Rooms are available — the fortress isn't comfortable, but it's safe. Isn't that enough?\"",
        greeting_friendly="\"Captain — your usual room. I've prepared the jasmine blend you liked. Also... I may have heard something about the inspection schedule. If you're interested.\"",
        greeting_hostile="\"Tea is available. Rooms are available. Information is not. Not today.\"",
        rumor="Wu was a Monsoon Syndicate informant before he came to Dragon's Gate. Or he still is. Nobody knows for certain, including Zhang. The Commander keeps him because a known intelligence risk is more useful than an unknown one.",
        relationship_notes={"dg_commander_zhang": "Zhang knows Wu has connections. Wu knows Zhang knows. The equilibrium works.", "dg_harbor_captain_li": "Officers' corner. Li Jun drinks quietly.", "dg_tea_merchant_liu": "Wu serves her tea. Soldiers drink it. Revenue cycle.", "dg_weapons_inspector_sun": "Sun watches the inn for deals. Wu keeps it honest — mostly.", "dg_healer_chen_ling": "Sends her the drunk soldiers.", "dg_broker_ming": "Ming negotiates deals at Wu's tables. Wu overhears. Sometimes helpfully."},
    ),
    PortNPC(
        id="dg_broker_ming", name="Broker Ming", title="Gate Broker",
        port_id="dragons_gate", institution="broker", personality="cautious",
        description="The most restricted broker in the East Indies — Ming can only broker what Zhang permits, which excludes weapons, explosives, and anything Inspector Sun considers suspicious. Within those boundaries, Ming is excellent: tea contracts, porcelain orders, medicine sourcing. He's learned to thrive in a cage.",
        agenda="Maximum commerce within minimum permissions. Ming wants Dragon's Gate to be a trade port, not just a military chokepoint. He dreams of the day Zhang loosens the restrictions. That day has never come in nine years. Ming keeps dreaming.",
        greeting_neutral="\"Contracts available: tea export, porcelain transit, medicine supply. No weapons, no explosives, no exceptions. What are you looking for?\"",
        greeting_friendly="\"Captain! Tea contract — premium volcanic-aged, Liu's best. Commander Zhang approved it this morning. The margin is excellent.\"",
        greeting_hostile="\"I have nothing for flagged vessels. Come back when your record clears the Commander's review.\"",
        rumor="Ming once submitted a contract proposal to Zhang that would have allowed limited iron transit through the strait — for agricultural tools only. Zhang read it, wrote 'NO' in brush strokes three inches tall, and returned it. Ming framed it. It hangs behind his desk as a reminder of the boundaries he works within.",
        relationship_notes={"dg_commander_zhang": "Every contract requires Zhang's approval. Ming has learned the boundaries.", "dg_harbor_captain_li": "Contracts must be approved before loading. Li Jun enforces the sequence.", "dg_tea_merchant_liu": "Necessary partnership. She produces; he sells.", "dg_weapons_inspector_sun": "Every contract reviewed by Sun. No exceptions.", "dg_healer_chen_ling": "Sources medicines for her. One of his proudest contract lines.", "dg_inn_keeper_wu": "Negotiations happen at Wu's tables. Wu overhears. Useful."},
    ),
]

_DRAGONS_GATE_INSTITUTIONS = [
    PortInstitution(id="dg_strait", name="The Chain Harbor", port_id="dragons_gate", institution_type="harbor_master",
        description="Twin stone towers flanking the strait. Chains ready to close in sixty seconds. Li Jun's domain.", function="Military harbor with chain deployment. No unauthorized passage in 15 years.", political_leaning="Absolute military control.", npc_id="dg_harbor_captain_li"),
    PortInstitution(id="dg_tea_hall", name="The Tea Terraces", port_id="dragons_gate", institution_type="exchange",
        description="Terraced gardens on the fortress's south wall where volcanic soil produces extraordinary tea.", function="Tea trade — the fortress's economic lifeline. Liu manages production and export.", political_leaning="Commerce within military constraints.", npc_id="dg_tea_merchant_liu"),
    PortInstitution(id="dg_command", name="The Gate Command", port_id="dragons_gate", institution_type="governor",
        description="The fortress's highest tower. Maps of the strait, chain deployment controls, and Zhang's desk — military-neat, one personal item: nothing. He has no personal items.", function="Absolute military governance. Zhang's word is law.", political_leaning="Silk Circle military enforcement.", npc_id="dg_commander_zhang"),
    PortInstitution(id="dg_inn", name="The Gate Inn", port_id="dragons_gate", institution_type="tavern",
        description="Stone building inside fortress walls. Jasmine tea by day, something stronger at night. Wu sees everything and says nothing.", function="Social pressure valve + intelligence nexus. Wu provides both.", political_leaning="Discreet. Wu's loyalties are ambiguous by design.", npc_id="dg_inn_keeper_wu"),
    PortInstitution(id="dg_inspection", name="The Strip Room", port_id="dragons_gate", institution_type="customs",
        description="A brightly lit room where every cargo is examined. Sun's tools: acid tests, magnifying lenses, and an encyclopedic memory for every smuggling technique ever attempted.", function="Weapons inspection. Zero tolerance. Sun finds everything.", political_leaning="Fortress security.", npc_id="dg_weapons_inspector_sun"),
    PortInstitution(id="dg_infirmary", name="The Strait Infirmary", port_id="dragons_gate", institution_type="apothecary",
        description="Small but well-equipped. Chen Ling's domain. The eastern strait's only reliable medical care.", function="Medical care + desperate medicine purchasing. Chen Ling will pay premium for any medical supply.", political_leaning="Humanitarian within military structure.", npc_id="dg_healer_chen_ling"),
    PortInstitution(id="dg_broker", name="The Permitted Desk", port_id="dragons_gate", institution_type="broker",
        description="Ming's desk with Zhang's framed 'NO' hanging behind it. The most restricted brokerage in the East.", function="Brokering within Zhang's permissions. Tea, porcelain, medicine. No weapons. No exceptions.", political_leaning="Commerce in a cage.", npc_id="dg_broker_ming"),
]

DRAGONS_GATE_PROFILE = PortInstitutionalProfile(
    port_id="dragons_gate", governor_title="Gate Commander",
    power_structure="Dragon's Gate is Zhang's fortress. His word is absolute. Li Jun runs the harbor chains. Sun finds the weapons. Liu produces the tea that funds everything. Chen Ling heals. Wu watches and says nothing. Ming brokers what's permitted. Every institution exists within Zhang's boundaries — and those boundaries have not moved in fifteen years.",
    internal_tension="The tension is between security and commerce. Zhang wants zero weapons through the strait — absolute control. Liu needs trade to fund the fortress. Ming needs contracts to exist. The equilibrium works because Zhang's strictness makes the strait safe, which makes it valuable, which brings trade. Break any link and it collapses. Wu is the wildcard: his possible Syndicate connections are the one variable Zhang can't fully control, and he keeps Wu precisely because a known risk is better than an unknown one.",
    institutions=_DRAGONS_GATE_INSTITUTIONS, npcs=_DRAGONS_GATE_NPCS,
)


# =========================================================================
# SPICE NARROWS — The Hidden Market
# =========================================================================

_SPICE_NARROWS_NPCS = [
    PortNPC(
        id="sn_the_mouth", name="The Mouth", title="Anchorage Keeper",
        port_id="spice_narrows", institution="harbor_master", personality="invisible",
        description="You never see The Mouth. You hear a voice from the cliff face directing you through the volcanic channel to the hidden anchorage. The voice knows your ship's name, your cargo, and whether you're welcome. How it knows is the Narrows' first mystery.",
        agenda="Access control. The Mouth decides who enters the Narrows. Unlike One-Eye at Corsair's Rest who checks if you're followed, The Mouth checks if you're WORTHY. Unwelcome ships are directed into dead-end channels where they ground on volcanic rock.",
        greeting_neutral="A voice from the cliff: \"Follow the left channel. Anchor at the third cave. Touch nothing until you hear the second voice.\"",
        greeting_friendly="\"Captain! The Narrows expected you. Center channel — the deep berth. The Spice Lords have prepared your welcome.\"",
        greeting_hostile="\"Right channel. Shallow anchorage. Do not proceed further. Your reputation precedes you, Captain. It is not welcome here.\"",
        rumor="Nobody has ever seen The Mouth. Some say it's a person in a cave with speaking tubes. Others say it's three people working in shifts. One captain claims the voice came from the rock itself. The Narrows does not clarify.",
        relationship_notes={"sn_spice_lord_kiran": "The Mouth serves the Spice Lords. Access is their decision.", "sn_the_weigher": "The Weigher prices what The Mouth admits. Sequential trust.", "sn_raj_shadow": "Raj uses different channels. The Mouth knows which ones.", "sn_mama_smoke": "The Mouth has never been to Mama Smoke's kitchen. Nobody's sure if The Mouth eats.", "sn_poison_doctor": "Medicine enters freely. The Mouth never delays medical cargo.", "sn_ghost_broker": "The Ghost Broker moves what The Mouth admits. Clean chain."},
    ),
    PortNPC(
        id="sn_spice_lord_kiran", name="Spice Lord Kiran", title="Lord of the Narrows",
        port_id="spice_narrows", institution="governor", personality="dangerous",
        description="The Monsoon Syndicate's governor at Spice Narrows. Kiran sits cross-legged on silk cushions in the deepest cave, surrounded by the most concentrated spice wealth in the world. He speaks softly because he never needs to shout. His authority is the Syndicate's authority, and the Syndicate controls the opium trade, the spice lanes, and the informant network that spans every port east of Crosswind Isle.",
        agenda="Control of information and spice. Kiran doesn't just sell spice — he sells KNOWLEDGE. Which ships carry what cargo on which route at which time. The Syndicate's informants are everywhere, and Kiran is their handler. His real product isn't opium or spice — it's intelligence.",
        greeting_neutral="\"You've found the Narrows. That alone suggests someone trusts you. Sit. Tell me what you need, and I will tell you what it costs. The prices here are not in silver alone.\"",
        greeting_friendly="\"Ah, Captain — a valued friend of the Syndicate. Please, sit. I have information as valuable as any cargo. And some cargo, too. Shall we discuss both?\"",
        greeting_hostile="\"You are here because The Mouth permitted it. I am less generous than The Mouth. State your business quickly.\"",
        rumor="Kiran predicted a navy raid on the Narrows three days before it happened — because the raid commander's servant was a Syndicate informant. The Narrows was empty when the navy arrived. They found nothing but spice dust and the smell of incense.",
        relationship_notes={"sn_the_mouth": "The Mouth guards access. Kiran controls everything inside.", "sn_the_weigher": "His commercial arm. The Weigher prices the product. Kiran sets the strategy.", "sn_raj_shadow": "Raj the Quiet is his intelligence chief. They communicate in notes, never voice.", "sn_mama_smoke": "Even Kiran eats at Mama Smoke's. Even Kiran pays. Some rituals transcend authority.", "sn_poison_doctor": "The Poison Doctor serves the Syndicate's medical needs — and occasionally its darker needs.", "sn_ghost_broker": "The Ghost Broker handles the contracts Kiran approves. The approval is non-negotiable."},
    ),
    PortNPC(
        id="sn_the_weigher", name="The Weigher", title="Price Master",
        port_id="spice_narrows", institution="exchange", personality="mathematical",
        description="A figure in a dark room lit by a single lamp, surrounded by scales of extraordinary precision. The Weigher prices everything at the Narrows: spice by the grain, opium by the pipe, stolen cargo by the crate, and information by the word. Prices are whispered. Always.",
        agenda="Perfect pricing. The Weigher's job is ensuring the black market stays liquid — prices that are too high drive buyers away; too low and sellers stop coming. Like Whisper at Corsair's Rest but more calculating — The Weigher uses mathematics, not intuition.",
        greeting_neutral="A whisper from the dark: \"Place your goods on the scale. I will name the price once. You accept or you leave.\"",
        greeting_friendly="\"Ah, a trusted buyer. For you, the second scale.\" A different set of weights appears. Better prices. The lamp flickers.",
        greeting_hostile="\"The first scale only. Posted rates. Do not ask for the second.\"",
        rumor="The Weigher's scales are rumored to be a thousand years old — from a dynasty that measured spice in gold equivalents. Whether this is true or marketing is the Narrows' second mystery.",
        relationship_notes={"sn_the_mouth": "Sequential trust. The Mouth admits; The Weigher prices.", "sn_spice_lord_kiran": "Commercial arm of the Syndicate. Kiran sets strategy; The Weigher executes.", "sn_raj_shadow": "Raj provides intelligence that affects pricing. The Weigher incorporates it silently.", "sn_mama_smoke": "The Weigher sends food orders through notes. Nobody's seen The Weigher eat in person.", "sn_poison_doctor": "Medicine is priced separately. The Weigher considers healing exempt from market forces.", "sn_ghost_broker": "The Ghost Broker sells what The Weigher prices. Clean chain."},
    ),
    PortNPC(
        id="sn_raj_shadow", name="Raj the Quiet's Shadow", title="Intelligence Officer",
        port_id="spice_narrows", institution="customs", personality="phantom",
        description="Not Raj the Quiet himself — Raj operates from the sea. This is his representative at the Narrows: a figure known only as Raj's Shadow, who receives intelligence reports, dispatches informants, and ensures the Syndicate knows everything happening east of the Gate. The Shadow sits in a cave with a dozen message tubes and a map marked with pins.",
        agenda="Information. Every ship, every cargo, every captain's route and schedule — the Shadow collects it all and sends it to Raj. The Narrows' 'customs' isn't inspection — it's intelligence gathering. Every captain who docks is observed, catalogued, and filed.",
        greeting_neutral="You don't see anyone. But you have the distinct feeling you've been observed, assessed, and catalogued. A note appears: \"Your arrival has been recorded.\"",
        greeting_friendly="A note in familiar handwriting: \"Raj sends regards. Your route has been noted as friendly. The Syndicate will not interfere with your next three voyages.\"",
        greeting_hostile="No note. No contact. But your cargo manifest appears, accurately detailed, on a wall in the intelligence cave. You were never told about the intelligence cave.",
        rumor="Raj's Shadow is rumored to be three people working in shifts — or one person who never sleeps. The Shadow has never been seen entering or leaving the intelligence cave. Food appears inside. Reports appear outside. The mechanism is unknown.",
        relationship_notes={"sn_the_mouth": "Raj uses different channels. The Mouth knows which.", "sn_spice_lord_kiran": "Intelligence chief. They communicate in notes, never voice.", "sn_the_weigher": "Intelligence affects pricing. The Shadow provides; The Weigher incorporates.", "sn_mama_smoke": "Food appears in the intelligence cave. Mama Smoke denies delivering it.", "sn_poison_doctor": "The Shadow occasionally requests specific compounds. Nobody asks why.", "sn_ghost_broker": "The Ghost Broker's contracts are informed by the Shadow's intelligence."},
    ),
    PortNPC(
        id="sn_mama_smoke", name="Mama Smoke", title="Cave Cook",
        port_id="spice_narrows", institution="tavern", personality="motherly",
        description="A stout woman who cooks in a cave filled with spice smoke so thick it stings the eyes. Mama Smoke feeds the Narrows — smugglers, Syndicate agents, visiting captains, and whoever else finds their way to her fire. Her spice-smoked fish is legendary. Her neutrality is absolute. Even Kiran pays.",
        agenda="Feeding people in a place that tries to forget they need feeding. Mama Smoke provides the only human warmth in the Narrows — a cave full of spice smoke where people can sit, eat, and for a moment, be something other than smugglers.",
        greeting_neutral="\"Sit. The smoke clears your lungs — don't fight it. Fish is on the fire. Tea is in the pot. You look like you need both.\"",
        greeting_friendly="\"My captain! You came back to the deep! Sit, sit — I've been smoking a special batch. The spice in this one will make you see colors you didn't know existed.\"",
        greeting_hostile="\"Everyone eats. Even those the Lords distrust. Sit. The smoke doesn't judge, and neither does my fish.\"",
        rumor="Mama Smoke's cave has a back exit that nobody maps. Twice, when raids threatened the Narrows, captains escaped through her kitchen. She claims she doesn't know about any back exit. The rescued captains send her gifts annually.",
        relationship_notes={"sn_the_mouth": "The Mouth has never visited. Mama Smoke finds this suspicious.", "sn_spice_lord_kiran": "Even Kiran pays. Even Kiran sits quietly. Some things are sacred.", "sn_the_weigher": "Sends food through notes. Nobody's seen The Weigher eat.", "sn_raj_shadow": "Food appears in the intelligence cave. She denies delivering it. Denial is a form of kindness.", "sn_poison_doctor": "Friends. Two people who keep others alive in a place that values other things.", "sn_ghost_broker": "She feeds the Ghost Broker's crews after midnight runs. Hot spice tea and smoked fish."},
    ),
    PortNPC(
        id="sn_poison_doctor", name="The Poison Doctor", title="Apothecary",
        port_id="spice_narrows", institution="apothecary", personality="ambiguous",
        description="A figure whose title is deliberately unsettling — 'Poison Doctor' could mean healer or assassin, and at the Narrows, the answer is yes. The Doctor compounds medicines from the archipelago's rare spice-based pharmacopoeia, treats wounds and fevers, and occasionally prepares things that nobody asks about for clients nobody names.",
        agenda="Survival. The Poison Doctor provides medical care to a community that has no other access to it — and provides other services to clients who can afford them. The morality is as ambiguous as the title. The Doctor sleeps fine.",
        greeting_neutral="\"Sick? Wounded? I can help. If you need something else... describe the symptoms. I'll decide what you need.\"",
        greeting_friendly="\"Captain — your health is good. I can see it. But I've prepared a preventive compound for the southern waters. Take it daily. You'll thank me.\"",
        greeting_hostile="\"I treat all. Even those I'm told not to. The oath doesn't come with conditions. Sit down or don't.\"",
        rumor="The Poison Doctor once cured a plague in the Narrows using a spice compound that also happens to be mildly hallucinogenic. The patients recovered and reported vivid dreams for a week. The Doctor said this was a side effect. Some patients came back for refills. The Doctor didn't ask why.",
        relationship_notes={"sn_the_mouth": "Medicine enters freely. The Mouth never delays medical cargo.", "sn_spice_lord_kiran": "Serves the Syndicate's medical needs — and darker needs.", "sn_the_weigher": "Medicine priced separately. Healing is exempt from market forces.", "sn_raj_shadow": "Occasionally requests specific compounds. Nobody asks why.", "sn_mama_smoke": "Friends. Two people keeping others alive in a place that values other things.", "sn_ghost_broker": "Provides medical supplies for the broker's crews."},
    ),
    PortNPC(
        id="sn_ghost_broker", name="The Ghost Broker", title="Contract Handler",
        port_id="spice_narrows", institution="broker", personality="anonymous",
        description="Nobody's sure if the Ghost Broker is one person or a service. Contracts appear on a cave wall — pinned to the rock, detailed in precise handwriting, with pickup and delivery instructions that account for navy patrols, monsoon timing, and faction territory. The contracts are always profitable. The source is always unknown.",
        agenda="Moving product. The Ghost Broker matches Syndicate cargo to willing captains. Opium runs, spice contracts, stolen goods fencing — all appear on the wall with terms that are fair enough to attract takers and profitable enough to sustain the operation.",
        greeting_neutral="A contract appears on the wall near you. It matches your ship's capacity, your route, and your risk tolerance. There is no signature. Just terms.",
        greeting_friendly="Three contracts appear. The best one has a note: 'For trusted captains only. Higher margin. Raj's guarantee.' You've never met Raj.",
        greeting_hostile="The wall is blank where you stand. Contracts appear elsewhere. You are not being offered work today.",
        rumor="The Ghost Broker once posted a contract that was completed before anyone in the Narrows saw it. The cargo moved, the payment cleared, and nobody knows who took the job. Either the Ghost Broker has captains nobody else knows about, or the Ghost Broker IS one of the captains.",
        relationship_notes={"sn_the_mouth": "The Mouth admits; the Ghost Broker contracts. Clean chain.", "sn_spice_lord_kiran": "Contracts approved by Kiran. The approval is non-negotiable.", "sn_the_weigher": "The Ghost Broker sells what The Weigher prices.", "sn_raj_shadow": "Contracts informed by the Shadow's intelligence.", "sn_mama_smoke": "Crews fed after midnight runs.", "sn_poison_doctor": "Medical supplies provided for crews."},
    ),
]

_SPICE_NARROWS_INSTITUTIONS = [
    PortInstitution(id="sn_channel", name="The Volcanic Channel", port_id="spice_narrows", institution_type="harbor_master",
        description="A narrow volcanic channel with The Mouth's voice echoing from cliff faces. Left for welcome. Right for unwelcome. Center for trusted.", function="Voice-guided access. The Mouth directs. Unwelcome ships ground on volcanic rock.", political_leaning="Monsoon Syndicate.", npc_id="sn_the_mouth"),
    PortInstitution(id="sn_dark_room", name="The Dark Room", port_id="spice_narrows", institution_type="exchange",
        description="A cave lit by a single lamp. Scales of extraordinary precision. Prices whispered, never spoken aloud.", function="Black market pricing. Spice by the grain, opium by the pipe, information by the word.", political_leaning="Pure black market.", npc_id="sn_the_weigher"),
    PortInstitution(id="sn_deep_cave", name="The Deep Throne", port_id="spice_narrows", institution_type="governor",
        description="The deepest cave. Silk cushions. The most concentrated spice wealth in the world. Kiran sits. The world comes to him.", function="Syndicate governance + intelligence nexus. Kiran's real product is information.", political_leaning="Monsoon Syndicate headquarters.", npc_id="sn_spice_lord_kiran"),
    PortInstitution(id="sn_smoke_kitchen", name="Mama Smoke's Cave", port_id="spice_narrows", institution_type="tavern",
        description="A cave of spice smoke so thick it stings the eyes. The fish is legendary. The back exit is officially nonexistent.", function="The only human warmth in the Narrows. Neutrality absolute. Even Kiran pays.", political_leaning="Neutral by fire.", npc_id="sn_mama_smoke"),
    PortInstitution(id="sn_intel_cave", name="The Intelligence Cave", port_id="spice_narrows", institution_type="customs",
        description="A cave with message tubes, a pin-marked map, and food that appears from nowhere. Raj's Shadow operates here.", function="Not customs — intelligence. Every captain observed, catalogued, filed.", political_leaning="Syndicate intelligence operations.", npc_id="sn_raj_shadow"),
    PortInstitution(id="sn_lab", name="The Poison Lab", port_id="spice_narrows", institution_type="apothecary",
        description="A cave of rare compounds, spice-based pharmacopoeia, and ambiguous morality. The Doctor heals. The Doctor also prepares other things.", function="Medicine + ambiguous services. The title is deliberately unsettling.", political_leaning="Above faction. The oath doesn't come with conditions.", npc_id="sn_poison_doctor"),
    PortInstitution(id="sn_wall", name="The Contract Wall", port_id="spice_narrows", institution_type="broker",
        description="A cave wall where contracts appear — pinned to rock in precise handwriting, no signature, terms that account for patrols and monsoons.", function="Anonymous contract posting. Profitable terms, unknown source. The Ghost Broker may be one person or a service.", political_leaning="Syndicate operations.", npc_id="sn_ghost_broker"),
]

SPICE_NARROWS_PROFILE = PortInstitutionalProfile(
    port_id="spice_narrows", governor_title="Spice Lord",
    power_structure="Spice Narrows is the Monsoon Syndicate's heart — Kiran controls everything from the deepest cave. The Mouth guards access. The Weigher prices in darkness. Raj's Shadow collects intelligence on every captain who enters. The Ghost Broker posts contracts on cave walls. Mama Smoke feeds people in spice smoke. The Poison Doctor heals and occasionally does other things. Every person here is partially invisible, partially anonymous, and entirely controlled by Kiran's intelligence network.",
    internal_tension="The Narrows has no internal tension — because Kiran's information control eliminates the possibility of opposition. He knows everything before it happens. The EXTERNAL tension is the navy: Dragon's Gate's Commander Zhang and Inspector Sun are systematically mapping the Narrows' supply lines. Every raid Kiran predicts and escapes makes him more confident, which makes him less careful. Mama Smoke's back exit — the one she denies exists — is the Narrows' secret survival insurance. If Kiran ever fails to predict a raid, that exit becomes the most important tunnel in the East Indies.",
    institutions=_SPICE_NARROWS_INSTITUTIONS, npcs=_SPICE_NARROWS_NPCS,
)


# =========================================================================
# Export all profiles from this file
# =========================================================================


# =========================================================================
# EMBER ISLE — The Volcano's Children
# =========================================================================

_EMBER_ISLE_NPCS = [
    PortNPC(
        id="ei_elder_kai", name="Elder Kai", title="Keeper Elder",
        port_id="ember_isle", institution="governor", personality="mystical",
        description="A man whose skin carries the grey-brown of volcanic ash and whose eyes hold fire. Elder Kai leads the Ember Keepers — the herbalists who know the volcanic plants that produce medicines unmatched anywhere. He governs from the hot springs, where the volcano's warmth rises through stone older than human memory.",
        agenda="The mountain's balance. Kai believes the volcano provides — medicines, minerals, dyes — and the Keepers receive. When outsiders try to take more than the mountain offers, Kai closes the paths. He refused the Iron Pact's demand for exclusive medicine rights because 'the mountain teaches us. It didn't teach you.'",
        greeting_neutral="\"Welcome to Ember Isle. The mountain permits your visit. Place a stone at the base. It is how we greet those who come in peace.\"",
        greeting_friendly="\"Captain — the mountain remembers you. Come to the springs. I have harvested something from the hot pools that I believe you need. The mountain provides for friends.\"",
        greeting_hostile="\"You may dock. The mountain does not judge. But the paths to the upper slopes are closed to you today. The Keepers have decided.\"",
        rumor="The volcano speaks more often now. Kai says it grumbles before a good harvest. The other Keepers aren't as certain. If the mountain is building toward an eruption, Kai will be the first to know — and the last to leave.",
        relationship_notes={"ei_harbor_manu": "Manu runs the harbor. Kai runs the mountain. The boundary is the dock.", "ei_head_herbalist": "Sera is his successor. She knows the plants. He knows the mountain. Together, they ARE Ember Isle.", "ei_dye_keeper": "Volcanic dyes are the isle's second export. Kai approves the pigments.", "ei_spring_keeper": "The springs are sacred. Olo protects them for Kai.", "ei_broker_tia": "She sells what the mountain provides. Kai watches the balance."},
    ),
    PortNPC(
        id="ei_harbor_manu", name="Harbor Chief Manu", title="Harbor Chief",
        port_id="ember_isle", institution="harbor_master", personality="watchful",
        description="A broad man with obsidian-dark skin who stands on the black sand beach watching every approaching ship through volcanic haze. Manu runs Ember Isle's harbor — not a dock but a beach approach where ships anchor and lighters bring cargo through the surf.",
        agenda="Safe approach. The volcanic reef around Ember Isle shifts. Manu knows where it's safe this season and where it isn't. Captains who ignore his guidance lose their hulls.",
        greeting_neutral="\"Anchor there. ONLY there. The reef has shifted since last season. My lighter will come for your cargo.\"",
        greeting_friendly="\"Captain! The sand is steady today. Inner anchorage for you — I'll pilot you through the channel myself.\"",
        greeting_hostile="\"Outer anchorage. Far from shore. Send your cargo by lighter. I'm not risking the channel for your reputation.\"",
        rumor="Manu reads the reef by the color of the water — volcanic minerals change the hue where new rock has formed. He saved a merchant fleet from grounding by spotting a color shift invisible to everyone else.",
        relationship_notes={"ei_elder_kai": "Kai runs the mountain. Manu runs the beach. Clear boundary.", "ei_head_herbalist": "Sera's medicine shipments get priority lighters.", "ei_dye_keeper": "Dye barrels are heavy. Manu's crew loads them carefully.", "ei_spring_keeper": "Olo's springs are uphill. Manu's harbor is at sea level. Different worlds.", "ei_broker_tia": "She needs efficient loading. He provides it."},
    ),
    PortNPC(
        id="ei_head_herbalist", name="Head Herbalist Sera", title="Head Herbalist",
        port_id="ember_isle", institution="exchange", personality="passionate",
        description="A woman whose hands are perpetually stained green from plant work, with a mind that catalogs every medicinal species on the volcano's slopes. Sera is Kai's successor — the next Elder, though nobody says it aloud. She knows the hot-spring plants that produce Ember Isle's famous medicines: fever cures, wound salves, and the volcanic mineral compound that the entire Known World demands.",
        agenda="Healing the world. Sera wants Ember Isle's medicines to reach every port — not for profit but because people are dying of things she can cure. She turned down the Iron Pact's exclusivity deal and would do it again. She sells at fair prices because she believes healing belongs to everyone.",
        greeting_neutral="\"Medicines? I have fever cure, wound salve, and the mineral compound. All harvested this season, all potent. The prices are fair — I don't profit from suffering.\"",
        greeting_friendly="\"Captain! You brought the southern root I asked for! Let me see — yes, YES! This changes everything. I've been trying to complete a compound for months. This is the missing piece!\"",
        greeting_hostile="\"I sell medicines to all who need them. My oath doesn't come with exceptions. But I won't share my recipes with those who'd use them for profit over healing.\"",
        rumor="Sera has been trying to recreate the legendary Ember Isle fever cure that works even on the monsoon plague. She's close — one ingredient short. She's been asking every visiting captain to search for a specific root from the deep South Seas. Nobody's found it yet.",
        relationship_notes={"ei_elder_kai": "Her mentor, her predecessor, the standard she measures herself against.", "ei_harbor_manu": "Her medicine shipments get priority.", "ei_dye_keeper": "He uses some of her plant waste for pigments. Waste not.", "ei_spring_keeper": "The springs grow the plants she harvests. Sacred partnership.", "ei_broker_tia": "Tia sells the medicines. Sera sets the prices. Non-negotiable."},
    ),
    PortNPC(
        id="ei_dye_keeper", name="Dye Keeper Lono", title="Dye Master",
        port_id="ember_isle", institution="shipyard", personality="artistic",
        description="A man whose entire body seems stained with volcanic pigments — ochre, deep violet from mineral deposits, and a green from hot-spring algae that no other island produces. Lono creates dyes from the volcano's gifts: ash, mineral springs, and organisms that thrive in extreme heat.",
        agenda="Color from fire. Lono sees the volcano as a palette, not a threat. He's been developing new pigments from recently exposed mineral veins, and his latest creation — a deep volcanic red — has textile merchants from Porto Novo bidding against each other.",
        greeting_neutral="\"Dyes? I have colors from the volcano itself. This ochre — ash from the eastern vent. This violet — mineral spring deposit. Touch carefully — the pigments stain.\"",
        greeting_friendly="\"Captain! I've created something new — a red from the fresh lava deposits. The textile merchants will lose their minds. Be the first to carry it.\"",
        greeting_hostile="\"Posted prices on the board. Standard pigments only. The rare colors go to those who appreciate them.\"",
        rumor="Lono's volcanic red pigment was tested on silk in Silk Haven. Grand Weaver Seo-yeon saw it and went silent for ten minutes. Then she ordered her entire next collection based on it. Lono hasn't been told yet. He's going to be very surprised.",
        relationship_notes={"ei_elder_kai": "The mountain provides pigments. Kai approves the harvesting.", "ei_harbor_manu": "Dye barrels are heavy. Manu's crew loads carefully.", "ei_head_herbalist": "He uses her plant waste for pigments. Efficient.", "ei_spring_keeper": "The springs produce the algae he uses for green. Sacred access.", "ei_broker_tia": "She sells his dyes alongside medicines. Complementary."},
    ),
    PortNPC(
        id="ei_spring_keeper", name="Spring Keeper Olo", title="Hot Springs Guardian",
        port_id="ember_isle", institution="tavern", personality="serene",
        description="A woman who sits at the volcanic hot springs from dawn to dark, ensuring the sacred pools remain undisturbed. Olo is Ember Isle's 'tavern keeper' — but the springs aren't a tavern. They're a place of healing, rest, and community where visitors soak in mineral water while Olo shares the mountain's stories. No rum. No noise. Just hot water and quiet.",
        agenda="The springs' sanctity. Olo protects the pools from overuse, contamination, and tourists who treat them as entertainment. The springs are medicine — for the body and the spirit. She rations access the way Kai rations the mountain's gifts.",
        greeting_neutral="\"The springs are open to travelers. Remove your boots. Enter slowly. The mountain's heat takes getting used to. And please — no talking above a whisper.\"",
        greeting_friendly="\"Captain — the private pool is ready. The minerals are strongest today. Soak. Rest. The mountain heals what the sea breaks.\"",
        greeting_hostile="\"You may use the outer pools. The inner springs are for those the mountain trusts. Earn that trust. It takes time.\"",
        rumor="Olo hasn't left the springs in seven years. She says the mountain speaks through the water, and if she leaves, she'll stop hearing it. Whether this is devotion or the mineral water affecting her mind is Ember Isle's gentlest debate.",
        relationship_notes={"ei_elder_kai": "She protects the springs for him. Sacred duty.", "ei_harbor_manu": "Different worlds — beach and mountain. Respect at distance.", "ei_head_herbalist": "The springs grow Sera's plants. Sacred partnership.", "ei_dye_keeper": "Lono accesses the algae with Olo's permission. Always granted, never assumed.", "ei_broker_tia": "Tia doesn't sell the springs. They're not for sale."},
    ),
    PortNPC(
        id="ei_broker_tia", name="Broker Tia", title="Island Broker",
        port_id="ember_isle", institution="broker", personality="dedicated",
        description="A young woman who handles Ember Isle's exports — medicines, dyes, and the volcanic minerals that captains increasingly seek. Tia is practical in a port that's mostly spiritual: she makes sure the mountain's gifts reach the world and that the island gets fair value in return.",
        agenda="Fair trade for the island. Tia watches the medicine prices at other ports and adjusts to ensure Ember Isle isn't undervalued. She's been building relationships with brokers at every port — Fatou in Sun Harbor, Kamala in Monsoon Reach, even Fernanda in Porto Novo.",
        greeting_neutral="\"Medicines, dyes, or minerals? I have export lots ready. The volcano's been generous this season.\"",
        greeting_friendly="\"Captain! I've been holding a lot — Sera's best fever cure, Lono's new volcanic red, and a mineral sample that the Kiln Masters in Jade Port are desperate for. Interested?\"",
        greeting_hostile="\"Standard lots at posted prices. The premium harvests go to captains the island trusts.\"",
        rumor="Tia wrote to Fatou in Sun Harbor proposing a Gold Coast-South Seas medicine exchange: Ember Isle's fever cure for Pearl Shallows' reef compounds. If it works, it creates a medicine trade circuit that bypasses every major bloc. Grandmother Binta is considering it.",
        relationship_notes={"ei_elder_kai": "She sells what the mountain provides. Kai watches the balance.", "ei_harbor_manu": "She needs efficient loading. He delivers.", "ei_head_herbalist": "Sera sets medicine prices. Non-negotiable. Tia respects this.", "ei_dye_keeper": "She packages dyes alongside medicines. Complementary.", "ei_spring_keeper": "The springs aren't for sale. Tia knows."},
    ),
]

_EMBER_ISLE_INSTITUTIONS = [
    PortInstitution(id="ei_beach", name="The Black Sand Harbor", port_id="ember_isle", institution_type="harbor_master",
        description="Not a dock — a volcanic beach. Ships anchor offshore. Lighters bring cargo through surf. The reef shifts seasonally.",
        function="Beach-approach harbor. Manu reads the reef by water color. Captains who ignore his guidance lose hulls.",
        political_leaning="Coral Crown, with mountain independence.", npc_id="ei_harbor_manu"),
    PortInstitution(id="ei_herb_garden", name="The Volcanic Garden", port_id="ember_isle", institution_type="exchange",
        description="Terraced gardens on the volcano's lower slopes where hot-spring-fed plants produce irreplaceable medicines.",
        function="Medicine production. Sera's compounds are unmatched. Fair prices because healing belongs to everyone.",
        political_leaning="Humanitarian. The mountain doesn't profit.", npc_id="ei_head_herbalist"),
    PortInstitution(id="ei_throne", name="The Hot Springs Throne", port_id="ember_isle", institution_type="governor",
        description="The volcanic hot springs where Kai governs. Steam rises. The mountain rumbles. Policy is made in mineral water.",
        function="Governance by the volcano's wisdom. Kai closes paths when the mountain says enough.",
        political_leaning="Coral Crown with spiritual sovereignty.", npc_id="ei_elder_kai"),
    PortInstitution(id="ei_pools", name="The Healing Springs", port_id="ember_isle", institution_type="tavern",
        description="Sacred hot pools. No rum. No noise. Just mineral water and quiet. Olo guards the sanctity.",
        function="Healing, rest, community. The springs are medicine — for body and spirit.",
        political_leaning="Sacred. Not for sale.", npc_id="ei_spring_keeper"),
    PortInstitution(id="ei_dye_works", name="The Pigment Cave", port_id="ember_isle", institution_type="shipyard",
        description="A cave near the vents where Lono grinds volcanic pigments. Impossible colors from impossible heat.",
        function="Dye production from volcanic sources — colors no other island can produce.",
        political_leaning="Artistic. The volcano is the palette.", npc_id="ei_dye_keeper"),
    PortInstitution(id="ei_broker_hut", name="The Export Hut", port_id="ember_isle", institution_type="broker",
        description="A simple hut near the beach where Tia manages the island's exports. Functional, not fancy.",
        function="Medicine, dye, and mineral brokering. Tia ensures the island gets fair value.",
        political_leaning="Practical Coral Crown.", npc_id="ei_broker_tia"),
]

EMBER_ISLE_PROFILE = PortInstitutionalProfile(
    port_id="ember_isle", governor_title="Keeper Elder",
    power_structure="Ember Isle is governed by the mountain — through Kai, who interprets what the volcano provides. Sera harvests medicines. Lono creates dyes. Olo guards the springs. Manu manages the beach. Tia sells to the world. The power structure is spiritual: the mountain gives, the Keepers receive, and outsiders are guests.",
    internal_tension="The volcano speaks more often. Kai says it grumbles before a good harvest. Others aren't sure. If the mountain is building toward eruption, Ember Isle's entire existence is at risk — and the Keepers would be the last to leave because leaving would mean abandoning the medicine plants that only grow here. Sera's quest for the missing fever-cure ingredient is the island's scientific hope: if she completes the compound, it could justify the Keepers' existence even without the mountain.",
    institutions=_EMBER_ISLE_INSTITUTIONS, npcs=_EMBER_ISLE_NPCS,
)


# =========================================================================
# TYPHOON ANCHORAGE — The Storm Riders
# =========================================================================

_TYPHOON_ANCHORAGE_NPCS = [
    PortNPC(
        id="ta_storm_chief", name="Storm Chief Rangi", title="Storm Chief",
        port_id="typhoon_anchorage", institution="governor", personality="fearless",
        description="A woman whose body is a map of typhoon survival — scars from flying debris, a missing ear from a grappling hook, and the calm eyes of someone who has stared into the eye of six storms and come out the other side. Rangi governs Typhoon Anchorage the way she sails: into the wind, never away from it.",
        agenda="Survival as identity. Rangi doesn't want comfort — she wants the Anchorage to remain the place where only the strongest dock. The Storm Wall (built from wrecked hulls) is both monument and warning. She considers softness a greater threat than any typhoon.",
        greeting_neutral="\"You're here. That means you survived the approach. Good start. Tie your ship properly — chains, not anchors. Anchors fail here.\"",
        greeting_friendly="\"Captain! You sailed INTO that storm front? You earned this berth. Come — carve your ship's name into the Wall. You've earned it.\"",
        greeting_hostile="\"Dock in the lee. Away from the Wall. You haven't earned a place here, and the storm doesn't care about your feelings.\"",
        rumor="Rangi has carved her ship's name into the Storm Wall seven times — once for each typhoon survived. The seventh carving is the deepest. When asked about it, she says, 'That was the one that almost won.' She won't elaborate.",
        relationship_notes={"ta_harbor_chains": "Koa chains the ships. Rangi decides who docks. Simple.", "ta_pearl_boss": "Moana's divers are the bravest. Rangi respects bravery above all.", "ta_shipwright_ahe": "Ahe builds ships that survive. Rangi tests them.", "ta_cook_hine": "Hine feeds the survivors. Rangi considers this essential.", "ta_broker_wiremu": "Wiremu sells what the reef provides. Rangi doesn't interfere with commerce."},
    ),
    PortNPC(
        id="ta_harbor_chains", name="Harbor Master Koa", title="Chain Master",
        port_id="typhoon_anchorage", institution="harbor_master", personality="methodical",
        description="A man whose entire job is chains — not the fortress chains of Dragon's Gate, but survival chains. Koa ensures every ship at Typhoon Anchorage is chained to the cliff face, because anchors aren't enough here. He maintains the chain anchors carved into the rock, and he can chain a ship in under three minutes.",
        agenda="No ship lost to storm. Koa has lost ships — early in his career, when the chains weren't deep enough. He re-carved every anchor point himself. The last ship lost at anchor was six years ago. He's aiming for ten.",
        greeting_neutral="\"Chains. Not anchors. The reef will eat your anchor. My chains hold. Bow chain to port, stern to starboard. Do it now.\"",
        greeting_friendly="\"Captain! The deep chains for you — the ones I carved into bedrock. Your ship will hold through anything. I guarantee it.\"",
        greeting_hostile="\"Standard chains. Outer cliff. If your ship drags in a storm, that's your problem. I told you where to chain.\"",
        rumor="Koa once swam to a dragging ship during a typhoon — in the dark, in thirty-foot swells — to re-attach a chain that had slipped. He saved the ship, its crew, and its cargo. He doesn't mention it because he considers it his job.",
        relationship_notes={"ta_storm_chief": "Rangi decides who docks. Koa chains them. Simple division.", "ta_pearl_boss": "Moana's diving boats need special chains — lighter but secure.", "ta_shipwright_ahe": "Ahe builds; Koa secures. They coordinate on hull-chain interface design.", "ta_cook_hine": "Koa eats standing up between chain checks. Hine brings food to the dock.", "ta_broker_wiremu": "Wiremu's trade depends on Koa's chains keeping the fleet intact."},
    ),
    PortNPC(
        id="ta_pearl_boss", name="Dive Boss Moana", title="Pearl Boss",
        port_id="typhoon_anchorage", institution="exchange", personality="bold",
        description="The Storm Riders' lead diver — a woman who dives deeper, longer, and in worse conditions than the Breath-Holders at Pearl Shallows. The rivalry between the two diving traditions is the oldest grudge in the South Seas. Moana considers the Breath-Holders' techniques sacred but outdated. They consider her reckless. Both produce extraordinary pearls.",
        agenda="Better pearls from deeper water. Moana pushes the limits — deeper dives, longer breath-holds, worse conditions. She uses Abena's breathing technique (which leaked from Pearl Shallows) and has improved it. The Breath-Holders consider this poaching of sacred knowledge. Moana considers it evolution.",
        greeting_neutral="\"Pearls? The reef here is deeper than Pearl Shallows'. The pearls are bigger. And I don't haggle — the price is the price.\"",
        greeting_friendly="\"Captain! I brought up something special yesterday — from the deep reef, below where anyone else dives. Look at this luster. You won't see this at Pearl Shallows.\"",
        greeting_hostile="\"Pearls at posted prices. I don't sell the deep-reef lots to captains I don't trust. Come back with a better reputation.\"",
        rumor="Moana dove the deepest reef in the South Seas and brought up a pearl the size of a fist — the legendary pearl that Pearl Shallows' Breath-Holders tell stories about. She didn't tell anyone for three days. Then she wore it to a trade council. Pearl Shallows hasn't spoken to the Storm Riders since.",
        relationship_notes={"ta_storm_chief": "Rangi respects her bravery. Moana respects Rangi's leadership. Mutual warrior respect.", "ta_harbor_chains": "Her diving boats need special chains.", "ta_shipwright_ahe": "Ahe designs diving craft for her. The collaboration is productive.", "ta_cook_hine": "Hine feeds the divers after deep dives. Essential recovery.", "ta_broker_wiremu": "He sells what she brings up. The margins fund everything."},
    ),
    PortNPC(
        id="ta_shipwright_ahe", name="Shipwright Ahe", title="Storm Shipwright",
        port_id="typhoon_anchorage", institution="shipyard", personality="innovative",
        description="A shipwright who builds for the worst weather on earth. Ahe's ships are designed to survive what kills everything else — reinforced hulls, flexible masts that bend rather than break, and hull shapes that ride waves rather than fight them. Her yard is built from the Storm Wall's wrecks — she literally builds from failure.",
        agenda="Ships that can't be broken. Ahe studies every wreck on the Storm Wall and designs against the failure mode. She's been corresponding with Devi in Monsoon Reach — two shipwrights who build for extreme weather, sharing data across the sea.",
        greeting_neutral="\"Need repairs? I build for typhoons. Whatever the sea did to your ship, I've seen worse. Let me look at your hull.\"",
        greeting_friendly="\"Captain! Your ship took that storm well — my reinforcements held. Come see what I'm working on next. A hull design that FLEXES in heavy seas instead of cracking.\"",
        greeting_hostile="\"I'll repair your ship. The sea teaches through damage. But you're paying storm rates, and I'm not explaining my methods.\"",
        rumor="Ahe built a ship so storm-resistant that Rangi took it into a typhoon deliberately to test it. The ship survived. Ahe said, 'I knew it would.' Rangi said, 'I didn't.' They've been inseparable since.",
        relationship_notes={"ta_storm_chief": "Rangi tests what Ahe builds. The ultimate quality assurance.", "ta_harbor_chains": "They coordinate on hull-chain interface design.", "ta_pearl_boss": "Designs diving craft for Moana. Productive collaboration.", "ta_cook_hine": "Ahe works through meals. Hine brings food to the yard.", "ta_broker_wiremu": "Ship repairs are part of the Anchorage's revenue."},
    ),
    PortNPC(
        id="ta_cook_hine", name="Cook Hine", title="Storm Cook",
        port_id="typhoon_anchorage", institution="tavern", personality="resilient",
        description="A woman who cooks on a volcanic-heated stone grill that never goes out — even in typhoons, because Hine built a windbreak from wrecked hull timbers. Her food is designed for survival: high-calorie, storm-resistant, and served in portions that fuel twelve-hour storm watches. She's the only person at the Anchorage who's never lost a night's sleep to weather.",
        agenda="Fuel. Hine doesn't serve meals — she serves fuel. Her food keeps divers diving, shipwrights building, and storm watches watching. She considers cooking a survival skill, not an art. Mama Lucia at Corsair's Rest would disagree about the art part. They'd agree about the importance.",
        greeting_neutral="\"Eat. You'll need it. Storm's building — I can feel the pressure changing. Eat now or not at all for two days.\"",
        greeting_friendly="\"Captain! The grill's hot and I've been smoking fish all morning. Sit — eat — you look like you haven't had a proper meal since the last port.\"",
        greeting_hostile="\"Everyone eats. Even people I don't like need fuel. Sit. Eat. Then leave.\"",
        rumor="Hine cooked through the worst typhoon in twenty years — the one that rearranged the Storm Wall. She served hot food for thirty-six straight hours because 'cold people make bad decisions.' Nobody died. Rangi credits Hine's cooking as much as the chains.",
        relationship_notes={"ta_storm_chief": "Rangi considers Hine essential. Hine considers cooking essential. Agreement.", "ta_harbor_chains": "Brings food to the dock. Koa eats standing.", "ta_pearl_boss": "Feeds divers after deep dives. Recovery fuel.", "ta_shipwright_ahe": "Brings food to the yard. Ahe forgets to eat.", "ta_broker_wiremu": "Wiremu eats at her grill. Everyone does. It's the only grill."},
    ),
    PortNPC(
        id="ta_broker_wiremu", name="Broker Wiremu", title="Trade Broker",
        port_id="typhoon_anchorage", institution="broker", personality="steady",
        description="A quiet man who brokers Typhoon Anchorage's exports — pearls, tropical hardwood, and the services of the only shipyard in the South Seas. Wiremu is practical where everyone else is dramatic: he handles contracts while storms rage, maintains trade relationships during typhoon season, and never raises his voice above conversational.",
        agenda="Steady revenue despite the weather. Wiremu's challenge: selling goods from a port that's famous for destroying ships. His solution: premium pricing for premium goods. Typhoon Anchorage pearls, he argues, are the best because the reef that produces them is the most dangerous to dive.",
        greeting_neutral="\"Pearls, timber, or ship repair? I have all three. The prices reflect the difficulty of getting them. You're not buying goods — you're buying bravery.\"",
        greeting_friendly="\"Captain! Moana brought up a new lot yesterday — deep-reef pearls. I've been waiting for a captain I trust. The margin is worth the voyage.\"",
        greeting_hostile="\"Standard lots at posted prices. The premium goods go to captains the Anchorage respects. Respect is earned here, not bought.\"",
        rumor="Wiremu brokered a pearl lot to the Coral Throne during a typhoon — literally signing the contract while the walls shook. The Coral King was so impressed by the delivery under storm conditions that he doubled the payment. Wiremu said, 'Standard service.'",
        relationship_notes={"ta_storm_chief": "Rangi doesn't interfere with commerce. Wiremu appreciates this.", "ta_harbor_chains": "Trade depends on Koa's chains keeping the fleet intact.", "ta_pearl_boss": "He sells what Moana dives. The margins fund everything.", "ta_shipwright_ahe": "Ship repair revenue is steady work.", "ta_cook_hine": "Everyone eats at Hine's. There's no alternative. There doesn't need to be."},
    ),
]

_TYPHOON_ANCHORAGE_INSTITUTIONS = [
    PortInstitution(id="ta_cliff", name="The Chained Harbor", port_id="typhoon_anchorage", institution_type="harbor_master",
        description="Carved into the leeward cliff. Ships chained, not anchored. The Storm Wall of wrecked hulls is both monument and breakwater.",
        function="Survival berthing. Koa's chains hold. Anchors don't.", political_leaning="Coral Crown, Storm Rider pride.", npc_id="ta_harbor_chains"),
    PortInstitution(id="ta_reef", name="The Deep Reef", port_id="typhoon_anchorage", institution_type="exchange",
        description="The reef itself — the most dangerous diving ground in the South Seas. Moana's domain. The pearls justify the risk.",
        function="Pearl diving and grading. Deeper, bigger, riskier than Pearl Shallows.", political_leaning="Storm Rider sovereignty.", npc_id="ta_pearl_boss"),
    PortInstitution(id="ta_wall", name="The Storm Wall", port_id="typhoon_anchorage", institution_type="governor",
        description="A breakwater built from wrecked hulls. Names carved by captains who survived typhoons. Rangi's seventh carving is the deepest.",
        function="Governance + monument. Rangi leads from the Wall. Survival IS governance.", political_leaning="Coral Crown warrior culture.", npc_id="ta_storm_chief"),
    PortInstitution(id="ta_grill", name="Hine's Storm Grill", port_id="typhoon_anchorage", institution_type="tavern",
        description="A volcanic-heated stone grill behind a windbreak of hull timbers. Never goes out — not even in typhoons. Fuel, not art.",
        function="Survival cooking. Hine served 36 hours straight during the worst typhoon. Nobody died.", political_leaning="Essential.", npc_id="ta_cook_hine"),
    PortInstitution(id="ta_yard", name="The Wreck Yard", port_id="typhoon_anchorage", institution_type="shipyard",
        description="A shipyard built from Storm Wall wrecks. Ahe literally builds from failure. Flexible masts, bending hulls, wave-riding designs.",
        function="Storm-proof shipbuilding. Only yard in the South Seas. Ships designed to survive what kills everything else.",
        political_leaning="Innovation through destruction.", npc_id="ta_shipwright_ahe"),
    PortInstitution(id="ta_broker", name="Wiremu's Steady Desk", port_id="typhoon_anchorage", institution_type="broker",
        description="A desk that doesn't move in a storm — because Wiremu bolted it to the rock. Contracts signed during typhoons.",
        function="Premium brokering. Pearls, timber, repair services. The prices reflect the bravery of getting them.",
        political_leaning="Practical Crown.", npc_id="ta_broker_wiremu"),
]

TYPHOON_ANCHORAGE_PROFILE = PortInstitutionalProfile(
    port_id="typhoon_anchorage", governor_title="Storm Chief",
    power_structure="Typhoon Anchorage is ruled by survival. Rangi leads because she's survived more. Koa chains ships. Moana dives deeper than anyone. Ahe builds from wreckage. Hine feeds through storms. Wiremu sells what the rest produce. Every institution exists to answer one question: can it survive a typhoon? If yes, it stays. If no, it's rebuilt.",
    internal_tension="The rivalry with Pearl Shallows is the deepest wound. Moana uses Abena's breathing technique — poached, improved, and wielded as proof of Storm Rider superiority. The fist-sized pearl she brought up from the deep reef is the physical evidence. Pearl Shallows hasn't spoken to them since. Within the Anchorage, the tension is simpler: Rangi glorifies survival. Ahe wants to eliminate the need for survival through better engineering. Both are right. The storm doesn't care about their debate.",
    institutions=_TYPHOON_ANCHORAGE_INSTITUTIONS, npcs=_TYPHOON_ANCHORAGE_NPCS,
)


# =========================================================================
# CORAL THRONE — The Reef Kingdom
# =========================================================================

_CORAL_THRONE_NPCS = [
    PortNPC(
        id="ct_coral_king", name="The Coral King", title="King",
        port_id="coral_throne", institution="governor", personality="imperious",
        description="A man whose crown is literally grown from living coral — placed on his head as a boy, it has grown with him for forty years. The Coral King governs the South Seas from a palace built of reef, and his authority is absolute within the lagoon. Trade is tribute. Commerce is negotiation with sovereignty. He has no heir, and three princes compete for his favor.",
        agenda="The kingdom's legacy. The King wants to ensure the Coral Crown outlasts him — which requires securing the succession, maintaining tribute from visiting captains, and building alliances with blocs powerful enough to protect the islands. He's been courting both the Gold Coast Compact and the Silk Circle, playing their goodwill against each other.",
        greeting_neutral="\"The Coral King permits you to anchor. State your tribute. Silk or weapons preferred. Refusal is exile.\"",
        greeting_friendly="\"Captain — the King remembers you. Your tribute was generous last time. You may enter the lagoon and approach the Palace. Few receive this honor.\"",
        greeting_hostile="\"The lagoon is closed to you. Anchor outside the reef. Send your tribute by canoe. If it is sufficient, we will discuss your return.\"",
        rumor="The Coral King has no heir, and three princes compete for the throne. Each courts foreign captains for weapons and alliances. Smart traders play all three. Dangerous traders pick a side. Nobody knows which prince the King favors. The King may not know either.",
        relationship_notes={"ct_reef_pilot": "Iti guides ships through the reef. The King's authority starts at the lagoon mouth.", "ct_pearl_trader": "Hana manages the pearl trade. The King takes tribute; Hana handles commerce.", "ct_war_chief": "Tane commands the war canoes. The King's military arm.", "ct_drum_keeper": "Miri keeps the cultural traditions alive. The King's ceremonial arm.", "ct_broker_ariki": "Ariki brokers what the King permits. Tribute first, trade second."},
    ),
    PortNPC(
        id="ct_reef_pilot", name="Reef Pilot Iti", title="Reef Pilot",
        port_id="coral_throne", institution="harbor_master", personality="proud",
        description="A man who knows every coral head, every channel, every treacherous shallow in the lagoon — because his family has piloted ships through the reef for twelve generations. Iti is Coral Throne's harbor master in the truest sense: without him, your ship doesn't enter. With him, you glide through the deadliest reef in the South Seas as if it were open water.",
        agenda="The reef's sovereignty. Iti doesn't just pilot — he protects. Ships that approach without a pilot ground on coral. This isn't carelessness; it's defense. The reef is the Coral Throne's wall, and Iti is the gatekeeper.",
        greeting_neutral="\"I will guide you through the reef. Follow my commands exactly. The lagoon entrance is narrow and the coral is living. One wrong turn and your hull belongs to the reef.\"",
        greeting_friendly="\"Captain! The channel is calm today. I'll pilot you through the inner passage — the short route. Reserved for friends of the Crown.\"",
        greeting_hostile="\"Outer channel. The long way around. And if your helmsman deviates from my course by one degree, I'm cutting the tow line.\"",
        rumor="Iti once piloted a ship through the reef in total darkness during a storm — by feel alone, reading the current against the hull. The captain fainted. The crew prayed. The ship arrived without a scratch. Iti said, 'The reef speaks to those who listen.'",
        relationship_notes={"ct_coral_king": "The King's authority starts at the lagoon. Iti's authority starts at the reef.", "ct_pearl_trader": "Hana's pearl boats use the inner channels. Iti knows every one.", "ct_war_chief": "Tane's war canoes don't need pilots. They know the reef from childhood.", "ct_drum_keeper": "Miri's ceremonies mark the reef seasons. Iti's piloting follows the same calendar.", "ct_broker_ariki": "Trade ships need Iti. Without him, there is no trade."},
    ),
    PortNPC(
        id="ct_pearl_trader", name="Pearl Trader Hana", title="Royal Pearl Trader",
        port_id="coral_throne", institution="exchange", personality="shrewd",
        description="A woman who handles the Coral Crown's pearl commerce with the understanding that every pearl belongs to the King first and the market second. Hana is shrewd not because she's greedy but because every pearl she undervalues is a pearl that doesn't fund the kingdom.",
        agenda="Maximum value for the Crown's pearls. Hana knows the pearl markets at Pearl Shallows and Typhoon Anchorage intimately — she prices Coral Throne pearls to compete but never undercut. The King takes tribute from trade; Hana ensures there's enough trade to fund the tribute system.",
        greeting_neutral="\"The Crown's pearls are available for trade — after tribute is paid. The finest lots are presented at the Palace. Prices are the King's to set.\"",
        greeting_friendly="\"Captain — I have set aside a pearl lot that the King approved for your hands. The quality is exceptional. The price reflects the Crown's generosity.\"",
        greeting_hostile="\"Standard lots only. Posted prices. The Palace selection is not available to you. Pay tribute and improve your standing.\"",
        rumor="Hana negotiated a pearl-for-weapons deal with an Iron Wolves captain that supplied the Crown's armory for a year. Commander Zhang at Dragon's Gate found out and was furious. Hana said the King's sovereignty includes the right to arm himself. Zhang had no answer.",
        relationship_notes={"ct_coral_king": "She handles commerce. The King takes tribute. Clean division.", "ct_reef_pilot": "Pearl boats use Iti's channels.", "ct_war_chief": "The weapons she trades for fund Tane's armory.", "ct_drum_keeper": "Pearls are part of the coronation ceremony. Miri and Hana coordinate.", "ct_broker_ariki": "Ariki handles contracts. Hana handles pearls. Complementary."},
    ),
    PortNPC(
        id="ct_war_chief", name="War Chief Tane", title="War Chief",
        port_id="coral_throne", institution="customs", personality="fierce",
        description="The Coral King's military commander — a warrior whose war canoes escort every entering ship and whose inspection is the closest thing Coral Throne has to customs: he checks your cargo for weapons, not to confiscate them but to ASSESS them. The King wants weapons. Tane decides if yours are good enough.",
        agenda="The Crown's defense. Tane wants weapons — swords, bows, gunpowder, anything that gives the war canoes an edge. He's the reason weapons sell for 700% markup at Coral Throne. He also assesses every visiting captain as a potential ally or threat. His war canoes can sink a galleon in the shallows.",
        greeting_neutral="\"Your weapons. Show them. The King demands tribute of arms. If yours are worthy, the price will be generous. If not... tribute in silk.\"",
        greeting_friendly="\"Captain! You brought the blades I asked for? Show me. Ah — yes. The King will be pleased. Your tribute is weapons today. A GOOD tribute.\"",
        greeting_hostile="\"Stand on your deck. My warriors will inspect your hold. Do not resist. The reef is shallow here, and war canoes are faster than anything you sail.\"",
        rumor="Tane's war canoes sank a pirate ship that tried to raid Coral Throne by luring it onto the reef and then boarding from the shallow side. The pirates never saw them coming — the canoes were painted to match the coral. The pirate captain's flag hangs in the Palace.",
        relationship_notes={"ct_coral_king": "His sword arm. Tane serves the Crown's military will absolutely.", "ct_reef_pilot": "Tane's canoes don't need pilots. They know the reef from childhood.", "ct_pearl_trader": "The weapons Hana trades for fund his armory.", "ct_drum_keeper": "War ceremonies before battle. Miri and Tane coordinate the drums.", "ct_broker_ariki": "Ariki's trade brings the weapons Tane needs."},
    ),
    PortNPC(
        id="ct_drum_keeper", name="Drum Keeper Miri", title="Keeper of Traditions",
        port_id="coral_throne", institution="tavern", personality="reverent",
        description="A woman whose drumming IS the Coral Throne — the rhythms that mark arrivals, departures, trade sessions, ceremonies, and the Coral Coronation itself. Miri is not a tavern keeper — she's a cultural institution. Her drum circle at the lagoon's edge is where stories are told, ceremonies performed, and the kingdom's identity maintained through rhythm.",
        agenda="Cultural continuity. The three competing princes each want Miri's support, because the Drum Keeper decides which coronation music plays — and the music determines which prince the gods favor. Miri hasn't decided. She may never decide. The drums will tell her when it's time.",
        greeting_neutral="\"The drums welcome you, Captain. Listen — each rhythm has meaning. This one means 'stranger arriving.' If you hear the war rhythm, leave immediately.\"",
        greeting_friendly="\"Captain! The welcome rhythm for you today — the long one, with the celebration beat. The King honors you. Sit. Listen. The drums speak.\"",
        greeting_hostile="\"The warning rhythm plays. Do you hear it? The drums know you, Captain. They don't forget.\"",
        rumor="The three princes each visit Miri separately, seeking her endorsement. She serves each the same tea and plays each the same neutral rhythm. None knows she plays a fourth rhythm — alone, at midnight, on the reef. What it means, only Miri and the coral know.",
        relationship_notes={"ct_coral_king": "His ceremonial arm. The drums validate his authority.", "ct_reef_pilot": "The drums mark the reef seasons. Iti's piloting follows the calendar.", "ct_pearl_trader": "Pearls in the coronation ceremony. Coordination essential.", "ct_war_chief": "War drums before battle. The rhythm decides morale.", "ct_broker_ariki": "The drums signal trade sessions. Ariki's work begins when Miri plays."},
    ),
    PortNPC(
        id="ct_broker_ariki", name="Broker Ariki", title="Royal Broker",
        port_id="coral_throne", institution="broker", personality="diplomatic",
        description="The Coral King's commercial face — the person who translates royal demands into trade contracts and tribute requirements into commercial language that visiting captains understand. Ariki bridges the gap between the King's absolute authority and the practical reality of international trade.",
        agenda="The Crown's commerce. Ariki wants trade flowing — weapons in, pearls out, silk in, tobacco out. He manages the balance between the King's demands (always more weapons, always more silk) and what the market actually provides. He's the only person who can tell the King 'no' — phrased, of course, as 'not yet, Your Majesty.'",
        greeting_neutral="\"The Crown offers trade — pearls, tobacco, rum. Tribute is required first. I can advise on what the King currently favors.\"",
        greeting_friendly="\"Captain! The King's demands align with your cargo. This is fortunate. Let me broker the terms — tribute as weapons, trade in pearls. Both parties benefit.\"",
        greeting_hostile="\"The Crown's trade requires a minimum tribute. Your history suggests your tribute may be... insufficient. I advise generosity.\"",
        rumor="Ariki told the King 'no' once — when the King demanded a tariff so high it would have driven away all trade. He phrased it as 'the reef provides in its own time, Your Majesty, and so does trade.' The King was silent for an hour. Then he reduced the tariff. Ariki hasn't slept soundly since, but the trade continued.",
        relationship_notes={"ct_coral_king": "The only person who says 'no' to the King — carefully.", "ct_reef_pilot": "Trade ships need Iti. Without pilots, there's no trade for Ariki to broker.", "ct_pearl_trader": "Hana handles pearls. Ariki handles everything else.", "ct_war_chief": "Ariki's trade brings weapons. Tane's armory depends on it.", "ct_drum_keeper": "The drums signal trade sessions. Ariki's work begins with Miri's rhythm."},
    ),
]

_CORAL_THRONE_INSTITUTIONS = [
    PortInstitution(id="ct_lagoon", name="The Lagoon Entrance", port_id="coral_throne", institution_type="harbor_master",
        description="A narrow, treacherous passage through living coral. Only Iti can guide you through. War canoes escort every ship.",
        function="Reef-piloted access. Iti is the gatekeeper. The reef is the wall.", political_leaning="Coral Crown absolute.", npc_id="ct_reef_pilot"),
    PortInstitution(id="ct_pearl_hall", name="The Pearl Hall", port_id="coral_throne", institution_type="exchange",
        description="A chamber in the Coral Palace where pearls are displayed, graded, and traded — after tribute is paid.",
        function="Royal pearl commerce. Every pearl belongs to the King first. Hana manages the market second.", political_leaning="Crown commerce.", npc_id="ct_pearl_trader"),
    PortInstitution(id="ct_palace", name="The Coral Palace", port_id="coral_throne", institution_type="governor",
        description="Grown from living reef over centuries. Walls glitter with embedded shells and pearls. The King sits on a throne of coral that was alive when his grandfather was born.",
        function="Absolute monarchy. Trade is tribute. Tribute is submission. Submission is the price of access.", political_leaning="The Crown IS the politics.", npc_id="ct_coral_king"),
    PortInstitution(id="ct_drum_circle", name="The Drum Circle", port_id="coral_throne", institution_type="tavern",
        description="The lagoon's edge where Miri's drums mark every moment. Not a tavern — a cultural heartbeat. Stories told through rhythm.",
        function="Cultural continuity, ceremonies, arrival/departure signals. The drums decide which prince the gods favor.", political_leaning="Above politics. The drums speak for the reef.", npc_id="ct_drum_keeper"),
    PortInstitution(id="ct_canoe_dock", name="The War Canoe Dock", port_id="coral_throne", institution_type="customs",
        description="Where Tane's warriors inspect arriving cargo — not for legality but for QUALITY. The King wants weapons. Tane decides if yours are good enough.",
        function="Military assessment disguised as customs. Weapons checked for tribute worthiness, not legality.", political_leaning="Crown military.", npc_id="ct_war_chief"),
    PortInstitution(id="ct_trade", name="The Royal Trading Post", port_id="coral_throne", institution_type="broker",
        description="A coral-walled room where Ariki translates royal demands into commercial language. The only person who can tell the King 'no.'",
        function="Royal brokering. Tribute first, trade second. Ariki manages the balance.", political_leaning="Crown diplomacy.", npc_id="ct_broker_ariki"),
]

CORAL_THRONE_PROFILE = PortInstitutionalProfile(
    port_id="coral_throne", governor_title="King",
    power_structure="Absolute monarchy. The Coral King's authority is total within the lagoon. Iti controls reef access. Tane commands the military. Hana manages pearls. Miri maintains culture. Ariki handles commerce. The King sits at the center, wearing a crown that is literally growing. Every institution radiates from the Palace like spokes from a hub.",
    internal_tension="The succession. The King has no heir, and three princes compete. Each courts foreign captains for weapons. Each visits Drum Keeper Miri seeking her endorsement — because the coronation music determines which prince the gods favor. Miri plays each the same neutral rhythm. She plays a fourth rhythm alone at midnight on the reef. Nobody knows what it means. The succession crisis isn't violent — yet. But when the King dies, three princes, their foreign alliances, and Miri's drums will determine whether the Coral Crown continues or shatters.",
    institutions=_CORAL_THRONE_INSTITUTIONS, npcs=_CORAL_THRONE_NPCS,
)


# =========================================================================
# Export all profiles from this file
# =========================================================================

EAST_PROFILES = {
    "silk_haven": SILK_HAVEN_PROFILE,
    "crosswind_isle": CROSSWIND_ISLE_PROFILE,
    "dragons_gate": DRAGONS_GATE_PROFILE,
    "spice_narrows": SPICE_NARROWS_PROFILE,
    "ember_isle": EMBER_ISLE_PROFILE,
    "typhoon_anchorage": TYPHOON_ANCHORAGE_PROFILE,
    "coral_throne": CORAL_THRONE_PROFILE,
}
