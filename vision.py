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
        Detect the roulette wheel center and radius with enhanced detection for real casino streams.
        
        Returns:
            Tuple of ((center_x, center_y), radius) or (None, None)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Multiple detection strategies with different parameters
        detection_configs = [
            # Standard detection
            {'dp': 1, 'minDist': 100, 'param1': 50, 'param2': 30, 'minRadius': 50, 'maxRadius': min(frame.shape[:2]) // 2},
            # More sensitive detection
            {'dp': 1, 'minDist': 80, 'param1': 40, 'param2': 25, 'minRadius': 40, 'maxRadius': min(frame.shape[:2]) // 2},
            # Less sensitive but more robust
            {'dp': 2, 'minDist': 120, 'param1': 60, 'param2': 35, 'minRadius': 60, 'maxRadius': min(frame.shape[:2]) // 3},
            # Very sensitive for small wheels
            {'dp': 1, 'minDist': 60, 'param1': 30, 'param2': 20, 'minRadius': 30, 'maxRadius': min(frame.shape[:2]) // 2},
        ]
        
        best_circle = None
        max_score = 0
        
        for config in detection_configs:
            try:
                circles = cv2.HoughCircles(
                    blurred,
                    cv2.HOUGH_GRADIENT,
                    **config
                )
                
                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    
                    for circle in circles:
                        x, y, r = circle
                        
                        # Validate circle is within frame bounds
                        if (x - r < 0 or y - r < 0 or 
                            x + r >= frame.shape[1] or y + r >= frame.shape[0]):
                            continue
                        
                        # Score the circle based on multiple criteria
                        score = self._score_wheel_candidate(frame, x, y, r)
                        
                        if score > max_score:
                            max_score = score
                            best_circle = (x, y, r)
                            
            except Exception:
                continue
        
        if best_circle and max_score > 0.3:  # Minimum confidence threshold
            x, y, r = best_circle
            self.wheel_center = (x, y)
            self.wheel_radius = r
            print(f"   🎯 Enhanced wheel detection: center=({x}, {y}), radius={r}, confidence={max_score:.2f}")
            return (x, y), r
        
        return None, None
    
    def _score_wheel_candidate(self, frame: np.ndarray, x: int, y: int, r: int) -> float:
        """Score a wheel candidate based on visual characteristics."""
        try:
            # Extract region around the circle
            roi_size = int(r * 2.2)
            roi_x = max(0, x - roi_size // 2)
            roi_y = max(0, y - roi_size // 2)
            roi_x2 = min(frame.shape[1], roi_x + roi_size)
            roi_y2 = min(frame.shape[0], roi_y + roi_size)
            
            roi = frame[roi_y:roi_y2, roi_x:roi_x2]
            if roi.size == 0:
                return 0
            
            # Convert to different color spaces
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            score = 0.0
            
            # 1. Check for circular edge strength
            edges = cv2.Canny(roi_gray, 50, 150)
            edge_density = np.sum(edges) / (edges.shape[0] * edges.shape[1])
            score += min(edge_density * 1000, 0.3)  # Normalize edge score
            
            # 2. Check for green color (roulette table felt)
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([85, 255, 255])
            green_mask = cv2.inRange(roi_hsv, lower_green, upper_green)
            green_ratio = np.sum(green_mask) / (green_mask.shape[0] * green_mask.shape[1] * 255)
            score += min(green_ratio * 2, 0.3)  # Bonus for green areas
            
            # 3. Check for radial patterns (wheel segments)
            center_roi = (roi.shape[1] // 2, roi.shape[0] // 2)
            radial_score = self._check_radial_patterns(roi_gray, center_roi, r)
            score += radial_score * 0.2
            
            # 4. Size appropriateness (prefer medium-sized circles)
            size_score = 1.0 - abs(r - 100) / 200  # Prefer radius around 100 pixels
            score += max(0, size_score) * 0.2
            
            return score
            
        except Exception:
            return 0.0
    
    def _check_radial_patterns(self, roi_gray: np.ndarray, center: Tuple[int, int], radius: int) -> float:
        """Check for radial patterns that indicate wheel segments."""
        try:
            h, w = roi_gray.shape
            cx, cy = center
            
            # Sample points on concentric circles
            pattern_score = 0.0
            num_angles = 36  # Check every 10 degrees
            
            for angle_deg in range(0, 360, 10):
                angle_rad = np.radians(angle_deg)
                
                # Sample at different radii
                for r_factor in [0.6, 0.8]:
                    sample_r = int(radius * r_factor)
                    sample_x = int(cx + sample_r * np.cos(angle_rad))
                    sample_y = int(cy + sample_r * np.sin(angle_rad))
                    
                    if 0 <= sample_x < w and 0 <= sample_y < h:
                        # Check for intensity variations (segment boundaries)
                        if sample_x > 0 and sample_x < w - 1:
                            gradient = abs(int(roi_gray[sample_y, sample_x + 1]) - int(roi_gray[sample_y, sample_x - 1]))
                            pattern_score += gradient
            
            # Normalize by number of samples
            return min(pattern_score / (num_angles * 2 * 255), 1.0)
            
        except Exception:
            return 0.0
    
    def detect_ball(self, frame: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Detect the ball position in the frame with enhanced detection for real casino streams.
        
        Returns:
            (x, y) position of ball or None if not detected
        """
        if self.wheel_center is None:
            self.detect_wheel(frame)
            if self.wheel_center is None:
                return None
        
        # Convert to different color spaces for better detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Multiple color detection strategies
        candidates = []
        
        # Strategy 1: White ball detection (traditional)
        lower_white = np.array([0, 0, 180])  # More lenient white threshold
        upper_white = np.array([180, 55, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Strategy 2: Bright objects in LAB color space
        _, _, b_channel = cv2.split(lab)
        _, bright_mask_lab = cv2.threshold(b_channel, 140, 255, cv2.THRESH_BINARY)
        
        # Strategy 3: High brightness in gray
        _, bright_mask_gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Strategy 4: Local maxima detection (for shiny ball)
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(gray, kernel)
        local_maxima = cv2.subtract(dilated, gray)
        _, maxima_mask = cv2.threshold(local_maxima, 10, 255, cv2.THRESH_BINARY)
        
        # Combine all masks
        combined_mask = cv2.bitwise_or(white_mask, bright_mask_lab)
        combined_mask = cv2.bitwise_or(combined_mask, bright_mask_gray)
        combined_mask = cv2.bitwise_or(combined_mask, maxima_mask)
        
        # Clean up the mask with more aggressive morphological operations
        kernel_small = np.ones((2, 2), np.uint8)
        kernel_medium = np.ones((3, 3), np.uint8)
        
        # Remove noise
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel_small)
        # Fill holes
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_medium)
        
        # Create a mask for the wheel area to focus detection
        wheel_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        if self.wheel_radius:
            # Focus on the area where the ball typically moves
            inner_radius = int(self.wheel_radius * 0.3)  # Inner edge of ball track
            outer_radius = int(self.wheel_radius * 0.95)  # Outer edge of ball track
            
            cv2.circle(wheel_mask, self.wheel_center, outer_radius, 255, -1)
            cv2.circle(wheel_mask, self.wheel_center, inner_radius, 0, -1)
            
            # Apply wheel mask
            combined_mask = cv2.bitwise_and(combined_mask, wheel_mask)
        
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            for contour in contours:
                area = cv2.contourArea(contour)
                # More lenient area filtering for different ball sizes
                if 5 < area < 500:  # Broader range
                    # Check if contour is roughly circular
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * math.pi * area / (perimeter * perimeter)
                        if circularity > 0.3:  # More lenient circularity
                            M = cv2.moments(contour)
                            if M["m00"] != 0:
                                cx = int(M["m10"] / M["m00"])
                                cy = int(M["m01"] / M["m00"])
                                
                                # Check if candidate is within wheel area
                                dist_from_center = math.sqrt(
                                    (cx - self.wheel_center[0])**2 + 
                                    (cy - self.wheel_center[1])**2
                                )
                                
                                # Check if it's in the ball track area
                                if (self.wheel_radius * 0.2 < dist_from_center < self.wheel_radius * 0.95):
                                    # Calculate additional metrics for ranking
                                    brightness = gray[cy, cx] if 0 <= cy < gray.shape[0] and 0 <= cx < gray.shape[1] else 0
                                    candidates.append((cx, cy, area, circularity, brightness, dist_from_center))
        
        if candidates:
            # Rank candidates by multiple criteria
            def rank_candidate(candidate):
                cx, cy, area, circularity, brightness, dist = candidate
                # Prefer: high brightness, good circularity, reasonable size, typical distance
                score = (brightness * 0.4 + 
                        circularity * 0.3 + 
                        min(area / 100, 1.0) * 0.2 +  # Normalize area score
                        (1.0 - abs(dist - self.wheel_radius * 0.7) / (self.wheel_radius * 0.3)) * 0.1)
                return score
            
            best_candidate = max(candidates, key=rank_candidate)
            ball_pos = (best_candidate[0], best_candidate[1])
            
            # Validate against previous position if available (motion consistency)
            if self.last_ball_position:
                prev_distance = math.sqrt(
                    (ball_pos[0] - self.last_ball_position[0])**2 + 
                    (ball_pos[1] - self.last_ball_position[1])**2
                )
                # If ball moved too far too fast, it might be a false detection
                if prev_distance > self.wheel_radius * 0.3:  # More than 30% of wheel radius
                    # Look for second-best candidate that's closer to previous position
                    for candidate in sorted(candidates, key=rank_candidate, reverse=True)[1:]:
                        alt_pos = (candidate[0], candidate[1])
                        alt_distance = math.sqrt(
                            (alt_pos[0] - self.last_ball_position[0])**2 + 
                            (alt_pos[1] - self.last_ball_position[1])**2
                        )
                        if alt_distance < prev_distance * 0.7:  # Much closer to previous
                            ball_pos = alt_pos
                            break
            
            # Update history
            self.last_ball_position = ball_pos
            self.ball_history.append(ball_pos)
            
            # Keep only recent history
            if len(self.ball_history) > 15:  # Increased history for better tracking
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