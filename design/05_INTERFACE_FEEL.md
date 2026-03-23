# Interface, Readability & Feel — Star Freight

> A complex game dies if the player cannot parse state fast enough. This doc must make the game feel like one coherent captain fantasy, not three tabs.

## Four Laws (carried from Campaign State)

Every interface decision is tested against these:

1. **Crew is the binding system** — crew members must read as multi-system campaign assets, not party inventory.
2. **Pressure must create decisions, not chores** — recurring costs and obligations must surface as choices, not notifications.
3. **Recovery must preserve consequence** — failure states must be visible and felt, not hidden behind clean UI resets.
4. **Every UI surface exposes shared campaign state** — no isolated subsystem screens. The player should always see how trade, tactics, and plot are connected through the same variables.

---

## Input Grammar

**Keyboard-driven.** This is a TUI or Tauri desktop game, not a browser app. The input model matches Portlight.

- **Arrow keys / WASD:** Navigate menus, move units on grid, scroll maps.
- **Enter / Space:** Confirm, select, interact.
- **Escape:** Back, cancel, close overlay.
- **Number keys (1–4):** Quick-select abilities in combat, quick-select crew in menus.
- **Tab:** Cycle between major UI panels (station view: market ↔ contracts ↔ crew ↔ ship).
- **Letter hotkeys:** Context-specific. `T` for trade, `C` for crew, `M` for map, `J` for journal, `R` for reputation. Consistent across all screens.
- **? key:** Context help. Always available. Shows what the current screen's options mean.

**No mouse required.** Mouse support optional for Tauri build but the game must be fully playable by keyboard. Every action reachable in 1–3 keystrokes.

---

## Action Windows

What the player can accomplish in a given time span. This defines the pace.

- **1 second:** Read the most important number on screen. Glance at credits, ship condition, or the current encounter prompt. The captain glances at the dashboard.
- **5 seconds:** Make a binary decision. Accept or decline a contract. Fight or flee an encounter. Buy or pass on a trade good. The captain reacts.
- **30 seconds:** Evaluate a trade opportunity. Compare buy price vs expected sell price, weigh the route danger, check if you have the cultural standing. Plan a combat turn (move unit, choose ability, confirm). The captain thinks.
- **2 minutes:** Plan a full session. Read the job board, check the market, assess ship condition, talk to a contact, decide on a route. The captain strategizes.
- **5–8 minutes:** Complete a combat encounter. Enter grid, fight 5–8 turns, resolve aftermath. The captain survives.

---

## Screen Flow

The game has one primary loop reflected in the screen flow. There are no separate "modes" with their own navigation — the player moves through the world and the screen adapts.

```
┌──────────────────────────────────────────────────────┐
│                    CAPTAIN'S VIEW                     │
│          (persistent bar: always visible)             │
├──────────────────────────────────────────────────────┤
│                                                      │
│   STATION ←──→ LANE ←──→ ENCOUNTER ←──→ COMBAT     │
│     │                        │                       │
│     ├─ Market                ├─ Social               │
│     ├─ Contracts             ├─ Environmental        │
│     ├─ Crew                  └─ Hostile → Grid       │
│     ├─ Ship                                          │
│     ├─ Contacts/NPCs                                 │
│     └─ Map                                           │
│                                                      │
│   OVERLAYS (accessible from anywhere):               │
│     Journal (investigation + consequence log)        │
│     Reputation (all factions at a glance)            │
│     Crew Detail (any crew member, full profile)      │
│     Debt Ledger (Veshan obligations)                 │
│     Map (star system, routes, station info)          │
└──────────────────────────────────────────────────────┘
```

**Key principle:** The player never "enters a mode." They dock at a station and the station UI appears. They launch and the lane narration begins. An encounter fires and the encounter UI replaces the lane view. If combat triggers, the grid appears. When combat ends, they're back in the encounter. When the encounter ends, they're back on the lane. When they arrive, they're at a station. One continuous flow.

