# Numenpy: BDI-Based God Game Prototype

Numenpy is a research-oriented simulation prototype inspired by games like *Black & White*. It features a modular BDI (Belief, Desire, Intention) AI architecture, a scalable chunked map system, and a reinforcement learning system that allows you to train creatures through interaction.

## 🌟 Key Features

- **BDI AI Architecture**: All agents (Villagers, Creatures) use a unified cognitive core including Beliefs, Desires, Intentions, Planning, and Learning.
- **Scalable Chunked Map System**: Support for large-scale worlds (1000x1000+) using sparse chunked storage and viewport culling.
- **Smooth RTS Camera**: Smooth panning (arrow keys), zooming (+/-), and boundary clamping.
- **Rich Telemetry (Brain Monitor)**: Real-time sidebar visualization of agent drives, intentions, moral alignment, and cognitive traits.
- **Interactive Training**: Slap or Pet your creature to influence its behavior using Goal-Aware Eligibility Traces for temporal credit assignment.
- **Dynamic Terrain**: A grid-based hex-like world with elevation, water, and mountains that affect movement and planning.
- **Biological Simulation**: Agents have internal drives (Hunger, Social, Boredom) that decay over time and drive their decision-making.
- **Detailed Death Logging**: The journal records specific death causes (starvation vs. violence) and tracks "carnage" and "remains" for predators.
- **Alignment-Driven Behavior**: Traits like Gentleness and Compassion dynamically influence goal utility. High-alignment agents naturally prioritize altruistic actions over violent ones.
- **Ethical Learning System**: The reinforcement system maps intentions to moral development. Rewarding pro-social behavior and punishing antisocial actions builds stable habits.
- **Robust Pathfinding & Exploration**: Agents detect unreachable goals, penalize failing intentions, and use targeted multi-step exploration for resource efficiency.
- **Procedural Island Generation**: Utility for generating island-style maps with varied biomes (sand, grass, trees, mountains).
- **Deterministic Replay**: The Global Event Journal records every logical event, enabling session persistence and reproducible debugging.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Pygame, NumPy, Pydantic, orjson

```bash
pip install pygame numpy pydantic orjson
```

### Running the Simulation
Execute the simulation as a module from the root directory:
```bash
python -m src.main
```

### Controls
- **Arrow Keys**: Pan the camera.
- **+/- Keys**: Zoom in/out.
- **Mouse Click**: Select an agent to monitor their AI state.
- **Space**: Toggle Pause/Resume.
- **D Key**: Toggle Debug Mode (Chunk grid, tile outlines, intention labels).
- **S Key**: Slap the selected creature (Punishment).
- **P Key**: Pet the selected creature (Reward).
- **ESC**: Exit and save session log.

## 🏗️ Architecture

This project follows a strict separation between the simulation logic and the presentation. 

- `src/world.py`: Sparse chunk manager and spatial indexing.
- `src/chunk.py`: Atomic world unit with tile data and entity presence.
- `src/camera.py`: Coordinate transformations and boundary clamping.
- `src/logic.py`: Core simulation loop and physical action execution.
- `src/video.py`: Viewport culling and rich telemetry rendering.
- `src/map_loader.py`: JSON/RLE based map loading.
- `src/map_gen.py`: Procedural island generation utility.
- `ai/`:
  - `ai_core.py`: The `AgentAI` container.
  - `ai_systems.py`: BDI subsystems (Belief, Drive, Desire, Intention, etc.).
  - `learning.py`: Goal-Aware Eligibility Traces and behavior matrices.

## 📜 License
This project is for research and educational purposes.
