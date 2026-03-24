import pytest
from src.world import GameWorld
from src.entities import Agent
from src.chunk import Chunk

def test_spatial_registration():
    world = GameWorld(seed=42)
    # Force initialize dimensions
    world.set_tile_at(100, 100, 1)
    
    # 1. Register agent in chunk (0, 0)
    a1 = Agent("a1", 5, 5)
    a1.register(world)
    
    chunk = world.get_chunk(0, 0, create=False)
    assert a1 in chunk.entities
    assert a1.chunk_coords == (0, 0)
    
    # 2. Move to different chunk (1, 1) - Chunk size is 32
    a1.move_to(35, 35, world)
    
    old_chunk = world.get_chunk(0, 0, create=False)
    new_chunk = world.get_chunk(1, 1, create=False)
    
    assert a1 not in old_chunk.entities
    assert a1 in new_chunk.entities
    assert a1.chunk_coords == (1, 1)
    
    # 3. Spatial Query
    nearby = world.query_radius(34, 34, radius=2)
    assert a1 in nearby
    
    far = world.query_radius(0, 0, radius=5)
    assert a1 not in far

def test_picking():
    world = GameWorld(seed=42)
    world.set_tile_at(100, 100, 1)
    
    a1 = Agent("a1", 10, 10)
    a2 = Agent("a2", 11, 11)
    a1.register(world)
    a2.register(world)
    
    # Click exactly on a1
    picked = world.pick_entity(10, 10)
    assert picked == a1
    
    # Click between them, but closer to a2
    picked = world.pick_entity(10.8, 10.8)
    assert picked == a2
    
    # Click far away
    picked = world.pick_entity(50, 50)
    assert picked is None
