# System Laws — Star Freight

> Every mechanical system, its rules, and how it touches every other system. "Laws" not "architecture" — we define causality and consequences.

## System Index

| # | System | Purpose (one line) |
|---|--------|--------------------|
| 1 | Trade & Economy | Buy/sell goods across civilizations for profit |
| 2 | Reputation | Track standing with each civilization and faction; gate access |
| 3 | Cultural Knowledge | Learn and apply civilization customs for advantage |
| 4 | Combat | One turn-based tactical grid system — crew on foot or ships on the field |
| 5 | Travel & Lanes | Move between stations, encounter generation |
| 6 | Crew | Recruit, manage, retain crew members with loyalty and morale |
| 7 | Ship | Maintain, repair, upgrade your vessel |
| 8 | Contracts & Jobs | Accept and complete structured work for pay |
| 9 | Consequence Engine | Past actions generate future encounters and world changes |
| 10 | Veshan Debt Ledger | Track favors owed/given with Veshan houses |
| 11 | Investigation | Follow the disgrace conspiracy through story beats |

---

## System Definitions

### System 1: Trade & Economy

- **Purpose:** The primary way the player makes money. Buy goods where they're cheap, sell where they're expensive. Civilization-specific goods, supply/demand, and event-driven price shifts create an economic puzzle.
- **Inputs:** Player credits, cargo hold capacity, market prices at current station, cultural standing (affects prices), seasonal/event modifiers, trade permits (Compact).
- **Outputs:** Credits gained or lost, reputation shifts (some goods are politically loaded), cultural standing changes (trading respectfully vs exploitatively).
- **Resources touched:** Credits, cargo hold, reputation, cultural standing, Compact permits.
- **Player decisions enabled:**
  - What to buy and where to sell (margin calculation)
  - Whether to haul legitimate or contraband goods (risk/reward)
  - Whether to cut the Orryn out of a brokered deal (better margin, reputation cost)
  - Whether to sell Ancestor tech openly or on the black market
  - Whether to honor Veshan trade debts or default
- **Failure states:** Bought goods that crashed in price (event-driven), cargo confiscated by patrol, sold at a loss to cover emergency repairs, couldn't afford fuel/docking.
- **Interactions:** Reputation gates prices. Cultural knowledge unlocks restricted goods. Ship hold limits volume. Contracts often involve cargo. Consequence engine shifts supply/demand based on player actions.

**Economy rules:**
- ~20 trade goods. 4 universal (fuel, rations, common metals, medical supplies) + 4 civilization-exclusive per faction (16 total).
- Prices follow Portlight's model: base price per good per station, modified by supply/demand, seasonal events, reputation standing, and recent player actions.
- Buying from a civilization at good standing: -5% to -15% price. Bad standing: +10% to +25% surcharge. Neutral: base price.
- Contraband: goods that are legal in one civilization but illegal in another. Keth bio-weapons in Compact space. Ancestor tech anywhere official. Veshan weapons without a house seal.
- The Orryn broker cross-civilization trades at +20% markup but guarantee delivery and handle permits. Cutting them out saves money but requires cultural knowledge and reputation to execute yourself.

---

### System 2: Reputation

- **Purpose:** Track how every civilization and faction views the player. Gates access to stations, goods, contracts, NPCs, and story content. The merchant-to-pirate spectrum lives here.
- **Inputs:** Player actions — trades completed, contracts fulfilled or broken, cultural customs respected or violated, combat outcomes, dialogue choices, crew composition.
- **Outputs:** Standing value per faction (numeric, -100 to +100), access tier changes, price modifiers, NPC behavior changes, contract availability, story gates.
- **Resources touched:** All other systems feed into reputation. Reputation gates everything.
- **Player decisions enabled:**
  - Which civilizations to cultivate vs neglect
  - Whether to take jobs that help one faction at another's expense
  - How to handle inter-civilization conflicts (proxy wars, trade disputes)
  - Whether to pursue merchant rehabilitation or pirate ascendancy
- **Failure states:** Standing drops below a threshold → locked out of a civilization's ports/goods/contracts. Multiple civilizations hostile simultaneously → very limited options (Orryn + Reach only).
- **Interactions:** Every system touches reputation. Trade affects it. Combat outcomes affect it. Cultural interactions affect it. Crew morale reacts to it. Contracts require it.

**Reputation structure:**
- Per-civilization standing: Compact, Keth, Veshan (per-house: Drashan, Vekhari, Solketh), Orryn, Sable Reach (per-faction: Ironjaw, Phantom Circuit, Ancestor Cult)
- Breakpoints at -75, -50, -25, 0, +25, +50, +75:

| Standing | Effect |
|----------|--------|
| -75 to -50 | **Hostile.** Shoot on sight in their space. No docking. Active bounties on you. |
| -50 to -25 | **Unwelcome.** Docking allowed but surcharges, inspections, restricted goods locked, no contracts. |
| -25 to 0 | **Cold.** Base prices, limited contracts, basic goods only. |
| 0 to +25 | **Neutral.** Standard access. Prove yourself. |
| +25 to +50 | **Respected.** Price discounts, mid-tier contracts, restricted goods tier 1, named NPCs engage. |
| +50 to +75 | **Trusted.** Best prices, high-tier contracts, restricted goods tier 2, faction inner circle access, story content unlocks. |
| +75 to +100 | **Allied.** Faction treats you as one of their own. Unique contracts, faction aid in emergencies, endgame story paths. |

