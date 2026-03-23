# State Dictionary — Star Freight

> Every canonical campaign variable. What it is, its range, who writes it, who reads it, and what the player sees. No variable exists outside this list. If a system needs state not listed here, the dictionary must be updated first.

---

## Primary Campaign Variables

These are the shared variables from the Campaign State doc. All three layers (trade, tactics, plot) read and write them.

### credits

| Property | Value |
|----------|-------|
| Type | Integer |
| Range | 0 – uncapped (practical ceiling ~20,000₡ in late game) |
| Starting value | 500₡ |
| Written by | Trade (sell goods), Contracts (payouts), Combat (loot/salvage), Narrative (story rewards), Bribes (-), Repairs (-), Upgrades (-), Fuel (-), Crew signing (-), Docking fees (-) |
| Read by | Trade (can I afford this cargo?), Ship (can I afford repairs?), Crew (can I pay?), Contracts (can I buy the entry goods?), Cultural (can I afford permits/gifts/bribes?) |
| Visible | Always. Captain's View persistent bar. Flashes on change. |
| Player meaning | "How safe am I?" Credits are survival. Below 200₡ is emergency. Above 2,000₡ is comfortable. Above 5,000₡ is investing. |

### reputation.[faction]

| Property | Value |
|----------|-------|
| Type | Integer per faction |
| Range | -100 to +100 |
| Factions tracked | compact, compact.fleet, compact.corporate, compact.frontier, keth, veshan.drashan, veshan.vekhari, veshan.solketh, orryn.grand, orryn.quiet, orryn.scholar, reach.ironjaw, reach.circuit, reach.cult |
| Starting values | compact: -25. All others: 0. |
| Written by | Trade (+1 to +3 per trade at their station), Contracts (+3 to +8 for completion, -5 to -15 for betrayal), Combat (+2 to +5 for defending their interests, -3 to -10 for attacking them), Cultural (+2 to +5 for customs honored, -3 to -10 for customs violated), Consequence engine (±1 to ±5 for echoed events) |
| Read by | Trade (price modifier), Travel (patrol behavior), Contracts (job availability), Combat (enemy aggression), Cultural (event access), Narrative (story gates), Crew (morale reaction), Station (docking fees, access tier) |
| Visible | Captain's View shows top 3 relevant. Full breakdown in Reputation overlay. |
| Player meaning | "Who trusts me? Who's hunting me? What doors are open?" |
| Breakpoints | -75 (Hostile), -50 (Unwelcome), -25 (Cold), 0 (Neutral), +25 (Respected), +50 (Trusted), +75 (Allied) |

### crew_roster

| Property | Value |
|----------|-------|
| Type | List of crew objects (max 6) |
| Each crew object contains | name, civilization, role, hp, hp_max, speed, abilities[3], ship_skill, morale (0–100), loyalty_tier (stranger/trusted/bonded), loyalty_points (0–100), injured (bool), pay_rate, narrative_hooks[], opinions |
| Starting value | Empty list |
| Written by | Recruitment (add), Departure (remove — permanent), Combat (hp changes, injury), Morale system (morale shifts from player choices), Loyalty system (loyalty point accumulation), Narrative (hook updates) |
| Read by | Combat (party composition, ship abilities), Trade (cultural knowledge grants), Cultural (knowledge level per civ), Narrative (loyalty missions, dialogue), Ship (ability slots), Crew screen (display) |
| Visible | Crew screen list view + detail view. Captain's View shows "X/Y fit." |
| Player meaning | "Who do I have? What can they do? Are they happy? What have they unlocked?" |

### crew.[name].morale

| Property | Value |
|----------|-------|
| Type | Integer |
| Range | 0–100 |
| Starting value | 40–50 (Stranger tier default) |
| Written by | Pay (+2 on time, -8 missed), Player choices aligned with crew values (+2 to +5), Player choices against crew values (-2 to -8), Cultural respect for crew's civ (+1 to +3), Cultural violation of crew's civ (-3 to -6), Combat outcomes (shared danger +1 to +3, failure -2 to -4), Gifts/personal gestures (+3 to +8) |
| Read by | Combat (stat modifier: <30 = -10% hit, >70 = +10% hit), Ship abilities (morale <20 = ability weakened), Departure check (morale <25 for 3+ consecutive days = crew member leaves), Dialogue (morale gates personal information) |
| Visible | Hearts on crew screen. Morale number on detail view. |
| Player meaning | "Does this person want to be here? What happens if I push too hard?" |
| Critical thresholds | <25: departure risk. 30–50: functional but disengaged. 50–70: committed. >70: loyal, volunteers, shares personal info. |

### crew.[name].loyalty_tier

