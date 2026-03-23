# Numbers Registry — Star Freight

> Every tunable number, its proven value, and why it's set there. Values come from the Economy Proof and Encounter Proof, not speculation. If a number wasn't tested in a proof, it's marked ESTIMATED and must be validated during the vertical slice.

---

## Economy: Starting Conditions

| Number | Value | Source | Why |
|--------|-------|--------|-----|
| Starting credits | 500₡ | Economy Proof | Covers ~6 weeks of floor costs with no income. Tight enough to force immediate work, loose enough to survive 2 bad runs. |
| Starting ship hull | 2,000 HP | Economy Proof | Low enough that combat is dangerous, high enough that one hit doesn't disable. |
| Starting ship shields | 250 HP | ESTIMATED | Absorbs one light attack before hull takes damage. |
| Starting ship systems | 70% | Economy Proof | Above the 50% breakdown threshold but close enough that deferred maintenance is immediately risky. |
| Starting ship cargo | 6 units | Economy Proof | Limits early trade runs to ~300–400₡ of cargo. Forces multiple runs to build capital. |
| Starting ship speed | 2 tiles | Economy Proof | Slow. Limits combat mobility. Engine upgrade is a meaningful investment. |
| Starting reputation (Compact) | -25 | Economy Proof | Cold tier. Surcharges, limited contracts. The disgrace is felt mechanically. |
| Starting reputation (all others) | 0 | Economy Proof | Neutral. Nobody knows you. |

## Economy: Floor Costs

| Cost | Value | Frequency | Source | Why |
|------|-------|-----------|--------|-----|
| Fuel per travel day | 25₡ | Per day of travel | Economy Proof | At 6 travel days/month average: 150₡/month. Meaningful but not crushing. |
| Ship maintenance (full repair to 85%) | 200–400₡ | Every 15–20 travel days | Economy Proof (Run 3 breakdown) | Deferred maintenance trap: emergency repair costs 2× preventive. |
| Systems degradation rate | 1.5–2% per travel day | Per day of travel | Economy Proof | Ships reach 50% (breakdown risk) in ~10–15 travel days without maintenance. |
| Crew pay (Stranger) | 80–100₡/month | Every 30 days | Economy Proof | Low entry cost for new crew. |
| Crew pay (Trusted) | 100–150₡/month | Every 30 days | Economy Proof | Meaningful increase. Worth it because Trusted unlocks ship abilities. |
| Crew pay (Bonded) | 150–200₡/month | Every 30 days | ESTIMATED | Highest tier. Offset by bonded crew's dramatically higher value. |
| Docking fee (Neutral) | 25–50₡ | Per station visit | Economy Proof | Small but adds up. |
| Docking fee (Cold/Unwelcome) | 50–100₡ | Per station visit | ESTIMATED | Surcharge makes hostile territory expensive to operate in. |
| Docking fee (Respected+) | 15–25₡ | Per station visit | ESTIMATED | Discount rewards relationship investment. |
| Monthly floor (early game, solo) | ~350₡ | Monthly | Economy Proof | Fuel 150 + maintenance 200. |
| Monthly floor (mid game, 3 crew) | ~640₡ | Monthly | Economy Proof | Fuel 130 + maintenance 140 + crew 370. |
| Monthly floor (late game, 6 crew) | ~1,200–1,500₡ | Monthly | ESTIMATED | Scales with capability. Never comfortable. |

## Economy: Income Sources

