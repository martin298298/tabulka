#!/usr/bin/env python3
"""
Quick start script for the enhanced roulette prediction system.
Specifically configured for tokyo.cz casino with optimal settings.
"""

import asyncio
import sys
import argparse

# Enhanced imports with fallbacks
try:
    from main import RoulettePredictionSystem
    print("✅ Enhanced system loaded successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    print("  playwright install chromium")
    sys.exit(1)


async def quick_start_tokyo():
    """Quick start for Tokyo.cz casino with optimized settings."""
    
    print("🎰 Enhanced Roulette Prediction System")
    print("🎯 Optimized for tokyo.cz casino")
    print("=" * 50)
    
    # Configuration for tokyo.cz
    config = {
        'url': "https://www.tokyo.cz/game/tomhornlive_56",
        'email': "martin298@post.cz",  # From problem statement
        'password': "Certik298",       # From problem statement
        'headless': False  # Show browser for debugging
    }
    
    print(f"🌐 Target URL: {config['url']}")
    print(f"🔐 Using credentials: {config['email']}")
    print(f"🖥️  Browser mode: {'Headless' if config['headless'] else 'Visible'}")
    print()
    
    # Ask user for confirmation
    response = input("Continue with these settings? (Y/n): ").strip().lower()
    if response in ['n', 'no']:
        print("❌ Cancelled by user")
        return
    
    try:
        # Create enhanced system
        print("🚀 Initializing enhanced prediction system...")
        system = RoulettePredictionSystem(**config)
        
        print("📡 Connecting to casino stream...")
        await system.initialize()
        
        print("🎯 Starting real-time prediction...")
        print("💡 The system will:")
        print("   • Automatically dismiss cookie banners and popups")
        print("   • Login with provided credentials")
        print("   • Optimize video view (fullscreen, play controls)")
        print("   • Detect roulette wheel and ball in real-time")
        print("   • Make predictions with confidence scores")
        print("   • Display performance metrics")
        print()
        print("🎮 Controls:")
        print("   • Press 'q' in the video window to quit")
        print("   • Watch console for predictions and diagnostics")
        print()
        
        await system.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check internet connection")
        print("   2. Verify casino website is accessible")
        print("   3. Ensure browser dependencies are installed:")
        print("      playwright install chromium")
        print("   4. Try running: python enhanced_test.py")


async def test_components():
    """Test system components before connecting to live casino."""
    
    print("🧪 Testing Enhanced System Components")
    print("=" * 40)
    
    try:
        # Import and run enhanced test
        import enhanced_test
        enhanced_test.main()
        
    except ImportError:
        print("❌ Enhanced test module not available")
        print("Running basic component test...")
        
        try:
            import test_system
            test_system.main()
        except ImportError:
            print("❌ No test modules available")


def main():
    """Main entry point with command line options."""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Roulette Prediction System for tokyo.cz",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_start.py                    # Start with default settings
  python quick_start.py --test             # Test components first
  python quick_start.py --headless         # Run without browser window
  python quick_start.py --help             # Show this help
        """
    )
    
    parser.add_argument('--test', action='store_true',
                       help='Test system components before running live')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode (no window)')
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_components())
    else:
        if args.headless:
            print("🖥️  Running in headless mode...")
        asyncio.run(quick_start_tokyo())


if __name__ == "__main__":
    main()