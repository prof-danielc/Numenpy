from typing import Optional, List
from ai.ai_core import AgentAI

class Agent:
    def __init__(self, agent_id: str, x: int, y: int, species_priors: Optional[dict] = None, seed: int = 1337):
        self.agent_id = agent_id
        self.x = x
        self.y = y
        self.energy = 1.0
        self.hunger = 0
        self.trainable = False
        self.last_action_result = "NONE"
        self.shared_beliefs = set() # Track what we've already told others
        self.ai = AgentAI(agent_id, species_priors, seed=seed)

    def update(self, world, journal, agents: List = []):
        # 1. Perception
        neighbors = []
        for nx, ny in world.get_neighbors(self.x, self.y):
            neighbors.append((nx, ny, world.get_terrain(nx, ny), world.get_elevation(nx, ny)))
        neighbors.append((self.x, self.y, world.get_terrain(self.x, self.y), world.get_elevation(self.x, self.y)))
        
        # Resources nearby
        resources = world.resources
        
        # Agents nearby
        nearby_agents = [{"id": a.agent_id, "x": a.x, "y": a.y} for a in agents if a.agent_id != self.agent_id]
        
        world_view = {
            "neighbors": neighbors,
            "resources": resources,
            "agents": nearby_agents
        }
        
        # 2. Think
        plan = self.ai.think(self.x, self.y, world_view, last_result=self.last_action_result, shared_beliefs=self.shared_beliefs)
        
        # 3. Execution (handled by logic.py or delegated here)
        return plan

class Person(Agent):
    def __init__(self, agent_id: str, x: int, y: int, seed: int = 1337):
        super().__init__(agent_id, x, y, species_priors={"aggression": 0.2, "curiosity": 0.8}, seed=seed)
        self.type = "person"

class Creature(Agent):
    def __init__(self, agent_id: str, x: int, y: int, seed: int = 1337):
        super().__init__(agent_id, x, y, species_priors={"aggression": 0.5, "curiosity": 0.9}, seed=seed)
        self.type = "creature"
        self.trainable = True