| Source | Payout | ₡/day net | Danger | Source |
|--------|--------|-----------|--------|--------|
| Safe haul (rations, basic cargo) | 150–250₡ gross | ~6–15₡ | ●○○○○ | Economy Proof Run 1 |
| Bio-crystal trade (Keth → Compact, normal) | 70–100₡ margin/unit | ~25–40₡ | ●○○○○ | Economy Proof Run 2 |
| Bio-crystal trade (harvest season) | 90–110₡ margin/unit | ~100–135₡ | ●○○○○ | Economy Proof Run 8 |
| Bounty (single target, low-mid) | 800–1,200₡ | ~60–100₡ | ●●●○○ | Economy Proof Run 5, Golden Path |
| Bounty (multi-target or escort) | 1,200–2,000₡ | ~80–130₡ | ●●●●○ | ESTIMATED |
| Smuggling / gray delivery | 350–700₡ gross | ~30–50₡ (after bribes) | ●●○○○ | Economy Proof Run 6 |
| Escort contract | 250–400₡ | ~40–60₡ | ●●○○○ | Golden Path Proof |
| Faction errand | 200–500₡ | ~30–50₡ | ●○○○○ to ●●○○○ | ESTIMATED |
| Salvage run (Ancestor tech) | 1,000–5,000₡ | Varies | ●●●●● | ESTIMATED |
| Contract stacking bonus (efficiency) | +30–50% effective ₡/day | — | — | Golden Path (3 contracts, 1 route) |

**Target income-to-floor ratio:** 1.3× to 1.8× at all stages. The player can cover costs but never coast. Active play earns 30–80% above floor. Passive play (safe hauls only) earns 5–15% above floor — survivable but stagnant.

## Economy: Major Purchases

| Purchase | Cost | When Available | What It Changes | Source |
|----------|------|---------------|-----------------|--------|
| Engine upgrade tier 1 | 800₡ | Any shipyard | +1 tile speed, +15% fuel efficiency | Economy Proof Run 9 |
| Engine upgrade tier 2 | 2,000₡ | Compact/Veshan shipyard | +1 tile speed, +15% fuel efficiency | ESTIMATED |
| Hull upgrade tier 1 | 600₡ | Any shipyard | +500 max hull HP | ESTIMATED |
| Hull upgrade tier 2 | 1,500₡ | Compact/Veshan shipyard | +800 max hull HP | ESTIMATED |
| Weapon upgrade tier 1 | 700₡ | Veshan/Reach | +30% base damage | ESTIMATED |
| Shield upgrade tier 1 | 500₡ | Compact shipyard | +200 max shields | ESTIMATED |
| Cargo hold expansion | 400₡ | Any shipyard | +2 cargo capacity | ESTIMATED |
| Crew quarters tier 2 | 600₡ | Any shipyard | +5 morale baseline for all crew | ESTIMATED |
| Crew quarters tier 3 | 1,500₡ | Compact shipyard | +10 morale baseline for all crew | ESTIMATED |
| New ship (light) | 5,000₡ | Late game | Faster, less cargo, different ability profile | ESTIMATED |
| New ship (heavy) | 8,000₡ | Late game, Veshan Allied | More hull, slower, more cargo | ESTIMATED |
| Compact trade permit (per type) | 200–500₡ + standing req | Compact stations | Unlocks a cargo category | ESTIMATED |

**Upgrade pacing target:** Player can afford first ship upgrade at hour 5–7 (3–5 sessions of saving). Second tier upgrades at hour 12–16. New ship at hour 18–22. No upgrade should feel trivial or impossibly distant.

## Combat Numbers

