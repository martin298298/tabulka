#!/usr/bin/env python3
"""
Live Roulette Prediction Script for https://www.tokyo.cz/game/tomhornlive_56
Analyzes live casino stream and predicts ball landing positions.
"""

import cv2
import numpy as np
import time
import asyncio
from typing import Optional, List, Tuple
import subprocess
import tempfile
import os

from vision import RouletteVision
from physics import RoulettePhysics, RouletteState


class TokyoRoulettePredictor:
    """Live roulette prediction system for Tokyo.cz casino stream."""
    
    def __init__(self):
        self.url = "https://www.tokyo.cz/game/tomhornlive_56"
        self.vision = RouletteVision()
        self.physics = RoulettePhysics()
        self.predictions = []
        self.frame_count = 0
        self.start_time = time.time()
        self.temp_dir = tempfile.mkdtemp()
        
    def capture_live_frame(self) -> Optional[np.ndarray]:
        """Capture frame from live casino stream."""
        try:
            # Try Chrome first
            for chrome_name in ['google-chrome', 'chromium-browser', 'chromium']:
                result = subprocess.run(['which', chrome_name], capture_output=True, text=True)
                if result.returncode == 0:
                    return self._capture_with_browser(chrome_name, "chrome")
            
            # Try Firefox
            result = subprocess.run(['which', 'firefox'], capture_output=True, text=True)
            if result.returncode == 0:
                return self._capture_with_browser('firefox', "firefox")
            
            print("❌ No browser available for capture")
            return None
            
        except Exception as e:
            print(f"⚠️  Capture error: {e}")
            return None
    
    def _capture_with_browser(self, browser_cmd: str, browser_type: str) -> Optional[np.ndarray]:
        """Capture frame using specified browser."""
        screenshot_path = os.path.join(self.temp_dir, 'live_capture.png')
        
        try:
            if browser_type == "chrome":
                cmd = [
                    browser_cmd,
                    '--headless',
                    '--disable-gpu', 
                    '--no-sandbox',
                    '--disable-web-security',
                    '--window-size=1920,1080',
                    '--screenshot=' + screenshot_path,
                    '--incognito',
                    '--noerrdialogs',
                    '--no-first-run',
                    self.url
                ]
            else:  # firefox
                cmd = [
                    browser_cmd,
                    '--headless',
                    '--screenshot=' + screenshot_path,
                    '--window-size=1920,1080',
                    self.url
                ]
            
            # Capture with timeout
            result = subprocess.run(cmd, timeout=15, capture_output=True)
            
            if os.path.exists(screenshot_path):
                frame = cv2.imread(screenshot_path)
                try:
                    os.remove(screenshot_path)
                except:
                    pass
                return frame
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {browser_type.title()} capture timed out")
        except Exception as e:
            print(f"❌ {browser_type.title()} capture failed: {e}")
        
        return None
    
    def process_live_frame(self, frame: np.ndarray) -> Optional[dict]:
        """Process captured frame and make prediction."""
        self.frame_count += 1
        
        # Initialize wheel detection on first few frames
        if self.frame_count <= 3:
            self.vision.detect_wheel(frame)
            if self.vision.wheel_center:
                print(f"🎯 Wheel detected: center={self.vision.wheel_center}, radius={self.vision.wheel_radius}")
        
        # Detect ball position
        ball_pos = self.vision.detect_ball(frame)
        
        prediction_data = None
        
        if ball_pos and self.vision.wheel_center and len(self.vision.ball_history) >= 5:
            # Create physics state from vision data
            recent_positions = self.vision.ball_history[-5:]
            state = self.physics.create_state_from_vision(
                recent_positions,
                self.vision.wheel_center,
                time_interval=0.2  # Assuming ~5 FPS capture
            )
            
            if state:
                # Run physics simulation
                trajectory = self.physics.simulate_trajectory(state, simulation_time=15.0)
                
                if trajectory:
                    final_angle, predicted_number = self.physics.predict_landing_position(trajectory)
                    confidence = self.physics.get_prediction_confidence(trajectory)
                    
                    prediction_data = {
                        'time': time.time(),
                        'frame': self.frame_count,
                        'predicted_number': predicted_number,
                        'confidence': confidence,
                        'ball_position': ball_pos,
                        'ball_speed': self.vision.calculate_ball_speed(),
                        'ball_angle': self.vision.get_ball_angle()
                    }
                    
                    self.predictions.append(prediction_data)
                    
                    # Keep only recent predictions
                    if len(self.predictions) > 50:
                        self.predictions.pop(0)
        
        return prediction_data
    
    def display_frame(self, frame: np.ndarray, prediction: Optional[dict] = None):
        """Display frame with prediction overlay."""
        # Create visualization
        vis_frame = self.vision.visualize_detection(frame.copy())
        
        # Add header
        cv2.putText(vis_frame, "Tokyo.cz Live Roulette Prediction", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        # Add prediction info
        if prediction:
            confidence = prediction['confidence']
            color = (0, 255, 0) if confidence > 0.6 else (0, 255, 255) if confidence > 0.3 else (0, 0, 255)
            
            cv2.putText(vis_frame, f"Predicted: {prediction['predicted_number']}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(vis_frame, f"Confidence: {confidence:.2f}", 
                       (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            if confidence > 0.6:
                cv2.putText(vis_frame, "HIGH CONFIDENCE!", 
                           (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add frame counter and status
        cv2.putText(vis_frame, f"Frame: {self.frame_count}", 
                   (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        if self.vision.wheel_center:
            cv2.putText(vis_frame, "Wheel: DETECTED", 
                       (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        else:
            cv2.putText(vis_frame, "Wheel: SEARCHING...", 
                       (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        # Show predictions history
        if len(self.predictions) > 0:
            recent_predictions = self.predictions[-5:]  # Last 5 predictions
            y_offset = 220
            cv2.putText(vis_frame, "Recent Predictions:", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            for i, pred in enumerate(recent_predictions):
                y = y_offset + 25 + (i * 20)
                conf_color = (0, 255, 0) if pred['confidence'] > 0.6 else (0, 255, 255)
                cv2.putText(vis_frame, f"{pred['predicted_number']:2d} ({pred['confidence']:.2f})", 
                           (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, conf_color, 1)
        
        # Add instructions
        cv2.putText(vis_frame, "Press 'q' to quit, 's' to save frame", 
                   (10, vis_frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow('Tokyo.cz Roulette Prediction', vis_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False
        elif key == ord('s'):
            filename = f"/tmp/tokyo_roulette_frame_{self.frame_count}.png"
            cv2.imwrite(filename, vis_frame)
            print(f"💾 Frame saved to {filename}")
        
        return True
    
    def run_live_prediction(self):
        """Main live prediction loop."""
        print("🎰 Tokyo.cz Live Roulette Prediction System")
        print("=" * 50)
        print(f"🌐 Target URL: {self.url}")
        print("🔍 Starting live analysis...")
        print("⌨️  Press 'q' to quit, 's' to save frame")
        print()
        
        frame_interval = 3.0  # Capture every 3 seconds
        last_capture_time = 0
        
        try:
            while True:
                current_time = time.time()
                
                # Capture frame at intervals
                if current_time - last_capture_time >= frame_interval:
                    print(f"📸 Capturing frame {self.frame_count + 1}...")
                    frame = self.capture_live_frame()
                    last_capture_time = current_time
                    
                    if frame is not None:
                        # Process frame
                        prediction = self.process_live_frame(frame)
                        
                        # Print prediction if confident
                        if prediction and prediction['confidence'] > 0.5:
                            print(f"🎯 PREDICTION: Number {prediction['predicted_number']} "
                                  f"(Confidence: {prediction['confidence']:.2f})")
                        
                        # Display frame
                        if not self.display_frame(frame, prediction):
                            break
                    else:
                        print("❌ Failed to capture frame from live stream")
                        time.sleep(1)
                else:
                    # Keep the display updated
                    cv2.waitKey(100)
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        cv2.destroyAllWindows()
        
        # Clean up temp files
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass
        
        # Print statistics
        total_time = time.time() - self.start_time
        print(f"\n📊 Session Statistics:")
        print(f"   Total frames: {self.frame_count}")
        print(f"   Session time: {total_time:.1f} seconds")
        print(f"   Total predictions: {len(self.predictions)}")
        
        if self.predictions:
            high_confidence = [p for p in self.predictions if p['confidence'] > 0.6]
            print(f"   High confidence predictions: {len(high_confidence)}")
            
            if high_confidence:
                # Show most predicted numbers
                number_counts = {}
                for pred in high_confidence:
                    num = pred['predicted_number']
                    number_counts[num] = number_counts.get(num, 0) + 1
                
                if number_counts:
                    best_number = max(number_counts, key=number_counts.get)
                    print(f"   Most predicted number: {best_number} ({number_counts[best_number]} times)")


def main():
    """Main entry point."""
    print("🎰 Tokyo.cz Live Roulette Prediction")
    print("🇨🇿 Živá analýza rulety z Tokyo.cz")
    print()
    
    # Check if we can run
    try:
        predictor = TokyoRoulettePredictor()
        predictor.run_live_prediction()
    except Exception as e:
        print(f"❌ Error starting prediction system: {e}")
        print("\n💡 Make sure you have:")
        print("   - Chrome or Firefox browser installed")
        print("   - Internet connection") 
        print("   - Required Python packages (opencv-python, numpy)")


if __name__ == "__main__":
    main()