"""
Renderer module for FPS Training Simulation.

Handles drawing of 3D environment and 2D overlay elements.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math


class Renderer:
    """
    Renderer class for drawing 3D and 2D elements.
    
    Handles:
        - Ground plane rendering
        - Coordinate axes visualization
        - 2D crosshair overlay
    """
    
    def __init__(self):
        """Initialize the renderer."""
        # Ground plane settings
        self.ground_size = 50.0  # Half-size of ground plane
        self.grid_spacing = 2.0  # Distance between grid lines
        self.ground_color = (0.3, 0.3, 0.3)  # Dark gray
        self.grid_color = (0.5, 0.5, 0.5)  # Light gray
        
        # Crosshair settings
        self.crosshair_size = 10  # Size in pixels
        self.crosshair_gap = 3    # Gap from center in pixels
        self.crosshair_thickness = 2
        self.crosshair_color = (0.0, 1.0, 0.0, 0.8)  # Green with alpha
    
    def draw_ground_plane(self):
        """
        Draw a ground plane with grid lines.
        
        The plane is centered at the origin on the XZ plane (Y = 0).
        """
        size = self.ground_size
        spacing = self.grid_spacing
        
        # Draw solid ground quad
        glBegin(GL_QUADS)
        glColor3f(*self.ground_color)
        glVertex3f(-size, 0.0, -size)
        glVertex3f(-size, 0.0, size)
        glVertex3f(size, 0.0, size)
        glVertex3f(size, 0.0, -size)
        glEnd()
        
        # Draw grid lines
        glBegin(GL_LINES)
        glColor3f(*self.grid_color)
        
        # Lines parallel to Z axis
        x = -size
        while x <= size:
            glVertex3f(x, 0.01, -size)  # Slight Y offset to prevent z-fighting
            glVertex3f(x, 0.01, size)
            x += spacing
        
        # Lines parallel to X axis
        z = -size
        while z <= size:
            glVertex3f(-size, 0.01, z)
            glVertex3f(size, 0.01, z)
            z += spacing
        
        glEnd()
    
    def draw_coordinate_axes(self):
        """
        Draw RGB coordinate axes for orientation reference.
        
        X = Red, Y = Green, Z = Blue
        """
        axis_length = 3.0
        
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # X axis (Red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.01, 0.0)
        glVertex3f(axis_length, 0.01, 0.0)
        
        # Y axis (Green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.01, 0.0)
        glVertex3f(0.0, axis_length, 0.0)
        
        # Z axis (Blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.01, 0.0)
        glVertex3f(0.0, 0.01, axis_length)
        
        glEnd()
        glLineWidth(1.0)
    
    def draw_crosshair(self, screen_width, screen_height):
        """
        Draw a 2D crosshair at the exact center of the screen.
        
        The crosshair stays fixed regardless of camera movement.
        
        Args:
            screen_width: Window width in pixels
            screen_height: Window height in pixels
        """
        # Switch to orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, screen_width, screen_height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Disable depth test for overlay
        glDisable(GL_DEPTH_TEST)
        
        # Calculate center position
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Draw crosshair
        glLineWidth(self.crosshair_thickness)
        glColor4f(*self.crosshair_color)
        
        glBegin(GL_LINES)
        
        # Horizontal line (left part)
        glVertex2f(center_x - self.crosshair_size - self.crosshair_gap, center_y)
        glVertex2f(center_x - self.crosshair_gap, center_y)
        
        # Horizontal line (right part)
        glVertex2f(center_x + self.crosshair_gap, center_y)
        glVertex2f(center_x + self.crosshair_size + self.crosshair_gap, center_y)
        
        # Vertical line (top part)
        glVertex2f(center_x, center_y - self.crosshair_size - self.crosshair_gap)
        glVertex2f(center_x, center_y - self.crosshair_gap)
        
        # Vertical line (bottom part)
        glVertex2f(center_x, center_y + self.crosshair_gap)
        glVertex2f(center_x, center_y + self.crosshair_size + self.crosshair_gap)
        
        glEnd()
        
        # Optional: Draw center dot
        glPointSize(3.0)
        glBegin(GL_POINTS)
        glVertex2f(center_x, center_y)
        glEnd()
        
        glLineWidth(1.0)
        
        # Re-enable depth test
        glEnable(GL_DEPTH_TEST)
        
        # Restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def draw_cube(self, position, size=1.0, color=(1.0, 1.0, 1.0)):
        """
        Draw a simple cube at the given position.
        
        Useful for testing and debugging.
        
        Args:
            position: tuple (x, y, z) for cube center
            size: length of cube edges
            color: tuple (r, g, b) for cube color
        """
        x, y, z = position
        half = size / 2.0
        
        glColor3f(*color)
        
        # Define vertices
        vertices = [
            (x - half, y - half, z + half),
            (x + half, y - half, z + half),
            (x + half, y + half, z + half),
            (x - half, y + half, z + half),
            (x - half, y - half, z - half),
            (x + half, y - half, z - half),
            (x + half, y + half, z - half),
            (x - half, y + half, z - half),
        ]
        
        # Define faces (as vertex indices)
        faces = [
            (0, 1, 2, 3),  # Front
            (5, 4, 7, 6),  # Back
            (4, 0, 3, 7),  # Left
            (1, 5, 6, 2),  # Right
            (3, 2, 6, 7),  # Top
            (4, 5, 1, 0),  # Bottom
        ]
        
        glBegin(GL_QUADS)
        for face in faces:
            for vertex_index in face:
                glVertex3fv(vertices[vertex_index])
        glEnd()
        
        # Draw edges
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINES)
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        for edge in edges:
            for vertex_index in edge:
                glVertex3fv(vertices[vertex_index])
        glEnd()

    def draw_sphere(self, position, radius, color, segments=16):
        """
        Draw a sphere (target ball) at the given position.
        
        Args:
            position: tuple (x, y, z) for sphere center
            radius: radius of the sphere
            color: tuple (r, g, b) for sphere color
            segments: number of segments for sphere detail
        """
        x, y, z = position
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Create quadric for sphere
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        
        # Draw filled sphere
        glColor3f(*color)
        gluSphere(quadric, radius, segments, segments)
        
        # Draw outline for better visibility
        glColor3f(1.0, 1.0, 1.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        gluSphere(quadric, radius * 1.01, segments // 2, segments // 2)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        gluDeleteQuadric(quadric)
        glPopMatrix()
    
    def draw_target(self, target):
        """
        Draw a target ball with visual feedback based on remaining time.
        
        Args:
            target: Target instance to draw
        """
        remaining = target.get_remaining_time()
        
        # Color fades from bright to dim as time runs out
        base_color = target.color
        fade = 0.3 + (0.7 * remaining)  # Fade from 1.0 to 0.3
        color = (base_color[0] * fade, base_color[1] * fade, base_color[2] * fade)
        
        # Slight pulsing effect
        pulse = 1.0 + 0.05 * math.sin(remaining * 20)
        radius = target.radius * pulse
        
        self.draw_sphere(target.position, radius, color)
    
    def draw_targets(self, targets):
        """
        Draw all active targets.
        
        Args:
            targets: list of Target instances
        """
        for target in targets:
            self.draw_target(target)
    
    def draw_stats(self, screen_width, screen_height, hits, misses, accuracy):
        """
        Draw game statistics on screen.
        
        Args:
            screen_width: Window width
            screen_height: Window height
            hits: number of hits
            misses: number of misses
            accuracy: accuracy percentage
        """
        # Switch to orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, screen_width, screen_height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Draw stats background
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(10, 10)
        glVertex2f(150, 10)
        glVertex2f(150, 80)
        glVertex2f(10, 80)
        glEnd()
        
        # Draw hit indicator bars
        bar_width = 120
        bar_height = 8
        
        # Hits bar (green)
        glColor4f(0.0, 1.0, 0.0, 0.8)
        hit_width = min(bar_width, hits * 10)
        glBegin(GL_QUADS)
        glVertex2f(20, 25)
        glVertex2f(20 + hit_width, 25)
        glVertex2f(20 + hit_width, 25 + bar_height)
        glVertex2f(20, 25 + bar_height)
        glEnd()
        
        # Misses bar (red)
        glColor4f(1.0, 0.0, 0.0, 0.8)
        miss_width = min(bar_width, misses * 10)
        glBegin(GL_QUADS)
        glVertex2f(20, 45)
        glVertex2f(20 + miss_width, 45)
        glVertex2f(20 + miss_width, 45 + bar_height)
        glVertex2f(20, 45 + bar_height)
        glEnd()
        
        # Accuracy bar (yellow)
        glColor4f(1.0, 1.0, 0.0, 0.8)
        acc_width = bar_width * (accuracy / 100.0)
        glBegin(GL_QUADS)
        glVertex2f(20, 65)
        glVertex2f(20 + acc_width, 65)
        glVertex2f(20 + acc_width, 65 + bar_height)
        glVertex2f(20, 65 + bar_height)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        
        # Restore matrices
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
