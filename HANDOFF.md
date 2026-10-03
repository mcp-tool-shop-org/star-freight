# Handoff — Star Freight TUI combat (2026-09-02)

Continue this, do not restart. Repo is `E:\AI\star-freight`. Package name stays `portlight`. Grounded / UE5 stays deferred. Do not invent factions, goods, AP rules, or stations — express overlay + the four laws.

Previous chat (Cursor): [TUI combat lock](a87cf329-539e-4894-ab2f-616dc88ee7fe)

## Where you are

| | |
|---|---|
| Branch | `feat/tui-grid-combat` (tracks `origin/feat/tui-grid-combat`) |
| Tip | `3ee4de3` feat: live Star Freight overlay with interactive TUI grid combat |
| PR | https://github.com/mcp-tool-shop-org/star-freight/pull/5 — **open, mergeable, not merged** |
| Why unmerged | Branch protection. CI **test (3.11) SUCCESS**. **test (3.12) still IN_PROGRESS** (looked hung ~15+ min). Auto-merge is not enabled on the repo. Do **not** `--admin` unless Mike says so. |
| Local tests | `pytest` — **2264 passed, 12 skipped** (Python 3.14) |
| Origin | `https://github.com/mcp-tool-shop-org/star-freight.git` (this folder is Star Freight, not Portlight) |

First commands:

```
cd E:\AI\star-freight
git checkout feat/tui-grid-combat
git pull
gh pr view 5
gh pr checks 5
```

If 3.12 is green: `gh pr merge 5 --squash --delete-branch` then `git checkout main && git pull`.

Leave [PR #3](https://github.com/mcp-tool-shop-org/star-freight/pull/3) (`chore/gh-actions-node24-third-party`) alone — still open.

## What shipped in 3ee4de3

Live game is the **Star Freight overlay**, not Portlight ocean:

- `GameSession.new()` → `start_campaign` at Meridian Exchange, empty crew, Compact −25, saves `saves/<slot>.sf.json`
- `GameSession.new_portlight()` is the ancestor (tests still use it)
- CLI: `status` / `station` / `market` / `buy` / `sell` / `crew` / `hire` / `routes` / `sail` / `travel` / … on overlay
- TUI dashboard / market / routes already on overlay

**Item 1 of the study-swarm build order is done:** interactive TUI grid combat.

- Travel (`G`) that rolls an encounter calls `begin_combat` and `push_screen(CombatScreen)` — no silent `run_combat`
- Combat verbs: `M` move, `T` attack, `A` then `1–4` abilities, `V` defend, `X` retreat
- Grey ability slots (4): crew name, or `no crew` / `cooldown N` / injured
- Captain bar stays visible; `RichLog` is memory; grid glyphs carry cover
- On end: `finish_combat` writeback + `resolve_transit` + one toast (not a victory-mode inventory)
- `D`/`C`/`R`/`F`/`J` during overlay combat are no-ops (C1). `M`/`T`/`A`/`X` forward from app bindings onto the screen because those keys already mean Market/Station/Advance/parry at app priority
- CLI / playtest still auto-resolve via `run_combat` (uses `begin_combat` + AI loop + `finish_combat`)

## Lock (do not reopen)

`design/STUDY_SWARM_TUI_COMBAT.dispatch.md` — **VERIFIED-WITH-NOTES**. Receipt: `design/STUDY_SWARM_TUI_COMBAT.citation-receipt.json`.

Five locks: **C1** static combat keys · **C2** approach gate (not every intercept is a grid) · **C3** no victory mode · **C4** docked chrome / void palette · **C5** grey labelled ability slots.

Steal Portlight **grammar** (save picker, numbered Harbor, persistent log, footer=engine verbs). Do **not** steal ocean palette, ship ASCII, 13 maritime tabs, stance-triangle, broadside/rake, or tab keys becoming naval verbs.

Canvas (this machine): `C:\Users\mikey\.cursor\projects\e-AI-star-freight\canvases\study-swarm-tui-combat.canvas.tsx`

## Next — study-swarm build order

1. ~~Combat Screen~~ **done**
2. **Approach overlay** on `travel_to` encounter — **this is the next coding item**. Every interdiction should open stakes (who, cargo, hull) then Negotiate / Flee / Fight. Grid only on Fight. Veshan honor / named setpiece cannot skip the grid. Routine archetypes may offer a stakes-previewed “cut through” (that preview *is* the decision). Live TUI currently jumps straight from interdiction notify → `CombatScreen`. CLI can stay auto-resolve until you wire it the same way.
3. Aftermath: captain bar already updates on writeback; replace/tighten the toast to one **contrastive** line (`kept cargo rather than dumping it; hull −400; Thal injured — Communion docking will hurt`). Optional overlay from existing `sf_views.after_action_summary`, Esc to dismiss, never a clean reset.
4. Station Services numbered picker (Harbor analogue); save-slot picker on new/load; Textual `Footer` of **live** keys on every tab. Survive 100×30.
5. Kill leftover Portlight remap in `src/portlight/app/tui/app.py` — still present for ancestor `EncounterScreen` (`f→flee`, `c→close`, `r→rake`, `t→thrust`, `b→broadside`, …). Overlay combat is gated off that path. Finish this when ancestor encounter is no longer reachable from live `starfreight tui`.

## Files to open first

| Path | Why |
|---|---|
| `design/STUDY_SWARM_TUI_COMBAT.dispatch.md` | Architecture lock |
| `design/TUI_SURFACE_SPEC.md` §5 | Combat layout / keys already specified |
| `design/02_SYSTEM_LAWS.md` | Ship is the unit; not every encounter is a fight |
| `src/portlight/app/tui/screens/combat.py` | Live Combat Screen |
| `src/portlight/app/tui/app.py` | App-level key forwarding + leftover ancestor remap |
| `src/portlight/app/tui/screens/routes.py` | `execute_sail_flow` → `begin_combat` + push screen |
| `src/portlight/engine/sf_campaign.py` | `begin_combat` / `finish_combat` / `run_combat` / `travel_to` |
| `src/portlight/engine/grid_combat.py` | 8×6, 3 AP, writeback contract |
| `src/portlight/app/session.py` | `new` = SF, `new_portlight` = ancestor |
| `tests/test_tui_grid_combat.py` | Screen keys, grey slots, no tab escape |
| `tests/test_star_freight_session.py` | Live overlay boot |

## Tests to run after you touch this

```
python -m pytest tests/test_tui_grid_combat.py tests/test_star_freight_session.py tests/test_tui_integration.py tests/test_tui_encounter.py tests/test_vertical_slice.py -q
python -m pytest -q
```

Ancestor TUI encounter tests still use `GameSession.new_portlight()` and `EncounterScreen`. Do not break them while live TUI is overlay.

## Do not

- Invent design truth (no new civs, goods, combat stats, stations)
- Start Grounded or UE5
- Copy Portlight ocean TUI wholesale
- Remap D/C/R/F during overlay combat
- Treat CLI auto-resolve as the TUI path
- Push this overlay to `mcp-tool-shop-org/portlight` — origin is **star-freight**
- Force-merge PR 5 with `--admin` unless asked
- Delete `chore/gh-actions-node24-third-party` (open PR #3)

## Shell cwd trap (Windows / Cursor)

A reused shell can sit in `E:\AI\portlight` while the workspace is `E:\AI\star-freight`. Always `git rev-parse --show-toplevel` before status. Pass `working_directory: E:\AI\star-freight` on every shell call.
