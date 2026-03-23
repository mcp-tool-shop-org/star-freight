# TUI Surface Spec — Star Freight

> The TUI has one job: make the four system truths legible in motion.
> Every screen must answer: Where am I? What matters? What can I do? What will it cost?

---

## Current State

The TUI is 100% Portlight maritime. Zero Star Freight surfaces exist. The backend (crew, grid combat, cultural knowledge, investigation) is wired in `sf_campaign.py` but has no view layer. This spec defines what must be built.

## Terminal Target

- **Primary:** 120x40
- **Minimum:** 100x30
- If a screen breaks at 100x30, it is not shippable.

---

## Screen Architecture

### Persistent Bar (Captain's View)

Visible on every major screen. Ship instrumentation, not a debug header.

```
╔══════════════════════════════════════════════════════════════════════════╗
║ 327₡  │ Hull ████░░ 1200/2000  │ Fuel 5d  │ Crew 2/6 fit  │ Day 47  ║
║ ▲keth  ▼compact  │ Dax injured  │ ⚠ Pay due in 3d  │ Meridian Exchange ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Must show:**
- Credits (flashes on change)
- Hull / shield condition (bar)
- Fuel (days remaining)
- Crew fitness summary (X/Y fit)
- Day counter
- Current station or transit status
- Top 2 reputation standings (arrows: ▲ gaining, ▼ losing)
- Urgent crew status (injured/departing)
- Time pressure (next pay, contract deadline)

**Must NOT show:**
- Raw numbers for everything (pick the 2 most important)
- Investigation progress (that's for the journal)
- Full reputation breakdown (that's for the overlay)

### Navigation Model

**Tab keys** (consistent across all screens):

| Key | Screen | Purpose |
|-----|--------|---------|
| D | Dashboard | Captain summary, pressure overview |
| M | Market | Buy/sell at current station |
| R | Routes | Lane selection, travel |
| W | Crew | Crew roster, abilities, morale, cultural contribution |
| J | Journal | Investigation fragments, threads, leads |
| C | Contracts | Available and active contracts |
| P | Station | Current station details, services, cultural rules |
| F | Faction | Reputation breakdown by civilization/house |
| S | Ship | Ship condition, upgrades, ability slots |
| ? | Help | Keybinds and quick reference |

**Action keys** (context-sensitive):

| Key | Context | Action |
|-----|---------|--------|
| B | Market | Buy goods |
| L | Market | Sell goods |
| G | Routes | Travel to selected destination |
| T | Combat | Attack target |
| A | Combat | Use ability |
| V | Combat | Defend / evade |
| X | Combat | Retreat |
| Enter | Dialog | Confirm selection |
| Esc | Any | Back / cancel / close overlay |

**Rules:**
- No key means two different things on the same screen
- "Leave," "back," "return," "exit," "close" all map to Esc
- Every screen has a visible keybind reminder at the bottom

---

## Screen Specifications

### 1. Dashboard

**Purpose:** Pressure overview. What matters right now.

**Layout:**
```
┌─ Captain's View (persistent bar) ──────────────────────────┐
│                                                              │
│  ┌─ Pressure ──────────┐  ┌─ Crew Summary ────────────────┐ │
│  │ Credits: 327₡       │  │ Thal  [ENG] Keth  ██░ 45 morale│
│  │ Monthly cost: 125₡  │  │ Varek [GUN] Veshan ███ 55      │
│  │ Runway: ~2.6 months │  │                                 │
│  │ Next pay: 3 days    │  │ Ship abilities: 2/3 active      │
│  │ Fuel: 5 days        │  │ Cultural access: Keth 1, Veshan 1│
│  └─────────────────────┘  └─────────────────────────────────┘│
│                                                              │
│  ┌─ Active Contracts ──────────────────────────────────────┐ │
│  │ Standard Delivery    → Communion Relay   4d remaining   │ │
│  │ Cold Lantern Freight → Mourning Quay    2d remaining ⚠ │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─ Investigation ─────────────────────────────────────────┐ │
│  │ The Medical Shipment — ACTIVE (2 fragments)             │ │
│  │ Last lead: 15 days ago ⚠ trail cooling                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**Proves:** All four truths visible in one glance.

### 2. Crew Screen

**Purpose:** The thesis surface. Each crew line shows all four contributions.

