"""
Target module for managing shooting targets
"""
import random
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from config import BOUNDARY_X_MIN, BOUNDARY_X_MAX, BOUNDARY_Y_MIN, BOUNDARY_Y_MAX, BOUNDARY_Z_MIN, BOUNDARY_Z_MAX


class Target:
    """Represents a moving sphere target"""
    def __init__(self, target_id):
        self.id = target_id
        self.radius = 0.5
        self.respawn()
    
    def respawn(self):
        """Randomly position the target within visual boundaries"""
        self.position = np.array([
            random.uniform(BOUNDARY_X_MIN, BOUNDARY_X_MAX),
            random.uniform(BOUNDARY_Y_MIN, BOUNDARY_Y_MAX),
            random.uniform(BOUNDARY_Z_MIN, BOUNDARY_Z_MAX)
        ])
        
        self.velocity = np.array([
            random.uniform(-0.02, 0.02),
            random.uniform(-0.02, 0.02),
            random.uniform(-0.01, 0.01)
        ])
        
        self.color = (
            random.uniform(0.5, 1.0),
            random.uniform(0.5, 1.0),
            random.uniform(0.5, 1.0)
        )
        
        self.active = True
    
    def update(self):
        """Update target position with boundary collision"""
        if not self.active:
            return
        
        self.position += self.velocity
        
        if self.position[0] < BOUNDARY_X_MIN or self.position[0] > BOUNDARY_X_MAX:
            self.velocity[0] *= -1
            self.position[0] = np.clip(self.position[0], BOUNDARY_X_MIN, BOUNDARY_X_MAX)
        if self.position[1] < BOUNDARY_Y_MIN or self.position[1] > BOUNDARY_Y_MAX:
            self.velocity[1] *= -1
            self.position[1] = np.clip(self.position[1], BOUNDARY_Y_MIN, BOUNDARY_Y_MAX)
        if self.position[2] < BOUNDARY_Z_MIN or self.position[2] > BOUNDARY_Z_MAX:
            self.velocity[2] *= -1
            self.position[2] = np.clip(self.position[2], BOUNDARY_Z_MIN, BOUNDARY_Z_MAX)
    
    def draw(self):
        """Render the target sphere"""
        if not self.active:
            return
        
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(*self.color)
        
        quad = gluNewQuadric()
        gluSphere(quad, self.radius, 20, 20)
        gluDeleteQuadric(quad)
        
        glPopMatrix()
    
    def check_hit(self, ray_origin, ray_direction):
        """Check if ray intersects this sphere (ray-sphere intersection)"""                 if not self.active:
            return False
        
        oc = ray_origin - self.position
        
        a = np.dot(ray_direction, ray_direction)
        b = 2.0 * np.dot(oc, ray_direction)
        c = np.dot(oc, oc) - self.radius * self.radius
        
        discriminant = b * b - 4 * a * c
        
        return discriminant > 0

class GameState:
    """Manages game statistics and state"""
    def __init__(self):
        self.shots_fired = 0
        self.hits = 0
        self.score = 0
    
    def get_accuracy(self):
        """Calculate shooting accuracy percentage"""
        if self.shots_fired == 0:
            return 0.0
        return (self.hits / self.shots_fired) * 100