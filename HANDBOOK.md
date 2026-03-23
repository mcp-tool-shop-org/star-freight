# Star Freight Handbook

This is the operating manual. Not for players — for anyone building, expanding, testing, or maintaining the game. If you're a future Claude, a contributor, or the lead developer returning after time away, this is the document that keeps Star Freight honest.

---

## 1. What this game is

Star Freight is a captain-life RPG. The player hauls freight, reads people, survives encounters, learns dangerous truths, and keeps flying long enough for a life to take shape.

It is **not** a space tactics game with freight flavor. It is **not** a merchant sim with story bolted on. It is **not** a JRPG in space. It is one continuous campaign where trade, tactics, culture, and investigation all write to the same state.

### The captain fantasy

The player should feel like a working captain under recurring pressure. Someone whose crew changes what the ship can do. Someone moving through civilizations with distinct social logic. Someone who learns dangerous truths through ordinary work. Someone who can survive, profit, compromise, lose face, become entangled, and define a way of living.

### What Star Freight must never become

- A Portlight reskin with different nouns
- A generic tactics game where combat is the point
- A quest-log detective RPG where investigation is separate from life
- Decorative culture where every civilization plays the same
- Content volume that does not sharpen captain identity

If any of these start happening, stop building and re-read this section.

---

## 2. The four system truths

Every significant decision — what to build, what to cut, what to expand, what to test — must reinforce one or more of these.

### Crew changes the campaign

A crew member is not a stat buff. They are a binding constraint. One person simultaneously affects ship abilities, combat options, cultural access, investigation interpretation, morale risk, and narrative obligation.

The test: one crew state change (injury, departure, morale collapse) must ripple across at least three systems without bespoke scripting. If it doesn't, the crew architecture is lying.

### Combat changes the campaign

Combat is a captain's problem, not a tactics toy. Victory, loss, and retreat must all write materially different state back into credits, cargo, ship condition, crew condition, reputation, investigation, and consequences.

The test: the same encounter resolved three ways must produce three different next decisions for the player. If it doesn't, combat is decorative.

### Culture changes the campaign

Civilizations have different social logic, not different flavor text. Knowledge changes which options exist, not just how they're described. The Keth seasonal calendar, the Veshan Debt Ledger, the Orryn Telling, and the Reach faction reading are all mechanical systems, not lore.

The test: the same player action in two different civilizations must produce different outcomes because the social rules are structurally different. If it doesn't, culture is paint.

### Plot changes the campaign

Investigation emerges from trade, travel, paperwork, encounters, and crew interpretation. Not from quest givers. Not from cutscenes. Not from a separate story tab. Leads surface because the player was hauling cargo, winning fights, reading documents, or listening to crew.

The test: a lead must be discoverable through at least two different source types (trade, combat, cultural, crew, station, transit). If it can only be found one way, it's authored too tightly.

---

## 3. Campaign state law

All major systems transact through shared campaign state. The canonical variables are defined in `STATE_MODEL.md` and `REGISTRY_STATE_DICTIONARY.md`. No system should maintain shadow state that the campaign doesn't know about.

The shared variables that matter most:

- **Credits** — survival and leverage
- **Crew roster** — who's aboard, their status, their contributions
- **Ship condition** — hull, shield, fuel, systems, cargo
- **Reputation** — per-faction standing with breakpoints
- **Cultural knowledge** — per-civilization level (0-3)
- **Investigation** — thread states, fragments, evidence grades
- **Day counter** — time pressure (crew pay, contract deadlines, seasonal cycles, delay consequences)
- **Consequence log** — the world's memory of what you did

If a new system needs state not on this list, update the State Dictionary first. Then build.

---

## 4. Product surface law

A system is not finished when it exists in backend code. It is finished when the player can see, feel, and act on it.

### The universal screen law

Every screen answers these, in this order:

1. Where am I?
2. What matters right now?
3. What can I do?
4. What will it cost or risk?
5. What changed last?

Any screen that violates this order fails the audit.

### The crew screen is the thesis surface

If one screen had to carry the entire game's identity, it would be the Crew Screen. Each crew line must communicate: this person changes my ship, my social access, my tactical options, and my future trouble. Injury must hurt at a glance. Absence must feel like loss.

### After-action is the campaign proof

The After-Action Summary is where the player feels that combat was a campaign event. Every state delta — credits, hull, cargo, reputation, crew injuries, ability degradation, investigation fragments, consequence tags — must be listed explicitly. No hidden changes. If the player has to guess whether something mattered, the summary failed.

### The Captain's View is ship instrumentation

The persistent bar should feel like a cockpit, not a debug strip. Credits, hull, fuel, crew fitness, day, reputation trends, injury alerts, pay timer. Calm when things are stable. Urgent when they're not. Visible everywhere important.

---

## 5. The three world layers

The universe expresses three kinds of aliveness. Every new content unit should know which layer it's extending.

### Human layer — people are living here

Civilian traffic, ritual commerce, mourning, kinship, sacred freight, personal obligation. This is the texture that makes the universe feel socially occupied.

*Proved through Working Lives: Mourning Quay, Pilgrim's Ribbon, Cinder Span, Brood Silk, Cold Lantern Freight, Witness Run, Hearth Right, Sera Vale, Ghost Tonnage.*

### Institutional layer — power has memory here

Claims, liens, seized cargo, monitored lanes, legal races, paper violence, administrative vulnerability. This is the pressure that makes the universe feel governed and watched.

