import random

class GameWorld:
    def __init__(self, width: int, height: int, seed: int = 1337):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)
        # grid[y][x] stored as heightmap or tile data
        self.elevation = [[0.0 for _ in range(width)] for _ in range(height)]
        self.terrain_type = [["grass" for _ in range(width)] for _ in range(height)]
        self.resources = [] # list of (x, y, type)
        self._generate_world()

    def _generate_world(self):
        # 1. Generate Elevation (Simple blobs)
        for _ in range(5): # blobs
            bx, by = self.rng.randint(0, self.width-1), self.rng.randint(0, self.height-1)
            radius = self.rng.randint(5, 15)
            for y in range(max(0, by-radius), min(self.height, by+radius)):
                for x in range(max(0, bx-radius), min(self.width, bx+radius)):
                    dist = ((x-bx)**2 + (y-by)**2)**0.5
                    if dist < radius:
                        self.elevation[y][x] += (radius - dist) / radius
        
        # 2. Assign Terrain Types
        for y in range(self.height):
            for x in range(self.width):
                h = self.elevation[y][x]
                if h < 0.2:
                    self.terrain_type[y][x] = "water"
                elif h > 0.8:
                    self.terrain_type[y][x] = "mountain"
                else:
                    self.terrain_type[y][x] = "grass"
            
        # Spawn initial food
        for _ in range(10):
            self.add_resource("food")

    def add_resource(self, rtype: str):
        for _ in range(100): # Attempts
            rx = self.rng.randint(0, self.width - 1)
            ry = self.rng.randint(0, self.height - 1)
            if self.is_walkable(rx, ry):
                self.resources.append((rx, ry, rtype))
                return True
        return False
    
    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.terrain_type[y][x] != "water"
        return False

    def find_random_land_tile(self):
        for _ in range(1000): # High number of attempts for robustness
            rx = self.rng.randint(0, self.width - 1)
            ry = self.rng.randint(0, self.height - 1)
            if self.is_walkable(rx, ry):
                return rx, ry
        return 0, 0 # Fallback

    def get_elevation(self, x: int, y: int) -> float:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.elevation[y][x]
        return 0.0

    def get_terrain(self, x: int, y: int) -> str:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.terrain_type[y][x]
        return "water"

    def regenerate_resources(self, chance=0.01):
        # Slowly regrow food on empty grass tiles
        for y in range(self.height):
            for x in range(self.width):
                if self.terrain_type[y][x] == "grass":
                    has_res = any(rx == x and ry == y for rx, ry, _ in self.resources)
                    if not has_res and self.rng.random() < chance:
                        self.resources.append((x, y, "food"))

    def get_neighbors(self, x: int, y: int):
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def get_resources_nearby(self, x, y, radius=5):
        res = []
        for rx, ry, rtype in self.resources:
            if abs(rx - x) <= radius and abs(ry - y) <= radius:
                res.append((rx, ry, rtype))
        return res

    def get_terrain_nearby(self, x, y, radius=5):
        terrain = []
        for dy in range(2 * radius + 1):
            for dx in range(2 * radius + 1):
                nx, ny = x + dx - radius, y + dy - radius
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    terrain.append((nx, ny, self.terrain_type[ny][nx], self.elevation[ny][nx]))
        return terrain
