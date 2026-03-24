import pygame
import numpy as np

class Chunk:
    CHUNK_SIZE = 32

    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        
        # NumPy array for tile IDs (compact storage)
        self.tiles = np.zeros((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=np.uint8)
        
        # Entity sets
        self.entities = set()
        
        # Rendering cache
        self.surface = None
        self.dirty = True

    def set_tile(self, tx, ty, tile_id):
        # tx, ty are 0 to CHUNK_SIZE-1
        self.tiles[ty, tx] = tile_id
        self.dirty = True

    def render_surface(self, renderer_instance):
        # placeholder for actual rendering logic once renderer is refactored
        # This will be called by video.py
        pass
