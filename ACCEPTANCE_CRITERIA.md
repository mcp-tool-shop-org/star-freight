# Acceptance Criteria — Star Freight

> Derived directly from the 3 GDOS Proof Artifacts.
> These are not vague goals — they are explicit pass/fail conditions.
> The vertical slice ships when all three pass.

---

## Proof 1: Golden Path

**Tests:** The game feels like one captain's life, not three stacked systems.

### Pass conditions:

1. **Continuous session:** A 15–30 minute play session flows through trade, combat, culture, and narrative without hard mode switches or menu-wall transitions.

2. **Pressure creates movement:** The player takes a contract not because it's the "next quest" but because crew pay is due, ship needs fuel, or a debt is closing in.

3. **Trade feeds tactics:** A trade decision (accepting a risky route, carrying contraband, docking at a hostile station) directly creates or modifies a combat encounter.

4. **Tactics feed plot:** A combat outcome (victory, loss, retreat) changes reputation, opens or closes a narrative lead, or shifts faction standing.

5. **Plot feeds trade:** An investigation lead or narrative event changes which stations are safe, which goods are valuable, or which contacts are available.

6. **Crew matters:** At least one moment where having a specific crew member changes available options (trade access, combat ability, cultural knowledge, or narrative lead).

7. **State change:** The player ends the session in a measurably different campaign state: different credits, reputation, crew condition, knowledge, obligations, or investigation progress.

### Fail conditions:

- Any system feels decorative (can be ignored without consequence)
- Combat can be avoided entirely with no tradeoff
- Trade is just "buy low, sell high" disconnected from narrative
- Plot feels like a separate quest log
- Crew members are interchangeable stat buffs

---

## Proof 2: Encounter

**Tests:** Combat is a campaign event, not a detached tactics minigame.

### Pass conditions:

1. **Causal origin:** The encounter exists because of a trade decision, faction standing, bounty status, contract obligation, or investigation pursuit — not random spawn.

2. **Crew binding active:** At least one tactical option exists only because a specific crew member is present, and at least one option is unavailable because a crew member is absent or injured.

3. **Cultural context:** Cultural knowledge affects at least one of: whether combat starts, deployment setup, available surrender terms, reinforcement likelihood, salvage legality, or reputation consequences.

4. **Three valid outcomes:** Victory, loss, and retreat all produce distinct and interesting campaign state changes.

   - **Victory:** Not just "credits and loot." Reputation shift, faction standing change, potential crew injury, investigation lead, or new obligation.
   - **Loss:** Not "reload." Cargo seized, crew injured, ship damaged, forced to a specific station, reputation hit, debt incurred.
   - **Retreat:** Not "free escape." Fuel/supply cost, reputation as coward, contract failure, route now dangerous, crew morale hit.

5. **Compact resolution:** 5–8 turns. If it takes longer, the design is wrong.

6. **Aftermath feeds loop:** After the encounter, the player's next trade/route/contract decision is materially different than it would have been before the fight.

### Fail conditions:

- Combat feels like a random interruption
- Crew members don't change tactical options
- All three outcomes feel the same (just different numbers)
- The player can ignore encounters without consequence
- Encounter takes more than 10 turns regularly

---

## Proof 3: Economy

**Tests:** Pressure remains meaningful over repeated runs and different captain styles.

### Pass conditions:

1. **Early squeeze:** Hours 1–2 feel tight. The player cannot ignore crew pay, maintenance, or fuel. Contracts are taken out of need, not preference.

2. **First momentum:** By hour 3–4, the player has made enough decisions that their captain has a visible economic identity: a preferred route, a trusted contact, a known culture, a recurring risk.

3. **Viable paths:** Legal (merchant), gray (opportunist), and predatory (pirate) play are all economically sustainable. None is obviously dominant.

4. **Setback recovery:** After a major loss (ship damage, cargo seizure, crew injury), recovery takes 2–4 play sessions, costs something real (dignity, time, leverage, or future options), and creates new decisions rather than dead air.

5. **Late pressure:** By hour 6–8, the player has more capability but also more obligations. Pressure has changed shape (from survival to strategy) but not disappeared.

6. **No chores:** Crew pay and maintenance create route/contract/allegiance decisions, not repetitive busywork. The player feels squeezed into choices, not squeezed into grind.

7. **Anti-soft-lock:** A player who makes bad decisions can always recover. Recovery is ugly, slow, and interesting — never painless, never impossible.

8. **Income curve:** Starting income ~200–400cr/run. By hour 6–8, income ~2000–4000cr/run. Growth comes from better routes, crew capability, cultural access, and reputation — not just bigger numbers.

### Fail conditions:

- Player can grind one safe route forever without pressure
- Gray/pirate play is either broken or obviously dominant
- Setbacks create dead time (nothing to do while recovering)
- Late game has no pressure (player is rich and safe)
- Anti-soft-lock mechanism is invisible or breaks the economy
- Crew pay feels like a tax instead of a decision driver

---

## Verification Protocol

Each proof is verified by playing the game (or running a deterministic test harness) and checking every pass condition. A proof passes when ALL conditions are met. A proof fails if ANY fail condition is triggered.

The vertical slice (Phase 6) ships when all three proofs pass.

No proof is "close enough." Either the loop works or it doesn't.
