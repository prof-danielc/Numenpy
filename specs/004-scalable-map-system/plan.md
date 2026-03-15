# Implementation Plan: Scalable Map System & Camera Navigation

**Branch**: `004-scalable-map-system` | **Date**: 2026-03-15 | **Spec**: [spec.md](file:///c:/Users/Daniel/Downloads/numenpy/specs/004-scalable-map-system/spec.md)

## Summary
Refactor the world and rendering systems using a chunked, spatially-indexed architecture inspired by professional RTS engines. This involves introducing a `Camera` authority for coordinate transforms, a chunked world structure for efficient rendering and spatial indexing, and a JSON-based map loading system.

## Technical Context
- **Language/Version**: Python 3.10+
- **Primary Dependencies**: Pygame, NumPy (compact storage), Pydantic (validation), orjson (fast parsing)
- **Storage**: JSON-based tilemaps with RLE compression; internal 2D NumPy array for IDs
- **Testing**: `pytest` for transforms, loader validation, and chunk boundary crossing
- **Target Platform**: Desktop (Pygame)
- **Project Type**: 2D Simulation
- **Performance Goals**: 60 FPS on 1000x1000; <1s map load; O(k) rendering where k=viewport area
- **Constraints**: Maintain deterministic replay compatibility; separate UI camera state from simulation journal
- **Technical constraints**: 32x32 CHUNK_SIZE

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle Separation of Concerns**: Camera state must be strictly decoupled from simulation logic (verified by FR-013)
- **Principle Determinism**: Map seeding and entity spawning must remain reproducible (verified by FR-007).
- **Principle Performance**: Compact memory (NumPy uint8) + O(k) spatial searches.

## Project Structure

### Documentation (this feature)
```text
specs/004-scalable-map-system/
├── plan.md              # This file
├── research.md          # Decision log (NumPy vs Lists, etc.)
├── data-model.md        # Pydantic schemas and Chunk entity structure
├── quickstart.md        # Usage guide
└── tasks.md             # Implementation checklist
```

### Source Code Refactor
```text
src/
├── camera.py            # Authorities for all transforms (Smoothed targets)
├── chunk.py             # [NEW] Container for tiles, entities, and surface cache
├── map_loader.py        # [NEW] Pydantic schemas & orjson/RLE loader
├── world.py             # [MODIFY] Refactored to Chunk manager + NumPy grid
├── video.py             # [MODIFY] View-frustum culling + debug overlays
├── logic.py             # [MODIFY] Transition to Spatial Query API (query_point)
└── entities.py          # [MODIFY] Spatial index registration (one-chunk rule)
```

## Proposed Changes

### Component: Compact Tile Storage & Validation
- Use **NumPy** `uint8` array for the global tile ID grid to minimize memory.
- Use **Pydantic** `MapSpec` to validate JSON maps on load.
- Use **orjson** for high-speed parsing of 1M+ tile files.

### Component: Chunk Module (`chunk.py`)
- Define `CHUNK_SIZE = 32`.
- `Chunk` class: stores sub-grid of tile IDs, cached `pygame.Surface`, `static_entities` (for optimization), and `dynamic_entities` set.
- Implement "dirty" flag for selective surface re-rendering.

### Component: Camera System (`camera.py`)
- Implement `Camera` class with `x`, `y`, `zoom`, `width`, and `height`.
- Provide canonical `world_to_screen` and `screen_to_world` methods.
- Implement clamping logic to keep viewport within map boundaries.
- Separate `camera.x/y` from `camera.target_x/y` for movement smoothing.

### Component: World & Spatial Index (`world.py`)
- Refactor `GameWorld` to manage a grid of `Chunk` objects.
- Implement a spatial entity index (list of entities per chunk).
- Add `query_point`, `query_radius`, and `query_rect` methods.

### Component: Rendering (`video.py`)
- Update `GameVideo` to use the `Camera` transforms.
- Implement viewport culling: only render chunks visible in the camera frame.
- Scale entities and tiles dynamically based on `camera.zoom`.

### Component: Map Loading (`map_loader.py`)
- Create a dedicated utility for parsing map JSON files.
- Support tileset palettes and RLE (Run-Length Encoding) for tile data.

## Verification Plan

### Automated Tests
- `tests/test_camera.py`: Verify coordinate round-tripping (`world -> screen -> world`).
- `tests/test_camera_smoothing.py`: Verify smoothed target convergence.
- `tests/test_map_loader.py`: Verify RLE decompression and grid initialization.
- `tests/test_spatial_index.py`: Verify entity registration and proximity queries.
- `tests/test_chunk_movement.py`: Verify entity updates when crossing boundaries.
- `tests/test_determinism.py`: Verify sorted spawn ordering across different seeds.

### Manual Verification
- **Debug Mode ('D')**: Toggle chunk boundaries, camera center, and entity pick-radii.
- **Stress Test**: Load 1000x1000 map and pan rapidly to verify cache performance.
- **Pixel-Accuracy**: Verify clicks at 0.5x and 4.0x zoom select the correct agent.
