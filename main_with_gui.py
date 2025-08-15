#!/usr/bin/env python3
"""
Enhanced roulette prediction system with TTS and GUI interface.
"""

import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional
import logging

# Import the main prediction system
from main import RoulettePredictionSystem
from tts_gui import TTSSettingsGUI, QuickTTSControl
from tts_system import get_tts_system


class RoulettePredictionGUI:
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("🎰 Enhanced Roulette Prediction System")
        self.root.geometry("900x700")
        
        # Configure style
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        self.prediction_system = None
        self.system_thread = None
        self.is_running = False
        
        self._create_interface()
        self._load_default_settings()
        
        # Setup logging to GUI
        self._setup_logging()
    
    def _create_interface(self):
        """Create the main GUI interface."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main control tab
        self._create_main_tab()
        
        # TTS settings tab
        self._create_tts_tab()
        
        # Status/log tab
        self._create_status_tab()
    
    def _create_main_tab(self):
        """Create the main control interface."""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="🎯 Prediction System")
        
        # Title
        title_label = ttk.Label(main_frame, text="🎰 Enhanced Roulette Prediction System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="15")
        config_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # URL input
        url_frame = ttk.Frame(config_frame)
        url_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(url_frame, text="Stream URL:").pack(side='left')
        self.url_var = tk.StringVar(value="https://www.tokyo.cz/game/tomhornlive_56")
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Credentials
        cred_frame = ttk.Frame(config_frame)
        cred_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(cred_frame, text="Email:").pack(side='left')
        self.email_var = tk.StringVar(value="martin298@post.cz")
        email_entry = ttk.Entry(cred_frame, textvariable=self.email_var, width=25)
        email_entry.pack(side='left', padx=(10, 20))
        
        ttk.Label(cred_frame, text="Password:").pack(side='left')
        self.password_var = tk.StringVar(value="Certik298")
        password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, 
                                  show="*", width=25)
        password_entry.pack(side='left', padx=(10, 0))
        
        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill='x')
        
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(options_frame, text="Headless mode (no browser window)",
                                        variable=self.headless_var)
        headless_check.pack(side='left')
        
        # Quick TTS control
        tts_frame = ttk.LabelFrame(main_frame, text="Quick TTS Control", padding="15")
        tts_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.quick_tts = QuickTTSControl(tts_frame, self._on_tts_setting_change)
        self.quick_tts.pack(fill='x')
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', padx=20, pady=20)
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Prediction System",
                                      command=self._start_system, style='Accent.TButton')
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Stop System",
                                     command=self._stop_system, state='disabled')
        self.stop_button.pack(side='left', padx=(0, 10))
        
        self.test_button = ttk.Button(control_frame, text="🧪 Test Components",
                                     command=self._test_components)
        self.test_button.pack(side='left')
        
        # Status display
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="15")
        status_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.status_var = tk.StringVar(value="System ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                font=('Arial', 12))
        status_label.pack(pady=10)
        
        # Performance metrics
        metrics_frame = ttk.Frame(status_frame)
        metrics_frame.pack(fill='x', pady=(10, 0))
        
        self.fps_var = tk.StringVar(value="FPS: --")
        self.detection_var = tk.StringVar(value="Detections: --")
        self.prediction_var = tk.StringVar(value="Predictions: --")
        
        ttk.Label(metrics_frame, textvariable=self.fps_var).pack(side='left')
        ttk.Label(metrics_frame, textvariable=self.detection_var).pack(side='left', padx=(20, 0))
        ttk.Label(metrics_frame, textvariable=self.prediction_var).pack(side='left', padx=(20, 0))
    
    def _create_tts_tab(self):
        """Create the TTS settings tab."""
        tts_frame = ttk.Frame(self.notebook)
        self.notebook.add(tts_frame, text="🔊 TTS Settings")
        
        self.tts_gui = TTSSettingsGUI(tts_frame, self._on_tts_setting_change)
    
    def _create_status_tab(self):
        """Create the status/log tab."""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="📊 Status & Logs")
        
        # Log display
        log_frame = ttk.LabelFrame(status_frame, text="System Logs", padding="10")
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(text_frame, wrap='word', state='disabled',
                               font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Log control buttons
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill='x', pady=(10, 0))
        
        clear_button = ttk.Button(log_control_frame, text="🗑️ Clear Logs",
                                 command=self._clear_logs)
        clear_button.pack(side='left')
        
        save_button = ttk.Button(log_control_frame, text="💾 Save Logs",
                                command=self._save_logs)
        save_button.pack(side='left', padx=(10, 0))
    
    def _load_default_settings(self):
        """Load default configuration settings."""
        # Settings loaded in _create_main_tab with default values
        pass
    
    def _setup_logging(self):
        """Setup logging to display in GUI."""
        # Create custom handler for GUI logging
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                if hasattr(self.text_widget, 'insert'):
                    self.text_widget.config(state='normal')
                    self.text_widget.insert('end', msg + '\n')
                    self.text_widget.see('end')
                    self.text_widget.config(state='disabled')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Add GUI handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
    
    def _on_tts_setting_change(self, setting: str, value):
        """Handle TTS setting changes."""
        self._log(f"TTS setting changed: {setting} = {value}")
    
    def _log(self, message: str):
        """Log a message to the GUI."""
        logging.info(message)
    
    def _start_system(self):
        """Start the prediction system in a separate thread."""
        if self.is_running:
            messagebox.showwarning("Already Running", "Prediction system is already running!")
            return
        
        # Validate inputs
        url = self.url_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not url:
            messagebox.showerror("Invalid Input", "Please enter a stream URL")
            return
        
        if not email or not password:
            messagebox.showerror("Invalid Input", "Please enter email and password")
            return
        
        # Update UI
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_running = True
        self.status_var.set("Starting prediction system...")
        
        # Start system in background thread
        self.system_thread = threading.Thread(target=self._run_system_thread, 
                                             args=(url, email, password, self.headless_var.get()),
                                             daemon=True)
        self.system_thread.start()
        
        self._log(f"Starting prediction system with URL: {url}")
    
    def _run_system_thread(self, url: str, email: str, password: str, headless: bool):
        """Run the prediction system in a background thread."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create and run prediction system
            self.prediction_system = RoulettePredictionSystem(
                url=url, headless=headless, email=email, password=password
            )
            
            # Run the system
            loop.run_until_complete(self._run_system_async())
            
        except Exception as e:
            self._log(f"System error: {e}")
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
        finally:
            self.root.after(0, self._system_stopped)
    
    async def _run_system_async(self):
        """Run the async prediction system."""
        try:
            self.root.after(0, lambda: self.status_var.set("Initializing..."))
            await self.prediction_system.initialize()
            
            self.root.after(0, lambda: self.status_var.set("Running prediction system..."))
            await self.prediction_system.run()
            
        except Exception as e:
            self._log(f"Async system error: {e}")
            raise
        finally:
            if self.prediction_system:
                await self.prediction_system.cleanup()
    
    def _stop_system(self):
        """Stop the prediction system."""
        if not self.is_running:
            return
        
        self.status_var.set("Stopping system...")
        self._log("Stopping prediction system...")
        
        if self.prediction_system:
            self.prediction_system.stop()
        
        self.is_running = False
    
    def _system_stopped(self):
        """Handle system stopped event (called from main thread)."""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.is_running = False
        self.status_var.set("System stopped")
        self.fps_var.set("FPS: --")
        self.detection_var.set("Detections: --")
        self.prediction_var.set("Predictions: --")
        self._log("Prediction system stopped")
    
    def _test_components(self):
        """Test system components."""
        self.status_var.set("Testing components...")
        self._log("Testing system components...")
        
        def test_thread():
            try:
                # Test TTS
                tts = get_tts_system()
                tts.speak("Testing TTS system")
                time.sleep(1)
                tts.speak_prediction("Test prediction: Number 17", confidence=0.8)
                
                self.root.after(0, lambda: self.status_var.set("Component test completed"))
                self._log("Component test completed successfully")
                
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Test failed: {e}"))
                self._log(f"Component test failed: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _clear_logs(self):
        """Clear the log display."""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')
    
    def _save_logs(self):
        """Save logs to file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="Save Logs",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                logs = self.log_text.get('1.0', 'end-1c')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(logs)
                messagebox.showinfo("Success", f"Logs saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def run(self):
        """Start the GUI application."""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()
    
    def _on_closing(self):
        """Handle application closing."""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Prediction system is running. Stop and quit?"):
                self._stop_system()
                time.sleep(1)  # Give time to stop
            else:
                return
        
        # Cleanup TTS
        from tts_system import cleanup_tts
        cleanup_tts()
        
        self.root.destroy()


def main():
    """Main entry point for GUI application."""
    print("🎰 Enhanced Roulette Prediction System with TTS")
    print("=" * 50)
    print("Starting GUI interface...")
    
    try:
        app = RoulettePredictionGUI()
        app.run()
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()