# Wave 1 Synthesis Verdict — Star Freight v0.1.0-dogfood

> 12 runs. No patches mid-wave. No reinterpretation.
> The question: Did the matrix reveal a real product, or a clever prototype?

---

## Wave Summary

All 12 scenarios executed successfully. No crashes. No stuck states. All runs completed their target day counts. The simulation harness worked as designed.

**Answer: Real product with calibration needed.** The architecture holds. The divergence is real. The economy is broken.

---

## 1. What Held

### Route divergence: STRONG PASS
Station divergence: **1.00** (perfect). Lane divergence: **1.00** (perfect). All three baseline captains visited completely different dominant stations and used completely different dominant lanes.

| Path | Dominant Stations | Dominant Lanes |
|---|---|---|
| Relief | Communion Relay, Mourning Quay, Meridian Exchange | meridian_communion, pilgrims_ribbon |
| Gray | Meridian Exchange, Registry Spindle, Grand Drift | communion_drift, meridian_drift, white_corridor |
| Honor | Grand Drift, Communion Relay, Drashan Citadel | drashan_ironjaw, meridian_drashan |

This is the strongest signal in the wave. The three captains genuinely live in different parts of the map.

### Captain identity divergence: PASS
3/3 unique identities. The simulation correctly labels Relief, Gray, and Honor as structurally different captains with different descriptions.

### Combat posture divergence: PASS
Gray retreats from every fight (4/4 retreats). Honor stands and fights (0 retreats). Relief encounters less combat overall (2 fights vs 4). The combat strategy profiles create genuinely different tactical lives.

### Trade goods divergence: PASS
Gray trades 5 varieties. Relief and Honor trade 2 each. Gray is the most commercially active captain. This matches the design intent — Gray works the margins.

### Crew composition divergence: PASS
Each path uses different crew, opening different cultural doors. Relief has Keth access (+3 Keth rep gain). Gray has Compact document depth. Honor has Veshan house access. The crew binding spine is working.

### Investigation emergence: PARTIAL PASS
8 of 12 runs discovered investigation fragments through station sources. The system works. But all fragments came from a single source type (station). See "What Bent" below.

---

## 2. What Bent

### Economy: CRITICAL — All captains go negative
Every single run ended with negative credits. Every one. The 90-day baselines end at -1100 to -1200 credits. The 60-day stress runs end at -630 to -720. Even the 30-day TUI runs end at -290 to -340.

**Diagnosis:** The economy is too punishing. Docking fees + crew pay + fuel costs outpace trade income. The monthly crew cost (55-75 per crew x 2 = 110-150/month) combined with docking fees (10-30 per stop) and fuel (10-25/day at stations) creates a burn rate the trade engine can't overcome at current margins.

**This is the #1 finding of Wave 1.** The game's pressure is not "tight but survivable." It's a slow bleed to death. That makes the economy non-functional for real play.

**Severity:** BREAKS. Not a tuning issue — the fundamental income/expense ratio needs recalibration.

### Fear convergence: WARN
Only 2/3 unique fears. Relief and Honor both fear "being stuck in someone else's queue." Gray fears "direct confrontation." The fear detection is too coarse — it's based on delay counts, which are similar across runs because the simulation's travel loop generates similar delay patterns.

**Diagnosis:** The fear classifier needs more dimensions. Relief should fear undercapacity, Honor should fear escalation, Gray should fear exposure. The current classifier only checks delays, retreats, injuries, and pay misses.

### Pressure homogeneity: WARN
All stress runs report "time and access" as main pressure. All recovery runs report the same. The pressure classifier is too narrow — it doesn't distinguish between shortage-driven time pressure (Relief) and seizure-driven time pressure (Gray) and escalation-driven time pressure (Honor).

### Investigation source monotony: WARN
All investigation fragments came from station sources only. Trade-triggered investigation (medical supplies at Keth) and combat-triggered investigation (salvage) never fired. The simulation's trade and combat flows don't hit the exact trigger strings the investigation system expects.

**Diagnosis:** The trigger matching is too brittle. `trade_medical_at_keth` requires exact cargo + exact station civilization match. The simulation trades goods but doesn't always carry medical supplies to Keth stations at the right moment.

### Reputation stagnation: WARN
Most faction standings barely moved from starting values. Only Relief gained Keth rep (+3) and Gray lost Compact rep (-2 from starting -25 to -27). The reputation system awards +1 per trade, which is too slow given the economic bleed.

---

## 3. What Broke

### The economy
See above. Every captain dies financially. No path is viable at current tuning. This must be fixed before any other dogfood work makes sense.

