"""
Headless version of the roulette prediction system.
Runs without GUI display, useful for server environments.
"""

import asyncio
import cv2
import numpy as np
import time
import json
from typing import Optional, List, Dict, Any

from vision import RouletteVision
from physics import RoulettePhysics, RouletteState


class HeadlessRoulettePrediction:
    def __init__(self):
        self.vision = RouletteVision()
        self.physics = RoulettePhysics()
        self.predictions = []
        self.frame_count = 0
        self.start_time = time.time()
        
    def create_test_frame(self, ball_angle: float, ball_radius_ratio: float = 0.8) -> np.ndarray:
        """Create a test roulette frame with ball at specified position."""
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Draw wheel
        wheel_center = (400, 300)
        wheel_radius = 150
        cv2.circle(frame, wheel_center, wheel_radius, (0, 100, 0), 3)
        cv2.circle(frame, wheel_center, wheel_radius - 20, (50, 50, 50), -1)
        
        # Draw segments
        for i in range(37):
            angle = (2 * np.pi * i) / 37
            x1 = int(wheel_center[0] + (wheel_radius - 40) * np.cos(angle))
            y1 = int(wheel_center[1] + (wheel_radius - 40) * np.sin(angle))
            x2 = int(wheel_center[0] + (wheel_radius - 10) * np.cos(angle))
            y2 = int(wheel_center[1] + (wheel_radius - 10) * np.sin(angle))
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
        
        # Draw ball
        ball_radius = (wheel_radius - 30) * ball_radius_ratio
        ball_x = int(wheel_center[0] + ball_radius * np.cos(ball_angle))
        ball_y = int(wheel_center[1] + ball_radius * np.sin(ball_angle))
        cv2.circle(frame, (ball_x, ball_y), 8, (255, 255, 255), -1)
        
        return frame
    
    def process_frame(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """Process a single frame and return prediction data."""
        self.frame_count += 1
        
        # Detect wheel on first frame
        if self.frame_count == 1:
            wheel_center, wheel_radius = self.vision.detect_wheel(frame)
            if not wheel_center:
                return None
        
        # Detect ball
        ball_pos = self.vision.detect_ball(frame)
        if not ball_pos:
            return None
        
        # Make prediction if we have enough history
        if len(self.vision.ball_history) >= 5:
            state = self.physics.create_state_from_vision(
                self.vision.ball_history[-5:],
                self.vision.wheel_center,
                time_interval=0.1,
                wheel_angular_velocity=3.0
            )
            
            if state:
                trajectory = self.physics.simulate_trajectory(state, simulation_time=10.0)
                
                if trajectory:
                    final_angle, predicted_number = self.physics.predict_landing_position(trajectory)
                    confidence = self.physics.get_prediction_confidence(trajectory)
                    
                    result = {
                        'frame': self.frame_count,
                        'time': time.time() - self.start_time,
                        'ball_position': ball_pos,
                        'ball_speed': self.vision.calculate_ball_speed(),
                        'ball_angle': self.vision.get_ball_angle(),
                        'predicted_number': predicted_number,
                        'confidence': confidence,
                        'wheel_center': self.vision.wheel_center,
                        'wheel_radius': self.vision.wheel_radius
                    }
                    
                    self.predictions.append(result)
                    return result
        
        return None
    
    def run_simulation(self, num_frames: int = 50) -> List[Dict[str, Any]]:
        """Run a complete simulation with generated frames."""
        print(f"🎰 Running headless simulation with {num_frames} frames...")
        
        results = []
        
        for i in range(num_frames):
            # Create frame with moving ball
            time_factor = i / num_frames
            ball_angle = 2 * np.pi * 3 * time_factor  # 3 rotations
            ball_radius_ratio = 0.9 - (time_factor * 0.4)  # Moving inward
            
            frame = self.create_test_frame(ball_angle, ball_radius_ratio)
            result = self.process_frame(frame)
            
            if result:
                results.append(result)
                if result['confidence'] > 0.5:
                    print(f"   Frame {i:2d}: Predicted {result['predicted_number']:2d} "
                          f"(confidence: {result['confidence']:.2f})")
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze prediction results and return statistics."""
        if not results:
            return {'error': 'No results to analyze'}
        
        # Filter high confidence predictions
        high_confidence = [r for r in results if r['confidence'] > 0.5]
        
        # Count predicted numbers
        number_counts = {}
        for result in high_confidence:
            num = result['predicted_number']
            number_counts[num] = number_counts.get(num, 0) + 1
        
        # Calculate statistics
        stats = {
            'total_frames': len(results),
            'high_confidence_predictions': len(high_confidence),
            'average_confidence': sum(r['confidence'] for r in high_confidence) / len(high_confidence) if high_confidence else 0,
            'predicted_numbers': number_counts,
            'most_predicted_number': max(number_counts, key=number_counts.get) if number_counts else None,
            'processing_time': results[-1]['time'] if results else 0,
            'fps': len(results) / results[-1]['time'] if results and results[-1]['time'] > 0 else 0
        }
        
        return stats
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = '/tmp/roulette_results.json'):
        """Save results to JSON file."""
        stats = self.analyze_results(results)
        
        output = {
            'metadata': {
                'system': 'Roulette Prediction System',
                'timestamp': time.time(),
                'version': '1.0.0'
            },
            'statistics': stats,
            'detailed_results': results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"📄 Results saved to {filename}")


def main():
    """Main function for headless testing."""
    print("🎰 Headless Roulette Prediction System")
    print("=" * 45)
    print("Running simulation without GUI display...")
    print()
    
    # Create prediction system
    predictor = HeadlessRoulettePrediction()
    
    # Run simulation
    try:
        results = predictor.run_simulation(num_frames=50)
        
        # Analyze and display results
        stats = predictor.analyze_results(results)
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total frames processed: {stats['total_frames']}")
        print(f"   High confidence predictions: {stats['high_confidence_predictions']}")
        print(f"   Average confidence: {stats['average_confidence']:.2f}")
        print(f"   Processing FPS: {stats['fps']:.1f}")
        
        if stats['predicted_numbers']:
            print(f"   Predicted numbers:")
            for num, count in sorted(stats['predicted_numbers'].items()):
                print(f"     {num:2d}: {count} times")
            print(f"   Most predicted: {stats['most_predicted_number']}")
        
        # Save results
        predictor.save_results(results)
        
        print("\n✅ Headless simulation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()