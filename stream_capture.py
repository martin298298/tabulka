"""
Stream capture module for roulette prediction system.
Handles browser automation and live stream capture using Playwright.
"""

import asyncio
import time
from playwright.async_api import async_playwright
import cv2
import numpy as np
from PIL import Image
import io


class StreamCapture:
    def __init__(self, url: str, headless: bool = True, email: str = None, password: str = None):
        self.url = url
        self.headless = headless
        self.email = email
        self.password = password
        self.browser = None
        self.page = None
        self.is_capturing = False
        
    async def initialize(self):
        """Initialize browser and navigate to stream."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        
        # Set viewport for consistent capture
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Navigate to the roulette stream
        await self.page.goto(self.url)
        
        # Wait for the page to load
        await self.page.wait_for_load_state("networkidle")
        
        # If credentials are provided, attempt to login with retry
        if self.email and self.password:
            login_success = await self.login_with_retry(max_attempts=3)
            if login_success:
                print("✅ Login successful, proceeding to stream")
            else:
                print("⚠️  All login attempts failed, but continuing to stream")
        
        await asyncio.sleep(3)  # Additional wait for stream to start
        
        
    async def debug_page_state(self, step_name: str):
        """Take a screenshot and log page state for debugging."""
        try:
            # Take screenshot
            screenshot_path = f"/tmp/debug_{step_name}_{int(time.time())}.png"
            await self.page.screenshot(path=screenshot_path)
            print(f"📸 Debug screenshot saved: {screenshot_path}")
            
            # Log basic page info
            url = self.page.url
            title = await self.page.title()
            print(f"🌐 URL: {url}")
            print(f"📄 Title: {title}")
            
        except Exception as e:
            print(f"⚠️  Debug screenshot failed: {e}")
    
    async def check_login_errors(self):
        """Check for common login error messages in Czech and English."""
        error_messages = []
        
        # Czech error messages
        czech_errors = [
            'Nesprávné uživatelské jméno nebo heslo',  # Incorrect username or password
            'Neplatné přihlašovací údaje',             # Invalid login credentials
            'Uživatel nenalezen',                      # User not found
            'Heslo je nesprávné',                      # Password is incorrect
            'Účet je zablokován',                      # Account is blocked
            'Přístup odepřen',                         # Access denied
            'Chyba přihlášení'                         # Login error
        ]
        
        # English error messages
        english_errors = [
            'Invalid username or password',
            'Invalid credentials',
            'Login failed',
            'User not found',
            'Password incorrect',
            'Account blocked',
            'Access denied',
            'Authentication failed'
        ]
        
        all_error_texts = czech_errors + english_errors
        
        # Check for error elements
        error_selectors = [
            '.error',
            '.alert-danger',
            '.alert-error',
            '.login-error',
            '.error-message',
            '[class*="error"]',
            '[class*="invalid"]',
            '[class*="warning"]',
            '.notification-error',
            '#error-message'
        ]
        
        for selector in error_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible():
                        text = await element.text_content()
                        if text and text.strip():
                            error_messages.append(f"Found error: {text.strip()}")
            except:
                continue
        
        # Check for specific error text anywhere on page
        for error_text in all_error_texts:
            try:
                element = await self.page.wait_for_selector(f'text={error_text}', timeout=1000)
                if element:
                    error_messages.append(f"Found error message: {error_text}")
            except:
                continue
        
        return error_messages
        """Login with retry mechanism."""
        for attempt in range(max_attempts):
            print(f"🔄 Login attempt {attempt + 1}/{max_attempts}")
            
            success = await self.login()
            if success:
                return True
            
            if attempt < max_attempts - 1:
                print(f"⏳ Waiting before retry...")
                await asyncio.sleep(5)
        
        print(f"❌ All {max_attempts} login attempts failed")
        return False
        """Handle specific requirements for tokyo.cz site."""
        try:
            current_url = self.page.url.lower()
            if 'tokyo.cz' not in current_url:
                return False
                
            print("🎯 Detected tokyo.cz - applying site-specific handling")
            
            # Wait for any overlays or popups to appear
            await asyncio.sleep(3)
            
            # Look for common overlays/popups that might block login
            overlay_selectors = [
                '.modal',
                '.popup',
                '.overlay',
                '.dialog',
                '[class*="modal"]',
                '[class*="popup"]',
                '[id*="modal"]',
                '[id*="popup"]'
            ]
            
            for selector in overlay_selectors:
                try:
                    overlay = await self.page.wait_for_selector(selector, timeout=2000)
                    if overlay and await overlay.is_visible():
                        # Try to close the overlay
                        close_selectors = [
                            f'{selector} .close',
                            f'{selector} [class*="close"]',
                            f'{selector} button',
                            f'{selector} .btn-close'
                        ]
                        
                        for close_sel in close_selectors:
                            try:
                                close_btn = await self.page.wait_for_selector(close_sel, timeout=1000)
                                if close_btn:
                                    await close_btn.click()
                                    print(f"✓ Closed overlay: {selector}")
                                    await asyncio.sleep(1)
                                    break
                            except:
                                continue
                except:
                    continue
            
            # Look for cookie consent banner
            cookie_selectors = [
                'button:has-text("Souhlasím")',    # Czech for "I agree"
                'button:has-text("Přijmout")',     # Czech for "Accept"
                'button:has-text("Accept")',
                'button:has-text("OK")',
                '.cookie-accept',
                '.accept-cookies',
                '#cookie-accept'
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_btn = await self.page.wait_for_selector(selector, timeout=2000)
                    if cookie_btn and await cookie_btn.is_visible():
                        await cookie_btn.click()
                        print("✓ Accepted cookies")
                        await asyncio.sleep(1)
                        break
                except:
                    continue
            
            return True
        except Exception as e:
            print(f"⚠️  Tokyo.cz specific handling failed: {e}")
            return False
    
    async def login(self):
        """Attempt to login using provided credentials with enhanced error handling."""
        try:
            print("🔐 Attempting to login...")
            
            # Wait for page to fully load first
            await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            await asyncio.sleep(2)  # Additional wait for dynamic content
            
            # Take debug screenshot of initial state
            await self.debug_page_state("login_start")
            
            # Handle site-specific requirements
            await self.handle_tokyo_cz_specific()
            
            # Check if we're already logged in by looking for logout elements
            logout_indicators = [
                'button:has-text("Odhlásit")',  # Czech for "Logout"
                'a:has-text("Odhlásit")',
                'button:has-text("Logout")',
                'a:has-text("Logout")',
                '.logout',
                '#logout'
            ]
            
            for selector in logout_indicators:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=1000)
                    if element:
                        print("✓ Already logged in (found logout button)")
                        return True
                except:
                    continue
            
            # Look for login modal or popup trigger
            login_triggers = [
                'button:has-text("Přihlásit se")',  # Czech for "Sign in"
                'button:has-text("Přihlásit")',    # Czech for "Login"
                'a:has-text("Přihlásit se")',
                'a:has-text("Přihlásit")',
                'button:has-text("Login")',
                'a:has-text("Login")',
                '.login-trigger',
                '#login-trigger',
                '[data-testid="login"]',
                '.auth-button'
            ]
            
            # Try to click login trigger if present
            for selector in login_triggers:
                try:
                    trigger = await self.page.wait_for_selector(selector, timeout=2000)
                    if trigger:
                        print(f"✓ Found login trigger: {selector}")
                        await trigger.click()
                        await asyncio.sleep(2)  # Wait for modal to appear
                        break
                except:
                    continue
            
            # Enhanced selectors for Czech casino sites
            login_selectors = [
                # Standard email/username inputs
                'input[type="email"]',
                'input[name="email"]',
                'input[name="login"]',
                'input[name="username"]',
                'input[name="user"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="přihlašovací" i]',  # Czech for "login"
                'input[placeholder*="uživatel" i]',     # Czech for "user"
                '#email',
                '#login',
                '#username',
                '#user',
                '.email-input',
                '.username-input',
                '.login-input',
                '[data-testid="email"]',
                '[data-testid="username"]',
                '[data-testid="login"]'
            ]
            
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[name="passwd"]',
                'input[placeholder*="heslo" i]',  # Czech for "password"
                'input[placeholder*="password" i]',
                '#password',
                '#passwd',
                '.password-input',
                '[data-testid="password"]'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Přihlásit se")',  # Czech for "Sign in"
                'button:has-text("Přihlásit")',    # Czech for "Login"
                'button:has-text("Vstoupit")',     # Czech for "Enter"
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'button:has-text("Submit")',
                '.login-button',
                '.submit-button',
                '.auth-submit',
                '#login-button',
                '#submit',
                '[data-testid="submit"]',
                '[data-testid="login-submit"]'
            ]
            
            # Debug: Print current URL and page title
            current_url = self.page.url
            title = await self.page.title()
            print(f"📍 Current URL: {current_url}")
            print(f"📄 Page title: {title}")
            
            # Try to find email/username field with better error reporting
            email_field = None
            successful_selector = None
            for selector in login_selectors:
                try:
                    email_field = await self.page.wait_for_selector(selector, timeout=3000)
                    if email_field:
                        # Check if field is visible and enabled
                        is_visible = await email_field.is_visible()
                        is_enabled = await email_field.is_enabled()
                        if is_visible and is_enabled:
                            successful_selector = selector
                            print(f"✓ Found email field: {selector}")
                            break
                        else:
                            print(f"⚠️  Email field found but not usable: {selector} (visible: {is_visible}, enabled: {is_enabled})")
                            email_field = None
                except Exception as e:
                    print(f"🔍 Trying selector {selector}: {str(e)[:50]}...")
                    continue
            
            if not email_field:
                print("❌ No usable email/username field found")
                # Debug: List all input fields on the page
                all_inputs = await self.page.query_selector_all('input')
                print(f"🔍 Found {len(all_inputs)} input fields on page:")
                for i, inp in enumerate(all_inputs[:10]):  # Show first 10
                    try:
                        inp_type = await inp.get_attribute('type') or 'text'
                        inp_name = await inp.get_attribute('name') or ''
                        inp_id = await inp.get_attribute('id') or ''
                        inp_placeholder = await inp.get_attribute('placeholder') or ''
                        print(f"   Input {i}: type='{inp_type}' name='{inp_name}' id='{inp_id}' placeholder='{inp_placeholder}'")
                    except:
                        pass
                return False
            
            # Find password field
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = await self.page.wait_for_selector(selector, timeout=3000)
                    if password_field:
                        is_visible = await password_field.is_visible()
                        is_enabled = await password_field.is_enabled()
                        if is_visible and is_enabled:
                            print(f"✓ Found password field: {selector}")
                            break
                        else:
                            password_field = None
                except:
                    continue
            
            if not password_field:
                print("❌ No usable password field found")
                return False
            
            # Clear fields first and then fill them slowly
            await email_field.click()
            await email_field.clear()
            await asyncio.sleep(0.5)
            
            # Type email slowly to avoid being detected as bot
            for char in self.email:
                await email_field.type(char)
                await asyncio.sleep(0.05)  # Small delay between characters
            
            print(f"✓ Filled email: {self.email}")
            await asyncio.sleep(1)
            
            await password_field.click()
            await password_field.clear()
            await asyncio.sleep(0.5)
            
            # Type password slowly
            for char in self.password:
                await password_field.type(char)
                await asyncio.sleep(0.05)
            
            print("✓ Filled password")
            await asyncio.sleep(1)
            
            # Find and click submit button
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.wait_for_selector(selector, timeout=3000)
                    if submit_button:
                        is_visible = await submit_button.is_visible()
                        is_enabled = await submit_button.is_enabled()
                        if is_visible and is_enabled:
                            print(f"✓ Found submit button: {selector}")
                            break
                        else:
                            submit_button = None
                except:
                    continue
            
            if submit_button:
                # Click submit button
                await submit_button.click()
                print("✓ Clicked login button")
                
                # Wait for any of several possible outcomes
                try:
                    # Wait for either successful navigation or error message
                    await asyncio.sleep(3)  # Give time for initial response
                    
                    # Check for login errors using enhanced detection
                    error_messages = await self.check_login_errors()
                    if error_messages:
                        print("❌ Login errors detected:")
                        for error in error_messages:
                            print(f"   {error}")
                        return False
                    
                    # Wait for page to stabilize
                    await self.page.wait_for_load_state("networkidle", timeout=15000)
                    
                    # Check if we're now logged in
                    final_url = self.page.url
                    if final_url != current_url:
                        print(f"✓ Page changed after login: {final_url}")
                    
                    # Look for logout button as confirmation
                    for selector in logout_indicators:
                        try:
                            element = await self.page.wait_for_selector(selector, timeout=2000)
                            if element:
                                print("✅ Login successful (found logout button)")
                                return True
                        except:
                            continue
                    
                    print("✓ Login attempt completed (no error detected)")
                    return True
                    
                except Exception as wait_error:
                    print(f"⚠️  Login may have completed (waiting error: {wait_error})")
                    return True
                    
            else:
                print("⚠️  No submit button found, trying Enter key")
                await password_field.press("Enter")
                await asyncio.sleep(3)
                await self.page.wait_for_load_state("networkidle", timeout=10000)
                return True
                
        except Exception as e:
            print(f"❌ Login attempt failed: {e}")
            print("🔄 Continuing without login...")
            return False
        
    async def capture_frame(self) -> np.ndarray:
        """Capture a single frame from the stream."""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
            
        # Take screenshot of the entire page
        screenshot_bytes = await self.page.screenshot()
        
        # Convert to OpenCV format
        image = Image.open(io.BytesIO(screenshot_bytes))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        return frame
    
    async def find_roulette_area(self, frame: np.ndarray) -> tuple:
        """
        Detect the roulette table area in the frame.
        Returns (x, y, width, height) of the roulette area.
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Look for circular objects (likely the roulette wheel)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100,
                                  param1=50, param2=30, minRadius=50, maxRadius=300)
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            # Find the largest circle (likely the roulette wheel)
            largest_circle = max(circles, key=lambda c: c[2])  # c[2] is radius
            x, y, r = largest_circle
            
            # Return bounding box with some padding
            padding = int(r * 0.5)
            return (max(0, x - r - padding), 
                   max(0, y - r - padding),
                   min(frame.shape[1], 2 * r + 2 * padding),
                   min(frame.shape[0], 2 * r + 2 * padding))
        
        # Fallback: return center portion of frame
        h, w = frame.shape[:2]
        return (w//4, h//4, w//2, h//2)
    
    async def capture_roulette_area(self) -> np.ndarray:
        """Capture and crop to roulette area only."""
        frame = await self.capture_frame()
        x, y, w, h = await self.find_roulette_area(frame)
        return frame[y:y+h, x:x+w]
    
    async def start_continuous_capture(self, callback, interval: float = 0.1):
        """
        Start continuous capture with callback for each frame.
        
        Args:
            callback: Function to call with each captured frame
            interval: Time between captures in seconds
        """
        self.is_capturing = True
        
        while self.is_capturing:
            try:
                frame = await self.capture_roulette_area()
                await callback(frame)
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Capture error: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    def stop_capture(self):
        """Stop continuous capture."""
        self.is_capturing = False
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


# Convenience function for simple frame capture
async def capture_single_frame(url: str, email: str = None, password: str = None) -> np.ndarray:
    """Capture a single frame from the stream URL."""
    capture = StreamCapture(url, email=email, password=password)
    try:
        await capture.initialize()
        frame = await capture.capture_roulette_area()
        return frame
    finally:
        await capture.cleanup()