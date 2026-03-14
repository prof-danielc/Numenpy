import pygame

class GameVideo:
    def __init__(self, screen, world):
        self.screen = screen
        self.world = world
        self.tile_size = 20 # pixels per grid cell
        
        # Colors
        self.COLORS = {
            "grass": (34, 139, 34),
            "water": (30, 144, 255),
            "obstacle": (105, 105, 105),
            "agent": (255, 69, 0),
            "creature": (255, 215, 0),
            "resource": (255, 0, 255),
            "mountain": (139, 137, 137)
        }
        self.font_small = pygame.font.SysFont("Arial", 14)
        self.font_med = pygame.font.SysFont("Arial", 16)
        self.font_header = pygame.font.SysFont("Arial", 20, bold=True)

    def render(self, logic, selected_agent=None, debug_mode=False):
        # 1. Render World
        world_width_px = self.world.width * self.tile_size
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, world_width_px, self.screen.get_height()))

        for y in range(self.world.height):
            for x in range(self.world.width):
                ttype = self.world.terrain_type[y][x]
                base_color = self.COLORS.get(ttype, self.COLORS["grass"])
                
                # Elevation shading (darker = lower, brighter = higher)
                h = self.world.elevation[y][x]
                color = tuple(max(0, min(255, int(c * (0.8 + h * 0.4)))) for c in base_color)
                
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, color, rect)

        # 2. Render Resources
        for rx, ry, rtype in self.world.resources:
            rect = pygame.Rect(rx * self.tile_size, ry * self.tile_size, self.tile_size, self.tile_size)
            pygame.draw.circle(self.screen, self.COLORS["resource"], rect.center, self.tile_size // 3)

        # 3. Render Agents
        for agent in logic.entities:
            color = self.COLORS["agent"]
            if hasattr(agent, 'type') and agent.type == "creature":
                color = self.COLORS["creature"]
            
            # Selection highlight
            if agent == selected_agent:
                pygame.draw.rect(self.screen, (255, 255, 255), (agent.x * self.tile_size - 2, agent.y * self.tile_size - 2, self.tile_size + 4, self.tile_size + 4), 2)

            rect = pygame.Rect(agent.x * self.tile_size, agent.y * self.tile_size, self.tile_size, self.tile_size)
            pygame.draw.rect(self.screen, color, rect)

            # Debug Overlays (FR-016)
            if debug_mode and agent == selected_agent:
                self._draw_debug_overlays(agent)

        # 4. Render Sidebar (Brain Monitor)
        sidebar_start_x = world_width_px
        # Always clear sidebar area
        pygame.draw.rect(self.screen, (20, 20, 20), (sidebar_start_x, 0, self.screen.get_width() - sidebar_start_x, self.screen.get_height()))
        
        if selected_agent and debug_mode:
            self._draw_brain_monitor(selected_agent, sidebar_start_x, logic.tick_count)
        elif selected_agent:
            # Hint for the user
            hint = self.font_med.render("Press 'D' for Brain Monitor", True, (150, 150, 150))
            self.screen.blit(hint, (sidebar_start_x + 50, self.screen.get_height() // 2))

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
        title = self.font_med.render(f"BRAIN: {agent.agent_id} ({agent.type})", True, (255, 255, 255))
        self.screen.blit(title, (start_x + 10, y))
        y += 40

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
        
        # More sensitive calculation: 
        # Average only traits that have moved from 0.0 significantly, 
        # or use full average if none have moved.
        sig_vals = [v for v in m_vals if abs(v) > 0.05]
        avg_alignment = sum(sig_vals) / len(sig_vals) if sig_vals else (sum(m_vals) / len(m_vals))
        
        align_str = "ANGELIC" if avg_alignment > 0.15 else "DIABOLIC" if avg_alignment < -0.15 else "NEUTRAL"
        align_color = (100, 255, 100) if align_str == "ANGELIC" else (255, 100, 100) if align_str == "DIABOLIC" else (255, 255, 200)
        self.screen.blit(self.font_med.render(f"ALIGNMENT: {align_str} ({avg_alignment:.2f})", True, align_color), (start_x + 10, y))
        y += 28

        # Traits (Personal Variance) - 4 Columns for density
        self.screen.blit(self.font_med.render("TRAITS (Cognitive Core):", True, (255, 200, 100)), (start_x + 10, y))
        y += 22
        # Filter non-numeric traits for the dashboard
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
        if hasattr(agent.ai, 'learning') and agent.ai.learning.behavior_matrix:
            self.screen.blit(self.font_med.render("HABITS (Learning Biases):", True, (255, 200, 200)), (start_x + 10, y))
            y += 22
            raw_biases = agent.ai.learning.behavior_matrix.get("default", {})
            bias_items = list(raw_biases.items())
            # Show up to 8 biases in 2 columns
            for i in range(0, min(8, len(bias_items)), 2):
                for j in range(2):
                    if i + j < len(bias_items):
                        goal, bias = bias_items[i+j]
                        b_val = float(bias)
                        col_x = start_x + 15 + (j * 140)
                        label = self.font_small.render(f"{goal[:12]}: {b_val:.2f}", True, (255, 255, 255))
                        self.screen.blit(label, (col_x, y))
                y += 18

    def _draw_debug_overlays(self, agent):
        # 1. Draw Intention Text above head
        intent = agent.ai.intentions.current_intention
        if intent:
            text = self.font_small.render(f"GOAL: {intent['goal']}", True, (255, 255, 255))
            tx = agent.x * self.tile_size
            ty = agent.y * self.tile_size - 15
            # Dark background for readability
            bg_rect = pygame.Rect(tx, ty, text.get_width() + 4, text.get_height())
            pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect)
            self.screen.blit(text, (tx + 2, ty))
        
        # 2. Draw Plan/Path visualization
        plan = agent.ai.planner.current_plan
        if plan:
            points = [(agent.x * self.tile_size + self.tile_size // 2, agent.y * self.tile_size + self.tile_size // 2)]
            target_pos = None
            
            for action, target in plan:
                if action == "move" and isinstance(target, tuple):
                    px, py = target
                    points.append((px * self.tile_size + self.tile_size // 2, py * self.tile_size + self.tile_size // 2))
                elif action in ["eat", "socialize", "share_belief"] and isinstance(target, tuple):
                    if len(target) == 2:
                        target_pos = target
                    elif len(target) == 3:
                        # For share_belief, target[1] is the (x, y) location
                        target_pos = target[1]

            if len(points) > 1:
                pygame.draw.lines(self.screen, (255, 255, 0), False, points, 2)
            
            if target_pos:
                tx, ty = target_pos
                t_center = (tx * self.tile_size + self.tile_size // 2, ty * self.tile_size + self.tile_size // 2)
                pygame.draw.line(self.screen, (255, 0, 0), points[-1], t_center, 1)
                pygame.draw.circle(self.screen, (255, 0, 0), t_center, 4, 1)
