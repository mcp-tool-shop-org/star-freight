# Campaign State / Progression Economy — Star Freight

> This doc defines the shared variables that trade, combat, and narrative all manipulate — and proves they form a loop, not three parallel tracks. If any layer feels like a side activity, the design is broken.

## The Three-Layer Loop

```
         TRADE
        ↗     ↘
    PLOT ←——→ TACTICS
```

**Trade feeds tactics:** Money buys ship upgrades, crew gear, healing, and fuel. A rich player has more combat options. A broke player fights desperate.

**Tactics feed plot:** Combat outcomes shift reputation, which gates narrative content. Sparing a pirate captain opens a story door. Destroying a Veshan warship closes one. The investigation beats are scattered behind faction access that combat helps or hinders.

**Plot feeds trade:** Narrative progression opens new trade routes, civilizations, and contacts. A crew loyalty mission in Keth space unlocks restricted bio-goods. The investigation leads you to stations you wouldn't visit for trade alone. Reputation thresholds (earned through the full loop) unlock the best margins.

**The proof:** At no point should the player be able to advance meaningfully by engaging with only one layer. A pure trader who avoids all combat will get ambushed on profitable routes and can't complete bounties. A pure fighter who ignores trade can't afford repairs or upgrades. A player who chases only the investigation will run out of money and standing. The loop must be tight enough that engaging with one layer naturally demands the other two.

---

## Shared Campaign Variables

These are the variables that all three layers read and write. They are the game's true state.

| Variable | Type | Who Writes | Who Reads | Why It Matters |
|----------|------|-----------|-----------|----------------|
| **Credits** | Integer | Trade (margins), Contracts (payouts), Combat (loot/salvage), Narrative (story rewards) | Trade (purchasing), Ship (repairs/upgrades/fuel), Crew (pay), Cultural (permit costs, gifts, bribes) | The universal resource. Everything costs money. Money comes from all three layers. |
| **Reputation (per faction)** | Integer (-100 to +100) | Trade (who you deal with), Combat (who you fight/spare), Cultural (customs honored/violated), Contracts (completed/betrayed), Narrative (story choices) | Trade (price modifiers, goods access), Combat (who attacks you), Travel (patrol behavior), Contracts (job availability), Narrative (story gates), Crew (morale reactions) | The universal gate. Every layer shifts it. Every layer is gated by it. |
| **Crew Roster** | Collection | Recruitment (narrative + reputation-gated), Combat (injuries/death), Morale (departures) | Combat (party + ship abilities), Trade (cultural knowledge → better margins), Narrative (loyalty missions, dialogue, cultural lens), Ship (ability slots) | The player's primary asset. Crew composition determines capability in all three layers simultaneously. |
| **Ship Condition** | Composite (hull, shields, weapons, engines, systems %) | Combat (damage), Travel (wear), Ship (repairs/upgrades) | Combat (stats + abilities), Travel (speed, breakdown risk), Trade (cargo capacity), Crew (quarters quality → morale) | The persistent constraint. Ship state carries across all activities. Damage in combat affects trade range. Deferred repairs increase travel risk. |
| **Cultural Knowledge (per civ)** | Integer (0–3) | Station visits, Crew (passive), Cultural events, Loyalty missions | Trade (restricted goods, negotiation bonuses), Cultural interactions (custom navigation), Narrative (inner circle access) | The skill tree equivalent. Growth is earned through engagement with specific civilizations across all layers. |
| **Cargo Hold** | Inventory (goods + contraband flags) | Trade (buying), Salvage (looting), Contracts (delivery cargo) | Trade (selling), Travel (patrol inspection risk), Combat (boarding loss risk), Narrative (contraband triggers consequence events) | The risk-reward container. What you carry affects every layer — profitable cargo attracts pirates, contraband creates patrol tension, delivery cargo drives you to specific destinations. |
| **Day Counter** | Integer | Travel (days consumed) | Keth seasons (90-day cycle), Crew pay (30-day cycle), Contract deadlines, Consequence engine (time-sensitive triggers) | The clock. Not a hard timer but a soft pressure — seasons change, pay comes due, deadlines approach. |
| **Veshan Debt Ledger** | Collection (debts owed + held, per house) | Veshan interactions (trade, gifts, hospitality, services) | Trade (call in for market access), Combat (call in for military aid), Narrative (call in for political backing), Reputation (honoring/defaulting shifts standing) | The Veshan-specific currency. A parallel economy that operates on obligation instead of money. Unique because it's the only variable where the world initiates transactions against the player. |
| **Investigation Progress** | Integer (0–10 beats) | Exploration, Reputation gates, Crew loyalty missions, Consequence triggers | Narrative (endgame path), some late-game contracts (conspiracy-related jobs appear) | The narrative backbone. Progress is gated by the other variables (reputation, crew loyalty, exploration) ensuring the player must engage all layers to advance the story. |
| **Consequence Log** | Tagged action history | Every significant player action across all layers | Encounter generation (lane + station events), NPC behavior, Job board content, Price shifts | The memory. The world's reaction to everything the player has done. Invisible to the player but felt constantly. |

