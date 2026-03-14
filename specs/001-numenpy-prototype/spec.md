# Feature Specification: Numenpy Prototype

**Feature Branch**: `001-numenpy-prototype`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: User description for Numenpy - a BDI-based god game inspired by Black & White.

## User Scenarios & Testing *(mandatory)*

## Clarifications

### Session 2026-03-13
- Q: Which graphics library should be used for the prototype's visualization and input handling? → A: Pygame
- Q: Should we implement a perfectly "correct" reinforcement learning system, or should we include the "irrationality" modifiers? → A: Configurable (Optimal vs Noisy)
- Q: Should the event journal be persisted to disk permanently, or is it sufficient to keep only a window of recent events in memory? → A: Session Disk Log
- Q: Clarification on module dependency? → A: Game logic MUST be completely separate and independent of graphics, sounds, etc.
- Q: How to handle dynamic action failure? → A: Use a "Verification-at-Runtime" model (inspired by UO emulators). Actions return status; Planner must handle interruptions.
- Q: How to handle temporal credit assignment ambiguity? → A: Use **Goal-Aware Eligibility Traces**. Filter recent actions by current `plan_id`/`intention_id` and apply decay ($\lambda^t$).
- Q: How to ensure deterministic replay with learning? → A: Log **causal inputs** (feedback, RNG seeds, plan IDs) in the journal. Learning must be a deterministic function of state + inputs.

### User Story 1 - Core World and IPOS Cycle (Priority: P1)

As a research developer, I want to run a simple grid-based world simulation using an IPOS (Input-Processing-Output-Storage) cycle so that I have a consistent loop for experimentation.

**Why this priority**: Fundamental loop required for all other systems.
**Independent Test**: Running the game loop for N ticks should result in a stored state that reflects the world's progress.

**Acceptance Scenarios**:
1. **Given** a 128x128 grid, **When** the IPOS cycle runs, **Then** inputs are processed, logic updates, and video renders.
2. **Given** a heightmap matrix, **When** the world is initialized, **Then** elevation and walkability are correctly represented.

---

### User Story 2 - Shared BDI AI Architecture (Priority: P1)

As a researcher, I want all agents to use the same modular AgentAI class (Beliefs, Desires, Intentions, Planner, Learning, Drives, Traits) so that behavioral differences are purely configuration-driven and personality-influenced.

**Why this priority**: Core requirement for the research and experimentation goal.
**Independent Test**: Verify that a "Tiger" species and a "Cow" species exhibit different baseline behaviors (aggression vs compassion) using the same code but different trait weights.

**Acceptance Scenarios**:
1. **Given** an agent with internal drives (Hunger, Boredom), **When** a drive exceeds a threshold, **Then** a corresponding Desire is generated.
2. **Given** an object (e.g., Rock), **When** an agent perceives it, **Then** its BeliefSystem understands its affordances (e.g., Throwable).

---

### User Story 3 - Trainable Creature AI and Temporal Learning (Priority: P2)

As a player, I want to pet or slap the creature to influence its behavior via the LearningSystem and temporal credit assignment so that it learns from sequences of actions.

**Why this priority**: Essential for the gameplay loop and AI training research.
**Independent Test**: Perform a sequence (Move -> Pick up -> Throw) and reward the final action; verify that "Pick up" and "Move" also receive partial reinforcement.

**Acceptance Scenarios**:
1. **Given** a trainable agent, **When** petted after an action, **Then** the `expected_reward` for that behavior in the behavior matrix increases.
2. **Given** a slap event, **When** the LearningSystem processes it, **Then** the recent action buffer (last 5-10 actions) is used for credit assignment.

---

### User Story 4 - Global Event Journal and Debugging (Priority: P2)

As a developer, I want all world changes and AI internal states recorded so that I can debug AI decisions and study personality shifts.

**Why this priority**: Critical for observability and deterministic simulation.
**Independent Test**: Perform actions and verify they appear chronologically in the world journal, including the internal drive values at the time of the action.

