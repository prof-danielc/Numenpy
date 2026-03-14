import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld

def verify_spawn():
    world = GameWorld(40, 30, seed=1337)
    print("Testing find_random_land_tile...")
    for i in range(10):
        x, y = world.find_random_land_tile()
        terrain = world.get_terrain(x, y)
        print(f"Spawn {i}: ({x}, {y}) -> {terrain}")
        assert terrain != "water", f"FAILED: Spawned on water at ({x}, {y})"
    print("SUCCESS: All test spawns were on land.")

if __name__ == "__main__":
    verify_spawn()
