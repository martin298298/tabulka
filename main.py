"""
Main application for roulette prediction system.
Integrates stream capture, computer vision, and physics prediction.
"""

import asyncio
import cv2
import numpy as np
import time
from typing import Optional, List, Tuple

# Try to import different capture methods
capture_method = None
try:
    from stream_capture import StreamCapture
    capture_method = "playwright"
    print("✓ Playwright capture available")
except Exception as e:
    print(f"⚠️  Playwright capture not available: {e}")

try:
    from alternative_selenium_capture import SeleniumStreamCapture
    if capture_method is None:
        capture_method = "selenium"
    print("✓ Selenium capture available as fallback")
except Exception as e:
    print(f"⚠️  Selenium capture not available: {e}")

from vision import RouletteVision
from physics import RoulettePhysics, RouletteState
from tts_system import get_tts_system, cleanup_tts


class RoulettePredictionSystem:
    def __init__(self, url: str, headless: bool = False, email: str = None, password: str = None):
        self.url = url
        
        # Initialize capture system with fallback
        if capture_method == "playwright":
            try:
                self.stream_capture = StreamCapture(url, headless=headless, email=email, password=password)
                self.capture_type = "Playwright"
            except Exception as e:
                print(f"⚠️  Playwright failed, trying Selenium: {e}")
                if capture_method == "selenium":
                    self.stream_capture = SeleniumStreamCapture(url, headless=headless, email=email, password=password)
                    self.capture_type = "Selenium"
                else:
                    raise RuntimeError("No capture method available")
        elif capture_method == "selenium":
            self.stream_capture = SeleniumStreamCapture(url, headless=headless, email=email, password=password)
            self.capture_type = "Selenium"
        else:
            raise RuntimeError("No capture method available. Please install Playwright or Selenium.")
        
        self.vision = RouletteVision()
        self.physics = RoulettePhysics()
        
        # Initialize TTS system
        self.tts = get_tts_system()
        
        self.is_running = False
        self.predictions = []
        self.frame_count = 0
        self.start_time = time.time()
        
        # Enhanced performance tracking
        self.fps = 0
        self.last_fps_time = time.time()
        self.processing_times = []
        self.successful_detections = 0
        self.total_predictions = 0
        
    async def initialize(self):
        """Initialize all components with enhanced error handling."""
        print("Initializing roulette prediction system...")
        print(f"📹 Using {self.capture_type} capture method")
        
        try:
            if hasattr(self.stream_capture, 'initialize'):
                if asyncio.iscoroutinefunction(self.stream_capture.initialize):
                    await self.stream_capture.initialize()
                else:
                    self.stream_capture.initialize()
            print("Stream capture initialized")
        except Exception as e:
            print(f"❌ Stream capture initialization failed: {e}")
            raise
        
        # Capture a few frames to initialize vision system
        print("Calibrating vision system...")
        calibration_frames = 0
        max_calibration_attempts = 10
        
        for i in range(max_calibration_attempts):
            try:
                if hasattr(self.stream_capture, 'capture_roulette_area'):
                    if asyncio.iscoroutinefunction(self.stream_capture.capture_roulette_area):
                        frame = await self.stream_capture.capture_roulette_area()
                    else:
                        frame = self.stream_capture.capture_roulette_area()
                else:
                    # Fallback method
                    if asyncio.iscoroutinefunction(self.stream_capture.capture_frame):
                        full_frame = await self.stream_capture.capture_frame()
                    else:
                        full_frame = self.stream_capture.capture_frame()
                    
                    # Extract roulette area
                    if hasattr(self.stream_capture, 'find_roulette_area'):
                        if asyncio.iscoroutinefunction(self.stream_capture.find_roulette_area):
                            x, y, w, h = await self.stream_capture.find_roulette_area(full_frame)
                        else:
                            x, y, w, h = self.stream_capture.find_roulette_area(full_frame)
                        frame = full_frame[y:y+h, x:x+w]
                    else:
                        frame = full_frame
                
                # Try to detect wheel
                wheel_center, wheel_radius = self.vision.detect_wheel(frame)
                if wheel_center and wheel_radius:
                    calibration_frames += 1
                    print(f"   Calibration frame {calibration_frames}: wheel detected")
                
                if calibration_frames >= 3:
                    break
                    
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   Calibration attempt {i+1} failed: {e}")
                await asyncio.sleep(1)
        
        if self.vision.wheel_center and self.vision.wheel_radius:
            print(f"✓ Wheel calibrated: center={self.vision.wheel_center}, radius={self.vision.wheel_radius}")
        else:
            print("⚠️  Warning: Could not calibrate wheel detection. Predictions may be inaccurate.")
    
    async def process_frame(self, frame: np.ndarray):
        """Process a single frame for prediction with enhanced performance tracking."""
        frame_start_time = time.time()
        self.frame_count += 1
        
        # Update FPS counter
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.start_time)
            self.last_fps_time = current_time
        
        # Detect ball position
        ball_pos = self.vision.detect_ball(frame)
        
        if ball_pos:
            self.successful_detections += 1
            
            if self.vision.wheel_center and len(self.vision.ball_history) >= 3:  # Reduced minimum for faster predictions
                # Create physics state from vision data
                ball_positions = self.vision.ball_history[-7:]  # Use more history for better accuracy
                
                state = self.physics.create_state_from_vision(
                    ball_positions,
                    self.vision.wheel_center,
                    time_interval=0.1  # Assuming 10 FPS capture
                )
                
                if state:
                    # Run physics simulation
                    trajectory = self.physics.simulate_trajectory(state, simulation_time=12.0)  # Slightly longer simulation
                    
                    if trajectory:
                        # Get prediction
                        final_angle, predicted_number = self.physics.predict_landing_position(trajectory)
                        confidence = self.physics.get_prediction_confidence(trajectory)
                        
                        # Store prediction
                        prediction = {
                            'time': current_time,
                            'frame': self.frame_count,
                            'number': predicted_number,
                            'confidence': confidence,
                            'ball_speed': self.vision.calculate_ball_speed(),
                            'ball_angle': self.vision.get_ball_angle(),
                            'ball_position': ball_pos,
                            'detection_success_rate': self.successful_detections / self.frame_count
                        }
                        
                        self.predictions.append(prediction)
                        self.total_predictions += 1
                        
                        # Keep only recent predictions
                        if len(self.predictions) > 50:  # Reduced memory usage
                            self.predictions.pop(0)
                        
                        # Print prediction if confidence is reasonable
                        if confidence > 0.4:  # Lower threshold for more feedback
                            prediction_text = f"PREDICTION #{self.total_predictions}: Number {predicted_number} (Confidence: {confidence:.2f}, Speed: {prediction['ball_speed']:.1f})"
                            print(f"🎯 {prediction_text}")
                            
                            # Announce prediction via TTS
                            self.tts.speak_prediction(f"Number {predicted_number}", confidence)
        
        # Create enhanced visualization
        vis_frame = self.vision.visualize_detection(frame)
        
        # Add comprehensive prediction info
        info_y = 30
        line_height = 25
        
        # System info
        cv2.putText(vis_frame, f"System: {self.capture_type} | FPS: {self.fps:.1f}", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        info_y += line_height
        
        cv2.putText(vis_frame, f"Frames: {self.frame_count} | Detections: {self.successful_detections}", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        info_y += line_height
        
        # Detection success rate
        if self.frame_count > 0:
            success_rate = self.successful_detections / self.frame_count
            color = (0, 255, 0) if success_rate > 0.7 else (0, 255, 255) if success_rate > 0.4 else (0, 0, 255)
            cv2.putText(vis_frame, f"Detection Rate: {success_rate:.2f}", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            info_y += line_height
        
        # Latest prediction
        if self.predictions:
            latest = self.predictions[-1]
            confidence_color = (0, 255, 0) if latest['confidence'] > 0.7 else (0, 255, 255) if latest['confidence'] > 0.4 else (0, 0, 255)
            
            cv2.putText(vis_frame, f"Predicted: {latest['number']}", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, confidence_color, 2)
            info_y += line_height
            
            cv2.putText(vis_frame, f"Confidence: {latest['confidence']:.2f}", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, confidence_color, 2)
            info_y += line_height
            
            if latest['ball_speed']:
                cv2.putText(vis_frame, f"Ball Speed: {latest['ball_speed']:.1f} px/s", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                info_y += line_height
        
        # Show frame
        cv2.imshow('Roulette Prediction System - Enhanced', vis_frame)
        
        # Track processing time
        processing_time = time.time() - frame_start_time
        self.processing_times.append(processing_time)
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)
        
        # Handle quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
    
    async def run(self):
        """Start the main prediction loop with enhanced performance."""
        self.is_running = True
        print("🎰 Starting roulette prediction system...")
        print("Press 'q' to quit")
        
        try:
            # Adaptive FPS based on system performance
            target_fps = 15  # Start with higher FPS target
            interval = 1.0 / target_fps
            
            if hasattr(self.stream_capture, 'start_continuous_capture'):
                if asyncio.iscoroutinefunction(self.stream_capture.start_continuous_capture):
                    await self.stream_capture.start_continuous_capture(
                        self.process_frame, 
                        interval=interval
                    )
                else:
                    # Synchronous version - wrap in async
                    def sync_callback(frame):
                        asyncio.create_task(self.process_frame(frame))
                    
                    self.stream_capture.start_continuous_capture(sync_callback, interval)
            else:
                # Manual capture loop for basic implementations
                print("Using manual capture loop...")
                while self.is_running:
                    try:
                        if hasattr(self.stream_capture, 'capture_roulette_area'):
                            if asyncio.iscoroutinefunction(self.stream_capture.capture_roulette_area):
                                frame = await self.stream_capture.capture_roulette_area()
                            else:
                                frame = self.stream_capture.capture_roulette_area()
                        else:
                            frame = await self.stream_capture.capture_frame()
                        
                        await self.process_frame(frame)
                        await asyncio.sleep(interval)
                        
                    except Exception as e:
                        print(f"Manual capture error: {e}")
                        await asyncio.sleep(1)
                        
        except KeyboardInterrupt:
            print("\n⏹️  Stopping...")
        finally:
            await self.cleanup()
    
    def stop(self):
        """Stop the prediction system."""
        self.is_running = False
        self.stream_capture.stop_capture()
    
    async def cleanup(self):
        """Clean up resources with enhanced statistics."""
        cv2.destroyAllWindows()
        
        # Cleanup capture system
        if hasattr(self.stream_capture, 'cleanup'):
            if asyncio.iscoroutinefunction(self.stream_capture.cleanup):
                await self.stream_capture.cleanup()
            else:
                self.stream_capture.cleanup()
        
        # Cleanup TTS system
        cleanup_tts()
        
        # Print comprehensive final statistics
        total_time = time.time() - self.start_time
        print(f"\n📊 Enhanced Session Statistics:")
        print(f"   Total time: {total_time:.1f} seconds")
        print(f"   Total frames: {self.frame_count}")
        print(f"   Successful detections: {self.successful_detections}")
        print(f"   Detection rate: {self.successful_detections/self.frame_count:.2%}" if self.frame_count > 0 else "   Detection rate: 0%")
        print(f"   Average FPS: {self.frame_count / total_time:.1f}")
        print(f"   Total predictions: {self.total_predictions}")
        
        if self.processing_times:
            avg_processing = sum(self.processing_times) / len(self.processing_times)
            print(f"   Average processing time: {avg_processing:.3f}s per frame")
            print(f"   Max processing time: {max(self.processing_times):.3f}s")
            print(f"   Min processing time: {min(self.processing_times):.3f}s")
        
        if self.predictions:
            high_confidence = [p for p in self.predictions if p['confidence'] > 0.6]
            medium_confidence = [p for p in self.predictions if 0.4 <= p['confidence'] <= 0.6]
            
            print(f"   High confidence predictions (>0.6): {len(high_confidence)}")
            print(f"   Medium confidence predictions (0.4-0.6): {len(medium_confidence)}")
            
            if high_confidence:
                most_predicted = {}
                for pred in high_confidence:
                    num = pred['number']
                    most_predicted[num] = most_predicted.get(num, 0) + 1
                
                if most_predicted:
                    best_number = max(most_predicted, key=most_predicted.get)
                    print(f"   Most predicted number: {best_number} ({most_predicted[best_number]} times)")
                    
                    # Show top 3 predictions
                    sorted_predictions = sorted(most_predicted.items(), key=lambda x: x[1], reverse=True)
                    print(f"   Top predictions: {', '.join([f'{num}({count})' for num, count in sorted_predictions[:3]])}")
                
                avg_confidence = sum(p['confidence'] for p in high_confidence) / len(high_confidence)
                print(f"   Average high confidence: {avg_confidence:.3f}")
        
        print(f"\n🎯 System Performance Summary:")
        print(f"   Capture Method: {self.capture_type}")
        print(f"   Overall Success Rate: {(self.total_predictions/self.frame_count)*100:.1f}%" if self.frame_count > 0 else "   Overall Success Rate: 0%")


async def main():
    """Main entry point."""
    # Default URL for the specified casino
    url = "https://www.tokyo.cz/game/tomhornlive_56"
    
    # Default credentials from problem statement
    email = "martin298@post.cz"
    password = "Certik298"
    
    print("🎰 Roulette Prediction System")
    print("=" * 40)
    print("This system analyzes live roulette streams to predict ball landing positions.")
    print("⚠️  For educational and research purposes only!")
    print()
    
    # Allow user to specify different URL
    user_url = input(f"Stream URL (press Enter for default: {url}): ").strip()
    if user_url:
        url = user_url
    
    # Ask about headless mode
    headless_input = input("Run browser in headless mode? (y/N): ").strip().lower()
    headless = headless_input in ['y', 'yes']
    
    print(f"\n🌐 Target URL: {url}")
    print(f"🖥️  Headless mode: {headless}")
    print(f"🔐 Using login credentials: {email}")
    print()
    
    # Create and run prediction system
    system = RoulettePredictionSystem(url, headless=headless, email=email, password=password)
    
    try:
        await system.initialize()
        await system.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        await system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())