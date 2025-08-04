"""
Demo script that shows the roulette prediction system working with static images.
This can be used when Playwright is not available.
"""

import cv2
import numpy as np
import time
from typing import List, Tuple

from vision import RouletteVision
from physics import RoulettePhysics, RouletteState


def create_animated_roulette_frames(num_frames: int = 50) -> List[np.ndarray]:
    """Create a sequence of frames showing ball movement around the wheel."""
    frames = []
    
    for frame_idx in range(num_frames):
        # Create a black image
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Draw roulette wheel (green circle)
        wheel_center = (400, 300)
        wheel_radius = 150
        cv2.circle(frame, wheel_center, wheel_radius, (0, 100, 0), 3)
        cv2.circle(frame, wheel_center, wheel_radius - 20, (50, 50, 50), -1)
        
        # Draw wheel segments
        for i in range(37):
            angle = (2 * np.pi * i) / 37
            x1 = int(wheel_center[0] + (wheel_radius - 40) * np.cos(angle))
            y1 = int(wheel_center[1] + (wheel_radius - 40) * np.sin(angle))
            x2 = int(wheel_center[0] + (wheel_radius - 10) * np.cos(angle))
            y2 = int(wheel_center[1] + (wheel_radius - 10) * np.sin(angle))
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
        
        # Animate ball position (spiraling inward)
        time_factor = frame_idx / num_frames
        ball_angle = 2 * np.pi * 3 * time_factor  # 3 full rotations
        ball_radius = wheel_radius - 30 - (time_factor * 40)  # Moving inward
        
        # Add some noise to make it more realistic
        noise = 5 * np.sin(ball_angle * 5)
        ball_radius += noise
        
        ball_x = int(wheel_center[0] + ball_radius * np.cos(ball_angle))
        ball_y = int(wheel_center[1] + ball_radius * np.sin(ball_angle))
        
        # Ensure ball stays visible
        ball_x = max(50, min(750, ball_x))
        ball_y = max(50, min(550, ball_y))
        
        # Draw ball (white circle with slight glow)
        cv2.circle(frame, (ball_x, ball_y), 12, (100, 100, 100), -1)
        cv2.circle(frame, (ball_x, ball_y), 8, (255, 255, 255), -1)
        
        # Add frame number for reference
        cv2.putText(frame, f"Frame: {frame_idx+1}/{num_frames}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        frames.append(frame)
    
    return frames


def run_demo():
    """Run the complete roulette prediction demo."""
    print("🎰 Roulette Prediction System - Demo Mode")
    print("=" * 50)
    print("This demo shows the system analyzing animated roulette frames.")
    print("Press ESC to exit, SPACE to pause/resume")
    print()
    
    # Initialize components
    vision = RouletteVision()
    physics = RoulettePhysics()
    
    # Create animated frames
    print("📹 Generating animated roulette frames...")
    frames = create_animated_roulette_frames(50)
    print(f"   Generated {len(frames)} frames")
    
    # Process frames
    predictions = []
    frame_idx = 0
    paused = False
    
    print("\n🔍 Starting analysis...")
    print("Controls: ESC=quit, SPACE=pause/resume, 's'=save screenshot")
    
    while frame_idx < len(frames):
        frame = frames[frame_idx]
        
        # Detect wheel and ball
        if frame_idx == 0:
            # Initialize wheel detection on first frame
            wheel_center, wheel_radius = vision.detect_wheel(frame)
            if wheel_center:
                print(f"   🎯 Wheel detected at {wheel_center}, radius: {wheel_radius}")
        
        ball_pos = vision.detect_ball(frame)
        
        # Make prediction if we have enough data
        if ball_pos and len(vision.ball_history) >= 5:
            # Create physics state
            state = physics.create_state_from_vision(
                vision.ball_history[-5:],
                vision.wheel_center,
                time_interval=0.1,
                wheel_angular_velocity=3.0
            )
            
            if state:
                # Run simulation
                trajectory = physics.simulate_trajectory(state, simulation_time=10.0)
                
                if trajectory:
                    final_angle, predicted_number = physics.predict_landing_position(trajectory)
                    confidence = physics.get_prediction_confidence(trajectory)
                    
                    prediction = {
                        'frame': frame_idx,
                        'number': predicted_number,
                        'confidence': confidence,
                        'ball_speed': vision.calculate_ball_speed(),
                        'ball_angle': vision.get_ball_angle()
                    }
                    
                    predictions.append(prediction)
                    
                    # Print high-confidence predictions
                    if confidence > 0.5:
                        print(f"   🎯 Frame {frame_idx:2d}: Predicted {predicted_number:2d} "
                              f"(confidence: {confidence:.2f})")
        
        # Create visualization
        vis_frame = vision.visualize_detection(frame)
        
        # Add prediction info
        if predictions:
            latest = predictions[-1]
            cv2.putText(vis_frame, f"Prediction: {latest['number']}", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(vis_frame, f"Confidence: {latest['confidence']:.2f}", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add demo info
        cv2.putText(vis_frame, "DEMO MODE - Simulated Data", 
                   (10, vis_frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(vis_frame, "ESC=quit SPACE=pause 's'=save", 
                   (10, vis_frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display frame
        cv2.imshow('Roulette Prediction Demo', vis_frame)
        
        # Handle keyboard input
        key = cv2.waitKey(100) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == ord(' '):  # SPACE
            paused = not paused
            print(f"   {'⏸️  Paused' if paused else '▶️  Resumed'}")
        elif key == ord('s'):  # Save screenshot
            filename = f'/tmp/roulette_demo_frame_{frame_idx:03d}.png'
            cv2.imwrite(filename, vis_frame)
            print(f"   💾 Screenshot saved: {filename}")
        
        if not paused:
            frame_idx += 1
    
    cv2.destroyAllWindows()
    
    # Print results summary
    print(f"\n📊 Demo Results:")
    print(f"   Total frames processed: {frame_idx}")
    print(f"   Total predictions made: {len(predictions)}")
    
    if predictions:
        high_confidence = [p for p in predictions if p['confidence'] > 0.5]
        print(f"   High confidence predictions: {len(high_confidence)}")
        
        if high_confidence:
            # Count most predicted numbers
            number_counts = {}
            for pred in high_confidence:
                num = pred['number']
                number_counts[num] = number_counts.get(num, 0) + 1
            
            print(f"   Number predictions:")
            for num, count in sorted(number_counts.items()):
                print(f"     {num:2d}: {count} times")
            
            avg_confidence = sum(p['confidence'] for p in high_confidence) / len(high_confidence)
            print(f"   Average confidence: {avg_confidence:.2f}")
    
    print("\n✅ Demo completed successfully!")


def run_static_image_test():
    """Test with a single static image."""
    print("\n🖼️  Static Image Test")
    print("-" * 30)
    
    vision = RouletteVision()
    physics = RoulettePhysics()
    
    # Create test frame
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    wheel_center = (400, 300)
    wheel_radius = 150
    
    # Draw wheel
    cv2.circle(frame, wheel_center, wheel_radius, (0, 100, 0), 3)
    cv2.circle(frame, wheel_center, wheel_radius - 20, (50, 50, 50), -1)
    
    # Draw ball
    ball_angle = np.pi / 3  # 60 degrees
    ball_radius = wheel_radius - 40
    ball_x = int(wheel_center[0] + ball_radius * np.cos(ball_angle))
    ball_y = int(wheel_center[1] + ball_radius * np.sin(ball_angle))
    cv2.circle(frame, (ball_x, ball_y), 8, (255, 255, 255), -1)
    
    # Test detection
    detected_center, detected_radius = vision.detect_wheel(frame)
    detected_ball = vision.detect_ball(frame)
    
    print(f"   Wheel: {detected_center}, radius: {detected_radius}")
    print(f"   Ball: {detected_ball}")
    
    # Create visualization
    vis_frame = vision.visualize_detection(frame)
    cv2.imwrite('/tmp/static_test.png', vis_frame)
    print("   💾 Result saved to /tmp/static_test.png")


if __name__ == "__main__":
    try:
        run_static_image_test()
        run_demo()
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        cv2.destroyAllWindows()