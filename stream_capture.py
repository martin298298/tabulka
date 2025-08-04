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
        
        # Dismiss overlays that might block the roulette view
        await self.dismiss_overlays()
        
        # Try to click video play buttons to start the stream
        await self.click_video_play_buttons()
        
        # Try to enter fullscreen or maximize video area
        await self.optimize_video_view()
        
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

    async def dismiss_overlays(self):
        """Detect and dismiss cookie banners, popups, and other overlays that might block the roulette view."""
        try:
            print("🚫 Looking for overlays to dismiss...")
            
            # Wait a moment for overlays to load
            await asyncio.sleep(2)
            
            # Common selectors for overlay dismissal
            overlay_dismiss_selectors = [
                # Cookie banners
                'button:has-text("Accept")',
                'button:has-text("Přijmout")',  # Czech for Accept
                'button:has-text("Souhlasím")',  # Czech for I agree
                'button:has-text("OK")',
                'button:has-text("Zavřít")',  # Czech for Close
                'button:has-text("Close")',
                'button:has-text("Dismiss")',
                'button[aria-label*="dismiss"]',
                'button[aria-label*="close"]',
                'button[aria-label*="accept"]',
                '.cookie-accept',
                '.cookie-dismiss',
                '.overlay-close',
                '.modal-close',
                '.popup-close',
                '[data-testid*="accept"]',
                '[data-testid*="dismiss"]',
                '[data-testid*="close"]',
                
                # Ad overlays
                '.ad-close',
                '.advertisement-close',
                'button[title*="close ad"]',
                'button[aria-label*="close ad"]',
                
                # General modal/popup closers
                'button.close',
                'button[class*="close"]',
                '.btn-close',
                '[role="button"]:has-text("×")',
                '[role="button"]:has-text("✕")',
                'button:has-text("×")',
                'button:has-text("✕")',
                
                # Casino-specific overlays
                '.promo-close',
                '.bonus-close',
                '.welcome-close',
                'button:has-text("Skip")',
                'button:has-text("Přeskočit")',  # Czech for Skip
                'button:has-text("Later")',
                'button:has-text("Později")',  # Czech for Later
            ]
            
            overlays_dismissed = 0
            
            for selector in overlay_dismiss_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    
                    for element in elements:
                        try:
                            # Check if element is visible and clickable
                            is_visible = await element.is_visible()
                            if not is_visible:
                                continue
                            
                            # Get element properties
                            text_content = await element.text_content() or ''
                            aria_label = await element.get_attribute('aria-label') or ''
                            title = await element.get_attribute('title') or ''
                            class_name = await element.get_attribute('class') or ''
                            
                            print(f"   Found overlay element: {selector}")
                            print(f"   Element properties: text='{text_content}', aria-label='{aria_label}', title='{title}'")
                            
                            # Click the element
                            await element.click()
                            overlays_dismissed += 1
                            print(f"   ✓ Dismissed overlay ({overlays_dismissed})")
                            
                            # Wait for dismissal to take effect
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            print(f"   ⚠️  Could not click overlay element: {e}")
                            continue
                        
                except Exception as e:
                    # Selector not found or other error, continue to next
                    continue
            
            if overlays_dismissed > 0:
                print(f"✓ Dismissed {overlays_dismissed} overlay(s)")
                # Wait for layout to stabilize
                await asyncio.sleep(2)
            else:
                print("   No overlays found to dismiss")
                
        except Exception as e:
            print(f"⚠️  Error while dismissing overlays: {e}")

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

    async def optimize_video_view(self):
        """Try to optimize the video view by entering fullscreen or maximizing the roulette area."""
        try:
            print("🔍 Optimizing video view...")
            
            # Look for fullscreen buttons
            fullscreen_selectors = [
                'button[aria-label*="fullscreen"]',
                'button[title*="fullscreen"]',
                'button[aria-label*="Fullscreen"]',
                'button[title*="Fullscreen"]',
                'button[aria-label*="celá obrazovka"]',  # Czech
                'button[title*="celá obrazovka"]',
                '.fullscreen-button',
                '.fs-button',
                '[data-testid*="fullscreen"]',
                'button:has-text("⛶")',  # Fullscreen icon
                'button:has-text("⛶")',
            ]
            
            # Look for maximize/expand buttons
            expand_selectors = [
                'button[aria-label*="expand"]',
                'button[title*="expand"]',
                'button[aria-label*="maximize"]',
                'button[title*="maximize"]',
                '.expand-button',
                '.maximize-button',
                '[data-testid*="expand"]',
                '[data-testid*="maximize"]',
            ]
            
            # Try fullscreen first
            for selector in fullscreen_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000)
                    if element and await element.is_visible():
                        print(f"   Found fullscreen button: {selector}")
                        await element.click()
                        print("   ✓ Entered fullscreen mode")
                        await asyncio.sleep(2)
                        return
                except:
                    continue
            
            # Try expand/maximize if fullscreen not found
            for selector in expand_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=2000)
                    if element and await element.is_visible():
                        print(f"   Found expand button: {selector}")
                        await element.click()
                        print("   ✓ Maximized video view")
                        await asyncio.sleep(2)
                        return
                except:
                    continue
            
            print("   No fullscreen/expand options found")
            
        except Exception as e:
            print(f"⚠️  Error while optimizing video view: {e}")
        
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
        Detect the roulette table area in the frame with enhanced detection.
        Returns (x, y, width, height) of the roulette area.
        """
        # Convert to different color spaces for better detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Look for circular objects (roulette wheel) with multiple parameter sets
        circle_configs = [
            # More sensitive detection
            {'dp': 1, 'minDist': 80, 'param1': 40, 'param2': 25, 'minRadius': 40, 'maxRadius': 400},
            # Standard detection
            {'dp': 1, 'minDist': 100, 'param1': 50, 'param2': 30, 'minRadius': 50, 'maxRadius': 300},
            # Less sensitive detection
            {'dp': 2, 'minDist': 120, 'param1': 60, 'param2': 35, 'minRadius': 60, 'maxRadius': 250},
        ]
        
        best_circle = None
        max_radius = 0
        
        # Apply Gaussian blur to improve circle detection
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        for config in circle_configs:
            try:
                circles = cv2.HoughCircles(
                    blurred, 
                    cv2.HOUGH_GRADIENT,
                    **config
                )
                
                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    # Find the largest circle
                    for circle in circles:
                        x, y, r = circle
                        # Ensure circle is within frame bounds
                        if (r > max_radius and 
                            r > 30 and  # Minimum reasonable wheel size
                            x - r > 0 and y - r > 0 and 
                            x + r < frame.shape[1] and y + r < frame.shape[0]):
                            best_circle = circle
                            max_radius = r
            except:
                continue
        
        if best_circle is not None:
            x, y, r = best_circle
            # Return bounding box with padding for full roulette table
            padding = int(r * 0.6)  # Increased padding to capture full table
            crop_x = max(0, x - r - padding)
            crop_y = max(0, y - r - padding)
            crop_w = min(frame.shape[1] - crop_x, 2 * r + 2 * padding)
            crop_h = min(frame.shape[0] - crop_y, 2 * r + 2 * padding)
            
            print(f"   🎯 Roulette wheel detected at ({x}, {y}) with radius {r}")
            return (crop_x, crop_y, crop_w, crop_h)
        
        # Enhanced fallback: look for green areas (roulette table felt)
        print("   🔍 No wheel found, looking for green table areas...")
        
        # Define green color range for roulette table
        lower_green = np.array([35, 40, 40])  # Lower HSV bound for green
        upper_green = np.array([85, 255, 255])  # Upper HSV bound for green
        
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours in green areas
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest green area
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            # If the green area is significant, use it
            if area > frame.shape[0] * frame.shape[1] * 0.05:  # At least 5% of frame
                x, y, w, h = cv2.boundingRect(largest_contour)
                print(f"   🟢 Green table area found at ({x}, {y}) with size {w}x{h}")
                
                # Add some padding around the green area
                padding = 20
                crop_x = max(0, x - padding)
                crop_y = max(0, y - padding)
                crop_w = min(frame.shape[1] - crop_x, w + 2 * padding)
                crop_h = min(frame.shape[0] - crop_y, h + 2 * padding)
                
                return (crop_x, crop_y, crop_w, crop_h)
        
        # Final fallback: intelligent center crop based on aspect ratio
        print("   📏 Using intelligent center crop")
        h, w = frame.shape[:2]
        
        # Assume roulette area is in center with reasonable aspect ratio
        if w > h:  # Landscape
            # Take center square-ish area
            size = min(w * 0.8, h * 0.9)
            crop_x = int((w - size) / 2)
            crop_y = int((h - size) / 2)
            crop_w = crop_h = int(size)
        else:  # Portrait or square
            # Take most of the width, centered vertically
            crop_w = int(w * 0.9)
            crop_h = int(h * 0.8)
            crop_x = int((w - crop_w) / 2)
            crop_y = int((h - crop_h) / 2)
        
        return (crop_x, crop_y, crop_w, crop_h)
    
    async def capture_roulette_area(self) -> np.ndarray:
        """Capture and crop to roulette area only."""
        frame = await self.capture_frame()
        x, y, w, h = await self.find_roulette_area(frame)
        return frame[y:y+h, x:x+w]
    
    async def start_continuous_capture(self, callback, interval: float = 0.1):
        """
        Start continuous capture with callback for each frame.
        Optimized for better FPS performance.
        
        Args:
            callback: Function to call with each captured frame
            interval: Time between captures in seconds (reduced for better FPS)
        """
        self.is_capturing = True
        
        # Performance optimization: pre-allocate variables
        frame_count = 0
        error_count = 0
        last_successful_crop = None
        
        print(f"🎥 Starting continuous capture at {1/interval:.1f} FPS target")
        
        while self.is_capturing:
            try:
                start_time = time.time()
                
                # Capture full frame
                frame = await self.capture_frame()
                
                # Use cached crop area if detection fails (for performance)
                if last_successful_crop:
                    x, y, w, h = last_successful_crop
                    roulette_frame = frame[y:y+h, x:x+w]
                    
                    # Re-detect every 10th frame to adjust for changes
                    if frame_count % 10 == 0:
                        try:
                            new_crop = await self.find_roulette_area(frame)
                            last_successful_crop = new_crop
                            x, y, w, h = new_crop
                            roulette_frame = frame[y:y+h, x:x+w]
                        except:
                            pass  # Keep using cached crop
                else:
                    # First time or no cached crop
                    x, y, w, h = await self.find_roulette_area(frame)
                    last_successful_crop = (x, y, w, h)
                    roulette_frame = frame[y:y+h, x:x+w]
                
                # Call processing callback
                await callback(roulette_frame)
                
                frame_count += 1
                error_count = 0  # Reset error count on success
                
                # Adaptive timing for consistent FPS
                processing_time = time.time() - start_time
                sleep_time = max(0, interval - processing_time)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                elif processing_time > interval * 2:
                    # If processing is too slow, warn and adjust
                    print(f"⚠️  Processing slow: {processing_time:.3f}s (target: {interval:.3f}s)")
                    
            except Exception as e:
                error_count += 1
                print(f"Capture error #{error_count}: {e}")
                
                # If too many consecutive errors, increase interval
                if error_count > 5:
                    interval = min(interval * 1.5, 1.0)  # Max 1 second interval
                    print(f"   Adjusted interval to {interval:.3f}s due to errors")
                    error_count = 0
                
                await asyncio.sleep(min(1.0, interval * 2))  # Wait before retrying
    
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