"""
Alternative stream capture using Selenium WebDriver.
Provides fallback when Playwright is not available or working.
"""

import time
import cv2
import numpy as np
from PIL import Image
import io
import asyncio
from typing import Optional, Callable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SeleniumStreamCapture:
    def __init__(self, url: str, headless: bool = True, email: str = None, password: str = None):
        self.url = url
        self.headless = headless
        self.email = email
        self.password = password
        self.driver = None
        self.is_capturing = False
        
    def initialize(self):
        """Initialize browser and navigate to stream."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Additional options for better compatibility
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading
        chrome_options.add_argument("--mute-audio")
        
        # User agent to appear more like a regular browser
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            
            print(f"🌐 Navigating to: {self.url}")
            self.driver.get(self.url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # If credentials are provided, attempt to login
            if self.email and self.password:
                self.login()
            
            # Dismiss overlays and optimize view
            self.dismiss_overlays()
            self.click_video_controls()
            
            time.sleep(3)  # Additional wait for stream to start
            
        except Exception as e:
            print(f"❌ Failed to initialize Selenium browser: {e}")
            if self.driver:
                self.driver.quit()
            raise
    
    def login(self):
        """Attempt to login using provided credentials."""
        try:
            print("🔐 Attempting to login...")
            
            # Look for login fields
            email_selectors = [
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
                'button:contains("Přihlásit")',
                'button:contains("Login")',
                '.login-button',
                '#login-button'
            ]
            
            # Find and fill email
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if email_field:
                email_field.clear()
                email_field.send_keys(self.email)
                print("✓ Filled email")
            
            # Find and fill password
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if password_field:
                password_field.clear()
                password_field.send_keys(self.password)
                print("✓ Filled password")
            
            # Find and click submit
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                submit_button.click()
                print("✓ Clicked login button")
                time.sleep(3)  # Wait for login to complete
            
        except Exception as e:
            print(f"⚠️  Login attempt failed: {e}")
    
    def dismiss_overlays(self):
        """Dismiss cookie banners and overlays."""
        try:
            print("🚫 Dismissing overlays...")
            
            overlay_selectors = [
                'button:contains("Accept")',
                'button:contains("Přijmout")',
                'button:contains("OK")',
                'button:contains("Close")',
                'button:contains("Zavřít")',
                '.cookie-accept',
                '.modal-close',
                '.popup-close',
                'button[class*="close"]',
                '.overlay-close'
            ]
            
            overlays_dismissed = 0
            for selector in overlay_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            overlays_dismissed += 1
                            print(f"   ✓ Dismissed overlay ({overlays_dismissed})")
                            time.sleep(1)
                except:
                    continue
            
            if overlays_dismissed == 0:
                print("   No overlays found to dismiss")
            
        except Exception as e:
            print(f"⚠️  Error dismissing overlays: {e}")
    
    def click_video_controls(self):
        """Click video play and optimization buttons."""
        try:
            print("🎬 Looking for video controls...")
            
            # Play button selectors
            play_selectors = [
                'button[aria-label*="play"]',
                'button[title*="play"]',
                '.play-button',
                '.video-play-button',
                'button:contains("Play")',
                'button:contains("Přehrát")'
            ]
            
            # Fullscreen selectors
            fullscreen_selectors = [
                'button[aria-label*="fullscreen"]',
                'button[title*="fullscreen"]',
                '.fullscreen-button',
                'button:contains("⛶")'
            ]
            
            # Mute/unmute for autoplay
            audio_selectors = [
                'button[aria-label*="mute"]',
                'button[aria-label*="unmute"]',
                'button[title*="sound"]',
                '.mute-button'
            ]
            
            controls_clicked = 0
            
            # Try play buttons
            for selector in play_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            controls_clicked += 1
                            print(f"   ✓ Clicked play button ({controls_clicked})")
                            time.sleep(1)
                except:
                    continue
            
            # Try audio controls
            for selector in audio_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            controls_clicked += 1
                            print(f"   ✓ Clicked audio control ({controls_clicked})")
                            time.sleep(1)
                except:
                    continue
            
            # Try fullscreen
            for selector in fullscreen_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            controls_clicked += 1
                            print(f"   ✓ Clicked fullscreen ({controls_clicked})")
                            time.sleep(2)
                            break  # Only click one fullscreen button
                except:
                    continue
            
            if controls_clicked > 0:
                print(f"✓ Clicked {controls_clicked} video control(s)")
            else:
                print("   No video controls found")
            
        except Exception as e:
            print(f"⚠️  Error with video controls: {e}")
    
    def capture_frame(self) -> np.ndarray:
        """Capture a single frame from the browser."""
        if not self.driver:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        # Take screenshot
        screenshot = self.driver.get_screenshot_as_png()
        
        # Convert to OpenCV format
        image = Image.open(io.BytesIO(screenshot))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        return frame
    
    def find_roulette_area(self, frame: np.ndarray) -> tuple:
        """Find the roulette area (same logic as Playwright version)."""
        # This is the same enhanced detection logic from the Playwright version
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Multiple circle detection configurations
        circle_configs = [
            {'dp': 1, 'minDist': 80, 'param1': 40, 'param2': 25, 'minRadius': 40, 'maxRadius': 400},
            {'dp': 1, 'minDist': 100, 'param1': 50, 'param2': 30, 'minRadius': 50, 'maxRadius': 300},
            {'dp': 2, 'minDist': 120, 'param1': 60, 'param2': 35, 'minRadius': 60, 'maxRadius': 250},
        ]
        
        best_circle = None
        max_radius = 0
        
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
                    for circle in circles:
                        x, y, r = circle
                        if (r > max_radius and r > 30 and 
                            x - r > 0 and y - r > 0 and 
                            x + r < frame.shape[1] and y + r < frame.shape[0]):
                            best_circle = circle
                            max_radius = r
            except:
                continue
        
        if best_circle is not None:
            x, y, r = best_circle
            padding = int(r * 0.6)
            crop_x = max(0, x - r - padding)
            crop_y = max(0, y - r - padding)
            crop_w = min(frame.shape[1] - crop_x, 2 * r + 2 * padding)
            crop_h = min(frame.shape[0] - crop_y, 2 * r + 2 * padding)
            
            print(f"   🎯 Roulette wheel detected at ({x}, {y}) with radius {r}")
            return (crop_x, crop_y, crop_w, crop_h)
        
        # Fallback: center crop
        h, w = frame.shape[:2]
        if w > h:
            size = min(w * 0.8, h * 0.9)
            crop_x = int((w - size) / 2)
            crop_y = int((h - size) / 2)
            crop_w = crop_h = int(size)
        else:
            crop_w = int(w * 0.9)
            crop_h = int(h * 0.8)
            crop_x = int((w - crop_w) / 2)
            crop_y = int((h - crop_h) / 2)
        
        return (crop_x, crop_y, crop_w, crop_h)
    
    def capture_roulette_area(self) -> np.ndarray:
        """Capture and crop to roulette area only."""
        frame = self.capture_frame()
        x, y, w, h = self.find_roulette_area(frame)
        return frame[y:y+h, x:x+w]
    
    def start_continuous_capture(self, callback: Callable, interval: float = 0.1):
        """Start continuous capture with callback for each frame."""
        self.is_capturing = True
        
        while self.is_capturing:
            try:
                frame = self.capture_roulette_area()
                callback(frame)
                time.sleep(interval)
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(1)
    
    def stop_capture(self):
        """Stop continuous capture."""
        self.is_capturing = False
    
    def cleanup(self):
        """Clean up browser resources."""
        if self.driver:
            self.driver.quit()


# Convenience function for single frame capture
def capture_single_frame_selenium(url: str, email: str = None, password: str = None) -> np.ndarray:
    """Capture a single frame using Selenium."""
    capture = SeleniumStreamCapture(url, headless=True, email=email, password=password)
    try:
        capture.initialize()
        frame = capture.capture_roulette_area()
        return frame
    finally:
        capture.cleanup()