**Overlays** are available from any screen via hotkey. They don't interrupt the current state — they layer on top and dismiss with Escape. This means the player can check reputation while planning a trade, or review the crew while deciding whether to accept a contract.

---

## The Captain's View (Persistent Bar)

The most important design surface in the game. This bar is always visible on every screen. It is the player's dashboard — the shared campaign state at a glance.

```
┌─────────────────────────────────────────────────────────────┐
│ ₡ 2,340  │  ⊙ Ship 67%  │  ☰ 3/6 crew fit  │  Day 147    │
│ Keth: ▓▓▓░░ +33  Compact: ▒░░░░ -15  Reach: ▓▓░░░ +20     │
└─────────────────────────────────────────────────────────────┘
```

**Line 1: The vitals.**
- **Credits** — the number the player checks most. Always visible. Changes flash briefly on gain/loss.
- **Ship condition** — percentage. Color-coded: green (75%+), yellow (50–74%), red (below 50%). The player should feel anxiety when this is yellow without having to open a submenu.
- **Crew fitness** — X of Y crew healthy. "3/6 crew fit" means 3 are injured. The player sees combat readiness at a glance. This is the tactical pressure.
- **Day counter** — the clock. Relevant for Keth seasons, crew pay, contract deadlines. Not alarming most of the time, but the player learns to track it.

**Line 2: The reputation snapshot.**
- Top 3 most relevant faction standings shown as small bar + number. Which 3 are shown depends on context: at a Keth station, Keth standing is shown first. On a lane near Veshan space, Veshan standings appear. The player always sees what matters NOW.
- This is the political pressure. If a reputation bar is red (negative), the player feels it before they see a consequence.

**What's NOT on the persistent bar:** Cargo contents, cultural knowledge levels, Veshan debts, investigation progress, crew details. These are one overlay away, not zero. The bar shows campaign pressure, not campaign inventory.

---

## Station Screen: The Planning Phase

The station screen is where most decisions happen. It must feel like a captain reviewing their situation, not a player navigating menus.

**Layout:**

```
┌────────────────────────────────────────────────────────┐
│ CAPTAIN'S VIEW (persistent bar)                        │
├────────────────┬───────────────────────────────────────┤
│                │                                       │
│  STATION       │   ACTIVE PANEL                        │
│  NAV           │   (Market / Contracts / Crew /        │
│                │    Ship / Contacts)                    │
│  [M] Market    │                                       │
│  [J] Jobs      │   Shows detail for selected tab.      │
│  [C] Crew      │   Context-sensitive.                  │
│  [S] Ship      │                                       │
│  [N] NPCs      │                                       │
│  [L] Launch    │                                       │
│                │                                       │
├────────────────┴───────────────────────────────────────┤
│ STATION FLAVOR: "Communion Hub. Harvest season.         │
│ The docks smell like growth medium and ozone.           │
│ A Keth elder watches you from the market entrance."     │
└────────────────────────────────────────────────────────┘
```

**Station flavor bar (bottom):** 1–2 sentences of atmosphere. Changes based on civilization, season, reputation, and consequence engine state. This is where the world breathes. The player reads it once per visit — it's ambient, not interactive, but it carries cultural and narrative information. "A Compact officer is watching the docking bay" tells the player something about their current standing without a stat screen.

**The Market panel** shows trade goods as a table: good name, buy price, your-hold quantity, estimated sell price at known destinations (based on cultural knowledge), and a small indicator for contraband status. The player should be able to evaluate a trade opportunity in 10–15 seconds.

**The Jobs panel** shows contracts as cards: objective, destination, pay, danger rating, reputation lean (small icon: clean/dirty/neutral), and deadline. The player reads the board like a captain reads a posting wall. Maximum 5–6 visible contracts at a time — the board is curated, not a spreadsheet.

**The Crew panel** — see below. This is the most important submenu in the game.

---

## Crew Screen: The Binding System Made Visible

