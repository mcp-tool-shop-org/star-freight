---
title: Systems Reference
description: Crew, combat, culture, investigation, and campaign state.
sidebar:
  order: 4
---

## Campaign state

The campaign state is the single source of truth. All systems read and write it. No system talks directly to another.

| Field | Description |
|-------|-------------|
| Credits | Universal currency. Crew pay due every 30 days. |
| Hull / Shield | Ship condition. Combat writes damage. Repair costs credits at port. |
| Reputation | Per-faction and per-region standing. Gates access, prices, and recruitment. |
| Cargo | What you carry shapes routing, risk, inspection triggers, and investigation. |
| Crew | Up to 6 members. Abilities, cultural access, morale, injury state, loyalty tiers. |
| Companions | Up to 2. Passive bonuses (combat, speed, healing, evasion, trade). |
| Investigation | Fragment-based evidence threads. Five grades: rumor, clue, corroborated, actionable, locked. |

## Crew system

Crew members provide three things simultaneously:

1. **Ship abilities** — combat actions, emergency repair, navigation bonuses
2. **Cultural access** — language, customs knowledge, faction trust
3. **Narrative obligations** — personal debts, loyalties, departure conditions

Crew has morale. Morale drops from missed pay, injuries, and bad outcomes. Below threshold, crew members leave — and take their capabilities with them.

### Roster limit
Maximum six crew members. Each has a pay rate (default 50 credits per 30 days). Full crew is expensive; running lean means fewer capabilities.

### Crew pay
Every 30 days, crew pay is due. If credits are insufficient, morale drops sharply. Two missed pay periods and departures begin.

### Morale and loyalty
Crew start at 45 morale (stranger level). Loyalty progresses one-way through three tiers: Stranger (0-30 pts), Trusted (31-65 pts), and Bonded (66-100 pts). Trusted crew unlock their third ability. Bonded crew unlock loyalty missions.

### Injuries
Combat can injure crew. Injured crew cannot fight and have degraded ship abilities until they recover. Multiple injuries compound -- a crew member who keeps getting hurt becomes a liability.

## Combat system

Grid-based tactical combat on an 8x6 grid. Player ship vs enemy ship. Terrain tiles (asteroids, debris, nebula) affect positioning and targeting.

**Actions per turn:** move, attack, defend, use ability, retreat.

**Terrain effects:**
- **Asteroid** -- blocks movement and shots
- **Debris** -- half cover (+25% evasion)
- **Nebula** -- hides occupant (no targeting beyond range 1)

**Outcomes write to campaign:**
- **Victory** -- salvage credits, faction heat, possible crew injury
- **Retreat** -- jettisoned cargo, reputation as someone who runs
- **Defeat** -- seized cargo, injured crew, expensive limping

Crew abilities are sourced from the crew binding spine. Lose a crew member, and you lose their combat ability.

### Escalation
Consecutive fights in a short window trigger escalation pressure:
- Diminishing salvage returns
- Increased injury chance
- Persistent hull wear
- Higher damage threshold for heavy damage

One fight is tactical. Seven fights in a row is attrition.

## Cultural knowledge

Each civilization has social rules that affect trade, access, and conflict.

**Keth seasons** — biological calendar changes what gifts mean, when trading is appropriate, and when outsiders are restricted.

**Veshan challenge** — refusing a challenge is worse than losing. The Debt Ledger tracks favors and obligations.

**Orryn neutrality** — they broker for everyone. Information has a price. Cutting them out is cheap until you need them.

Cultural knowledge increases through crew interactions and successful cultural navigation. Higher knowledge unlocks restricted goods, better prices, and diplomatic options.

## Investigation system

Fragment-based evidence discovery. Threads accumulate clues from:
- Station visits (overhearing rumors)
- Trade (noticing cargo discrepancies)
- Combat salvage (finding debris with manifests)
- Crew interpretation (cultural context for patterns)

Fragments can be corroborated when multiple sources confirm the same thread. The investigation does not announce itself — it emerges from doing the job.

## Trade system

**Source discount** -- goods cost less at ports that produce them (local affinity > 1.0).
**Demand premium** -- goods sell for more at ports that need them (local affinity < 1.0).
**Flood penalty** -- dumping the same good repeatedly at one port degrades your sell price over time.
**Cultural gates** -- some goods require cultural knowledge to buy.
**Contraband** -- opium, black powder, and stolen cargo are only tradeable at black market ports. Extreme margins, extreme inspection risk.

The core loop: buy at source, sell at demand, but routing is constrained by fuel, faction standing, route danger, ship class requirements, and what you are willing to carry through whose territory.

## Contracts

Twenty-four contract templates across seven families:

| Family | Style |
|--------|-------|
| Return freight | Deliver goods between specific ports |
| Luxury discreet | High-value, low-profile deliveries |
| Procurement | Source specific goods for a buyer |
| Circuit | Multi-stop trade circuits |
| Smuggling | Contraband runs through dangerous territory |
| Shortage | Emergency supply during scarcity events |
| Reputation charter | Faction-aligned missions that build standing |

Contracts look simple until the paperwork catches up, the shortage changes the price, or the cargo turns out to be evidence.

## Tech

Python 3.11+. Typer CLI + Rich TUI + Textual full-screen mode. No external AI dependencies. No cloud services. Runs on your machine.

- **Engine:** `portlight.engine` -- campaign state, crew, combat, culture, investigation, economy
- **Content:** `portlight.content` -- ports, routes, goods, companions, contracts, factions, ships
- **Views:** `portlight.app.sf_views` -- campaign-aware Rich rendering surfaces
- **Playtest:** `portlight.engine.playtest` -- deterministic simulation harness
- **Dogfood:** `portlight.engine.dogfood_runner` -- automated scenario runner
- **Tests:** 2,200+ covering all systems
