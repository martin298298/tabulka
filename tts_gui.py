#!/usr/bin/env python3
"""
GUI interface for TTS and language settings with improved styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable, Optional
import threading
from tts_system import get_tts_system, TTSSystem


class TTSSettingsGUI:
    def __init__(self, parent=None, on_settings_change: Optional[Callable] = None):
        """
        Initialize the TTS settings GUI.
        
        Args:
            parent: Parent window (None for standalone)
            on_settings_change: Callback function when settings change
        """
        self.tts = get_tts_system()
        self.on_settings_change = on_settings_change
        
        # Create main window or frame
        if parent is None:
            self.root = tk.Tk()
            self.root.title("TTS Settings")
            self.root.geometry("500x400")
            self.main_frame = self.root
        else:
            self.root = parent
            self.main_frame = ttk.Frame(parent)
            self.main_frame.pack(fill='both', expand=True)
        
        self._setup_styles()
        self._create_widgets()
        self._load_current_settings()
        
    def _setup_styles(self):
        """Setup custom styles for better appearance."""
        self.style = ttk.Style()
        
        # Configure modern style theme
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'alt' in available_themes:
            self.style.theme_use('alt')
        
        # Custom styles
        self.style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'))
        self.style.configure('Modern.TButton', padding=(10, 5))
        
        # Configure combobox style
        self.style.configure('Modern.TCombobox', 
                            fieldbackground='white',
                            selectbackground='#0078d4',
                            selectforeground='white')
        
        # Configure frame styles
        self.style.configure('Card.TFrame', relief='solid', borderwidth=1)
        
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container with padding
        container = ttk.Frame(self.main_frame, padding="20")
        container.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(container, text="🔊 Text-to-Speech Settings", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Voice Settings Card
        self._create_voice_settings_card(container)
        
        # Language Settings Card  
        self._create_language_settings_card(container)
        
        # Audio Settings Card
        self._create_audio_settings_card(container)
        
        # Filter Settings Card
        self._create_filter_settings_card(container)
        
        # Control Buttons
        self._create_control_buttons(container)
        
        # Status Bar
        self._create_status_bar(container)
    
    def _create_voice_settings_card(self, parent):
        """Create voice selection interface."""
        # Voice Settings Frame
        voice_frame = ttk.LabelFrame(parent, text="Voice Selection", padding="15")
        voice_frame.pack(fill='x', pady=(0, 15))
        
        # Current voice display
        current_frame = ttk.Frame(voice_frame)
        current_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(current_frame, text="Current Voice:", 
                 style='Subtitle.TLabel').pack(side='left')
        
        self.current_voice_var = tk.StringVar()
        self.current_voice_label = ttk.Label(current_frame, 
                                           textvariable=self.current_voice_var,
                                           foreground='#0078d4')
        self.current_voice_label.pack(side='left', padx=(10, 0))
        
        # Voice selection
        selection_frame = ttk.Frame(voice_frame)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(selection_frame, text="Select Voice:").pack(side='left')
        
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(selection_frame, 
                                       textvariable=self.voice_var,
                                       style='Modern.TCombobox',
                                       state='readonly',
                                       width=30)
        self.voice_combo.pack(side='left', padx=(10, 0), fill='x', expand=True)
        self.voice_combo.bind('<<ComboboxSelected>>', self._on_voice_change)
        
        # Test voice button
        test_button = ttk.Button(selection_frame, text="🎵 Test Voice", 
                                style='Modern.TButton',
                                command=self._test_voice)
        test_button.pack(side='right', padx=(10, 0))
    
    def _create_language_settings_card(self, parent):
        """Create language detection and selection interface."""
        lang_frame = ttk.LabelFrame(parent, text="Language Settings", padding="15")
        lang_frame.pack(fill='x', pady=(0, 15))
        
        # Auto language detection
        auto_frame = ttk.Frame(lang_frame)
        auto_frame.pack(fill='x', pady=(0, 10))
        
        self.auto_detect_var = tk.BooleanVar(value=True)
        auto_check = ttk.Checkbutton(auto_frame, 
                                    text="Auto-detect language for voice selection",
                                    variable=self.auto_detect_var,
                                    command=self._on_auto_detect_change)
        auto_check.pack(side='left')
        
        # Language status
        status_frame = ttk.Frame(lang_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(status_frame, text="Supported Languages:").pack(side='left')
        
        self.lang_status_var = tk.StringVar()
        lang_status_label = ttk.Label(status_frame, 
                                     textvariable=self.lang_status_var,
                                     foreground='#666666')
        lang_status_label.pack(side='left', padx=(10, 0))
        
        # Manual language override
        override_frame = ttk.Frame(lang_frame)
        override_frame.pack(fill='x')
        
        ttk.Label(override_frame, text="Manual Override:").pack(side='left')
        
        self.manual_lang_var = tk.StringVar()
        lang_combo = ttk.Combobox(override_frame,
                                 textvariable=self.manual_lang_var,
                                 style='Modern.TCombobox',
                                 state='readonly',
                                 width=20)
        lang_combo.pack(side='left', padx=(10, 0))
        
        # Populate language options
        supported_langs = self.tts.supported_languages
        lang_combo['values'] = ['Auto'] + [f"{code.upper()} - {name}" 
                                          for code, name in supported_langs.items()]
        lang_combo.set('Auto')
    
    def _create_audio_settings_card(self, parent):
        """Create audio quality and volume settings."""
        audio_frame = ttk.LabelFrame(parent, text="Audio Settings", padding="15")
        audio_frame.pack(fill='x', pady=(0, 15))
        
        # Speech rate
        rate_frame = ttk.Frame(audio_frame)
        rate_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(rate_frame, text="Speech Rate (WPM):").pack(side='left')
        
        self.rate_var = tk.IntVar(value=150)
        rate_scale = ttk.Scale(rate_frame, 
                              from_=50, to=300,
                              variable=self.rate_var,
                              orient='horizontal',
                              command=self._on_rate_change)
        rate_scale.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        self.rate_label = ttk.Label(rate_frame, text="150")
        self.rate_label.pack(side='right', padx=(10, 0))
        
        # Volume
        volume_frame = ttk.Frame(audio_frame)
        volume_frame.pack(fill='x')
        
        ttk.Label(volume_frame, text="Volume:").pack(side='left')
        
        self.volume_var = tk.DoubleVar(value=0.8)
        volume_scale = ttk.Scale(volume_frame,
                                from_=0.0, to=1.0,
                                variable=self.volume_var,
                                orient='horizontal', 
                                command=self._on_volume_change)
        volume_scale.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        self.volume_label = ttk.Label(volume_frame, text="80%")
        self.volume_label.pack(side='right', padx=(10, 0))
    
    def _create_filter_settings_card(self, parent):
        """Create text filtering options."""
        filter_frame = ttk.LabelFrame(parent, text="Text Filtering", padding="15")
        filter_frame.pack(fill='x', pady=(0, 15))
        
        # Bracket filtering
        bracket_frame = ttk.Frame(filter_frame)
        bracket_frame.pack(fill='x', pady=(0, 10))
        
        self.filter_brackets_var = tk.BooleanVar(value=True)
        bracket_check = ttk.Checkbutton(bracket_frame,
                                       text="Filter out content in square brackets [like this]",
                                       variable=self.filter_brackets_var,
                                       command=self._on_filter_change)
        bracket_check.pack(side='left')
        
        # Test filtering
        test_frame = ttk.Frame(filter_frame)
        test_frame.pack(fill='x')
        
        ttk.Label(test_frame, text="Test Text:").pack(side='top', anchor='w')
        
        self.test_text_var = tk.StringVar(value="Prediction [internal data] Number 17")
        test_entry = ttk.Entry(test_frame, textvariable=self.test_text_var, width=50)
        test_entry.pack(side='left', fill='x', expand=True, pady=(5, 0))
        
        test_filter_button = ttk.Button(test_frame, text="🔊 Test Filter",
                                       style='Modern.TButton',
                                       command=self._test_filter)
        test_filter_button.pack(side='right', padx=(10, 0), pady=(5, 0))
    
    def _create_control_buttons(self, parent):
        """Create control buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=(15, 0))
        
        # Enable/Disable TTS
        self.enable_var = tk.BooleanVar(value=True)
        enable_check = ttk.Checkbutton(button_frame,
                                      text="Enable Text-to-Speech",
                                      variable=self.enable_var,
                                      command=self._on_enable_change)
        enable_check.pack(side='left')
        
        # Spacer
        ttk.Frame(button_frame).pack(side='left', fill='x', expand=True)
        
        # Action buttons
        test_system_button = ttk.Button(button_frame, text="🎯 Test System",
                                       style='Modern.TButton',
                                       command=self._test_system)
        test_system_button.pack(side='right', padx=(5, 0))
        
        reset_button = ttk.Button(button_frame, text="🔄 Reset to Defaults",
                                 style='Modern.TButton',
                                 command=self._reset_defaults)
        reset_button.pack(side='right', padx=(5, 0))
    
    def _create_status_bar(self, parent):
        """Create status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill='x', pady=(15, 0), side='bottom')
        
        ttk.Separator(status_frame, orient='horizontal').pack(fill='x', pady=(0, 5))
        
        self.status_var = tk.StringVar(value="TTS System Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                foreground='#666666')
        status_label.pack(side='left')
        
        # Queue status
        self.queue_var = tk.StringVar()
        queue_label = ttk.Label(status_frame, textvariable=self.queue_var,
                               foreground='#666666')
        queue_label.pack(side='right')
        
        # Update status periodically
        self._update_status()
    
    def _load_current_settings(self):
        """Load current TTS settings into the GUI."""
        # Load voice settings
        voices = self.tts.get_available_voices()
        self.voice_combo['values'] = list(voices.keys())
        
        current_voice = self.tts.get_current_voice()
        if current_voice:
            self.voice_var.set(current_voice)
            self.current_voice_var.set(current_voice)
        
        # Load audio settings
        self.rate_var.set(self.tts.rate)
        self.volume_var.set(self.tts.volume)
        
        # Load filter settings
        self.filter_brackets_var.set(self.tts.filter_brackets)
        self.enable_var.set(self.tts.is_enabled())
        
        # Load language settings
        supported_langs = self.tts.supported_languages
        lang_names = ", ".join(supported_langs.values())
        self.lang_status_var.set(lang_names)
    
    def _on_voice_change(self, event=None):
        """Handle voice selection change."""
        selected_voice = self.voice_var.get()
        if selected_voice:
            success = self.tts.set_voice(selected_voice)
            if success:
                self.current_voice_var.set(selected_voice)
                self.status_var.set(f"Voice changed to: {selected_voice}")
                if self.on_settings_change:
                    self.on_settings_change('voice', selected_voice)
            else:
                self.status_var.set(f"Failed to change voice to: {selected_voice}")
    
    def _on_rate_change(self, value):
        """Handle speech rate change."""
        rate = int(float(value))
        self.tts.set_rate(rate)
        self.rate_label.config(text=str(rate))
        if self.on_settings_change:
            self.on_settings_change('rate', rate)
    
    def _on_volume_change(self, value):
        """Handle volume change."""
        volume = float(value)
        self.tts.set_volume(volume)
        self.volume_label.config(text=f"{int(volume * 100)}%")
        if self.on_settings_change:
            self.on_settings_change('volume', volume)
    
    def _on_filter_change(self):
        """Handle filter setting change."""
        filter_enabled = self.filter_brackets_var.get()
        self.tts.set_filter_brackets(filter_enabled)
        self.status_var.set(f"Bracket filtering {'enabled' if filter_enabled else 'disabled'}")
        if self.on_settings_change:
            self.on_settings_change('filter_brackets', filter_enabled)
    
    def _on_enable_change(self):
        """Handle TTS enable/disable."""
        enabled = self.enable_var.get()
        if enabled:
            self.tts.enable()
            self.status_var.set("TTS enabled")
        else:
            self.tts.disable()
            self.status_var.set("TTS disabled")
        
        if self.on_settings_change:
            self.on_settings_change('enabled', enabled)
    
    def _on_auto_detect_change(self):
        """Handle auto-detect language change."""
        auto_detect = self.auto_detect_var.get()
        self.status_var.set(f"Auto language detection {'enabled' if auto_detect else 'disabled'}")
        if self.on_settings_change:
            self.on_settings_change('auto_detect', auto_detect)
    
    def _test_voice(self):
        """Test the currently selected voice."""
        selected_voice = self.voice_var.get()
        if selected_voice:
            test_text = f"Testing voice: {selected_voice}"
            self.tts.speak(test_text, selected_voice)
            self.status_var.set(f"Testing voice: {selected_voice}")
        else:
            messagebox.showwarning("No Voice Selected", "Please select a voice to test.")
    
    def _test_filter(self):
        """Test text filtering with the current settings."""
        test_text = self.test_text_var.get()
        if test_text:
            self.tts.speak(test_text)
            self.status_var.set("Testing text filter...")
        else:
            messagebox.showwarning("No Text", "Please enter test text.")
    
    def _test_system(self):
        """Test the entire TTS system."""
        if not self.tts.is_enabled():
            messagebox.showinfo("TTS Disabled", "Please enable TTS first.")
            return
        
        # Test basic functionality
        self.tts.speak("Testing TTS system functionality")
        
        # Test prediction format
        self.tts.speak_prediction("Number 17", confidence=0.8)
        
        self.status_var.set("Running full system test...")
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset Settings", "Reset all TTS settings to defaults?"):
            # Reset TTS system
            self.tts.set_rate(150)
            self.tts.set_volume(0.8)
            self.tts.set_filter_brackets(True)
            self.tts.enable()
            
            # Reset GUI
            self.rate_var.set(150)
            self.volume_var.set(0.8)
            self.filter_brackets_var.set(True)
            self.enable_var.set(True)
            self.auto_detect_var.set(True)
            
            # Update labels
            self.rate_label.config(text="150")
            self.volume_label.config(text="80%")
            
            self.status_var.set("Settings reset to defaults")
            
            if self.on_settings_change:
                self.on_settings_change('reset', None)
    
    def _update_status(self):
        """Update status information periodically."""
        try:
            status = self.tts.get_status()
            queue_size = status.get('queue_size', 0)
            if queue_size > 0:
                self.queue_var.set(f"Queue: {queue_size} items")
            else:
                self.queue_var.set("")
            
            # Schedule next update
            self.root.after(1000, self._update_status)
            
        except Exception as e:
            # GUI might be destroyed
            pass
    
    def show(self):
        """Show the GUI (for standalone usage)."""
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.mainloop()
    
    def destroy(self):
        """Destroy the GUI."""
        if hasattr(self, 'root'):
            self.root.destroy()


class QuickTTSControl:
    """Lightweight TTS control widget for embedding in other interfaces."""
    
    def __init__(self, parent, on_settings_change: Optional[Callable] = None):
        self.tts = get_tts_system()
        self.on_settings_change = on_settings_change
        
        # Create compact control frame
        self.frame = ttk.LabelFrame(parent, text="🔊 TTS", padding="10")
        
        # Enable/disable toggle
        self.enabled_var = tk.BooleanVar(value=self.tts.is_enabled())
        enable_check = ttk.Checkbutton(self.frame, text="Enable",
                                      variable=self.enabled_var,
                                      command=self._toggle_tts)
        enable_check.grid(row=0, column=0, sticky='w')
        
        # Voice selection
        ttk.Label(self.frame, text="Voice:").grid(row=0, column=1, padx=(10, 5))
        
        self.voice_var = tk.StringVar()
        voice_combo = ttk.Combobox(self.frame, textvariable=self.voice_var,
                                  width=15, state='readonly')
        voice_combo.grid(row=0, column=2, padx=(0, 10))
        
        # Load voices
        voices = self.tts.get_available_voices()
        voice_combo['values'] = list(voices.keys())
        current_voice = self.tts.get_current_voice()
        if current_voice:
            self.voice_var.set(current_voice)
        
        voice_combo.bind('<<ComboboxSelected>>', self._change_voice)
        
        # Settings button
        settings_button = ttk.Button(self.frame, text="⚙️", width=3,
                                    command=self._show_settings)
        settings_button.grid(row=0, column=3)
        
        self.settings_window = None
    
    def _toggle_tts(self):
        """Toggle TTS on/off."""
        if self.enabled_var.get():
            self.tts.enable()
        else:
            self.tts.disable()
        
        if self.on_settings_change:
            self.on_settings_change('enabled', self.enabled_var.get())
    
    def _change_voice(self, event=None):
        """Change the selected voice."""
        voice = self.voice_var.get()
        if voice:
            self.tts.set_voice(voice)
            if self.on_settings_change:
                self.on_settings_change('voice', voice)
    
    def _show_settings(self):
        """Show full settings window."""
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = tk.Toplevel(self.frame)
            self.settings_window.title("TTS Settings")
            self.settings_window.geometry("500x400")
            
            TTSSettingsGUI(self.settings_window, self.on_settings_change)
    
    def pack(self, **kwargs):
        """Pack the control frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the control frame."""
        self.frame.grid(**kwargs)


if __name__ == "__main__":
    # Test the GUI
    def on_change(setting, value):
        print(f"Setting changed: {setting} = {value}")
    
    # Test standalone GUI
    print("🔊 Testing TTS Settings GUI")
    gui = TTSSettingsGUI(on_settings_change=on_change)
    gui.show()