import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Creature

def test_phase13_social():
    world = GameWorld(width=10, height=10, seed=1337)
    journal = GlobalEventJournal("test_social", 1337)
    logic = GameLogic(world, journal)
    
    # 1. Setup two agents: Explorer and Listener
    explorer = Creature("Explorer", 1, 1)
    listener = Creature("Listener", 3, 3)
    logic.add_agent(explorer)
    logic.add_agent(listener)
    
    # 2. Explorer knows about food at (5, 5)
    explorer.ai.beliefs.known_locations[(5, 5)] = "food"
    
    print(f"Initial: Listener knows {len(listener.ai.beliefs.known_locations)} locations.")
    assert (5, 5) not in listener.ai.beliefs.known_locations
    
    # 3. Increase social drive for Explorer to seek Listener
    explorer.ai.drives.drives["social"] = 1.0
    explorer.ai.drives.drives["hunger"] = 0.0 # Don't wander for food
    
    # 4. Run simulation until they meet and share
    shared = False
    for i in range(50):
        logic.update()
        if (5, 5) in listener.ai.beliefs.known_locations:
            print(f"Tick {i}: Knowledge successfully shared!")
            shared = True
            break
        
        if i % 10 == 0:
            print(f"Tick {i}: Explorer at ({explorer.x}, {explorer.y}), Listener at ({listener.x}, {listener.y})")
    
    assert shared, "Knowledge was NOT shared between agents!"
    print("Social Knowledge Sharing Test Passed!")

if __name__ == "__main__":
    test_phase13_social()
