# Production Truth — Star Freight

> Prevents "we designed a game, but not one we can actually build." This doc defends the game's real shape by defining what the shippable version is, what's mandatory, what's aspirational, and what dies first under pressure.

---

## Engine / Stack

**Primary: Rust TUI (proven stack).**

Portlight is Rust + Python (CLI). Saint's Mile is Rust TUI. The team has shipped both. The choice:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Python CLI (Portlight direct fork)** | Fastest start. Portlight codebase is proven (1,832 tests). Direct code reuse for world sim, economy, NPC memory, consequence engine. | Python TUI limitations. Combat grid rendering is harder. Performance ceiling lower for complex state. | **Start here.** Fork Portlight, reskin to space, prove the thesis. |
| **Rust TUI** | Best performance. Saint's Mile proves the stack. Richer TUI rendering for combat grid. | Slower start. Portlight's Python systems must be rewritten. | **Migrate after vertical slice** if the game proves out. |
| **Tauri (desktop)** | Richest interface. Crew portraits, visual grid, audio. | Heaviest build. Longest path to playable. Unproven for this game type. | **Only if the game succeeds and warrants a visual edition.** |

**Decision: Python CLI fork of Portlight for the vertical slice and alpha. Rust TUI migration for beta if the game proves out. Tauri is a luxury goal.**

This means the vertical slice can be playable in weeks, not months. The Portlight codebase provides:
- World structure (ports → stations, routes → lanes)
- Trade economy (goods, prices, supply/demand)
- NPC memory and standing-aware behavior
- Reputation system
- Companion/crew system (morale, loyalty)
- Consequence engine
- Sea culture engine (→ space culture)
- Encounter generation
- Pirate faction ecosystem
- Seasonal system
- Cross-port politics

