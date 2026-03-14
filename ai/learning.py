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

    def apply_feedback(self, plan_id: Optional[str], reward: float, traits: Optional[Dict] = None):
        """Apply reward/punishment to actions and intentions in the active plan's trace."""
        if plan_id is None or plan_id not in self.eligibility_traces:
            return # No context to apply feedback to
            
        traces = self.eligibility_traces[plan_id]
        context = "default"
        if context not in self.behavior_matrix:
            self.behavior_matrix[context] = {}
            
        alpha = 0.5 # Learning rate for habits
        trait_alpha = alpha / 5.0 # traits shift 5x slower
        
        # Intention-Specific Feedback Map (Good: +, Evil: -)
        TRAIT_MAP = {
            "hunt": {"positive": [("gentleness", 1.0), ("patience", 1.0)], "negative": [("compassion", -1.0), ("gentleness", -1.0)]},
            "socialize": {"positive": [("compassion", 1.0), ("empathy", 1.0)], "negative": [("patience", -1.0), ("obedience", -1.0)]},
            "eat": {"positive": [("patience", 1.0), ("obedience", 1.0)], "negative": [("generosity", -1.0), ("gluttony", 1.0)]},
            "explore": {"positive": [("curiosity", 1.0), ("focus", 1.0)], "negative": [("fearfulness", 1.0)]},
            "work": {"positive": [("diligence", 1.0), ("altruism", 1.0)], "negative": [("diligence", -1.0), ("altruism", -1.0)]}
        }
        
        for trace in traces:
            action = trace["action"]
            intention = trace["intention"] # This is the GOAL name (e.g. "eat")
            value = trace["value"]
            
            # 1. Update Habit Weight (Behavior Matrix)
            if action not in self.behavior_matrix[context]:
                self.behavior_matrix[context][action] = 1.0
            self.behavior_matrix[context][action] += alpha * reward * value
            
            if intention not in self.behavior_matrix[context]:
                self.behavior_matrix[context][intention] = 1.0
            self.behavior_matrix[context][intention] += alpha * reward * value
            
            # Clamp habits
            self.behavior_matrix[context][action] = max(0.1, min(5.0, self.behavior_matrix[context][action]))
            self.behavior_matrix[context][intention] = max(0.1, min(5.0, self.behavior_matrix[context][intention]))

            # 2. Update Cognitive Traits (If traits dict is provided)
            if traits and intention in TRAIT_MAP:
                feedback_key = "positive" if reward > 0 else "negative"
                target_traits = TRAIT_MAP[intention].get(feedback_key, [])
                for trait_name, sign in target_traits:
                    if trait_name in traits:
                        old_val = traits[trait_name]
                        # ΔT = (α/5) * reward * trace_value * sign
                        shift = trait_alpha * abs(reward) * value * sign
                        traits[trait_name] = max(-1.0, min(1.0, traits[trait_name] + shift))
                        if abs(shift) > 0.01:
                            print(f"[LEARNING] {self.agent_id} trait {trait_name}: {old_val:.2f} -> {traits[trait_name]:.2f} (Goal: {intention}, Reward: {reward})")
            elif traits:
                print(f"[LEARNING] {self.agent_id} feedback received but intention '{intention}' not in TRAIT_MAP")

    def get_bias(self, context: str, action: str) -> float:
        return self.behavior_matrix.get(context, {}).get(action, 1.0)
