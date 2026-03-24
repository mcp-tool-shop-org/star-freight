# Changelog

All notable changes to Star Freight are documented here.

## [1.0.0] - 2026-03-24

### Added
- Complete game engine: crew binding, grid combat, cultural knowledge, investigation
- Campaign integration layer wiring all four system truths
- 3 expansion packs: Working Lives, Houses/Audits/Seizures, Shortages/Sanctions/Convoys
- 3 proved captain paths: Relief/Legitimacy, Gray/Document, Honor/Frontier
- 10 TUI view functions rendering from campaign state
- Star Freight TUI surface (StarFreightApp) with void palette
- Captain pressure bar (persistent header)
- Maritime term guard CI test (12 assertions)
- Dogfood system: 12-scenario matrix, 3 waves completed
- P1 economy tuning: credit ratio 4.78x (target 3-5x)
- Fear classifier: 3/3 distinct captain fears
- Scenario override system: danger_multiplier, initial_state support
- README in 8 languages, HANDBOOK as operating manual

### Changed
- TUI cutover from Portlight (maritime) to Star Freight (space)
- App class: PortlightApp -> StarFreightApp
- Theme: ocean palette -> void palette
- Currency: silver -> credits (₡)
- Navigation: 12 maritime tabs -> 8 Star Freight tabs
- Station services: "shipyard" -> "drydock"

### Fixed
- Scenario overrides now applied before simulation (not after)
- simulate_run respects starting station from initial_state
- Honor escalation stress now actually stresses (was mislabeled baseline)

## [0.1.1-dogfood] - 2026-03-24

### Fixed
- P1 tuning confirmed under corrected scenario infrastructure
- Wave 3: 8/8 pass criteria met

## [0.1.0-dogfood] - 2026-03-23

### Added
- Initial dogfood release
- GDOS game design framework
- All four system truth modules
- Wave 1 and Wave 2 dogfood runs
