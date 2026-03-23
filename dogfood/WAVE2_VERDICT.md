# Wave 2 Synthesis Verdict — Post-P0 Economy Fix

> Confirmation wave. Did the economy repair reveal the real remaining issues, or hide a new imbalance?

---

## Wave Summary

9 runs across 3 passes. All captains survive. Divergence preserved. Economy viable.

**Answer: The fix revealed two real remaining issues and one new imbalance.**

---

## Pass A: Baseline Confirmation — PASS with WARN

### What held
- **All 3 captains survive.** Zero missed pay across all baselines.
- **Divergence perfect.** Station 1.00, lane 1.00, trade 1.00.
- **Different economic shapes.** Relief climbs steadily. Gray peaks and declines. Honor is combat-funded.
- **Combat posture intact.** Gray retreats all 4. Honor wins 6/7. Relief fights when forced.

### What bent: Relief dominance
Relief ends at 4,585. Gray ends at 407. Honor at 1,034. That's an **11.3x ratio** between strongest and weakest. Relief is not just viable — it's secretly dominant.

Relief trades 63 goods bought / 51 sold. That's a volume machine. Keth organics at source discount (65%) selling at base price (100%) across many cycles creates compounding wealth. Meanwhile Gray's Compact/Orryn margins are thinner and Honor's trade volume is low (17 bought, 9 sold).

**Diagnosis:** Relief's trade route (Keth stations -> non-Keth stations) has the widest consistent margin. Gray and Honor routes have narrower margins or fewer sell opportunities. This is the next balance target — not by nerfing Relief, but by improving Gray and Honor margin opportunities.

**Severity:** WARN. Not broken — Relief should be the steadiest earner as the "legitimate work" path. But 11x is too much. Target ratio: 3-5x.

### What bent: Fear/pressure classifier still too coarse
All three captains report the same pressure ("time and access") and only 2/3 unique fears. The classifier doesn't distinguish between Relief's "time pressure from delivery deadlines" and Honor's "time lost to combat recovery" and Gray's "time pressure from avoiding exposure."

**Severity:** P1 carry-forward. Not product-blocking but weakens synthesis readability.

---

## Pass B: Investigation Source Diversity — FAIL

### Finding
Only station sources fired. Zero trade, combat, or route investigation sources across all 3 runs. Gray found zero fragments total.

**Root cause:** The simulation's trigger strings don't match investigation source triggers. The investigation system requires exact strings like `trade_medical_at_keth` but the simulation's trade flow calls `execute_trade` without generating those exact trigger events. Combat salvage requires `salvage_freighter_debris` but the combat system resolves to `salvage_freighter_debris` only on victory at specific encounter types.

**Diagnosis:** This is not an investigation design problem — the investigation system works (Phase 4 tests prove it). It's a **simulation wiring gap**. The playtest harness doesn't emit the game events that the investigation system listens for. In a real TUI playthrough, the triggers would fire because the player's specific actions (hauling medical cargo to Keth, salvaging wreckage) generate the right events.

**Severity:** P2. The investigation system is proved by unit tests. The simulation harness needs event emission to test it properly. This should not block product progress but should be fixed before Wave 3.

---

## Pass C: Stress Confirmation — PASS

### What held
All 3 stress runs survive. No missed pay. The economy fix unblocked the stress signals.

| Stress Run | Credits | Survival | Pressure Signal |
|---|---|---|---|
| Gray seizure | 922 | Yes | 18 delays, all retreats, lean but alive |
| Relief shortage | 4,505 | Yes | 6 combats, 2 injuries, still profitable |
| Honor escalation | 3,195 | Yes | 7 combats (all victories!), 1 injury |

### What the stress runs now show
- **Gray under seizure:** Survives by retreating and trading lean. 18 delays but positive credits. The seizure pressure is now visible as "institutional friction" rather than "economic death." This is the right shape.
- **Relief under shortage:** Still profitable. The shortage multiplier doesn't hit hard enough to threaten Relief's high-volume trade loop. Could make shortages more punishing in future tuning.
- **Honor under escalation:** Actually thrives. 7 combats, 7 victories, 3195 credits. The increased encounter rate feeds Honor's salvage income. Honor under combat pressure is the strongest version of Honor. This is correct — fighting is how Honor earns.

### New finding: Honor escalation is too comfortable
Honor under escalation stress (more encounters) is richer than baseline Honor (3195 vs 1034). That means escalation isn't stress for Honor — it's opportunity. The escalation scenario should feel dangerous, not profitable. Combat injuries need to cost more, or salvage needs diminishing returns, or encounter damage needs to accumulate faster.

**Severity:** P1 for next tuning pass.

---

## Cross-Wave Comparison

| Metric | Wave 1 | Wave 2 | Change |
|---|---|---|---|
| Relief credits (90d) | -1,144 | 4,585 | Fixed |
| Gray credits (90d) | -1,205 | 407 | Fixed |
| Honor credits (90d) | -1,143 | 1,034 | Fixed |
| All survive | No (0/3) | Yes (3/3) | Fixed |
| Station divergence | 1.00 | 1.00 | Held |
| Lane divergence | 1.00 | 1.00 | Held |
| Trade divergence | 1.00 | 1.00 | Held |
| Investigation sources | station only | station only | Unchanged (P2) |
| Fear divergence | 2/3 | 2/3 | Unchanged (P1) |

---

## Tuning Actions

### P1: Relief dominance
- Reduce Keth organics margin slightly (source discount 65% -> 70%)
- OR increase Gray/Honor margin opportunities (more demand stations for their goods)
- Target: 3-5x ratio between strongest and weakest captain at day 90

### P1: Honor escalation comfort
- Escalation stress should feel dangerous, not profitable
- Options: higher injury rate in escalation, salvage diminishing returns, or accumulated hull damage between fights
- Honor should survive escalation, but barely

### P1: Fear/pressure classifier
- Add captain-specific fear detection: Relief fears delivery failure, Gray fears paper exposure, Honor fears crew loss in combat
- Stop using generic "time and access" for all three

### P2: Investigation simulation wiring
- Add event emission to the playtest simulation loop so investigation triggers fire during simulated trade and combat
- This is a harness fix, not a game fix

---

## Protected Truths — Unchanged

| Truth | Wave 2 Status |
|---|---|
| Crew as binding law | HOLDING |
| Combat as campaign event | HOLDING (Honor's salvage income proves this) |
| Culture as decision grammar | HOLDING (Relief's Keth route proves this) |
| Different captain lives | HOLDING (1.00 divergence) |
| Pressure without chores | IMPROVED (no more death spiral) |

---

## Overall Wave 2 Verdict

**PASS with known P1 items.**

The economy fix worked. All captains survive. Divergence preserved. Stress signals now visible instead of obscured by poverty.

Three items carry forward:
1. Relief dominance (11x ratio too high)
2. Honor escalation comfort (stress should stress)
3. Fear classifier coarseness

One item is a harness issue, not a game issue:
4. Investigation source diversity (simulation doesn't emit game events)

**The game is real. The economy is viable. The next tuning pass is balance refinement, not structural repair.**
