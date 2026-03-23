# Build Plan — Star Freight

> Phase 0 is complete when the fork runs, the seams are mapped, and the build order is locked.
> Production phases are ordered by thesis risk, not feature completeness.

---

## Phase 0: Fork Truth (current)

**Goal:** Inherit Portlight, prove the fork runs, map every inherited vs new system.

- [x] Create repo (mcp-tool-shop-org/star-freight)
- [x] Copy Portlight source, tests, world data
- [x] Update pyproject.toml for Star Freight
- [x] Write FORK_MAP.md (inherited vs replaced vs new vs removed)
- [ ] Write ACCEPTANCE_CRITERIA.md (proof-derived pass conditions)
- [ ] Write STATE_MODEL.md (code-facing canonical state)
- [ ] Verify inherited tests pass (`pytest`)
- [ ] Initial commit and push
- [ ] Strip removed modules (printandplay, medieval weapons/armor, fleet)
- [ ] Verify tests still pass after strip

**Exit condition:** Fork runs green. Every system is tagged inherited/replace/new/remove. Build order is locked.

---

## Phase 1: Crew Binding Spine

**Goal:** Build the thesis seam. Crew members are the binding constraint across trade, tactics, and narrative.

**Why first:** If crew binding is weak, the game becomes three stacked systems. This is the single highest-risk design decision.

- [ ] Design crew data model (identity, abilities, cultural knowledge, loyalty, fitness, ship role)
- [ ] Implement crew roster management (recruit, dismiss, injury, recovery)
- [ ] Wire crew to trade (cultural access, negotiation modifiers, merchant relationships)
- [ ] Wire crew to combat (abilities determined by crew, absence limits options)
- [ ] Wire crew to narrative (crew unlock plot leads, cultural knowledge gates)
- [ ] Wire crew to ship (engineer → repair ability, gunner → weapon power, pilot → evasion)
- [ ] Crew morale and pressure (pay, injury, loyalty shifts, departure risk)
- [ ] Tests for all crew bindings

**Exit condition:** Adding/removing a crew member visibly changes trade options, combat abilities, and narrative access in a test harness.

---

## Phase 2: Grid Combat Engine

**Goal:** One tactical combat system that works for ground encounters and ship battles.

**Why second:** Combat is the second most visible system. It must be unified before content.

- [ ] Grid model (hex or square, obstacles, cover, positioning)
- [ ] Turn system (initiative, action points, move/attack/ability/item)
- [ ] Ground combat entities (crew as combatants, enemy archetypes)
- [ ] Ship combat entities (ships-as-characters, same grid, bigger numbers)
- [ ] Crew abilities wired to combat (determined by crew binding spine)
- [ ] Victory/loss/retreat with real state consequences
- [ ] Boarding transition (ship combat → ground combat mid-encounter)
- [ ] Encounter state machine (replaces Portlight's 4-phase escalation)
- [ ] Combat views (TUI grid renderer)
- [ ] Tests: full encounter with state change verification

**Exit condition:** Can play a ship encounter that transitions to boarding, with crew abilities active, and aftermath changes campaign state.

---

## Phase 3: Cultural Knowledge System

**Goal:** Civilizations feel alive and knowledge matters mechanically.

- [ ] Cultural knowledge model (per-civilization understanding level)
- [ ] Knowledge gates (trade access, diplomatic options, safe passage, ritual participation)
- [ ] Knowledge acquisition (crew members, time in culture, cultural events, study)
- [ ] Customs and consequences (violate customs → reputation damage, respect them → access)
- [ ] Civilization-specific mechanics (Keth seasons, Veshan debt, Orryn drift markets, Sable Reach silence protocols)
- [ ] Tests: cultural knowledge changes available options at a station

**Exit condition:** Player with Keth crew member can access Keth seasonal markets that a culturally ignorant player cannot.

---

## Phase 4: Investigation System

**Goal:** The conspiracy plot layer that gives the campaign its arc.

- [ ] Investigation state (leads, evidence, connections, dead ends)
- [ ] Lead acquisition (crew contacts, station events, trade encounters, faction relationships)
- [ ] Evidence gates (investigation progress unlocks plot beats)
- [ ] Investigation cost (time, reputation, money — the plot competes with survival)
- [ ] 10 investigation beats mapped to campaign progression
- [ ] Tests: investigation progress changes available narrative and gameplay options

**Exit condition:** Investigation feels like a real campaign thread with economic and political cost, not a separate quest log.

---

## Phase 5: Content Rewrite

**Goal:** Replace all Portlight content with Star Freight world.

- [ ] 5 civilizations fully defined in code (from Content Architecture)
- [ ] 20 stations (4 per civ) with markets, services, cultural rules
- [ ] Space lanes between stations with distance, risk, encounter tables
- [ ] 20 trade goods with civilization affinities
- [ ] Ship classes (sci-fi vessels replacing sailing ships)
- [ ] 7 crew members with full identity, abilities, cultural knowledge, loyalty arcs
- [ ] Contract families reskinned for sci-fi
- [ ] Encounter tables (pirates, patrols, faction conflicts, hazards)
- [ ] Station NPCs with cross-station relationships
- [ ] Transit events (replacing sea culture)

**Exit condition:** Portlight maritime content fully replaced. No medieval language, no ocean references, no sailing terminology in gameplay.

---

## Phase 6: Vertical Slice

**Goal:** Prove the three-layer loop works end to end.

- [ ] 5 stations (one per civ), 8 lanes, 5 trade goods
- [ ] 2 crew members recruited and wired
- [ ] 3 contract types available
- [ ] At least 1 ground combat and 1 ship combat encounter
- [ ] Cultural knowledge check at 1 station
- [ ] 1 investigation lead discoverable
- [ ] Economy runs for ~30 minutes of play without collapse
- [ ] All 3 acceptance criteria pass

**Exit condition:** Golden Path, Encounter, and Economy proofs all pass as playable sequences.

---

## Phase 7: Full Build

**Goal:** Scale from vertical slice to full game.

- [ ] All 20 stations live
- [ ] All 7 crew members recruitable
- [ ] Full investigation chain (10 beats)
- [ ] All 5 civilization cultural mechanics active
- [ ] Balance harness adapted and running
- [ ] Stress harness extended with new invariants
- [ ] Full playthrough possible: disgrace → merchant/pirate → resolution

**Exit condition:** The full designed game is playable. GDOS Thesis Lock is honored.

---

## Build Order Law

The order above is not arbitrary. It follows thesis risk:

1. **Crew binding** — if this fails, no game
2. **Combat** — if this is boring, players leave
3. **Culture** — if this is shallow, the world is dead
4. **Investigation** — if this is missing, no campaign arc
5. **Content** — if this is wrong, it can be rewritten
6. **Slice** — proof of integration
7. **Full** — scale

Never skip ahead. Never build content before systems. Never build systems before the thesis seam.
