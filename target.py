"""
Target module for FPS Training Simulation.

Handles target (ball) spawning, lifetime, and hit detection similar to Aim Lab.
"""

import random
import math
import time
import numpy as np


class Target:
    """
    A single target ball that spawns, stays visible, and despawns after timeout.
    """
    
    def __init__(self, position, radius=0.3, lifetime=3.0):
        """
        Initialize a target.
        
        Args:
            position: np.array [x, y, z] position in world space
            radius: radius of the target ball
            lifetime: seconds before target disappears if not hit
        """
        self.position = np.array(position, dtype=float)
        self.radius = radius
        self.lifetime = lifetime
        self.spawn_time = time.time()
        self.is_active = True
        self.is_hit = False
        
        # Visual properties
        self.color = (1.0, 0.3, 0.1)  # Orange-red
        self.hit_color = (0.0, 1.0, 0.0)  # Green on hit
    
    def update(self, delta_time):
        """
        Update target state.
        
        Returns:
            bool: True if target is still active, False if expired
        """
        if not self.is_active:
            return False
        
        elapsed = time.time() - self.spawn_time
        if elapsed >= self.lifetime:
            self.is_active = False
            return False
        
        return True
    
    def get_remaining_time(self):
        """Get remaining lifetime as a ratio (0.0 to 1.0)."""
        elapsed = time.time() - self.spawn_time
        return max(0.0, 1.0 - (elapsed / self.lifetime))
    
    def check_hit(self, ray_origin, ray_direction):
        """
        Check if a ray (from camera) hits this target.
        
        Uses ray-sphere intersection.
        
        Args:
            ray_origin: np.array [x, y, z] - starting point of ray
            ray_direction: np.array [x, y, z] - normalized direction
            
        Returns:
            bool: True if hit
        """
        if not self.is_active:
            return False
        
        # Ray-sphere intersection
        oc = ray_origin - self.position
        a = np.dot(ray_direction, ray_direction)
        b = 2.0 * np.dot(oc, ray_direction)
        c = np.dot(oc, oc) - self.radius * self.radius
        
        discriminant = b * b - 4 * a * c
        
        if discriminant > 0:
            # Check if intersection is in front of ray
            t = (-b - math.sqrt(discriminant)) / (2 * a)
            if t > 0:
                self.is_hit = True
                self.is_active = False
                return True
        
        return False


class TargetManager:
    """
    Manages spawning and tracking of multiple targets.
    
    Similar to Aim Lab's Gridshot/Spheretrack modes.
    """
    
    def __init__(self):
        """Initialize the target manager."""
        self.targets = []
        self.max_targets = 3  # Max concurrent targets
        self.spawn_interval = 1.0  # Seconds between spawns
        self.last_spawn_time = 0
        self.target_lifetime = 2.5  # Seconds before target disappears
        self.target_radius = 0.4
        
        # Spawn area bounds (in front of player)
        self.spawn_min = np.array([-8.0, 1.0, -15.0])
        self.spawn_max = np.array([8.0, 5.0, -5.0])
        
        # Stats
        self.hits = 0
        self.misses = 0
        self.total_spawned = 0
    
    def get_random_spawn_position(self):
        """Generate a random position within spawn bounds."""
        x = random.uniform(self.spawn_min[0], self.spawn_max[0])
        y = random.uniform(self.spawn_min[1], self.spawn_max[1])
        z = random.uniform(self.spawn_min[2], self.spawn_max[2])
        return np.array([x, y, z])
    
    def spawn_target(self):
        """Spawn a new target at a random position."""
        position = self.get_random_spawn_position()
        target = Target(
            position=position,
            radius=self.target_radius,
            lifetime=self.target_lifetime
        )
        self.targets.append(target)
        self.total_spawned += 1
        self.last_spawn_time = time.time()
    
    def update(self, delta_time):
        """
        Update all targets and handle spawning.
        
        Args:
            delta_time: time since last frame
        """
        current_time = time.time()
        
        # Remove expired targets and count misses
        expired_targets = [t for t in self.targets if not t.is_active and not t.is_hit]
        self.misses += len(expired_targets)
        
        # Update remaining targets
        self.targets = [t for t in self.targets if t.update(delta_time)]
        
        # Spawn new targets if needed
        active_count = len(self.targets)
        time_since_spawn = current_time - self.last_spawn_time
        
        if active_count < self.max_targets and time_since_spawn >= self.spawn_interval:
            self.spawn_target()
    
    def check_shot(self, ray_origin, ray_direction):
        """
        Check if a shot hits any target.
        
        Args:
            ray_origin: camera position
            ray_direction: normalized look direction
            
        Returns:
            bool: True if a target was hit
        """
        for target in self.targets:
            if target.check_hit(ray_origin, ray_direction):
                self.hits += 1
                return True
        return False
    
    def get_targets(self):
        """Get list of active targets for rendering."""
        return [t for t in self.targets if t.is_active]
    
    def get_accuracy(self):
        """Calculate hit accuracy percentage."""
        total_shots = self.hits + self.misses
        if total_shots == 0:
            return 0.0
        return (self.hits / total_shots) * 100
    
    def reset_stats(self):
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.total_spawned = 0
