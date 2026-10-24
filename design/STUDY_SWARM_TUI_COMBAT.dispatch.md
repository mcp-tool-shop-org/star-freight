<!-- study-swarm · Star Freight TUI + combat · 2026-09-02 -->
# Study-swarm dispatch: Star Freight TUI combat (own thing, not a Portlight reskin)

> Design dispatch. Live `starfreight tui` now boots overlay campaign state, but travel auto-resolves grid combat and the app still remaps tab keys during ancestor encounter screens. This pass locks **how** we express existing system laws on the TUI — it does not invent factions, AP rules, or stations. Five load-bearing questions went to parallel retrieval-grounded agents. Step 3 below contains **only findings the coordinator retrieval-checked this session**. Agent-cited papers that were not re-fetched are listed in Step 4 as dropped, not as architecture.

Synthesizer: Cursor Grok 4.6. Existence oracle: coordinator WebFetch / publisher pages plus prism arXiv/Crossref. Groundedness LLM lens: `mistral-small:24b` via prism (family-different). Status: **VERIFIED-WITH-NOTES**.

## Step 1 — Load-bearing questions

Each has two real designs; an adjacent field has measured it; getting it wrong ships a known-broken default:

- **Q1 — Combat option set.** 4–5 stable verbs + numbered abilities vs Portlight-style 5–7 keys remapped by phase.
- **Q2 — Which fights are a grid.** Every interdiction opens the 8×6 grid vs approach-first (negotiate / flee / fight), with the grid reserved for the fight choice and named setpieces.
- **Q3 — Aftermath.** Dedicated victory inventory vs persistent captain-bar deltas + one contrastive line.
- **Q4 — TUI quality bar.** What makes a Textual game first-class vs a CLI with panels. Portlight grammar is allowed; ocean identity is not.
- **Q5 — Crew binding on the HUD.** Grey labelled slots (`Repair — Thal injured`) vs hiding absent abilities.

## Step 2 — Research dispatch

Five parallel agents (Q1–Q5), retrieve-then-cite, ~550-word cap. Coordinator then ran a **coverage-recovery existence audit** on the union of citations: publisher/arXiv pages fetched this session. Precise figures that live only in an unfetched PDF body were not promoted.

## Step 3 — Research grounding

