"""
Computer vision module for roulette prediction system.
Handles ball and wheel detection using OpenCV.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
import math


class RouletteVision:
    def __init__(self):
        self.wheel_center = None
        self.wheel_radius = None
        self.last_ball_position = None
        self.ball_history = []
        
    def detect_wheel(self, frame: np.ndarray) -> Tuple[Optional[Tuple[int, int]], Optional[int]]:
        """
        Detect the roulette wheel center and radius.
        
        Returns:
            Tuple of ((center_x, center_y), radius) or (None, None)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=50,
            param2=30,
            minRadius=50,
            maxRadius=min(frame.shape[:2]) // 2
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            # Find the largest circle (most likely the wheel)
            largest_circle = max(circles, key=lambda c: c[2])
            x, y, r = largest_circle
            
            self.wheel_center = (x, y)
            self.wheel_radius = r
            return (x, y), r
        
        return None, None
    
    def detect_ball(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Detect the ball position in the frame.
        
        Returns:
            (x, y) position of ball or None if not detected
        """
        if self.wheel_center is None:
            self.detect_wheel(frame)
            if self.wheel_center is None:
                return None
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define range for white ball (adjust as needed)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        
        # Create mask for white objects
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Also try detecting bright objects
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bright_mask = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
        
        # Combine masks
        combined_mask = cv2.bitwise_or(white_mask, bright_mask)
        
        # Apply morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            ball_candidates = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                # Filter by area (ball should be small but not too small)
                if 10 < area < 200:
                    # Check if contour is roughly circular
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * math.pi * area / (perimeter * perimeter)
                        if circularity > 0.5:  # Reasonably circular
                            M = cv2.moments(contour)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                
                                # Check if candidate is within wheel area
                                dist_from_center = math.sqrt(
                                    (cx - self.wheel_center[0])**2 + 
                                    (cy - self.wheel_center[1])**2
                                )
                                
                                if dist_from_center < self.wheel_radius:
                                    ball_candidates.append((cx, cy, area, circularity))
            
            if ball_candidates:
                # Choose best candidate (highest circularity)
                best_candidate = max(ball_candidates, key=lambda x: x[3])
                ball_pos = (best_candidate[0], best_candidate[1])
                
                # Update history
                self.last_ball_position = ball_pos
                self.ball_history.append(ball_pos)
                
                # Keep only recent history
                if len(self.ball_history) > 10:
                    self.ball_history.pop(0)
                
                return ball_pos
        
        return None
    
    def calculate_ball_speed(self, time_interval: float = 0.1) -> Optional[float]:
        """
        Calculate ball speed based on position history.
        
        Args:
            time_interval: Time between frames in seconds
            
        Returns:
            Speed in pixels per second or None
        """
        if len(self.ball_history) < 2:
            return None
        
        # Calculate distance between last two positions
        pos1 = self.ball_history[-2]
        pos2 = self.ball_history[-1]
        
        distance = math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
        speed = distance / time_interval
        
        return speed
    
    def get_ball_angle(self) -> Optional[float]:
        """
        Get the current angle of the ball relative to wheel center.
        
        Returns:
            Angle in radians or None
        """
        if self.last_ball_position is None or self.wheel_center is None:
            return None
        
        dx = self.last_ball_position[0] - self.wheel_center[0]
        dy = self.last_ball_position[1] - self.wheel_center[1]
        
        angle = math.atan2(dy, dx)
        return angle
    
    def detect_wheel_segments(self, frame: np.ndarray, num_segments: int = 37) -> List[float]:
        """
        Detect wheel segment positions (for European roulette).
        
        Returns:
            List of angles for each segment
        """
        if self.wheel_center is None or self.wheel_radius is None:
            return []
        
        # For now, return evenly spaced segments
        # In a real implementation, you'd detect actual segment markers
        angles = []
        for i in range(num_segments):
            angle = (2 * math.pi * i) / num_segments
            angles.append(angle)
        
        return angles
    
    def visualize_detection(self, frame: np.ndarray) -> np.ndarray:
        """
        Add visual overlays showing detected wheel and ball.
        
        Returns:
            Frame with overlays
        """
        vis_frame = frame.copy()
        
        # Draw wheel
        if self.wheel_center and self.wheel_radius:
            cv2.circle(vis_frame, self.wheel_center, self.wheel_radius, (0, 255, 0), 2)
            cv2.circle(vis_frame, self.wheel_center, 5, (0, 255, 0), -1)
        
        # Draw ball
        if self.last_ball_position:
            cv2.circle(vis_frame, self.last_ball_position, 8, (0, 0, 255), -1)
            cv2.circle(vis_frame, self.last_ball_position, 12, (0, 0, 255), 2)
        
        # Draw ball trail
        if len(self.ball_history) > 1:
            for i in range(1, len(self.ball_history)):
                cv2.line(vis_frame, self.ball_history[i-1], self.ball_history[i], (255, 0, 0), 2)
        
        # Add text info
        if self.last_ball_position and self.wheel_center:
            speed = self.calculate_ball_speed()
            angle = self.get_ball_angle()
            
            if speed:
                cv2.putText(vis_frame, f"Speed: {speed:.1f} px/s", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if angle:
                cv2.putText(vis_frame, f"Angle: {math.degrees(angle):.1f}°", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return vis_frame