The crew screen must communicate that each crew member is a multi-system campaign asset. Not a stat block. Not a party slot. A person who changes what the captain can do across trade, tactics, and plot.

**Crew list view:**

```
┌──────────────────────────────────────────────────────────┐
│ CREW                                                     │
│                                                          │
│ 1. Kethra (Keth)   Navigator   ♥♥♥♡♡  Trusted   [FIT]  │
│    → Keth access Lv.1 │ Ship: Evasive Burn │ Harvest tip │
│                                                          │
│ 2. Dax (Reach)     Mechanic    ♥♥♡♡♡  Stranger  [FIT]  │
│    → Reach access Lv.0 │ Ship: Repair │ Faction intel    │
│                                                          │
│ 3. Maren (Compact) Medic       ♥♥♥♡♡  Trusted   [INJ]  │
│    → Compact access Lv.1 │ Ship: — (injured) │ Permits  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Each crew member's list entry shows three layers in one line:**

1. **Identity:** Name, civilization, role, morale hearts, loyalty tier, fitness status.
2. **Campaign contribution (second line):** What they give you RIGHT NOW across all three layers:
   - Cultural access level (trade layer) — "Keth access Lv.1"
   - Ship ability granted (tactics layer) — "Ship: Evasive Burn"
   - Current narrative hook (plot layer) — "Harvest tip" or "Faction intel" or "Personal mission available"

**This is the core design move.** The player looks at a crew member and sees one person with three kinds of value, not a stat block with a flavor paragraph. When Maren is injured, her ship ability goes offline ("Ship: — (injured)") and the player feels the tactical cost instantly. When Kethra hits Trusted, a new narrative hook appears in her row and the player knows something opened up.

**Crew detail view (Enter on a crew member):**

```
┌──────────────────────────────────────────────────────────┐
│ KETHRA — Keth Communion — Navigator                      │
│                                                          │
│ Morale: ♥♥♥♡♡ (63/100)    Loyalty: Trusted              │
│ Status: Fit                Pay: 120₡/month               │
│                                                          │
│ GROUND COMBAT                                            │
│  Role: Tech   HP: 45/45   Speed: 6                       │
│  [1] Hack  [2] EMP Grenade  [3] Overload                │
│                                                          │
│ SHIP CONTRIBUTION                                        │
│  Grants: Evasive Burn (pilot skill)                      │
│  Effect: Ship dodge +15%, emergency maneuver ability     │
│                                                          │
│ CULTURAL VALUE                                           │
│  Keth knowledge: Level 1 (Aware)                         │
│  Unlocks: Basic Keth customs, seasonal calendar visible  │
│  Next level requires: 8+ Keth visits + cultural event    │
│                                                          │
│ NARRATIVE                                                │
│  Hook: "Mentioned her sister works at a station in the   │
│  next sector. Hasn't said more."                         │
│  Personal mission: Locked (requires Bonded loyalty)      │
│                                                          │
│ OPINIONS                                                 │
│  Values: Cultural respect, patience, collective good     │
│  Dislikes: Recklessness, Keth customs violated           │
│  Recent: +3 morale (respected Keth harvest ritual)       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Four sections, one per layer plus personality.** The player sees exactly what this crew member does for them in combat, on the ship, in trade/culture, and in the story — and what this crew member cares about (which predicts future morale shifts). This is a person, not a spreadsheet. But it's also a campaign asset with visible, concrete value.

---

## Lane Screen: Travel as Tension

Travel must feel tense without becoming menu sludge. The player is a captain watching the stars, not a player clicking "next day."

