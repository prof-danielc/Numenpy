import pygame
import numpy as np
from src.camera import Camera
from src.chunk import Chunk

class GameVideo:
    def __init__(self, screen, world, camera: Camera):
        self.screen = screen
        self.world = world
        self.camera = camera
        
        # Internal colors (can be moved to a palette later)
        self.COLORS = {
            "grass": (34, 139, 34),
            "water": (30, 144, 255),
            "mountain": (139, 137, 137),
            "agent": (255, 69, 0),
            "creature": (255, 215, 0),
            "resource": (255, 0, 255),
        }
        self.font_small = pygame.font.SysFont("Arial", 12)
        self.font_med = pygame.font.SysFont("Arial", 16)

    def render(self, logic, selected_agent=None, debug_mode=False):
        self.screen.fill((20, 20, 25)) # Background
        
        # 1. Viewport Culling: Get visible chunks
        min_cx, max_cx, min_cy, max_cy = self.camera.get_visible_chunk_range(Chunk.CHUNK_SIZE)
        
        # 2. Render Visible Chunks
        tile_size_scaled = int(self.camera.tile_size * self.camera.zoom)
        
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                chunk = self.world.get_chunk(cx, cy, create=False)
                if chunk:
                    self._render_chunk(chunk, tile_size_scaled, debug_mode)

        # 3. Render Resources
        visible_resources = self.world.query_rect(*self.camera.get_world_bounds(Chunk.CHUNK_SIZE))
        for rx, ry, rtype in visible_resources:
            sx, sy = self.camera.world_to_screen(rx, ry)
            color = self.COLORS.get("resource", (255, 0, 255))
            if rtype == "remains": color = (150, 50, 50)
            pygame.draw.circle(self.screen, color, (int(sx + tile_size_scaled//2), int(sy + tile_size_scaled//2)), max(2, tile_size_scaled // 4))

        # 4. Render Entities
        for entity in logic.entities:
            sx, sy = self.camera.world_to_screen(entity.x, entity.y)
            if -50 < sx < self.screen.get_width() + 50 and -50 < sy < self.screen.get_height() + 50:
                self._render_entity(entity, sx, sy, tile_size_scaled, selected_agent == entity)
                
                # Floating intention labels
                if debug_mode and hasattr(entity, 'ai'):
                    intention = entity.ai.intentions.current_intention
                    if intention:
                        label = self.font_small.render(str(intention["goal"]).upper(), True, (255, 255, 0))
                        self.screen.blit(label, (sx, sy - 15))

        # 5. Selected Agent Visuals (Paths/Targets)
        if selected_agent and hasattr(selected_agent, 'ai'):
            plan = selected_agent.ai.planner.current_plan
            if plan:
                # Draw path lines
                points = [(selected_agent.x, selected_agent.y)]
                for action, target in plan:
                    if action == "move" and isinstance(target, (tuple, list)):
                        points.append(target)
                
                if len(points) > 1:
                    screen_points = [self.camera.world_to_screen(p[0], p[1]) for p in points]
                    screen_points = [(p[0] + tile_size_scaled//2, p[1] + tile_size_scaled//2) for p in screen_points]
                    pygame.draw.lines(self.screen, (255, 255, 0), False, screen_points, 2)
                    
                # Draw target destination
                last_action, last_target = plan[-1]
                tx, ty = None, None
                
                if last_action in ["move", "eat", "eat_villager"] and isinstance(last_target, (tuple, list)) and len(last_target) == 2:
                    tx, ty = last_target
                elif last_action == "share_belief" and isinstance(last_target, (tuple, list)) and len(last_target) == 3:
                    # Target is (agent_id, (x, y), type)
                    loc = last_target[1]
                    if isinstance(loc, (tuple, list)) and len(loc) == 2:
                        tx, ty = loc
                
                if tx is not None and ty is not None:
                    # Ensure tx/ty are numbers, not tuples (extra safety)
                    if isinstance(tx, (int, float)) and isinstance(ty, (int, float)):
                        tsx, tsy = self.camera.world_to_screen(tx, ty)
                        pygame.draw.circle(self.screen, (255, 0, 0), (int(tsx + tile_size_scaled//2), int(tsy + tile_size_scaled//2)), int(tile_size_scaled * 0.6), 2)

        # 6. Global HUD
        tick_label = self.font_small.render(f"SIM TICK: {logic.tick_count}", True, (200, 200, 200))
        self.screen.blit(tick_label, (10, 10))

        # 7. Debug Overlays (Chunk Grid)
        if debug_mode:
            self._render_debug_grid(min_cx, max_cx, min_cy, max_cy)

        # 8. Brain Monitor Sidebar
        if selected_agent:
            # We assume sw (main game area) is screen_width - 300
            start_x = self.screen.get_width() - 300
            self._draw_brain_monitor(selected_agent, start_x, logic.tick_count)

    def _draw_brain_monitor(self, agent, start_x, tick):
        # Background
        sidebar_rect = pygame.Rect(start_x, 0, 300, self.screen.get_height())
        pygame.draw.rect(self.screen, (40, 40, 45), sidebar_rect)
        pygame.draw.line(self.screen, (100, 100, 100), (start_x, 0), (start_x, self.screen.get_height()), 2)
        
        y = 10
        # Tick counter (verification)
        tick_text = self.font_small.render(f"SIM TICK: {tick}", True, (100, 100, 100))
        self.screen.blit(tick_text, (start_x + 200, y))
        y = 20
        
        # Header
        title = self.font_med.render(f"BRAIN: {agent.agent_id} ({getattr(agent, 'type', 'unknown')})", True, (255, 255, 255))
        self.screen.blit(title, (start_x + 10, y))
        y += 40

        if not hasattr(agent, 'ai'):
            self.screen.blit(self.font_med.render("NO AI CORE", True, (255, 100, 100)), (start_x + 10, y))
            return

        # Drives
        self.screen.blit(self.font_med.render("DRIVES:", True, (200, 200, 255)), (start_x + 10, y))
        y += 25
        for drive, val in agent.ai.drives.drives.items():
            # Label
            self.screen.blit(self.font_med.render(f"{drive}:", True, (255, 255, 255)), (start_x + 20, y))
            # Bar
            pygame.draw.rect(self.screen, (60, 60, 60), (start_x + 100, y + 4, 150, 10))
            pygame.draw.rect(self.screen, (100, 255, 100), (start_x + 100, y + 4, int(val * 150), 10))
            y += 20
        
        # Physical Attributes (Health/Energy)
        self.screen.blit(self.font_med.render("ENERGY:", True, (255, 255, 255)), (start_x + 20, y))
        pygame.draw.rect(self.screen, (60, 60, 60), (start_x + 100, y + 4, 150, 10))
        pygame.draw.rect(self.screen, (255, 100, 100), (start_x + 100, y + 4, int(agent.energy * 150), 10))
        y += 30

        # Desires & Intention
        self.screen.blit(self.font_med.render("INTENTION:", True, (200, 255, 200)), (start_x + 10, y))
        y += 25
        intent = agent.ai.intentions.current_intention
        intent_str = f"{intent['goal']} (u={intent['utility']:.2f})" if intent else "none"
        self.screen.blit(self.font_med.render(intent_str, True, (255, 255, 100)), (start_x + 20, y))
        y += 30

        # Plan
        plan_len = len(agent.ai.planner.current_plan)
        self.screen.blit(self.font_med.render(f"PLAN STEPS: {plan_len}", True, (255, 255, 255)), (start_x + 10, y))
        y += 40

        # Moral Alignment Summary
        moral_traits = ["compassion", "generosity", "obedience", "gentleness", "diligence", "altruism", "empathy", "patience"]
        m_vals = [float(agent.ai.traits.traits.get(t, 0.0)) for t in moral_traits]
        
        sig_vals = [v for v in m_vals if abs(v) > 0.05]
        avg_alignment = sum(sig_vals) / len(sig_vals) if sig_vals else (sum(m_vals) / len(m_vals))
        
        align_str = "ANGELIC" if avg_alignment > 0.15 else "DIABOLIC" if avg_alignment < -0.15 else "NEUTRAL"
        align_color = (100, 255, 100) if align_str == "ANGELIC" else (255, 100, 100) if align_str == "DIABOLIC" else (255, 255, 200)
        self.screen.blit(self.font_med.render(f"ALIGNMENT: {align_str} ({avg_alignment:.2f})", True, align_color), (start_x + 10, y))
        y += 28

        # Traits (Personal Variance) - 4 Columns for density
        self.screen.blit(self.font_med.render("TRAITS (Cognitive Core):", True, (255, 200, 100)), (start_x + 10, y))
        y += 22
        t_dash = {k: v for k, v in agent.ai.traits.traits.items() if isinstance(v, (int, float))}
        t_items = list(t_dash.items())
        for i in range(0, len(t_items), 4):
            for j in range(4):
                if i + j < len(t_items):
                    k, v = t_items[i+j]
                    col_x = start_x + 10 + (j * 72)
                    v_num = float(v)
                    label = self.font_small.render(f"{k[:4]}:{v_num:.1f}", True, (200, 200, 200))
                    self.screen.blit(label, (col_x, y))
            y += 16
        y += 10

        # Learning Biases (if creature)
        if hasattr(agent, 'ai') and hasattr(agent.ai, 'learning') and agent.ai.learning.behavior_matrix:
            self.screen.blit(self.font_med.render("HABITS (Learning Biases):", True, (255, 200, 200)), (start_x + 10, y))
            y += 22
            raw_biases = agent.ai.learning.behavior_matrix.get("default", {})
            bias_items = list(raw_biases.items())
            for i in range(0, min(8, len(bias_items)), 2):
                for j in range(2):
                    if i + j < len(bias_items):
                        goal, bias = bias_items[i+j]
                        b_val = float(bias)
                        col_x = start_x + 15 + (j * 140)
                        label = self.font_small.render(f"{goal[:12]}: {b_val:.2f}", True, (255, 255, 255))
                        self.screen.blit(label, (col_x, y))
                y += 18

    def _render_chunk(self, chunk: Chunk, tile_size_scaled: int, debug_mode: bool):
        CS = Chunk.CHUNK_SIZE
        for ty in range(CS):
            for tx in range(CS):
                tile_id = chunk.tiles[ty, tx]
                if tile_id == 0: continue # Skip void
                
                wx, wy = chunk.cx * CS + tx, chunk.cy * CS + ty
                sx, sy = self.camera.world_to_screen(wx, wy)
                
                # Check if tile is on screen
                if -tile_size_scaled < sx < self.screen.get_width() and \
                   -tile_size_scaled < sy < self.screen.get_height():
                    
                    # Get color from palette
                    tile_spec = self.world.tile_definitions.get(tile_id, {})
                    color = tile_spec.get('color', (100, 100, 100))
                    
                    # Dynamic rect to eliminate sub-pixel gaps (cracks)
                    nx, ny = self.camera.world_to_screen(wx + 1, wy + 1)
                    tw, th = max(1, nx - sx), max(1, ny - sy)
                    rect = pygame.Rect(sx, sy, tw, th)
                    
                    pygame.draw.rect(self.screen, color, rect)
                    
                    if debug_mode:
                        # Show tile outlines in debug mode
                        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

                    if debug_mode and tx == 0 and ty == 0:
                        # Draw chunk coordinate
                        label = self.font_small.render(f"C:{chunk.cx},{chunk.cy}", True, (255, 255, 255))
                        self.screen.blit(label, (sx + 2, sy + 2))

    def _render_entity(self, entity, sx, sy, size, is_selected):
        color = self.COLORS.get(getattr(entity, 'type', 'agent'), self.COLORS['agent'])
        
        # Adjust size for zoom
        e_size = max(4, int(size * 0.8))
        rect = pygame.Rect(sx + (size - e_size)//2, sy + (size - e_size)//2, e_size, e_size)
        
        if is_selected:
            pygame.draw.rect(self.screen, (255, 255, 255), rect.inflate(4, 4), 2)
            
        pygame.draw.rect(self.screen, color, rect)

    def _render_debug_grid(self, min_cx, max_cx, min_cy, max_cy):
        CS = Chunk.CHUNK_SIZE
        for cy in range(min_cy, max_cy + 2):
            # Horizontal lines
            wx, wy = min_cx * CS, cy * CS
            sx1, sy1 = self.camera.world_to_screen(wx, wy)
            sx2, sy2 = self.camera.world_to_screen((max_cx + 1) * CS, wy)
            pygame.draw.line(self.screen, (255, 0, 0, 100), (sx1, sy1), (sx2, sy2), 1)
            
        for cx in range(min_cx, max_cx + 2):
            # Vertical lines
            wx, wy = cx * CS, min_cy * CS
            sx1, sy1 = self.camera.world_to_screen(wx, wy)
            sx2, sy2 = self.camera.world_to_screen(wx, (max_cy + 1) * CS)
            pygame.draw.line(self.screen, (255, 0, 0, 100), (sx1, sy1), (sx2, sy2), 1)
