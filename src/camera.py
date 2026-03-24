import pygame

class Camera:
    def __init__(self, screen_width, screen_height, tile_size=20):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        
        # Current position (pixel center in world space)
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        
        # Target position for smoothing
        self.target_x = 0
        self.target_y = 0
        self.target_zoom = 1.0
        
        # Map boundaries (world tiles)
        self.map_width = 0
        self.map_height = 0

    def set_map_bounds(self, width, height):
        self.map_width = width
        self.map_height = height

    def update(self, dt=0.2):
        # 0. Clamp targets FIRST to prevent ghosting lag outside map
        if self.map_width > 0 and self.map_height > 0:
            view_w = self.screen_width / (self.target_zoom * self.tile_size)
            view_h = self.screen_height / (self.target_zoom * self.tile_size)
            half_w, half_h = view_w / 2, view_h / 2
            
            self.target_x = max(half_w, min(self.target_x, self.map_width - half_w))
            self.target_y = max(half_h, min(self.target_y, self.map_height - half_h))

        # 1. Linear interpolation for smoothing
        self.x += (self.target_x - self.x) * dt
        self.y += (self.target_y - self.y) * dt
        self.zoom += (self.target_zoom - self.zoom) * dt
        
        self.clamp()

    def clamp(self):
        if self.map_width == 0 or self.map_height == 0:
            return

        # Viewport width/height in world space
        view_w = self.screen_width / (self.zoom * self.tile_size)
        view_h = self.screen_height / (self.zoom * self.tile_size)
        
        # Clamp camera center to keep viewport edges inside map
        half_view_w = view_w / 2
        half_view_h = view_h / 2
        
        min_x = half_view_w
        max_x = self.map_width - half_view_w
        min_y = half_view_h
        max_y = self.map_height - half_view_h
        
        # If map is smaller than viewport, center it
        if min_x > max_x: self.x = self.map_width / 2
        else: self.x = max(min_x, min(self.x, max_x))
            
        if min_y > max_y: self.y = self.map_height / 2
        else: self.y = max(min_y, min(self.y, max_y))

    def world_to_screen(self, wx, wy):
        # (wx, wy) are world tile coordinates
        # Offset from camera center
        dx = (wx - self.x) * self.tile_size * self.zoom
        dy = (wy - self.y) * self.tile_size * self.zoom
        
        # To screen coordinates
        sx = dx + self.screen_width / 2
        sy = dy + self.screen_height / 2
        return int(sx), int(sy)

    def screen_to_world(self, sx, sy):
        # (sx, sy) are screen pixel coordinates
        dx = sx - self.screen_width / 2
        dy = sy - self.screen_height / 2
        
        wx = (dx / (self.tile_size * self.zoom)) + self.x
        wy = (dy / (self.tile_size * self.zoom)) + self.y
        return wx, wy

    def get_visible_chunk_range(self, chunk_size):
        # Viewport edges in world space
        view_w = self.screen_width / (self.zoom * self.tile_size)
        view_h = self.screen_height / (self.zoom * self.tile_size)
        
        min_wx = self.x - view_w / 2
        max_wx = self.x + view_w / 2
        min_wy = self.y - view_h / 2
        max_wy = self.y + view_h / 2
        
        min_cx = int(min_wx // chunk_size)
        max_cx = int(max_wx // chunk_size)
        min_cy = int(min_wy // chunk_size)
        max_cy = int(max_wy // chunk_size)
        
        return min_cx, max_cx, min_cy, max_cy
    def get_world_bounds(self, chunk_size):
        """Returns (min_x, min_y, max_x, max_y) in world coordinates."""
        view_w = self.screen_width / (self.zoom * self.tile_size)
        view_h = self.screen_height / (self.zoom * self.tile_size)
        
        min_wx = self.x - view_w / 2
        max_wx = self.x + view_w / 2
        min_wy = self.y - view_h / 2
        max_wy = self.y + view_h / 2
        
        return min_wx, min_wy, max_wx, max_wy
