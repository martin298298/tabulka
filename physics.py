"""
Physics simulation module for roulette ball trajectory prediction.
Implements physics-based prediction of where the ball will land.
"""

import math
import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class RouletteState:
    """Current state of the roulette system."""
    ball_position: Tuple[float, float]  # (angle, radius) in polar coordinates
    ball_velocity: Tuple[float, float]  # (angular_velocity, radial_velocity)
    wheel_velocity: float  # angular velocity of wheel
    time: float


class RoulettePhysics:
    def __init__(self):
        # Physical constants (can be calibrated)
        self.gravity = 9.81  # m/s^2
        self.friction_coefficient = 0.02  # Ball-wheel friction
        self.air_resistance = 0.001  # Air resistance coefficient
        self.wheel_radius = 0.3  # Typical roulette wheel radius in meters
        self.ball_mass = 0.005  # Ball mass in kg (5 grams)
        
        # Conversion factors (pixels to meters, adjust based on calibration)
        self.pixels_per_meter = 300  # Approximate, needs calibration
        
        # European roulette numbers in wheel order
        self.wheel_numbers = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5,
            24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ]
        
    def pixel_coords_to_polar(self, x: int, y: int, center: Tuple[int, int]) -> Tuple[float, float]:
        """Convert pixel coordinates to polar coordinates (angle, radius)."""
        dx = x - center[0]
        dy = y - center[1]
        
        angle = math.atan2(dy, dx)
        radius = math.sqrt(dx*dx + dy*dy) / self.pixels_per_meter
        
        return angle, radius
    
    def calculate_angular_velocity(self, positions: List[Tuple[float, float]], 
                                 time_interval: float) -> Optional[float]:
        """
        Calculate angular velocity from position history.
        
        Args:
            positions: List of (angle, radius) positions
            time_interval: Time between measurements
            
        Returns:
            Angular velocity in rad/s
        """
        if len(positions) < 2:
            return None
        
        # Calculate angle differences, handling wraparound
        angle_diffs = []
        for i in range(1, len(positions)):
            angle_diff = positions[i][0] - positions[i-1][0]
            
            # Handle wraparound at ±π
            if angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            elif angle_diff < -math.pi:
                angle_diff += 2 * math.pi
                
            angle_diffs.append(angle_diff)
        
        # Average angular velocity
        avg_angular_velocity = sum(angle_diffs) / (len(angle_diffs) * time_interval)
        return avg_angular_velocity
    
    def calculate_radial_velocity(self, positions: List[Tuple[float, float]], 
                                time_interval: float) -> Optional[float]:
        """Calculate radial velocity (inward/outward movement)."""
        if len(positions) < 2:
            return None
        
        radius_diffs = []
        for i in range(1, len(positions)):
            radius_diff = positions[i][1] - positions[i-1][1]
            radius_diffs.append(radius_diff)
        
        avg_radial_velocity = sum(radius_diffs) / (len(radius_diffs) * time_interval)
        return avg_radial_velocity
    
    def simulate_trajectory(self, initial_state: RouletteState, 
                          simulation_time: float = 10.0, dt: float = 0.01) -> List[RouletteState]:
        """
        Simulate ball trajectory using physics.
        
        Args:
            initial_state: Starting state of the system
            simulation_time: How long to simulate (seconds)
            dt: Time step for simulation
            
        Returns:
            List of states over time
        """
        states = [initial_state]
        current_state = RouletteState(
            ball_position=initial_state.ball_position,
            ball_velocity=initial_state.ball_velocity,
            wheel_velocity=initial_state.wheel_velocity,
            time=initial_state.time
        )
        
        while current_state.time < initial_state.time + simulation_time:
            # Calculate forces
            angle, radius = current_state.ball_position
            angular_vel, radial_vel = current_state.ball_velocity
            
            # Centrifugal force (outward)
            centrifugal_force = self.ball_mass * angular_vel * angular_vel * radius
            
            # Friction force (opposes motion)
            friction_force = self.friction_coefficient * self.ball_mass * self.gravity
            
            # Air resistance (opposes velocity)
            air_resistance_angular = self.air_resistance * angular_vel * abs(angular_vel)
            air_resistance_radial = self.air_resistance * radial_vel * abs(radial_vel)
            
            # Update angular velocity (friction slows it down)
            angular_acceleration = -friction_force / (self.ball_mass * radius) - air_resistance_angular / self.ball_mass
            new_angular_vel = angular_vel + angular_acceleration * dt
            
            # Update radial velocity (centrifugal force and friction)
            radial_acceleration = centrifugal_force / self.ball_mass - air_resistance_radial / self.ball_mass
            
            # Gravity component (depends on wheel tilt, assume slight inward tilt)
            gravity_radial = -0.1 * self.gravity  # Small inward component
            radial_acceleration += gravity_radial
            
            new_radial_vel = radial_vel + radial_acceleration * dt
            
            # Update positions
            new_angle = angle + new_angular_vel * dt
            new_radius = max(0.05, radius + new_radial_vel * dt)  # Don't let ball go to center
            
            # Normalize angle to [-π, π]
            while new_angle > math.pi:
                new_angle -= 2 * math.pi
            while new_angle < -math.pi:
                new_angle += 2 * math.pi
            
            # Update wheel velocity (wheel also slows down due to friction)
            wheel_deceleration = 0.01  # rad/s^2
            new_wheel_vel = max(0, current_state.wheel_velocity - wheel_deceleration * dt)
            
            # Create new state
            new_state = RouletteState(
                ball_position=(new_angle, new_radius),
                ball_velocity=(new_angular_vel, new_radial_vel),
                wheel_velocity=new_wheel_vel,
                time=current_state.time + dt
            )
            
            states.append(new_state)
            current_state = new_state
            
            # Stop if ball has essentially stopped moving
            if abs(new_angular_vel) < 0.1 and abs(new_radial_vel) < 0.01:
                break
        
        return states
    
    def predict_landing_position(self, trajectory: List[RouletteState]) -> Tuple[float, int]:
        """
        Predict where the ball will land based on trajectory.
        
        Returns:
            (final_angle, predicted_number)
        """
        if not trajectory:
            return 0.0, 0
        
        final_state = trajectory[-1]
        final_angle = final_state.ball_position[0]
        
        # Adjust for wheel rotation during ball travel
        time_traveled = final_state.time - trajectory[0].time
        wheel_rotation = trajectory[0].wheel_velocity * time_traveled
        
        # Relative angle between ball and wheel
        relative_angle = final_angle - wheel_rotation
        
        # Normalize to [0, 2π]
        while relative_angle < 0:
            relative_angle += 2 * math.pi
        while relative_angle >= 2 * math.pi:
            relative_angle -= 2 * math.pi
        
        # Convert to wheel segment (37 segments for European roulette)
        segment_angle = 2 * math.pi / 37
        segment_index = int(relative_angle / segment_angle) % 37
        
        predicted_number = self.wheel_numbers[segment_index]
        
        return relative_angle, predicted_number
    
    def get_prediction_confidence(self, trajectory: List[RouletteState]) -> float:
        """
        Calculate confidence in prediction based on trajectory quality.
        
        Returns:
            Confidence value between 0 and 1
        """
        if len(trajectory) < 10:
            return 0.1
        
        # Check trajectory smoothness
        angular_velocities = [state.ball_velocity[0] for state in trajectory[:10]]
        velocity_variance = np.var(angular_velocities)
        
        # Lower variance means more consistent measurement, higher confidence
        confidence = max(0.1, min(1.0, 1.0 - velocity_variance / 10.0))
        
        return confidence
    
    def create_state_from_vision(self, ball_positions: List[Tuple[int, int]], 
                               wheel_center: Tuple[int, int], 
                               time_interval: float,
                               wheel_angular_velocity: float = 5.0) -> Optional[RouletteState]:
        """
        Create a RouletteState from computer vision data.
        
        Args:
            ball_positions: Recent ball positions in pixels
            wheel_center: Wheel center in pixels
            time_interval: Time between position measurements
            wheel_angular_velocity: Estimated wheel angular velocity
            
        Returns:
            RouletteState or None if insufficient data
        """
        if len(ball_positions) < 2:
            return None
        
        # Convert to polar coordinates
        polar_positions = []
        for pos in ball_positions:
            polar_pos = self.pixel_coords_to_polar(pos[0], pos[1], wheel_center)
            polar_positions.append(polar_pos)
        
        # Calculate velocities
        angular_vel = self.calculate_angular_velocity(polar_positions, time_interval)
        radial_vel = self.calculate_radial_velocity(polar_positions, time_interval)
        
        if angular_vel is None or radial_vel is None:
            return None
        
        # Use most recent position
        current_position = polar_positions[-1]
        
        return RouletteState(
            ball_position=current_position,
            ball_velocity=(angular_vel, radial_vel),
            wheel_velocity=wheel_angular_velocity,
            time=0.0
        )