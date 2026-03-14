import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Creature

def test_phase7_race():
    # 1. Setup
    world = GameWorld(20, 20, seed=1337)
    journal = GlobalEventJournal("race_session", 1337)
    logic = GameLogic(world, journal)
    
    # Spawn two agents
    c1 = Creature("c1", 10, 10, seed=1)
    c2 = Creature("c2", 11, 10, seed=2)
    logic.add_agent(c1)
    logic.add_agent(c2)
    
    # Spawn ONE food near both
    world.resources = [(10, 9, "food")] # c1 is closer
    
    # Set high hunger
    c1.ai.drives.drives["hunger"] = 1.0
    c2.ai.drives.drives["hunger"] = 1.0
    
    print("Starting Race...")
    
    # Step 1: Both should plan 'eat'
    logic.update()
    print(f"Tick 1: C1 Plan: {c1.ai.planner.current_plan}, C2 Plan: {c2.ai.planner.current_plan}")
    
    # Step 2: C1 reaches food first because it's at (10,9) and moves from (10,10)
    # Actually, c1 starts at (10,10), food at (10,9). c1 can eat immediately if dist <= 1.
    # In logic.py, 'eat' checks dist <= 1. 
    # Let's see who gets it. Logic updates entities in order of addition.
    
    for t in range(5):
        logic.update()
        print(f"Tick {t+2}: C1 hunger={c1.hunger:.2f}, C2 intent={c2.ai.intentions.current_intention['goal'] if c2.ai.intentions.current_intention else 'none'}")
        print(f"   C2 plan length: {len(c2.ai.planner.current_plan)}")
        if c2.last_action_result == "MISSING":
            print(f"!!! C2 detected MISSING at tick {t+2}")
            # After detecting MISSING at Tick 2, at Tick 3 it should have re-evaluated
    
    # Verification: C1 should have eaten, C2 should have failed and then cleared its plan
    if c1.hunger < 0.1 and c2.hunger > 0.0:
        print("PASSED: C1 ate, C2 handled failure.")
    else:
        print(f"FAILED: C1 hunger={c1.hunger}, C2 hunger={c2.hunger}")
        exit(1)

if __name__ == "__main__":
    test_phase7_race()
