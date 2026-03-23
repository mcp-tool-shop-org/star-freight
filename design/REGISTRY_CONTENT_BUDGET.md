# Content Budget — Star Freight

> What actually needs to be authored to ship the full designed game. Lower tiers are emergency fallbacks documented in the Cuts Registry — not build targets. **Build toward Full.**

---

## Scope Tiers (Full is the target — others are emergency reference only)

| Tier | Condition | Stations | Lanes | Goods | Crew | NPCs | Civs |
|------|-----------|----------|-------|-------|------|------|------|
| **Slice** | Vertical slice proof | 5 | 8 | 5 | 2 | 10 | 5 (thin) |
| **Tier 3** | 50% capacity emergency | 9 | 15 | 10 | 3 | 40 | 3 |
| **Tier 2** | 70% capacity | 15 | 30 | 15 | 5 | 80 | 5 (thin) |
| **Tier 1** | 90% capacity | 20 | 40 | 18 | 6 | 100 | 5 (standard) |
| **Full** | 100% — the designed game | 20 | 40 | 20 | 7 | 120+ | 5 (deep) |

**Build target: Full scope.** The vertical slice proves the thesis with minimal content. After that, build toward Full. Only drop to a lower tier if the lead developer explicitly authorizes it.

---

## World Content

| Category | Slice | Tier 3 | Tier 2 | Tier 1 | Full | Effort/Unit | Notes |
|----------|-------|--------|--------|--------|------|-------------|-------|
| **Stations** | 5 | 9 | 15 | 20 | 20 | ~2 hrs each (JSON profile + flavor text + market config + NPC placement) | Hand-authored. Each station has: name, civ, description, market goods, danger, docking behavior, 2–5 flavor text variants. |
| **Space lanes** | 8 | 15 | 30 | 40 | 40 | ~30 min each (JSON: origin, dest, distance, danger, terrain, faction) | Hand-authored data, systemic narration. |
| **Trade goods** | 5 | 10 | 15 | 18 | 20 | ~15 min each (JSON: name, base price per station, civ origin, contraband flags) | 4 universal + 3–4 per civilization. |
| **Keth seasonal configs** | 1 season | 2 seasons | 2 seasons | 4 seasons | 4 seasons | ~1 hr per season (trade modifiers, custom changes, access rules, flavor) | 2-season model (harvest/dormancy) is the viable floor. |

**World total at Tier 2:** ~45 hrs hand-authoring. Spread across Phase 5 (content expansion).

---

## Character Content

| Category | Slice | Tier 3 | Tier 2 | Tier 1 | Full | Effort/Unit | Notes |
|----------|-------|--------|--------|--------|------|-------------|-------|
| **Crew members** | 2 | 3 | 5 | 6 | 7 | ~8 hrs each (profile, dialogue tree, 3 abilities, ship skill, values, morale triggers, loyalty events, narrative hooks) | The most expensive per-unit content. Each crew member must demonstrably change the captain's posture across trade, tactics, and plot. |
| **Crew loyalty missions** | 0 | 1 (simple) | 3 (simple) | 6 (simple) | 6 (multi-stage) | ~3 hrs simple, ~8 hrs multi-stage | At Tier 2: single-encounter arcs. Full: multi-stage sequences. |
| **Key NPCs (with dialogue trees)** | 5 | 12 | 20 | 25 | 30 | ~2 hrs each (personality, dialogue tree, standing-aware branches, consequence reactions) | Named characters the player interacts with repeatedly. |
| **Template NPCs (standing-aware)** | 5 | 28 | 60 | 75 | 90+ | ~20 min each (template profile + greeting variants per standing tier) | Generated from templates. Low effort per unit because the Portlight engine handles greeting/behavior variation. |
| **Named pirate captains** | 1 | 3 | 5 | 6 | 8 | ~1.5 hrs each (personality, ship type, combat behavior, consequence reactions, surrender/spare dialogue) | Portlight pattern: named antagonists with memory. |

**Character total at Tier 2:** ~85 hrs. The most labor-intensive category. Crew members alone are 40 hrs.

---

## Encounter Content

| Category | Slice | Tier 3 | Tier 2 | Tier 1 | Full | Effort/Unit | Notes |
|----------|-------|--------|--------|--------|------|-------------|-------|
| **Route-specific lane encounters** | 5 | 20 | 50 | 70 | 85 | ~20 min each (text snippet + choices + consequence tags) | Hand-authored. Per-lane identity. "The Keth Corridor has grain convoys and bioluminescent buoys." |
| **Lane encounter templates** | 5 | 10 | 15 | 20 | 20 | ~30 min each (parameterized: {faction} patrol checks, {faction} distress signals, debris/salvage with {danger} rating) | Systemic assembly from hand-authored parts. High reuse. |
| **Cultural events** | 1 | 3 | 5 | 10 | 15 | ~1.5 hrs each (scripted encounter sequence with choices, knowledge gates, consequence branches) | The Keth gift ritual, the Orryn Telling, the Veshan honor challenge. Core cultural gameplay. |
| **Consequence-triggered events** | 3 | 10 | 20 | 30 | 40 | ~30 min each (trigger condition + text + consequence tags) | "You spared Ratch, so Ironjaw approaches you at the next station." Portlight pattern. |
| **Investigation beats** | 2 | 5 | 7 | 10 | 10 | ~2 hrs each (narrative sequence, discoverable via multiple paths, gates documented) | Hand-authored. The narrative spine. |

**Encounter total at Tier 2:** ~55 hrs. Route encounters are the bulk (17 hrs), but they're small units with high reuse via the systemic engine.

---

## Combat Content