**Acceptance Scenarios**:
1. **Given** multiple agent actions, **When** the journal is queried by position, **Then** only local events are returned.
2. **Given** the journal state, **When** a trainable agent perceives, **Then** it updates beliefs based on recent events and potentially imitates player behavior.

---

### Edge Cases

- **Drive Satiation**: How does the agent handle multiple high-intensity drives simultaneously?
- **Ambiguous Reinforcement**: How does the system resolve credit assignment when two different actions were performed in close temporal proximity before feedback?
- **Irrational Overlearning**: How does the system handle "irrational" associations (e.g., throw villager -> reward) without becoming stuck in loops?
- **Action Pre-validation**: Every action (e.g., `PickUp`) MUST validate all prerequisites (distance, object existence) at the exact moment of execution.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement an IPOS (Input, Processing, Output, Storage) main loop using **Pygame** for window management and event polling.
- **FR-011**: **Strict Logic Separation**: The `GameLogic` and `GameWorld` modules MUST be completely independent of graphics, sound, or input-handling libraries (Pygame). They must be portable to other presentation layers.
- **FR-002**: System MUST provide a grid-based `GameWorld` where objects have **Affordances** (e.g., edible, throwable, interactable).
- **FR-003**: System MUST utilize a shared `AgentAI` class for all NPCs, containing Belief, Desire, Intention, Planner, Learning, **Drives**, and **Traits** modules.
- **FR-004**: System MUST implement **Internal Drives**: Hunger, Boredom, Curiosity, and Player Approval.
- **FR-005**: System MUST implement **Personality Traits**: Aggression, Compassion, Curiosity, Playfulness, and Obedience.
- **FR-006**: System MUST implement a **LearningSystem** using a Behavior Matrix and **Goal-Aware Eligibility Traces**:
    - **Context Filtering**: Reward only actions where `event.plan_id == current_plan_id`.
    - **Eligibility Decay**: Apply $\alpha \cdot \lambda^t$ weight to filtered actions.
- **FR-007**: System MUST provide a toggle for **Learning Mode**: "Optimal" (greedy behavior) or "Noisy" (includes research-based irrationality/randomness).
- **FR-008**: System MUST support a `trainable` flag per agent, enabling reinforcement learning updates.
- **FR-009**: System MUST record all world events in an append-only, time-ordered Global Event Journal, which is **persisted to disk as a session log** (JSON/CSV) at the end of each simulation run.
- **FR-010**: System MUST support player interactions: Pet (Reward) and Slap (Punishment).
- **FR-012**: **Action Result Protocol**: Every primitive action MUST return a `Result` (Success, Distant, Missing, etc.).
- **FR-013**: **Planner Interruption**: If a multi-step plan's step returns a failure, the `Planner` MUST abort the plan and re-evaluate beliefs.
- **FR-014**: **Deterministic Learning**: Learning updates MUST be derived solely from prior state and journaled events (including RNG seeds). The journal MUST NOT record internal weight updates.

### Key Entities

- **Agent**: Base class for all NPCs; contains `AgentAI`.
- **AgentAI**: Cognitive core including BeliefSystem, DesireSystem, IntentionSystem, Planner, LearningSystem, DriveSystem, and TraitSystem.
- **AffordanceMap**: Definitions of what actions can be performed on which objects.
- **BehaviorMatrix**: Lookup table for `(Action, Object, Context)` mapping to `ExpectedReward`.
- **EventRecord**: Data structure for journal entries (timestamp, event_type, actor_id, drive_states, **plan_id**, **intention_id**, etc.).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Simulation supports 20+ agents running at interactive speeds (at least 30 TPS).
- **SC-002**: Agents successfully execute a 3-step action sequence (Move -> Action -> Outcome) based on BDI planning.
- **SC-003**: Trainable agents show a statistically significant preference change (>20% weight shift) after 10 feedback cycles.
- **SC-004**: Simulation state can be fully reproduced from a "Causal History" journal (initial state + events + RNG seeds).
