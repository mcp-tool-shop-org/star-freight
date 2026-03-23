# TUI Screen Audit — Star Freight

> Every screen judged against: pressure clarity, decision clarity, consequence clarity, continuity.
> Status: PORTLIGHT = still maritime, ADAPT = reusable with changes, BUILD = must create new, CUT = not needed for slice.

---

## Audit Summary

| Screen | Status | Verdict |
|--------|--------|---------|
| Dashboard | PORTLIGHT | **ADAPT** — add crew panel, investigation, time pressure |
| Market | PORTLIGHT | **ADAPT** — add cultural gates, crew access notes |
| Routes | PORTLIGHT | **ADAPT** — add terrain, danger context, contraband risk |
| Cargo | PORTLIGHT | **REUSE** — generic enough |
| Station | PORTLIGHT | **ADAPT** — add cultural rules, investigation leads |
| Contracts | PORTLIGHT | **ADAPT** — add system truth tags |
| Ledger | PORTLIGHT | **REUSE** — trade history is neutral |
| Map | PORTLIGHT | **ADAPT** — replace maritime map with space map |
| Help | PORTLIGHT | **ADAPT** — new keybinds |
| Encounter | PORTLIGHT | **REPLACE** — grid combat replaces 4-phase naval |
| Inventory | PORTLIGHT | **CUT** — replaced by Crew + Ship screens |
| Fleet | PORTLIGHT | **CUT** — not in slice scope |
| Infrastructure | PORTLIGHT | **CUT** — not in slice scope |
| Crew Screen | MISSING | **BUILD** — thesis surface |
| Journal | MISSING | **BUILD** — investigation fragments |
| Grid Combat | MISSING | **BUILD** — tactical combat |
| Faction | MISSING | **BUILD** — reputation with meaning |
| After-Action | MISSING | **BUILD** — writeback made visible |
| Captain's View bar | MISSING | **BUILD** — persistent pressure bar |

---

## Screen-by-Screen Audit

### Dashboard — ADAPT

**Current state:** Maritime captain summary. Silver, provisions, ship hull, sailing progress, ASCII sloop, wave animation.

**What works:** Layout structure (sidebar + content). Tab navigation. Contract display.

**What fails:**
- Pressure: Shows silver but not monthly cost or runway. No crew pay timer.
- Decision: No crew fitness summary. No cultural access summary.
- Consequence: No investigation status. No faction trend.
- Continuity: Maritime terminology. "Provisions" instead of "Fuel." "Silver" instead of "Credits."

**Fix:** Replace sidebar content. Add crew summary panel. Add investigation status widget. Replace maritime terminology. Remove wave animation, add ship condition bar.

---

### Market — ADAPT

**Current state:** Table of goods with buy/sell prices, stock, margin, held cargo.

**What works:** Table layout. Price display. Stock scarcity indicators.

**What fails:**
- Decision: No cultural access gates visible. Player doesn't know WHY a good is available or restricted.
- Consequence: No crew attribution ("Thal provides Keth access for this good").
- Continuity: Good names are Portlight maritime.

**Fix:** Add cultural requirement column. Add "Access: [crew name]" note on gated goods. Replace maritime good names with Star Freight goods. Add contraband warning icon.

---

### Routes — ADAPT

**Current state:** Table of destinations with distance, danger (skulls), ship requirements.

**What works:** Destination list. Distance/time display.

**What fails:**
- Decision: No terrain type shown (affects combat). No contraband risk shown. No cultural notes.
- Consequence: No faction control shown (who patrols this lane).
- Continuity: Maritime region badges. "Leagues" terminology.

**Fix:** Add terrain column. Add contraband risk column. Add controlled-by column. Add cultural note for relevant lanes. Replace maritime terminology.

---

### Cargo — REUSE

**Current state:** Cargo list with quantity, good name, value.

**What works:** Simple, clear.

**What fails:** Minor — no contraband flag visible in cargo list.

