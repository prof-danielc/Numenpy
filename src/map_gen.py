import orjson
import numpy as np
import random
import os

def generate_island_map(width=100, height=100, filename="maps/island_map.json"):
    # 1. Create base layers
    # Layers: 0: Void, 1: Grass, 2: Sand, 3: Water, 4: Mountain, 5: Tree
    grid = np.zeros((height, width), dtype=int)
    
    cx, cy = width // 2, height // 2
    max_dist = min(cx, cy)
    
    for y in range(height):
        for x in range(width):
            dist = np.sqrt((x - cx)**2 + (y - cy)**2)
            noise = random.uniform(-5, 5)
            effective_dist = dist + noise
            
            if effective_dist < max_dist * 0.4:
                # Mountain core
                if random.random() < 0.2:
                    grid[y, x] = 4 # Mountain
                elif random.random() < 0.15:
                    grid[y, x] = 5 # Tree
                else:
                    grid[y, x] = 1 # Grass
            elif effective_dist < max_dist * 0.7:
                # Main land
                if random.random() < 0.05:
                    grid[y, x] = 5 # Tree
                else:
                    grid[y, x] = 1 # Grass
            elif effective_dist < max_dist * 0.85:
                # Sand beaches
                grid[y, x] = 2 # Sand
            else:
                # Surrounding Water
                grid[y, x] = 3 # Water

    # 2. RLE Compression
    def compress_rle(arr):
        flat = arr.flatten()
        if len(flat) == 0: return []
        
        result = []
        current_id = int(flat[0])
        count = 0
        
        for val in flat:
            if int(val) == current_id:
                count += 1
            else:
                result.extend([current_id, count])
                current_id = int(val)
                count = 1
        result.extend([current_id, count])
        return result

    base_layer_rle = compress_rle(grid)
    
    # 3. Tileset Palette
    tileset = {
        "tiles": [
            {"id": 1, "type": "grass", "walkable": True, "color": [34, 139, 34]},
            {"id": 2, "type": "sand", "walkable": True, "color": [238, 214, 175]},
            {"id": 3, "type": "water", "walkable": False, "color": [30, 144, 255]},
            {"id": 4, "type": "mountain", "walkable": False, "color": [139, 137, 137]},
            {"id": 5, "type": "tree", "walkable": False, "color": [0, 100, 0]}
        ]
    }
    
    # 4. Spawns
    spawns = []
    # Find valid land tiles
    land_tiles = []
    for y in range(height):
        for x in range(width):
            if grid[y, x] == 1: # Grass only for spawns
                land_tiles.append((x, y))
    
    random.shuffle(land_tiles)
    
    # 10 Villagers
    for i in range(10):
        if land_tiles:
            tx, ty = land_tiles.pop()
            spawns.append({"type": "person", "x": tx, "y": ty, "id": f"villager_{i}"})
            
    # 1 Creature
    if land_tiles:
        tx, ty = land_tiles.pop()
        spawns.append({"type": "creature", "x": tx, "y": ty, "id": "behemoth_0"})

    # 5. Assemble and Save
    map_data = {
        "name": "Honey Island",
        "width": width,
        "height": height,
        "seed": random.randint(0, 9999),
        "tileset": tileset,
        "layers": {
            "base": base_layer_rle
        },
        "spawns": spawns
    }
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(orjson.dumps(map_data, option=orjson.OPT_INDENT_2))
    
    print(f"Generated map saved to {filename}")

if __name__ == "__main__":
    generate_island_map()
