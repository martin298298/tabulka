"""
Test script for roulette prediction system components.
Tests individual modules without requiring live stream.
"""

import cv2
import numpy as np
import asyncio
import time
from unittest.mock import Mock

from vision import RouletteVision
from physics import RoulettePhysics, RouletteState


def create_test_frame_with_wheel_and_ball():
    """Create a synthetic test frame with a roulette wheel and ball."""
    # Create a black image
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    
    # Draw roulette wheel (green circle)
    wheel_center = (400, 300)
    wheel_radius = 150
    cv2.circle(frame, wheel_center, wheel_radius, (0, 100, 0), 3)
    cv2.circle(frame, wheel_center, wheel_radius - 20, (50, 50, 50), -1)
    
    # Draw wheel segments (simplified)
    for i in range(37):
        angle = (2 * np.pi * i) / 37
        x1 = int(wheel_center[0] + (wheel_radius - 40) * np.cos(angle))
        y1 = int(wheel_center[1] + (wheel_radius - 40) * np.sin(angle))
        x2 = int(wheel_center[0] + (wheel_radius - 10) * np.cos(angle))
        y2 = int(wheel_center[1] + (wheel_radius - 10) * np.sin(angle))
        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
    
    # Draw ball (white circle)
    ball_angle = np.pi / 4  # 45 degrees
    ball_radius = wheel_radius - 30
    ball_x = int(wheel_center[0] + ball_radius * np.cos(ball_angle))
    ball_y = int(wheel_center[1] + ball_radius * np.sin(ball_angle))
    cv2.circle(frame, (ball_x, ball_y), 8, (255, 255, 255), -1)
    
    return frame, wheel_center, wheel_radius, (ball_x, ball_y)


def test_vision_system():
    """Test the computer vision components."""
    print("🔍 Testing Vision System...")
    
    vision = RouletteVision()
    test_frame, expected_center, expected_radius, expected_ball = create_test_frame_with_wheel_and_ball()
    
    # Test wheel detection
    detected_center, detected_radius = vision.detect_wheel(test_frame)
    
    if detected_center:
        center_error = np.sqrt((detected_center[0] - expected_center[0])**2 + 
                             (detected_center[1] - expected_center[1])**2)
        radius_error = abs(detected_radius - expected_radius)
        
        print(f"   ✅ Wheel detected at {detected_center}, radius: {detected_radius}")
        print(f"   📏 Center error: {center_error:.1f} pixels")
        print(f"   📏 Radius error: {radius_error:.1f} pixels")
    else:
        print("   ❌ Wheel not detected")
        return False
    
    # Test ball detection
    detected_ball = vision.detect_ball(test_frame)
    
    if detected_ball:
        ball_error = np.sqrt((detected_ball[0] - expected_ball[0])**2 + 
                           (detected_ball[1] - expected_ball[1])**2)
        print(f"   ✅ Ball detected at {detected_ball}")
        print(f"   📏 Ball position error: {ball_error:.1f} pixels")
    else:
        print("   ❌ Ball not detected")
        return False
    
    # Test visualization
    vis_frame = vision.visualize_detection(test_frame)
    cv2.imwrite('/tmp/test_detection.png', vis_frame)
    print("   💾 Visualization saved to /tmp/test_detection.png")
    
    return True


def test_physics_system():
    """Test the physics simulation components."""
    print("\n⚡ Testing Physics System...")
    
    physics = RoulettePhysics()
    
    # Create test state
    test_state = RouletteState(
        ball_position=(np.pi/4, 0.12),  # 45 degrees, 12cm from center
        ball_velocity=(5.0, -0.1),      # 5 rad/s angular, slight inward
        wheel_velocity=3.0,             # 3 rad/s wheel rotation
        time=0.0
    )
    
    print(f"   🎯 Initial state: angle={test_state.ball_position[0]:.2f} rad, "
          f"radius={test_state.ball_position[1]:.3f} m")
    print(f"   🏃 Initial velocity: angular={test_state.ball_velocity[0]:.2f} rad/s, "
          f"radial={test_state.ball_velocity[1]:.3f} m/s")
    
    # Run simulation
    trajectory = physics.simulate_trajectory(test_state, simulation_time=10.0)
    
    if trajectory:
        print(f"   ✅ Simulation completed with {len(trajectory)} time steps")
        
        # Get prediction
        final_angle, predicted_number = physics.predict_landing_position(trajectory)
        confidence = physics.get_prediction_confidence(trajectory)
        
        print(f"   🎰 Predicted number: {predicted_number}")
        print(f"   📊 Confidence: {confidence:.2f}")
        print(f"   📐 Final angle: {final_angle:.2f} rad ({np.degrees(final_angle):.1f}°)")
        
        # Test state creation from vision data
        mock_positions = [(400, 300), (410, 295), (420, 290), (430, 285)]
        mock_center = (400, 300)
        
        vision_state = physics.create_state_from_vision(
            mock_positions, mock_center, time_interval=0.1
        )
        
        if vision_state:
            print("   ✅ State creation from vision data successful")
        else:
            print("   ❌ State creation from vision data failed")
            return False
    else:
        print("   ❌ Simulation failed")
        return False
    
    return True


async def test_stream_capture():
    """Test stream capture with a simple webpage."""
    print("\n📹 Testing Stream Capture...")
    
    try:
        from stream_capture import capture_single_frame
        
        # Test with a simple webpage instead of the actual casino
        test_url = "https://www.google.com"
        print(f"   🌐 Testing capture from: {test_url}")
        
        frame = await capture_single_frame(test_url)
        
        if frame is not None and frame.size > 0:
            print(f"   ✅ Frame captured successfully: {frame.shape}")
            cv2.imwrite('/tmp/test_capture.png', frame)
            print("   💾 Test capture saved to /tmp/test_capture.png")
            return True
        else:
            print("   ❌ Frame capture failed")
            return False
    
    except Exception as e:
        print(f"   ❌ Stream capture test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Roulette Prediction System - Component Tests")
    print("=" * 50)
    
    # Test results
    results = {}
    
    # Test vision system
    results['vision'] = test_vision_system()
    
    # Test physics system
    results['physics'] = test_physics_system()
    
    # Test stream capture (async)
    async def run_capture_test():
        return await test_stream_capture()
    
    try:
        results['capture'] = asyncio.run(run_capture_test())
    except Exception as e:
        print(f"   ❌ Capture test error: {e}")
        results['capture'] = False
    
    # Print summary
    print("\n📋 Test Results Summary:")
    print("-" * 30)
    
    all_passed = True
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {component.capitalize():12} {status}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 System is ready for live testing!")
        print("   Run: python main.py")
    else:
        print("\n🔧 Please fix failing components before running live system.")


if __name__ == "__main__":
    main()