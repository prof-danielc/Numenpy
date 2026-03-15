import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.ai_systems import BeliefSystem, DriveSystem, TraitSystem, DesireSystem, IntentionSystem
from ai.learning import LearningSystem

def test_angelic_behavior_repro():
    print("--- Repro: Angelic Predator Behavior ---")
    
    # 1. Setup an "Angelic" agent
    traits = {
        "compassion": 1.0,
        "gentleness": 1.0,
        "altruism": 1.0,
        "curiosity": 0.5
    }
    
    ls = LearningSystem("angelic_creature")
    beliefs = BeliefSystem()
    drives = DriveSystem()
    desires_sys = DesireSystem()
    
    # Fake some beliefs: visible villager
    beliefs.known_agents = [{"id": "villager_1", "type": "person", "x": 10, "y": 10}]
    
    # Set high hunger to trigger hunt
    drives.drives["hunger"] = 0.8
    
    # 2. Evaluate desires
    desires = desires_sys.evaluate(drives.drives, traits, ls, "creature", beliefs)
    
    print("\nDesires for 'Angelic' agent with 0.8 hunger:")
    for d in desires:
        print(f"Goal: {d['goal']}, Utility: {d['utility']:.4f}")
        
    hunt_desire = next((d for d in desires if d["goal"] == "hunt"), None)
    help_desire = next((d for d in desires if d["goal"] == "help"), None)
    
    if hunt_desire and help_desire and hunt_desire["utility"] > help_desire["utility"]:
        print("\nISSUE REPRODUCED: 'hunt' utility is higher than 'help' even for 1.0 gentleness/compassion.")
    else:
        print("\nISSUE NOT REPRODUCED in utility calculation.")

    # 3. Test Learning logic (Backwards TRAIT_MAP)
    print("\n--- Repro: Backwards TRAIT_MAP ---")
    # Reset traits to mid-range
    test_traits = {"gentleness": 0.5, "patience": 0.5, "compassion": 0.5, "altruism": 0.5}
    ls.record_action("plan_hunt", "hunt", "kill_villager")
    
    print(f"Traits before rewarding 'hunt': {test_traits}")
    ls.apply_feedback("plan_hunt", 2.0, test_traits)
    print(f"Traits after rewarding 'hunt': {test_traits}")
    
    if test_traits["gentleness"] < 0.5:
        print(f"SUCCESS: Rewarding 'hunt' decreased 'gentleness' to {test_traits['gentleness']:.2f}")
    else:
        print(f"FAILURE: Rewarding 'hunt' did not decrease 'gentleness'! Value: {test_traits['gentleness']:.2f}")

    if test_traits["compassion"] < 0.5:
        print(f"SUCCESS: Rewarding 'hunt' decreased 'compassion' to {test_traits['compassion']:.2f}")
    else:
        print(f"FAILURE: Rewarding 'hunt' did not decrease 'compassion'! Value: {test_traits['compassion']:.2f}")

if __name__ == "__main__":
    test_angelic_behavior_repro()