- Standing shifts are small per action (+1 to +5 typical) with occasional large swings for major events (+10 to +20). Cross-civilization actions create opposing shifts: helping Veshan in the cold war hurts Compact standing.
- The player's overall position on the merchant-pirate spectrum is derived from the portfolio: high Compact + low Reach = merchant, high Reach + low Compact = pirate, balanced = independent.

---

### System 3: Cultural Knowledge

- **Purpose:** Represent the player's understanding of each civilization's customs. Knowing a culture unlocks better trades, smoother interactions, and avoids costly missteps.
- **Inputs:** Time spent in a civilization's stations, crew members from that civilization (passive knowledge), specific cultural events experienced, investigation/study actions.
- **Outputs:** Cultural knowledge level per civilization (0–3), dialogue options unlocked, custom navigation success rate, restricted interaction access.
- **Resources touched:** Reputation (knowledge prevents missteps), trade (knowledge unlocks restricted goods), crew (crew members are knowledge sources).
- **Player decisions enabled:**
  - Whether to invest time learning a culture or brute-force it with money/reputation
  - Which crew member to consult before a cultural interaction
  - Whether to attempt an unfamiliar custom (risk) or decline (safe but missed opportunity)
- **Failure states:** Attempting a cultural interaction without sufficient knowledge → misstep → reputation hit + possible material cost. Ignoring cultural requirements entirely → locked out of the most profitable opportunities.
- **Interactions:** Crew members grant passive knowledge of their home civilization. Reputation gates which cultural events you can access. Trade benefits scale with knowledge.

**Knowledge levels:**

| Level | Name | How Earned | Effect |
|-------|------|-----------|--------|
| 0 | **Ignorant** | Default | No custom navigation. Risk of missteps at every interaction. Must rely on crew or skip. |
| 1 | **Aware** | 3+ station visits OR crew member from civ | Basic customs known. Can navigate simple interactions. Misstep risk reduced. |
| 2 | **Conversant** | 8+ visits + crew member + 2 cultural events completed | Complex customs accessible. Can negotiate directly. Restricted goods tier 1. |
| 3 | **Fluent** | Crew loyalty mission complete + 15+ visits + reputation 50+ | Inner circle access. Master-level negotiation. Restricted goods tier 2. No misstep risk. |

**Per-civilization cultural mechanics:**

- **Compact — Permits:** Licenses purchased at Compact stations. Each permit unlocks a cargo type or route. Cost: credits + standing requirement. Knowledge level determines which permits are visible on the menu.
- **Keth — Seasonal Protocols:** 4 seasons cycle on a fixed calendar. Knowledge level determines how much the player knows about current-season customs. At level 0, the player doesn't even know which season it is without asking crew.
- **Veshan — Debt Ledger:** See System 10. Knowledge level determines whether the player understands the weight of debts being offered. At level 0, you might accept a debt that's far more costly than it appears.
- **Orryn — The Telling:** Negotiation ritual. Knowledge level determines available Telling strategies. At level 0, you can only do a basic honest statement. At level 3, you can frame truth strategically for maximum advantage.
- **Reach — Rep Reading:** No formal culture, but knowledge lets you read pirate faction dynamics. At level 0, you can't tell Ironjaw from Phantom Circuit. At level 3, you know who's feuding, who's allied, and who's about to betray whom.

---

### System 4: Combat