**Fix:** Add contraband icon per item. Otherwise reusable.

---

### Station — ADAPT

**Current state:** Port name, region, description, features list, port fee.

**What works:** Basic layout.

**What fails:**
- Decision: No cultural rules visible. No cultural greeting context.
- Consequence: No investigation leads listed. No cultural opportunity/restriction.
- Continuity: "Port" terminology. Maritime features.

**Fix:** Replace with Star Freight station data. Add cultural greeting, restriction, opportunity sections. Add "Investigation leads here" section. Add "Crew that matters here" note.

---

### Contracts — ADAPT

**Current state:** Contract board with reward, deadline, description.

**What works:** Deadline urgency coloring. Layout.

**What fails:**
- Decision: No system truth tags. Player can't see which truths this contract touches.
- Consequence: No cultural knowledge requirement shown. No reputation requirement shown.

**Fix:** Add requirement line (reputation, cultural knowledge). Add risk type label (economic/political/combat). Add "proves:" tag for development reference (can be hidden in release).

---

### Encounter — REPLACE

**Current state:** 4-phase maritime combat (approach → naval → boarding → duel). Rich log, naval combat bars, duel stance selection.

**What fails:** Entirely wrong combat model. Star Freight uses grid combat with ships-as-characters, not phase-based naval/duel.

**Fix:** Replace entirely with Grid Combat Screen per TUI_SURFACE_SPEC. Must show grid, turn order, crew abilities with source, retreat progress.

---

### Crew Screen — BUILD (New)

**Does not exist.** This is the most important missing screen.

**Must show per crew member:**
- Name, role, civilization
- Status (active/injured/recovering) with visibility
- Ship ability (active/degraded/gone)
- Combat abilities (available, locked-by-loyalty)
- Cultural contribution (civ + level + what it unlocks)
- Narrative hooks (active leads)
- Morale bar with departure risk
- Pay rate

**Must show for roster:**
- Slots filled / max
- Total monthly crew cost
- Missing roles and cultural gaps

---

### Journal — BUILD (New)

**Does not exist.** Investigation has no player-facing surface.

**Must show:**
- Active threads with state (dormant/active/advanced/critical/resolved)
- Fragments per thread with grade icon, content, source, day
- Crew interpreter credited
- Delay warning if thread is going cold
- No task lists, no objectives, no quest markers

---

### Grid Combat — BUILD (New)

**Does not exist.** Grid combat engine is proven in tests but has no visual layer.

**Must show:**
- 8x6 grid with position, terrain, combatants
- Whose turn + actions remaining
- Available actions with cost, range, cooldown
- Crew-sourced abilities with crew name
- Unavailable abilities with reason (injured, cooldown, no crew)
- Retreat progress
- After-combat summary with full writeback

---

### Faction — BUILD (New)

**Does not exist.** Reputation is tracked but not displayed in Star Freight terms.

**Must show per faction:**
- Standing + breakpoint label
- Practical meaning (price modifier, access tier)
- Trend direction
- Per-house breakdown for Veshan

---

### After-Action Summary — BUILD (New)

**Does not exist.** Combat and trade results are logged but not summarized.

**Must show after every significant action:**
- Every state delta (credits, hull, cargo, reputation, crew)
- Crew consequences (ability lost/degraded, morale change)
- Investigation fragments discovered
- Consequence tags added

---

## Priority Order

1. **Captain's View persistent bar** — everything else depends on this
2. **Crew Screen** — thesis surface, most important new screen
3. **Grid Combat Screen** — second most visible system
4. **Journal Screen** — investigation needs to be visible
5. **After-Action Summary** — writeback must be felt
6. **Dashboard adaptation** — existing screen, highest traffic
7. **Market/Routes/Station adaptation** — existing screens, point-of-decision
8. **Faction Screen** — reputation context
9. **Theme/terminology pass** — maritime → space
10. **Help/keybind update** — final pass
