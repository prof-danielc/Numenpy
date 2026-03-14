from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from .learning import LearningSystem
import random

class BeliefSystem:
    def __init__(self):
        self.beliefs = {} # object_type -> affordances
        self.known_locations = {} # (x, y) -> object_type
        self.known_agents = []
        self.known_carnage = set() # Locations of recent deaths
        self.terrain_kb = {} # (x, y) -> str
        self.elevation_kb = {} # (x, y) -> float
        
    def update(self, x: int, y: int, neighbors: List, resources: List, agents: List = [], events: List = []):
        # neighbors is now List of (x, y, ttype, elevation)
        for nx, ny, ttype, elev in neighbors:
            self.terrain_kb[(nx, ny)] = ttype
            self.elevation_kb[(nx, ny)] = elev
            
        for rx, ry, rtype in resources:
            if abs(rx - x) <= 5 and abs(ry - y) <= 5:
                self.known_locations[(rx, ry)] = rtype
        
        # Track other agents
        self.known_agents = agents 

        # Prune stale beliefs (FR-015: Perception-Belief Sync)
        # For every neighboring tile we can see, if we thought there was a resource there
        # but it's not in the current 'resources' list, it must be gone.
        visible_tiles = {(nx, ny) for nx, ny, ttype, elev in neighbors}
        actual_resources = {(rx, ry) for rx, ry, rtype in resources}
        
        stale_locs = []
        for loc, rtype in self.known_locations.items():
            if loc in visible_tiles and loc not in actual_resources:
                stale_locs.append(loc)
        
        for loc in stale_locs:
            self.known_locations.pop(loc, None)

        # Track carnage/deaths within perception range
        for event in events:
            if event["event_type"] == "entity_death":
                ex, ey = event["data"].get("x"), event["data"].get("y")
                if ex is not None and ey is not None:
                    if abs(ex - x) <= 5 and abs(ey - y) <= 5:
                        self.known_carnage.add((ex, ey))

    def get_interesting_beliefs(self, shared_set: set):
        # TODO: brainstorming here 
        # instead of returning locations of a fixed resource (currently food)
        # the agent should be able to return locations of any object type
        # and the planner should be able to generate a plan to share it
        # according to what the agent FEELS (desires?) to be most important

        # Return locations of food not yet shared
        interesting = []
        for loc, rtype in self.known_locations.items():
            if rtype == "food" and loc not in shared_set:
                interesting.append((loc, rtype))
        return interesting

class DriveSystem:
    def __init__(self):
        self.drives = {
            "hunger": 0.0,
            "boredom": 0.0,
            "curiosity": 0.0,
            "approval": 1.0, # desire for player approval
            "social": 0.5 # companion seeking
        }

    def update(self):
        # Accumulate drives over time (0.01 was too fast)
        self.drives["hunger"] += 0.0002
        self.drives["boredom"] += 0.005
        self.drives["curiosity"] += 0.002
        self.drives["social"] += 0.003
        # Normalize
        for k in self.drives:
            self.drives[k] = max(0.0, min(1.0, self.drives[k]))

class TraitSystem:
    def __init__(self, species_priors: Optional[Dict] = None, rng: Optional[random.Random] = None):
        self.traits = {
            "aggression": 0.5,
            "compassion": 0.5,
            "curiosity": 0.5,
            "friendliness": 0.5,
            "laziness": 0.2,
            "bravery": 0.5
        }
        if species_priors:
            self.traits.update(species_priors)
            
        # Individual Variance: +/- 20% randomization if rng is provided
        if rng:
            for k, v in self.traits.items():
                if isinstance(v, (int, float)):
                    variance = (rng.random() * 0.4) - 0.2 # -0.2 to 0.2
                    self.traits[k] = max(0.0, min(1.0, v + variance))

