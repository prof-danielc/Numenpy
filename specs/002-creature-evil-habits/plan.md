# Implementation Plan: Creature Evil Habits (Evil Habits & Social Fear)

**Branch**: `002-creature-evil-habits`  
**Date**: 2026-03-14  
**Spec**: [spec.md](file:///c:/Users/Daniel/Downloads/numenpy/specs/002-creature-evil-habits/spec.md)

## Summary
Implement a mechanism where Creatures can hunt, kill, and eat Villagers to satiate hunger. This involves new actions, journal-based event perception for social fear (fleeing), and reinforcement learning for habit formation.

## Technical Context
- **Simulation**: `GameLogic` (logic.py) handles action verification and entity lifecycle.
- **AI**: `AgentAI` (ai/ai_systems.py) orchestrates planning and goals.
- **Memory/Learning**: `BeliefSystem` tracks entities; `LearningSystem` (ai/learning.py) manages behavior biases.
- **Events**: `GlobalEventJournal` (journal.py) used for cross-agent perception of death.

## Proposed Changes

### Component: Core Logic (`logic.py`)
#### [MODIFY] [logic.py](file:///c:/Users/Daniel/Downloads/numenpy/logic.py)
- **`kill_villager` Action**:
    - Check proximity (distance <= 1).
    - Set target `energy = 0`.
    - Restricted to `Creature` actor and `Person` target.
- **`eat_villager` Action**:
    - Only valid if target is a "Remains" (dead agent at location).
    - Reduce hunger by 0.7.
    - Record success in journal.
- **`ENTITY_DEATH` Event**:
    - In `update` cleanup, record an `entity_death` event in the journal before removing the agent. Include `location` and `cause` (e.g., "predation" or "hunger").

### Component: AI Systems (`ai/ai_systems.py`)
#### [MODIFY] [ai_systems.py](file:///c:/Users/Daniel/Downloads/numenpy/ai/ai_systems.py)
- **`DesireSystem`**:
    - For `Creature` agents: Add "hunt" goal with utility tied to `hunger` and `aggression`.
    - For `Person` agents: Add "flee" goal if "carnage" is detected (see below).
- **`Planner`**:
    - `goal == "hunt"`:
        - Target the nearest `Person`.
        - Plan: `move` to target -> `kill_villager` -> `eat_villager`.
    - `goal == "flee"`:
        - Plan: Move in opposite direction of the threat or to a random safe distance.
- **Perception Update in `BeliefSystem`**:
    - Agents should scan `journal.get_recent_events()` for `entity_death`.
    - If event location is within perception range, add to `known_carnage`.

### Component: Learning & Behavior (`ai/learning.py`)
#### [MODIFY] [learning.py](file:///c:/Users/Daniel/Downloads/numenpy/ai/learning.py)
- Ensure the behavior matrix includes `kill_villager` and `eat_villager`.
- Calibrate reward weights so hunger satiation from "evil" actions reinforces the behavior.

## Verification Plan

### Automated Tests
- Create `tests/test_predation.py` to:
    1. Spawn a hungry creature and a villager.
    2. Verify creature generates a "hunt" plan.
    3. Verify villager dies and creature hunger decreases.
    4. Verify `entity_death` event in the journal.

### Manual Verification
- Observe simulation with Debug Mode ON ('D').
- Verify the "hunt" goal appears above the creature.
- Verify yellow path lines target the villager.
- Verify villagers flee when witnessing a kill (shown via intention labels).