| Property | Value |
|----------|-------|
| Type | Enum: stranger (0–30 pts), trusted (31–65 pts), bonded (66–100 pts) |
| Written by | Loyalty point accumulation (morale staying above 50 for 10+ days: +1 pt/day. Personal quest completion: +15 pts. Major aligned choice: +5 pts.) |
| Read by | Abilities (3rd ability locked until trusted, unique ability locked until bonded), Ship skill (locked until trusted), Narrative (personal quest at trusted, loyalty mission at bonded), Dialogue (depth gates) |
| Visible | Label on crew screen. |
| Player meaning | "How deep is this relationship? What have I unlocked?" |

### ship

| Property | Value |
|----------|-------|
| Type | Composite object |
| Contains | hull_hp, hull_max, shield_hp, shield_max, weapon_power, engine_speed, cargo_capacity, quarters_tier (1–3), systems_condition (0–100%), ability_slots[3], upgrades{}, fuel |
| Starting values | hull: 1800/2000, shields: 200/250, weapons: base, engines: 2 tiles, cargo: 6, quarters: tier 1, systems: 70%, abilities: [Volley], fuel: 4 days |
| Written by | Combat (hull/shield damage), Travel (systems degradation ~1.5–2%/day, fuel consumption), Repair (systems + hull restoration), Upgrades (stat improvements), Crew (ability slots filled by crew ship_skill) |
| Read by | Combat (all stats), Travel (speed, fuel efficiency, breakdown risk), Crew (quarters tier → morale modifier), Trade (cargo capacity) |
| Visible | Captain's View shows "Ship X%". Ship screen shows full breakdown. |
| Player meaning | "How healthy is my ship? Can I make this trip? Can I survive this fight?" |
| Critical thresholds | Systems <50%: breakdown chance per travel day. Systems <25%: guaranteed breakdown within 2 days. Hull 0: disabled (drift + emergency). |

### ship.ability_slots

| Property | Value |
|----------|-------|
| Type | List of 3 ability references |
| Filled by | Top 3 crew members by relevant ship_skill. Auto-assigned. Player can swap before combat. |
| Written by | Crew roster changes (recruitment, departure, injury). An injured crew member's ability is disabled. |
| Read by | Ship combat (available actions). |
| Visible | Ship combat screen. Crew screen shows "Ship: [ability name]" per crew. |
| Player meaning | "What can my ship do in a fight? Who makes it possible?" |

### cargo_hold

| Property | Value |
|----------|-------|
| Type | List of {good, quantity, contraband_flag, origin_civ} |
| Max entries | Limited by ship.cargo_capacity |
| Written by | Trade (buy/sell), Contracts (delivery cargo loaded/unloaded), Combat (loot added, cargo jettisoned on retreat), Confiscation (patrol inspection) |
| Read by | Trade (what do I have to sell?), Travel (patrol inspection risk if contraband), Combat (jettison option on retreat), Contracts (delivery completion check) |
| Visible | Market screen shows "Your hold" column. Cargo overlay accessible from anywhere. |
| Player meaning | "What am I carrying? Is any of it going to get me in trouble?" |

### day

| Property | Value |
|----------|-------|
| Type | Integer |
| Range | 1 – uncapped |
| Starting value | 1 |
| Written by | Travel (advances by lane distance in days) |
| Read by | Keth seasonal cycle (day % 360 determines season, day % 90 determines season phase), Crew pay (due every 30 days from recruitment), Contract deadlines, Veshan debt aging (debts older than 30 days generate pressure) |
| Visible | Captain's View persistent bar. |
| Player meaning | "How much time has passed? When is pay due? What season is it?" |

### keth_season

| Property | Value |
|----------|-------|
| Type | Derived from day counter. Enum: emergence (day 0–89), harvest (90–179), dormancy (180–269), spawning (270–359). Cycles every 360 days. |
| Written by | Automatic (derived from day). |
| Read by | Trade (Keth station prices shift by season), Cultural (customs change by season, access restrictions during spawning), Lane encounters (Keth convoy frequency), Narrative (seasonal events) |
| Visible | Reputation overlay shows season + days remaining. Crew Keth member mentions it contextually. At Keth Lv.0: invisible. At Lv.1+: visible. |
| Player meaning | "What can I do in Keth space right now? When do the good margins hit?" |

### veshan_debts

