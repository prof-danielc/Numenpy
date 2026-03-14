import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Creature

def test_phase4():
    # 1. Setup
    world = GameWorld(20, 20)
    journal = GlobalEventJournal()
    logic = GameLogic(world, journal)
    
    # 2. Add Creature
    c1 = Creature("c1", 10, 10)
    logic.add_agent(c1)
    
    # Ensure food is nearby for the test
    world.resources = [(11, 11, "food")]
    
    # 3. Simulate Ticks
    print("Simulating cognitive cycle...")
    for i in range(20):
        # Force high hunger to trigger 'eat' goal
        c1.ai.drives.drives["hunger"] = 1.0
        
        logic.update()
        
        last_event = journal.get_recent_events(1)[0] if journal.events else None
        print(f"Tick {i}: Pos({c1.x}, {c1.y}) | Goal: {c1.ai.intentions.current_intention['goal'] if c1.ai.intentions.current_intention else 'None'} | Last Event: {last_event['event_type'] if last_event else 'None'} ({last_event['data'].get('result') if last_event else ''})")
        
        if c1.hunger < 0.1 and i > 0:
            print("PASSED: Creature successfully found and ate food.")
            return

    print("FAILED: Creature did not eat food within 20 ticks.")
    exit(1)

if __name__ == "__main__":
    test_phase4()