**Layout:**
```
┌─ Crew ──────────────────────────────────────────────────────┐
│                                                              │
│  THAL  [ENGINEER]  Keth Communion                           │
│  ├─ Status: ACTIVE  HP: 80/80  Morale: ██░░ 45  Stranger   │
│  ├─ Ship:    Emergency Repair (active)                      │
│  ├─ Combat:  Organic Patch, Hull Bond  [+1 locked]          │
│  ├─ Culture: Keth access level 1 — seasonal protocols       │
│  ├─ Plot:    "keth_medical_debt" — active lead              │
│  └─ Pay: 55₡/month  │  Opinions: +patience, -violence      │
│                                                              │
│  VAREK  [GUNNER]  Veshan / House Drashan                    │
│  ├─ Status: INJURED (3d)  HP: 60/120  Morale: ███░ 55      │
│  ├─ Ship:    Heavy Volley (DEGRADED — injured)              │
│  ├─ Combat:  UNAVAILABLE — injured                          │
│  ├─ Culture: Veshan access level 1 — debt ledger, honor     │
│  ├─ Plot:    "house_drashan_exile" — active lead            │
│  └─ Pay: 70₡/month  │  Opinions: +honor, -deception        │
│                                                              │
│  [2/6 crew slots filled]  Monthly crew cost: 125₡           │
└──────────────────────────────────────────────────────────────┘
```

**Rules:**
- Injury/absence must be immediately visible (red status, strikethrough abilities)
- Ship ability shows active/degraded/gone
- Cultural contribution shows civ + level + what it unlocks
- Third ability locked status visible (loyalty gate)
- Morale bar with departure risk if <25

### 3. Market Screen

**Purpose:** Trade decisions with cultural and risk context visible.

**Must show at point of purchase:**
- Price (base, cultural modifier, supply/demand)
- Cultural requirement if gated ("Requires Keth knowledge 1 — Thal provides")
- Contraband status at current station
- Who this crew member enables access to
- Cargo space remaining

### 4. Routes Screen

**Purpose:** Lane selection with pressure visible.

**Must show per lane:**
- Destination name + civilization
- Travel days + fuel cost
- Danger rating (encounter chance)
- Terrain type (affects combat)
- Contraband risk (inspection chance)
- Controlled by whom
- Cultural knowledge note if relevant

### 5. Combat Screen (Grid)

**Purpose:** Tactical decisions with crew abilities visible.

**Layout:**
```
┌─ COMBAT: Reach Pirate Ambush ─────────────────────────────┐
│                                                             │
│  ┌─ Grid (8x6) ──────────────────┐  ┌─ Status ──────────┐ │
│  │ . . . . . . . .               │  │ Nyx    1200/2000hp │ │
│  │ . . . . . . . .               │  │ Shield  150/250    │ │
│  │ . N . . . . E .               │  │ Actions: 2/2       │ │
│  │ . . . # . . . .               │  │                    │ │
│  │ . . . . . . . .               │  │ Enemy   800/1500hp │ │
│  │ . . . . . . . .               │  │ Range: 3 tiles     │ │
│  └────────────────────────────────┘  └────────────────────┘ │
│                                                             │
│  ┌─ Actions ──────────────────────────────────────────────┐ │
│  │ [T] Attack (150 dmg, range 3)                          │ │
│  │ [A] Emergency Repair — Thal (heals 300hp, cd: 2)       │ │
│  │ [V] Defend (+15% evasion this turn)                    │ │
│  │ [X] Retreat (1/2 turns — cargo at risk)                │ │
│  │ [M] Move (2 tiles)                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  # = asteroid  ~ = debris (cover)  ≈ = nebula (hide)       │
└─────────────────────────────────────────────────────────────┘
```

**Rules:**
- Abilities show crew source name
- Unavailable abilities show why (injured, cooldown, no crew)
- Retreat shows progress and cargo risk
- Cover/terrain effects visible on grid
- Turn number and whose turn clearly shown

### 6. Journal Screen

**Purpose:** Investigation fragments. Not a task list.

**Layout:**
```
┌─ Journal ───────────────────────────────────────────────────┐
│                                                              │
│  THE MEDICAL SHIPMENT — ACTIVE                              │
│  "Medical cargo routed through Keth space in patterns       │
│   that don't match seasonal demand."                        │
│                                                              │
│  Fragments:                                                  │
│  ● [CLUE] Price anomaly at Keth relay — Day 15             │
│    "Demand is high but it's not the right season..."        │
│    Source: Price data at Keth relay station                  │
│                                                              │
│  ○ [RUMOR] Dock workers at Keth relay — Day 22              │
│    "Crates go into a warehouse that never opens..."         │
│    Source: Overheard at Keth relay station docks             │
│                                                              │
│  ⚠ Trail cooling — 15 days since last progress              │
│                                                              │
│  GHOST TONNAGE — DORMANT                                     │
│  (No fragments yet)                                          │
└──────────────────────────────────────────────────────────────┘
```

