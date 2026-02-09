"""
Camera module for first-person view control
"""
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from config import MOUSE_SENSITIVITY


class Camera:
    """Handles first-person camera with mouse look"""
    def __init__(self):
        self.position = np.array([0.0, 0.0, 5.0])
        self.yaw = -90.0
        self.pitch = 0.0
        self.update_vectors()
    
    def update_vectors(self):
        """Calculate forward, right, and up vectors based on yaw and pitch"""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        
        self.forward = np.array([
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            math.sin(yaw_rad) * math.cos(pitch_rad)
        ])
        self.forward = self.forward / np.linalg.norm(self.forward)
        
        self.right = np.cross(self.forward, np.array([0.0, 1.0, 0.0]))
        self.right = self.right / np.linalg.norm(self.right)
        
        self.up = np.cross(self.right, self.forward)
    
    def process_mouse(self, dx, dy):
        """Update camera rotation based on mouse movement"""
        self.yaw += dx * MOUSE_SENSITIVITY
        self.pitch -= dy * MOUSE_SENSITIVITY
        
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
        
        self.update_vectors()
    
    def apply(self):
        """Apply camera transformation to OpenGL"""
        glLoadIdentity()
        look_at = self.position + self.forward
        gluLookAt(
            self.position[0], self.position[1], self.position[2],
            look_at[0], look_at[1], look_at[2],
            self.up[0], self.up[1], self.up[2]
        )
