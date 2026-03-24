import pytest
import json
import os
from src.map_loader import MapLoader, rle_decompress
from src.world import GameWorld

def test_rle_decompress():
    stream = [1, 3, 2, 1, 5, 2] # 3x ID 1, 1x ID 2, 2x ID 5
    result = rle_decompress(stream)
    assert result == [1, 1, 1, 2, 5, 5]

def test_load_map(tmp_path):
    # Setup dummy map data
    map_data = {
        "name": "Test Map",
        "width": 10,
        "height": 10,
        "seed": 42,
        "tileset": {
            "tiles": [
                {"id": 0, "type": "water", "walkable": False},
                {"id": 1, "type": "grass", "walkable": True}
            ]
        },
        "layers": {
            "base": [1, 100] # 100 tiles of ID 1 (grass)
        },
        "spawns": [
            {"type": "creature", "x": 5, "y": 5},
            {"type": "villager", "x": 1, "y": 1}
        ]
    }
    
    map_file = tmp_path / "test_map.json"
    map_file.write_text(json.dumps(map_data))
    
    world = GameWorld()
    spawns = MapLoader.load(str(map_file), world)
    
    assert world.width == 10
    assert world.height == 10
    assert world.get_tile_at(0, 0) == 1
    assert world.get_tile_at(9, 9) == 1
    assert world.is_walkable(0, 0) == True
    
    # Verify deterministic spawns (villager first because y=1 < y=5)
    assert len(spawns) == 2
    assert spawns[0]['type'] == "villager"
    assert spawns[1]['type'] == "creature"
