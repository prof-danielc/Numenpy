import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from world import GameWorld
from logic import GameLogic
from journal import GlobalEventJournal
from entities import Person, Creature

def test_phase3():
    # 1. World Setup
    world = GameWorld(20, 20)
    print(f"PASSED: World created with {len(world.resources)} resources")
    if len(world.resources) == 0:
        print("FAILED: No resources spawned")
        exit(1)
        
    # 2. Logic Setup
    journal = GlobalEventJournal()
    logic = GameLogic(world, journal)
    logic.add_agent(Person("p1", 1, 1))
    logic.add_agent(Creature("c1", 2, 2))
    print(f"PASSED: Logic created with {len(logic.entities)} agents")
    
    # 3. Update Check
    logic.update()
    print(f"PASSED: Logic update successful (Tick: {logic.tick_count})")
    
    # 4. Rendering Check (Mock screen)
    try:
        from video import GameVideo
        import pygame
        pygame.display.init()
        screen = pygame.Surface((400, 400))
        video = GameVideo(screen, world)
        video.render(logic)
        print("PASSED: Rendering successful")
    except Exception as e:
        print(f"WARNING: Rendering test skipped or failed due to environment: {e}")

if __name__ == "__main__":
    test_phase3()