---

## Currencies

| Currency | Source (Faucet) | Sink | Visible? | Flow Rate |
|----------|----------------|------|----------|-----------|
| **Credits** | Trade margins, contract payouts, combat loot/salvage, selling Ancestor tech | Ship repairs, fuel, crew pay, upgrades, permits, gifts, bribes, docking fees, emergency loans | Yes | Net positive most sessions, but sinks are relentless. The player should always feel one bad run from trouble. |
| **Reputation (×10+ factions)** | Trades, contracts completed, customs honored, combat outcomes (sparing, honor duels), gifts, cultural events | Contracts betrayed, customs violated, faction conflicts (helping one hurts another), smuggling caught, debts defaulted | Yes (per-faction meter) | Slow accumulation (+1 to +5 typical), occasional big swings (±10 to ±20). Diminishing returns on repeated actions. |
| **Cultural Knowledge (×5 civs)** | Station visits, crew members, cultural events, loyalty missions | Not consumed — only grows. But requires sustained engagement to level up. | Yes (per-civ level) | Slow. Level 1 in ~2 hours of engagement with a civ. Level 3 requires deep investment (loyalty mission + 15 visits + rep 50+). |
| **Crew Loyalty (×6 crew)** | Respecting their values, cultural respect for their civ, fair pay, completing their personal missions | Disrespecting their values, mistreating their civ, skipping pay, forcing actions that violate their code | Yes (per-crew meter) | Slow build, fast collapse. Trust takes sessions to build. One betrayal can break it. |
| **Veshan Debts** | Accepting hospitality, receiving favors, being helped in combat | Repaying favors, honoring obligations, being called on by houses | Yes (ledger UI) | Accumulates through Veshan engagement. Pressure builds if debts age past 30 days. |
| **Ship Condition (%)** | Repairs at stations, engineer crew ability (in-combat only) | Travel wear (~2% per travel day), combat damage, environmental hazards | Yes | Constant drain. The player must choose between spending on repairs vs investing in cargo. |
| **Time (days)** | Nothing — only advances | Travel, Keth seasonal cycle, crew pay cycle, contract deadlines | Yes (day counter) | ~2-5 days per session. Keth season turns every 90 days. Crew pay every 30. Most contracts have 15–30 day deadlines. |

---

## The Loop in Practice: How Each Layer Forces the Other Two

### Trade → Tactics (money enables violence)

- Ship upgrades (weapons, shields, engines) are purchased with trade profits. A player who doesn't trade fights in a worse ship.
- Crew healing costs credits. A player who fights without trading can't afford to heal injuries.
- Fuel costs credits. A player who can't trade can't travel to combat encounters.
- The best trade routes run through dangerous lanes. Profitable cargo attracts pirates. The player doesn't choose "trade or fight" — they choose "trade AND fight."

