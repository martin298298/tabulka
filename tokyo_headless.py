#!/usr/bin/env python3
"""
Headless Tokyo.cz Roulette Prediction Script
Analyzes live casino stream without GUI display.
Perfect for running on servers or systems without display.
"""

import cv2
import numpy as np
import time
import json
from typing import Optional, List, Tuple, Dict, Any
import subprocess
import tempfile
import os

from vision import RouletteVision
from physics import RoulettePhysics, RouletteState


class HeadlessTokyoPredictor:
    """Headless roulette prediction system for Tokyo.cz casino stream."""
    
    def __init__(self):
        self.url = "https://www.tokyo.cz/game/tomhornlive_56"
        self.vision = RouletteVision()
        self.physics = RoulettePhysics()
        self.predictions = []
        self.frame_count = 0
        self.start_time = time.time()
        self.temp_dir = tempfile.mkdtemp()
        self.session_data = []
        
    def capture_live_frame(self) -> Optional[np.ndarray]:
        """Capture frame from live casino stream."""
        try:
            # Try Chrome first (usually more reliable for headless)
            for chrome_name in ['/opt/google/chrome/chrome', 'google-chrome', 'chromium-browser', 'chromium']:
                try:
                    if os.path.exists(chrome_name) or subprocess.run(['which', chrome_name], capture_output=True, text=True).returncode == 0:
                        return self._capture_with_chrome(chrome_name)
                except:
                    continue
            
            # Try Firefox
            try:
                if subprocess.run(['which', 'firefox'], capture_output=True, text=True).returncode == 0:
                    return self._capture_with_firefox()
            except:
                pass
            
            print("❌ No browser available for capture")
            return None
            
        except Exception as e:
            print(f"⚠️  Capture error: {e}")
            return None
    
    def _capture_with_chrome(self, chrome_cmd: str) -> Optional[np.ndarray]:
        """Capture frame using Chrome/Chromium."""
        screenshot_path = os.path.join(self.temp_dir, 'live_capture.png')
        
        try:
            cmd = [
                chrome_cmd,
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080',
                '--screenshot=' + screenshot_path,
                '--incognito',
                '--noerrdialogs',
                '--no-first-run',
                '--user-data-dir=' + self.temp_dir,
                '--ozone-platform=headless',
                '--ozone-override-screen-size=800,600',
                '--use-angle=swiftshader-webgl',
                self.url
            ]
            
            result = subprocess.run(cmd, timeout=20, capture_output=True)
            
            if os.path.exists(screenshot_path):
                frame = cv2.imread(screenshot_path)
                try:
                    os.remove(screenshot_path)
                except:
                    pass
                return frame
                
        except subprocess.TimeoutExpired:
            print("⏰ Chrome capture timed out")
        except Exception as e:
            print(f"❌ Chrome capture failed: {e}")
        
        return None
    
    def _capture_with_firefox(self) -> Optional[np.ndarray]:
        """Capture frame using Firefox."""
        screenshot_path = os.path.join(self.temp_dir, 'live_capture.png')
        
        try:
            cmd = [
                'firefox',
                '--headless',
                '--screenshot=' + screenshot_path,
                '--window-size=1920,1080',
                self.url
            ]
            
            result = subprocess.run(cmd, timeout=20, capture_output=True)
            
            if os.path.exists(screenshot_path):
                frame = cv2.imread(screenshot_path)
                try:
                    os.remove(screenshot_path)
                except:
                    pass
                return frame
                
        except subprocess.TimeoutExpired:
            print("⏰ Firefox capture timed out")
        except Exception as e:
            print(f"❌ Firefox capture failed: {e}")
        
        return None
    
    def process_live_frame(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """Process captured frame and make prediction."""
        self.frame_count += 1
        timestamp = time.time()
        
        # Initialize wheel detection on first few frames
        if self.frame_count <= 3:
            wheel_center, wheel_radius = self.vision.detect_wheel(frame)
            if wheel_center:
                print(f"🎯 Wheel detected: center={wheel_center}, radius={wheel_radius}")
        
        # Detect ball position
        ball_pos = self.vision.detect_ball(frame)
        
        frame_data = {
            'frame_number': self.frame_count,
            'timestamp': timestamp,
            'ball_detected': ball_pos is not None,
            'ball_position': ball_pos,
            'wheel_center': self.vision.wheel_center,
            'wheel_radius': self.vision.wheel_radius,
            'prediction': None
        }
        
        prediction_data = None
        
        if ball_pos and self.vision.wheel_center and len(self.vision.ball_history) >= 5:
            # Create physics state from vision data
            recent_positions = self.vision.ball_history[-5:]
            state = self.physics.create_state_from_vision(
                recent_positions,
                self.vision.wheel_center,
                time_interval=0.3  # Assuming slower capture rate
            )
            
            if state:
                # Run physics simulation
                trajectory = self.physics.simulate_trajectory(state, simulation_time=15.0)
                
                if trajectory:
                    final_angle, predicted_number = self.physics.predict_landing_position(trajectory)
                    confidence = self.physics.get_prediction_confidence(trajectory)
                    
                    prediction_data = {
                        'predicted_number': predicted_number,
                        'confidence': confidence,
                        'ball_speed': self.vision.calculate_ball_speed(),
                        'ball_angle': self.vision.get_ball_angle(),
                        'simulation_time': 15.0,
                        'trajectory_length': len(trajectory)
                    }
                    
                    frame_data['prediction'] = prediction_data
                    self.predictions.append(prediction_data)
                    
                    # Keep only recent predictions
                    if len(self.predictions) > 100:
                        self.predictions.pop(0)
        
        self.session_data.append(frame_data)
        return prediction_data
    
    def save_frame_analysis(self, frame: np.ndarray, frame_number: int):
        """Save frame with analysis for review."""
        try:
            # Create analysis visualization
            vis_frame = self.vision.visualize_detection(frame.copy())
            
            # Save to file
            filename = f"/tmp/tokyo_frame_{frame_number:03d}.png"
            cv2.imwrite(filename, vis_frame)
            print(f"💾 Analysis frame saved: {filename}")
            
        except Exception as e:
            print(f"⚠️  Could not save frame: {e}")
    
    def run_analysis(self, duration_minutes: int = 10, capture_interval: float = 5.0):
        """Run analysis for specified duration."""
        print("🎰 Tokyo.cz Headless Roulette Analysis")
        print("=" * 45)
        print(f"🌐 Target URL: {self.url}")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print(f"📸 Capture interval: {capture_interval} seconds")
        print("🔍 Starting analysis...\n")
        
        end_time = time.time() + (duration_minutes * 60)
        last_capture_time = 0
        
        try:
            while time.time() < end_time:
                current_time = time.time()
                
                # Capture frame at intervals
                if current_time - last_capture_time >= capture_interval:
                    elapsed_minutes = (current_time - self.start_time) / 60
                    print(f"📸 [{elapsed_minutes:.1f}min] Capturing frame {self.frame_count + 1}...")
                    
                    frame = self.capture_live_frame()
                    last_capture_time = current_time
                    
                    if frame is not None:
                        # Process frame
                        prediction = self.process_live_frame(frame)
                        
                        # Print prediction if confident
                        if prediction:
                            conf = prediction['confidence']
                            num = prediction['predicted_number']
                            
                            if conf > 0.7:
                                print(f"🎯 HIGH CONFIDENCE: Number {num} (confidence: {conf:.2f})")
                            elif conf > 0.4:
                                print(f"🎲 Prediction: Number {num} (confidence: {conf:.2f})")
                            else:
                                print(f"💭 Low confidence prediction: {num} ({conf:.2f})")
                        else:
                            print("🔍 Analyzing... (no prediction yet)")
                        
                        # Save frame analysis periodically
                        if self.frame_count % 5 == 0:  # Every 5th frame
                            self.save_frame_analysis(frame, self.frame_count)
                            
                    else:
                        print("❌ Failed to capture frame")
                        
                    print()  # Empty line for readability
                    
                else:
                    time.sleep(1)  # Wait a bit before next check
                    
        except KeyboardInterrupt:
            print("\n⏹️  Analysis stopped by user")
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
        
        self.finalize_analysis()
    
    def finalize_analysis(self):
        """Finalize and save analysis results."""
        total_time = time.time() - self.start_time
        
        # Calculate statistics
        stats = self.calculate_statistics()
        
        # Print summary
        print("\n📊 Analysis Complete - Summary:")
        print("=" * 40)
        print(f"⏱️  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        print(f"📸 Total frames: {self.frame_count}")
        print(f"🎯 Ball detections: {stats['ball_detections']}")
        print(f"🔮 Total predictions: {len(self.predictions)}")
        print(f"⭐ High confidence predictions: {stats['high_confidence_count']}")
        
        if stats['predicted_numbers']:
            print(f"🎲 Most predicted numbers:")
            for num, count in sorted(stats['predicted_numbers'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {num:2d}: {count} times")
        
        # Save detailed results
        self.save_session_data()
        
        # Cleanup
        self.cleanup()
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate analysis statistics."""
        ball_detections = sum(1 for data in self.session_data if data['ball_detected'])
        high_confidence = [p for p in self.predictions if p['confidence'] > 0.6]
        
        # Count predicted numbers
        number_counts = {}
        for pred in high_confidence:
            num = pred['predicted_number']
            number_counts[num] = number_counts.get(num, 0) + 1
        
        return {
            'total_frames': self.frame_count,
            'ball_detections': ball_detections,
            'predictions_count': len(self.predictions),
            'high_confidence_count': len(high_confidence),
            'average_confidence': sum(p['confidence'] for p in self.predictions) / len(self.predictions) if self.predictions else 0,
            'predicted_numbers': number_counts,
            'most_predicted': max(number_counts, key=number_counts.get) if number_counts else None
        }
    
    def save_session_data(self):
        """Save complete session data to JSON file."""
        stats = self.calculate_statistics()
        
        session_report = {
            'metadata': {
                'system': 'Tokyo.cz Roulette Prediction System',
                'url': self.url,
                'timestamp': time.time(),
                'duration_seconds': time.time() - self.start_time,
                'version': '1.0.0'
            },
            'statistics': stats,
            'session_data': self.session_data,
            'predictions': self.predictions
        }
        
        filename = f"/tmp/tokyo_roulette_session_{int(time.time())}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(session_report, f, indent=2, default=str)
            print(f"📄 Session data saved: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save session data: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass


def main():
    """Main entry point."""
    print("🎰 Tokyo.cz Headless Roulette Prediction")
    print("🇨🇿 Živá analýza rulety z Tokyo.cz (bez GUI)")
    print()
    
    # Get analysis parameters
    try:
        duration_input = input("Duration in minutes (default 10): ").strip()
        duration = int(duration_input) if duration_input else 10
        
        interval_input = input("Capture interval in seconds (default 5): ").strip()
        interval = float(interval_input) if interval_input else 5.0
        
        print()
        
    except (ValueError, KeyboardInterrupt):
        print("Using default values: 10 minutes, 5 second intervals")
        duration = 10
        interval = 5.0
    
    # Run analysis
    try:
        predictor = HeadlessTokyoPredictor()
        predictor.run_analysis(duration_minutes=duration, capture_interval=interval)
    except Exception as e:
        print(f"❌ Error starting prediction system: {e}")
        print("\n💡 Make sure you have:")
        print("   - Chrome or Firefox browser installed")
        print("   - Internet connection") 
        print("   - Required Python packages (opencv-python, numpy)")


if __name__ == "__main__":
    main()