import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Creature

def test_phase8_social():
    # 1. Setup
    world = GameWorld(20, 20, seed=1337)
    journal = GlobalEventJournal("social_session", 1337)
    logic = GameLogic(world, journal)
    
    # c1 knows where food is but isn't hungry. c2 is hungry but doesn't know where food is.
    c1 = Creature("c1", 10, 10, seed=1)
    c2 = Creature("c2", 12, 10, seed=2)
    logic.add_agent(c1)
    logic.add_agent(c2)
    
    # Food is far away from both
    world.resources = [(1, 1, "food")]
    
    # c1 knows it
    c1.ai.beliefs.known_locations[(1, 1)] = "food"
    
    # c1 is compassionate
    c1.ai.traits.traits["compassion"] = 1.0
    c1.ai.drives.drives["social"] = 0.0 # not lonely
    
    # c2 is hungry
    c2.ai.drives.drives["hunger"] = 1.0
    
    print("Starting Social Test...")
    
    # Tick 1: c1 should decide to 'help' c2, c2 should plan to 'explore' or 'socialize'
    logic.update()
    print(f"Tick 1: C1 Plan: {c1.ai.planner.current_plan}")
    print(f"Tick 1: C2 Beliefs: {c2.ai.beliefs.known_locations}")
    
    # Run a few ticks
    for t in range(5):
        logic.update()
        print(f"Tick {t+2}: C1 Intent: {c1.ai.intentions.current_intention['goal'] if c1.ai.intentions.current_intention else 'none'}")
        print(f"Tick {t+2}: C2 Beliefs: {c2.ai.beliefs.known_locations}")
        if (1, 1) in c2.ai.beliefs.known_locations:
            print("!!! C2 learned food location from C1!")
            break
            
    # Final Verification
    if (1, 1) in c2.ai.beliefs.known_locations:
        print("PASSED: Social knowledge transfer successful.")
    else:
        print("FAILED: No knowledge transfer.")
        exit(1)

if __name__ == "__main__":
    test_phase8_social()