### Tactics → Plot (violence moves the story)

- Combat outcomes shift reputation, which gates narrative content. Destroying a Compact patrol shifts you toward pirate — and toward story content only pirates can access.
- Bounty contracts (combat) are the primary way to earn large reputation swings.
- Sparing or killing named NPCs in combat triggers consequence engine events that seed story beats.
- The investigation leads sometimes require fighting: a data chip in a pirate captain's ship, a Compact officer who won't talk without being pressured.
- Crew loyalty builds through shared danger. Combat where you protect a crew member's interests (defending their homeland, honoring their culture in a fight) advances loyalty faster than anything else.

### Plot → Trade (story opens markets)

- Reputation thresholds (earned through the full loop including narrative choices) unlock restricted goods tiers. The most profitable trades require Trusted or Allied standing.
- Crew loyalty missions take you to new stations and open new contacts. A Keth navigator's loyalty mission might open restricted bio-goods access worth thousands.
- Investigation beats lead to stations the player wouldn't visit for trade alone — and those stations have trade opportunities.
- Narrative choices about Ancestor tech create trade opportunities: sell it openly (legal but low price), broker through the Orryn (higher price, neutral reputation), sell on the black market (highest price, pirate lean).
- The Veshan Debt Ledger creates trade obligations: a house calls in a debt that requires you to deliver specific goods, creating a trade run you didn't plan.

### The Binding Constraint: Crew

Crew is the variable that makes the loop mandatory. A single crew member simultaneously:
- Grants a ground combat ability (tactics layer)
- Grants a ship combat ability (tactics layer)
- Provides cultural knowledge for their home civilization (trade layer — better margins, restricted goods)
- Has a loyalty arc and personal mission (narrative layer)
- Has morale that reacts to choices across all three layers

**You cannot optimize one layer without affecting the others through crew.** Recruiting a Veshan fighter for combat means gaining Veshan cultural knowledge (trade benefit) and gaining a Veshan loyalty arc (narrative content) — but also gaining a crew member who has opinions about your choices regarding Veshan honor. Losing that crew member to low morale costs you in all three layers simultaneously.

---

## Sinks & Faucets: The Pressure Machine

The economy must keep the player in a constant state of **productive anxiety** — always enough to survive, never enough to relax.

### Recurring Sinks (the floor cost)

