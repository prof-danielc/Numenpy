import random
import numpy as np
from typing import Dict, Optional, Tuple, List
from src.chunk import Chunk

class GameWorld:
    def __init__(self, seed: int = 1337):
        self.seed = seed
        self.rng = random.Random(seed)
        
        # Sparse dictionary of chunks: (cx, cy) -> Chunk
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        
        # Dimensions (informational, can expand)
        self.width = 0
        self.height = 0
        
        # Global tile definition mapping (populated by MapLoader)
        self.tile_definitions = {}
        
        # Resources: list of (x, y, type) - to be chunked in future
        self.resources: List[Tuple[int, int, str]] = []

    def get_chunk(self, cx: int, cy: int, create: bool = True) -> Chunk:
        if (cx, cy) not in self.chunks and create:
            self.chunks[(cx, cy)] = Chunk(cx, cy)
        return self.chunks.get((cx, cy)) # May return None if create=False

    def get_tile_at(self, wx: int, wy: int) -> int:
        cx, cy = wx // Chunk.CHUNK_SIZE, wy // Chunk.CHUNK_SIZE
        tx, ty = wx % Chunk.CHUNK_SIZE, wy % Chunk.CHUNK_SIZE
        chunk = self.get_chunk(cx, cy, create=False)
        if chunk:
            return chunk.tiles[ty, tx]
        return 0

    def set_tile_at(self, wx: int, wy: int, tile_id: int):
        cx, cy = wx // Chunk.CHUNK_SIZE, wy // Chunk.CHUNK_SIZE
        tx, ty = wx % Chunk.CHUNK_SIZE, wy % Chunk.CHUNK_SIZE
        chunk = self.get_chunk(cx, cy, create=True)
        chunk.set_tile(tx, ty, tile_id)
        
        # Update world bounds
        self.width = max(self.width, wx + 1)
        self.height = max(self.height, wy + 1)

    def is_walkable(self, wx: int, wy: int) -> bool:
        # Bounds check not strictly necessary for inf world, but good for map limits
        if wx < 0 or wy < 0: return False
        
        tile_id = self.get_tile_at(wx, wy)
        tile_spec = self.tile_definitions.get(tile_id)
        if tile_spec:
            return tile_spec.get('walkable', True)
        return True # Default to walkable if unknown

    def find_random_land_tile(self) -> Tuple[int, int]:
        if self.width == 0 or self.height == 0:
            return 0, 0
            
        for _ in range(1000):
            rx = self.rng.randint(0, self.width - 1)
            ry = self.rng.randint(0, self.height - 1)
            if self.is_walkable(rx, ry):
                return rx, ry
        return 0, 0

    def query_radius(self, wx: float, wy: float, radius: float) -> List:
        """
        Efficiently find all entities within radius using chunked indexing.
        """
        CS = Chunk.CHUNK_SIZE
        min_cx = int((wx - radius) // CS)
        max_cx = int((wx + radius) // CS)
        min_cy = int((wy - radius) // CS)
        max_cy = int((wy + radius) // CS)
        
        results = []
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                chunk = self.get_chunk(cx, cy, create=False)
                if chunk:
                    for entity in chunk.entities:
                        # Euclidean distance check
                        dist_sq = (entity.x - wx)**2 + (entity.y - wy)**2
                        if dist_sq <= radius**2:
                            results.append(entity)
        return results

    def query_rect(self, x1, y1, x2, y2) -> List:
        """
        Find resources within the specified rectangle.
        Currently iterates over all global resources. 
        TODO: Spatial indexing for resources too.
        """
        results = []
        for rx, ry, rtype in self.resources:
            if x1 <= rx <= x2 and y1 <= ry <= y2:
                results.append((rx, ry, rtype))
        return results

    def pick_entity(self, wx: float, wy: float, radius: float = 0.8):
        """
        Find the single closest entity to the world coordinate.
        """
        nearby = self.query_radius(wx, wy, radius)
        if not nearby:
            return None
            
        # Return closest
        return min(nearby, key=lambda e: (e.x - wx)**2 + (e.y - wy)**2)

    def get_terrain_nearby(self, wx, wy, radius=2):
        # Returns list of (nx, ny, type, elev)
        results = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = int(wx + dx), int(wy + dy)
                # Note: We use max(self.width, wx+radius) style bounds if needed
                # For now, stay within current known bounds
                if 0 <= nx < (self.width or 1000) and 0 <= ny < (self.height or 1000):
                    tile_id = self.get_tile_at(nx, ny)
                    spec = self.tile_definitions.get(tile_id)
                    ttype = spec.get('type', 'grass') if spec else 'grass'
                    results.append((nx, ny, ttype, 0.0))
        return results

    def get_elevation(self, wx: int, wy: int) -> float:
        return 0.0 # Standardized to flat world for US4

    def get_neighbors(self, wx: int, wy: int) -> List[Tuple[int, int]]:
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = int(wx + dx), int(wy + dy)
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def regenerate_resources(self, chance: float = 0.0001):
        if self.width == 0 or self.height == 0:
            return
            
        if self.rng.random() < chance:
            rx, ry = self.find_random_land_tile()
            self.resources.append((rx, ry, "food"))
