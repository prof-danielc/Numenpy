# Changelog: Numenpy Prototype

All notable changes to this project will be documented in this file.

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