| Sink | Cost | Frequency | Can Skip? |
|------|------|-----------|-----------|
| Fuel | ~50 credits/travel day | Every trip | No (stranded if empty) |
| Crew pay | ~100–300 credits/crew member | Every 30 days | Yes (massive morale hit) |
| Ship maintenance | ~200–500 credits | Every 5–10 travel days | Yes (breakdown risk climbs) |
| Docking fees | ~25–100 credits | Every station visit | No (can't dock without paying) |
| Healing injuries | ~150–400 credits/injury | After combat | Yes (crew fights at reduced stats) |

**Floor cost estimate:** ~500–800 credits per 30-day cycle at early game. Scales to ~1,500–2,500 at late game (better ship, more crew, higher pay expectations).

### Faucet Targets (what the player earns)

| Source | Typical Payout | Frequency | Risk |
|--------|---------------|-----------|------|
| Safe trade run | 100–300 credit margin | Every session | Low (barely covers floor cost) |
| Risky trade run | 500–1,500 credit margin | Every 1–2 sessions | Medium (lane danger, contraband risk) |
| Bounty contract | 800–2,000 credits | Every 2–3 sessions | High (combat required) |
| Smuggling contract | 600–1,200 credits | Opportunistic | Medium-High (patrol risk, reputation cost) |
| Salvage run | 1,000–5,000 credits (Ancestor tech) | Rare | Very high (Reach danger, holding risk) |
| Faction errand | 200–500 credits | Frequent | Low-Medium |
| Escort job | 400–800 credits | Moderate | Medium (combat likely) |

**Target net income:** The player should average ~500–1,000 credits net per session in early game (after sinks), ~1,000–2,500 in mid game, ~2,000–5,000 in late game. This means they can afford one meaningful upgrade every 3–5 sessions, keeping the scrappy survival pillar alive throughout.

### The Squeeze Points

The economy has designed pressure points where the three layers collide:

1. **Early game squeeze (hours 1–3):** Credits barely cover fuel and docking. The player must take whatever contracts are available, including ones outside their comfort zone. This forces engagement with unfamiliar civilizations (trade layer), low-level combat encounters (tactics layer), and the first investigation breadcrumbs (narrative layer).

2. **Crew pay squeeze (every 30 days):** Pay is due and it's significant. The player must have earned enough in the last 30 days to cover it. Missing pay tanks morale, which reduces combat effectiveness and risks crew departure. This prevents the player from ignoring trade for too long.

3. **Ship maintenance squeeze (ongoing):** Deferred maintenance creates compounding risk. A player who spends everything on cargo and ignores repairs will eventually break down on a lane — which costs more than the repair would have, plus lost time, plus possible combat while vulnerable.

4. **Reputation gate squeeze (mid game):** The best trade margins are behind reputation gates (Trusted: +50 standing). But earning standing requires contracts, cultural events, and sometimes combat — all of which cost time and money. The player must invest in relationships before they pay off.

5. **Veshan debt squeeze (ongoing):** The Debt Ledger creates obligations that compete with the player's plans. A Veshan house calls in a debt: deliver alloy to Solketh Station within 10 days. You had planned a profitable run to Keth space. Do you honor the debt (protect Veshan standing, lose the Keth opportunity) or default (keep the profit, devastate Veshan standing)?

---

## Unlock Cadence

| Hours | What Opens Up | Through What |
|-------|--------------|-------------|
| 0–2 | Freeport (Reach), 1–2 frontier stations, basic trade goods, first crew member, tutorial contracts | Starting position |
| 2–5 | First Keth and first Compact station accessible. Second crew member. First cultural event. Basic permits available. | Trade runs + early contracts earning initial reputation |
| 5–8 | Veshan space opens (one house). Orryn Grand Drift first contact. Investigation beats 1–3 discoverable. Ship upgrade tier 1 affordable. | Reputation reaching Neutral (+25) with 2+ civs |
| 8–12 | Second Veshan house. Keth restricted goods tier 1. Orryn Quiet Drift (underworld). Crew loyalty missions unlock (Trusted tier). Pirate faction differentiation becomes clear. | Cultural knowledge level 2 in 1+ civs, crew at Trusted |
| 12–16 | All stations accessible (though some at bad standing). Investigation beats 4–7 gated by faction access. Ship upgrade tier 2. Proxy war contracts appear. Ancestor salvage runs available. | Reputation reaching Respected (+50) with 1+ civs |
| 16–20 | Inner circle access with allied civs. Restricted goods tier 2. Crew loyalty missions completable (Bonded tier). Investigation beats 8–9. Late-game ship purchase possible. | Cultural knowledge level 3, crew at Bonded, deep faction investment |
| 20–25 | Endgame content. Investigation beat 10 (revelation). Ancestor tech endgame. Final reputation-dependent narrative paths. | Full loop mastery — trade + combat + narrative investment |

---

## Upgrade Philosophy

**Lateral over linear. Wider options, not bigger numbers.**

- Ship upgrades improve capability in specific directions (more cargo OR better weapons OR faster engines), not everything at once. The player specializes their ship.
- Crew abilities unlock through loyalty, not XP. Bonding with a crew member gives you a new tactical option — not a stat boost.
- Cultural knowledge opens new trade goods and negotiation options — not higher prices for the same goods.
- Reputation opens new doors — not better versions of existing doors.
- The player at hour 20 is not 10x more powerful than at hour 2. They have 10x more options. They can trade in restricted goods, fight with a full crew of bonded specialists, navigate any culture fluently, and access any station. But a pirate ambush on a bad day still hurts.

---

## Scarcity Model

| Resource | Intentionally Scarce? | Why | What Happens if Hoarded? |
|----------|-----------------------|-----|--------------------------|
| Credits | Yes — always | Scrappy survival pillar. Comfort kills tension. | Recurring sinks prevent meaningful hoarding. A player with 10,000 credits still has 3,000/month in floor costs. |
| Cargo hold space | Yes — always | Forces trade-off decisions. Can't haul everything. | Ship upgrades can increase hold, but at the cost of other upgrades. |
| Crew slots | Yes — 6 max | Every slot is a strategic choice. Can't have all civilizations covered deeply. | Mutual exclusivity prevents collecting everyone. |
| Ancestor tech | Yes — rare | The game's most valuable commodity must feel rare. | Holding it generates consequence events (factions come looking). Scarcity is enforced by danger of holding. |
| Keth seasonal access | Yes — time-locked | Seasons create natural scarcity windows. Some goods only available during harvest. | Can't hoard time. Must plan around the calendar. |
| Veshan favors (debts owed to you) | Yes — earned slowly | Major debts are rare and valuable. | Debts expire or lose weight if held too long without being called. |
| Ship ability slots | Yes — 3 from 6 crew | Forces crew recruitment trade-offs. | Can't hoard — limited by crew roster size. |

---

## Catch-Up Mechanics

| Failure State | Catch-Up Mechanism | Cost |
|---------------|--------------------|------|
| Broke (0 credits) | Zero-cost hauling job always available at any station. Low pay (~100 credits), no risk. | Time — these jobs are slow money but keep you flying. |
| Ship wrecked (systems below 25%) | Emergency repair on credit at any station. | Debt — must repay within 30 days or reputation hit. At Reach stations, the interest rate is worse. |
| Reputation tanked with a civ | Orryn broker reputation rehabilitation. Pay the Orryn to mediate. | Credits (expensive) + Orryn standing (must be positive). Slow — restores 10–15 standing over several game-days. |
| Crew departed (morale collapse) | New crew always recruitable at stations. Never fewer than 2 available prospects at any station. | Lost relationship is permanent. New crew starts at Stranger tier. Ship abilities may change. |
| Locked out of all major civs | Sable Reach and Orryn never lock you out entirely. Freeport is always open. | Pirate path becomes the path of least resistance — which is by design. |
| All crew injured | Emergency medical at any station. | Credits. Expensive at Compact stations, cheap at Reach (but worse care — longer recovery). |

---

## Anti-Soft-Lock Rules

| Scenario | Why It Could Soft-Lock | Prevention |
|----------|----------------------|------------|
| No credits, no fuel, no cargo | Can't travel, can't trade, can't do anything | Zero-cost hauling job generates fuel + small credits. Always available. |
| Hostile with every faction | Can't dock, can't trade, can't heal | Orryn and Freeport never go below Cold standing. Minimum docking always available. |
| All crew dead or gone | Can't fight, can't navigate cultures | Solo operation is possible (reduced capability). Recruitment is always available at Freeport. Player character can fill one ground combat role alone. |
| Ship destroyed | No transport | Insurance payout. Starter-class replacement ship. Debt. Painful but not terminal. |
| Contract deadline impossible | Accepted a job you can't complete in time | Contracts can be abandoned. Reputation penalty is survivable. |
| Veshan debt spiral | Owe more than you can repay, houses pressing | Orryn can mediate debt restructuring (for a fee). Defaulting is catastrophic to Veshan standing but doesn't kill the game — it closes Veshan doors and opens pirate ones. |
| Investigation stuck | Can't reach the next beat due to reputation locks | First 3 beats are always accessible. Middle beats have multiple paths (at least 2 factions can provide each one). Final beats unlock when any combination of factions reaches Trusted. |

---

## Rubber-Banding Stance

**No rubber-banding. The world is fixed.**

- Enemies don't scale. A Veshan warship is always 5,000–8,000 HP whether you're at hour 2 or hour 20.
- Trade prices don't inflate to match the player's wallet. A rich player can exploit the same margins as a poor one.
- Contract payouts don't scale to player power. A bounty is worth what the posting faction says it's worth.
- Danger ratings on lanes are fixed. The Sable Reach is always dangerous.

**Why:** The fixed world is what makes player knowledge valuable. Learning that the Deepwell lane is safe during Keth harvest is meaningful because it's always true. A scaling world makes knowledge worthless. The player's power growth comes from options (more trade routes, more contacts, better crew), not from the world getting easier.

**The safety valve:** The player controls difficulty through choice. There are always safe, low-paying jobs available. The player who is struggling takes safe jobs until they recover. The player who is thriving takes risky jobs because the reward justifies it. This is player-driven difficulty, not system-driven scaling.

---

## Balance Targets by Stage

| Stage | Credits (wallet) | Ship HP | Crew Size | Reputation (best civ) | Cultural Knowledge (best civ) | Monthly Floor Cost | Typical Session Net |
|-------|-----------------|---------|-----------|----------------------|-------------------------------|-------------------|-------------------|
| Early (hrs 1–5) | 200–1,500 | ~2,000 | 1–2 | 0 to +25 | 0–1 | ~500–800 | +300–800 |
| Mid (hrs 5–15) | 1,000–5,000 | ~3,500 | 3–4 | +25 to +50 | 1–2 | ~1,200–1,800 | +800–2,000 |
| Late (hrs 15–22) | 3,000–12,000 | ~5,000+ | 5–6 | +50 to +75 | 2–3 | ~2,000–2,500 | +1,500–4,000 |
| Endgame (hrs 22–25) | 5,000–20,000 | ~6,000+ | 6 (bonded) | +75+ with 1–2 civs | 3 in 1–2 civs | ~2,500–3,000 | +2,000–5,000 |

**Key constraint:** Floor costs scale with capability. A late-game player with 6 bonded crew, a heavy ship, and Allied standing has a monthly nut of ~2,500 credits. They earn more, but they also spend more. The ratio of income-to-cost should stay roughly constant — the player never feels rich, only less desperate.

---

## Progression Proof: The Three-Layer Loop in Action

**Hour 6. The player has:**
- 2,200 credits
- 3 crew (Keth navigator, Reach mechanic, Compact defector)
- Ship: 2,800 hull HP, shields patched, weapons basic
- Reputation: Keth +30 (Respected), Compact -15 (Cold), Reach +20 (Neutral), Veshan 0, Orryn +10
- Cultural Knowledge: Keth level 1, others level 0
- Ship maintenance at 65% (needs repair soon)
- Crew pay due in 12 days: 450 credits

**The player's situation forces the loop:**

1. **Trade pressure:** Crew pay is due in 12 days. After pay (450) and a minimum ship repair (300), the player will have 1,450 credits. That's thin — one bad run and they can't cover next month. They need a profitable run NOW.

2. **Trade opportunity:** Keth harvest season starts in 3 days. Bio-crystal prices at the Communion Hub will spike for alloy imports. The player's Keth standing (+30, Respected) gives them a price discount. Their Keth navigator (cultural knowledge level 1) can guide the gift ritual. A load of alloy from Thorngate → Communion Hub could net 800–1,200 credits.

3. **Tactics intrusion:** The lane to Communion Hub passes through a sector where Ironjaw pirates have been active (consequence engine: player completed a Reach contract last session, Ironjaw noticed). Danger rating: moderate. The player's ship is at 65% condition. Fighting with damaged systems is risky.

4. **Tactical decision:** Repair before leaving (spend 300 credits now, travel safely) or save the money and risk the lane? The player repairs — they can't afford to lose cargo to a pirate ambush.

5. **Trade execution:** Buy alloy at Thorngate (400 credits). Travel to Communion Hub (2 days). No encounter on the lane — lucky. Arrive during harvest. Gift ritual succeeds (navigator coaching + Keth knowledge level 1). Sell alloy at festival prices: +1,100 credits. Keth standing ticks up to +33.

6. **Narrative hook:** At the Communion Hub, a Keth elder mentions that a human matching the description of a Compact intelligence officer has been asking about Ancestor tech in Keth space. This is investigation beat 4 — it only appeared because the player's Keth standing crossed +30 (Respected). The elder doesn't trust humans, but trusts the player because of their standing.

7. **Narrative → Trade feedback:** Following the investigation lead requires traveling to the Scholar Drift (Orryn), where the officer was last seen buying navigation data. The Scholar Drift is currently in the Veshan sector (mobile station). The player has 0 Veshan standing — docking at nearby Veshan stations will cost surcharges and they can't access Veshan goods. But the trip is necessary for the investigation.

8. **Tactics → Trade feedback:** On the way to the Scholar Drift, the player encounters a Veshan merchant convoy under pirate attack. Help the convoy (combat risk, possible ship damage, but earns Veshan standing) or pass by (safe, but miss the standing opportunity and the Veshan remember cowardice). The player helps — ship combat, 6 turns, takes 400 hull damage but drives off the pirates. Veshan standing jumps to +15 (one house grateful). The convoy captain offers a trade contact at House Vekhari's port (trade opportunity unlocked through combat).

9. **Loop complete:** The player started the sequence needing money (trade pressure). They made a cultural trade play (Keth harvest). They followed a narrative lead (investigation). They stumbled into combat that opened a new trade relationship (Veshan contact). All three layers fed each other. No layer was optional.

---

## Unresolved Questions

- Exact credit values for all trade goods at all stations. Deferred to Numbers Ledger, but the targets above constrain the range.
- How does Ancestor tech pricing work? It's the most valuable commodity but selling it openly is risky. Need a price structure that reflects risk: black market (highest price, pirate lean), Orryn broker (medium price, neutral), official sale (lowest price, clean lean).
- How steep is the diminishing return on repeated trade routes? Too steep and the player is forced to diversify unnaturally. Too shallow and they find one route and milk it.
- Crew pay scaling: if bonded crew demand higher pay, does that create a perverse incentive to keep crew at Trusted (cheaper but still functional)? Pay increases should be offset by bonded crew's dramatically higher combat and cultural value.
- How does the late-game ship purchase affect the economy? A heavy Veshan warship costs a fortune — is this a 5-session savings goal or a 15-session one? Leaning toward 8–10 sessions of dedicated saving, making it a major campaign milestone.

## Contradictions Discovered

- "Never feels rich, only less desperate" vs "lateral upgrade philosophy" — if the player gets wider options but never more comfortable, the late game could feel like a treadmill. The late game needs to feel qualitatively different from the early game, not just more of the same with fancier tools. The narrative escalation and faction inner-circle access must provide this qualitative shift.
- "Fixed world, no rubber-banding" vs "balance targets that scale" — the world doesn't scale but the player's floor costs do. This means a player who stops growing (plateaus on reputation, stops recruiting) will eventually drown in costs. The catch-up mechanics must account for this.
- "3 active contracts max" vs "loop forces multi-layer engagement" — if the player can only hold 3 contracts and each session is one loop, they need to be able to stack contracts efficiently. The contract system should encourage multi-objective runs (bounty on the same lane as a trade route) rather than penalizing them.

## What Must Be Proven Next

- Numbers Ledger: concrete prices for 20 trade goods across 20 stations. Margin analysis.
- Economy proof: 3 full trade runs simulated with exact numbers, showing floor cost pressure and net margins.
- Encounter proof: one combat encounter showing how ship damage creates economic pressure (the repair bill matters).
- The three-layer loop above needs to be walked through with exact numbers, not estimates.
