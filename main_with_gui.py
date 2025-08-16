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
        self.root.geometry("1200x800")  # Increased width for sidebar
        
        # Configure style
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        self.prediction_system = None
        self.system_thread = None
        self.is_running = False
        self.current_section = "prediction"  # Track current active section
        
        self._create_interface()
        self._load_default_settings()
        
        # Setup logging to GUI
        self._setup_logging()
    
    def _create_interface(self):
        """Create the main GUI interface."""
        # Create main container with horizontal layout
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)
        
        # Create navigation sidebar
        self._create_sidebar(main_container)
        
        # Create main content area
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(side='right', fill='both', expand=True, padx=(0, 10), pady=10)
        
        # Create content sections (initially hidden)
        self.sections = {}
        self._create_prediction_section()
        self._create_pricing_section()
        self._create_podcast_section()
        self._create_tts_section()
        self._create_status_section()
        
        # Show initial section
        self._show_section("prediction")
    
    def _create_sidebar(self, parent):
        """Create the navigation sidebar."""
        # Sidebar frame
        sidebar_frame = ttk.Frame(parent, width=200)
        sidebar_frame.pack(side='left', fill='y', padx=(10, 0), pady=10)
        sidebar_frame.pack_propagate(False)  # Maintain fixed width
        
        # Sidebar title
        title_label = ttk.Label(sidebar_frame, text="🎰 Navigation", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("prediction", "🎯 Prediction System", "Main roulette prediction interface"),
            ("pricing", "💰 Pricing", "Pricing information and plans"),
            ("podcast", "🎙️ Podcast", "Podcast generation and management"),
            ("tts", "🔊 TTS Settings", "Text-to-speech configuration"),
            ("status", "📊 Status & Logs", "System status and logs")
        ]
        
        for section_id, title, description in nav_items:
            # Create button frame
            btn_frame = ttk.Frame(sidebar_frame)
            btn_frame.pack(fill='x', pady=(0, 5))
            
            # Navigation button
            btn = ttk.Button(btn_frame, text=title,
                           command=lambda s=section_id: self._show_section(s),
                           width=25)
            btn.pack(fill='x')
            self.nav_buttons[section_id] = btn
            
            # Description label
            desc_label = ttk.Label(btn_frame, text=description, 
                                 font=('Arial', 8), foreground='gray')
            desc_label.pack(anchor='w', padx=(5, 0))
        
        # Separator
        ttk.Separator(sidebar_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Quick actions
        quick_frame = ttk.LabelFrame(sidebar_frame, text="Quick Actions", padding="10")
        quick_frame.pack(fill='x', pady=(0, 10))
        
        quick_test_btn = ttk.Button(quick_frame, text="🧪 Test System",
                                   command=self._test_components)
        quick_test_btn.pack(fill='x', pady=(0, 5))
        
        quick_tts_btn = ttk.Button(quick_frame, text="🎵 Test TTS",
                                  command=self._quick_tts_test)
        quick_tts_btn.pack(fill='x')
    
    def _show_section(self, section_id):
        """Show the specified section and hide others."""
        # Hide all sections
        for section_frame in self.sections.values():
            section_frame.pack_forget()
        
        # Show selected section
        if section_id in self.sections:
            self.sections[section_id].pack(fill='both', expand=True)
            self.current_section = section_id
            
            # Update button styles to show active section
            for btn_id, btn in self.nav_buttons.items():
                if btn_id == section_id:
                    btn.configure(style='Accent.TButton')
                else:
                    btn.configure(style='TButton')
    
    def _quick_tts_test(self):
        """Quick TTS test function."""
        def test_thread():
            try:
                tts = get_tts_system()
                tts.speak("Quick TTS test from navigation sidebar")
                self._log("Quick TTS test completed")
            except Exception as e:
                self._log(f"TTS test failed: {e}")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _create_prediction_section(self):
        """Create the main prediction system section."""
        main_frame = ttk.Frame(self.content_frame)
        self.sections["prediction"] = main_frame
        
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
    
    def _create_pricing_section(self):
        """Create the pricing section."""
        pricing_frame = ttk.Frame(self.content_frame)
        self.sections["pricing"] = pricing_frame
        
        # Title
        title_label = ttk.Label(pricing_frame, text="💰 Pricing Plans", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Description
        desc_label = ttk.Label(pricing_frame, 
                              text="Choose the perfect plan for your roulette prediction needs",
                              font=('Arial', 12))
        desc_label.pack(pady=(0, 30))
        
        # Pricing cards container
        cards_frame = ttk.Frame(pricing_frame)
        cards_frame.pack(fill='both', expand=True, padx=20)
        
        # Basic Plan
        basic_frame = ttk.LabelFrame(cards_frame, text="Basic Plan", padding="20")
        basic_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(basic_frame, text="$9.99/month", font=('Arial', 14, 'bold')).pack()
        ttk.Label(basic_frame, text="Perfect for beginners").pack(pady=(5, 15))
        
        basic_features = [
            "✓ Basic prediction algorithm",
            "✓ Standard TTS voices",
            "✓ Up to 100 predictions/day",
            "✓ Email support"
        ]
        for feature in basic_features:
            ttk.Label(basic_frame, text=feature).pack(anchor='w', pady=2)
        
        ttk.Button(basic_frame, text="Choose Basic", 
                  command=lambda: self._select_plan("basic")).pack(pady=(15, 0))
        
        # Pro Plan
        pro_frame = ttk.LabelFrame(cards_frame, text="Pro Plan ⭐", padding="20")
        pro_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(pro_frame, text="$29.99/month", font=('Arial', 14, 'bold')).pack()
        ttk.Label(pro_frame, text="Most popular choice").pack(pady=(5, 15))
        
        pro_features = [
            "✓ Advanced prediction algorithm",
            "✓ Premium TTS voices",
            "✓ Unlimited predictions",
            "✓ Real-time analytics",
            "✓ Priority support"
        ]
        for feature in pro_features:
            ttk.Label(pro_frame, text=feature).pack(anchor='w', pady=2)
        
        ttk.Button(pro_frame, text="Choose Pro", style='Accent.TButton',
                  command=lambda: self._select_plan("pro")).pack(pady=(15, 0))
        
        # Enterprise Plan
        enterprise_frame = ttk.LabelFrame(cards_frame, text="Enterprise Plan", padding="20")
        enterprise_frame.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
        ttk.Label(enterprise_frame, text="$99.99/month", font=('Arial', 14, 'bold')).pack()
        ttk.Label(enterprise_frame, text="For professionals").pack(pady=(5, 15))
        
        enterprise_features = [
            "✓ AI-powered predictions",
            "✓ Custom TTS voices",
            "✓ API access",
            "✓ Multi-table support",
            "✓ 24/7 phone support",
            "✓ Custom integrations"
        ]
        for feature in enterprise_features:
            ttk.Label(enterprise_frame, text=feature).pack(anchor='w', pady=2)
        
        ttk.Button(enterprise_frame, text="Choose Enterprise",
                  command=lambda: self._select_plan("enterprise")).pack(pady=(15, 0))
    
    def _create_podcast_section(self):
        """Create the podcast generation section."""
        podcast_frame = ttk.Frame(self.content_frame)
        self.sections["podcast"] = podcast_frame
        
        # Title
        title_label = ttk.Label(podcast_frame, text="🎙️ Podcast Generation", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Description
        desc_label = ttk.Label(podcast_frame, 
                              text="Generate engaging podcasts about roulette strategies and predictions",
                              font=('Arial', 12))
        desc_label.pack(pady=(0, 30))
        
        # Podcast creation form
        form_frame = ttk.LabelFrame(podcast_frame, text="Create New Podcast", padding="20")
        form_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Podcast title
        title_input_frame = ttk.Frame(form_frame)
        title_input_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(title_input_frame, text="Podcast Title:").pack(side='left')
        self.podcast_title_var = tk.StringVar(value="Roulette Strategies Weekly")
        ttk.Entry(title_input_frame, textvariable=self.podcast_title_var, width=50).pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Topic selection
        topic_frame = ttk.Frame(form_frame)
        topic_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(topic_frame, text="Topic:").pack(side='left')
        self.podcast_topic_var = tk.StringVar(value="prediction_strategies")
        topics = [
            ("prediction_strategies", "Prediction Strategies"),
            ("betting_systems", "Betting Systems"),
            ("risk_management", "Risk Management"),
            ("psychology", "Psychology of Gambling"),
            ("technology", "Technology in Gaming")
        ]
        topic_combo = ttk.Combobox(topic_frame, textvariable=self.podcast_topic_var, 
                                  values=[topic[0] for topic in topics], state='readonly')
        topic_combo.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Duration
        duration_frame = ttk.Frame(form_frame)
        duration_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(duration_frame, text="Duration:").pack(side='left')
        self.podcast_duration_var = tk.StringVar(value="15")
        duration_spin = ttk.Spinbox(duration_frame, from_=5, to=60, textvariable=self.podcast_duration_var, width=10)
        duration_spin.pack(side='left', padx=(10, 5))
        ttk.Label(duration_frame, text="minutes").pack(side='left')
        
        # Voice selection
        voice_frame = ttk.Frame(form_frame)
        voice_frame.pack(fill='x', pady=(0, 15))
        ttk.Label(voice_frame, text="Voice:").pack(side='left')
        self.podcast_voice_var = tk.StringVar(value="professional_male")
        voices = ["professional_male", "professional_female", "casual_male", "casual_female"]
        voice_combo = ttk.Combobox(voice_frame, textvariable=self.podcast_voice_var, 
                                  values=voices, state='readonly')
        voice_combo.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Generate button
        ttk.Button(form_frame, text="🎵 Generate Podcast", style='Accent.TButton',
                  command=self._generate_podcast).pack()
        
        # Recent podcasts
        recent_frame = ttk.LabelFrame(podcast_frame, text="Recent Podcasts", padding="20")
        recent_frame.pack(fill='both', expand=True, padx=20)
        
        # Sample recent podcasts
        recent_podcasts = [
            "🎙️ Roulette Strategies Weekly - Episode 1 (15 min)",
            "🎙️ Advanced Betting Systems - Episode 2 (22 min)",
            "🎙️ Psychology of Winning - Episode 3 (18 min)"
        ]
        
        for podcast in recent_podcasts:
            podcast_item_frame = ttk.Frame(recent_frame)
            podcast_item_frame.pack(fill='x', pady=2)
            ttk.Label(podcast_item_frame, text=podcast).pack(side='left')
            ttk.Button(podcast_item_frame, text="▶️ Play", width=8).pack(side='right', padx=(0, 5))
            ttk.Button(podcast_item_frame, text="📥 Download", width=10).pack(side='right', padx=(0, 5))
    
    def _create_tts_section(self):
        """Create the TTS settings section."""
        tts_frame = ttk.Frame(self.content_frame)
        self.sections["tts"] = tts_frame
        
        self.tts_gui = TTSSettingsGUI(tts_frame, self._on_tts_setting_change)
    
    def _create_status_section(self):
        """Create the status/log section."""
        status_frame = ttk.Frame(self.content_frame)
        self.sections["status"] = status_frame
        
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
    
    def _select_plan(self, plan_type):
        """Handle plan selection."""
        self._log(f"Selected {plan_type} plan")
        messagebox.showinfo("Plan Selected", 
                           f"You have selected the {plan_type.title()} plan.\n"
                           f"This is a demonstration - no actual payment will be processed.")
    
    def _generate_podcast(self):
        """Generate a new podcast."""
        title = self.podcast_title_var.get()
        topic = self.podcast_topic_var.get()
        duration = self.podcast_duration_var.get()
        voice = self.podcast_voice_var.get()
        
        self._log(f"Generating podcast: {title} ({duration} min, {topic}, {voice})")
        
        def generate_thread():
            try:
                # Simulate podcast generation
                for i in range(1, 6):
                    time.sleep(1)
                    self.root.after(0, lambda i=i: self._log(f"Generating podcast... {i*20}%"))
                
                self.root.after(0, lambda: self._log("Podcast generation completed!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"Podcast '{title}' has been generated successfully!\n"
                    f"Duration: {duration} minutes\nTopic: {topic}\nVoice: {voice}"))
                
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Podcast generation failed: {e}"))
        
        threading.Thread(target=generate_thread, daemon=True).start()
    
    def _load_default_settings(self):
        """Load default configuration settings."""
        # Settings loaded in _create_prediction_section with default values
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