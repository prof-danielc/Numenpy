import pytest
from src.camera import Camera

def test_camera_transforms():
    cam = Camera(800, 600, tile_size=20)
    cam.x, cam.y = 100, 100
    cam.zoom = 1.0
    
    # Test world to screen
    sx, sy = cam.world_to_screen(100, 100)
    assert sx == 400
    assert sy == 300
    
    # Test screen to world round-trip
    wx, wy = cam.screen_to_world(400, 300)
    assert wx == 100
    assert wy == 100

def test_camera_zoom_transforms():
    cam = Camera(800, 600, tile_size=20)
    cam.x, cam.y = 100, 100
    cam.zoom = 2.0
    
    # At 2x zoom, a tile at 101, 101 should be offset by 1 tile (20px) * 2 zoom = 40px
    sx, sy = cam.world_to_screen(101, 101)
    assert sx == 400 + 40
    assert sy == 300 + 40
    
    wx, wy = cam.screen_to_world(sx, sy)
    assert wx == pytest.approx(101)
    assert wy == pytest.approx(101)

def test_camera_clamping():
    cam = Camera(800, 600, tile_size=20)
    cam.set_map_bounds(100, 100)
    
    # Try to move camera to edge
    cam.target_x, cam.target_y = 0, 0
    cam.update(dt=1.0) # instant snap
    
    # Center should be clamped so top-left of viewport (400px/20px = 20 tiles half-width) is at 0
    assert cam.x == 20
    assert cam.y == 15