**Rules:**
- Grade icons: ○ rumor, ● clue, ◆ corroborated, ★ actionable, ✦ locked
- Source attribution on every fragment
- Crew interpreter credited when applicable
- Delay warning visible
- No objectives, no quest markers, no checklists

### 7. Station Screen

**Purpose:** Station identity + services + cultural rules.

**Must show:**
- Station name, civilization, description (brief)
- Cultural greeting (what happens when you dock)
- Services available
- Cultural restriction (what you can't do without knowledge)
- Cultural opportunity (what knowledge opens)
- Which crew members matter here
- Investigation leads available here (if any threads are active)

### 8. Faction Screen

**Purpose:** Reputation breakdown with practical meaning.

**Must show per faction:**
- Standing number + breakpoint label (Hostile/Cold/Neutral/Respected/Trusted/Allied)
- What this standing means practically (price modifier, access tier, patrol behavior)
- Trend arrow (gaining/losing)
- Per-house breakdown for Veshan

### 9. After-Action Summary

**Purpose:** Make campaign writeback emotionally real.

Shown after every combat, major trade, contract completion, or investigation discovery.

```
┌─ AFTERMATH ─────────────────────────────────────────────────┐
│                                                              │
│  VICTORY — Reach Pirate Ambush                              │
│                                                              │
│  Credits:     +200₡ (salvage)                               │
│  Hull damage: -400 (1200/2000 remaining)                    │
│  Cargo lost:  none                                          │
│  Reputation:  reach.ironjaw -5 │ compact +2                 │
│  Crew:        Varek INJURED (5 days recovery)                │
│               → Heavy Volley DEGRADED until recovery         │
│               → Ground combat: Varek UNAVAILABLE             │
│  Investigation: salvage revealed manifest fragment           │
│                                                              │
│  Press any key to continue...                                │
└──────────────────────────────────────────────────────────────┘
```

**Rules:**
- Every state delta listed explicitly
- Crew consequences spelled out (what ability is lost/degraded)
- Investigation fragments surfaced with source
- No hidden changes — everything the player should know is here

---

## Semantic Standards

### Color Palette (Space Theme)

| Color | Use | Hex |
|-------|-----|-----|
| Deep void | Background | #0a0e1a |
| Star white | Primary text | #e8e8e8 |
| Credit gold | Credits, positive economic | #f0c040 |
| Alert red | Danger, damage, low morale, contraband | #e05050 |
| Shield blue | Shields, defensive actions, Compact | #4090e0 |
| Growth green | Healing, positive standing, safe | #40c060 |
| Keth amber | Keth civilization, seasonal | #d0a040 |
| Veshan crimson | Veshan civilization, honor | #c04040 |
| Orryn teal | Orryn civilization, data | #40b0b0 |
| Reach purple | Sable Reach, contraband | #9060c0 |
| Muted gray | Disabled, unavailable, locked | #606060 |

### Typography Rules

- **Bold:** Station names, crew names, thread titles, section headers
- **Dim/gray:** Locked abilities, unavailable options, dormant threads
- **Colored bars:** Health/morale/fuel use filled blocks (█░)
- **Icons:** ▲ gaining, ▼ losing, ⚠ warning, ● clue, ★ actionable
- **No emoji** unless explicitly approved

### Information Hierarchy Rule

Every screen answers these in order:
1. **Where am I?** (header)
2. **What matters right now?** (pressure indicators)
3. **What can I do?** (available actions)
4. **What will it cost/risk?** (consequence preview)

If any screen violates this order, it fails the audit.

---

## What Must Be Built

The TUI currently has zero Star Freight surfaces. These must be created:

### New screens (not in Portlight):
1. **Crew Screen** — thesis surface, all four truths per crew member
2. **Journal Screen** — investigation fragments, not task lists
3. **Grid Combat Screen** — tactical grid with crew abilities
4. **Faction Screen** — reputation with practical meaning
5. **After-Action Summary** — campaign writeback made visible

### Existing screens to adapt:
1. **Dashboard** — add crew panel, investigation status, time pressure
2. **Market** — add cultural access gates, crew-enabled notes
3. **Routes** — add terrain, cultural notes, contraband risk
4. **Station** — add cultural rules, investigation leads
5. **Contracts** — add system truth tags (which truths this contract touches)

### Existing screens reusable as-is:
1. **Cargo** — generic enough
2. **Ledger** — trade history is system-neutral
3. **Help** — needs new keybinds but structure is fine

### Must be removed/replaced:
1. **Encounter Screen** — replaced by Grid Combat
2. **Inventory** — replaced by Crew + Ship screens
3. **Fleet** — not in scope for slice
4. **Infrastructure** — not in scope for slice
5. **Maritime theme** — colors, ASCII art, terminology
