"""
Renderer module for drawing game elements

This module handles all rendering operations including:
- HUD (Heads-Up Display) with game statistics
- Ground grid for spatial reference
- Crosshair for aiming
"""
import pygame
from OpenGL.GL import *
from config import WINDOW_WIDTH, WINDOW_HEIGHT


def draw_crosshair():
    """Draw crosshair at center of screen"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2)
    
    cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
    size = 15
    
    glBegin(GL_LINES)
    glVertex2f(cx - size, cy)
    glVertex2f(cx + size, cy)
    glVertex2f(cx, cy - size)
    glVertex2f(cx, cy + size)
    glEnd()
    
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_ground():
    """Draw infinite/far-reaching ground grid to prevent horizon clipping"""
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_LINES)
    
    # Extended grid for seamless horizon coverage
    grid_x_min, grid_x_max = -100, 101
    grid_z_min, grid_z_max = -100, 101
    grid_y = -3.0
    grid_spacing = 2
    
    for i in range(grid_x_min, grid_x_max, grid_spacing):
        glVertex3f(i, grid_y, grid_z_min)
        glVertex3f(i, grid_y, grid_z_max)
    
    for i in range(grid_z_min, grid_z_max, grid_spacing):
        glVertex3f(grid_x_min, grid_y, i)
        glVertex3f(grid_x_max, grid_y, i)
    
    glEnd()


def draw_hud(game_state, font, screen):
    """Draw HUD with game statistics"""
    stats_text = [
        f"Score: {game_state.score}",
        f"Hits: {game_state.hits}",
        f"Shots: {game_state.shots_fired}",
        f"Accuracy: {game_state.get_accuracy():.1f}%"
    ]
    
    # Enable alpha blending for smooth text overlay
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    def _avg_luminance(px, py, sw=4, sh=4):
        """Sample framebuffer to calculate background luminance"""
        try:
            sw = max(1, int(sw))
            sh = max(1, int(sh))
            # Read RGB pixels from framebuffer
            data = glReadPixels(int(px), int(py), sw, sh, GL_RGB, GL_UNSIGNED_BYTE)
            if not data:
                return 0.0
            
            total = 0
            count = 0
            for i in range(0, len(data), 3):
                r = data[i]
                g = data[i+1]
                b = data[i+2]
                # Calculate relative luminance using Rec. 709 standard
                lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
                total += lum
                count += 1
            return total / max(1, count)
        except Exception:
            return 0.0

    # Render each line with adaptive color
    y_offset = 20
    for text in stats_text:
        width, height = font.size(text)

        pos_x = 20
        pos_y = WINDOW_HEIGHT - y_offset - height

        # Sample background to determine brightness
        sample_w = min(8, max(1, width // 4))
        sample_h = min(8, max(1, height // 4))
        luminance = _avg_luminance(pos_x, pos_y, sample_w, sample_h)

        # Choose contrasting text color
        if luminance < 0.5:
            fg = (255, 255, 255)  # White on dark
        else:
            fg = (0, 0, 0)  # Black on bright

        text_surface = font.render(text, True, fg)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width, height = text_surface.get_size()

        glWindowPos2d(pos_x, pos_y)
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        y_offset += 35