class DesireSystem:
    def __init__(self):
        self.candidate_desires: List[Dict] = []

    def evaluate(self, drives: Dict, traits: Dict, learning: 'LearningSystem', agent_type: str, beliefs: BeliefSystem) -> List[Dict]:
        desires = []
        # Bias from learning
        bias_eat = learning.get_bias("default", "eat")
        bias_explore = learning.get_bias("default", "explore")
        # hunger -> desire_food (All agents need to eat!)
        desires.append({"goal": "eat", "utility": drives["hunger"] * (1.2 - traits["laziness"]) * bias_eat})

        # hunger + creature -> hunt (Only if prey is visible)
        if agent_type == "creature" and drives["hunger"] > 0.4:
            has_prey = any("villager" in a["id"] or a.get("type") == "person" for a in beliefs.known_agents)
            if has_prey:
                bias_hunt = learning.get_bias("default", "hunt")
                desires.append({"goal": "hunt", "utility": drives["hunger"] * traits["aggression"] * 2.0 + bias_hunt})

        # carnage + person -> flee
        if agent_type == "person" and beliefs.known_carnage:
            desires.append({"goal": "flee", "utility": 0.8}) # High priority fear
        
        # curiosity -> desire_explore (Brave agents explore more)
        desires.append({"goal": "explore", "utility": drives["curiosity"] * traits["curiosity"] * traits["bravery"] * bias_explore})
        
        # social -> socialize (Friendly agents prioritize social, boost if we have gossip)
        social_utility = drives["social"] * traits["friendliness"]
        # Boost if we have unshared interesting beliefs
        # Note: DesireSystem doesn't have access to Agent but we can pass shared_set or just assume
        # For now, let's just use the basic utility and let Planner handle the action choice.
        desires.append({"goal": "socialize", "utility": social_utility})

        # boredom -> idle (Lazy agents idle more)
        desires.append({"goal": "idle", "utility": drives["boredom"] * traits["laziness"]})

        # compassion -> help
        desires.append({"goal": "help", "utility": traits["compassion"] * 0.5})
        
        self.candidate_desires = sorted(desires, key=lambda x: x["utility"], reverse=True)
        return self.candidate_desires

class IntentionSystem:
    def __init__(self):
        self.current_intention: Optional[Dict] = None

    def commit(self, desires: List[Dict]):
        if desires:
            # Commit to the highest utility desire
            self.current_intention = desires[0]
        return self.current_intention

