"""
Main application for roulette prediction system.
Integrates stream capture, computer vision, and physics prediction.
"""

import asyncio
import cv2
import numpy as np
import time
from typing import Optional, List, Tuple

from stream_capture import StreamCapture
from vision import RouletteVision
from physics import RoulettePhysics, RouletteState


class RoulettePredictionSystem:
    def __init__(self, url: str, headless: bool = False):
        self.url = url
        self.stream_capture = StreamCapture(url, headless=headless)
        self.vision = RouletteVision()
        self.physics = RoulettePhysics()
        
        self.is_running = False
        self.predictions = []
        self.frame_count = 0
        self.start_time = time.time()
        
        # Performance tracking
        self.fps = 0
        self.last_fps_time = time.time()
        
    async def initialize(self):
        """Initialize all components."""
        print("Initializing roulette prediction system...")
        await self.stream_capture.initialize()
        print("Stream capture initialized")
        
        # Capture a few frames to initialize vision system
        print("Calibrating vision system...")
        for i in range(3):
            frame = await self.stream_capture.capture_roulette_area()
            self.vision.detect_wheel(frame)
            await asyncio.sleep(0.5)
        
        if self.vision.wheel_center and self.vision.wheel_radius:
            print(f"Wheel detected at center: {self.vision.wheel_center}, radius: {self.vision.wheel_radius}")
        else:
            print("Warning: Could not detect wheel. Predictions may be inaccurate.")
    
    async def process_frame(self, frame: np.ndarray):
        """Process a single frame for prediction."""
        self.frame_count += 1
        
        # Update FPS counter
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.start_time)
            self.last_fps_time = current_time
        
        # Detect ball position
        ball_pos = self.vision.detect_ball(frame)
        
        if ball_pos and self.vision.wheel_center:
            # Create physics state from vision data
            ball_positions = self.vision.ball_history[-5:]  # Use last 5 positions
            if len(ball_positions) >= 2:
                state = self.physics.create_state_from_vision(
                    ball_positions,
                    self.vision.wheel_center,
                    time_interval=0.1  # Assuming 10 FPS capture
                )
                
                if state:
                    # Run physics simulation
                    trajectory = self.physics.simulate_trajectory(state, simulation_time=15.0)
                    
                    if trajectory:
                        # Get prediction
                        final_angle, predicted_number = self.physics.predict_landing_position(trajectory)
                        confidence = self.physics.get_prediction_confidence(trajectory)
                        
                        # Store prediction
                        prediction = {
                            'time': current_time,
                            'number': predicted_number,
                            'confidence': confidence,
                            'ball_speed': self.vision.calculate_ball_speed(),
                            'ball_angle': self.vision.get_ball_angle()
                        }
                        
                        self.predictions.append(prediction)
                        
                        # Keep only recent predictions
                        if len(self.predictions) > 100:
                            self.predictions.pop(0)
                        
                        # Print prediction if confidence is high
                        if confidence > 0.6:
                            print(f"🎯 PREDICTION: Number {predicted_number} "
                                  f"(Confidence: {confidence:.2f})")
        
        # Display visualization
        vis_frame = self.vision.visualize_detection(frame)
        
        # Add prediction info to frame
        if self.predictions:
            latest = self.predictions[-1]
            cv2.putText(vis_frame, f"Predicted: {latest['number']}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(vis_frame, f"Confidence: {latest['confidence']:.2f}", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add performance info
        cv2.putText(vis_frame, f"FPS: {self.fps:.1f}", 
                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(vis_frame, f"Frames: {self.frame_count}", 
                   (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow('Roulette Prediction System', vis_frame)
        
        # Handle quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop()
    
    async def run(self):
        """Start the main prediction loop."""
        self.is_running = True
        print("🎰 Starting roulette prediction system...")
        print("Press 'q' to quit")
        
        try:
            await self.stream_capture.start_continuous_capture(
                self.process_frame, 
                interval=0.1  # 10 FPS
            )
        except KeyboardInterrupt:
            print("\n⏹️  Stopping...")
        finally:
            await self.cleanup()
    
    def stop(self):
        """Stop the prediction system."""
        self.is_running = False
        self.stream_capture.stop_capture()
    
    async def cleanup(self):
        """Clean up resources."""
        cv2.destroyAllWindows()
        await self.stream_capture.cleanup()
        
        # Print final statistics
        total_time = time.time() - self.start_time
        print(f"\n📊 Session Statistics:")
        print(f"   Total time: {total_time:.1f} seconds")
        print(f"   Total frames: {self.frame_count}")
        print(f"   Average FPS: {self.frame_count / total_time:.1f}")
        print(f"   Total predictions: {len(self.predictions)}")
        
        if self.predictions:
            high_confidence = [p for p in self.predictions if p['confidence'] > 0.6]
            print(f"   High confidence predictions: {len(high_confidence)}")
            
            if high_confidence:
                most_predicted = {}
                for pred in high_confidence:
                    num = pred['number']
                    most_predicted[num] = most_predicted.get(num, 0) + 1
                
                if most_predicted:
                    best_number = max(most_predicted, key=most_predicted.get)
                    print(f"   Most predicted number: {best_number} ({most_predicted[best_number]} times)")


async def main():
    """Main entry point."""
    # Default URL for the specified casino
    url = "https://www.tokyo.cz/game/tomhornlive_56"
    
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
    print()
    
    # Create and run prediction system
    system = RoulettePredictionSystem(url, headless=headless)
    
    try:
        await system.initialize()
        await system.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        await system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())