```
┌──────────────────────────────────────────────────────────┐
│ CAPTAIN'S VIEW (persistent bar)                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  EN ROUTE: Thorngate → Communion Hub                     │
│  Day 2 of 3  │  Lane: Keth Corridor  │  Danger: ●●○○○   │
│  Sector: Keth space  │  Season: Harvest                  │
│                                                          │
│  ─────────────────────────────────────────────────        │
│                                                          │
│  The corridor is quiet. A Keth grain convoy passes       │
│  on the far lane, formation tight — harvest shipments    │
│  running on schedule. Kethra watches them and says       │
│  nothing, but her antennae are tracking.                 │
│                                                          │
│  Your engineer reports the starboard shield emitter      │
│  is running hot. Not critical. Yet.                      │
│                                                          │
│  ─────────────────────────────────────────────────        │
│                                                          │
│  [CONTINUE]  [SCAN]  [SHIP STATUS]                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**The narration IS the travel.** Each day produces 1–3 paragraphs of lane narration — sector conditions, crew reactions, ship status notes, ambient encounters. The player reads, absorbs, and presses Continue (or responds to an event). This is Portlight's sea culture engine reskinned.

**When an event fires, the narration shifts tone:**

```
│  ─────────────────────────────────────────────────        │
│                                                          │
│  Scanner contact. Two ships, closing fast, no            │
│  transponder. Your gunner says the drive signatures      │
│  read Ironjaw.                                           │
│                                                          │
│  They're hailing. No — they're not. They're locking on.  │
│                                                          │
│  [FIGHT]  [FLEE]  [HAIL]                                 │
│                                                          │
```

**Key design rule:** Travel narration is never more than 3 paragraphs per day. The player should spend 30–60 seconds per travel day. A 3-day trip takes 2–4 minutes including one event. Travel is anticipation, not a slog.

**Campaign state visible during travel:** The persistent bar shows credits, ship condition (which is degrading slightly), crew fitness, and day count. The lane header shows route info and danger rating. The player feels the campaign state while traveling without checking submenus.

---

## Combat Screen: The Grid

Combat must be immediately readable. The player enters the grid, understands the situation in 5 seconds, and starts making decisions.

**Ground combat layout:**

```
┌──────────────────────────────────────────────────────────┐
│ CAPTAIN'S VIEW (persistent bar)                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  GROUND COMBAT — Ironjaw boarding party                  │
│  Turn 3  │  Your move: Kethra (Tech)                     │
│                                                          │
│   1  2  3  4  5  6  7  8                                 │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┐                               │
│ A│  │  │  │██│  │  │  │  │  ██ = full cover              │
│  ├──┼──┼──┼──┼──┼──┼──┼──┤  ▓▓ = half cover              │
│ B│  │K │  │██│  │e1│  │  │  K  = Kethra (selected)       │
│  ├──┼──┼──┼──┼──┼──┼──┼──┤  D  = Dax                     │
│ C│  │  │▓▓│  │  │  │e2│  │  PC = Player Captain          │
│  ├──┼──┼──┼──┼──┼──┼──┼──┤  e1 = enemy 1 (Ironjaw Heavy) │
│ D│  │D │  │  │▓▓│  │  │  │  e2 = enemy 2 (Ironjaw Hacker)│
│  ├──┼──┼──┼──┼──┼──┼──┼──┤                                │
│ E│PC│  │  │  │  │  │  │e3│  e3 = enemy 3 (Ironjaw Rusher)│
│  └──┴──┴──┴──┴──┴──┴──┴──┘                               │
│                                                          │
│  KETHRA  HP: 42/45  In half cover                        │
│  [1] Hack (disable e2's tech, range 4) — 85% hit        │
│  [2] EMP Grenade (AoE stun, range 3) — hits e1,e2       │
│  [3] Overload (boost Dax damage +50%, 2 turns)           │
│  [M] Move  [A] Basic Attack (range 3) — 70% hit on e1   │
│  [R] Retreat to exit                                     │
│                                                          │
│  ENEMY PATTERNS: e1 advances (rusher), e2 hacks (stay), │
│                  e3 flanking (circler)                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Space combat is the same grid, different labels:**

```
│  SPACE COMBAT — Ironjaw raiders (×2)                     │
│  Turn 2  │  Your move: Captain's Ship                    │
│                                                          │
│   1  2  3  4  5  6  7  8                                 │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┐                               │
│ A│  │  │  │**│**│  │  │  │  ** = asteroid (cover)        │
│  ├──┼──┼──┼──┼──┼──┼──┼──┤  CS = Captain's Ship          │
│ B│  │  │CS│  │**│  │  │  │  P1 = Pirate raider 1         │
│  ├──┼──┼──┼──┼──┼──┼──┼──┤  P2 = Pirate raider 2         │
│ C│  │  │  │  │  │  │P1│  │                                │
│  ├──┼──┼──┼──┼──┼──┼──┼──┤                                │
│ D│  │  │  │**│  │  │  │P2│                                │
│  └──┴──┴──┴──┴──┴──┴──┴──┘                               │
│                                                          │
│  YOUR SHIP  Hull: 2,340/2,800  Shields: 180/400          │
│  [1] Volley (range 4) — 75% on P1, 60% on P2            │
│  [2] Evasive Burn (dodge +30% this turn, no attack)      │
│  [3] Repair (restore 200 hull, no move)                  │
│  [M] Move (3 tiles)  [B] Board (adjacent only)           │
│  [R] Retreat (flee combat, jettison cargo if pursued)    │
│                                                          │
│  ENEMY: P1 closing (2 tiles away), P2 flanking wide     │
│                                                          │
```

**Key readability rules for combat:**

1. **Hit chances visible before committing.** The player sees "85% hit" on every option. No hidden rolls. No surprises.
2. **Enemy behavior patterns displayed.** "e1 advances, e2 hacks, e3 flanks." The player reads the enemy like a captain reads a battlefield. This is the puzzle — not the dice.
3. **One unit acts at a time.** No simultaneous resolution. The player focuses on one decision per turn step.
4. **Selected unit's options are always visible.** No submenu diving. Abilities are 1-keypress away.
5. **Campaign state persists** — the Captain's View bar stays on screen during combat. The player sees their credits, ship condition, and crew fitness while fighting. Combat isn't a separate mode — it's an event in the captain's ongoing life.

---

## Encounter Screen: Where Decisions Happen

Non-combat encounters (social, environmental, cultural) use a simple text + choices format. No special UI — just narration and options.

```
┌──────────────────────────────────────────────────────────┐
│ CAPTAIN'S VIEW (persistent bar)                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ENCOUNTER — Keth Harvest Greeting                       │
│                                                          │
│  The elder stands motionless at the market entrance.     │
│  The protocol is clear to anyone who knows it: approach  │
│  slowly, present the gift with both hands, speak only    │
│  when spoken to. Kethra briefed you on the lane.         │
│                                                          │
│  You're holding Earth tea, wrapped in plain cloth.       │
│                                                          │
│  [1] Present the tea correctly (Keth knowledge Lv.1+)   │
│  [2] Present the tea, skip the ritual (risky)            │
│  [3] Decline to approach (safe, miss opportunity)        │
│  [4] Ask Kethra to present on your behalf                │
│                                                          │
│  ⚠ Option 1 requires Keth knowledge Level 1.            │
│    You have: Level 1 (Aware) via crew: Kethra            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Cultural risk is surfaced BEFORE the mistake.** The player sees which options require cultural knowledge, what level they have, and where that knowledge comes from (crew). If they attempt something above their level, the game warns them — but lets them try. The consequence is theirs to own, not a surprise.

**Options show their source.** "Keth knowledge Lv.1+ ... You have: Level 1 (Aware) via crew: Kethra" tells the player exactly why this option is available and who made it possible. The crew member's value is visible at the moment of decision.

---

## Overlays: Campaign State On Demand

Overlays are accessible from any screen via hotkey. They don't interrupt gameplay — they layer on top and dismiss with Escape.

### Reputation Overlay (`R` key)

```
┌──────────────────────────────────────────────────────────┐
│ REPUTATION                                               │
│                                                          │
│ TERRAN COMPACT        -15  ▒░░░░░░░░░ Cold               │
│   Fleet Command: -20 │ Corporate: -10 │ Frontier: 0      │
│   Effect: Surcharges, limited contracts, no military dock │
│                                                          │
│ KETH COMMUNION        +33  ▓▓▓▓░░░░░░ Respected          │
│   Season: Harvest (42 days remaining)                    │
│   Effect: Price discount, mid-tier contracts, Lv.1 goods │
│                                                          │
│ VESHAN PRINCIPALITIES  +2  ▓░░░░░░░░░ Neutral            │
│   Drashan: +5 │ Vekhari: 0 │ Solketh: 0                 │
│   Debts owed: 0 │ Debts held: 1 minor (House Drashan)   │
│   Effect: Standard access                                │
│                                                          │
│ ORRYN DRIFT           +10  ▓░░░░░░░░░ Neutral            │
│   Grand: +12 │ Quiet: +8 │ Scholar: +5                   │
│   Effect: Standard access                                │
│                                                          │
│ SABLE REACH           +20  ▓▓░░░░░░░░ Neutral            │
│   Ironjaw: +15 │ Circuit: +25 │ Cult: +5                 │
│   Effect: Standard access, Freeport contacts available   │
│                                                          │
│ MERCHANT ←───────●──────────→ PIRATE                     │
│            (leaning independent)                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Key features:**
- Every faction on one screen. The player sees their entire political position in 5 seconds.
- Sub-faction standings visible (Veshan houses, Reach pirate factions, Compact branches).
- Current effects stated in plain language. Not "+12% price modifier" — instead "Price discount, mid-tier contracts, Lv.1 goods." The player reads consequences, not numbers.
- The merchant ↔ pirate spectrum bar at the bottom shows overall position derived from the portfolio. This is the player's identity at a glance.
- Keth seasonal timer is shown here because it's reputation-adjacent — it changes what Keth standing means right now.

### Journal Overlay (`J` key)

```
┌──────────────────────────────────────────────────────────┐
│ JOURNAL                                                  │
│                                                          │
│ ACTIVE CONTRACTS (2/3)                                   │
│  ▸ Alloy delivery to Communion Hub — 3 days remaining    │
│  ▸ Bounty: Ironjaw scout, last seen Sargasso Belt       │
│                                                          │
│ INVESTIGATION                                            │
│  ▸ Beat 3: "A Compact intel officer was seen at the      │
│    Scholar Drift asking about Ancestor navigation data.  │
│    Kethra recognized the name — it came up during your   │
│    court-martial."                                       │
│  ▸ [4 of 10 leads found]                                 │
│                                                          │
│ RECENT CONSEQUENCES                                      │
│  ▸ Day 142: Helped Veshan convoy vs pirates → Drashan    │
│    standing +8, contact offered at Vekhari port          │
│  ▸ Day 138: Sold bio-crystal at Thorngate → Keth         │
│    standing +2, Thorngate prices updated                 │
│  ▸ Day 135: Turned down smuggling job at Freeport →      │
│    Ironjaw standing -3, clean reputation maintained      │
│                                                          │
│ CREW NOTES                                               │
│  ▸ Kethra: "Mentioned her sister. First personal detail  │
│    she's shared."                                        │
│  ▸ Dax: "Seemed tense after the Ironjaw encounter.       │
│    Old business?"                                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**The journal is the captain's notebook, not a quest log.** It surfaces active contracts, investigation breadcrumbs, recent consequence events, and crew observations — all in one place. The player sees the three-layer loop in their own history: trade actions, combat outcomes, and story beats interleaved chronologically.

**Investigation leads are written as narrative fragments, not quest objectives.** "A Compact intel officer was seen at the Scholar Drift" reads like a lead in a story, not "Go to Scholar Drift." The player follows leads as a captain would — by deciding to travel there when it makes sense, not by following a waypoint.

---

## Feedback Hierarchy

How the game communicates state changes, ranked by importance.

| Priority | Event Type | Feedback Method |
|----------|-----------|-----------------|
| 1 (critical) | Combat damage, crew injury, ship system failure | Number flash on unit + color change on persistent bar. Immediate, visceral. |
| 2 (important) | Reputation threshold crossed, cultural misstep, contract failed | Full-screen text event with 1-paragraph consequence description. The player stops and reads. |
| 3 (significant) | Trade completed, contract completed, standing shift, crew morale change | Persistent bar updates + brief inline text ("Keth standing: +3"). Visible but doesn't interrupt. |
| 4 (ambient) | Lane narration, NPC greetings, station flavor, seasonal changes | Narration text in the appropriate screen section. Read if interested, skimmable if not. |
| 5 (background) | Consequence engine logging, NPC memory updates, supply/demand shifts | Invisible. The player never sees this directly — they feel it through future events. |

**Key rule: Pressure surfaces passively, not through notifications.** The game doesn't pop up "Crew pay due in 5 days!" Instead, the persistent bar shows "Day 147" and the player has internalized that pay is due on Day 150. The journal doesn't nag — it shows the contracts and their deadlines. The crew screen doesn't flash warnings — it shows morale hearts. Pressure is visible. It is never a push notification.

---

## Onboarding

**Progressive disclosure. No tutorial. The captain learns by doing.**

- **First 30 minutes:** The player starts at Freeport with a bad ship, no crew, and one contract on the board (a simple delivery). The delivery teaches: check the board, accept a job, buy fuel, launch, travel, arrive, complete. No combat, no cultural mechanics, no reputation complexity. Just: move cargo, get paid.
- **Hours 1–2:** First crew member recruited (Keth navigator at a Keth station). Crew screen appears for the first time. First cultural interaction (simple — the navigator handles it). First lane encounter (a distress call — fight, flee, or investigate). Each new system appears when the world demands it, not before.
- **Hours 2–5:** Systems layer in as they become relevant. Reputation bar fills in as the player visits new civilizations. Combat grid appears on the first hostile encounter. The Veshan Debt Ledger appears on first Veshan interaction. Nothing is explained in advance — everything is explained in context.
- **The `?` key:** Always available. Context-sensitive help that explains what the current screen shows and what the player's options mean. Not a tutorial — a reference. The player who never presses `?` should still understand the game through playing it.

---

## Readability Rules

1. **Numbers mean something.** Don't show "+12 reputation" — show "Keth: Respected (+33)." The player reads their position, not an increment.
2. **Colors are consistent.** Green = healthy/positive. Yellow = caution/neutral. Red = danger/negative. Across all screens, all contexts.
3. **Faction identity is visually distinct.** Each civilization has a consistent text marker or color when referenced: Compact (steel/blue), Keth (amber/organic), Veshan (crimson/angular), Orryn (teal/fluid), Reach (grey/rough). The player recognizes a Veshan contract vs a Keth contract at a glance.
4. **Hit chances are always shown.** In combat, every action displays its probability before the player commits. No hidden information.
5. **Enemy patterns are always shown.** In combat, each enemy's behavioral tendency is stated in plain language. The player fights with information, not guesswork.
6. **Cultural requirements are always shown.** At encounters, options that require cultural knowledge display the requirement and whether the player meets it.
7. **Crew contribution is always attributed.** When a crew member enables something (ship ability, cultural knowledge, narrative insight), the UI says so. The player always knows why they can do what they can do.

---

## Accessibility

- **Fully keyboard-navigable.** No mouse required for any action.
- **Color is never the sole indicator.** All color-coded information also has text labels, symbols, or position cues. Green/yellow/red bars also show percentage numbers.
- **Screen reader compatible text.** If TUI: all UI elements are text. If Tauri: semantic HTML with ARIA labels.
- **Remappable keys.** All hotkeys configurable through settings.
- **Adjustable text speed.** Lane narration and combat text can be instant, fast, or slow.
- **No twitch requirements.** Turn-based combat, no timers on decisions, no reaction-speed tests. The player thinks, then acts.

---

## Always Visible

- Credits
- Ship condition (%)
- Crew fitness (X/Y healthy)
- Day counter
- Top 3 relevant reputation standings
- Current location or route

These are the captain's instruments. They never leave the screen.

## May Remain Hidden

- Full cargo manifest (one overlay away — `I` key)
- Detailed reputation breakdown (one overlay away — `R` key)
- Cultural knowledge levels (visible in crew screen, not persistent)
- Veshan debt details (one overlay away — `D` key or in reputation overlay)
- Investigation progress (journal overlay — `J` key)
- Consequence log (journal overlay — recent events section)
- Ship upgrade details (ship screen at station)
- Trade good price history (market screen at station)

**Principle:** The persistent bar shows pressure. The overlays show detail. The player feels the state always and inspects it when they choose to.

---

## How Plot Leads Appear

Investigation beats and narrative hooks must feel like part of the captain's life, not a separate quest UI.

**They appear through:**
- Station flavor text: "A Compact officer is watching the docking bay. Maren says she recognizes the rank insignia — intelligence division."
- Lane narration: "Your scanner picks up a derelict on long-range. Dax says the hull markings are Compact military — decommissioned, supposedly."
- NPC dialogue: A contact mentions your name, a merchant drops a rumor, an Orryn broker offers to sell you information.
- Crew remarks: Kethra recognizes a name from your court-martial. Maren admits she processed the paperwork.
- Consequence events: An NPC you spared 5 sessions ago shows up with information.

**They're logged in the journal** as narrative fragments, not objectives. The player pursues them when they choose to, on their schedule, as part of their route planning — not as a separate quest chain.

---

## Unresolved Questions

- TUI or Tauri? This doc is designed to work for both, but Tauri allows richer visual treatment (faction colors, grid rendering, crew portraits). TUI is proven and faster to build. Platform decision affects interface scope.
- How much crew portrait/visual identity is needed? TUI: none (text only, personality through dialogue). Tauri: portraits add recognition but cost art budget.
- Map screen design: how does the star system map look? Node graph (like FTL) or spatial map? Node graph is simpler and more readable. Spatial map is more immersive.
- Sound design: any audio? Ambient lane sounds, combat impacts, station atmosphere? Or pure text? Budget question.
- How does the Orryn Telling render? A special dialogue format? Color-shifting text to represent chromatophore honesty? A structured input where the player composes their statement?

## Contradictions Discovered

- "No tutorial" vs "11 interconnected systems" — progressive disclosure must be very carefully paced. If two systems appear in the same session before the player has internalized the first one, the game feels overwhelming. The unlock cadence (from Campaign State doc) must be tested against the onboarding pace.
- "Pressure surfaces passively" vs "some events need to interrupt" — a reputation threshold crossing or a crew departure is too important to be a quiet bar update. The feedback hierarchy must distinguish between "update the bar" and "stop and show the player what happened." The threshold is: if the player's options have changed, interrupt. If a number shifted, update.
- "One continuous flow, no modes" vs "combat has a grid that replaces the screen" — the transition into and out of combat must feel natural. The grid appears because violence happened, and disappears because it ended. No loading screen, no mode-switch fanfare. Enter → grid drawn → first turn. Exit → aftermath text → back on the lane or at the station.

## What Must Be Proven Next

- Production Truth: engine/stack, content pipeline, what's hand-authored vs systemic, vertical slice definition, cut tiers.
- A full UI walkthrough: one complete session (dock → trade → travel → encounter → combat → arrive → resolve) with every screen transition shown.
- The crew screen proof: does the three-layer crew display actually work in practice? Mock it up with real crew data.
- Grid readability proof: can the player understand a combat situation in 5 seconds from the text grid? Test with a friend who hasn't seen the design.
