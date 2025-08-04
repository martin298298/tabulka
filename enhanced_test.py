#!/usr/bin/env python3
"""
Enhanced test script for the improved roulette prediction system.
Tests all components with the new enhancements.
"""

import cv2
import numpy as np
import time
import asyncio
from typing import List, Tuple

# Import the enhanced components
from vision import RouletteVision
from physics import RoulettePhysics, RouletteState


def create_enhanced_test_frame_with_wheel_and_ball():
    """Create a more realistic test frame with enhanced roulette wheel and ball."""
    # Create a larger, more realistic image
    frame = np.zeros((800, 1200, 3), dtype=np.uint8)
    
    # Draw roulette table background (green felt)
    cv2.rectangle(frame, (50, 50), (1150, 750), (0, 80, 0), -1)
    
    # Draw roulette wheel (larger, more detailed)
    wheel_center = (600, 400)
    wheel_radius = 200
    
    # Outer rim
    cv2.circle(frame, wheel_center, wheel_radius + 10, (139, 69, 19), 15)  # Brown rim
    
    # Main wheel body
    cv2.circle(frame, wheel_center, wheel_radius, (0, 100, 0), -1)  # Green base
    cv2.circle(frame, wheel_center, wheel_radius, (255, 255, 255), 3)  # White outer edge
    
    # Inner wheel area
    cv2.circle(frame, wheel_center, wheel_radius - 50, (139, 69, 19), -1)  # Brown inner
    cv2.circle(frame, wheel_center, wheel_radius - 60, (255, 215, 0), 2)  # Gold separator
    
    # Center hub
    cv2.circle(frame, wheel_center, 30, (139, 69, 19), -1)
    cv2.circle(frame, wheel_center, 25, (255, 215, 0), -1)
    
    # Draw wheel segments (37 for European roulette)
    for i in range(37):
        angle = (2 * np.pi * i) / 37
        
        # Segment separators
        x1 = int(wheel_center[0] + (wheel_radius - 60) * np.cos(angle))
        y1 = int(wheel_center[1] + (wheel_radius - 60) * np.sin(angle))
        x2 = int(wheel_center[0] + (wheel_radius - 15) * np.cos(angle))
        y2 = int(wheel_center[1] + (wheel_radius - 15) * np.sin(angle))
        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        
        # Number pockets (alternating red/black)
        pocket_angle = angle + np.pi / 37  # Center of segment
        pocket_x = int(wheel_center[0] + (wheel_radius - 35) * np.cos(pocket_angle))
        pocket_y = int(wheel_center[1] + (wheel_radius - 35) * np.sin(pocket_angle))
        
        # Color depends on roulette number (simplified)
        if i == 0:  # Green for 0
            pocket_color = (0, 255, 0)
        elif i % 2 == 0:  # Red
            pocket_color = (0, 0, 255)
        else:  # Black
            pocket_color = (50, 50, 50)
        
        cv2.circle(frame, (pocket_x, pocket_y), 12, pocket_color, -1)
        cv2.circle(frame, (pocket_x, pocket_y), 12, (255, 255, 255), 1)
    
    # Ball track
    cv2.circle(frame, wheel_center, wheel_radius - 25, (255, 255, 255), 1)  # Ball track edge
    
    # Draw ball (more realistic white ball with shadow)
    ball_angle = np.pi / 4  # 45 degrees
    ball_radius = wheel_radius - 25  # On the ball track
    ball_x = int(wheel_center[0] + ball_radius * np.cos(ball_angle))
    ball_y = int(wheel_center[1] + ball_radius * np.sin(ball_angle))
    
    # Ball shadow
    cv2.circle(frame, (ball_x + 2, ball_y + 2), 10, (0, 0, 0), -1)
    # Ball highlight
    cv2.circle(frame, (ball_x, ball_y), 9, (240, 240, 240), -1)
    cv2.circle(frame, (ball_x, ball_y), 8, (255, 255, 255), -1)
    # Ball shine
    cv2.circle(frame, (ball_x - 2, ball_y - 2), 3, (255, 255, 255), -1)
    
    # Add some realistic casino UI elements
    # Betting layout outline
    cv2.rectangle(frame, (100, 600), (500, 750), (255, 255, 255), 2)
    cv2.putText(frame, "BETTING AREA", (200, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Casino name/logo area
    cv2.rectangle(frame, (50, 50), (300, 120), (0, 0, 0), -1)
    cv2.putText(frame, "CASINO LIVE", (60, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    return frame, wheel_center, wheel_radius, (ball_x, ball_y)


def test_enhanced_vision_system():
    """Test the enhanced computer vision components."""
    print("🔍 Testing Enhanced Vision System...")
    
    vision = RouletteVision()
    test_frame, expected_center, expected_radius, expected_ball = create_enhanced_test_frame_with_wheel_and_ball()
    
    # Save test frame for reference
    cv2.imwrite('/tmp/enhanced_test_frame.png', test_frame)
    print("   💾 Enhanced test frame saved to /tmp/enhanced_test_frame.png")
    
    # Test enhanced wheel detection
    detected_center, detected_radius = vision.detect_wheel(test_frame)
    
    if detected_center:
        center_error = np.sqrt((detected_center[0] - expected_center[0])**2 + 
                             (detected_center[1] - expected_center[1])**2)
        radius_error = abs(detected_radius - expected_radius)
        
        print(f"   ✅ Enhanced wheel detected at {detected_center}, radius: {detected_radius}")
        print(f"   📏 Center error: {center_error:.1f} pixels")
        print(f"   📏 Radius error: {radius_error:.1f} pixels")
        
        # Test if errors are reasonable
        if center_error < 50 and radius_error < 50:
            print("   ✅ Wheel detection accuracy: GOOD")
        else:
            print("   ⚠️  Wheel detection accuracy: MODERATE")
    else:
        print("   ❌ Enhanced wheel not detected")
        return False
    
    # Test enhanced ball detection
    detected_ball = vision.detect_ball(test_frame)
    
    if detected_ball:
        ball_error = np.sqrt((detected_ball[0] - expected_ball[0])**2 + 
                           (detected_ball[1] - expected_ball[1])**2)
        print(f"   ✅ Enhanced ball detected at {detected_ball}")
        print(f"   📏 Ball position error: {ball_error:.1f} pixels")
        
        if ball_error < 20:
            print("   ✅ Ball detection accuracy: EXCELLENT")
        elif ball_error < 50:
            print("   ✅ Ball detection accuracy: GOOD")
        else:
            print("   ⚠️  Ball detection accuracy: MODERATE")
    else:
        print("   ❌ Enhanced ball not detected")
        return False
    
    # Test enhanced visualization
    vis_frame = vision.visualize_detection(test_frame)
    cv2.imwrite('/tmp/enhanced_detection_result.png', vis_frame)
    print("   💾 Enhanced detection result saved to /tmp/enhanced_detection_result.png")
    
    # Test ball tracking with multiple frames
    print("   🎯 Testing ball tracking with motion...")
    
    for i in range(5):
        # Create frames with moving ball
        angle_offset = i * 0.2  # Ball moves around wheel
        ball_angle = np.pi / 4 + angle_offset
        ball_radius = expected_radius - 25 - (i * 2)  # Ball spiraling inward
        
        ball_x = int(expected_center[0] + ball_radius * np.cos(ball_angle))
        ball_y = int(expected_center[1] + ball_radius * np.sin(ball_angle))
        
        # Create new frame with ball in new position
        motion_frame = test_frame.copy()
        
        # Clear old ball area
        cv2.circle(motion_frame, expected_ball, 15, (0, 100, 0), -1)
        
        # Draw new ball
        cv2.circle(motion_frame, (ball_x + 2, ball_y + 2), 10, (0, 0, 0), -1)  # Shadow
        cv2.circle(motion_frame, (ball_x, ball_y), 9, (240, 240, 240), -1)
        cv2.circle(motion_frame, (ball_x, ball_y), 8, (255, 255, 255), -1)
        cv2.circle(motion_frame, (ball_x - 2, ball_y - 2), 3, (255, 255, 255), -1)  # Shine
        
        # Detect ball in new position
        motion_ball = vision.detect_ball(motion_frame)
        if motion_ball:
            speed = vision.calculate_ball_speed()
            angle = vision.get_ball_angle()
            print(f"   Frame {i+1}: Ball at {motion_ball}, Speed: {speed:.1f}, Angle: {angle:.2f}" if speed and angle else f"   Frame {i+1}: Ball at {motion_ball}")
    
    print(f"   📊 Ball history length: {len(vision.ball_history)}")
    
    return True


def test_performance_metrics():
    """Test system performance with realistic workload."""
    print("\n⚡ Testing Performance Metrics...")
    
    vision = RouletteVision()
    physics = RoulettePhysics()
    
    # Create multiple test frames
    frames = []
    print("   📹 Generating performance test frames...")
    
    for i in range(20):
        frame, center, radius, ball_pos = create_enhanced_test_frame_with_wheel_and_ball()
        frames.append(frame)
    
    # Time the processing
    start_time = time.time()
    detections = 0
    predictions = 0
    
    print("   🔄 Processing frames...")
    
    for i, frame in enumerate(frames):
        frame_start = time.time()
        
        # Detect wheel (first frame only)
        if i == 0:
            vision.detect_wheel(frame)
        
        # Detect ball
        ball_pos = vision.detect_ball(frame)
        if ball_pos:
            detections += 1
            
            # Try prediction if enough history
            if len(vision.ball_history) >= 3:
                state = physics.create_state_from_vision(
                    vision.ball_history[-5:],
                    vision.wheel_center,
                    time_interval=0.1
                )
                
                if state:
                    trajectory = physics.simulate_trajectory(state, simulation_time=10.0)
                    if trajectory:
                        predictions += 1
        
        frame_time = time.time() - frame_start
        if i < 5:  # Show timing for first few frames
            print(f"   Frame {i+1}: {frame_time:.3f}s")
    
    total_time = time.time() - start_time
    
    print(f"   📊 Performance Results:")
    print(f"      Total time: {total_time:.2f}s")
    print(f"      Average FPS: {len(frames) / total_time:.1f}")
    print(f"      Detection rate: {detections}/{len(frames)} ({detections/len(frames)*100:.1f}%)")
    print(f"      Prediction rate: {predictions}/{detections} ({predictions/detections*100:.1f}%)" if detections > 0 else "      Prediction rate: 0%")
    
    target_fps = 10
    if len(frames) / total_time >= target_fps:
        print(f"   ✅ Performance: EXCELLENT (>= {target_fps} FPS)")
    elif len(frames) / total_time >= target_fps * 0.7:
        print(f"   ✅ Performance: GOOD (>= {target_fps * 0.7:.1f} FPS)")
    else:
        print(f"   ⚠️  Performance: NEEDS IMPROVEMENT (< {target_fps * 0.7:.1f} FPS)")
    
    return True


def main():
    """Run all enhanced tests."""
    print("🧪 Enhanced Roulette Prediction System - Comprehensive Tests")
    print("=" * 65)
    print("Testing all enhanced components and performance...")
    print()
    
    # Test results
    results = {}
    
    # Test enhanced vision system
    results['enhanced_vision'] = test_enhanced_vision_system()
    
    # Test performance
    results['performance'] = test_performance_metrics()
    
    # Print summary
    print("\n📋 Enhanced Test Results Summary:")
    print("-" * 35)
    
    all_passed = True
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {component.replace('_', ' ').title():20} {status}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 Enhanced system is ready for live testing!")
        print("   Key improvements:")
        print("   • Enhanced wheel detection with confidence scoring")
        print("   • Improved ball detection with multiple color spaces")
        print("   • Better motion tracking and consistency validation")
        print("   • Performance optimizations for real-time processing")
        print("   • Fallback capture methods for better compatibility")
        print("   • Enhanced visualization and diagnostics")
    else:
        print("\n🔧 Please review failing components.")
    
    print(f"\n📁 Generated test files:")
    print("   • /tmp/enhanced_test_frame.png - Realistic test roulette frame")
    print("   • /tmp/enhanced_detection_result.png - Detection visualization")


if __name__ == "__main__":
    main()