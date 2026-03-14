# Feature Specification: Creature Evil Habits

**Feature Branch**: `002-creature-evil-habits`  
**Created**: 2026-03-14  
**Status**: Draft  
**Input**: User description: "The creature must now be able to develop evil habits, like learning it can kill and also eat villagers to satiate hunger."

## Clarifications

### Session 2026-03-14
- Q: How should death be communicated to the system and actors? → A: Use existing `GlobalEventJournal` for entity death events.
- Q: When should villagers flee? → A: Only if they "see" the carnage (perceive a `death` event in the journal occurring within range).
- Q: Notification mechanism? → A: Journal events will enable future sounds/UI; currently discovery is visual.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Satiation through Villainy (Priority: P1)

A hungry creature, unable to find regular food, discovers it can hunt villagers to survive. This establishes the basic mechanics of the "evil habit."

**Why this priority**: Core functionality requested by the user. Without this, the creature cannot "develop" the habit.

**Independent Test**: Can be tested by placing a hungry creature and a villager in a restricted area with no food and verifying the creature attacks, kills, and eats the villager.

**Acceptance Scenarios**:

1. **Given** a creature with hunger drive > 0.7 and no food in its known locations, **When** a villager is within perception range, **Then** the creature may select "kill_villager" as its goal.
2. **Given** a villager has been killed by a creature, **When** the creature performs "eat_villager", **Then** its hunger drive MUST decrease by at least 0.5.

---

### User Story 2 - Habit Formation (Priority: P2)

The creature's internal learning system reinforces the behavior of hunting villagers based on the rewarding nature of satiation.

**Why this priority**: This fulfills the "learning" and "developing habits" part of the requirement.

**Independent Test**: Verify via the Brain Monitor that the "kill_villager" bias in the behavior matrix increases after a successful, unpunished kill/eat cycle.

**Acceptance Scenarios**:

1. **Given** a successful "eat_villager" action, **When** the learning system processes the reward (hunger reduction), **Then** the behavior bias for "kill_villager" MUST increase.

---

### User Story 3 - Social Consequences (Priority: P3)

The player's intervention can suppress the development of evil habits through negative reinforcement (slaps).

**Why this priority**: Balancing mechanic to allow the player to "train" the creature out of evil habits.

**Independent Test**: Slap the creature immediately after it kills a villager and verify the "kill_villager" bias decreases.

**Acceptance Scenarios**:

1. **Given** a creature has just killed a villager, **When** the player slaps the creature, **Then** the temporal credit assignment MUST apply negative feedback to the "kill_villager" action.

---

### Edge Cases

- **What happens when the creature kills a villager but is already full?** (Should it still eat it? Influence on learning?)
- **How does the system handle multiple creatures attacking the same villager?**
- **What happens if a creature is interrupted during the "eat_villager" process?**

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow Creatures to target Villagers with a "kill" action.
- **FR-002**: System MUST allow Creatures to perform "eat_villager" on a killed villager entity.
- **FR-003**: Killing and eating a villager MUST significantly reduce the Creature's "hunger" drive.
- **FR-004**: The LearningSystem MUST support updating the behavior matrix for the "kill_villager" action based on satiation reward vs. player feedback.
- **FR-005**: Villagers MUST be removed from the simulation logic when killed and eaten.
- **FR-006**: System MUST NOT proactively notify the player when a villager is killed; player discovery should be visual.
- **FR-007**: Villagers MUST panic and attempt to flee (move away) ONLY if they perceive a `death` event in the `GlobalEventJournal` or an ongoing attack within their perception range.
- **FR-008**: System MUST record an `entity_death` event in the `GlobalEventJournal` whenever an agent is killed.

### Key Entities

- **Villager (Target)**: Existing Person entity, but now with a "targetable" state for creatures.
- **Remains**: A temporary entity or state of a killed villager that can be "eaten" before being removed from the world.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A hungry creature successfully converts a villager into hunger satiation in 100% of cases where a villager is the only available resource.
- **SC-002**: The behavior matrix bias for "kill_villager" increases by at least 0.05 after one successful unpunished kill/eat cycle.
- **SC-003**: The simulation maintains 60 FPS and stable memory usage even after multiple villager entity removals.