### Nothing else truly broke
No crashes. No stuck states. No incoherent behavior. No fake divergence. The architecture is sound. The tuning is wrong.

---

## 4. What Gets Tuned Next

These are balance and legibility adjustments only. No new systems.

### P0: Economy recalibration
- **Increase trade margins.** Buying at source (-20%) and selling at demand (+30%) isn't enough when fees eat the spread. Options: wider buy/sell spread, reduce docking fees, reduce fuel costs, or increase contract payouts.
- **Reduce crew pay frequency or amount.** 110-150 credits/month is too high relative to trade income of ~50-100 per round trip.
- **Consider emergency income floor.** Anti-soft-lock needs to kick in before credits go deeply negative.

### P1: Fear and pressure classifiers
- Add more dimensions to fear classification: cargo-at-risk for Gray, standing-volatility for Honor, delivery-failure for Relief.
- Distinguish shortage pressure from seizure pressure from escalation pressure.

### P2: Investigation trigger broadening
- Relax trigger matching. Instead of requiring exact `trade_medical_at_keth`, match on cargo type + station civilization.
- Add trade-triggered and combat-triggered investigation to the simulation loop more reliably.

### P3: Reputation velocity
- Increase rep gain per trade from +1 to +2 or +3.
- Add rep gain from contract completion.
- Cultural interactions should move reputation faster.

---

## 5. What Must Not Change

These are protected truths. No tuning should flatten them.

| Truth | Status | Protection |
|---|---|---|
| **Crew as binding law** | HOLDING | Crew composition drives route, trade access, and combat posture. Do not weaken this. |
| **Combat as campaign event** | HOLDING | Victory/loss/retreat write different state. Gray retreats, Honor fights. Do not homogenize. |
| **Culture as decision grammar** | HOLDING | Keth stations attract Relief. Veshan stations attract Honor. Compact stations attract Gray. Do not merge these. |
| **Plot as life-emergent** | PARTIALLY HOLDING | Investigation fires but only through one source type. Fix the triggers, don't add quest givers. |
| **Different captain lives** | STRONG | 1.00 route divergence. 3/3 unique identities. Different goods, different combat profiles. This is the strongest signal. Do not flatten it. |
| **Pressure without chores** | AT RISK | Economy bleed makes pressure feel like slow death, not interesting decisions. Fix the economy, keep the pressure. |

---

## Per-Scenario Verdict Table

| # | Scenario | Class | Verdict | Key Finding |
|---|---|---|---|---|
| 1 | relief_baseline_90d_s42 | baseline | **WARN** | Route divergence excellent. Economy non-viable (-1144). |
| 2 | gray_baseline_90d_s42 | baseline | **WARN** | Best goods variety (5). All retreats. Economy worst (-1205). |
| 3 | honor_baseline_90d_s42 | baseline | **WARN** | Clear combat identity. Economy non-viable (-1143). |
| 4 | gray_seizure_60d_s17 | stress | **WARN** | 18 delays. Pressure real but economy obscures it. |
| 5 | relief_shortage_60d_s17 | stress | **WARN** | Shortage pressure present. Economy dominates all signals. |
| 6 | honor_escalation_60d_s17 | stress | **WARN** | 3 injuries. Most combat damage. Economy still dominant. |
| 7 | recovery_injured_crew_45d_s99 | recovery | **WARN** | Crew recovered. Economy still bleeds. |
| 8 | recovery_broke_hull_45d_s99 | recovery | **WARN** | Starting broke stays broke. No recovery path visible. |
| 9 | recovery_burned_rep_45d_s99 | recovery | **WARN** | Rep damage persists. Economy compounds the problem. |
| 10 | tui_first_hour_s01 | tui | **PASS** | 3 stations, 2 goods, clean run. |
| 11 | tui_combat_heavy_s01 | tui | **PASS** | 5 stations, 4 fights, no confusion. |
| 12 | tui_investigation_s01 | tui | **PASS** | 4 stations, 5 goods, fragments surfaced. |

---

## Overall Wave 1 Verdict

**The matrix revealed a real product with one critical calibration failure.**

The architecture works. The divergence is genuine. The captain lives are real. The system truths hold. The TUI runs pass cleanly.

But the economy kills every captain. That makes the game unplayable as-is — not because it lacks content, but because the income/expense ratio is fundamentally wrong. No amount of clever play can overcome the current bleed rate.

**Wave 1 result: WARN (economy blocks PASS)**

**Next action: Economy recalibration (P0), then re-run the 3 baseline scenarios to verify the fix before proceeding to Wave 2.**
