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
        # Normalize and cap
        for k in self.drives:
            self.drives[k] = max(0.0, min(1.0, self.drives[k]))
        for k in self.drives:
            self.drives[k] = max(0.0, min(1.0, self.drives[k]))

class TraitSystem:
    def __init__(self, species_priors: Optional[Dict] = None, rng: Optional[random.Random] = None):
        # Continuous traits in range [-1.0, +1.0]
        # Positive values = Good/Pro-social, Negative values = Evil/Selfish
        self.traits = {
            # Good/Evil Axis (Paired)
            "compassion": 0.0,  # +: Compassion, -: Cruelty
            "generosity": 0.0,   # +: Generosity, -: Greed
            "obedience": 0.0,    # +: Obedience, -: Arrogance
            "gentleness": 0.0,   # +: Gentleness, -: Aggression
            "diligence": 0.0,    # +: Diligence, -: Laziness
            "altruism": 0.0,     # +: Altruism, -: Dominance
            "empathy": 0.0,
            "gratitude": 0.0,
            "patience": 0.0,     # +: Patience, -: Vindictiveness
            "temperance": 0.0,
            "protectiveness": 0.0,
            "cleanliness": 0.0,
            
            # Additional Evil/Selfish mappings (can be independent or negative offsets)
            "sadism": 0.0,
            "deceitfulness": 0.0,
            "gluttony": 0.0,
            "destructiveness": 0.0,
            "neglectfulness": 0.0,
            "corruption": 0.0,

            # Neutral / Personality Traits (Style)
            "curiosity": 0.5,
            "playfulness": 0.5,
            "fearfulness": 0.5,
            "boldness": 0.5,
            "sociability": 0.5,
            "focus": 0.5,
            "adaptability": 0.5
        }
        if species_priors:
            self.traits.update(species_priors)
            
        # Individual Variance: +/- 0.4 randomization if rng is provided
        if rng:
            for k, v in self.traits.items():
                if isinstance(v, (int, float)):
                    variance = (rng.random() * 0.4) - 0.2
                    self.traits[k] = max(-1.0, min(1.0, v + variance))

class DesireSystem:
    def __init__(self):
        self.candidate_desires: List[Dict] = []

    def evaluate(self, drives: Dict, traits: Dict, learning: 'LearningSystem', agent_type: str, beliefs: BeliefSystem) -> List[Dict]:
        desires = []
        # Bias from learning (Habits)
        bias_eat = learning.get_bias("default", "eat")
        bias_explore = learning.get_bias("default", "explore")

        # Trait mappings (Mapping [-1, 1] to [0, 2] multipliers roughly)
        # 1.0 + trait allows 0.0 to 2.0 range (Neutral is 1.0)
        t_compassion = 1.0 + traits.get("compassion", 0.0)
        t_gentleness = 1.0 + traits.get("gentleness", 0.0)
        t_patience = 1.0 + traits.get("patience", 0.0)
        t_curiosity = 1.0 + traits.get("curiosity", 0.0)
        t_sociability = 1.0 + traits.get("sociability", 0.0)
        t_laziness = 1.0 - traits.get("diligence", 0.0) # diligent -> low laziness
        t_obedience = 1.0 + traits.get("obedience", 0.0)

        # hunger -> desire_food (Survival boost)
        # Non-linear boost after 0.6 hunger to prevent starvation
        survival_mult = 1.0
        if drives["hunger"] > 0.6:
            survival_mult = 1.0 + (drives["hunger"] - 0.6) * 15.0 # Even more aggressive boost
        if drives["hunger"] > 0.85:
            survival_mult *= 5.0 # Emergency priority
        
        # Ensure patience doesn't zero out hunger drive (floor 0.2)
        patience_factor = max(0.2, 2.0 - t_patience)
        desires.append({"goal": "eat", "utility": drives["hunger"] * patience_factor * bias_eat * survival_mult})

        # hunger + creature -> hunt (Only if prey is visible)
        if agent_type == "creature" and drives["hunger"] > 0.4:
            has_prey = any("villager" in a["id"] or a.get("type") == "person" for a in beliefs.known_agents)
            if has_prey:
                bias_hunt = learning.get_bias("default", "hunt")
                # High Aggression (negative gentleness) increases hunt utility
                aggression_factor = 2.0 - t_gentleness
                desires.append({"goal": "hunt", "utility": drives["hunger"] * aggression_factor * 2.0 + bias_hunt})

        # carnage + person -> flee
        if agent_type == "person" and beliefs.known_carnage:
            desires.append({"goal": "flee", "utility": 1.2}) # High priority fear

        # curiosity -> desire_explore
        desires.append({"goal": "explore", "utility": drives["curiosity"] * t_curiosity * bias_explore})

        # Social -> socialize
        desires.append({"goal": "socialize", "utility": drives["social"] * t_sociability})

        # Boredom -> idle
        desires.append({"goal": "idle", "utility": drives["boredom"] * t_laziness})

        # Compassion -> help
        desires.append({"goal": "help", "utility": t_compassion * 0.5})

        self.candidate_desires = sorted(desires, key=lambda x: x["utility"], reverse=True)
        return self.candidate_desires

