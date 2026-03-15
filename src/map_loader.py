import orjson
import numpy as np
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from src.world import GameWorld
from src.chunk import Chunk

class TileSpec(BaseModel):
    id: int
    type: str
    walkable: bool = True
    cost: float = 1.0
    color: Optional[List[int]] = None # [R, G, B]

class TilesetPalette(BaseModel):
    tiles: List[TileSpec]

class MapSpec(BaseModel):
    name: str
    width: int
    height: int
    seed: int
    tileset: TilesetPalette
    layers: Dict[str, List[int]] # Maps layer names to RLE streams [id, count, ...]
    spawns: List[Dict] = [] # list of {type, x, y, id}

def rle_decompress(stream: List[int]) -> List[int]:
    """
    Standard RTS RLE: [id1, count1, id2, count2, ...]
    """
    result = []
    for i in range(0, len(stream), 2):
        tile_id = stream[i]
        count = stream[i+1]
        result.extend([tile_id] * count)
    return result

class MapLoader:
    @staticmethod
    def load(filepath: str, world: GameWorld, journal=None):
        with open(filepath, 'rb') as f:
            data = orjson.loads(f.read())
            
        spec = MapSpec(**data)
        
        # 1. Initialize World metadata
        world.width = spec.width
        world.height = spec.height
        world.seed = spec.seed
        world.tile_definitions = {t.id: t.model_dump() for t in spec.tileset.tiles}
        
        # 2. Decompress and Populate Tiles
        # We only support 'base' layer for now as per simple grid
        if 'base' in spec.layers:
            tile_stream = rle_decompress(spec.layers['base'])
            for i, tile_id in enumerate(tile_stream):
                wx = i % spec.width
                wy = i // spec.width
                world.set_tile_at(wx, wy, tile_id)
        
        # 3. Deterministic Spawns
        # Sort spawns by y, x, then type key to ensure deterministic ID assignment
        sorted_spawns = sorted(spec.spawns, key=lambda s: (s.get('y', 0), s.get('x', 0), s.get('type', '')))
        
        # 4. Journaling
        if journal:
            journal.record_event("map_loaded", "system", {
                "name": spec.name,
                "width": spec.width,
                "height": spec.height,
                "seed": spec.seed,
                "spawn_count": len(sorted_spawns)
            })
            
        return sorted_spawns
