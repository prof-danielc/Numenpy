# Numenpy: BDI-Based God Game Prototype

Numenpy is a research-oriented simulation prototype inspired by games like *Black & White*. It features a modular BDI (Belief, Desire, Intention) AI architecture, a grid-based world with heightmaps, and a reinforcement learning system that allows you to train creatures through interaction.

## 🌟 Key Features

- **BDI AI Architecture**: All agents (Villagers, Creatures) use a unified cognitive core including Beliefs, Desires, Intentions, Planning, and Learning.
- **Interactive Training**: Slap or Pet your creature to influence its behavior using Goal-Aware Eligibility Traces for temporal credit assignment.
- **Dynamic Terrain**: A grid-based hex-like world with elevation, water, and mountains that affect movement and planning.
- **Biological Simulation**: Agents have internal drives (Hunger, Social, Boredom) that decay over time and drive their decision-making.
<<<<<<< Updated upstream
=======
- **Detailed Death Logging**: The journal records specific death causes (starvation vs. violence) and tracks "carnage" and "remains" for predators.
- **Robust Pathfinding & Exploration**: Agents detect unreachable goals, penalize failing intentions, and use targeted multi-step exploration to find resources efficiently in sparse environments.
>>>>>>> Stashed changes
- **Deterministic Replay**: The Global Event Journal records every logical event, enabling session persistence and reproducible debugging.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Pygame

```bash
pip install pygame
```

### Running the Simulation
Execute the main script to start the world:
```bash
python main.py
```

### Controls
- **Mouse Click**: Select an agent to view their status/AI state.
- **Space**: Toggle Pause/Resume.
- **ESC**: Exit and save the session log.
- **S Key**: Slap the selected creature (Punishment).
- **P Key**: Pet the selected creature (Reward).
- **D Key**: Toggle Visual Debugging Mode (AI Brain Monitor & Map Overlays).

## 🏗️ Architecture

The project follows a strict **IPOS (Input-Processing-Output-Storage)** cycle with clear separation between simulation logic and presentation:

- `world.py`: Terrain generation, resource management, and heightmaps.
- `logic.py`: Core simulation loop and physical action execution.
- `entities.py`: Agent definitions (Person, Creature).
- `video.py`: Pygame-based rendering and visualization.
- `journal.py`: Global event logging and session persistence.
- `ai/`:
  - `ai_core.py`: The `AgentAI` container.
  - `ai_systems.py`: Implementation of Belief, Drive, Trait, Desire, Intention, and Planner systems.
  - `learning.py`: Goal-Aware Eligibility Traces and the behavior matrix.

## 🧪 Testing

We use a suite of phase-based tests to verify each component of the simulation:

```bash
# Run social interaction tests
python tests/test_phase13_social.py

# Verify terrain spawning
python tests/verify_spawn.py

# Check logic/graphics separation
python tests/verify_separation.py
```

## 📜 License
This project is for research and educational purposes.
