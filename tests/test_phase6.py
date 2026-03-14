import os
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Creature

def run_sim(seed, ticks, journal_path):
    world = GameWorld(20, 20, seed=seed)
    journal = GlobalEventJournal("test_session", seed)
    logic = GameLogic(world, journal)
    c1 = Creature("c1", 10, 10, seed=seed) # Assume AgentAI also takes seed
    logic.add_agent(c1)
    
    world.resources = [(11, 11, "food")]
    c1.ai.drives.drives["hunger"] = 1.0
    
    states = []
    for _ in range(ticks):
        logic.update()
        states.append((c1.x, c1.y))
        
    journal.save_session(journal_path)
    return states

def test_causal_replay():
    seed = 1234
    ticks = 10
    path = "replay_test.json"
    
    print("Running initial simulation...")
    original_states = run_sim(seed, ticks, path)
    
    print("Running replay simulation...")
    # For replay, we just need to ensure the SAME seed results in SAME outcomes
    # Full causal replay would involve loading external events (slaps), but here we test determinism
    replay_states = run_sim(seed, ticks, "replay_check.json")
    
    if original_states == replay_states:
        print("PASSED: Simulations are deterministic and identical.")
    else:
        print("FAILED: Simulations diverged!")
        for i, (s1, s2) in enumerate(zip(original_states, replay_states)):
            if s1 != s2:
                print(f"Divergence at tick {i}: {s1} != {s2}")
                break
        exit(1)

if __name__ == "__main__":
    test_causal_replay()
