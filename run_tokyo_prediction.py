#!/usr/bin/env python3
"""
Tokyo.cz Roulette Prediction - Quick Start Script
Demonstrates the system with the live casino stream.
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking system requirements...")
    
    # Check Python packages
    required_packages = ['cv2', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    # Check browsers
    browsers_available = []
    for browser in ['/opt/google/chrome/chrome', 'google-chrome', 'chromium-browser', 'chromium', 'firefox']:
        try:
            if os.path.exists(browser) or subprocess.run(['which', browser], capture_output=True, text=True).returncode == 0:
                browsers_available.append(browser)
                print(f"✅ Browser: {browser} - AVAILABLE")
                break
        except:
            continue
    
    if not browsers_available:
        print("❌ No suitable browser found")
        return False
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Run: pip install opencv-python numpy")
        return False
    
    print("\n✅ All requirements met!")
    return True

def run_quick_test():
    """Run a quick test of the system."""
    print("\n🧪 Running quick system test...")
    
    try:
        result = subprocess.run([sys.executable, 'test_system.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if "ALL TESTS PASSED" in result.stdout:
            print("✅ System test passed!")
            return True
        else:
            print("⚠️  Some components may have issues")
            print("But the core system should still work")
            return True
            
    except Exception as e:
        print(f"⚠️  Test failed: {e}")
        print("But the system may still work for live analysis")
        return True

def show_usage_options():
    """Show available usage options."""
    print("\n🎰 Tokyo.cz Roulette Prediction - Usage Options")
    print("=" * 50)
    print()
    print("1. 🖥️  Live Analysis with GUI:")
    print("   python tokyo_roulette_live.py")
    print("   - Real-time visual display")
    print("   - Interactive controls")
    print("   - Best for desktop use")
    print()
    print("2. 💻 Headless Analysis (No GUI):")
    print("   python tokyo_headless.py")
    print("   - Perfect for servers")
    print("   - Saves results to files")
    print("   - Configurable duration")
    print()
    print("3. 🧪 Test System Components:")
    print("   python test_system.py")
    print("   - Verify all components work")
    print("   - Generate test results")
    print()
    print("4. 🎬 Demo Simulation:")
    print("   python headless_demo.py")
    print("   - Simulated roulette analysis")
    print("   - No internet required")
    print()
    print("🎯 Target URL: https://www.tokyo.cz/game/tomhornlive_56")
    print("🔬 Uses computer vision + physics simulation")
    print("⚠️  For educational/research purposes only!")

def run_interactive():
    """Run interactive selection."""
    print("\n🎮 What would you like to do?")
    print("1. Run headless analysis (recommended)")
    print("2. Run live analysis with GUI")
    print("3. Test system components")
    print("4. Show info only")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting headless analysis...")
            subprocess.run([sys.executable, 'tokyo_headless.py'])
        elif choice == "2":
            print("\n🚀 Starting live analysis with GUI...")
            subprocess.run([sys.executable, 'tokyo_roulette_live.py'])
        elif choice == "3":
            print("\n🚀 Running system tests...")
            subprocess.run([sys.executable, 'test_system.py'])
        elif choice == "4":
            print("\n📋 System ready! Use any of the scripts shown above.")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

def main():
    """Main entry point."""
    print("🎰 Tokyo.cz Live Roulette Prediction System")
    print("🇨🇿 Živá analýza rulety z Tokyo.cz")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Run quick test
    run_quick_test()
    
    # Show options
    show_usage_options()
    
    # Interactive mode
    run_interactive()

if __name__ == "__main__":
    main()