from typing import Optional, List, Tuple
from ai.ai_core import AgentAI

class Agent:
    def __init__(self, agent_id: str, x: int, y: int, species_priors: Optional[dict] = None, seed: int = 1337):
        self.agent_id = agent_id
        self.x = x
        self.y = y
        self.chunk_coords: Optional[Tuple[int, int]] = None # (cx, cy)
        
        self.energy = 1.0
        self.hunger = 0
        self.trainable = False
        self.last_action_result = "NONE"
        self.last_action_type = "NONE"
        self.last_action_target = None
        self.shared_beliefs = set() # Track what we've already told others
        self.killed_by = None # ID of agent that killed this one
        self.ai = AgentAI(agent_id, species_priors, seed=seed)

    def register(self, world):
        from src.chunk import Chunk
        cx, cy = int(self.x // Chunk.CHUNK_SIZE), int(self.y // Chunk.CHUNK_SIZE)
        chunk = world.get_chunk(cx, cy, create=True)
        if chunk:
            chunk.entities.add(self)
            self.chunk_coords = (cx, cy)

    def unregister(self, world):
        if self.chunk_coords:
            chunk = world.get_chunk(*self.chunk_coords, create=False)
            if chunk and self in chunk.entities:
                chunk.entities.remove(self)
        self.chunk_coords = None

    def move_to(self, nx, ny, world):
        from src.chunk import Chunk
        new_cx, new_cy = int(nx // Chunk.CHUNK_SIZE), int(ny // Chunk.CHUNK_SIZE)
        
        # Cross-chunk movement
        if (new_cx, new_cy) != self.chunk_coords:
            self.unregister(world)
            self.x, self.y = nx, ny
            self.register(world)
        else:
            self.x, self.y = nx, ny

    def update(self, world, journal):
        # 1. Perception (Updated to use World Spatial Query API)
        # Use query_radius to find nearby agents (e.g. within 15 tiles)
        perception_radius = 15
        nearby_agents = world.query_radius(self.x, self.y, radius=perception_radius)
        nearby_agents_clean = [{"id": a.agent_id, "x": a.x, "y": a.y} for a in nearby_agents if a != self]
        
        # Resources nearby (Spatial query would be better here too)
        resources = world.query_rect(self.x-perception_radius, self.y-perception_radius, self.x+perception_radius, self.y+perception_radius)
        
        world_view = {
            "neighbors": world.get_terrain_nearby(self.x, self.y, radius=2),
            "resources": resources,
            "agents": nearby_agents_clean,
            "physical_hunger": self.hunger,
            "recent_events": journal.get_recent_events(limit=20)
        }
        
        # 2. Think
        plan = self.ai.think(self.x, self.y, world_view, last_result=self.last_action_result, last_action=self.last_action_type, last_target=self.last_action_target, shared_beliefs=self.shared_beliefs)
        return plan

class Person(Agent):
    def __init__(self, agent_id, x, y, seed=1337):
        super().__init__(agent_id, x, y, species_priors={"compassion": 0.3, "gentleness": 0.5, "curiosity": 0.6, "sociability": 0.7, "type": "person"}, seed=seed)
        self.type = "person"

class Creature(Agent):
    def __init__(self, agent_id, x, y, seed=1337):
        # Creatures start more baseline/neutral but are more "extreme" in potential
        super().__init__(agent_id, x, y, species_priors={"compassion": 0.0, "gentleness": -0.2, "curiosity": 0.8, "type": "creature"}, seed=seed)
        self.type = "creature"
        self.trainable = True