**What must be built new (on the fork):**
- Turn-based tactical grid combat (replacing Portlight's stance/broadside systems)
- Ship-as-character combat model
- Crew-to-ship ability mapping
- Cultural knowledge system (the 4-level per-civ mechanic)
- Veshan Debt Ledger
- Civilization-specific cultural mechanics (permits, seasonal protocols, Telling, rep reading)
- Investigation system (10 beats, scattered discovery)
- Sci-fi content layer (all new: station names, NPC names, goods, lore, encounter text)
- The Captain's View persistent bar
- The reskinned UI (ocean terminology → space terminology throughout)

---

## Content Pipeline

All content in this game is text. No art, no audio, no animation in the shippable version. This is the single biggest production advantage — content creation is writing, not asset production.

| Content Type | Source | Format | Volume |
|-------------|--------|--------|--------|
| Station profiles | Hand-authored | JSON + flavor text | 20 stations |
| NPC profiles | Hand-authored (template + personality) | JSON | ~100–134 NPCs |
| Trade goods | Hand-authored | JSON (name, base price, civilization, contraband flags) | ~20 goods |
| Lane definitions | Hand-authored | JSON (origin, destination, distance, danger, terrain) | ~40 lanes |
| Lane encounter text | Hand-authored per route + systemic templates | Text snippets | ~80–100 route encounters + 20 templates |
| Combat enemy types | Hand-authored | JSON (stats, behavior pattern, abilities) | ~15 ground types + ~10 ship types |
| Cultural events | Hand-authored | Scripted encounter sequences | ~15 events (3 per civ) |
| Investigation beats | Hand-authored | Scripted narrative sequences | 10 beats |
| Crew member profiles | Hand-authored (deep) | JSON + dialogue trees + loyalty missions | 6–7 crew members |
| Crew loyalty missions | Hand-authored | Scripted multi-stage encounters | 6–7 missions |
| Seasonal content (Keth) | Hand-authored | JSON (per-season trade/custom/access rules) + flavor text | 4 seasons × modifiers |
| Station flavor text | Hand-authored + consequence-reactive templates | Text snippets | ~3–5 per station × reputation states |
| NPC dialogue | Hand-authored (key NPCs) + template (generic) | Text | ~20 key NPCs with trees, ~100 template NPCs |
| Contract templates | Hand-authored types + systemic generation | JSON + text | 8 types × ~5 variants each = ~40 templates |

**Total hand-authored content estimate:** ~200–250 text documents/snippets, ~50 JSON definitions, 10 scripted sequences, 6–7 deep crew profiles with loyalty arcs. This is achievable because it's all text — no art pipeline, no audio pipeline, no animation pipeline.

**Systemic content (Portlight engine generates):** Trade prices, encounter selection, NPC greeting variation, consequence-triggered events, contract board population, crew morale reactions, lane narration assembly. This is where the Portlight fork pays for itself — the engine already does all of this.

---

## Tooling Needs

| Tool | Purpose | Exists? |
|------|---------|---------|
| Portlight test harness | Balance testing, economy simulation, encounter validation | Yes (1,832 tests) |
| Station editor | Create/modify station profiles (JSON) | No — use text editor. Stations are small JSON files. |
| NPC generator | Batch-generate template NPCs from civilization + role templates | Partially (Portlight has NPC templates). Extend for alien civs. |
| Combat balance sim | Simulate fights with given party vs enemy compositions | No — build as part of combat engine. Priority. |
| Economy sim | Run multi-session trade simulations to validate margins | Partially (Portlight has balance harness). Extend for new goods/stations. |
| Consequence debugger | View consequence log and upcoming triggered events | No — build as debug CLI command. |
| Save inspector | Read and validate save files | Build alongside save system. |

**No new tools block the vertical slice.** The Portlight test harness covers economy and world sim testing. The combat balance sim is the only critical new tool and should be built as part of the combat engine (it's the same code — simulate a fight without rendering it).

---

## Save / Load Architecture

**What's persisted (the campaign state from the Progression Economy doc):**

| Data | Format | Size |
|------|--------|------|
| Credits | Integer | Trivial |
| Reputation (all factions + sub-factions) | Dict of integers | ~15 values |
| Cultural knowledge (per civ) | Dict of integers | 5 values |
| Crew roster (full profiles, morale, loyalty, injuries) | List of dicts | 6–7 entries |
| Ship state (hull, shields, systems, upgrades, cargo) | Dict | 1 entry |
| Cargo hold contents | List | ~10 entries max |
| Day counter | Integer | Trivial |
| Veshan Debt Ledger | List of debt objects | ~5–15 entries |
| Investigation progress | Integer + list of found beats | ~10 flags |
| Consequence log | List of tagged events | ~50–200 entries |
| NPC memory (per named NPC, last 3 interactions) | Dict of lists | ~60–100 entries |
| Active contracts | List | 3 max |
| World state (supply/demand per station, faction events) | Dict | ~20 stations × ~20 goods |
| Current location + lane position | String + integer | Trivial |
| Keth season counter | Integer | Trivial |

**Format:** JSON. Single file. Portlight uses JSON saves — same pattern. Total save file size: ~50–100KB estimated. Trivial.

**Save points:** Auto-save on dock at station + auto-save on travel day advance. Manual save available at stations. No save during combat (combat is short enough that this isn't painful — 5–8 turns, 5–10 minutes max).

**Migration:** Save format includes a version number. New versions include migration functions that update old saves. Portlight pattern — proven.

---

## Test Strategy

| Layer | What's Tested | How | Coverage Target |
|-------|--------------|-----|-----------------|
| Economy | Trade margins, price stability, sink/faucet balance, soft-lock prevention | Portlight balance harness extended. Run 100-session simulations with different strategies (cautious, aggressive, pirate, merchant). | All anti-soft-lock rules verified. No strategy produces negative net income over 10 sessions. |
| Combat | Balance between party compositions, fight duration targets (5–8 turns), retreat viability, boarding transition | Combat balance sim. Run every enemy type vs every reasonable party composition. | No fight exceeds 10 turns. No party composition is nonviable. Retreat always available. |
| Reputation | Gate thresholds work, cross-faction shifts are balanced, no faction is unreachable, recovery paths function | Unit tests on reputation math. Integration tests on gate behavior. | All 7 breakpoints function correctly per faction. Recovery from -50 to 0 takes <10 sessions. |
| Cultural | Knowledge levels gate correctly, misstep consequences are survivable, crew knowledge grants work | Unit tests. Integration tests per cultural mechanic (permits, seasons, debts, telling, rep reading). | Every cultural interaction has a testable outcome. No interaction soft-locks the player. |
| Consequence | Events trigger correctly from tagged actions, NPC memory works, escalation compounds | Portlight's existing test suite adapted. Event trigger validation. | 100% of consequence triggers fire when conditions are met. No orphaned triggers. |
| Crew | Morale math, loyalty tiers, ship ability grants, departure conditions, recruitment gates | Unit tests. Multi-session integration tests. | Morale never goes negative. Departure triggers only at documented thresholds. Ship abilities correctly reflect crew state. |
| Narrative | Investigation beats discoverable in correct order, gates function, endgame paths reachable | Scripted playthrough tests. Multiple paths validated. | All 10 beats reachable. Endgame reachable from 3+ different reputation portfolios. |
| Save/Load | Round-trip persistence, migration from older versions, corrupt save handling | Unit tests. Save → load → verify state identity. | 100% state round-trip accuracy. |

**Playtest protocol:** After vertical slice, recruit 2–3 playtesters. Focus areas: (1) do all three layers feel connected? (2) does the crew feel like a multi-system asset? (3) is pressure motivating or annoying? (4) can they understand the game without a tutorial?

---

## Telemetry / Debug Views

Development-only views accessible via CLI flags or debug commands.

| Debug View | What It Shows | Why |
|-----------|--------------|-----|
| `--debug-economy` | Real-time credit flow, margin calculation, sink/faucet rates per session | Catch economy imbalance before playtesters hit it. |
| `--debug-reputation` | All faction standings with recent change history, gate status | Verify cross-faction shifts and gate thresholds. |
| `--debug-consequence` | Full consequence log with trigger conditions and upcoming events | Ensure events fire correctly. Diagnose "why did that happen" questions. |
| `--debug-combat` | Hit chance calculations, damage formulas, turn counter, ability cooldowns | Balance combat encounters during development. |
| `--debug-npc` | NPC memory state, standing-aware behavior selection, dialogue tree position | Verify NPC reactions match reputation state. |
| `--debug-culture` | Cultural knowledge levels, available interactions, misstep risk calculations | Test cultural mechanics in isolation. |
| `inspect` command (in-game) | Show raw state for any game object (NPC, station, good, crew member) | Quick data checking during development. |

---

## Vertical Slice Definition

**The vertical slice must prove the three-layer loop works.** Not "all content exists" — but "trade feeds tactics, tactics feed plot, plot feeds trade, and the player feels it."

### What the vertical slice contains:

**World:** 5 stations (one per civilization), 8 lanes connecting them, 5 trade goods (1 per civ).

**Crew:** 2 recruitable crew members (1 Keth, 1 Reach). Player character as third.

**Combat:** Ground theater functional on 8x8 grid with 3 unit types (fighter, tech, rusher). Ship theater functional with 3 ship types (player, pirate raider, Compact patrol). Boarding transition works.

**Trade:** Buy/sell at 5 stations. Supply/demand functional. Reputation affects prices. One contraband good.

**Reputation:** 2 factions tracked (Keth, Reach). Breakpoints at 0, +25, +50 functional. Standing-aware NPC greetings.

**Culture:** Keth seasonal protocol (1 season active). One cultural event (gift ritual).

**Contracts:** 3 contract types functional (trade run, bounty, smuggling).

**Consequence engine:** Basic version — actions logged, 3 consequence triggers functional.

**Investigation:** Beats 1–2 placeable and discoverable.

**Crew system:** Morale, loyalty (Stranger/Trusted), ship ability grants, one crew cultural knowledge contribution.

**Ship:** Basic stats, fuel consumption, maintenance degradation, one upgrade purchasable.

**UI:** Captain's View persistent bar, station screen (market + contracts + crew), lane narration, combat grid, one overlay (reputation).

### What the vertical slice proves:

1. **The loop:** A player can trade at a Keth station, get ambushed on the lane (combat), and discover an investigation beat at their destination — and all three feel connected through the shared campaign state.
2. **Crew as binding constraint:** Recruiting the Keth navigator changes trade margins (cultural access), combat capability (ship ability), and narrative options (Keth cultural event).
3. **Pressure creates decisions:** The player's floor costs (fuel, maintenance) force them to take contracts. The contracts force them into lanes where combat happens. Combat outcomes shift reputation which affects their next trade.
4. **It feels like one game.** The Captain's View stays on screen. The transitions between station → lane → encounter → combat → station feel continuous. No mode-switching.

### What the vertical slice does NOT contain:

- All 20 stations (only 5)
- All trade goods (only 5)
- All crew members (only 2 + player)
- Veshan Debt Ledger
- Orryn Telling mechanic
- Full investigation (only 2 of 10 beats)
- Ship upgrades beyond tier 1
- New ship purchase
- Crew loyalty missions
- Proxy war contracts
- Ancestor salvage runs
- Full lane encounter variety (templates only)
- Full NPC roster (5–10 key NPCs, not 134)

**The vertical slice is ~15% of final content but 100% of the systems.** Every system runs. Content is thin. If the loop works with 5 stations, it will work with 20.

---

## Mandatory vs Aspirational

### Mandatory (the game doesn't ship without these)

| System | Why It's Mandatory |
|--------|-------------------|
| Trade economy (buy/sell/margins) | Core loop layer 1. |
| Turn-based grid combat (ground + ship) | Core loop layer 2. |
| Reputation (per-faction, gated access) | Core loop layer 3. The binding variable. |
| Crew system (morale, loyalty, multi-layer contribution) | The binding constraint. Without this, the three layers are disconnected. |
| Consequence engine | What makes the world feel alive. Without it, actions have no echo. |
| Cultural knowledge (4 levels) | What makes civilizations gameplay-distinct, not just flavor. |
| 20 stations across 5 civilizations | The Portlight-scale world. Fewer stations = less trade variety = thin economy. |
| ~40 lanes with encounter generation | Travel must feel alive. |
| 6 recruitable crew with loyalty arcs | Crew is the game. 6 is the minimum for meaningful roster decisions. |
| Investigation (10 beats) | The narrative spine. Without it, the merchant/pirate spectrum has no endgame. |
| Ship maintenance + upgrades | Scrappy survival pillar. Without ship pressure, the economy has no teeth. |
| Anti-soft-lock systems | Non-negotiable. The player must always be able to recover. |
| Captain's View (persistent bar) | The interface thesis. Without it, the game feels like three tabs. |

### Aspirational (the game is better with these but ships without them)

| Feature | Why It's Aspirational | When It Gets Cut |
|---------|----------------------|------------------|
| Veshan Debt Ledger | Deep and unique, but the Veshan work with standard reputation if debts are cut. | If production time runs short on cultural systems. |
| Orryn Telling mechanic | Distinctive, but Orryn function with standard negotiation if the Telling is cut. | If cultural interaction design takes too long. |
| Orryn mobile drifts | Cool mechanic, but fixed Orryn stations work fine. | If the simulation complexity is too high. |
| Keth seasonal protocols (full 4-season cycle) | Ideal, but a simpler 2-season model (harvest/dormancy) captures 80% of the gameplay value. | If content volume is too high for all 4 seasons. |
| New ship purchase (late game) | Nice milestone, but the game works with one upgradeable ship. | If ship balance testing takes too long. |
| Crew portraits (Tauri only) | Visual identity, but the game is text-first. | If Tauri build happens at all. |
| Sound design | Atmospheric, but the game is proven as pure text (Portlight, Saint's Mile). | Unless explicitly budgeted. |
| 134 NPCs (Portlight scale) | Ideal density. 80–100 works. 60 is the floor. | If NPC authoring bogs down. |

---

## Cut Tiers

> **WARNING: The build target is the FULL game — all 5 civilizations, all 7 crew, all 20 stations, all cultural mechanics, all 10 investigation beats. These tiers are emergency fallback plans, not scope recommendations. No tier below Full should be treated as a target unless the lead developer explicitly authorizes a scope reduction in response to concrete production pressure.**

What gets cut first IF production pressure hits. Each tier preserves the three-layer loop and the crew binding constraint. The game gets smaller but doesn't lose its shape.

### Tier 1: 90% capacity (mild pressure)

**Cut:**
- Orryn mobile drifts → fixed stations
- Keth 4 seasons → 2 seasons (harvest/dormancy)
- NPC count: 134 → 100
- Lane encounter variety: 100 route-specific → 60 route-specific + 20 templates
- Crew loyalty missions: full multi-stage → simplified single-encounter arcs

**Preserved:** All 5 civilizations, all core systems, all 20 stations, full combat, full economy, full reputation, investigation, 6 crew members.

### Tier 2: 70% capacity (significant pressure)

**Cut (everything from Tier 1 plus):**
- Veshan Debt Ledger → standard reputation only for Veshan
- Orryn Telling → standard negotiation for Orryn
- Cultural events per civ: 3 → 1 signature event each
- Investigation beats: 10 → 7 (cut 3 middle beats, collapse the discovery arc)
- Crew members: 6 → 5 (cut the wildcard late-game recruit)
- Trade goods: 20 → 15 (cut 1 exclusive per civ)
- Stations: 20 → 15 (cut 1 per civilization, keep the most distinct)
- Pirate factions: 3 → 2 (merge Ancestor Cult into Phantom Circuit)

**Preserved:** 5 civilizations (thinner), all core systems, combat, economy, reputation, cultural knowledge (simplified), crew as binding constraint (5 instead of 6), investigation (shorter), consequence engine.

### Tier 3: 50% capacity (emergency — ship the core)

**Cut (everything from Tiers 1–2 plus):**
- Civilizations: 5 → 3 (Compact, Keth, Sable Reach — cut Veshan and Orryn entirely)
- Crew members: 5 → 3 (1 Keth, 1 Reach, 1 Compact)
- Stations: 15 → 9 (3 per civilization)
- Lanes: 40 → 15
- Trade goods: 15 → 10
- Cultural knowledge levels: 4 → 2 (Ignorant/Aware)
- Investigation: 7 → 5 beats
- Contract types: 8 → 4 (trade run, bounty, smuggling, investigation)
- Lane encounters: 60 → 30 (templates + a few per-route)
- NPCs: 100 → 40

**Preserved:** The three-layer loop, crew as binding system, combat (ground + ship), trade economy, reputation (3 factions), consequence engine (basic), investigation (short), anti-soft-lock. The game is small but the thesis holds. 3 civilizations with real culture, 3 crew members who each bridge all three layers, a working economy with pressure, combat that matters, and a story about a disgraced pilot. **This is the minimum viable game.**

---

## Red-Flag Dependencies

| Dependency | Risk | Mitigation |
|-----------|------|------------|
| Portlight codebase stability | Medium — Portlight has known wiring gaps (loot not called, armor not passed, surgeon not wired) | Fork from stable branch. Don't depend on unfinished Portlight features. Build combat fresh. |
| Python TUI performance | Low — Portlight runs fine, and this game has similar complexity | Monitor during vertical slice. If performance is an issue, Rust migration is the planned escape. |
| Combat grid rendering in terminal | Medium — Portlight has no grid. This is new TUI territory. | Prototype the 8x8 grid early. If terminal rendering is too limited, consider curses library or blessed/rich for Python. |
| Content volume (200+ text documents) | Medium — this is a lot of writing | Prioritize systemic content (templates, procedural assembly) over hand-authored unique text. The engine should generate 70% of what the player reads. |
| Single developer | High — all design, code, content, and testing from one person with AI assistance | The cut tiers are designed for this. Start at Tier 3 scope. Expand toward full scope as production proves viable. |
| Alien civilization depth | Medium — 4 alien species with distinct cultures is a lot of worldbuilding | Start with the Keth (most developed in design). Build one civ to full depth, then replicate the pattern. |
| Combat balance | Medium — turn-based tactical combat is hard to balance without extensive playtesting | Build the combat balance sim early. Automated testing catches gross imbalances. Playtest catches feel issues. |

---

## Hand-Authored vs Systemic

The Portlight engine's greatest strength is generating lived-in world texture from templates and rules. This game must lean on that hard.

| Content | Hand-Authored | Systemic | Ratio |
|---------|--------------|----------|-------|
| Station profiles (name, civ, flavor, layout) | ✓ | | 100% hand |
| NPC profiles (key NPCs with dialogue trees) | ✓ (~20 key NPCs) | ✓ (~80–100 template NPCs) | 20% hand / 80% systemic |
| NPC greetings and reactions | | ✓ (standing-aware templates) | 100% systemic |
| Trade good definitions | ✓ | | 100% hand |
| Trade prices | | ✓ (base + supply/demand + events) | 100% systemic |
| Lane encounter text | ✓ (~80 route-specific) | ✓ (~20 templates assembled from parts) | 80% hand / 20% systemic |
| Lane narration (daily travel text) | | ✓ (assembled from sector + weather + crew mood + season) | 100% systemic |
| Combat enemy definitions | ✓ | | 100% hand |
| Combat encounter composition | | ✓ (enemy count + type selected by danger rating + faction) | 100% systemic |
| Cultural events | ✓ | | 100% hand |
| Cultural interaction options | ✓ (options) | ✓ (availability gated by knowledge level) | 50/50 |
| Contract definitions (templates) | ✓ | | 100% hand |
| Contract generation (which appear on the board) | | ✓ (weighted by station, rep, world state) | 100% systemic |
| Consequence events | ✓ (event definitions) | ✓ (trigger conditions + timing) | 50/50 |
| Investigation beats | ✓ | | 100% hand |
| Crew profiles + dialogue | ✓ | | 100% hand |
| Crew morale reactions | ✓ (reaction definitions) | ✓ (trigger selection based on player actions) | 50/50 |
| Station flavor text | ✓ (templates per civ × rep state) | ✓ (assembled from templates + consequence state) | 30% hand / 70% systemic |

**The rule:** Hand-author identity (who are the NPCs, what are the cultures, what happens in the story). Systematize texture (what the player reads day-to-day, how NPCs greet you, what's on the board, what happens on the lane). The engine should produce 60–70% of the text the player sees by assembling hand-authored parts.

---

## Build Order

The order in which systems are built, optimized for proving the thesis early.

| Phase | What's Built | What's Proven | Duration (est.) |
|-------|-------------|---------------|-----------------|
| **0. Fork** | Fork Portlight. Reskin terminology (port→station, sea→space, route→lane). Verify existing tests pass with new names. | The codebase is viable as a foundation. | 1 week |
| **1. Combat** | Build turn-based grid combat engine. Ground theater first (8x8, 3 abilities per unit, cover, retreat). Then ship theater (same engine, ship stats, boarding transition). Combat balance sim. | Combat works. Ships are characters. Boarding transitions. | 3–4 weeks |
| **2. Crew binding** | Implement crew-to-ship ability mapping. Crew cultural knowledge grants. Morale affecting combat stats. Injury disabling ship abilities. | Crew is the binding constraint — one crew change affects all three layers. | 2 weeks |
| **3. Vertical slice** | 5 stations, 8 lanes, 5 goods, 2 crew, 3 contract types, basic consequence engine, 2 investigation beats, Captain's View UI. | **The three-layer loop works.** Trade feeds tactics, tactics feed plot, plot feeds trade. The game is real. | 3–4 weeks |
| **4. Cultural depth** | Cultural knowledge system (4 levels). Keth seasonal protocols. Veshan Debt Ledger (if in scope). One cultural event per civ. | Civilizations are gameplay-distinct, not just flavor. | 3–4 weeks |
| **5. Content expansion** | Expand to 20 stations, 40 lanes, 20 goods, 6 crew, full NPC roster, full lane encounters, full contract types. | The world is Portlight-scale and feels alive. | 4–6 weeks |
| **6. Investigation** | All 10 investigation beats, endgame paths, narrative integration. | The story works and responds to player reputation. | 2–3 weeks |
| **7. Polish** | Balance pass, playtest integration, UI polish, bug fixing, anti-soft-lock verification. | The game is shippable. | 3–4 weeks |

**Total estimate: 20–28 weeks from fork to shippable.** This assumes single developer with AI assistance, building on Portlight's codebase, text-only output.

**Critical path:** Phase 0 (fork) → Phase 1 (combat) → Phase 2 (crew binding) → Phase 3 (vertical slice). If the vertical slice doesn't prove the loop, stop and redesign before investing in content. Everything after Phase 3 is content expansion and polish.

---

## The Shippable Version

**The game ships when:**
1. The three-layer loop functions and feels connected in playtesting.
2. All mandatory systems from the list above are implemented and tested.
3. At least Tier 2 content scope is achieved (15 stations, 5 civs, 5 crew, 7 investigation beats).
4. All anti-soft-lock rules are verified.
5. 3 playtesters have completed the game and confirmed: (a) the layers feel connected, (b) crew feels like a multi-system asset, (c) pressure motivates decisions, not repetition.

**The game does NOT need to ship with:** Tauri build, audio, crew portraits, Orryn mobile drifts, full 4-season Keth cycle, 134 NPCs, or perfect balance. These are post-launch improvements.

---

## Unresolved Questions

- Working title. "Star Freight" needs to become something real before the vertical slice is shown to anyone.
- Licensing for the Portlight fork. Portlight is a personal project — no licensing issue, but the fork relationship should be documented.
- Playtest recruitment. Who are the 2–3 playtesters? Should be people who play JRPGs and/or trading games, not just friends.
- Release platform. itch.io? GitHub release? PyPI package? If Python CLI, distribution is pip install or standalone binary (PyInstaller).
- Price. Free? Paid? This affects scope expectations.

## Contradictions Discovered

- "Start with Python fork" vs "Rust TUI is the proven stack for games" — the Python fork is faster but creates a rewrite obligation if the game succeeds. The mitigation: design the combat engine with clean interfaces so the Rust rewrite is a port, not a redesign.
- "Single developer" vs "200+ content documents" — even with systemic generation, the hand-authored content is substantial. The build order front-loads systems and defers content. If content becomes the bottleneck, Tier 2 cuts reduce it to manageable scope.
- "20–28 weeks" vs "this is a side project" — if this runs alongside other active projects (Saint's Mile, Portlight, StudioFlow, etc.), the timeline stretches. The phased build order means each phase produces a playable result — the project can pause between phases without losing progress.

## What Must Be Proven Next

- **The proofs.** The spine is complete. Before any code:
  1. Golden Path Proof — a 30-minute play session, fully written out, showing the three-layer loop in action.
  2. Encounter Proof — one ground combat and one ship combat, turn by turn on the grid, showing ships-as-characters.
  3. Economy Proof — 3 trade runs with exact numbers, showing margins, floor costs, and how reputation/knowledge affect profitability.
- Then: fork Portlight and build Phase 0.
