---
title: Beginner's Guide
description: Your first 30 minutes as a Star Freight captain — from install to first profit.
sidebar:
  order: 99
---

This guide walks you through your first session as a Star Freight captain. By the end you will have installed the game, created a captain, made your first trade, survived your first route, and understood how crew, combat, and culture shape your captain life.

## 1. Installation

Star Freight requires Python 3.11 or later and a terminal with Unicode support.

```bash
git clone https://github.com/mcp-tool-shop-org/star-freight.git
cd star-freight
pip install -e ".[tui]"
```

Verify the install:

```bash
starfreight version
```

## 2. Creating your first captain

Start a new game with the `new` command. For your first run, Merchant is the most forgiving class:

```bash
starfreight new "Your Name" --type merchant
```

Nine captain classes are available: merchant, smuggler, navigator, privateer, corsair, scholar, merchant_prince, dockhand, and bounty_hunter. There is also a custom builder that lets you distribute 10 skill points. Merchant gives you port fee discounts and steady trade margins -- a good foundation while you learn the systems.

Launch the full-screen TUI:

```bash
starfreight tui
```

You can run multiple captain lives in parallel using save slots:

```bash
starfreight new "Alt Captain" --type corsair --save slot2
starfreight tui --save slot2
```

## 3. Reading the dashboard

Press `D` to see the Dashboard. This is your pressure overview -- it shows credits, hull condition, cargo, crew status, and days until crew pay is due.

Key things to check every time you dock:

- **Credits** -- can you afford crew pay on the next pay day (every 30 days)?
- **Hull** -- combat damage accumulates. Repair at port before it becomes critical.
- **Cargo hold** -- empty space is wasted opportunity. Full holds need a destination.
- **Crew morale** -- dropping morale leads to departures. Pay on time and avoid bad outcomes.

The other screens:

| Key | Screen | What it tells you |
|-----|--------|-------------------|
| `C` | Crew | Abilities, culture, morale, injury status, loyalty tier |
| `R` | Routes | Available routes, distance, danger, ship class requirement |
| `M` | Market | Goods, prices, what this port produces vs demands |
| `T` | Station | Where you are, what services are available |
| `J` | Journal | Investigation fragments you have discovered |
| `F` | Faction | Standing with civilizations and pirate factions |

## 4. Your first trade

Trading is the core loop. The principle is simple: buy where goods are cheap (source ports), sell where they are expensive (demand ports).

**Step 1: Check the market.** Press `M` at your starting port (Porto Novo). Look for goods with high stock and low prices -- those are exports. Porto Novo exports Grain (cheap to buy here).

**Step 2: Check routes.** Press `R` to see where you can go. Al-Manar is a short sloop-safe route from Porto Novo, and it demands Grain (pays premium).

**Step 3: Buy.** Press `B` to buy Grain. Buy as much as your hold allows.

**Step 4: Travel.** Press `G` and select Al-Manar. The route takes several days. You may encounter events along the way.

**Step 5: Sell.** When you arrive, press `S` to sell your Grain at the demand premium.

**Step 6: Repeat in reverse.** Al-Manar exports Spice. Buy Spice and haul it back to where it sells well.

Tips:
- Sell before buying. A captain who arrives with cargo and leaves with cargo is wasting hold space.
- Watch the flood penalty. Dumping the same good at the same port repeatedly degrades your sell price.
- Contraband (opium, black powder, stolen cargo) is only tradeable at black market ports. The margins are extreme but so is the inspection risk.

## 5. Understanding crew

Crew members are not stat bonuses. They are dependencies. A crew member is WHY you can do something -- dock at certain stations, use a combat ability, interpret cultural patterns.

Your crew roster holds up to six members. Each provides:

1. **Ship abilities** -- combat actions, emergency repair, navigation
2. **Cultural access** -- language, customs knowledge, faction trust
3. **Narrative obligations** -- personal debts, loyalties, departure conditions

Crew morale starts low (45 out of 100). It rises through good outcomes, on-time pay, and loyalty building. It drops from missed pay, injuries, and bad decisions. Below the departure threshold, crew members leave permanently -- and take their capabilities with them.

Loyalty progresses one-way through three tiers:
- **Stranger** (0-30 points) -- limited trust, two abilities available
- **Trusted** (31-65 points) -- third ability unlocked, personal quest available
- **Bonded** (66-100 points) -- loyalty mission available, deepest narrative access

Pay day comes every 30 days. If you cannot pay, morale drops sharply. Two missed pay periods and people start leaving.

## 6. Surviving combat

Combat happens on an 8x6 grid with terrain (asteroids block movement, debris provides cover, nebula hides you). It is not a mode switch -- every outcome writes permanently to your campaign state.

**Actions per turn:** move, attack, defend, use ability, retreat.

Winning a fight earns salvage credits and faction heat. Retreating costs jettisoned cargo and reputation. Losing means seized cargo, injured crew, and an expensive limp to the nearest port.

Combat advice for beginners:
- Avoid fights you do not need. Route choice is your first defense.
- Use terrain. Debris gives +25% evasion. Nebula hides you from ranged attacks beyond range 1.
- Watch escalation. Consecutive fights in a short window trigger diminishing salvage, increased injury chance, and persistent hull wear.
- Crew abilities matter. Losing a crew member mid-fight means losing their ability. Protect your specialists.

## 7. Culture and investigation

Each civilization has social rules that affect what you can buy, how much you pay, and whether you are welcome.

**Keth seasons** -- a biological calendar changes what gifts mean, when trading is appropriate, and when outsiders are restricted. Having a Keth crew member helps you read the room.

**Veshan challenge** -- refusing a formal challenge is worse than losing. The Debt Ledger tracks favors and obligations that become leverage.

**Orryn neutrality** -- they broker for everyone and charge for information. Cutting them out saves money until you need them.

Cultural knowledge increases through crew interactions and successful navigation of cultural situations. Higher knowledge unlocks restricted goods, better prices, and diplomatic options.

Investigation threads surface through ordinary play -- not through quest markers. You notice a cargo discrepancy because you have been hauling medical supplies. You find a manifest fragment in combat salvage. Your crew member interprets the pattern because she remembers the same supplier. The journal (press `J`) tracks fragments across five evidence grades: rumor, clue, corroborated, actionable, and locked.

You do not need to chase the investigation. But ignoring it has consequences.

---

Once you have completed a few trade runs, paid your crew on time, and survived an encounter or two, you are no longer a beginner. You are a working captain. The rest of the handbook covers the systems in depth: [The World](/star-freight/handbook/the-world/), [Captain Paths](/star-freight/handbook/captain-paths/), and [Systems Reference](/star-freight/handbook/reference/).
