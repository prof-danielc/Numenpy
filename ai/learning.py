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
        
        # FR-017: Multi-Plan Credit Assignment
        self.plan_history: List[str] = []
        self.max_plan_history = 5
        self.plan_decay_rate = 0.5 

    def record_action(self, plan_id: str, intention_id: str, action_tag: str):
        """Add action to eligibility trace for the specific plan."""
        if plan_id not in self.eligibility_traces:
            self.eligibility_traces[plan_id] = []
            # Manage plan history
            if plan_id not in self.plan_history:
                self.plan_history.append(plan_id)
                if len(self.plan_history) > self.max_plan_history:
                    old_plan = self.plan_history.pop(0)
                    self.eligibility_traces.pop(old_plan, None)
        
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
        """Apply reward/punishment to actions and intentions in recent plans."""
        # 0. Global Trait Shift (Alignment always moves for pets/slaps)
        if traits:
            global_alpha = 0.05
            feedback_sign = 1.0 if reward > 0 else -1.0
            # Affect all core moral traits globally to ensure alignment moves
            moral_traits = ["compassion", "gentleness", "obedience", "altruism", "generosity", "patience", "empathy", "diligence"]
            for t_name in moral_traits:
                if t_name in traits:
                    traits[t_name] = max(-1.0, min(1.0, traits[t_name] + global_alpha * feedback_sign))

        # Handle missing plan_id (fallback to most recent)
        target_plans = []
        if plan_id and plan_id in self.plan_history:
            # Multi-plan credit assignment: Reward propagates backwards
            idx = self.plan_history.index(plan_id)
            for i in range(idx, -1, -1):
                p_id = self.plan_history[i]
                weight = self.plan_decay_rate ** (idx - i)
                target_plans.append((p_id, reward * weight))
        elif self.plan_history:
            # If current plan_id is unknown, reward the most recent one
            target_plans = [(self.plan_history[-1], reward)]
        else:
            return # No context to apply feedback to
            
        # Intention-Specific Feedback Map (Good: +, Evil: -)
        TRAIT_MAP = {
            "hunt": {"positive": [("gentleness", -1.0), ("patience", -0.5), ("compassion", -1.0)], "negative": [("gentleness", 0.5), ("compassion", 0.5)]},
            "socialize": {"positive": [("compassion", 1.0), ("empathy", 1.0)], "negative": [("patience", -1.0), ("obedience", -1.0)]},
            "eat": {"positive": [("patience", 1.0), ("obedience", 1.0)], "negative": [("generosity", -1.0), ("gluttony", 1.0)]},
            "explore": {"positive": [("curiosity", 1.0), ("focus", 1.0)], "negative": [("fearfulness", 1.0)]},
            "work": {"positive": [("diligence", 1.0), ("altruism", 1.0)], "negative": [("diligence", -1.0), ("altruism", -1.0)]},
            "help": {"positive": [("compassion", 1.0), ("altruism", 1.0)], "negative": [("sadism", 1.0), ("cruelty", 1.0)]},
            "idle": {"positive": [("patience", 1.0), ("gentleness", 1.0)], "negative": [("arrogance", 1.0), ("aggression", 1.0)]},
            "unknown": {"positive": [("patience", 0.5), ("gentleness", 0.5)], "negative": [("arrogance", 0.5), ("aggression", 0.5)]}
        }

        alpha = 0.5 # Learning rate for habits
        trait_alpha = alpha / 2.0 # traits shift slightly slower
        context = "default"
        if context not in self.behavior_matrix:
            self.behavior_matrix[context] = {}

        for p_id, current_reward in target_plans:
            if p_id not in self.eligibility_traces: continue
            traces = self.eligibility_traces[p_id]
            
            for trace in traces:
                action = trace["action"]
                intention = trace["intention"]
                value = trace["value"]
                
                # 1. Update Habit Weight (Behavior Matrix)
                if action not in self.behavior_matrix[context]:
                    self.behavior_matrix[context][action] = 1.0
                self.behavior_matrix[context][action] += alpha * current_reward * value
                
                if intention not in self.behavior_matrix[context]:
                    self.behavior_matrix[context][intention] = 1.0
                self.behavior_matrix[context][intention] += alpha * current_reward * value
                
                # Clamp habits
                self.behavior_matrix[context][action] = max(0.1, min(5.0, self.behavior_matrix[context][action]))
                self.behavior_matrix[context][intention] = max(0.1, min(5.0, self.behavior_matrix[context][intention]))

                # 2. Update Cognitive Traits
                if traits and intention in TRAIT_MAP:
                    feedback_key = "positive" if current_reward > 0 else "negative"
                    target_traits = TRAIT_MAP[intention].get(feedback_key, [])
                    for trait_name, sign in target_traits:
                        if trait_name in traits:
                            old_val = traits[trait_name]
                            shift = trait_alpha * abs(current_reward) * value * sign
                            traits[trait_name] = max(-1.0, min(1.0, traits[trait_name] + shift))
                            if abs(shift) > 0.01:
                                print(f"[LEARNING] {self.agent_id} trait {trait_name}: {old_val:.2f} -> {traits[trait_name]:.2f} (Goal: {intention}, Reward: {current_reward:.2f})")
                elif traits:
                    # Log missing intention only if it's the primary reward (not decayed)
                    if current_reward == reward:
                        print(f"[LEARNING] {self.agent_id} feedback received but intention '{intention}' not in TRAIT_MAP")

    def get_bias(self, context: str, action: str) -> float:
        return self.behavior_matrix.get(context, {}).get(action, 1.0)
