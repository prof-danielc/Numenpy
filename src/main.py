import pygame
import sys
import time
import json
from src.world import GameWorld
from src.logic import GameLogic
from src.video import GameVideo
from src.journal import GlobalEventJournal
from src.entities import Person, Creature
from src.camera import Camera
from src.map_loader import MapLoader

# Constants
FPS = 60 # Increased for smoothing
SIDEBAR_WIDTH = 300

def handle_inputs(camera, logic, journal, selected_agent, paused, debug_mode):
    running = True
    keys = pygame.key.get_pressed()
    
    # Camera Panning (Arrow Keys)
    move_speed = 0.5 / camera.zoom
    if keys[pygame.K_LEFT]: camera.target_x -= move_speed
    if keys[pygame.K_RIGHT]: camera.target_x += move_speed
    if keys[pygame.K_UP]: camera.target_y -= move_speed
    if keys[pygame.K_DOWN]: camera.target_y += move_speed
    
    # Camera Zoom (+/-)
    if keys[pygame.K_KP_PLUS] or keys[pygame.K_EQUALS]:
        camera.target_zoom = min(4.0, camera.target_zoom + 0.05)
    if keys[pygame.K_KP_MINUS] or keys[pygame.K_MINUS]:
        camera.target_zoom = max(0.1, camera.target_zoom - 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Convert screen to world for selection
            wx, wy = camera.screen_to_world(mx, my)
            # Efficiently pick entity using spatial index
            picked = logic.world.pick_entity(wx, wy, radius=0.8)
            if picked:
                selected_agent = picked
                journal.log("player", f"Selected {picked.agent_id} at {wx:.1f}, {wy:.1f}")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_d:
                debug_mode = not debug_mode

            # Target creature etc. (existing logic)
            target_creature = selected_agent if getattr(selected_agent, 'type', '') == 'creature' else None
            # ... (rest of slap/pet logic)
            if target_creature and not paused:
                if event.key == pygame.K_s: # Slap
                    target_creature.ai.learning.apply_feedback(target_creature.ai.planner.plan_id, -1.0, target_creature.ai.traits.traits)
                    journal.record_event("player_feedback", "player", {"type": "slap", "target": target_creature.agent_id})
                elif event.key == pygame.K_p: # Pet
                    target_creature.ai.learning.apply_feedback(target_creature.ai.planner.plan_id, 1.0, target_creature.ai.traits.traits)
                    journal.record_event("player_feedback", "player", {"type": "pet", "target": target_creature.agent_id})
        
    return running, selected_agent, paused, debug_mode

def main():
    pygame.init()
    
    # Session Settings
    world_seed = 1337
    session_id = f"session_{time.time()}"
    
    # Core Modules
    world = GameWorld(seed=world_seed)
    journal = GlobalEventJournal(session_id, world_seed)
    
    # Load generated island map
    map_path = "maps/island_map.json"
    spawns = MapLoader.load(map_path, world, journal)

    # Visualization
    sw, sh = 800, 600
    screen = pygame.display.set_mode((sw + SIDEBAR_WIDTH, sh))
    pygame.display.set_caption("Numenpy")
    
    camera = Camera(sw, sh)
    camera.set_map_bounds(world.width, world.height)
    camera.target_x, camera.target_y = world.width / 2, world.height / 2
    
    video = GameVideo(screen, world, camera)
    logic = GameLogic(world, journal)
    clock = pygame.time.Clock()
    
    # Spawn agents from map data
    for s in spawns:
        if s['type'] == 'person':
            a = Person(s['id'], s['x'], s['y'])
            logic.add_agent(a)
        elif s['type'] == 'creature':
            a = Creature(s['id'], s['x'], s['y'])
            logic.add_agent(a)
    
    running = True
    paused = False
    debug_mode = True
    selected_agent = logic.entities[0] #None

    while running:
        dt = clock.tick(FPS) / 1000.0 # Seconds
        
        # 1. Input
        running, selected_agent, paused, debug_mode = handle_inputs(camera, logic, journal, selected_agent, paused, debug_mode) 

        # 2. Process
        if not paused:
            logic.update()
        
        camera.update(dt * 10.0) # Smooth factor
        
        # 3. Output
        video.render(logic, selected_agent=selected_agent, debug_mode=debug_mode)
        
        if paused:
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            pause_font = pygame.font.SysFont("Arial", 64)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(sw // 2, sh // 2))
            screen.blit(pause_text, text_rect)
        
        pygame.display.flip()

    pygame.quit()
    journal.save_session(f"./journal_sessions/{session_id}.json")
    sys.exit()

if __name__ == "__main__":
    main()
