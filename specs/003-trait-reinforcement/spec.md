# Feature Specification: Trait Reinforcement & Cognitive Alignment

## Overview
This feature introduces a multi-dimensional personality model where creature traits are stored as continuous values in the range `[-1.0, +1.0]`. Player feedback (slaps and pets) will not only influence behavioral biases but also reinforce the underlying cognitive traits, shifting the creature's personality toward "Good" or "Evil" alignments.

## Goals
- Transition `TraitSystem` from `[0, 1]` to `[-1, +1]` range.
- Implement a comprehensive list of Good, Evil, and Neutral traits.
- Link player feedback (slap/pet) to trait modifications.
- Ensure traits influence action utility calculation in the `DesireSystem`.

## Clarifications
### Session 2026-03-14
- **Q1: How should feedback map to the 24+ traits?** → **A: Intention-Specific Feedback**. Feedback affects only traits most relevant to the current Goal (BDI Intention).
- **Q2: Should trait changes be permanent or match habits?** → **A: 5x Slower**. Traits update with `ΔT = (α/5) * reward`.
- **Q3: What happens when a trait hits +/- 1.0?** → **A: Hard Clamp**.

## Trait Model
Traits are stored in the `TraitSystem` within a `[-1.0, +1.0]` range.

### 😇 Good Traits (Positive Range)
Pushed by **Pets** and pro-social actions.
- **Compassion** (vs Cruelty): Increases `help_villager`.
- **Generosity** (vs Greed): Decreases resource hoarding.
- **Empathy**: Increases response to negative events.
- **Obedience** (vs Arrogance): Compliance with player signals.
- **Gentleness** (vs Aggression): Reduces damage actions.
- **Diligence** (vs Laziness): Increases labor tasks.
- **Altruism** (vs Dominance): Prioritizes village goals.
- **Gratitude**: Strengthens reward learning.
- **Patience** (vs Vindictiveness): Reduces retaliation.
- **Temperance**: Reduces impulsive actions.
- **Protectiveness**: Increases `attack_enemy`.
- **Cleanliness**: Increases `clean_village`.

### 😈 Evil Traits (Negative Range)
Pushed by **Slaps** and destructive actions.
- **Aggression**: Tendency to attack.
- **Cruelty**: Enjoyment of harming.
- **Greed**: Hoarding resources.
- **Dominance**: Desire to control.
- **Sadism**: Pleasure from punishment.
- **Deceitfulness**: Increases trickery.
- **Gluttony**: Increases food consumption.
- **Destructiveness**: Enjoyment of breaking things.
- **Arrogance**: Ignores player instruction.
- **Vindictiveness**: Revenge seeking.
- **Neglectfulness**: Ignores villager needs.
- **Corruption**: Tendency to exploit systems.

### 😐 Neutral / Personality Traits
- **Curiosity**: Desire to explore.
- **Playfulness**: Tendency to interact.
- **Fearfulness**: Reaction to slap (reinforcement sensitivity).
- **Boldness**: Willingness to take risks.
- **Sociability**: Desire to interact with agents.
- **Laziness**: Reluctance to work.
- **Focus**: Pursuit of long goals.
- **Adaptability**: Responsiveness to new situations.

## Intention-Specific Feedback Map
| Intention | Positive (Pet) Traits | Negative (Slap) Traits |
|-----------|-----------------------|-------------------------|
| **Hunt** | -Aggression, +Patience | +Cruelty, +Aggression |
| **Socialize** | +Compassion, +Empathy | +Vindictiveness, +Arrogance |
| **Eat** | +Patience, +Obedience | +Greed, +Gluttony |
| **Explore** | +Curiosity, +Focus | +Fearfulness |
| **Work** | +Diligence, +Altruism | +Laziness, +Neglectfulness |

## Technical Requirements
- `TraitSystem` needs to initialize with species-specific priors using the new range.
- `DesireSystem` must map the `[-1, +1]` traits to utility values (e.g., `utility = drive * (trait + 1) / 2` or similar normalization).
- `LearningSystem` should trigger trait updates when `apply_feedback` is called.

## UI/Debugging
- Brain Monitor (sidebar) must display the full list of traits and their new values.
- Alignment summary (Good/Evil/Neutral) based on the average of moral traits.
