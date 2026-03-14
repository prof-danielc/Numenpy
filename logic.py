class GameLogic:
    def __init__(self, world, journal):
        self.world = world
        self.journal = journal
        self.entities = []
        self.tick_count = 0

    def add_agent(self, agent):
        self.entities.append(agent)
    
    def update(self):
        """Core simulation tick - NO PYGAME ALLOWED HERE"""
        self.tick_count += 1
        
        # 1. World updates
        self.world.regenerate_resources(chance=0.0001)
        
        # 2. Update all entities
        for entity in self.entities:
            # Physical hunger naturally increases (0.01 was too fast)
            entity.hunger = min(1.0, entity.hunger + 0.002)
            
            # Starvation damage
            if entity.hunger >= 0.95:
                entity.energy -= 0.001
                if self.tick_count % 10 == 0:
                    self.journal.log(entity.agent_id, "is starting to starve...")
            
            # Sync AI with physical reality
            nearby_terrain = self.world.get_terrain_nearby(entity.x, entity.y, radius=5)
            nearby_resources = self.world.get_resources_nearby(entity.x, entity.y, radius=5)
            
            world_view = {
                "neighbors": nearby_terrain, # AI.think expects a list of (x, y, type, elev)
                "resources": nearby_resources,
                "agents": [{"id": a.agent_id, "x": a.x, "y": a.y} for a in self.entities if a != entity and abs(a.x - entity.x) <= 5 and abs(a.y - entity.y) <= 5],
                "physical_hunger": entity.hunger,
                "recent_events": self.journal.get_recent_events(limit=20)
            }
            
            plan = entity.ai.think(entity.x, entity.y, world_view, last_result=entity.last_action_result, shared_beliefs=entity.shared_beliefs)
            if plan:
                self._execute_action(entity, plan)
            
        # 3. Cleanup Dead Agents
        alive_agents = [a for a in self.entities if a.energy > 0]
        if len(alive_agents) < len(self.entities):
            for a in self.entities:
                if a.energy <= 0:
                    cause = "starvation"
                    if a.killed_by:
                        cause = f"killed by {a.killed_by}"
                        # Spawn remains for predators to eat later
                        self.world.resources.append((a.x, a.y, "remains"))
                    
                    self.journal.record_event("entity_death", a.agent_id, {
                        "x": a.x, "y": a.y, 
                        "type": a.type if hasattr(a, 'type') else "unknown",
                        "cause": cause
                    })
                    self.journal.log(a.agent_id, f"has perished (Cause: {cause}).")
        self.entities = alive_agents

    def _execute_action(self, agent, plan):
        action_type, target = plan[0]
        result = "FAILURE"
        
        if action_type == "move":
            tx, ty = target
            if self.world.is_walkable(tx, ty):
                # Calculate cost (elevation difference)
                old_h = self.world.get_elevation(agent.x, agent.y)
                new_h = self.world.get_elevation(tx, ty)
                diff = max(0, new_h - old_h)
                
                # Apply effort penalty to drives if it exists
                if hasattr(agent.ai, 'drives'):
                    agent.ai.drives.drives["hunger"] += 0.005 * (1.0 + diff * 5.0)
                
                agent.x, agent.y = tx, ty
                result = "SUCCESS"
            else:
                result = "IMPASSABLE"
        elif action_type == "move_random":
            import random
            neighbors = self.world.get_neighbors(agent.x, agent.y)
            if neighbors:
                agent.x, agent.y = random.choice(neighbors)
                result = "SUCCESS"
        elif action_type == "eat":
            # Check if food is still there
            tx, ty = target
            food_found = False
            for i, (rx, ry, rtype) in enumerate(self.world.resources):
                if rx == tx and ry == ty and rtype == "food":
                    if abs(agent.x - rx) <= 1 and abs(agent.y - ry) <= 1:
                        self.world.resources.pop(i)
                        agent.hunger = max(0.0, agent.hunger - 0.5)
                        if hasattr(agent.ai, 'learning'):
                            agent.ai.learning.apply_feedback(agent.ai.planner.plan_id, 1.5)
                        food_found = True
                        result = "SUCCESS"
                        break
            if not food_found:
                result = "MISSING"
        elif action_type == "socialize":
            # Check proximity to target agent
            target_id = target
            target_agent = next((e for e in self.entities if e.agent_id == target_id), None)
            if target_agent and abs(agent.x - target_agent.x) <= 1 and abs(agent.y - target_agent.y) <= 1:
                agent.ai.drives.drives["social"] = max(0.0, agent.ai.drives.drives["social"] - 0.5)
                # Reciprocal benefit
                if hasattr(target_agent.ai.drives, 'drives'):
                    target_agent.ai.drives.drives["social"] = max(0.0, target_agent.ai.drives.drives["social"] - 0.3)
                result = "SUCCESS"
            else:
                result = "MISSING"
        elif action_type == "share_belief":
            target_id, loc, rtype = target
            target_agent = next((e for e in self.entities if e.agent_id == target_id), None)
            if target_agent and abs(agent.x - target_agent.x) <= 2 and abs(agent.y - target_agent.y) <= 2:
                target_agent.ai.beliefs.known_locations[loc] = rtype
                agent.shared_beliefs.add(loc) # Mark as shared
                self.journal.log(agent.agent_id, f"told {target_id} about food at {loc}")
                result = "SUCCESS"
            else:
                result = "MISSING"
        elif action_type == "idle":
            result = "SUCCESS"
        elif action_type == "kill_villager":
            # Target is a villager ID
            target_agent = next((e for e in self.entities if e.agent_id == target), None)
            if target_agent and hasattr(target_agent, 'type') and target_agent.type == "person":
                if abs(agent.x - target_agent.x) <= 1 and abs(agent.y - target_agent.y) <= 1:
                    target_agent.energy = 0 # Instant kill for now
                    target_agent.killed_by = agent.agent_id # Track perpetrator
                    result = "SUCCESS"
                else:
                    result = "TOO_FAR"
            else:
                result = "INVALID_TARGET"
        elif action_type == "eat_villager":
            # Check for "remains" resource at target location
            # Target for eat_villager is usually the same as the kill target (the dead agent's ID)
            # But remains are at a location. Let's find agent's current location or target's last known.
            # Simplified: just look for 'remains' in adjacent tiles.
            remains_found = False
            for i, (rx, ry, rtype) in enumerate(self.world.resources):
                if rtype == "remains":
                    if abs(agent.x - rx) <= 1 and abs(agent.y - ry) <= 1:
                        self.world.resources.pop(i)
                        agent.hunger = max(0.0, agent.hunger - 0.7)
                        if hasattr(agent.ai, 'learning'):
                            agent.ai.learning.apply_feedback(agent.ai.planner.plan_id, 2.0)
                        remains_found = True
                        result = "SUCCESS"
                        break
            if not remains_found:
                result = "MISSING"
        
        # Journal the action
        self.journal.record_event(
            event_type=f"action_{action_type}",
            actor_id=agent.agent_id,
            data={"target": target, "result": result},
            plan_id=agent.ai.planner.plan_id
        )
        
        # Propagate result to agent for reactivity
        agent.last_action_result = result
        
        # FR-013: Planner Interruption
        if result == "SUCCESS":
            plan.pop(0) # Step completed
        else:
            agent.ai.planner.current_plan = [] # Abort and re-evaluate