1. **A central capacity limit averages about four chunks in the focus of attention (typically three to five).** Cowan 2001 (DOI:10.1017/S0140525X01003922). Implication: the combat action row is one chunk-set — keep a handful of verbs, not a second party-management screen.
2. **Hick’s log-RT law does not justify “fewer keys are always faster”; with compatible overlearned keys, cost sits in visual search and decision, not bit-counting.** Liu, Gori, Rioul, Beaudouin-Lafon & Guiard 2020 (DOI:10.1145/3313831.3376878). Implication: freeze verb identity and screen position; do not grow or shuffle the set to “optimize Hick.”
3. **In 27 users, a static split menu was significantly faster than a system-remapped adaptive menu.** Findlater & McGrenere 2004 (DOI:10.1145/985692.985704). Implication: do not remap D/C/R/F to combat verbs when those keys already mean Dashboard/Crew/Routes/Faction.
4. **Roguelike games feature exploration as a critical yet often repetitive element of gameplay; automation is studied to minimize exploration time while balancing coverage with resource cost.** Campbell & Verbrugge 2017 (arXiv:1711.03087). Implication: routine lane contacts may offer a stakes-visible resolve; named honor/setpiece fights stay player-driven.
5. **Players rate games higher when they fail some then succeed; “too easy” is going through the motions with no need to rethink strategy.** Juul 2009 (https://jesperjuul.net/text/fearoffailing/). Implication: a grid that cannot change the next trade/route is a chore even if it is pretty.
6. **People rarely analyze each listed rationale; they form a competence heuristic, and extra explanation can increase overreliance on a wrong suggestion.** Buçinca et al. 2021 (arXiv:2102.09692). Implication: a long after-action inventory will be skimmed as “we won,” not used to plan the next dock.
7. **Most XAI work uses researchers’ intuition of a good explanation; the field should build on how people actually define, generate, select, evaluate, and present explanations.** Miller 2019 (arXiv:1706.07269). Implication: aftermath is a selected explanation, not a complete dump — coordinator-fetched body text of this paper is the contrastive (“why P rather than Q”) foil used in C3.
8. **Amplified “juicy” win-spectacle can impede agency by occluding action–outcome bindings; success-dependent, legible, non-occluding feedback supports updating.** Kao, Ballou, Gerling, Breitsohl & Deterding 2024 (DOI:10.1145/3613904.3642656). Implication: no victory fireworks that hide hull/cargo/crew deltas.
9. **Keep status visible with immediate feedback; recognition over recall; extra decoration competes with needed information.** Nielsen 1994 (https://www.nngroup.com/articles/ten-usability-heuristics/). Implication: docked captain bar + live footer keys; void palette is encoding, not ornament.
10. **A mode is the same input with different results; poorly signaled modes cause slips; use ≥2 redundant mode indicators or avoid modes when the slip is costly.** Laubheimer 2019 (https://www.nngroup.com/articles/modes/). Implication: combat is a Screen with its own footer, not a silent remap of navigation keys.
11. **A Textual app is a retained layout: dock outermost chrome, fill remaining space with `fr`, use Footer to list live bindings.** Textualize 2023 (https://textual.textualize.io/how-to/design-a-layout/). Implication: header = captain bar, footer = current verbs, body = station/grid — not a reprint of CLI stdout.
12. **Cogmind keeps a small patterned verb set, prints keys in the UI, and puts facts on the map rather than only in a scrolling log.** Kyzrati 2014 (https://www.gridsagegames.com/blog/2014/01/f1-help/). Implication: grid glyphs carry cover/range; log is memory, not the only channel.

## Step 4 — Verification gate

**Existence (coordinator retrieval, this session):** findings 1–12 resolved on publisher/arXiv/official-docs pages. Miller’s contrastive foil is in the paper body (fetched); the numbered claim was softened to the abstract so the groundedness lens could score it.

**Form lint:** `study-swarm lint --strict` → 12 findings, all sourced and connected.

**Groundedness LLM lens:** `prism verify --type citations --provider ollama --caller-family anthropic` with `PRISM_DEV=1` (unsigned local receipts; first roleos attempt without a signing key correctly escalated). Seat: `mistral-small:24b`, reasoning-stripped. Synthesizer is Cursor Grok 4.6 (xAI); prism has no xAI family — the studio default excludes Anthropic and lands on Mistral. Family difference holds (xAI ≠ Mistral). Receipt: `design/STUDY_SWARM_TUI_COMBAT.citation-receipt.json` (prism id `prism-01m1gbf4yh1942n8j6t19f6p9y`).

| # | Identifier | Existence | Abstract lens | Notes |
|---|---|---|---|---|
| 1 | DOI:10.1017/S0140525X01003922 | resolved | **supported** | Cowan 2001 |
| 2 | DOI:10.1145/3313831.3376878 | resolved | not_addressed (no Crossref abstract) | Coordinator fetched HAL PDF — keep |
| 3 | DOI:10.1145/985692.985704 | resolved | not_addressed (no Crossref abstract) | Coordinator fetched UBC PDF — keep |
| 4 | arXiv:1711.03087 | resolved | **supported** | Softened once to abstract |
| 5 | URL juul.net | coordinator-fetched | n/a (URL) | Prism cannot resolve URLs |
| 6 | arXiv:2102.09692 | resolved | **supported** | Buçinca et al. 2021 |
| 7 | arXiv:1706.07269 | resolved | **supported** | Softened once to abstract; contrastive foil is body-fetched |
| 8 | DOI:10.1145/3613904.3642656 | resolved | not_addressed (no Crossref abstract) | Coordinator fetched ACM page — keep |
| 9–12 | NN/g, Textual, Cogmind URLs | coordinator-fetched | n/a (URL) | Manual existence |

**Verdict: VERIFIED-WITH-NOTES.** 0 fabricated. 4/7 arXiv-DOI claims supported by the abstract lens; 3 ACM papers exist but Crossref returned no abstract (advisory escalate, never auto-passed — same pattern as the specialists-layer dispatch). Five URL findings are outside prism’s resolver and were coordinator-fetched. Architecture below proceeds on that record, not on a clean `accept`.

**Dropped (agent-cited, not re-fetched — contrastive: you may have expected these; they are not load-bearing here):** Iyengar-Lepper choice timings; Haynes paradox; Chernev meta-analysis; Cockburn menu model; Norman CACM slips (DOI conflict across agents); Adamczyk/Iqbal/Borst interruption suite; Hunicke-Chapman Hamlet; Shields AIIDE; Perdomo thesis; Bansal CHI (cited inside Buçinca, not independently fetched); Simons change-blindness; Tannenbaum-Cerasoli debrief meta; Masicampo unfulfilled goals; Endsley SA local PDF; Friedman/Chen/Harris practitioner posts; Lim-Dey-Avrahami intelligibility; Horvitz mixed-initiative; secondhand ME2 GDC notes; Wiltshire/RPS Into the Breach.

## Step 5 — Architecture lock (express existing truth)

Existing law (do not reopen): crew grants ship abilities; ship is the space-combat unit; 8×6 grid; 5–8 turns; combat writes campaign state; not every encounter is a fight (`02_SYSTEM_LAWS.md`); captain bar is always visible (`05_INTERFACE_FEEL.md`); combat layout already specified (`TUI_SURFACE_SPEC.md` §5).

| Choice | Lock | Findings |
|---|---|---|
| **C1 Combat keys** | Stable verbs on a Combat Screen footer: `M` move, `T` attack, `A` ability (then `1–4`), `V` defend, `X` retreat. **Stop remapping** D/C/R/F while a fight is up. | 1, 2, 3, 10, 12 |
| **C2 Encounter gate** | Every interdiction opens an **approach** surface (stakes: who, cargo, hull). Negotiate / flee / fight. Grid only on fight. Veshan honor / named setpiece cannot skip the grid. A “cut through” resolve is allowed on routine archetypes **only if stakes are previewed** — that preview *is* the decision. | 4, 5, 9 |
| **C3 Aftermath** | No victory mode. Update the captain bar in place. One contrastive toast. Optional overlay using existing `after_action_summary` — dismiss with Esc, never a clean reset. | 6, 7, 8 |
| **C4 TUI chrome** | Docked captain bar + Textual Footer of live keys. Body fills `1fr`. Survive 100×30. Color + glyph. `?` context help. | 9, 11, 12 |
| **C5 Binding HUD** | Ability row already specified: show crew source; unavailable states show why (injured, cooldown, no crew). Empty slots stay labelled, never vanish. | 1, 3, 7 |

Each lock above is justified by findings 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 as mapped in the table. Combat `M` (move) vs tab `M` (market) is allowed because combat is its own Screen — the spec already forbids one key meaning two things *on the same screen*.

### Steal from Portlight (grammar, not identity)

Portlight v2.1 TUI earned: save-slot picker; numbered service picker (Harbor); persistent encounter log; footer verbs that match the engine; toasts for campaign events.

Star Freight takes those **interaction shapes**. Station Services is the harbor analogue. Combat log is a RichLog that survives the fight. New game is a slot picker, not nine ocean captain types.

### Do not steal from Portlight

Ocean palette, ship ASCII, compass rose, 13 maritime tabs, stance-triangle duel, broadside/rake as the combat model, **tab keys silently becoming naval verbs**. That last one is the mode-error factory C1 forbids.

### Build order (after this lock)

1. Combat Screen on overlay `CombatState` (static keys, grey ability slots, log, bar still visible).
2. Approach overlay on `travel_to` encounter (replace silent auto-resolve).
3. Aftermath toast + bar writeback (hook existing campaign writeback).
4. Station Services numbered picker; save slots; Footer chrome on all tabs.
5. Kill leftover Portlight key remap in `tui/app.py`.

Grounded / UE5 stays deferred. Package name stays `portlight` until a later rename.
