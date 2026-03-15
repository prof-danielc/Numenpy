# Changelog: Numenpy Prototype

All notable changes to this project will be documented in this file.
## [1.7.0] - 2026-03-15
### Added
- **Reproduction & Verification Suite**: Added `tests/test_angelic_behavior.py` to verify trait reinforcement and desire suppression logic.

### Fixed
- **Angelic Predator Behavior**: 
    - Corrected `TRAIT_MAP` reinforcement; hunting villagers now correctly decreases pro-social traits (Gentleness, Compassion).
    - Strengthened behavioral inhibition; high Gentleness now more aggressively suppresses the "hunt" desire.
    - Rebalanced reward structure; natural vegetation is now more "intrinsically" rewarding (2.0) than villager predation (1.0).
### Added
- **Robust Pathfinding & Failure Tracking**: Agents now track failed intentions and apply utility penalties to unreachable goals, preventing infinite "stalling" loops.
- **Targeted Exploration**: Hungry agents now use multi-step pathfinding to reach distant, potentially fertile areas when searching for food.

### Fixed
- **Villager Starvation Regression**: Added a safety floor to the `patience` trait multiplier to ensure hunger drive is never completely suppressed.
- **Refined Success Reporting**: "Success" is now only reported on terminal action completion, preventing random moves from prematurely clearing failure penalties.
- **Planner Target Selection**: The planner now evaluates multiple nearby targets and only commits to reachable ones.

## [1.5.0] - 2026-03-14
### Added
- **Detailed Death Logging**: The journal now distinguishes between "starvation" and "killed by [Creature ID]".
- **Persistent Remains**: Agents killed by violence now leave consumable `remains` resources, ensuring predators have time to feed before the body disappears.
- **Dynamic Prey Sensitivity**: The `hunt` goal now requires visible prey; agents will naturally revert to vegetation if no villagers are spotted.

### Fixed
- **TraitSystem Stability**: Prevented crashes when adding non-numeric traits (like `type`) to agents; randomization now safely ignores strings.
- **Defensive Sidebar Formatting**: Fixed a `ValueError` in the Brain Monitor when attempting to format string traits as floats.
- **Mass Starvation Regression**: Restored the core `eat` instinct that was accidentally deprioritized during predation tuning.
- **Reinforcement Balancing**: Added reward feedback for eating vegetation to prevent "hunting addiction" from causing starvation.

## [1.4.0] - 2026-03-14
### Added
- **Creature Evil Habits**: Creatures can now hunt, kill, and eat villagers.
- **Biological Drives**: Hunger, energy, and social needs drive agent behavior.
- **Predation & Social Fear**: Creatures can develop "evil habits" by hunting villagers, while villagers react to witnessed carnage.
- **Event Journaling**: Every action and life event is recorded for replay and learning, tracking entity life cycles and social consequences.
- **Brain Monitor Upgrades**: Intentions like "hunt" and "flee" now visible in debug overlays.

## [1.3.0] - 2026-03-14
### Added
- **Visual Debugging Mode**: Press `D` to toggle the AI Brain Monitor and Map Overlays.
- **Enhanced Map Overlays**: Visualizes the selected agent's current path (yellow lines), target destination (red circle), and intention (floating labels).
- **Sim Tick Counter**: Added a real-time tick counter to the UI to verify simulation state updates.
- **Mass Spawning**: Increased initial village size to 10 villagers for richer social and resource-sharing simulations.

### Fixed
- **Perception-Belief Sync**: Agents now prune stale resource locations from their memory when they perceive the tile is empty.
- **Sidebar Refresh Fix**: Resolved an issue where sidebar values appeared static; the UI now correctly refreshes every frame.
- **Planner Action Fix**: Corrected a crash-inducing mismatch where the planner generated 'explore' instead of 'move_random'.
- **Robust Debug Unpacking**: Fixed a `ValueError` crash when visualizing complex 3-tuple actions (like belief sharing).

## [1.2.0] - 2026-03-14
### Added
- **Perception-Based Terrain Learning**: Agents now "see" and learn terrain within their full 5-tile perception range, enabling better long-distance pathfinding.
- **Game Controls**: 
  - `ESC` to quickly exit and save the session.
  - `Space` to pause/resume the simulation with a visual overlay.
- **Documentation**: 
  - Comprehensive `README.md` with architecture and usage details.
  - This `changelog.md` file.

### Fixed
- **Infinite Gossip Loop**: Fixed a bug where agents would repeatedly share the same belief. They now correctly track `shared_beliefs`.
- **Exploration Loop**: Resolved an action naming mismatch where the AI generated 'explore' but the logic expected 'move_random'.
- **Safe Spawning**: Agents no longer spawn on water tiles; implemented `find_random_land_tile` for initial placement.
- **Survival Rebalance**: Drastically slowed hunger and energy decay (from ~2s lifespan to ~100s) to make the simulation playable.
- **Resource Balancing**: Reduced food regeneration rate to prevent the world from being flooded with resources.

## [1.1.0] - 2026-03-13
### Added
- **BDI AI Core**: Implemented Belief, Desire, Intention, and Planner systems.
- **Goal-Aware Eligibility Traces**: Added a LearningSystem that supports Pet/Slap feedback with temporal credit assignment.
- **Deterministic Journaling**: Centralized RNG and event logging for session persistence and replay.
- **Reactive Planning**: Agents now detect tool/action failures and immediately re-evaluate their plans.
- **Species Priors**: Introduced unique trait distributions for different agent types (Person vs Creature).

## [1.0.0] - 2026-03-13
### Added
- **Initial Prototype**: Basic grid-based world with heightmaps and water/grass/mountain terrain.
- **IPOS Cycle**: Foundation main loop with Pygame visualization and logic separation.
- **Entity System**: Basic classes for Person and Creature agents.
