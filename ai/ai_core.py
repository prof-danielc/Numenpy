import random
from typing import Optional
from .ai_systems import BeliefSystem, DriveSystem, TraitSystem, DesireSystem, IntentionSystem, Planner
from .learning import LearningSystem

class AgentAI:
    def __init__(self, agent_id: str, species_priors: Optional[dict] = None, seed: int = 1337):
        self.agent_id = agent_id
        self.rng = random.Random(seed)
        self.beliefs = BeliefSystem()
        self.drives = DriveSystem()
        self.traits = TraitSystem(species_priors, rng=self.rng)
        self.desires = DesireSystem()
        self.intentions = IntentionSystem()
        self.planner = Planner(self.rng)
        self.learning = LearningSystem(agent_id)
        self.agent_type = species_priors.get("type", "unknown") if species_priors else "unknown"
        
    def think(self, x: int, y: int, world_view: dict, last_result: str = "NONE", shared_beliefs: Optional[set] = None):
        # 1. Update Beliefs
        self.beliefs.update(x, y, world_view["neighbors"], world_view["resources"], world_view.get("agents", []), world_view.get("recent_events", []))
        
        # 2. Update Drives
        self.drives.update()
        # SYNC: Biological hunger overrides psychological accumulation
        if "physical_hunger" in world_view:
            self.drives.drives["hunger"] = world_view["physical_hunger"]

        # 3. Handle Failure / Interruption
        # If the last action failed, we should flush existing plan and re-evaluate
        if last_result not in ["SUCCESS", "NONE"]:
            self.planner.current_plan = []
        
        # 3. Evaluate Desires
        candidate_desires = self.desires.evaluate(self.drives.drives, self.traits.traits, self.learning, self.agent_type, self.beliefs)
        
        # 4. Commit to Intention if no active plan
        if not self.planner.current_plan:
            intention = self.intentions.commit(candidate_desires)
            if intention:
                self.planner.generate_plan(intention, x, y, self.beliefs, self.agent_type, shared_beliefs=shared_beliefs)
        
        # 5. Record action if plan exists (for credit assignment)
        if self.planner.current_plan and self.planner.plan_id:
            action_tag = self.planner.current_plan[0][0]
            intention_id = self.intentions.current_intention["goal"] if self.intentions.current_intention else "unknown"
            self.learning.record_action(self.planner.plan_id, intention_id, action_tag)
            
        return self.planner.current_plan
