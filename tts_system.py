#!/usr/bin/env python3
"""
Text-to-Speech system for roulette predictions with multi-voice support and language detection.
"""

import pyttsx3
import re
import threading
import queue
from typing import Optional, List, Dict, Any
from langdetect import detect
import time
import logging


class TTSSystem:
    def __init__(self):
        """Initialize the TTS system with multiple voice options."""
        self.engine = None
        self.available_voices = []
        self.current_voice_id = None
        self.voice_names = {}
        self.supported_languages = {
            'en': 'English',
            'cs': 'Czech', 
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian'
        }
        
        # TTS settings
        self.rate = 150  # Words per minute
        self.volume = 0.8  # Volume (0.0 to 1.0)
        self.enabled = True
        self.filter_brackets = True  # Filter content in square brackets
        
        # Queue for TTS requests to avoid blocking
        self.tts_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        
        self._initialize_engine()
        self._start_worker_thread()
    
    def _initialize_engine(self):
        """Initialize the TTS engine and discover available voices."""
        try:
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                self.available_voices = voices
            else:
                self.available_voices = []
            
            # Map voice names for easier selection
            for i, voice in enumerate(self.available_voices):
                voice_name = voice.name if hasattr(voice, 'name') else f"Voice {i+1}"
                voice_id = voice.id if hasattr(voice, 'id') else str(i)
                
                # Clean up voice name
                clean_name = self._clean_voice_name(voice_name)
                self.voice_names[clean_name] = voice_id
                
                logging.info(f"Available voice: {clean_name} (ID: {voice_id})")
            
            # Set default voice (try to avoid "Alex" if other options exist)
            if self.available_voices:
                self._set_default_voice()
                
                # Set initial properties
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
                
                logging.info(f"TTS System initialized with {len(self.available_voices)} voices")
            else:
                logging.warning("No voices available, TTS will be disabled")
                self.enabled = False
            
        except Exception as e:
            logging.error(f"Failed to initialize TTS engine: {e}")
            self.enabled = False
            # Create a dummy voice for fallback
            self.voice_names["System Default"] = "default"
    
    def _clean_voice_name(self, name: str) -> str:
        """Clean up voice name for display."""
        # Remove system prefixes and clean up
        name = re.sub(r'^Microsoft\s+', '', name)
        name = re.sub(r'\s+\-\s+.*$', '', name)  # Remove trailing descriptions
        name = re.sub(r'\s+\(.*\)$', '', name)  # Remove parenthetical info
        return name.strip()
    
    def _set_default_voice(self):
        """Set a default voice, preferring non-Alex voices."""
        if not self.available_voices:
            return
        
        # Try to find a voice that's not "Alex"
        preferred_voices = []
        alex_voices = []
        
        for clean_name, voice_id in self.voice_names.items():
            if 'alex' in clean_name.lower():
                alex_voices.append((clean_name, voice_id))
            else:
                preferred_voices.append((clean_name, voice_id))
        
        # Prefer non-Alex voices
        if preferred_voices:
            default_name, default_id = preferred_voices[0]
            logging.info(f"Setting default voice to: {default_name} (avoiding Alex)")
        elif alex_voices:
            default_name, default_id = alex_voices[0]
            logging.info(f"Using Alex voice as fallback: {default_name}")
        else:
            # Fallback to first available
            default_id = self.available_voices[0].id
            default_name = self.available_voices[0].name
            logging.info(f"Using first available voice: {default_name}")
        
        self.current_voice_id = default_id
        self.engine.setProperty('voice', default_id)
    
    def _start_worker_thread(self):
        """Start the background worker thread for TTS processing."""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def _worker_loop(self):
        """Background worker loop to process TTS requests."""
        while self.running:
            try:
                # Get next TTS request with timeout
                text, voice_id = self.tts_queue.get(timeout=1.0)
                
                if text and self.enabled and self.engine:
                    # Set voice if specified
                    if voice_id:
                        self.engine.setProperty('voice', voice_id)
                    
                    # Filter text if needed
                    filtered_text = self._filter_text(text)
                    
                    if filtered_text.strip():
                        self.engine.say(filtered_text)
                        self.engine.runAndWait()
                
                self.tts_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"TTS worker error: {e}")
    
    def _filter_text(self, text: str) -> str:
        """Filter text based on settings (e.g., remove content in square brackets)."""
        if not text:
            return text
        
        filtered = text
        
        # Remove content in square brackets if enabled
        if self.filter_brackets:
            filtered = re.sub(r'\[.*?\]', '', filtered)
        
        # Clean up extra whitespace
        filtered = re.sub(r'\s+', ' ', filtered).strip()
        
        return filtered
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of the given text."""
        try:
            # Filter text before detection
            filtered_text = self._filter_text(text)
            
            if len(filtered_text.strip()) < 3:
                return None
            
            detected = detect(filtered_text)
            return detected if detected in self.supported_languages else None
            
        except Exception as e:
            # Handle any langdetect exceptions
            logging.debug(f"Language detection error: {e}")
            return None
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get dictionary of available voices {name: id}."""
        return self.voice_names.copy()
    
    def get_current_voice(self) -> Optional[str]:
        """Get the name of the currently selected voice."""
        if not self.current_voice_id:
            return None
        
        for name, voice_id in self.voice_names.items():
            if voice_id == self.current_voice_id:
                return name
        
        return None
    
    def set_voice(self, voice_name: str) -> bool:
        """Set the TTS voice by name."""
        if voice_name in self.voice_names:
            voice_id = self.voice_names[voice_name]
            self.current_voice_id = voice_id
            
            if self.engine:
                self.engine.setProperty('voice', voice_id)
            
            logging.info(f"Voice changed to: {voice_name}")
            return True
        
        logging.warning(f"Voice not found: {voice_name}")
        return False
    
    def set_rate(self, rate: int):
        """Set the speech rate (words per minute)."""
        self.rate = max(50, min(300, rate))  # Clamp between 50-300 WPM
        if self.engine:
            self.engine.setProperty('rate', self.rate)
    
    def set_volume(self, volume: float):
        """Set the speech volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        if self.engine:
            self.engine.setProperty('volume', self.volume)
    
    def speak(self, text: str, voice_name: Optional[str] = None) -> bool:
        """
        Queue text for speech synthesis.
        
        Args:
            text: Text to speak
            voice_name: Optional voice name to use for this utterance
            
        Returns:
            True if queued successfully, False otherwise
        """
        if not self.enabled or not text.strip():
            # If TTS is disabled, at least log the text that would be spoken
            if text.strip():
                print(f"🔊 TTS: {text.strip()}")
            return False
        
        # Get voice ID if voice name specified
        voice_id = None
        if voice_name and voice_name in self.voice_names:
            voice_id = self.voice_names[voice_name]
        else:
            voice_id = self.current_voice_id
        
        try:
            # Add to queue for background processing
            self.tts_queue.put((text, voice_id), timeout=1.0)
            return True
            
        except queue.Full:
            logging.warning("TTS queue is full, skipping utterance")
            return False
    
    def speak_prediction(self, prediction_text: str, confidence: float = 0.0) -> bool:
        """
        Speak a roulette prediction with appropriate formatting.
        
        Args:
            prediction_text: The prediction text to announce
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            True if queued successfully
        """
        if not self.enabled:
            return False
        
        # Detect language for appropriate voice selection
        detected_lang = self.detect_language(prediction_text)
        
        # Format the announcement
        if confidence > 0.7:
            announcement = f"High confidence prediction: {prediction_text}"
        elif confidence > 0.4:
            announcement = f"Prediction: {prediction_text}"
        else:
            announcement = f"Low confidence prediction: {prediction_text}"
        
        # Choose voice based on detected language if available
        voice_to_use = None
        if detected_lang:
            # Try to find a voice that matches the detected language
            lang_voices = [name for name in self.voice_names.keys() 
                          if detected_lang in name.lower() or 
                          self.supported_languages.get(detected_lang, '').lower() in name.lower()]
            if lang_voices:
                voice_to_use = lang_voices[0]
        
        return self.speak(announcement, voice_to_use)
    
    def enable(self):
        """Enable TTS output."""
        self.enabled = True
        logging.info("TTS enabled")
    
    def disable(self):
        """Disable TTS output."""
        self.enabled = False
        logging.info("TTS disabled")
    
    def is_enabled(self) -> bool:
        """Check if TTS is enabled."""
        return self.enabled
    
    def set_filter_brackets(self, filter_enabled: bool):
        """Enable or disable filtering of content in square brackets."""
        self.filter_brackets = filter_enabled
        logging.info(f"Bracket filtering {'enabled' if filter_enabled else 'disabled'}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current TTS system status."""
        return {
            'enabled': self.enabled,
            'current_voice': self.get_current_voice(),
            'available_voices': list(self.voice_names.keys()),
            'rate': self.rate,
            'volume': self.volume,
            'filter_brackets': self.filter_brackets,
            'supported_languages': self.supported_languages,
            'queue_size': self.tts_queue.qsize()
        }
    
    def cleanup(self):
        """Clean up TTS resources."""
        self.running = False
        
        # Clear queue
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
                self.tts_queue.task_done()
            except queue.Empty:
                break
        
        # Wait for worker thread
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        
        # Stop engine
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
        
        logging.info("TTS system cleanup completed")


