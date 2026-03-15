import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.learning import LearningSystem

def test_reinforcement_fixes():
    ls = LearningSystem("test_agent")
    traits = {
        "compassion": 0.0,
        "gentleness": 0.0,
        "obedience": 0.0,
        "altruism": 0.0,
        "generosity": 0.0,
        "patience": 0.0,
        "empathy": 0.0,
        "diligence": 0.0,
        "cruelty": 0.0,
        "sadism": 0.0,
        "arrogance": 0.0,
        "aggression": 0.0
    }

    print("--- 1. Testing 'help' intention reinforcement ---")
    ls.record_action("plan_help", "help", "share_belief")
    ls.apply_feedback("plan_help", 1.0, traits)
    
    # Check if compassion and altruism increased
    if traits["compassion"] > 0 and traits["altruism"] > 0:
        print("SUCCESS: 'help' intention reinforced traits.")
    else:
        print(f"FAILURE: 'help' intention did not reinforce traits. Traits: {traits}")

    print("\n--- 2. Testing Multi-Plan Credit Assignment ---")
    # Record a new plan
    ls.record_action("plan_eat", "eat", "eat_food")
    
    # Reset traits for clean test
    for k in traits: traits[k] = 0.0
    
    # Apply feedback to 'plan_eat'
    ls.apply_feedback("plan_eat", 1.0, traits)
    
    print(f"Traits after multi-plan feedback: {traits}")
    if traits["compassion"] > 0 and traits["patience"] > 0:
        print("SUCCESS: Multi-plan credit assignment reinforced previous plan.")
    else:
        print("FAILURE: Multi-plan credit assignment failed.")

    print("\n--- 3. Testing DIABOLIC transition (Repeated Slaps) ---")
    # Reset traits
    for k in traits: traits[k] = 0.0

    # Slap multiple times while creature is 'idle'
    ls.record_action("plan_idle", "idle", "idle_action")
    for i in range(5):
        ls.apply_feedback("plan_idle", -1.0, traits)
    
    print(f"Traits after 5 slaps: {traits}")
    
    # Calculation for alignment in video.py:
    moral_traits = ["compassion", "generosity", "obedience", "gentleness", "diligence", "altruism", "empathy", "patience"]
    m_vals = [float(traits.get(t, 0.0)) for t in moral_traits]
    sig_vals = [v for v in m_vals if abs(v) > 0.05]
    avg_alignment = sum(sig_vals) / len(sig_vals) if sig_vals else (sum(m_vals) / len(m_vals))
    
    print(f"Average Alignment (Sensitive): {avg_alignment:.2f}")
    if avg_alignment < -0.15:
        print("SUCCESS: Creature turned DIABOLIC.")
    else:
        print("FAILURE: Creature did not turn DIABOLIC.")

if __name__ == "__main__":
    test_reinforcement_fixes()
