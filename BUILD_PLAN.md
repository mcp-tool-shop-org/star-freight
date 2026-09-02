# Build Plan — Star Freight

> Status 2026-09-02. Python CLI/TUI is the active build. Grounded / UE5 2.5D is deferred.

---

## Remaining (in order)

1. **TUI combat** — travel currently auto-resolves overlay grid combat. Next is a real grid combat screen, then aftermath.
2. **Later strip** — melee/naval/`world/ports` stay in tree for ancestor tests. Delete when `new_portlight()` is gone.

Grounded / UE5 2.5D is deferred.

Do not invent new system truth during these steps. Express the overlay that is already proved.

---

## Completed

### Phase 0: Fork Truth

- [x] Create repo (mcp-tool-shop-org/star-freight)
- [x] Copy Portlight source, tests, world data
- [x] Update pyproject.toml for Star Freight
- [x] Write FORK_MAP.md
- [x] Write ACCEPTANCE_CRITERIA.md
- [x] Write STATE_MODEL.md
- [x] Inherited tests pass
- [ ] Strip removed modules (printandplay kept as Star Freight board game; melee/naval/ports still in tree) — **later strip; live path no longer loads them**

### Phase 1: Crew Binding Spine — COMPLETE

Crew members change trade access, combat abilities, and narrative options.

### Phase 2: Grid Combat Engine — COMPLETE

8x6 grid, ships-as-characters, victory/loss/retreat write campaign state.

### Phase 3: Cultural Knowledge System — COMPLETE

Keth seasons, Veshan honor/debt, knowledge gates on station options.

### Phase 4: Investigation System — COMPLETE

Fragment journal, multi-path threads, crew interpretation.

### Phase 5: Content Rewrite — OVERLAY COMPLETE, ANCESTOR NOT STRIPPED

Star Freight content lives in `content/star_freight.py` (8 stations, 14 lanes, 18 goods, 5 crew). Live `GameSession.new()` starts overlay campaign state. `new_portlight()` keeps ancestor tests working.

### Phase 6: Vertical Slice — COMPLETE

Golden Path, Encounter, and Economy proofs pass on the overlay.

### Phase 7A–7C: Expansion packs — COMPLETE

Working Lives. Houses, Audits, and Seizures. Shortages, Sanctions, and Convoys.

### Phase 8: Captain Paths — COMPLETE

Relief / Gray / Honor diverge. Wave 3 dogfood PASS.

### Phase 9A–9B: TUI audit and Star Freight views — COMPLETE

`sf_views.py` renders overlay state. Live Textual app and CLI drive Star Freight `CampaignState`.

### Dogfood — COMPLETE through Wave 3

Wave 1 WARN (economy killed captains). Wave 2 PASS with P1 items. Wave 3 PASS after P1 tuning (credit ratio 4.78x).

---

## Build Order Law

The remaining work follows the same law as the original plan:

1. **Honesty** — operators and players must know which layer they are in
2. **Fork** — if the live session is still Portlight, the TUI cannot be Star Freight
3. **TUI** — a game the player can actually play on the proved overlay

Never skip ahead. Never build Grounded in this lane.
