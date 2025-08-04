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
        
        # If credentials are provided, attempt to login
        if self.email and self.password:
            await self.login()
        
        # Try to click video play buttons to start the stream
        await self.click_video_play_buttons()
        
        await asyncio.sleep(3)  # Additional wait for stream to start
        
    async def login(self):
        """Attempt to login using provided credentials."""
        try:
            print("🔐 Attempting to login...")
            
            # Look for common login elements
            login_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[name="login"]',
                'input[name="username"]',
                '#email',
                '#login',
                '#username'
            ]
            
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                '#password'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Přihlásit")',  # Czech for "Login"
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                '.login-button',
                '#login-button'
            ]
            
            # Find email/username field
            email_field = None
            for selector in login_selectors:
                try:
                    email_field = await self.page.wait_for_selector(selector, timeout=2000)
                    if email_field:
                        break
                except:
                    continue
            
            if not email_field:
                print("⚠️  No email/username field found, checking if already logged in...")
                return
            
            # Find password field
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = await self.page.wait_for_selector(selector, timeout=2000)
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                print("⚠️  No password field found")
                return
            
            # Fill in credentials
            await email_field.fill(self.email)
            print(f"✓ Filled email: {self.email}")
            
            await password_field.fill(self.password)
            print("✓ Filled password")
            
            # Find and click submit button
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.wait_for_selector(selector, timeout=2000)
                    if submit_button:
                        break
                except:
                    continue
            
            if submit_button:
                await submit_button.click()
                print("✓ Clicked login button")
                
                # Wait for navigation or login to complete
                try:
                    await self.page.wait_for_load_state("networkidle", timeout=10000)
                    print("✓ Login completed successfully")
                except:
                    print("⚠️  Login may have completed (timeout waiting for networkidle)")
                    
            else:
                print("⚠️  No submit button found, trying Enter key")
                await password_field.press("Enter")
                await self.page.wait_for_load_state("networkidle", timeout=5000)
                
        except Exception as e:
            print(f"⚠️  Login attempt failed: {e}")
            print("Continuing without login...")

    async def click_video_play_buttons(self):
        """Detect and click video play buttons to start the stream."""
        try:
            print("🎬 Looking for video play buttons...")
            
            # Common selectors for video play buttons
            play_button_selectors = [
                # Standard video controls
                'button[aria-label*="play"]',
                'button[title*="play"]',
                'button[aria-label*="Play"]',
                'button[title*="Play"]',
                '.play-button',
                '.video-play-button',
                '.player-play-button',
                
                # Mute/unmute buttons (often need to be clicked for autoplay)
                'button[aria-label*="mute"]',
                'button[aria-label*="unmute"]',
                'button[title*="mute"]',
                'button[title*="unmute"]',
                'button[aria-label*="sound"]',
                'button[title*="sound"]',
                '.mute-button',
                '.sound-button',
                '.volume-button',
                
                # Czech language variants
                'button:has-text("Přehrát")',  # Play
                'button:has-text("přehrát")',  # play (lowercase)
                'button:has-text("Přehrát bez zvuku")',  # Play without sound
                'button:has-text("přehrát bez zvuku")',  # play without sound (lowercase)
                'button:has-text("Spustit")',  # Start
                'button:has-text("spustit")',  # start (lowercase)
                'button[aria-label*="přehrát"]',
                'button[title*="přehrát"]',
                'button[aria-label*="zvuk"]',  # sound
                'button[title*="zvuk"]',
                
                # Generic video/media selectors
                '[role="button"][aria-label*="play"]',
                '[role="button"][title*="play"]',
                'div[class*="play"]',
                'span[class*="play"]',
                '.video-overlay button',
                '.media-control button',
                '.player-overlay button',
                
                # HTML5 video controls
                'video + div button',  # Button next to video element
                'video ~ div button',   # Button sibling to video element
                '.video-container button',
                '.video-wrapper button',
                
                # Casino/game specific selectors
                '.game-controls button',
                '.casino-controls button',
                '.live-controls button'
            ]
            
            buttons_clicked = 0
            
            # Try each selector
            for selector in play_button_selectors:
                try:
                    # Look for the element with a short timeout
                    elements = await self.page.query_selector_all(selector)
                    
                    for element in elements:
                        try:
                            # Check if element is visible and clickable
                            is_visible = await element.is_visible()
                            if not is_visible:
                                continue
                            
                            # Get element properties to determine if it's a play/mute button
                            aria_label = await element.get_attribute('aria-label') or ''
                            title = await element.get_attribute('title') or ''
                            text_content = await element.text_content() or ''
                            class_name = await element.get_attribute('class') or ''
                            
                            # Check if this looks like a play or mute button
                            element_text = f"{aria_label} {title} {text_content} {class_name}".lower()
                            
                            play_keywords = ['play', 'přehrát', 'spustit', 'start']
                            sound_keywords = ['mute', 'unmute', 'sound', 'zvuk', 'audio', 'volume']
                            
                            is_play_button = any(keyword in element_text for keyword in play_keywords)
                            is_sound_button = any(keyword in element_text for keyword in sound_keywords)
                            
                            if is_play_button or is_sound_button:
                                print(f"   Found potential button: {selector}")
                                print(f"   Button properties: aria-label='{aria_label}', title='{title}', text='{text_content}'")
                                
                                # Click the button
                                await element.click()
                                buttons_clicked += 1
                                print(f"   ✓ Clicked button ({buttons_clicked})")
                                
                                # Wait a moment for the action to take effect
                                await asyncio.sleep(1)
                                
                        except Exception as e:
                            print(f"   ⚠️  Could not click element: {e}")
                            continue
                        
                except Exception as e:
                    # Selector not found or other error, continue to next
                    continue
            
            if buttons_clicked > 0:
                print(f"✓ Clicked {buttons_clicked} video control button(s)")
                # Wait a bit longer for video to start
                await asyncio.sleep(3)
            else:
                print("⚠️  No video play buttons found - stream may already be playing")
                
        except Exception as e:
            print(f"⚠️  Error while looking for play buttons: {e}")
            print("Continuing anyway...")
        
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