| Category | Slice | Tier 3 | Tier 2 | Tier 1 | Full | Effort/Unit | Notes |
|----------|-------|--------|--------|--------|------|-------------|-------|
| **Ground enemy types** | 3 | 8 | 10 | 13 | 15 | ~1 hr each (stats, behavior pattern, abilities, visual description) | Enough variety for 15–25 hrs of play. Types recombine for encounter variety. |
| **Ship enemy types** | 2 | 5 | 7 | 9 | 10 | ~1 hr each (hull/shield/weapon stats, abilities, behavior pattern, civilization identity) | Each civilization has a distinct ship combat style. |
| **Combat encounter compositions** | 3 | 10 | 20 | 30 | 40 | ~15 min each (which enemies, what terrain, what narrative trigger, what consequences) | Systemic: the engine picks from compositions based on lane danger + faction + consequence state. |
| **Terrain presets (ground)** | 2 | 4 | 6 | 8 | 8 | ~15 min each (8x8 grid layout: cover placement, entry/exit points, thematic description) | Station corridor, cargo bay, planet surface, ship interior, etc. |
| **Terrain presets (space)** | 2 | 3 | 5 | 6 | 6 | ~15 min each (8x8 grid layout: asteroid placement, debris, station proximity) | Open space, asteroid field, debris field, near-station, nebula, corridor. |

**Combat total at Tier 2:** ~30 hrs. Enemy types are the bulk. Terrain presets and compositions are fast.

---

## Contract Content

| Category | Slice | Tier 3 | Tier 2 | Tier 1 | Full | Effort/Unit | Notes |
|----------|-------|--------|--------|--------|------|-------------|-------|
| **Contract types** | 3 | 4 | 6 | 8 | 8 | ~2 hrs each (template definition, payout formula, reputation leans, danger mapping, board generation rules) | Trade run, bounty, smuggling, escort, faction errand, proxy war, salvage, investigation. |
| **Contract variants per type** | 2 | 3 | 4 | 5 | 6 | ~20 min each (specific flavor text, destination, complication, consequence) | Each type has variants so the board doesn't repeat. |
| **Board generation rules** | 1 | 1 | 1 | 1 | 1 | ~4 hrs (weighted selection logic based on station, reputation, world state, consequence engine) | One system. Systemic. Built once. |

**Contract total at Tier 2:** ~20 hrs.

---

## UI Content

| Category | Slice | Tier 3 | Tier 2 | Tier 1 | Full | Effort/Unit | Notes |
|----------|-------|--------|--------|--------|------|-------------|-------|
| **Screen layouts** | 5 | 6 | 7 | 8 | 8 | ~3 hrs each (station, lane, combat ground, combat space, encounter, overlays, crew detail, map) | Core UI. Built in Phase 3. |
| **Captain's View persistent bar** | 1 | 1 | 1 | 1 | 1 | ~4 hrs | The most important single UI element. |
| **Overlay screens** | 1 | 3 | 5 | 6 | 6 | ~2 hrs each (reputation, journal, crew detail, debt ledger, cargo, map) | Layer on top of any screen. |
| **Context help entries** | 5 | 15 | 25 | 35 | 40 | ~15 min each (per-screen help text explaining what the player is looking at) | The `?` key reference system. |

**UI total at Tier 2:** ~35 hrs.

---

## System Code (not content, but budgeted for completeness)

| System | Slice | Tier 2 | Full | Effort | Notes |
|--------|-------|--------|------|--------|-------|
| Fork + reskin | ✓ | ✓ | ✓ | ~1 week | Phase 0. Rename Portlight terminology. |
| Combat engine (grid, turns, abilities) | ✓ | ✓ | ✓ | ~3–4 weeks | Phase 1. The biggest new code. |
| Crew binding (ship abilities, knowledge grants) | ✓ | ✓ | ✓ | ~2 weeks | Phase 2. |
| Cultural knowledge system | — | ✓ | ✓ | ~2 weeks | Phase 4. |
| Veshan Debt Ledger | — | — | ✓ | ~1 week | Deferrable. Standard reputation works without it. |
| Orryn Telling mechanic | — | — | ✓ | ~1 week | Deferrable. Standard negotiation works without it. |
| Orryn mobile drifts | — | — | ✓ | ~1 week | Deferrable. Fixed stations work. |
| Investigation system | basic | ✓ | ✓ | ~2 weeks | Phase 6. Beat discovery + gates + journal. |
| Captain's View UI | ✓ | ✓ | ✓ | ~1 week | Phase 3. |
| Balance harness extensions | ✓ | ✓ | ✓ | ~1 week | Phase 1. Combat sim + economy sim. |

---

## Grand Total by Tier

| Tier | Content Hours | Code Weeks | Total Calendar (est.) |
|------|--------------|------------|----------------------|
| **Slice** | ~40 hrs | ~8 weeks | 10–12 weeks |
| **Tier 3** | ~90 hrs | ~10 weeks | 14–16 weeks |
| **Tier 2** | ~170 hrs | ~14 weeks | 20–24 weeks |
| **Tier 1** | ~230 hrs | ~16 weeks | 24–28 weeks |
| **Full** | ~280 hrs | ~18 weeks | 28–32 weeks |

**At ~10 hrs/week content writing pace** (side project, AI-assisted):
- Tier 2 content: ~17 weeks of writing
- Running parallel with code: ~20–24 weeks total to Tier 2 shippable
- This aligns with the Production Truth estimate of 20–28 weeks

**The content budget is achievable.** The biggest risk is not volume — it's maintaining quality across 170 hrs of writing. The systemic engine (Portlight's template assembly) reduces the effective authoring burden by generating ~60–70% of what the player reads from hand-authored parts. The 170 hrs is the hand-authored floor, not the player-facing output.