- **Purpose:** One unified turn-based tactical grid system for all violent encounters. The same engine handles crew on foot (ground theater) and ships in space (space theater). Ships are characters — they move on the grid, attack, use abilities, take cover behind asteroids, and have HP in the thousands. The rules are the same. The scale changes.
- **Inputs:** Theater context (ground or space), combatant roster (crew members or ships), gear/upgrades, terrain, enemy composition.
- **Outputs:** Victory/defeat/retreat, injuries (ground) or ship damage (space), loot/salvage, reputation shifts, narrative consequences.
- **Resources touched:** Crew HP/injuries, ship HP/systems, credits (loot/salvage), reputation.
- **Player decisions enabled:**
  - Positioning (cover, flanking, chokepoints — asteroids and debris in space, crates and walls on the ground)
  - Ability usage and targeting
  - Retreat timing (before it's too late vs pushing for victory)
  - Post-combat choices (spare/capture/loot/execute — reputation implications)
  - Boarding decision in space (close to adjacent → transition to ground theater inside the enemy ship)
- **Failure states:** All units down → forced retreat. Ground: crew takes injuries that persist until healed. Space: ship disabled, drift to nearest station (expensive repair). Retreating costs loot/objectives.
- **Interactions:** Crew morale affects combat stats. Cultural knowledge affects post-combat options (Veshan honor protocols). Reputation determines enemy behavior. Consequence engine logs outcomes. Contracts trigger combat encounters.

**Core combat rules (shared across both theaters):**

- **Grid:** 8x8 tiles. Same size for ground and space. Keeps fights fast regardless of theater.
- **Units:** Ground = crew members (3–4 per fight, HP in the tens/hundreds). Space = ships (yours + enemies, HP in the thousands). A unit is a unit — it occupies a tile, has HP, has abilities, has a speed stat, attacks, and takes damage.
- **Turn order:** Speed stat determines initiative. Each unit gets Move + Action per turn.
- **Cover:** Half cover (+25% dodge) and full cover (+50% dodge, blocks line of sight). Flanking ignores cover. Ground cover: walls, crates, consoles, doorways. Space cover: asteroids, debris, station structures, nebula clouds.
- **Abilities:** Each unit has 3 abilities + a basic attack. Abilities are what make each unit distinct. Ground crew abilities come from their role. Ship abilities come from the ship class + crew upgrades.
- **Retreat:** Available any turn. Unit(s) move to exit tile and leave. Cost: any loot/objective on the field is lost. No permadeath.
- **Fights resolve in 5–8 turns.** If a fight drags longer, the encounter design is wrong.

**Ground theater specifics:**

- Party: 3–4 crew members selected from your roster.
- Terrain types: station corridors (chokepoints, doors), cargo bays (open with crate cover), planet surfaces (open, environmental hazards), ship interiors (tight, boarding context).
- Crew roles and abilities:

| Role | Abilities | Specialty |
|------|-----------|-----------|
| Fighter | Charge (close distance + attack), Shield Wall (adjacent ally gains cover), Intimidate (enemy loses next action on failed resist) | Frontline, damage, control |
| Medic | Field Patch (heal HP), Stimulant (target gets extra action next turn), Triage (remove injury, 1/fight) | Healing, tempo |
| Tech | Hack (disable enemy tech/turret/door), EMP Grenade (AoE stun, 1 turn), Overload (boost ally damage for 2 turns) | Utility, area control |
| Face | Negotiate (attempt to end combat via persuasion, reputation-gated), Distract (target attacks Face instead of allies), Rally (party-wide +hit chance) | Social, support |

- Enemies have visible behavior patterns: rushers close distance, snipers hold back, hackers disable your tech, heavies absorb damage. Reading the pattern is the puzzle.

**Space theater specifics:**

- Units: Ships. Your ship + allied ships (if any) vs enemy ships. Each ship is one unit on the grid, just like a crew member on the ground. Ships have HP in the thousands, hit harder, and move differently — but the grid, cover, turns, and ability structure are identical.
- Terrain types: open space (no cover), asteroid fields (abundant cover, movement obstacles), debris fields (scattered cover, salvage), near-station (station structures as cover, possible reinforcements), nebula (limited visibility, blocks long range).
- Ship stats: Hull HP (thousands), Shields (absorb damage first, regen slowly per turn), Weapon Power (damage output), Engine Speed (tiles per move, dodge chance). These are the ship's equivalent of crew member stats.
- Ship abilities: Each ship has 3 abilities determined by ship class + crew-granted improvements. Crew doesn't act as separate roles on the grid — instead, having a good engineer means your ship has a Repair ability. A skilled gunner means your ship has a Barrage ability. The crew determines what your ship CAN do, but in combat, the ship is the unit.
- Example ship ability sets:

| Ship Type | Abilities (determined by class + crew) | HP Scale |
|-----------|---------------------------------------|----------|
| Player's ship (light) | Volley (standard attack), Repair (heal hull, crew: engineer), Evasive Burn (boost dodge, crew: pilot) | 2,000–5,000 |
| Pirate raider | Strafe (move + attack), Grapple (adjacent: lock target, setup for boarding), Overclock Guns (double damage, 1 turn) | 1,500–3,000 |
| Compact patrol | Formation Fire (bonus if adjacent to ally), Shield Boost (double shields 1 turn), Call Reinforcements (spawn ally after 3 turns) | 3,000–6,000 |
| Veshan warship | Ram (close + heavy damage to both), Honor Challenge (1v1 duel lock, +damage both sides), Heavy Broadside (high damage, can't move) | 5,000–8,000 |
| Orryn runner | ECM Burst (AoE: all enemies -accuracy 2 turns), Afterburn (double move, no attack), Decoy Deploy (fake unit, draws fire) | 1,000–2,000 |
| Keth swarm drone | Self-Destruct (sacrifice for AoE damage), Regenerate (organic hull heals over time), Swarm Coordination (+damage per adjacent ally) | 500–1,000 each |

- **Boarding:** When your ship is adjacent to an enemy ship, you can initiate boarding. Combat pauses in the space theater and transitions to the ground theater — your crew vs the enemy crew inside their ship. Ship damage state persists (a disabled ship can't flee during boarding). After boarding resolves, space combat resumes or ends depending on outcome.

**How crew improves ships (not roles — upgrades):**

The crew doesn't "fill roles" during ship combat. Instead, crew members passively improve your ship's capabilities based on their skills. This works like equipment:

| Crew Skill | Ship Improvement |
|-----------|-----------------|
| Skilled gunner aboard | Ship gains access to Barrage ability (AoE attack) |
| Skilled pilot aboard | Ship gains Evasive Burn ability + movement bonus |
| Skilled engineer aboard | Ship gains Repair ability + shields regen faster |
| Skilled face/captain aboard | Ship gains Hail ability (negotiate mid-combat, reputation-gated) |
| High crew morale | Ship gets flat stat bonus (+accuracy, +dodge) |
| Low crew morale | Ship gets stat penalty |
| Crew injuries | Corresponding ship ability weakened or disabled until healed |

This means your ship's combat performance reflects your crew composition without the crew acting as separate units on the grid. Lose your engineer to an injury? Your ship can't repair mid-fight until they're healed. Recruit a legendary Veshan gunner? Your ship hits like a warship.

---

### System 5: Travel & Lanes

- **Purpose:** Moving between stations. Travel takes time, costs fuel, and generates encounters. The lanes are alive.
- **Inputs:** Origin, destination, route choice (some destinations have multiple routes — safe/slow vs dangerous/fast), ship speed, sector conditions, reputation (affects patrol behavior).
- **Outputs:** Travel time (measured in days), fuel consumed, encounters generated, crew morale shifts, cargo condition (some goods degrade over time or in hazards).
- **Resources touched:** Fuel, credits (fuel cost), cargo condition, crew morale, time (some contracts have deadlines).
- **Player decisions enabled:**
  - Route choice (safe vs fast vs scenic)
  - How to respond to lane events (investigate, ignore, evade, fight)
  - Whether to stop at a waypoint station or push through
  - Whether to answer distress calls (genuine or trap?)
- **Failure states:** Ran out of fuel → drift (expensive rescue, reputation cost). Ship breakdown on lane → emergency repair (costs parts or credits, delays). Ambushed by pirates → combat.
- **Interactions:** Reputation determines who attacks you on lanes and who leaves you alone. Consequence engine seeds lane events based on past actions. Seasonal conditions (Keth) affect certain routes. Ship condition affects travel speed and breakdown risk.

**Lane rules:**
- ~40 lanes connecting ~20 stations. Each lane has: distance (travel days), danger rating (encounter chance per day), terrain type (open space, asteroid field, nebula, debris field), faction control (who patrols it).
- Encounter chance: base 15% per travel day, modified by danger rating and sector conditions. Encounters drawn from a weighted table: pirate ambush, patrol check, distress signal, merchant convoy, debris/salvage, environmental hazard, NPC sighting, faction event.
- Fuel: consumed per travel day. Fuel is a trade good — buy at stations, price varies. Running dry is survivable but expensive and humiliating.
- Sector conditions: solar storms (slow travel, shield damage), trade booms (more merchants on lanes, fewer pirates), blockades (patrols increase, smuggling risk up), festival periods (specific lanes busier).
- Portlight's sea culture engine maps directly: route-specific encounters, NPC sightings, spacer superstitions, crew mood narration, weather/hazard narration.

---

### System 6: Crew

- **Purpose:** Recruit, manage, and retain crew members. Crew is the player's primary resource — they fight on the ground, improve the ship in space, navigate cultures, open doors, and have opinions.
- **Inputs:** Recruitment events, player choices, reputation shifts, cultural interactions, combat outcomes, pay/living conditions.
- **Outputs:** Ground combat capability, ship ability upgrades (passive), cultural knowledge bonuses, faction access, dialogue/story content, morale state.
- **Resources touched:** Credits (crew pay), reputation (crew backgrounds open doors), cultural knowledge (crew grants passive knowledge), combat stats (ground and ship), story progression.
- **Player decisions enabled:**
  - Who to recruit (each crew member opens different civilization access AND changes your ship's combat abilities)
  - How to handle crew disagreements (they have opinions about your choices)
  - Whether to pursue crew loyalty missions (time + risk investment for deep rewards)
  - Whether to keep crew members whose civilizations you've alienated
- **Failure states:** Crew morale drops too low → crew member leaves (permanent). Crew member's civilization becomes hostile to you → loyalty crisis (must choose). Crew killed in combat → permanent loss (rare, only on critical failures).
- **Interactions:** Crew feeds into every system. Ground combat (party composition), ship combat (passive ability grants), culture (knowledge bonuses), reputation (crew presence affects faction reactions), ship (crew skills determine available ship abilities), trade (crew contacts unlock deals).

**Crew rules:**
- Max active crew: 4 (in ground combat). Total crew on ship: 6. Player selects ground combat party from available crew. All 6 contribute passively to ship combat abilities.
- Each crew member has: home civilization, role (fighter/medic/tech/face), 3 ground abilities, personal stats (HP, speed, skill), morale (0–100), loyalty tier (stranger → trusted → bonded), ship skill (what they contribute to the ship in space combat).
- Morale: affected by pay, living conditions (ship quality), player choices that align or conflict with their values, cultural respect shown to their civilization. Low morale: stat penalties, refuse certain orders, eventually leave. High morale: stat bonuses, volunteer for dangerous actions, share personal information.
- Loyalty tiers:
  - **Stranger (0–30):** Basic functionality. Won't share personal info. May leave if morale dips.
  - **Trusted (31–65):** Full ability access. Shares cultural insights. Stays through rough patches. Personal quest becomes available.
  - **Bonded (66–100):** Peak stats. Unique ability unlocked. Loyalty mission available. Will follow you into the endgame regardless of faction politics. Has opinions about the ending.
- Pay: Crew expects regular pay. Amount scales with loyalty tier (strangers are cheap, bonded crew knows their worth). Failing to pay → morale hit. Overpaying → small morale boost but the money matters more.
- Recruitment: Crew found at stations, in encounters, through contracts. Each has a recruitment condition (reputation threshold, story event, cultural interaction). You can't have everyone — some crew members are mutually exclusive (the Compact defector won't serve alongside a known pirate).

---

### System 7: Ship

- **Purpose:** The player's vessel. Transport, home, combat unit, and money pit. Ship condition affects everything. In space combat, the ship IS you — it's your character on the grid.
- **Inputs:** Credits (repairs, upgrades, fuel), combat damage, travel wear, cargo load, crew composition (determines available ship combat abilities).
- **Outputs:** Travel speed, combat stats (HP, shields, weapons, engines), cargo capacity, crew quarters quality (morale modifier), breakdown risk, available ship abilities in combat.
- **Resources touched:** Credits (maintenance is constant), combat (the ship is the combat unit in space), travel (speed, fuel efficiency), crew (quarters quality affects morale, crew skills unlock ship abilities).
- **Player decisions enabled:**
  - What to upgrade vs what to defer (shields or weapons? cargo hold or crew quarters?)
  - Whether to do full repairs or patch and fly (cost vs breakdown risk)
  - Whether to invest in a better ship eventually (major purchase, late-game)
  - Crew recruitment choices directly affect ship combat potential
- **Failure states:** System breakdown on a lane (emergency repair cost + delay). Hull breach in combat (crew injury risk). Total ship loss (fail state — but recoverable via insurance/debt, not game over).
- **Interactions:** Ship quality affects travel, combat, crew morale, and maintenance costs. Better ship = more options but higher upkeep. Crew composition determines which of the ship's 3 ability slots are filled and with what. The "scrappy survival" pillar means the ship is always slightly worse than what you need.

**Ship rules:**
- Ship stats: Hull HP (thousands), Shield HP (absorbs damage first), Weapon Power (base damage), Engine Speed (tiles per move + dodge), Cargo Hold (units), Crew Quarters (quality tier 1–3), Systems Condition (0–100%, affects breakdown chance).
- Starting ship: low everything. Functional but embarrassing. Quarters tier 1, small hold, weak weapons. ~2,000 hull HP.
- Upgrades: purchased at shipyards (Compact orbital, Veshan citadel, Reach Boneyard). Each system upgraded independently. Costs scale steeply — the first upgrade is affordable, the third is a major investment.
- Ship ability slots: 3 slots. Each slot is filled by a crew member's ship skill. No crew with engineering skill = no Repair ability in ship combat. This makes crew recruitment a ship-building decision as much as a ground combat decision.
- Maintenance: Systems Condition degrades with travel and combat. Below 50%: breakdown chance per travel day. Below 25%: guaranteed breakdown within 2 travel days. Repair cost scales with severity. Deferred maintenance is a trap that catches up.
- Fuel: consumed per travel day. Fuel efficiency improves with engine upgrades.
- New ship: available late-game. 2–3 ship classes (fast/light, balanced, heavy/slow). Costs a fortune. Not required but changes the experience significantly. Different classes have different base stats and ability affinities.

---

### System 8: Contracts & Jobs

- **Purpose:** Structured work with defined objectives, pay, and consequences. The job board is the player's menu of opportunity.
- **Inputs:** Station job board (procedurally generated + hand-placed story contracts), player reputation (gates which jobs appear), civilization relationships (cross-faction jobs).
- **Outputs:** Credits, reputation shifts, story progression, loot, crew recruitment opportunities.
- **Resources touched:** Credits, reputation, cargo hold (delivery jobs), time (deadlines), crew (some jobs require specific roles or cultural knowledge).
- **Player decisions enabled:**
  - Which jobs to take (risk/reward/reputation calculation)
  - Whether to take multiple jobs on the same route (efficient but complex)
  - How to complete a job (violent vs diplomatic where the job allows)
  - Whether to betray a contract (take the cargo, skip the delivery, sell it yourself — pirate lean)
- **Failure states:** Contract failed (target escaped, cargo lost, deadline missed) → no pay, possible reputation penalty with the posting faction. Contract betrayed → large reputation penalty with posting faction, possible bounty placed on you.
- **Interactions:** Contracts drive the player into trade routes, combat encounters, and cultural interactions. They're the connective tissue between all other systems.

**Contract types:**

| Type | Objective | Pay Range | Reputation Lean | Combat Chance |
|------|-----------|-----------|-----------------|---------------|
| Trade run | Deliver cargo A→B | Low-Med | Neutral | Lane risk only |
| Bounty | Capture/kill target | Med-High | Depends on target | High (space + possible boarding) |
| Smuggling | Move contraband past patrols | Med-High | Pirate lean | Evasion, sometimes combat |
| Escort | Protect NPC ship on a route | Med | Clean lean | High (space) |
| Faction errand | Deliver message, negotiate deal, retrieve item | Low-Med | Faction-specific | Varies |
| Proxy war | Run ops against a rival faction | High | Complex (helps one, hurts another) | High |
| Salvage | Extract Ancestor tech from ruins | High | Neutral (selling it has lean) | Hazards + combat |
| Investigation | Follow a disgrace conspiracy lead | None (story reward) | Varies | Varies |

- Job boards refresh when the player docks. Available jobs depend on: station location, player reputation with the station's civilization, current sector conditions, and consequence engine state.
- Deadlines: Some contracts have time limits (bounty targets move, cargo is perishable, faction errands are urgent). Missing a deadline = contract failure.
- Stacking: Player can hold up to 3 active contracts simultaneously. Encourages combining jobs on the same route.

---

### System 9: Consequence Engine

- **Purpose:** Make the world react to the player's history. Past actions seed future encounters, NPC behavior, and world state changes. Ported directly from Portlight.
- **Inputs:** Every significant player action — contracts completed/failed/betrayed, combat outcomes (who was spared, who was killed), trades made, cultural customs honored/violated, reputation thresholds crossed.
- **Outputs:** Triggered encounters (lane events, station events), NPC behavior changes, job board content, price shifts, faction state changes.
- **Resources touched:** All other systems. The consequence engine reads everything and writes encounter triggers.
- **Player decisions enabled:** Not directly — the consequence engine is invisible infrastructure. But the player learns that their actions have echoes. Sparing a pirate captain means she shows up later — as an ally or an enemy depending on how the relationship evolved.
- **Failure states:** None internal. The consequence engine cannot fail — it only generates content.
- **Interactions:** Feeds into travel (lane events), stations (NPC behavior), contracts (new jobs appear because of past actions), reputation (consequences can shift standing), and the investigation (conspiracy clues appear through consequence triggers).

**Consequence rules (from Portlight):**
- Actions logged with tags (faction, severity, type). Each tag can trigger future content.
- Encounter generation: ~15% chance per travel day for a consequence-seeded event. ~25% chance per station arrival.
- NPC memory: Named NPCs remember the player's last 3 interactions and adjust dialogue/behavior accordingly.
- Escalation: Repeated actions in the same direction compound. Running 5 smuggling jobs doesn't just shift reputation — it creates specific smuggling-related consequences (contacts approach you, patrols target you, rivals notice you).

---

### System 10: Veshan Debt Ledger

- **Purpose:** Track the specific favor/obligation economy with Veshan houses. A sub-system of reputation that adds mechanical depth to the most politically complex civilization.
- **Inputs:** Every interaction with Veshan NPCs — trades, gifts, hospitality accepted, services rendered, promises made.
- **Outputs:** Debts owed (by you) and debts held (owed to you). Each debt has a weight (minor/standard/major). Debts can be called in for specific favors.
- **Resources touched:** Reputation (honoring debts builds standing, defaulting destroys it), contracts (debts can be called in for jobs, access, or aid), combat (a major debt can summon Veshan allies in a fight).
- **Player decisions enabled:**
  - Whether to accept offered debts (accepting hospitality creates obligation)
  - When to call in debts you're owed (timing matters)
  - Whether to honor debts that become costly (the debt may demand something you can't afford)
  - Whether to default (reputation nuclear option)
- **Failure states:** Defaulting on a debt → massive reputation loss with that house + possible standing loss with other houses. Accumulating too many debts → you're trapped in obligations.
- **Interactions:** Cultural knowledge (System 3) determines whether you understand the weight of a debt being offered. A level 0 player might accept a major debt thinking it's minor.

**Debt rules:**
- Debt weight: Minor (a courtesy, easily repaid — share a meal, small trade favor), Standard (a real favor — route information, market access, introduction to a contact), Major (a life-altering obligation — military aid, political backing, a house vouching for you publicly).
- Calling in debts: You can ask a Veshan house to honor a debt owed to you. They will — that's the code. But calling in a major debt for something trivial is wasteful, and calling in too many debts too fast is seen as greedy.
- Debt inheritance: If you deal with multiple members of the same house, debts are shared. The house knows what the house owes and what the house is owed.
- Default consequences scale with weight: defaulting on a minor debt is embarrassing (-5 standing). Defaulting on a major debt is catastrophic (-30 standing, possible exile from Veshan space, other houses hear about it).

---

### System 11: Investigation

- **Purpose:** The narrative spine. The player uncovers the conspiracy behind their disgrace through story beats scattered across the system.
- **Inputs:** Player exploration, reputation thresholds (some leads require faction access), contracts that cross conspiracy paths, crew loyalty missions that reveal connected information.
- **Outputs:** Story content, narrative escalation, endgame path determination.
- **Resources touched:** Reputation (some leads require standing), crew (crew members have connected backstories), time (investigation competes with earning money).
- **Player decisions enabled:**
  - Whether to pursue leads when they appear (opportunity cost — time spent investigating is time not trading)
  - Who to trust with information
  - What to do with evidence (expose publicly, leverage privately, sell to highest bidder)
  - How to resolve the conspiracy in the endgame
- **Failure states:** Not a fail state — investigation is optional content with story rewards. But ignoring it entirely means the endgame is less informed (you resolve your situation without fully understanding what happened to you).
- **Interactions:** Investigation beats are seeded by the consequence engine and gated by reputation. Crew loyalty missions connect to the conspiracy. The Ancestor tech discovery in the Reach is connected to why you were framed.

**Investigation structure:**
- 10 story beats, loosely ordered. First 3 can be found anywhere. Middle 4 require specific faction access (Compact military intel, Veshan house records, Orryn information brokers, Reach salvagers who saw something). Final 3 are the revelation and endgame triggers.
- Beats are placed as discoverable content: a data chip in a derelict, an NPC who mentions your name, a contract that leads somewhere unexpected, a crew member who recognizes a name from their past.
- The conspiracy: you were framed because you stumbled onto something connected to Ancestor tech that powerful people in the Compact (and possibly other factions) wanted suppressed. The specifics don't need to be designed yet — the system design just needs to support scattered discovery and escalating revelation.

---

## Interaction Matrix

How every system touches every other system. R = reads, W = writes, T = triggers, — = no interaction.

|  | Trade | Rep | Culture | Combat | Travel | Crew | Ship | Contracts | Conseq | Debt | Invest |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Trade** | — | W | R | | | R | R | R | W | R | |
| **Rep** | R | — | R | W | R | W | | W | R | R | R |
| **Culture** | W | W | — | | | R | | R | | W | |
| **Combat** | | W | R | — | | R,W | R,W | R | W | R | R |
| **Travel** | R | R | | T | — | R | R | R | R | | R |
| **Crew** | R | R,W | W | R,W | R | — | R,W | R | R | R | R |
| **Ship** | | | | R | R,W | W | — | | | | |
| **Contracts** | T | R,W | R | T | T | R | R | — | W | R | T |
| **Conseq** | W | R | | T | T | | | W | — | | T |
| **Debt** | R | W | R | R | | R | | R | W | — | |
| **Invest** | | R | | T | R | R | | T | R | | — |

---

## Time Model

**Hybrid: event-driven + day counter.**

- Time advances in **days**. Travel consumes days. Docking at a station is "instant" (no day cost for station activities — you spend as long as you want planning).
- Keth seasons cycle on a fixed day counter (every 90 days = 1 season, 360 days = full cycle). This is the primary time-sensitive system.
- Some contracts have deadlines measured in days.
- Crew pay is due every 30 days.
- The investigation has no time pressure — beats unlock based on reputation and exploration, not clock.
- Combat is turn-based (no real-time element).

## State Model

**Major game states:**

```
STATION → TRAVEL → ENCOUNTER → COMBAT (optional) → STATION
                                    ↓
                              BOARDING (space→ground transition)
```

- **Station:** Player is docked. All station activities available (market, contracts, repair, crew, NPCs). No time pressure. The planning phase.
- **Travel:** Player is on a lane. Day-by-day narration. Events fire probabilistically. Player responds to events. Time advances.
- **Encounter:** A travel event or station event that requires player decision. Could be social (dialogue, negotiation), environmental (hazard, salvage), or hostile (combat trigger).
- **Combat (Ground):** Turn-based grid, 8x8. Crew members as units. Exits back to encounter resolution.
- **Combat (Space):** Turn-based grid, 8x8. Ships as units (same rules as ground, bigger numbers). Can transition to ground via boarding. Exits back to encounter resolution.
- **Boarding Transition:** Space combat → ground combat. Ship damage state persists. Crew moves from passive ship roles to active ground units.

## Randomness Model

- **Market prices:** Base price + deterministic modifiers (season, events, reputation) + small random variance (±5%). Player can predict prices with knowledge but not perfectly.
- **Lane encounters:** Probabilistic per travel day. Encounter type drawn from weighted table based on lane, faction control, and consequence engine state.
- **Combat:** Hit chance based on stats + positioning modifiers. Displayed to player before committing. No hidden rolls. Damage has small variance (±10%).
- **Cultural interactions:** No randomness. Success or failure based on knowledge level + player choice. The player should always know why they succeeded or failed.
- **Contract generation:** Weighted random from a pool based on station, reputation, and world state. Some contracts are hand-placed story beats.
- **Philosophy:** Randomness creates variety in encounters and markets. It never determines success in cultural or social interactions — those are knowledge/choice based. Combat randomness is visible and influenceable through positioning and abilities.

## Recovery Model

**No permadeath. No game over. Consequences compound but recovery is always possible.**

- **Combat loss (ground):** Retreat. Crew takes injuries (persist until healed at station, cost: credits + time). Objective failed.
- **Combat loss (space):** Ship disabled. Drift to nearest station (auto-travel, costs days). Repair bill. Cargo possibly lost.
- **Boarding gone wrong:** Lost the ground fight inside the enemy ship. Your crew retreats to your (damaged) ship. Enemy ship escapes. You're floating with injuries, ship damage, no prize.
- **Economic ruin:** Can't afford fuel or repairs. Emergency options: sell cargo at a loss, take an emergency loan at a Reach station (reputation cost), work a zero-cost hauling job (always available at any station, low pay, no risk).
- **Reputation catastrophe:** Locked out of a civilization. Recovery: slow standing rebuild through the Orryn (they broker reputation rehabilitation for a fee) or through crew members with ties to the hostile faction.
- **Crew loss:** Crew member leaves due to low morale. Permanent for that playthrough. Recruitment of new crew is always possible but the lost relationship is gone. Losing a crew member also removes their ship combat contribution.
- **Ship total loss:** Extremely rare (only through multiple compounding failures). Recovery: insurance payout (partial ship replacement) + debt. Sets the player back significantly but does not end the game.

## Exploit Audit

| Potential Exploit | Prevention |
|---|---|
| Trade loop (buy A here, sell there, repeat forever) | Supply/demand shifts with player actions. Buying in bulk raises price at source, selling in bulk lowers price at destination. Margins shrink if you run the same route repeatedly. |
| Reputation grinding (repeat same action for standing) | Diminishing returns. The first trade run with the Keth gives +3 standing. The fifth gives +1. Major standing gains require escalating commitment (cultural events, loyalty missions, risky contracts). |
| Debt exploit (accumulate Veshan favors, never repay) | Veshan houses track debt age. Unpaid debts older than 30 days generate escalating pressure (requests, then demands, then enforcement). |
| Risk-free money (take only safe contracts forever) | Safe contracts pay poorly. Ship maintenance and crew pay create a floor cost that safe contracts barely cover. Progress requires taking risks. |
| Cultural cheese (send crew member to handle all interactions) | Crew member grants passive knowledge but the player must still make choices. Some interactions require the captain specifically. Crew members can advise but not substitute. |
| Hoard Ancestor tech (collect everything, sell at peak) | Ancestor tech is flagged cargo. Holding it generates consequence engine events (factions come looking for it). The longer you hold it, the more dangerous it becomes. |
| Ship combat stacking (recruit all combat-skilled crew, ignore culture) | Best trade opportunities require cultural knowledge, which requires culturally diverse crew. Min-maxing combat crew means worse trade margins and locked-out content. |

---

## Unresolved Questions

- Exact stat formulas for combat (HP pools, damage numbers, hit chances). Deferred to Numbers Ledger.
- How many ship ability combinations are possible? If 6 crew each contribute a skill, and the ship has 3 slots, which 3 win? Highest skill? Player choice? Role priority?
- Does the player character have a fixed role (Captain/Face) or can they specialize? Leaning toward fixed Captain with unique abilities in both theaters.
- Save system: manual save at stations only? Auto-save per day? Save anywhere?
- How does the Orryn Telling work as an actual interaction mechanic? Dialogue tree? Stat check? Player-composed statement?
- Are there ship-to-ship encounters that DON'T involve combat? (Merchant convoys, Orryn drifts passing, Compact patrol hailing for inspection — resolved socially.) Yes — these are encounter events resolved through the social/cultural systems, not the combat grid.
- How many total enemy types (ground + ship) are needed? Content budget question.

## Contradictions Discovered

- "Crew max 4 in ground combat but 6 on ship" — 2 crew are always benched during ground fights. They should either provide passive bonuses from the bench or there needs to be a rotation reason (injuries forcing substitution). In space combat this isn't an issue — all 6 contribute passively.
- "Investigation is optional" but "the conspiracy is connected to the Ancestor tech which is the endgame MacGuffin" — if the player ignores investigation, the endgame needs a fallback path that still makes narrative sense.
- "No busywork" vs "ship maintenance is constant" — maintenance must feel like a meaningful decision (defer repairs to buy cargo = risk/reward) not a tax. If it ever feels like busywork, reduce the frequency.
- Ship ability slot selection (3 from 6 crew) needs a clear rule. If the player can't choose, it feels arbitrary. If they can choose freely, it's a pre-combat loadout step that might feel like busywork. Best option may be: top 3 crew by relevant skill auto-fill, player can swap before combat.

## What Must Be Proven Next

- Progression & Economy: numbers for all of this. Trade good prices, crew costs, ship maintenance, upgrade costs, contract payouts.
- Encounter proof: one ground combat and one space combat on the same 8x8 grid — showing how ships-as-characters plays.
- Economy proof: 3 trade runs across different civilizations showing how reputation + cultural knowledge affect margins.
- Veshan Debt Ledger proof: one interaction sequence showing debt creation, accumulation, and being called in.
