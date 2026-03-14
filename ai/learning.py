import time
from typing import Dict, List, Optional

class LearningSystem:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # matrix[context][action_id] = weight
        self.behavior_matrix: Dict[str, Dict[str, float]] = {
            "default": {"eat": 1.0, "play": 1.0, "explore": 1.0}
        }
        # trace[plan_id][action_tag] = timestamp_or_decay_value
        self.eligibility_traces: Dict[str, List[Dict]] = {}
        self.lambda_decay = 0.8 # Eligibility decay factor

    def record_action(self, plan_id: str, intention_id: str, action_tag: str):
        """Add action to eligibility trace for the specific plan."""
        if plan_id not in self.eligibility_traces:
            self.eligibility_traces[plan_id] = []
        
        # Add new action with full eligibility (1.0)
        # Decay existing traces for this plan
        for trace in self.eligibility_traces[plan_id]:
            trace["value"] *= self.lambda_decay
            
        self.eligibility_traces[plan_id].append({
            "action": action_tag,
            "intention": intention_id,
            "value": 1.0
        })

    def apply_feedback(self, plan_id: Optional[str], reward: float):
        """Apply reward/punishment to actions and intentions in the active plan's trace."""
        if plan_id is None or plan_id not in self.eligibility_traces:
            return # No context to apply feedback to
            
        traces = self.eligibility_traces[plan_id]
        context = "default"
        if context not in self.behavior_matrix:
            self.behavior_matrix[context] = {}
            
        alpha = 0.5 # Learning rate
        
        for trace in traces:
            action = trace["action"]
            intention = trace["intention"] # This is the GOAL name (e.g. "eat")
            value = trace["value"]
            
            # Update action weight
            if action not in self.behavior_matrix[context]:
                self.behavior_matrix[context][action] = 1.0
            self.behavior_matrix[context][action] += alpha * reward * value
            
            # Update intention weight (the GOAL bias)
            if intention not in self.behavior_matrix[context]:
                self.behavior_matrix[context][intention] = 1.0
            self.behavior_matrix[context][intention] += alpha * reward * value
            
            # Clamp
            self.behavior_matrix[context][action] = max(0.1, min(5.0, self.behavior_matrix[context][action]))
            self.behavior_matrix[context][intention] = max(0.1, min(5.0, self.behavior_matrix[context][intention]))

    def get_bias(self, context: str, action: str) -> float:
        return self.behavior_matrix.get(context, {}).get(action, 1.0)