# Global TTS instance
_tts_instance = None

def get_tts_system() -> TTSSystem:
    """Get the global TTS system instance."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSSystem()
    return _tts_instance


def cleanup_tts():
    """Clean up the global TTS system."""
    global _tts_instance
    if _tts_instance:
        _tts_instance.cleanup()
        _tts_instance = None


if __name__ == "__main__":
    # Test the TTS system
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    print("🔊 Testing TTS System")
    print("=" * 30)
    
    tts = TTSSystem()
    
    # Show available voices
    voices = tts.get_available_voices()
    print(f"Available voices: {list(voices.keys())}")
    print(f"Current voice: {tts.get_current_voice()}")
    
    # Test basic speech
    print("\n🎯 Testing basic speech...")
    tts.speak("Testing text to speech system")
    time.sleep(2)
    
    # Test filtered speech (with brackets)
    print("\n🎯 Testing bracket filtering...")
    tts.speak("This is a test [this should be filtered out] with brackets")
    time.sleep(3)
    
    # Test prediction announcement
    print("\n🎯 Testing prediction announcement...")
    tts.speak_prediction("Number 17", confidence=0.8)
    time.sleep(3)
    
    # Test language detection
    print("\n🎯 Testing language detection...")
    lang = tts.detect_language("This is English text")
    print(f"Detected language: {lang}")
    
    lang = tts.detect_language("Tohle je český text")
    print(f"Detected language: {lang}")
    
    # Test voice switching
    if len(voices) > 1:
        print("\n🎯 Testing voice switching...")
        voice_names = list(voices.keys())
        tts.set_voice(voice_names[1])
        tts.speak(f"Now using voice: {voice_names[1]}")
        time.sleep(3)
    
    print("\n✅ TTS test completed")
    tts.cleanup()