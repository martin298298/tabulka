#!/usr/bin/env python3
"""
Demo script showing the enhanced login functionality.
Since Playwright may not be fully installed, this shows the logic improvements.
"""

import asyncio
import time

class MockPage:
    """Mock page class for demonstration."""
    def __init__(self, url):
        self.url = url
        self._title = "Tokyo Casino - Live Roulette"
        
    async def wait_for_load_state(self, state, timeout=5000):
        await asyncio.sleep(0.1)
        
    async def wait_for_selector(self, selector, timeout=2000):
        # Simulate finding login elements based on improved selectors
        if 'email' in selector or 'login' in selector:
            return MockElement("email")
        elif 'password' in selector:
            return MockElement("password")
        elif 'submit' in selector or 'Přihlásit' in selector:
            return MockElement("submit")
        else:
            raise Exception(f"Element not found: {selector}")
    
    async def title(self):
        return self._title
    
    async def screenshot(self, path=None):
        print(f"📸 Mock screenshot saved to: {path}")

class MockElement:
    """Mock element class."""
    def __init__(self, element_type):
        self.element_type = element_type
        
    async def is_visible(self):
        return True
    
    async def is_enabled(self):
        return True
    
    async def click(self):
        print(f"🖱️  Clicked {self.element_type} element")
    
    async def clear(self):
        print(f"🧹 Cleared {self.element_type} field")
        
    async def type(self, text):
        if self.element_type == "password":
            print(f"⌨️  Typed password: {'*' * len(text)}")
        else:
            print(f"⌨️  Typed: {text}")
    
    async def press(self, key):
        print(f"⌨️  Pressed key: {key}")

class MockStreamCapture:
    """Mock stream capture to demonstrate enhanced login logic."""
    
    def __init__(self, url, email, password):
        self.url = url
        self.email = email
        self.password = password
        self.page = MockPage(url)
    
    async def debug_page_state(self, step_name: str):
        """Mock debug page state."""
        screenshot_path = f"/tmp/mock_debug_{step_name}_{int(time.time())}.png"
        await self.page.screenshot(path=screenshot_path)
        
        url = self.page.url
        title = await self.page.title()
        print(f"🌐 URL: {url}")
        print(f"📄 Title: {title}")
    
    async def handle_tokyo_cz_specific(self):
        """Mock tokyo.cz specific handling."""
        print("🎯 Detected tokyo.cz - applying site-specific handling")
        await asyncio.sleep(0.5)  # Simulate processing time
        print("✓ Handled overlays and cookie consent")
        return True
    
    async def login(self):
        """Enhanced login logic demonstration."""
        try:
            print("🔐 Attempting to login...")
            
            # Wait for page to fully load
            await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            await asyncio.sleep(0.2)  # Simulate wait
            
            # Take debug screenshot
            await self.debug_page_state("login_start")
            
            # Handle site-specific requirements
            await self.handle_tokyo_cz_specific()
            
            # Check if already logged in
            print("🔍 Checking if already logged in...")
            
            # Enhanced login selectors (demonstration)
            login_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="přihlašovací" i]',  # Czech
            ]
            
            password_selectors = [
                'input[type="password"]',
                'input[placeholder*="heslo" i]',  # Czech for password
            ]
            
            submit_selectors = [
                'button:has-text("Přihlásit se")',  # Czech for "Sign in"
                'button:has-text("Přihlásit")',    # Czech for "Login"
                'button[type="submit"]',
            ]
            
            # Find email field
            print("🔍 Looking for email field...")
            email_field = await self.page.wait_for_selector(login_selectors[0])
            print(f"✓ Found email field")
            
            # Find password field
            print("🔍 Looking for password field...")
            password_field = await self.page.wait_for_selector(password_selectors[0])
            print(f"✓ Found password field")
            
            # Clear and fill email slowly (anti-bot measure)
            await email_field.clear()
            await asyncio.sleep(0.1)
            
            for char in self.email:
                await email_field.type(char)
                await asyncio.sleep(0.02)  # Simulate human typing
            
            print(f"✓ Filled email: {self.email}")
            
            # Clear and fill password slowly
            await password_field.clear()
            await asyncio.sleep(0.1)
            
            for char in self.password:
                await password_field.type(char)
                await asyncio.sleep(0.02)
            
            print("✓ Filled password")
            
            # Find and click submit button
            print("🔍 Looking for submit button...")
            submit_button = await self.page.wait_for_selector(submit_selectors[0])
            await submit_button.click()
            print("✓ Clicked login button")
            
            # Wait and check for success
            await asyncio.sleep(1)
            print("✅ Login process completed successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    async def login_with_retry(self, max_attempts=3):
        """Login with retry mechanism."""
        for attempt in range(max_attempts):
            print(f"🔄 Login attempt {attempt + 1}/{max_attempts}")
            
            success = await self.login()
            if success:
                return True
            
            if attempt < max_attempts - 1:
                print(f"⏳ Waiting before retry...")
                await asyncio.sleep(1)  # Shortened for demo
        
        print(f"❌ All {max_attempts} login attempts failed")
        return False

async def demo_enhanced_login():
    """Demonstrate the enhanced login functionality."""
    print("🎰 Enhanced Login System Demo")
    print("=" * 40)
    print("This demo shows the improved login logic without requiring")
    print("a full Playwright installation.")
    print()
    
    # Test data
    url = "https://www.tokyo.cz/game/tomhornlive_56"
    email = "martin298@post.cz"
    password = "Certik298"
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {'*' * len(password)}")
    print(f"🌐 URL: {url}")
    print()
    
    # Create mock capture instance
    capture = MockStreamCapture(url, email, password)
    
    # Test login with retry
    print("🚀 Starting login process...")
    success = await capture.login_with_retry(max_attempts=2)
    
    if success:
        print("\n✅ Demo completed successfully!")
        print("📋 Enhanced features demonstrated:")
        print("   ✓ Site-specific handling for tokyo.cz")
        print("   ✓ Enhanced Czech language selectors")
        print("   ✓ Anti-bot typing simulation")
        print("   ✓ Retry mechanism")
        print("   ✓ Debug screenshots")
        print("   ✓ Better error handling")
    else:
        print("\n⚠️  Demo showed retry mechanism working")
    
    print("\n🔧 The actual system will use these improvements")
    print("   when connecting to the real casino site.")

def main():
    """Run the demo."""
    asyncio.run(demo_enhanced_login())

if __name__ == "__main__":
    main()