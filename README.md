<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/star-freight/readme.png" alt="Star Freight — Trade. Decide. Survive." width="400">
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/star-freight/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/star-freight/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  <a href="https://mcp-tool-shop-org.github.io/star-freight/"><img src="https://img.shields.io/badge/landing_page-live-brightgreen" alt="Landing Page"></a>
</p>

# Star Freight

You were a military pilot. Then you were a disgrace. Now you are a captain with a bad ship, no standing, and a star system that was already moving before you got here.

**Star Freight** is a text-first tactics merchant RPG about hauling freight through a politically fractured star system. Five civilizations. One economy. Four truths that won't let you play the same life twice.

---

## The game

You dock at stations where the culture changes how you negotiate. You pick routes where the terrain changes how you fight. You hire crew who change what you can do, what you can access, and what you owe. You take contracts that look simple until the paperwork catches up, the shortage changes the price, or the cargo turns out to be evidence.

You are not the chosen one. You are a working captain trying to keep a ship moving while institutions seize cargo, shortages reshape routes, crews bring obligations aboard, and dangerous truths surface through ordinary work.

Every run becomes a different captain life. Not because you picked a class, but because your crew, your routes, your risks, and your standing shaped you into someone.

## Why it feels different

Most RPGs stack systems side by side. Star Freight makes them transact.

**Crew is binding law.** Thal isn't a +10% repair bonus. Thal is *why* you can dock at Keth stations, *why* your ship has an emergency repair ability, and *why* you noticed the medical cargo didn't match the season. Lose Thal, and three systems lose capability at once.

**Combat is a campaign event.** You don't load into a fight and load back out. Victory writes salvage credits and faction heat. Retreat costs jettisoned cargo and a reputation as someone who runs. Defeat means seized cargo, injured crew, and a ship that limps to the nearest station at a premium. Every outcome changes your next trade decision.

**Culture is social logic.** The Keth don't just have different prices. They have a seasonal biological calendar that changes what gift-giving means, when pushing a deal is an insult, and when outsiders are confined to the outer ring. The Veshan don't just fight. They challenge — and refusing is worse than losing. Knowledge isn't a codex. It's reading the room.

**Investigation emerges from life.** You notice the medical cargo doesn't match the season because you've been hauling it. You find the manifest discrepancy because you salvaged a wreck. Your Keth crew member interprets the pattern because she remembers her debt to the same supplier. The conspiracy doesn't announce itself. You stumble into it by doing the job.

## The world

Five civilizations share a star system called the Threshold.

**The Terran Compact** — Bureaucratic human government. They disgraced you. Getting back in means permits, patience, and swallowing pride. Safe markets, tight margins, heavy paperwork.

**The Keth Communion** — Arthropod collective on a biological calendar. Patient, observant, and devastating when offended. The best margins in the system if you understand the seasons. The fastest reputation collapse if you don't.

**The Veshan Principalities** — Reptilian feudal houses obsessed with honor and debt. They fight formally, trade directly, and remember everything. The Debt Ledger is not flavor. It's leverage.

**The Orryn Drift** — Mobile broker civilization. Neutral by policy, profitable by design. They trade with everyone, know everything, and charge for both. Cutting them out saves money. Losing their goodwill costs more.

**The Sable Reach** — Pirate factions, Ancestor tech salvagers, and people the Compact would rather forget. No law. No customs. No refunds. The highest risk and the highest reward in the system.

## Nine captain classes

Each captain class reshapes pricing, voyage modifiers, reputation growth, and starting relationships with the 20-port world.

**Merchant** -- volume trade, port fee discounts, steady and reliable.
**Smuggler** -- inspection evasion, underworld connections, lean margins.
**Navigator** -- speed bonuses, fuel efficiency, storm resilience.
**Privateer** -- faction-aligned combat, salvage income, political leverage.
**Corsair** -- high-risk piracy, black market access, reputation volatility.
**Scholar** -- cultural knowledge, luxury trade bonuses, diplomatic options.
**Merchant Prince** -- luxury specialist, high starting capital, expensive tastes.
**Dockhand** -- hard start, no advantages, everything earned from nothing.
**Bounty Hunter** -- combat-funded, target contracts, faction heat.
**Custom** -- distribute 10 skill points across Trade, Sailing, Shadow, and Reputation. Choose a home port, cultural background, and faction alignment. No best build -- only trade-offs.

## Quickstart

```bash
# Clone and install
git clone https://github.com/mcp-tool-shop-org/star-freight.git
cd star-freight
pip install -e ".[tui]"

# Start a new game (pick any of 9 types or custom)
starfreight new "Captain Nyx" --type merchant
starfreight tui
```

**Controls:** `D` Dashboard | `C` Crew | `R` Routes | `M` Market | `T` Station | `J` Journal | `F` Faction | `B` Buy | `S` Sell | `G` Travel | `A` Advance

Use `--save slotname` to run multiple captain lives in parallel.

## Current state

Star Freight is a proved product, not a design concept.

| | Count |
|---|---|
| Ports | 20 (5 regions) |
| Trade routes | 43 (tiered by ship class) |
| Trade goods | 18 (6 categories incl. contraband) |
| Captain classes | 9 + custom builder |
| Companions | 10 (5 roles, 2 each) |
| Ship classes | 5 (sloop to man-of-war) |
| Contract templates | 24 (7 families) |
| Pirate factions | 4 |
| Tests passing | 2,200+ |

The vertical slice has passed all three proof criteria: Golden Path (continuous captain life), Encounter (three branches with different campaign state), and Economy (pressure sustains without collapsing into grind).

Three expansion packs are shipped: Working Lives (human texture), Houses, Audits, and Seizures (institutional pressure), and Shortages, Sanctions, and Convoys (managed scarcity).

Captain path divergence is proved: three postures produce different routes, different trade mixes, different combat profiles, different failure textures, and different captain identities.

## Shipcheck scorecard

| Gate | Status | Evidence |
|------|--------|----------|
| A. Security | PASS | SECURITY.md, offline-only, no secrets/telemetry |
| B. Errors | PASS | 2200+ tests, structured campaign validation |
| C. Docs | PASS | README (8 languages), CHANGELOG, LICENSE, HANDBOOK |
| D. Hygiene | PASS | CI (Python 3.11+3.12), v1.0.0, paths-gated workflow |
| E. Polish | PASS | Logo, translations, maritime term guard CI |

## Tech

Python 3.11+. Typer CLI + Rich TUI + Textual full-screen mode. Crew binding, grid combat (8x6), cultural knowledge, investigation, and campaign orchestration. 2,200+ tests.

No external AI dependencies. No cloud services. Runs on your machine.

**Threat model:** Star Freight is a single-player offline game. It touches only local save files. It does NOT access the network, collect telemetry, store credentials, or require user accounts. Dependencies are Typer, Rich, and Textual -- all well-maintained, no native code. See [SECURITY.md](SECURITY.md) for the full policy.

## The standing rule

When unsure what to build next:

- Does it reinforce one of the four truths?
- Does it sharpen a captain life?
- Does it create a decision the player can feel?

If not, it can wait.

---

*Star Freight is a game about moving through systems of power without ever fully belonging to them.*

Built by <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