*Proved through Houses, Audits, and Seizures: Registry Spindle, White Corridor, Grain Eclipse, Bond Plate, Bonded Relief Run, Claim Courier, Seizure Notice, Nera Quill, Paper Fleet.*

### Historical layer — the world is tilting here

Scarcity politics, ration priority, convoy routing, emergency authority, selective legitimacy, managed instability. This is the momentum that makes the universe feel like it's going somewhere the player can't fully control.

*Proved through Shortages, Sanctions, and Convoys: Queue of Flags, Mercy Track, Red Wake, Ration Grain, Coolant Ampoules, Priority Relief, Embargo Slip, Convoy Refusal, Ilen Marr, Dry Ledger.*

---

## 6. Content doctrine

### The prime rule

> **Do not invent new truth. Express existing truth through content.**

New stations, lanes, crew, contracts, goods, encounters, and investigation threads must reinforce the game's proved laws. They must not introduce new systems, new currencies, new progression layers, or new mode surfaces.

### Three admission questions

Every content unit must answer before it enters the game:

1. **What decision does this create?**
2. **What truth does this reinforce?**
3. **Why isn't an existing unit already doing this?**

If the answers are weak, the content is decorative. Cut it.

### Content unit standards

- A **station** must create different captain behavior from every other station
- A **lane** must justify itself against alternate routes
- A **crew member** must affect all four system truths and hurt when absent
- A **contract** must pressure at least two layers before completion
- An **encounter** must make aftermath as explicit as the fight
- An **investigation thread** must be learnable by living the job
- A **trade good** must tell the player something about the world

### Production templates

All expansion content should be authored through the templates in `design/templates/`. The Content Pass template gates every batch with proof coverage checks and an exit criterion.

---

## 7. Captain paths

The game is replayable because different crew, routes, and risk postures produce different captain lives.

### Proved postures

| Posture | Crew bias | Route bias | Fear |
|---|---|---|---|
| **Relief / Legitimacy** | Thal + Ilen | Keth + convoy lanes | Delay, undercapacity |
| **Gray / Document** | Sera + Nera | Registry + Orryn | Seizure, exposure |
| **Honor / Frontier** | Varek + Thal | Veshan + contested lanes | Escalation, thin support |

### Divergence is real only if it changes five things

1. Route choice
2. Contract preference
3. Encounter profile
4. Investigation posture
5. Failure texture

If two runs differ only in bonuses or dialogue, the branching is fake.

### The failure rule

Different captain lives must **fear different things**. This is the strongest divergence signal. If all three postures fail the same way, the game has one life with three costumes.

---

## 8. Expansion rules

### What to add

More of what already works:

- Stations with distinct social and economic roles
- Lanes with sharper route psychology
- Crew who change all four truths in new ways
- Contracts with distinct risk shapes
- Encounters with different campaign consequences
- Investigation threads that emerge through different captain lives
- Trade goods that carry cultural, political, or institutional meaning

### What not to add

- New currencies without strong proof of need
- Ornamental lore systems
- Detached minigames
- Progression layers that dilute captain identity
- Content that is just volume

### The multiplication rule

Expansion should increase **difference**, not merely amount. A new station that feels like an existing station is worse than no station. A new crew member who doesn't change posture is worse than an empty slot.

---

## 9. Balance doctrine

No captain path should dominate profit, survivability, access, legitimacy handling, or investigation velocity. Legal, gray, and confrontational play must all remain viable.

### What balance protects

- Tight but non-humiliating economy pressure
- Meaningful crew dependence
- Real retreat decisions
- Visible cost to cultural ignorance
- All three postures remaining different and sustainable

### What balance prevents

- One solved optimal path
- Runaway wealth trivializing pressure
- Gray play automatically dominating
- Safe play becoming dead air
- Combat as the universal answer

---

## 10. Build history

| Phase | What | Tests |
|---|---|---|
| 0 | Fork Portlight | 1,832 |
| 1 | Crew Binding Spine | +45 |
| 2 | Grid Combat Engine | +31 |
| 3 | Cultural Knowledge | +40 |
| 4 | Investigation System | +38 |
| 5 | Content Rewrite | +39 |
| 6 | Vertical Slice (3 GDOS proofs pass) | +16 |
| 7A | Working Lives | +19 |
| 7B | Houses, Audits, Seizures | +18 |
| 7C | Shortages, Sanctions, Convoys | +17 |
| 8 | Captain Paths (divergence proved) | +30 |
| 9A | TUI Audit | — |
| 9B | TUI Product Surfaces | +36 |
| **Total** | | **2,161** |

---

## 11. Playtest law

A playtest succeeds when feedback is about the game's pressures, not interface confusion.

### Core questions

- Did the player know what mattered right now?
- Did they understand why an option existed or was unavailable?
- Did they feel crew as binding law?
- Did they notice culture before and after a mistake?
- Did they understand what changed after an encounter?
- Could they describe what kind of captain they were becoming?

### Path questions

- Does this run want different stations and routes than another?
- Does it fear different failure states?
- Does it reach investigation through different sources?
- Does crew choice change social and tactical posture enough?

The full playtest checklist is at `design/PLAYTEST_TUI_CHECKLIST.md`.

---

## 12. The standing rule

When unsure what to build, expand, or fix:

- Does it reinforce one of the four truths?
- Does it sharpen a captain life?
- Does it create a decision the player can feel?
- Does it make the universe more alive without inventing new system truth?

If not, it can wait.

---

*This handbook is not a contract. It is a compass. The game should always be more interesting than the document that describes it.*
