import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

from camera import Camera
from renderer import Renderer
from target import TargetManager


# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "FPS Training Simulation"

# OpenGL settings
FOV = 45.0
NEAR_CLIP = 0.1
FAR_CLIP = 100.0


def init_opengl():
    """Initialize OpenGL settings and perspective projection."""
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    
    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
    gluPerspective(FOV, aspect_ratio, NEAR_CLIP, FAR_CLIP)
    
    # Switch to modelview matrix for rendering
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Set clear color (dark sky blue)
    glClearColor(0.1, 0.1, 0.2, 1.0)
    
    # Enable blending for crosshair
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def handle_input(camera, target_manager, keys_pressed, mouse_rel, delta_time):
    """
    Handle all input: keyboard for movement, mouse for looking, click for shooting.
    
    Args:
        camera: Camera instance
        target_manager: TargetManager instance for hit detection
        keys_pressed: pygame key state
        mouse_rel: tuple of mouse relative movement (dx, dy)
        delta_time: time since last frame in seconds
    
    Returns:
        bool: False if should quit, True otherwise
    """
    # Check for quit and mouse clicks
    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return False
            if event.key == K_r:
                # Reset stats
                target_manager.reset_stats()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Shoot - check for hit
                ray_origin = camera.position.copy()
                ray_direction = camera.get_forward_vector()
                target_manager.check_shot(ray_origin, ray_direction)
        # Re-grab mouse if it was released (e.g., by Cmd key on macOS)
        if event.type == ACTIVEEVENT or event.type == WINDOWEVENT:
            if not pygame.event.get_grab():
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
    
    # Ensure mouse stays grabbed (macOS Cmd key workaround)
    if not pygame.event.get_grab():
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        # Discard the mouse movement from ungrab/regrab
        pygame.mouse.get_rel()
        return True
    
    # Mouse look
    mouse_sensitivity = 0.1
    dx, dy = mouse_rel
    
    # Ignore large mouse jumps (from grab state changes)
    if abs(dx) > 100 or abs(dy) > 100:
        dx, dy = 0, 0
    
    camera.rotate(dx * mouse_sensitivity, -dy * mouse_sensitivity)
    
    # Keyboard movement
    move_speed = 5.0 * delta_time
    
    if keys_pressed[K_w]:
        camera.move_forward(move_speed)
    if keys_pressed[K_s]:
        camera.move_forward(-move_speed)
    if keys_pressed[K_a]:
        camera.move_right(-move_speed)
    if keys_pressed[K_d]:
        camera.move_right(move_speed)
    if keys_pressed[K_SPACE]:
        camera.move_up(move_speed)
    if keys_pressed[K_LSHIFT]:
        camera.move_up(-move_speed)
    
    return True


def update(camera, target_manager, delta_time):
    """
    Update game state.
    
    Args:
        camera: Camera instance
        target_manager: TargetManager instance
        delta_time: time since last frame in seconds
    """
    # Update targets (spawning, despawning)
    target_manager.update(delta_time)


def draw(camera, renderer, target_manager):
    """
    Render the scene.
    
    Args:
        camera: Camera instance
        renderer: Renderer instance
        target_manager: TargetManager instance
    """
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up view matrix from camera
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    camera.apply_view_matrix()
    
    # Draw 3D environment
    renderer.draw_ground_plane()
    renderer.draw_coordinate_axes()
    
    # Draw targets
    renderer.draw_targets(target_manager.get_targets())
    
    # Draw 2D overlay (crosshair)
    renderer.draw_crosshair(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Draw stats
    renderer.draw_stats(
        WINDOW_WIDTH, WINDOW_HEIGHT,
        target_manager.hits,
        target_manager.misses,
        target_manager.get_accuracy()
    )
    
    # Swap buffers
    pygame.display.flip()


def main():
    """Main entry point for the FPS Training Simulation."""
    # Initialize pygame
    pygame.init()
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(WINDOW_TITLE)
    
    # Capture mouse
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    
    # Initialize OpenGL
    init_opengl()
    
    # Create game objects
    camera = Camera(position=np.array([0.0, 1.7, 5.0]))  # Eye height ~1.7m
    renderer = Renderer()
    target_manager = TargetManager()
    
    # Timing
    clock = pygame.time.Clock()
    
    # Main game loop
    running = True
    while running:
        # Calculate delta time
        delta_time = clock.tick(60) / 1000.0  # Convert ms to seconds
        
        # Get input state
        keys_pressed = pygame.key.get_pressed()
        mouse_rel = pygame.mouse.get_rel()
        
        # Handle input
        running = handle_input(camera, target_manager, keys_pressed, mouse_rel, delta_time)
        
        # Update game state
        update(camera, target_manager, delta_time)
        
        # Render
        draw(camera, renderer, target_manager)
    
    # Cleanup
    pygame.quit()


if __name__ == "__main__":
    main()
