# Tasks: Numenpy Prototype

**Feature**: Numenpy Prototype (BDI God Game)
**Implementation Strategy**: Modular approach, IPOS loop first, followed by AI architecture and learning systems.

## Phase 1: Setup

- [x] T001 Create project structure: `ai/`, `specs/`, `tests/`
- [x] T002 [P] Initialize `main.py` with basic IPOS skeleton
- [x] T003 [P] Create `requirements.txt` with base dependencies (pygame if needed)

## Phase 2: Foundational

- [x] T004 Implement `GameWorld` grid data structure in `world.py`
- [x] T005 Implement basic `Agent` base class in `entities.py`
- [x] T006 [P] Create `GlobalEventJournal` skeleton in `journal.py`
- [x] T007 [P] Verify strict logic separation (no Pygame imports in `logic.py`, `world.py`, `ai/`)

## Phase 3: [US1] Core World and IPOS Cycle

**Goal**: A running grid simulation with time-stepping world logic.
**Independent Test**: Simulation runs for 100 ticks and records world state in logs.

- [x] T008 [P] [US1] Implement heightmap and walkability logic in `world.py`
- [x] T009 [US1] Connect `GameLogic.update()` to `main.py` IPOS loop in `logic.py`
- [x] T010 [US1] Implement simple `GameVideo` rendering for the grid in `video.py`
- [x] T011 [US1] Add resource spawning (food, trees) to `world.py`

## Phase 4: [US2] Shared BDI AI Architecture

**Goal**: Agents perceive the world and plan actions (Move -> Pick up -> Eat).
**Independent Test**: A villager agent finds food, moves to it, and consumes it.

- [x] T012 [P] [US2] Implement `BeliefSystem` (perception & affordances) in `ai/ai_systems.py`
- [x] T013 [P] [US2] Implement `DriveSystem` (hunger, boredom, etc.) in `ai/ai_systems.py`
- [x] T014 [P] [US2] Implement `TraitSystem` (personality weights) in `ai/ai_systems.py`
- [x] T015 [P] [US2] Implement `DesireSystem` (weighted goals) in `ai/ai_systems.py`
- [x] T016 [P] [US2] Implement `IntentionSystem` (utility-based selection) in `ai/ai_systems.py`
- [x] T017 [US2] Implement `Planner` (action sequencing) in `ai/ai_systems.py`
- [x] T018 [US2] Integrate all systems into `AgentAI` class in `ai/ai_core.py`
- [x] T019 [US2] Update `Agent.update_ai()` to use `AgentAI` in `entities.py`

## Phase 5: [US3] Trainable Creature AI

**Goal**: Creature learns preference for actions via player feedback and temporal credit assignment.
**Independent Test**: Creature changes action preference in a sequence after 10 pet/slap cycles.

- [x] T020 [US3] Implement `LearningSystem` with `BehaviorMatrix` in `ai/ai_systems.py` (Implemented in `ai/learning.py`)
- [x] T021 [US3] Implement Player Interaction commands (Pet/Slap) in `main.py`
- [x] T022 [US3] Implement **Goal-Aware Eligibility Trace** algorithm (plan-filtering + decay) in `ai/ai_systems.py` (Implemented in `ai/learning.py`)
- [x] T023 [US3] Enable `trainable=True` and species priors for `Creature` in `entities.py`
- [x] T024 [US4] Implement full event-sourcing records (including `plan_id` and `rng_seed`) in `journal.py`

## Phase 6: [US4] Global Event Journal and Debugging

**Goal**: All actions are recorded and observable via debug UI.
**Independent Test**: Replay a move-action sequence from the journal and verify same end position.

- [x] T024 [US4] Implement full event-sourcing records (including `plan_id` and `rng_seed`) in `journal.py`
- [x] T025 [US4] Implement **Deterministic RNG seeding** per agent in `ai/ai_core.py`
- [x] T026 [US4] Add `save_session` and JSON persistence to `journal.py`
- [x] T027 [US4] Implement `test_phase6.py` for Causal Replay verification.
- [x] T027 [US4] Implement debug visualization overlay (beliefs, alignment) in `video.py`
- [x] T028 [US4] Implement **Full Causal Replay** mode in `main.py`

## Phase 7: [US2] Dynamic Failure Handling & Reactive Planning

**Goal**: Agents detect when a plan step fails (e.g., food stolen) and immediately replan.
**Independent Test**: Two agents race for one food; the loser detects the "missing" resource and finds another.