| Property | Value |
|----------|-------|
| Type | List of {house, weight (minor/standard/major), direction (owed/held), description, day_created} |
| Written by | Veshan interactions (trade, gifts, hospitality, combat aid, services). Each creates a debt entry. Calling in a debt removes it. Defaulting removes it + reputation penalty. |
| Read by | Reputation (honoring/defaulting shifts standing), Contracts (debts callable for access/aid/intel), Cultural (Veshan interactions reference the ledger), Narrative (debts create story obligations), Debt aging (debts >30 days old generate pressure events via consequence engine) |
| Visible | Reputation overlay shows debt count per house. Debt Ledger overlay shows full list. |
| Player meaning | "What do I owe the Veshan? What do they owe me? When should I call in a favor?" |

### cultural_knowledge.[civ]

| Property | Value |
|----------|-------|
| Type | Integer per civilization |
| Range | 0–3 |
| Civilizations | compact, keth, veshan, orryn, reach |
| Starting value | All 0 |
| Written by | Station visits (+progress toward next level), Crew from civ (grants minimum Lv.1), Cultural events completed (+progress), Loyalty missions completed (+progress toward Lv.3) |
| Read by | Trade (restricted goods access), Cultural (interaction options, misstep risk), Encounters (options visible/hidden based on level), Narrative (inner circle access at Lv.3) |
| Visible | Crew detail view shows per-civ level. Cultural interactions show required level. |
| Player meaning | "How well do I know this civilization? What can I do here that I couldn't before?" |

### investigation_progress

| Property | Value |
|----------|-------|
| Type | Integer (0–10) + list of found beat IDs |
| Written by | Exploration (discovering beat locations), Reputation gates (some beats require standing thresholds), Crew loyalty missions (some reveal connected info), Consequence triggers (some beats appear based on player actions) |
| Read by | Narrative (next beat availability, endgame path), Journal (display found leads), Contracts (conspiracy-related jobs gate on progress) |
| Visible | Journal overlay: "X of 10 leads found" + narrative fragments per beat. |
| Player meaning | "How much do I know about why I was framed? What do I need to find next?" |

### consequence_log

| Property | Value |
|----------|-------|
| Type | List of {action_tag, faction_tags[], severity, day, description} |
| Max size | Rolling 200 entries (oldest pruned) |
| Written by | Every significant player action across all systems. Logged automatically. |
| Read by | Encounter generation (weighted trigger tables), NPC memory (last 3 interactions per named NPC), Job board population, Price shifts, Station flavor text |
| Visible | Journal overlay shows "Recent Consequences" (last 5). Full log accessible via debug only. |
| Player meaning | Not directly visible as a list. The player feels it through NPC behavior, encounter content, and world reactions. "The world remembers what I did." |

---

## Derived States

These are computed from primary variables, not stored independently.

| State | Derived From | Meaning |
|-------|-------------|---------|
| merchant_pirate_spectrum | Weighted average of compact + keth + veshan vs reach faction standings | Overall identity position. Displayed as spectrum bar. |
| crew_fitness | Count of crew where injured == false | "How many of my crew can fight?" |
| ship_combat_ready | hull_hp > 0 AND systems_condition > 25% AND fuel > 0 | "Can my ship fight or do I need repairs?" |
| monthly_floor_cost | fuel_rate + maintenance_rate + sum(crew.pay_rate) | "How much does it cost to exist per month?" |
| station_access_tier | reputation[station.faction] mapped to breakpoint | "What can I do at this station?" |
| trade_price_modifier | reputation[station.faction] mapped to discount/surcharge table | "Am I getting a good deal or getting gouged?" |
| breakdown_risk | 0% if systems > 50%, 5%/day if 25–50%, guaranteed if <25% | "Is my ship going to fail on this trip?" |

---

## State That Does NOT Exist

To prevent scope creep, these are explicitly excluded:

| Rejected State | Why |
|----------------|-----|
| Player XP / level | No XP system. Growth comes from crew, reputation, knowledge, and ship upgrades. |
| Skill points | No skill tree. Crew abilities are fixed per role. Growth is lateral (more crew, more cultures) not vertical (bigger numbers). |
| Alignment / morality score | No alignment. The merchant-pirate spectrum is derived from reputation, not a separate moral tracker. |
| Hunger / thirst / survival meters | No survival simulation. Fuel is the only consumable resource that creates travel pressure. |
| Crew relationship graph (crew-to-crew) | Crew have opinions about player choices, not about each other. No romance system. No crew-to-crew conflict system. |
| Weather system (independent) | Sector conditions are hand-placed events, not a simulation. No weather state to track. |
| NPC schedules | NPCs are at their stations. They don't move on schedules. Orryn drifts move, but on a fixed orbital path, not an NPC AI. |
| Permanent stat bonuses from items | No equipment system beyond ship upgrades. Crew stats are fixed. No "+5 damage sword." |
| Map fog / exploration state | All stations are known from the start (the player is from this system). Lane danger ratings and cultural information are gated by knowledge, not exploration. |
