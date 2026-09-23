# star-freight: how it works

Mapped at 2026-09-23 from commit fd07312.

## What this is

8 parts, mostly Python (207 files). Work enters through 5 doors; the busiest is CI, which reaches 2 parts. It publishes to PyPI. People run starfreight.

## What changed since the last map

This is the first map.

## What comes in

1. **CI.** On a pull request touching 7 paths; on a push touching 7 paths; or by hand. Runs tests/.
2. **Deploy site to GitHub Pages.** On a push to main touching 2 paths; or by hand. Runs site/astro.config.mjs and site/src/.
3. **Publish to PyPI.** When a release is published; or by hand. Runs no file this map can see.
4. **Release Binaries.** When a release is published; or by hand. Runs no file this map can see.
5. **starfreight** (a command people run). Runs src/portlight/app/cli.py.

## What happens through CI

1. The workflow runs tests/ in tests.
2. That reaches src (104 files).

## Who reads the results

CI writes nothing this map can see.

## The other doors

**Deploy site to GitHub Pages** runs site/astro.config.mjs and site/src/, and deploys the site.

**Publish to PyPI** runs no file this map can see and publishes to PyPI.

**Release Binaries** runs no file this map can see and creates a GitHub release.

**starfreight** (a command people run) runs src/portlight/app/cli.py.

## What breaks what

- **src** is imported by 1 part (dogfood), and by 1 more only from tests; it sits on the path of 2 doors.

## What tends to change together

- **src/portlight/content/star_freight.py** and **tests/test_star_freight_content.py** changed together in 5 of 7 commits, and the tests part imports the src part.

Confidence is low: fewer than 20 source files reach 10 revisions in the window.

Window: 180 days; a pair counts from 3 shared commits, since 0 source files reach 10 revisions; the floor rises to 10 when 25 do.

## What no test touches

- **dogfood** is imported by no test.

## Written but never read

- **dogfood/wave1_results.json** is written by dogfood/run_wave1.py and read by nothing else in this repository.
- **dogfood/wave2_results.json** is written by dogfood/run_wave2.py and read by nothing else in this repository.
- **dogfood/wave3_results.json** is written by dogfood/run_wave3.py and read by nothing else in this repository.

## Helpers that look duplicated

No two parts export a helper that looks alike.

## Generated, never hand-edited

- **dogfood/wave1_results.json** is written by dogfood/run_wave1.py.
- **dogfood/wave2_results.json** is written by dogfood/run_wave2.py.
- **dogfood/wave3_results.json** is written by dogfood/run_wave3.py.

## Hand-authored

People write .github/, design/, the repository root, site/ and world/; 5 writes with paths built at run time may land here.

## Where to start

.github/workflows/ci.yml → tests/balance/test_captain_parity.py → src/portlight/balance/aggregates.py

Read those in order to follow one pull request end to end.

## What this map cannot see

- 2 import sites could not be resolved.
- 5 writes and 2 reads use paths built at run time and are not named here.
- Statistics confidence is low: fewer than 20 source files reach 10 revisions in the window.

Regenerate with `npx --yes @dogfood-lab/atlas map`.
