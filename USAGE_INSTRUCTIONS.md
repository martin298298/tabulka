# Usage Instructions for Enhanced TTS Features

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
sudo apt-get install espeak espeak-data python3-tk  # For Linux
```

### 2. Test TTS System
```bash
python tts_demo.py
```

### 3. Test Complete Solution
```bash
python test_complete_solution.py
```

### 4. Run with GUI Interface
```bash
python main_with_gui.py
```

### 5. Run Enhanced Prediction System (Command Line)
```bash
python main.py
```

## Problem Statement Solutions

### ✅ "the voocies dont change only alex is reading"
**Solution**: Multi-voice TTS system with automatic Alex avoidance
- System automatically selects non-Alex voices when available
- User can choose from all available system voices
- Runtime voice switching supported
- Fallback to print output when TTS unavailable

### ✅ "dont read things in square brackets"
**Solution**: Configurable text filtering
- Content in [square brackets] automatically filtered from TTS
- Configurable enable/disable option
- Preserves important prediction information while removing debug data

### ✅ "multichoice selection boxes are looking bad and not coresponding with the website design"
**Solution**: Modern styled GUI components
- Clean, modern interface using ttk themes
- Styled comboboxes with proper appearance
- Responsive layout that adapts to content
- Professional color scheme and typography

### ✅ "add check lenguage there please"
**Solution**: Automatic language detection and multi-language support
- Detects language of text automatically
- Supports: English, Czech, German, French, Spanish, Italian
- Attempts to match voice to detected language
- Manual language override available

## Key Features

### Multi-Voice Support
```python
from tts_system import get_tts_system

tts = get_tts_system()
voices = tts.get_available_voices()
print(f"Available: {list(voices.keys())}")

# Change voice
tts.set_voice("Voice Name")
```

### Bracket Filtering
```python
# Enable filtering (default)
tts.set_filter_brackets(True)
tts.speak("Important info [debug data filtered] here")
# Only speaks: "Important info here"
```

### Language Detection
```python
# Automatic detection
lang = tts.detect_language("Hello world")  # Returns 'en'
lang = tts.detect_language("Ahoj světe")   # Returns 'cs'

# Language-aware predictions
tts.speak_prediction("Number 17", confidence=0.8)
```

### GUI Controls
```python
from tts_gui import TTSSettingsGUI, QuickTTSControl

# Full settings interface
gui = TTSSettingsGUI()
gui.show()

# Quick control widget
control = QuickTTSControl(parent_frame)
control.pack()
```

## Integration with Roulette System

The TTS system is fully integrated:

1. **Automatic Announcements**: Predictions are automatically announced
2. **Confidence Levels**: Different announcement styles based on confidence
3. **Error Handling**: Graceful fallback when TTS unavailable
4. **Background Processing**: Non-blocking operation

### Example Integration
```python
# In main.py, predictions now include TTS
if confidence > 0.4:
    prediction_text = f"Number {predicted_number}"
    print(f"🎯 PREDICTION: {prediction_text}")
    
    # Announce via TTS with confidence-based formatting
    self.tts.speak_prediction(prediction_text, confidence)
```

## Files Overview

### Core TTS System
- `tts_system.py` - Main TTS engine with multi-voice support
- `tts_gui.py` - GUI interface for settings and controls
- `tts_demo.py` - Demo and testing script

### Enhanced Applications
- `main_with_gui.py` - Full GUI application with TTS
- `main.py` - Enhanced command-line version with TTS
- `test_complete_solution.py` - Comprehensive test suite

### Documentation
- `TTS_FEATURES.md` - Detailed feature documentation
- `USAGE_INSTRUCTIONS.md` - This file

## Troubleshooting

### TTS Not Working
- Install espeak: `sudo apt-get install espeak espeak-data`
- Check audio system: Test with `espeak "hello"`
- System will fallback to print output if TTS unavailable

### GUI Not Displaying
- Install tkinter: `sudo apt-get install python3-tk`
- For headless systems, use command-line version
- All functionality available via code even without GUI

### Voice Issues
- Check available voices: `python -c "from tts_system import get_tts_system; print(get_tts_system().get_available_voices())"`
- Different systems have different voices available
- System automatically adapts to available voices

## Architecture

The solution uses a modular architecture:

```
TTS System
├── Core Engine (pyttsx3)
├── Voice Management
├── Language Detection
├── Text Filtering
├── Background Processing
└── GUI Interface

Integration Points
├── Main Prediction System
├── Configuration Management
├── Error Handling
└── Resource Cleanup
```

This provides a complete solution to all issues mentioned in the problem statement while maintaining compatibility and providing graceful fallbacks.