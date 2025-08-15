# TTS Features Update

## New Text-to-Speech Functionality

The roulette prediction system now includes comprehensive text-to-speech (TTS) capabilities to address the issues mentioned in the problem statement:

### 🔊 Multi-Voice Support
- **Multiple Voice Options**: The system now supports multiple TTS voices, not just "Alex"
- **Voice Selection**: Users can choose from all available system voices
- **Automatic Voice Detection**: Avoids defaulting to "Alex" when other voices are available
- **Voice Switching**: Runtime voice changes supported

### 🗣️ Language Detection & Support
- **Automatic Language Detection**: Detects language of text for appropriate voice selection
- **Multi-Language Support**: Supports English, Czech, German, French, Spanish, and Italian
- **Smart Voice Matching**: Attempts to match voice to detected language when possible

### 📝 Text Filtering
- **Square Bracket Filtering**: Content in square brackets [like this] is automatically filtered out
- **Configurable Filtering**: Can be enabled/disabled as needed
- **Clean Announcements**: Only relevant prediction information is spoken

### 🎯 Prediction Announcements
- **Confidence-Based Announcements**: Different announcement styles based on prediction confidence
- **High Confidence**: "High confidence prediction: Number 17"
- **Medium Confidence**: "Prediction: Number 17"  
- **Low Confidence**: "Low confidence prediction: Number 17"

### 🎛️ Advanced Settings
- **Speech Rate Control**: Adjustable speaking speed (50-300 WPM)
- **Volume Control**: Adjustable volume (0-100%)
- **Enable/Disable Toggle**: Easy on/off control
- **Queue Management**: Background processing prevents blocking

### 🖥️ User Interface Improvements
- **Modern GUI**: Clean, styled interface for TTS settings
- **Quick Controls**: Compact control widget for embedding
- **Real-time Settings**: Changes apply immediately
- **Status Monitoring**: Shows current settings and queue status

### 🔧 Technical Features
- **Fallback Support**: When TTS is unavailable, falls back to console output
- **Background Processing**: Non-blocking TTS processing
- **Error Handling**: Graceful handling of TTS engine issues
- **Resource Management**: Proper cleanup and memory management

## Usage Examples

### Basic TTS Usage
```python
from tts_system import get_tts_system

tts = get_tts_system()
tts.speak("Hello world")
tts.speak_prediction("Number 17", confidence=0.8)
```

### Voice Selection
```python
# List available voices
voices = tts.get_available_voices()
print(voices)  # {'Voice 1': 'id1', 'Voice 2': 'id2'}

# Change voice
tts.set_voice("Voice 2")
```

### Settings Control
```python
# Adjust speech settings
tts.set_rate(180)  # Words per minute
tts.set_volume(0.7)  # 70% volume
tts.set_filter_brackets(True)  # Filter [brackets]
```

### Language Detection
```python
# Automatic language detection
lang = tts.detect_language("This is English text")
print(lang)  # 'en'

lang = tts.detect_language("Tohle je český text")  
print(lang)  # 'cs'
```

## GUI Applications

### Full Settings Interface
```python
python main_with_gui.py
```
- Complete TTS settings interface
- Integrated with roulette prediction system
- Real-time configuration changes

### Standalone TTS Demo
```python
python tts_demo.py
```
- Test all TTS features
- Voice testing and comparison
- Settings demonstration

## Integration with Roulette System

The TTS system is fully integrated with the main roulette prediction system:

1. **Automatic Announcements**: Predictions are automatically announced via TTS
2. **Smart Filtering**: System messages and debug info in brackets are filtered out
3. **Multi-Language**: Supports both English and Czech casino interfaces
4. **Fallback Operation**: Works even when TTS hardware is not available

## Files Added/Modified

### New Files
- `tts_system.py` - Core TTS functionality
- `tts_gui.py` - GUI interface for TTS settings  
- `main_with_gui.py` - Enhanced GUI application
- `tts_demo.py` - TTS testing and demonstration

### Modified Files
- `main.py` - Integrated TTS announcements
- `requirements.txt` - Added pyttsx3 and langdetect dependencies

## Requirements

```bash
pip install pyttsx3 langdetect
sudo apt-get install espeak espeak-data  # For Linux TTS support
sudo apt-get install python3-tk         # For GUI support
```

## Problem Statement Resolution

✅ **"the voocies dont change only alex is reading"**
- Fixed: Multiple voice options available, automatic non-Alex voice selection

✅ **"dont read things in square brackets"**  
- Fixed: Configurable bracket filtering removes [bracketed content]

✅ **"multichoice selection boxes are looking bad and not coresponding with the website design"**
- Fixed: Modern, styled GUI with proper comboboxes and controls

✅ **"add check lenguage there please"**
- Fixed: Automatic language detection with multi-language support