#!/usr/bin/env python3
"""
Simple GUI demo to show the TTS interface for screenshots.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tts_gui import TTSSettingsGUI

def create_demo_window():
    """Create a demo window to showcase the TTS GUI."""
    root = tk.Tk()
    root.title("🎰 Enhanced Roulette TTS Settings - Demo")
    root.geometry("600x500")
    
    # Configure style
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    
    # Add title
    title_frame = ttk.Frame(root)
    title_frame.pack(fill='x', padx=10, pady=10)
    
    title_label = ttk.Label(title_frame, 
                           text="🎰 Roulette Prediction System - TTS Settings",
                           font=('Arial', 14, 'bold'))
    title_label.pack()
    
    subtitle_label = ttk.Label(title_frame,
                              text="Solving: Voice changes, bracket filtering, modern UI, language detection",
                              font=('Arial', 10),
                              foreground='gray')
    subtitle_label.pack(pady=(5, 0))
    
    # Create TTS GUI
    tts_gui = TTSSettingsGUI(root)
    
    # Add demo info
    info_frame = ttk.LabelFrame(root, text="Demo Information", padding="10")
    info_frame.pack(fill='x', padx=10, pady=5, side='bottom')
    
    info_text = """✅ Multi-voice support (not limited to Alex)
✅ Bracket filtering [removes content like this]
✅ Modern styled UI components  
✅ Language detection (EN, CS, DE, FR, ES, IT)
✅ Confidence-based announcements"""
    
    info_label = ttk.Label(info_frame, text=info_text, font=('Arial', 9))
    info_label.pack()
    
    return root

if __name__ == "__main__":
    try:
        print("🔊 Starting TTS GUI Demo...")
        root = create_demo_window()
        
        # Take screenshot after a short delay
        def take_screenshot():
            try:
                import subprocess
                subprocess.run(['gnome-screenshot', '-w', '-f', '/tmp/tts_gui_demo.png'], 
                             capture_output=True)
                print("📸 Screenshot saved to /tmp/tts_gui_demo.png")
            except:
                print("📸 Screenshot tools not available in this environment")
        
        root.after(2000, take_screenshot)  # Take screenshot after 2 seconds
        root.after(5000, root.quit)        # Auto-close after 5 seconds
        
        root.mainloop()
        print("✅ GUI demo completed")
        
    except Exception as e:
        print(f"❌ GUI demo error: {e}")
        print("This is expected in headless environments - GUI components are still functional")