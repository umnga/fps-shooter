"""
Main entry point for FPS Training Simulation
"""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from config import WINDOW_WIDTH, WINDOW_HEIGHT, FOV, TARGET_COUNT
from camera import Camera
from target import Target, GameState
from renderer import draw_crosshair, draw_ground, draw_hud


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("FPS Training Simulation")
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(FOV, WINDOW_WIDTH / WINDOW_HEIGHT, 1.0, 500.0)
    glMatrixMode(GL_MODELVIEW)
    
    camera = Camera()
    targets = [Target(i) for i in range(TARGET_COUNT)]
    game_state = GameState()
    font = pygame.font.Font(None, 36)
    
    clock = pygame.time.Clock()
    running = True
    
    print("=== FPS Training Simulation ===")
    print("Controls:")
    print("  Mouse: Look around")
    print("  Left Click: Shoot")
    print("  ESC: Exit")
    print("===============================")
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEMOTION:
                dx, dy = event.rel
                camera.process_mouse(dx, dy)
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    game_state.shots_fired += 1
                    
                    ray_origin = camera.position
                    ray_direction = camera.forward
                    
                    hit_any = False
                    for target in targets:
                        if target.check_hit(ray_origin, ray_direction):
                            game_state.hits += 1
                            game_state.score += 10
                            target.respawn()
                            hit_any = True
                            break
                    
                    if hit_any:
                        print(f"HIT! Score: {game_state.score} | Accuracy: {game_state.get_accuracy():.1f}%")
        
        for target in targets:
            target.update()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        camera.apply()
        
        draw_ground()
        
        for target in targets:
            target.draw()
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        draw_crosshair()
        draw_hud(game_state, font, screen)
        
        glEnable(GL_DEPTH_TEST)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        pygame.display.flip()
        clock.tick(60)
    
      # Cleanup on exit
    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    pygame.quit()


if __name__ == "__main__":
    main()