- [x] T029 [US2] Update `GameLogic` to return explicit failure reasons to agents.
- [x] T030 [US2] Implement "Reactive Re-perception" trigger in `AgentAI` on action failure.
- [x] T031 [US2] Add plan-flushing mechanism to `Planner` for aborted sequences.
- [x] T032 [US2] Integration test: `test_phase7_race.py` (Two-agent race scenario).

## Phase 8: [US5] Social AI & Communication

- [x] T033 [US5] Add `social` drive and communication actions.
- [x] T034 [US5] Pass `test_phase8_social.py`.

## Phase 9: [US4] Brain Monitor UI

- [x] T035 [US4] Implement side-panel rendering area in `video.py`.
- [x] T036 [US4] Add `selected_agent` logic and mouse click handling to `main.py`.
- [x] T037 [US4] Render Drive progress bars and Desire utility list.
- [x] T038 [US4] Render Learning System biases for the selected agent.

## Phase 10: [US6] Advanced Terrain & Elevation

**Goal**: Complex terrain (Water, Mountains) affects movement and costs energy.

- [x] T039 [US6] Implement per-tile `elevation` and `terrain_type` in `world.py`.
- [x] T040 [US6] Update `video.py` to render elevation (shading) and terrain types.
- [x] T041 [US6] Update movement cost logic in `logic.py` (hills cost more).
- [x] T042 [US6] Update `Planner` to prefer easy terrain (A* cost).
- [x] T043 [US6] Verification test: `test_phase10_terrain.py`.

## Phase 11: [US7] Species Priors & Individual Variance

**Goal**: Agents have distinct, randomized "personalities" within species limits.

- [x] T044 [US7] Expand `TraitSystem` with `friendliness`, `laziness`, and `bravery`.
- [x] T045 [US7] Implement individual randomization in `Agent` constructor (priors + variance).
- [x] T046 [US7] Update `DesireSystem` to incorporate new traits into goal utility.
- [x] T047 [US7] Render trait values in the Brain Monitor sidebar.
- [x] T048 [US7] Verification: `test_phase11_priors.py`.

## Phase 12: [US8] Hunger & Survival Stakes

**Goal**: Agents must eat to survive; death is permanent.

- [x] T049 [US8] Update `logic.py` to apply energy damage from hunger.
- [x] T050 [US8] Implement agent removal (death) logic in `GameLogic`.
- [x] T051 [US8] Update `world.py` with `regenerate_resources()` loop.
- [x] T052 [US8] Sync `DriveSystem` hunger with `Agent.hunger` in `ai_core.py`.
- [x] T053 [US8] Verification: `test_phase12_survival.py`.

## Phase 13: [US9] Social Knowledge Sharing

**Goal**: Agents exchange information about resource locations.

- [x] T054 [US9] Expand `socialize` effect to trigger belief sharing.
- [x] T055 [US9] Implement `share_belief` action in `GameLogic`.
- [x] T056 [US9] Update `Planner` to generate sharing plans when social drive is high.
- [x] T057 [US9] Add "Last Shared" tracking to `Agent` to avoid spam.
- [x] T058 [US9] Verification: `test_phase13_social.py`.

## Phase 14: Reorganization & Polish

**Goal**: Clean up project root and consolidate tests.

- [x] T059 Organize all `test_*.py` files into `tests/` directory.
- [x] T060 Update test import paths to support the new directory structure.

## Phase 15: Bug Fixes & Polish

**Goal**: Fix immediate issues found by the user.

- [x] T061 [US11] Implement `find_random_land_tile` in `GameWorld`.
- [x] T062 [US11] Update `main.py` to spawn agents on land.
- [x] T063 [US12] Rebalance hunger/energy decay to increase lifespan to ~100s.
- [x] T064 [US12] Drastically reduce food regeneration and increase perception range.

## Phase 16: Game Controls [US13]

**Goal**: Implement basic UI controls.

- [x] T065 [US13] Implement ESC key to exit.
- [x] T066 [US13] Implement Space bar to pause.
- [x] T067 [US13] Fix infinite gossip loop and distance-related sharing bugs.
- [x] T068 [US13] Implement perception-based terrain learning.

## Phase 17: Documentation [US15]

**Goal**: Provide project overview and usage instructions.

- [x] T069 [US15] Create comprehensive `README.md`.
- [x] T070 [US15] Create `changelog.md`.

## Dependencies

1. Phase 1 & 2 (Setup/Foundational) -> Phase 3 [US1]
2. Phase 3 [US1] -> Phase 4 [US2]
3. Phase 4 [US2] -> Phase 5 [US3]
4. Phase 1-5 -> Phase 6 [US4] (observability)
