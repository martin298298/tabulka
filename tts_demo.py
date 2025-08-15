#!/usr/bin/env python3
"""
Demo script to test TTS functionality for roulette predictions.
"""

import time
from tts_system import get_tts_system

def main():
    """Demo the TTS system with roulette-style announcements."""
    print("🎰 TTS Demo for Roulette Predictions")
    print("=" * 40)
    
    # Get TTS system
    tts = get_tts_system()
    
    # Show system status
    status = tts.get_status()
    print(f"TTS Enabled: {status['enabled']}")
    print(f"Available voices: {len(status['available_voices'])}")
    print(f"Current voice: {status['current_voice']}")
    print(f"Supported languages: {', '.join(status['supported_languages'].values())}")
    print(f"Filter brackets: {status['filter_brackets']}")
    print()
    
    if not status['enabled']:
        print("⚠️  TTS is disabled - announcements will be printed instead")
        print()
    
    # Test basic functionality
    print("🎯 Testing basic TTS...")
    tts.speak("Testing text to speech system for roulette predictions")
    time.sleep(2)
    
    # Test different confidence levels
    print("🎯 Testing prediction announcements...")
    
    # High confidence
    tts.speak_prediction("Number 17", confidence=0.85)
    time.sleep(3)
    
    # Medium confidence  
    tts.speak_prediction("Number 23", confidence=0.6)
    time.sleep(3)
    
    # Low confidence
    tts.speak_prediction("Number 5", confidence=0.3)
    time.sleep(3)
    
    # Test bracket filtering
    print("🎯 Testing bracket filtering...")
    tts.speak("This announcement [internal data should be filtered] contains brackets")
    time.sleep(3)
    
    # Test language detection
    print("🎯 Testing language detection...")
    english_text = "Number seventeen prediction"
    czech_text = "Číslo sedmnáct predikce"
    
    en_lang = tts.detect_language(english_text)
    cs_lang = tts.detect_language(czech_text)
    
    print(f"English text language: {en_lang}")
    print(f"Czech text language: {cs_lang}")
    
    tts.speak(english_text)
    time.sleep(2)
    tts.speak(czech_text)
    time.sleep(2)
    
    # Test voice switching if multiple voices available
    voices = tts.get_available_voices()
    if len(voices) > 1:
        print("🎯 Testing voice switching...")
        voice_names = list(voices.keys())[:3]  # Test up to 3 voices
        
        for voice_name in voice_names:
            print(f"   Testing voice: {voice_name}")
            tts.set_voice(voice_name)
            tts.speak(f"This is voice {voice_name}")
            time.sleep(2)
    else:
        print("⚠️  Only one voice available, skipping voice switching test")
    
    # Test settings
    print("🎯 Testing speech settings...")
    
    # Test different rates
    tts.set_rate(100)  # Slow
    tts.speak("Speaking slowly at 100 words per minute")
    time.sleep(3)
    
    tts.set_rate(200)  # Fast
    tts.speak("Speaking quickly at 200 words per minute")
    time.sleep(2)
    
    tts.set_rate(150)  # Normal
    tts.speak("Back to normal speed at 150 words per minute")
    time.sleep(2)
    
    # Test volume
    tts.set_volume(0.5)  # Quiet
    tts.speak("Speaking at 50 percent volume")
    time.sleep(2)
    
    tts.set_volume(0.8)  # Normal
    tts.speak("Back to normal volume")
    time.sleep(2)
    
    # Test enable/disable
    print("🎯 Testing enable/disable...")
    tts.disable()
    tts.speak("This should not be heard when TTS is disabled")
    time.sleep(1)
    
    tts.enable()
    tts.speak("TTS is now re-enabled")
    time.sleep(2)
    
    print("\n✅ TTS Demo completed!")
    print("Final status:")
    final_status = tts.get_status()
    for key, value in final_status.items():
        if key != 'available_voices':  # Skip long list
            print(f"   {key}: {value}")
    
    # Cleanup
    tts.cleanup()
    print("\n🧹 TTS system cleaned up")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()