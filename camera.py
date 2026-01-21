"""
Camera module for FPS Training Simulation.

Implements a first-person camera with position, yaw (horizontal rotation),
and pitch (vertical rotation) controls.
"""

import numpy as np
import math
from OpenGL.GL import *
from OpenGL.GLU import *


class Camera:
    """
    First-person camera class managing position and orientation.
    
    Attributes:
        position: numpy array [x, y, z] representing camera position
        yaw: horizontal rotation in degrees (0 = looking along -Z axis)
        pitch: vertical rotation in degrees (constrained to -90 to +90)
    """
    
    # Pitch constraints to prevent screen flipping
    MIN_PITCH = -89.0
    MAX_PITCH = 89.0
    
    def __init__(self, position=None, yaw=0.0, pitch=0.0):
        """
        Initialize the camera.
        
        Args:
            position: Initial position as numpy array [x, y, z]. Defaults to origin.
            yaw: Initial yaw angle in degrees. Defaults to 0.
            pitch: Initial pitch angle in degrees. Defaults to 0.
        """
        if position is None:
            self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        else:
            self.position = np.array(position, dtype=np.float32)
        
        self.yaw = yaw
        self.pitch = self._clamp_pitch(pitch)
    
    def _clamp_pitch(self, pitch):
        """Clamp pitch to valid range to prevent screen flipping."""
        return max(self.MIN_PITCH, min(self.MAX_PITCH, pitch))
    
    def get_forward_vector(self):
        """
        Calculate the forward direction vector based on yaw and pitch.
        
        Returns:
            numpy array: Normalized forward direction vector [x, y, z]
        """
        # Convert to radians
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        
        # Calculate direction vector
        forward = np.array([
            math.sin(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            -math.cos(yaw_rad) * math.cos(pitch_rad)
        ], dtype=np.float32)
        
        return forward
    
    def get_right_vector(self):
        """
        Calculate the right direction vector (perpendicular to forward on XZ plane).
        
        Returns:
            numpy array: Normalized right direction vector [x, y, z]
        """
        yaw_rad = math.radians(self.yaw)
        
        right = np.array([
            math.cos(yaw_rad),
            0.0,
            math.sin(yaw_rad)
        ], dtype=np.float32)
        
        return right
    
    def get_up_vector(self):
        """
        Get the world up vector.
        
        Returns:
            numpy array: Up vector [0, 1, 0]
        """
        return np.array([0.0, 1.0, 0.0], dtype=np.float32)
    
    def get_look_at_target(self):
        """
        Calculate the point the camera is looking at.
        
        Returns:
            numpy array: Target point [x, y, z]
        """
        return self.position + self.get_forward_vector()
    
    def get_view_matrix(self):
        """
        Calculate the view matrix using NumPy.
        
        This creates a custom LookAt matrix for the camera.
        
        Returns:
            numpy array: 4x4 view matrix
        """
        # Get camera vectors
        forward = self.get_forward_vector()
        forward = forward / np.linalg.norm(forward)  # Normalize
        
        world_up = self.get_up_vector()
        
        # Calculate right vector (cross product of forward and world up)
        right = np.cross(forward, world_up)
        right = right / np.linalg.norm(right)
        
        # Recalculate up vector (cross product of right and forward)
        up = np.cross(right, forward)
        up = up / np.linalg.norm(up)
        
        # Create rotation matrix
        rotation = np.array([
            [right[0], right[1], right[2], 0.0],
            [up[0], up[1], up[2], 0.0],
            [-forward[0], -forward[1], -forward[2], 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        # Create translation matrix
        translation = np.array([
            [1.0, 0.0, 0.0, -self.position[0]],
            [0.0, 1.0, 0.0, -self.position[1]],
            [0.0, 0.0, 1.0, -self.position[2]],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        # View matrix = rotation * translation
        view_matrix = rotation @ translation
        
        return view_matrix
    
    def apply_view_matrix(self):
        """
        Apply the view transformation using gluLookAt.
        
        This is the OpenGL-native way to set up the view matrix.
        """
        target = self.get_look_at_target()
        up = self.get_up_vector()
        
        gluLookAt(
            self.position[0], self.position[1], self.position[2],  # Eye position
            target[0], target[1], target[2],                        # Look at target
            up[0], up[1], up[2]                                     # Up vector
        )
    
    def rotate(self, yaw_delta, pitch_delta):
        """
        Rotate the camera by the given amounts.
        
        Args:
            yaw_delta: Change in yaw (horizontal rotation) in degrees
            pitch_delta: Change in pitch (vertical rotation) in degrees
        """
        self.yaw += yaw_delta
        
        # Keep yaw in reasonable range
        while self.yaw > 360.0:
            self.yaw -= 360.0
        while self.yaw < 0.0:
            self.yaw += 360.0
        
        # Update and clamp pitch
        self.pitch = self._clamp_pitch(self.pitch + pitch_delta)
    
    def move_forward(self, distance):
        """
        Move the camera forward/backward along the viewing direction (XZ plane only).
        
        Args:
            distance: Distance to move (positive = forward, negative = backward)
        """
        yaw_rad = math.radians(self.yaw)
        
        # Move only on XZ plane for FPS-style movement
        self.position[0] += math.sin(yaw_rad) * distance
        self.position[2] -= math.cos(yaw_rad) * distance
    
    def move_right(self, distance):
        """
        Move the camera left/right perpendicular to the viewing direction.
        
        Args:
            distance: Distance to move (positive = right, negative = left)
        """
        right = self.get_right_vector()
        self.position += right * distance
    
    def move_up(self, distance):
        """
        Move the camera up/down along the world Y axis.
        
        Args:
            distance: Distance to move (positive = up, negative = down)
        """
        self.position[1] += distance
    
    def set_position(self, x, y, z):
        """
        Set the camera position directly.
        
        Args:
            x, y, z: New position coordinates
        """
        self.position = np.array([x, y, z], dtype=np.float32)
    
    def set_rotation(self, yaw, pitch):
        """
        Set the camera rotation directly.
        
        Args:
            yaw: New yaw angle in degrees
            pitch: New pitch angle in degrees (will be clamped)
        """
        self.yaw = yaw
        self.pitch = self._clamp_pitch(pitch)