| Number | Value | Source | Why |
|--------|-------|--------|-----|
| Grid size | 8×8 | System Laws, Encounter Proof | Small enough for 5–8 turn fights, large enough for positioning. |
| Player ship hull (starting) | 2,000 HP | Economy Proof | See starting conditions. |
| Player ship hull (upgraded, mid) | 2,800–3,800 HP | Golden Path, Encounter Proof | Mid-game combat values used in proofs. |
| Player crew HP (Fighter) | 55–65 | Encounter Proof | Takes 2–3 enemy hits before critical. |
| Player crew HP (Tech) | 40–50 | Encounter Proof | Fragile. Needs cover and protection. |
| Player crew HP (Medic) | 35–45 | Encounter Proof | Fragile. Positioned behind frontline. |
| Player crew HP (Face) | 30–40 | Encounter Proof | Most fragile. Social role, not combat tank. |
| Basic attack damage (crew) | 12–20 | Encounter Proof | 3–5 hits to down an enemy. Fights last 5–8 turns. |
| Ability damage (Charge, etc.) | 25–42 | Encounter Proof | Abilities hit 1.5–2× basic attack. Worth using but not trivially dominant. |
| Enemy crew HP (light) | 30–40 | Encounter Proof (Strikers) | Goes down in 1–2 focused hits. |
| Enemy crew HP (heavy) | 50–60 | Encounter Proof (Shields) | Takes sustained pressure. |
| Ship damage (Volley) | 320–380 | Encounter Proof, Golden Path | ~5–6 volleys to disable a light raider. |
| Ship damage (Heavy Broadside) | 580–680 | Encounter Proof | Veshan heavy hits. 2–3 broadsides disable the player without mitigation. |
| Ship damage (Ram) | 400–500 to both | Encounter Proof | Risk/reward: closes distance but hurts yourself. |
| Heal amount (Field Patch) | 20 HP | Encounter Proof | Heals ~40–50% of a fragile crew member. Worth a turn. |
| Heal amount (Repair, ship) | 200–250 hull | Golden Path, Encounter Proof | ~6–10% of mid-game hull. Sustain, not full recovery. |
| Shield Boost | 2× shields for 1 turn | Encounter Proof | Absorbs one heavy hit. Timing is the skill. |
| Evasive Burn | +30% dodge for 1 turn | Golden Path, Encounter Proof | Negates most attacks when combined with cover. |
| Cover (half) | +25% dodge | System Laws | Standard positioning benefit. |
| Cover (full) | +50% dodge, blocks LoS | System Laws | Strong defensive position. Flanking counters it. |
| Fight duration target | 5–8 turns | All proofs | Longer = encounter design problem. Shorter = too trivial. |

## Reputation Numbers

| Number | Value | Source | Why |
|--------|-------|--------|-----|
| Standing gain per trade | +1 to +3 | Economy Proof | Small. Requires sustained engagement. |
| Standing gain per contract completed | +3 to +8 | Economy Proof | Moderate. Primary reputation builder. |
| Standing gain per cultural event | +3 to +5 | Golden Path Proof | Rewards cultural engagement. |
| Standing gain per honor challenge won | +8 to +12 (all Veshan houses) | Encounter Proof | Large. Combat reputation is valuable with Veshan. |
| Standing loss per contract betrayed | -5 to -15 | System Laws | Severe. Betrayal is costly. |
| Standing loss per cultural violation | -3 to -10 | System Laws | Scales with severity. |
| Standing loss per dishonor (Veshan retreat) | -15 to -20 (one house) + -5 to -8 (other houses) | Encounter Proof Branch C | Catastrophic for Veshan relations. |
| Diminishing returns start | After 5th identical action type | Campaign State doc | Prevents grinding. First trade +3, fifth trade +1. |
| Recovery rate (Orryn brokered rehabilitation) | +10 to +15 per instance | System Laws | Slow. Expensive. But always available. |
| Bribe standing cost (patrol) | -3 | Economy Proof Run 6 | Minor but accumulates. |

## Crew Numbers

| Number | Value | Source | Why |
|--------|-------|--------|-----|
| Recruitment signing cost | 60–120₡ | Economy Proof | Significant early game, trivial late game. |
| Morale starting value (new recruit) | 40–50 | Economy Proof | Below the "committed" threshold. Must be earned. |
| Morale loss: missed pay | -8 per occurrence | State Dictionary | Severe. Forces regular income. |
| Morale loss: cultural violation (their civ) | -3 to -6 | State Dictionary | Crew members care about their civilization. |
| Morale loss: combat failure | -2 to -4 | Economy Proof Run 9 | Failure affects the whole crew. |
| Morale loss: values-opposed choice | -2 to -8 | Economy Proof Run 6 (Kethra, gray delivery) | The gray path has crew costs. |
| Morale gain: pay on time | +2 | State Dictionary | Small but consistent. Baseline maintenance. |
| Morale gain: cultural respect (their civ) | +1 to +3 | Golden Path (Keth harvest ritual) | Rewards engaging with crew's culture. |
| Morale gain: shared danger | +1 to +3 | Golden Path (survived combat together) | Bonding through combat. |
| Morale gain: personal gesture | +3 to +8 | Golden Path (15₡ harvest gift → +5) | Small investment, large return. The human touch. |
| Departure threshold | Morale <25 for 3+ consecutive days | State Dictionary | Clear, predictable. Player can see it coming. |
| Loyalty point rate | +1/day when morale >50 | State Dictionary | Slow accumulation. Stranger→Trusted: ~30 days minimum. |
| Loyalty points: personal quest complete | +15 | State Dictionary | Major acceleration. Rewards engagement. |

