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
    def __init__(self, url: str, headless: bool = True):
        self.url = url
        self.headless = headless
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
        await asyncio.sleep(3)  # Additional wait for stream to start
        
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
async def capture_single_frame(url: str) -> np.ndarray:
    """Capture a single frame from the stream URL."""
    capture = StreamCapture(url)
    try:
        await capture.initialize()
        frame = await capture.capture_roulette_area()
        return frame
    finally:
        await capture.cleanup()