class Planner:
    def __init__(self, rng: random.Random):
        self.current_plan: List[tuple] = [] # List of primitive actions
        self.plan_id: Optional[str] = None
        self.rng = rng

    def generate_plan(self, intention: Dict, x: int, y: int, beliefs: BeliefSystem, agent_type: str, shared_beliefs: Optional[set] = None):
        self.plan_id = f"plan_{self.rng.randint(0, 99999)}"
        goal = intention["goal"]
        
        if goal == "eat":
            food_locs = [loc for loc, t in beliefs.known_locations.items() if t in ["food", "remains"]]
            if food_locs:
                target = min(food_locs, key=lambda l: abs(l[0]-x) + abs(l[1]-y))
                rtype = beliefs.known_locations[target]
                action = "eat" if rtype == "food" else "eat_villager"
                path = self._astar(x, y, target, beliefs)
                if path:
                    self.current_plan = [("move", p) for p in path] + [(action, target)]
                else:
                    self.current_plan = [("move", target), (action, target)] # Fallback
            else:
                self.current_plan = [("move_random", None)]
        elif goal == "socialize":
            if beliefs.known_agents:
                target_agent = beliefs.known_agents[0]
                tx, ty = target_agent["x"], target_agent["y"]
                path = self._astar(x, y, (tx, ty), beliefs)
                
                # Gossip logic: check for interesting things to say
                s_set = shared_beliefs if shared_beliefs is not None else set()
                unshared = beliefs.get_interesting_beliefs(s_set)
                gossip_actions = [("share_belief", (target_agent["id"], unshared[0][0], unshared[0][1]))] if unshared else []
                
                dist = abs(x - tx) + abs(y - ty)
                if path:
                    # We have a known path. Move, then interact.
                    self.current_plan = [("move", p) for p in path] + gossip_actions + [("socialize", target_agent["id"])]
                elif dist <= 2:
                    # No path needed, we are already adjacent
                    self.current_plan = gossip_actions + [("socialize", target_agent["id"])]
                else:
                    # Target is far and we don't know the path. Try to wander closer or explore.
                    self.current_plan = [("move_random", None)]
            else:
                self.current_plan = [("move_random", None)]
        elif goal == "hunt":
            # Target villagers
            target_ids = [a["id"] for a in beliefs.known_agents if "villager" in a["id"] or a.get("type") == "person"]
            if target_ids:
                target_id = target_ids[0]
                # Find target's last known pos
                target_agent = next((a for a in beliefs.known_agents if a["id"] == target_id), None)
                if target_agent:
                    tx, ty = target_agent["x"], target_agent["y"]
                    path = self._astar(x, y, (tx, ty), beliefs)
                    if path:
                        self.current_plan = [("move", p) for p in path] + [("kill_villager", target_id), ("eat_villager", target_id)]
                    else:
                        self.current_plan = [("move", (tx, ty)), ("kill_villager", target_id), ("eat_villager", target_id)]
                else:
                    self.current_plan = [("move_random", None)]
            else:
                self.current_plan = [("move_random", None)]
        elif goal == "flee":
            if beliefs.known_carnage:
                # Move away from nearest carnage
                carnage_pos = list(beliefs.known_carnage)[0]
                dx = x - carnage_pos[0]
                dy = y - carnage_pos[1]
                # Try to move away
                target_x = x + (1 if dx >= 0 else -1) * 3
                target_y = y + (1 if dy >= 0 else -1) * 3
                self.current_plan = [("move_random", None), ("move_random", None)]
                # Clear fear after fleeing
                beliefs.known_carnage.clear()
            else:
                self.current_plan = [("idle", None)]
        elif goal == "explore":
             self.current_plan = [("move_random", None)]
        elif goal == "help":
            if beliefs.known_agents and beliefs.known_locations:
                s_set = shared_beliefs if shared_beliefs is not None else set()
                unshared = beliefs.get_interesting_beliefs(s_set)
                if unshared:
                    target_agent = beliefs.known_agents[0]
                    tx, ty = target_agent["x"], target_agent["y"]
                    dist = abs(x - tx) + abs(y - ty)
                    
                    if dist <= 2:
                        loc, rtype = unshared[0]
                        self.current_plan = [("share_belief", (target_agent["id"], loc, rtype))]
                    else:
                        path = self._astar(x, y, (tx, ty), beliefs)
                        if path:
                            self.current_plan = [("move", p) for p in path] + [("share_belief", (target_agent["id"], unshared[0][0], unshared[0][1]))]
                        else:
                            self.current_plan = [("move_random", None)]
                else:
                    self.current_plan = [("move_random", None)]
            else:
                self.current_plan = [("move_random", None)]
        else:
            self.current_plan = [("idle", None)]
        return self.current_plan

    def _astar(self, start_x, start_y, goal_pos, beliefs: BeliefSystem):
        import heapq
        start = (start_x, start_y)
        frontier = [(0, start)]
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        cost_so_far: Dict[Tuple[int, int], float] = {start: 0.0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            if current == goal_pos: break
            
            cx, cy = current
            # Neighbors are adjacent tiles known in terrain_kb
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_pos = (cx + dx, cy + dy)
                if next_pos not in beliefs.terrain_kb: continue
                if beliefs.terrain_kb[next_pos] == "water": continue
                
                # Cost formula matching logic.py
                h1 = beliefs.elevation_kb[current]
                h2 = beliefs.elevation_kb[next_pos]
                new_cost = cost_so_far[current] + 1.0 + max(0, h2 - h1) * 5.0
                
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + abs(next_pos[0] - goal_pos[0]) + abs(next_pos[1] - goal_pos[1])
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        if goal_pos not in came_from: return None
        
        # Reconstruct path
        path = []
        curr = goal_pos
        while curr != start:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()
        return path
