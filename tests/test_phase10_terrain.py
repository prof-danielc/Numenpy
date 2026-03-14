import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Person

def test_phase10_terrain():
    # 1. Setup
    world = GameWorld(10, 10, seed=1337)
    journal = GlobalEventJournal("terrain_session", 1337)
    logic = GameLogic(world, journal)
    
    # 2. Add an agent
    agent = Person("hiker", 0, 0)
    logic.add_agent(agent)
    
    # Check initial values
    start_hunger = agent.ai.drives.drives["hunger"]
    print(f"Start Hunger: {start_hunger:.4f}")
    
    # 3. Force predictable elevation
    world.elevation[0][0] = 0.0
    world.elevation[1][0] = 0.9 # x=0, y=1
    
    print(f"Start (0,0) elevation: {world.get_elevation(0,0)}")
    print(f"Target (0,1) elevation: {world.get_elevation(0,1)}")
    
    print("Moving from (0,0) to (0,1)")
    logic._execute_action(agent, [("move", (0, 1))])
    
    end_hunger = agent.ai.drives.drives["hunger"]
    print(f"End Hunger: {end_hunger:.4f}")
    
    diff = end_hunger - start_hunger
    print(f"Hunger increase: {diff:.4f}")
    
    # Verify cost was applied (0.005 * (1.0 + 0.9*5) = 0.005 * 5.5 = 0.0275)
    # Default update in entities.py also adds 0.01 per tick
    if diff > 0.02:
        print("PASSED: Movement cost applied correctly.")
    else:
        print(f"FAILED: Movement cost too low ({diff}).")
        exit(1)

if __name__ == "__main__":
    test_phase10_terrain()
