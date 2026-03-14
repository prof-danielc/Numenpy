import pygame
import sys
import time
import json
from world import GameWorld
from logic import GameLogic
from video import GameVideo
from journal import GlobalEventJournal
from entities import Person, Creature

# Constants
GRID_WIDTH = 40
GRID_HEIGHT = 30
FPS = 30

def handle_inputs(logic, journal, selected_agent, paused):
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx, gy = mx // 20, my // 20
            # Select agent at this tile
            selected_agent = next((e for e in logic.entities if e.x == gx and e.y == gy), None)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
                print("PAUSED" if paused else "RESUMED")

            # Target the selected creature or the first creature for feedback
            target_creature = selected_agent if getattr(selected_agent, 'type', '') == 'creature' else None
            if not target_creature:
                creatures = [e for e in logic.entities if getattr(e, 'type', '') == 'creature']
                if creatures: target_creature = creatures[0]
            
            if target_creature and not paused:
                if event.key == pygame.K_s: # Slap
                    print(f"SLAP! {target_creature.agent_id}")
                    target_creature.ai.learning.apply_feedback(target_creature.ai.planner.plan_id, -1.0)
                    journal.record_event("player_feedback", "player", {"type": "slap", "target": target_creature.agent_id})
                elif event.key == pygame.K_p: # Pet
                    print(f"PET! {target_creature.agent_id}")
                    target_creature.ai.learning.apply_feedback(target_creature.ai.planner.plan_id, 1.0)
                    journal.record_event("player_feedback", "player", {"type": "pet", "target": target_creature.agent_id})
        
    return running, selected_agent, paused

def main():
    # Parse Args
    replay_file = None
    if len(sys.argv) > 2 and sys.argv[1] == "--replay":
        replay_file = sys.argv[2]
        
    # Initial State
    pygame.init()
    
    # Session Settings
    if replay_file:
        with open(replay_file, 'r') as f:
            session_data = json.load(f)
        world_seed = session_data["world_seed"]
        session_id = session_data["session_id"] + "_replay"
    else:
        world_seed = 1337
        session_id = f"session_{time.time()}"
    
    # Core Modules
    world = GameWorld(GRID_WIDTH, GRID_HEIGHT, seed=world_seed)
    journal = GlobalEventJournal(session_id, world_seed)
    logic = GameLogic(world, journal)
    
    # Visualization
    SIDEBAR_WIDTH = 300
    screen = pygame.display.set_mode((GRID_WIDTH * 20 + SIDEBAR_WIDTH, GRID_HEIGHT * 20))
    pygame.display.set_caption("Numenpy Prototype")
    video = GameVideo(screen, world)
    clock = pygame.time.Clock()
    
    # Spawn initial agents
    vx, vy = world.find_random_land_tile()
    logic.add_agent(Person("villager_1", vx, vy))
    
    cx, cy = world.find_random_land_tile()
    logic.add_agent(Creature("creature_1", cx, cy))
    
    running = True
    paused = False
    selected_agent = None
    while running:
        # IPOS Loop
        
        # 1. Input
        running, selected_agent, paused = handle_inputs(logic, journal, selected_agent, paused) 

        # 2. Process
        if not paused:
            logic.update()
        
        # 3. Output
        video.render(logic, selected_agent=selected_agent)
        if paused:
            # Overlay pause text
            overlay = pygame.Surface((GRID_WIDTH * 20, GRID_HEIGHT * 20), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont("Arial", 48)
            text = font.render("PAUSED", True, (255, 255, 255))
            screen.blit(text, (GRID_WIDTH * 10 - 70, GRID_HEIGHT * 10 - 20))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    journal.save_session(f"./journal_sessions/{session_id}.json")
    sys.exit()

if __name__ == "__main__":
    main()