class IntentionSystem:
    def __init__(self):
        self.current_intention: Optional[Dict] = None
        self.failed_intentions: Dict[str, int] = {} # goal -> failure_count

    def commit(self, desires: List[Dict]):
        if not desires:
            self.current_intention = None
            return None
            
        # Add penalty to utilities based on failure counts
        for d in desires:
            goal = d["goal"]
            fail_count = self.failed_intentions.get(goal, 0)
            if fail_count > 0:
                # Exponential decay penalty
                d["utility"] *= (0.5 ** fail_count)
        
        # Re-sort after penalties
        desires.sort(key=lambda x: x["utility"], reverse=True)
        
        # Commit to the highest utility desire
        self.current_intention = desires[0]
        return self.current_intention

    def report_failure(self):
        if self.current_intention:
            goal = self.current_intention["goal"]
            self.failed_intentions[goal] = self.failed_intentions.get(goal, 0) + 1
            self.current_intention = None

    def report_success(self):
        if self.current_intention:
            goal = self.current_intention["goal"]
            self.failed_intentions[goal] = 0

class Planner:
    def __init__(self, rng: random.Random):
        self.current_plan: List[tuple] = [] # List of primitive actions
        self.plan_id: Optional[str] = None
        self.rng = rng
        self.last_goal_pos: Optional[Tuple[int, int]] = None

    def generate_plan(self, intention: Dict, x: int, y: int, beliefs: BeliefSystem, agent_type: str, shared_beliefs: Optional[set] = None):
        if not intention:
            self.current_plan = [("idle", None)]
            return self.current_plan

        self.plan_id = f"plan_{self.rng.randint(0, 99999)}"
        goal = intention["goal"]
        
        if goal == "eat":
            food_locs = [loc for loc, t in beliefs.known_locations.items() if t in ["food", "remains"]]
            if food_locs:
                # Try targets until one is reachable
                food_locs.sort(key=lambda l: abs(l[0]-x) + abs(l[1]-y))
                for target in food_locs[:3]: # Check 3 nearest
                    rtype = beliefs.known_locations[target]
                    action = "eat" if rtype == "food" else "eat_villager"
                    path = self._astar(x, y, target, beliefs)
                    if path:
                        self.current_plan = [("move", p) for p in path] + [(action, target)]
                        return self.current_plan
                
                # If no path found to nearest targets, wander
                self._generate_exploration_plan(x, y, beliefs)
            else:
                # No known food: Targeted Exploration Search
                self._generate_exploration_plan(x, y, beliefs)
        elif goal == "socialize":
            if beliefs.known_agents:
                # Try to find a reachable agent
                agents = sorted(beliefs.known_agents, key=lambda a: abs(a["x"]-x) + abs(a["y"]-y))
                for target_agent in agents[:2]:
                    tx, ty = target_agent["x"], target_agent["y"]
                    path = self._astar(x, y, (tx, ty), beliefs)
                    
                    # Gossip logic
                    s_set = shared_beliefs if shared_beliefs is not None else set()
                    unshared = beliefs.get_interesting_beliefs(s_set)
                    gossip_actions = [("share_belief", (target_agent["id"], unshared[0][0], unshared[0][1]))] if unshared else []
                    
                    dist = abs(x - tx) + abs(y - ty)
                    if path:
                        self.current_plan = [("move", p) for p in path] + gossip_actions + [("socialize", target_agent["id"])]
                        return self.current_plan
                    elif dist <= 2:
                        self.current_plan = gossip_actions + [("socialize", target_agent["id"])]
                        return self.current_plan
                
                self.current_plan = [("move_random", None)]
            else:
                self.current_plan = [("move_random", None)]
        elif goal == "hunt":
            target_ids = [a["id"] for a in beliefs.known_agents if "villager" in a["id"] or a.get("type") == "person"]
            if target_ids:
                # Try nearest targets
                agents = [a for a in beliefs.known_agents if a["id"] in target_ids]
                agents.sort(key=lambda a: abs(a["x"]-x) + abs(a["y"]-y))
                
                for target_agent in agents[:2]:
                    tx, ty = target_agent["x"], target_agent["y"]
                    path = self._astar(x, y, (tx, ty), beliefs)
                    if path:
                        self.current_plan = [("move", p) for p in path] + [("kill_villager", target_agent["id"]), ("eat_villager", target_agent["id"])]
                        return self.current_plan
                
                self.current_plan = [("move_random", None)]
            else:
                self.current_plan = [("move_random", None)]
        elif goal == "flee":
            if beliefs.known_carnage:
                carnage_pos = list(beliefs.known_carnage)[0]
                self.current_plan = [("move_random", None), ("move_random", None)]
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
                    agents = sorted(beliefs.known_agents, key=lambda a: abs(a["x"]-x) + abs(a["y"]-y))
                    for target_agent in agents[:2]:
                        tx, ty = target_agent["x"], target_agent["y"]
                        dist = abs(x - tx) + abs(y - ty)
                        if dist <= 2:
                            self.current_plan = [("share_belief", (target_agent["id"], unshared[0][0], unshared[0][1]))]
                            return self.current_plan
                        else:
                            path = self._astar(x, y, (tx, ty), beliefs)
                            if path:
                                self.current_plan = [("move", p) for p in path] + [("share_belief", (target_agent["id"], unshared[0][0], unshared[0][1]))]
                                return self.current_plan
                self.current_plan = [("move_random", None)]
            else:
                self.current_plan = [("move_random", None)]
        else:
            self.current_plan = [("idle", None)]
        return self.current_plan

    def _generate_exploration_plan(self, x, y, beliefs: BeliefSystem):
        """Generates a multi-step plan to move towards an unexplored area."""
        # Pick 5 random distant tiles and see which one is walkable and far
        best_target = None
        max_dist = -1
        
        # We don't have world dimensions here, but we can guess or use terrain_kb bounds
        # Simple: just pick random offsets and check terrain_kb
        for _ in range(10):
            tx = x + self.rng.randint(-15, 15)
            ty = y + self.rng.randint(-15, 15)
            # Only target tiles we know are walkable
            if (tx, ty) in beliefs.terrain_kb and beliefs.terrain_kb[(tx, ty)] != "water":
                dist = abs(tx - x) + abs(ty - y)
                if dist > max_dist:
                    max_dist = dist
                    best_target = (tx, ty)
        
        if best_target:
            path = self._astar(x, y, best_target, beliefs)
            if path:
                self.current_plan = [("move", p) for p in path]
                return
        
        # Total fallback
        self.current_plan = [("move_random", None)]

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
