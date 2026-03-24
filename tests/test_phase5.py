import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Creature

def test_phase5():
    # 1. Setup
    world = GameWorld(20, 20)
    journal = GlobalEventJournal()
    logic = GameLogic(world, journal)
    
    c1 = Creature("c1", 10, 10)
    logic.add_agent(c1)
    
    # Force a plan
    world.resources = [(11, 11, "food")]
    c1.ai.drives.drives["hunger"] = 1.0
    logic.update() # Creature should plan 'eat' and record first step
    
    plan_id = c1.ai.planner.plan_id
    print(f"Active Plan: {plan_id}")
    
    # 2. Verify Eligibility Trace
    if plan_id not in c1.ai.learning.eligibility_traces:
        print("FAILED: Action not recorded in eligibility traces")
        exit(1)
    
    initial_weight = c1.ai.learning.get_bias("default", "eat")
    print(f"Initial 'eat' weight: {initial_weight}")
    
    # 3. Apply Punish
    print("Applying SLAP...")
    c1.ai.learning.apply_feedback(plan_id, -1.0)
    
    new_weight = c1.ai.learning.get_bias("default", "eat")
    print(f"New 'eat' weight: {new_weight}")
    
    if new_weight < initial_weight:
        print("PASSED: Reward/Punish correctly modified weights")
    else:
        print("FAILED: Weight did not decrease after punishment")
        exit(1)

if __name__ == "__main__":
    test_phase5()
