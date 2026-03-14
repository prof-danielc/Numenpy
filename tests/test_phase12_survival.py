import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Creature

def test_phase12_survival():
    world = GameWorld(width=10, height=10)
    journal = GlobalEventJournal("test_survival", 1337)
    logic = GameLogic(world, journal)
    
    # 1. Spawn agent in a sterile world (no food)
    world.resources = []
    agent = Creature("Starver", 0, 0)
    logic.add_agent(agent)
    
    print(f"Starting survival test for {agent.agent_id}")
    
    # Run simulation for 200 ticks (Death should occur around tick 145)
    for i in range(200):
        logic.update() # Logic.update now manages entities internally
        
        # Check if agent still alive
        if not logic.entities:
            print(f"Tick {i}: Agent has perished.")
            break
            
        if i % 20 == 0:
            a = logic.entities[0]
            print(f"Tick {i}: Hunger={a.hunger:.2f}, Energy={a.energy:.2f}")
    
    assert not logic.entities, "Agent should have died after 120 ticks of starvation!"
    print("Survival Test Passed: Agent died as expected.")

    # 2. Test Regeneration
    print("Testing Resource Regeneration...")
    world.resources = []
    # Ensure there is at least one grass tile
    world.terrain_type[0][0] = "grass"
    # Force 100% chance for testing
    world.regenerate_resources(chance=1.0)
    assert len(world.resources) > 0, "Resource regeneration failed! No food regrown on grass."
    print(f"PASSED: Regenerated {len(world.resources)} resources.")

if __name__ == "__main__":
    test_phase12_survival()
