# Tasks: Scalable Map System & Camera Navigation

**Input**: Design documents from `/specs/004-scalable-map-system/`
**Prerequisites**: [plan.md](file:///c:/Users/Daniel/Downloads/numenpy/specs/004-scalable-map-system/plan.md), [spec.md](file:///c:/Users/Daniel/Downloads/numenpy/specs/004-scalable-map-system/spec.md)

**Tests**: Tests are requested in the specification (SC-004, US Independent Tests). Follow TDD for coordinate transforms and loader logic.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Install dependencies (`numpy`, `pydantic`, `orjson`, `pytest`) in [requirements.txt](file:///c:/Users/Daniel/Downloads/numenpy/requirements.txt)
- [x] T002 [P] Create initial files: `src/camera.py`, `src/chunk.py`, `src/map_loader.py`
- [x] T003 [P] Setup test directory structure: `tests/test_camera.py`, `tests/test_map_loader.py`, `tests/test_spatial_index.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for chunks and camera transforms

- [x] T004 Define `MapSpec`, `TileSpec`, and `TilesetPalette` Pydantic schemas in `src/map_loader.py`
- [x] T005 Implement `Camera` class with `world_to_screen`, `screen_to_world` and basic properties in `src/camera.py`
- [x] T006 [P] Implement `Chunk` class with NumPy-backed tile storage and static/dynamic entity sets in `src/chunk.py`
- [x] T007 Implement coordinate round-trip tests in `tests/test_camera.py`

**Checkpoint**: Foundation ready - chunk structure and camera authority are defined.

---

## Phase 3: User Story 1 - Large Map Loading (Priority: P1) 🎯 MVP

**Goal**: Load maps from JSON files with RLE decompression and deterministic spawn ordering

**Independent Test**: Load a custom 100x100 JSON map and verify `world.grid` dimensions and spawn counts.

- [x] T008 [P] [US1] Implement RLE decompression utility in `src/map_loader.py`
- [x] T009 [US1] Implement map loader with orjson and Pydantic validation in `src/map_loader.py`
- [x] T010 [US1] Refactor `GameWorld` in `src/world.py` to use a sparse dictionary of `Chunk` objects instead of a 2D list
- [x] T011 [US1] Implement deterministic spawn sorting by (x, y, type) in `src/map_loader.py`
- [x] T012 [US1] Record map metadata (name, dimensions, seed) in `GlobalEventJournal` upon loading in `src/map_loader.py`
- [x] T013 [US1] Write map loading integration tests in `tests/test_map_loader.py`

**Checkpoint**: Large map loading is functional and deterministic.

---

## Phase 4: User Story 2 - Smooth Camera Navigation (Priority: P1)

**Goal**: Panning, zooming, and movement smoothing with boundary clamping

**Independent Test**: Panning to the map edge should stop exactly when the viewport edge hits the map boundary.

- [x] T014 [US2] Implement `target_x/y` and lerp-based smoothing in `src/camera.py`
- [x] T015 [US2] Implement zoom-aware clamping logic in `src/camera.py`
- [x] T016 [US2] Update `main.py` handle_inputs to update `camera.target_x/y` and `camera.zoom`
- [x] T017 [US2] Verify camera smoothing and clamping in `tests/test_camera.py`

**Checkpoint**: Camera feels fluid and is safely contained within map bounds.

---

## Phase 5: User Story 3 - Viewport-Based Chunked Rendering (Priority: P2)

**Goal**: O(k) rendering performance via view-frustum culling and chunk caching

**Independent Test**: Frame rate should be identical regardless of total map size (e.g., 40x30 vs 1000x1000).

- [x] T018 [US3] Update `GameVideo` in `src/video.py` to use `camera.world_to_screen` for all rendering positions
- [x] T019 [P] [US3] Implement viewport culling in `src/video.py` using `camera.get_visible_chunk_range`
- [x] T020 [US3] Update `GameVideo` to render entities based on their chunk-relative positions or frustum check
- [x] T021 [US3] Implement debug overlays (chunk boundaries, camera center) in `src/video.py`
- [x] T022 [US3] Verify culling performance on a 100x100 map (60 FPS target)

**Checkpoint**: High-performance rendering is active.

---

## Phase 6: Spatial Entity Index & Interaction

**Purpose**: Professional interaction logic and spatial query API

- [ ] T022 [P] Implement "One Chunk Rule" in `src/entities.py` (agents update their current chunk on movement)
- [x] T023 [US4] Implement `query_radius` and `pick_entity` in `src/world.py` using chunk-level entity sets
- [x] T024 [US4] Update `Agent` in `src/entities.py` to handle chunk registration/unregistration during `move_to`
- [x] T025 [US4] Update `handle_inputs` in `src/main.py` to use `world.pick_entity` for selection
- [x] T026 [US4] Verify selection and neighbor detection logic in a dense entity environment

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Debugging tools and final validation

- [ ] T027 [P] Implement debug overlay ('D') showing chunk boundaries, camera center, and entity occupancy in `src/video.py`
- [ ] T028 Final performance profiling on a 1000x1000 map
- [ ] T029 Run full determinism check (replay sessions on custom maps)

---

## Dependencies & Execution Order

- **Phase 1 & 2** are foundations. T004-T007 BLOCKS US1.
- **US1** is the MVP. It must be completed before interaction logic (Phase 6).
- **US2 & US3** are primarily presentation layers and can theoretically start once the World/Camera foundation is layed.
- **Phase 6** depends on Chunk entity sets (T006).

## Parallel Opportunities

- **T002, T003**: File creation and test setup.
- **T004, T006, T008**: Independent implementation of schemas, containers, and utilities.
- **T021, T025**: Component-specific logic that doesn't block the core engine.

## Implementation Strategy

1. **MVP (Loading)**: Setup → Foundational → US1.
2. **Observation**: Add US2 (Smooth Camera) to explore the loaded map.
3. **Performance**: Add US3 (Chunked Rendering) to scale to 1000x1000.
4. **Interaction**: Finalize spatial querying and pixel-accurate selection.
