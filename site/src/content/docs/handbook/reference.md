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
| Hull / Shield | Ship condition. Combat writes damage. Repair costs credits. |
| Reputation | Per-faction standing. Gates access and prices. |
| Cargo | What you carry shapes routing, risk, and investigation triggers. |
| Crew | Abilities, cultural access, morale, injury state, loyalty. |
| Investigation | Fragment-based evidence threads, corroborated by crew and events. |

## Crew system

Crew members provide three things simultaneously:

1. **Ship abilities** — combat actions, emergency repair, navigation bonuses
2. **Cultural access** — language, customs knowledge, faction trust
3. **Narrative obligations** — personal debts, loyalties, departure conditions

Crew has morale. Morale drops from missed pay, injuries, and bad outcomes. Below threshold, crew members leave — and take their capabilities with them.

### Crew pay
Every 30 days, crew pay is due. If credits are insufficient, morale drops sharply. Two missed pay periods and departures begin.

### Injuries
Combat can injure crew. Injured crew cannot use abilities for 5 days. Multiple injuries compound — a crew member who keeps getting hurt becomes a liability.

## Combat system

Grid-based tactical combat. Player ship vs enemy ship on a hex-adjacent grid.

**Actions per turn:** move, attack, defend, use ability, retreat.

**Outcomes write to campaign:**
- **Victory** — salvage credits, faction heat, possible crew injury
- **Retreat** — jettisoned cargo, reputation as someone who runs
- **Defeat** — seized cargo, injured crew, expensive limping

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

**Source discount** — goods cost less at stations that produce them.
**Demand premium** — goods sell for more at stations that need them.
**Cultural gates** — some goods require cultural knowledge to buy.
**Specialist premiums** — intelligence, brokered goods, and luxury items command higher prices at demand stations.

The core loop: buy at source, sell at demand, but routing is constrained by fuel, faction standing, lane danger, and what you're willing to carry through whose territory.

## Tech

Python 3.11+. Rich TUI. No external AI dependencies. No cloud services. Runs on your machine.

- **Engine:** `portlight.engine` — campaign state, crew, combat, culture, investigation
- **Content:** `portlight.content.star_freight` — stations, lanes, goods, encounters, crew
- **TUI:** `portlight.tui.sf_views` — 10 view functions rendering from campaign state
- **Playtest:** `portlight.engine.playtest` — deterministic simulation harness
- **Tests:** 2,200+ covering all systems
