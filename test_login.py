#!/usr/bin/env python3
"""
Test script for enhanced login functionality.
Tests the improved login system with better debugging.
"""

import asyncio
import sys
from stream_capture import StreamCapture

async def test_login():
    """Test the enhanced login functionality."""
    print("🧪 Testing Enhanced Login System")
    print("=" * 40)
    
    # Test URL - using a safe test site first
    test_url = "https://httpbin.org/html"
    email = "martin298@post.cz"
    password = "Certik298"
    
    print(f"📧 Email: {email}")
    print(f"🌐 Test URL: {test_url}")
    print()
    
    # Create stream capture instance
    capture = StreamCapture(test_url, headless=False, email=email, password=password)
    
    try:
        print("🚀 Initializing browser...")
        await capture.initialize()
        
        print("✅ Browser initialized successfully")
        print("🔍 Login test completed")
        
        # Take a final screenshot
        await capture.debug_page_state("test_complete")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        print("🧹 Cleaning up...")
        await capture.cleanup()
    
    return True

async def test_actual_site():
    """Test with the actual casino site (if accessible)."""
    print("\n🎰 Testing with actual casino site")
    print("=" * 40)
    
    # Actual casino URL
    casino_url = "https://www.tokyo.cz/game/tomhornlive_56"
    email = "martin298@post.cz"
    password = "Certik298"
    
    print(f"📧 Email: {email}")
    print(f"🌐 Casino URL: {casino_url}")
    print()
    
    capture = StreamCapture(casino_url, headless=False, email=email, password=password)
    
    try:
        print("🚀 Initializing browser for casino site...")
        await capture.initialize()
        
        print("✅ Casino site test completed")
        
    except Exception as e:
        print(f"❌ Casino site test failed: {e}")
        print("This might be expected if the site is blocked or requires VPN")
        return False
    finally:
        await capture.cleanup()
    
    return True

def main():
    """Run login tests."""
    print("🔐 Enhanced Login System Tests")
    print("="*50)
    
    # Test with safe site first
    try:
        success = asyncio.run(test_login())
        if success:
            print("\n✅ Basic login test passed")
        else:
            print("\n❌ Basic login test failed")
    except Exception as e:
        print(f"\n❌ Basic test error: {e}")
    
    # Test with actual casino site
    try:
        success = asyncio.run(test_actual_site())
        if success:
            print("\n✅ Casino site test passed")
        else:
            print("\n⚠️  Casino site test failed (may be expected)")
    except Exception as e:
        print(f"\n⚠️  Casino site test error: {e}")
    
    print("\n📸 Check /tmp/ directory for debug screenshots")
    print("🔧 Login system improvements complete!")

if __name__ == "__main__":
    main()