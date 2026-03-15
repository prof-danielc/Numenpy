# Feature Specification: Scalable Map System & Camera Navigation (RTS-style)

**Feature Branch**: `004-scalable-map-system`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "Large simulation worlds, Camera System (Zoom/Pan), Map Loading from JSON, Chunked Rendering, Deterministic Replay Integration."

## Clarifications

### Session 2026-03-15

- Q: Should the camera be strictly constrained so the viewport always stays within the map? → A: Strict Clamping: Camera center is constrained so that the viewport edges never exceed map boundaries.
- Q: Should we maintain Top-Left (0,0) or switch to Bottom-Left (0,0)? → A: Top-Left (0,0): Y increases downwards, consistent with existing logic and Pygame standards.
- Q: Should entities scale linearly with the world zoom or have a minimum size? → A: Linear Scaling: Entities scale exactly with the map zoom to maintain accurate visual relationships.
- Q: Should agents treat map edges as hard walls or despawn? → A: Hard Boundaries: Agents cannot move outside the tile grid; pathfinder treats edges as unwalkable.
- Q: Should the camera state (pan/zoom) be recorded in the journal? → A: Non-Deterministic UI State: Camera state is UI-only and MUST NOT be recorded; replays allow free camera exploration.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Large Map Loading (Priority: P1)

The world should support maps much larger than the screen resolution by loading a chunked tilemap from a JSON file.

**Why this priority**: Core requirement for scalability and research reproducibility.

**Independent Test**: Can be tested by loading a 200x200 map and verifying that the `World` object correctly initializes all tiles with their specified types and attributes.

**Acceptance Scenarios**:

1. **Given** a valid `map.json` with a 200x200 grid, **When** the simulation starts, **Then** the world should initialize without crashing and report the correct dimensions.
2. **Given** a map with RLE-compressed tiles, **When** loaded, **Then** it should decompress into the full grid correctly.

---

### User Story 2 - Smooth Camera Navigation (Priority: P1)

The user should be able to pan the camera using arrow keys and zoom in/out using '+' and '-' keys to explore the world.

**Why this priority**: Essential for interacting with and observing large simulation environments.

**Independent Test**: Can be tested by loading a large map and verifying that camera world coordinates update correctly in response to inputs.

**Acceptance Scenarios**:

1. **Given** the simulation is running, **When** the '+' key is pressed, **Then** the `camera.zoom` should increase and the view should scale up.
2. **Given** a zoomed-in view, **When** arrow keys are pressed, **Then** the camera center should shift, and new areas of the map should become visible.

---

### User Story 3 - Viewport-Based Chunked Rendering (Priority: P2)

To maintain performance, only tiles and entities within the current camera viewport should be rendered.

**Why this priority**: Crucial for high performance on very large maps (e.g., 1000x1000).

**Independent Test**: Can be verified by counting the number of blit operations per frame and ensuring it remains proportional to the viewport size, not the map size.

**Acceptance Scenarios**:

1. **Given** a 1000x1000 map, **When** panned, **Then** the frame rate should remain stable and only visible chunks should be processed for rendering.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support arbitrarily large tilemaps divided into fixed-size chunks (e.g., 32x32 tiles).
- **FR-002**: System MUST load maps from JSON files containing a tileset palette, tile data (or RLE stream), and spawn lists.
- **FR-003**: Every tile MUST specify a `type` (grass, sand, rock, water, etc.) which influences movement cost and perception.
- **FR-004**: System MUST implement a `Camera` system that handles world-to-screen and screen-to-world coordinate transforms. World coordinates MUST use Top-Left (0,0) as the origin, with Y increasing downwards.
- **FR-005**: Camera MUST support zooming (0.5x to 4.0x) and panning via keyboard input. Camera center MUST be strictly clamped so the viewport never renders areas outside the map boundaries.
- **FR-006**: The renderer MUST implement view-frustum culling, blitting only visible chunks and entities. Entities MUST scale linearly with the camera zoom level.
- **FR-007**: Map metadata (name, width, height, seed) MUST be recorded in the Global Event Journal upon loading.
- **FR-008**: The `Planner` and `Pathfinder` MUST utilize tile attributes (walkability, cost) for long-range navigation. Agents MUST treat map edges as hard boundaries (unwalkable).
- **FR-009**: System MUST maintain a spatial entity index mapping entities to world chunks; all proximity, perception, and rendering queries MUST use this index rather than global iteration.
- **FR-010**: System MUST provide a Spatial Query API supporting radius and rectangle searches within the chunked structure.
- **FR-011**: All interactive systems (Selection, Slap, Pet, Spawn) MUST convert screen coordinates to world coordinates using the Camera transform before performing entity queries.
- **FR-012**: The `Camera` module MUST be the single authority for coordinate transforms; duplicate implementations in other modules are prohibited.
- **FR-013**: Camera position, zoom, and viewport state MUST NOT be recorded in the simulation journal, ensuring clean separation between simulation state and observer state.
- **FR-014**: The `MapLoader` MUST perform strict schema validation (dimensions, tile IDs, spawn bounds) and ensure deterministic entity spawn ordering.
- **FR-015**: Tile data MUST be stored in a compact, memory-efficient format (e.g., Integer ID grid) rather than object-per-tile.
- **FR-016**: Camera MUST implement smoothed panning and zoom clamping that accounts for viewport half-width to prevent edge artifacts.

### Key Entities

- **MapData**: Metadata (name, seed, dimensions) and the tile/spawn collections.
- **Tile**: Individual grid cell with `id`, `type`, `elevation`, and `attributes`.
- **Chunk**: A logical group of tiles that caches a pre-rendered surface and maintains a list of entities currently within its bounds for spatial indexing.
- **Camera**: Defines the viewport with `x`, `y`, and `zoom` properties.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A 500x500 map loads in under 1 second.
- **SC-002**: Rendering performance (FPS) remains consistent (within 5% variance) when switching from a 40x30 map to a 1000x1000 map.
- **SC-003**: Camera panning and zooming maintain a consistent "physical" speed relative to the map scale.
- **SC-004**: Replay of a session on a custom map produces bit-identical results when given the same seed and map file.