## Cultural Knowledge Numbers

| Number | Value | Source | Why |
|--------|-------|--------|-----|
| Lv.0 → Lv.1 | 3+ station visits OR crew from civ | System Laws | Crew shortcut makes recruitment immediately valuable. |
| Lv.1 → Lv.2 | 8+ visits + crew + 2 cultural events | System Laws | Mid-game investment. ~3–5 hours of engagement with a civ. |
| Lv.2 → Lv.3 | 15+ visits + crew loyalty mission + rep 50+ | System Laws | Deep investment. Late game. |
| Trade price bonus at Lv.1 | -5% buy, +5% sell at that civ | ESTIMATED | Noticeable but not dominant. |
| Trade price bonus at Lv.2 | -10% buy, +10% sell | ESTIMATED | Strong. Cultural knowledge is profitable. |
| Misstep chance at Lv.0 | ~30% per cultural interaction | ESTIMATED | High enough to be scary. Crew member eliminates it. |
| Misstep chance at Lv.1 | ~10% | ESTIMATED | Reduced but not eliminated. |
| Misstep chance at Lv.2+ | 0% | ESTIMATED | Conversant = reliable. No more gambling. |

## Time Numbers

| Number | Value | Source | Why |
|--------|-------|--------|-----|
| Keth season length | 90 days | System Laws | Long enough to plan around, short enough to feel the cycle. |
| Full Keth year | 360 days | System Laws | ~12 months of player time at ~10 days/session = 36 sessions for a full cycle. |
| Crew pay cycle | 30 days | Economy Proof | Monthly. Predictable pressure. |
| Veshan debt aging pressure | 30 days | System Laws | Same cadence as pay. Debts and bills share the same rhythm. |
| Average travel days per session | 4–8 | Economy Proof | A session covers 1–2 routes of 2–4 days each. |
| Contract deadline range | 10–30 days | System Laws | Short enough to create urgency, long enough to not be frustrating. |
| Game length (main path) | ~300–450 days (15–25 hours, ~25–35 sessions) | Production Truth | Tested economy sustains this without collapse or inflation. |

---

## Tuning Knobs

Numbers marked ESTIMATED must be validated during the vertical slice. If they need adjustment, these are the safe knobs to turn:

| Knob | What It Controls | Safe Range | Danger Zone |
|------|-----------------|-----------|-------------|
| Fuel cost per day | Travel pressure | 15–35₡ | Below 15: travel is free. Above 35: movement is punishing. |
| Crew pay rates | Monthly floor cost | 60–200₡ | Below 60: crew is free. Above 200: third crew member is unaffordable. |
| Trade good margins | Income rate per run | 40–120% markup | Below 40%: trading isn't worth the trip. Above 120%: trading dominates all other income. |
| Bounty payouts | Combat income | 600–1,500₡ | Below 600: bounties aren't worth the risk. Above 1,500: bounties dominate economy. |
| Systems degradation rate | Maintenance frequency | 1–3%/day | Below 1%: maintenance is ignorable. Above 3%: every trip requires repair. |
| Reputation gain per action | Progression speed | +1 to +8 | Below +1: factions feel unreachable. Above +8: standing is trivially easy. |
| Heal cost per injury | Setback severity | 100–400₡ | Below 100: injuries are free. Above 400: one bad fight ruins the session. |
