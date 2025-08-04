# Auto-Click Video Play Button Feature

## Problem Solved

The casino stream at `https://www.tokyo.cz/game/tomhornlive_56` requires users to manually click a "přehrát bez zvuku" (play without sound) button before the roulette wheel becomes visible in the video stream. This manual step interrupted the automation flow.

## Solution

Added automatic detection and clicking of video play buttons in the `StreamCapture` class.

## Implementation Details

### New Method: `click_video_play_buttons()`

This async method:
1. Scans the page for video control buttons
2. Identifies play/mute buttons using comprehensive selectors
3. Clicks all relevant buttons to start video playback
4. Handles errors gracefully if no buttons are found

### Button Detection Strategy

The method searches for buttons using these selectors:

#### Standard Video Controls
- `button[aria-label*="play"]` - Buttons with "play" in aria-label
- `button[title*="play"]` - Buttons with "play" in title
- `.play-button`, `.video-play-button` - CSS class-based selectors

#### Mute/Unmute Buttons (for autoplay policies)
- `button[aria-label*="mute"]` - Mute/unmute buttons
- `.mute-button`, `.sound-button` - Sound control buttons

#### Czech Language Support
- `button:has-text("Přehrát bez zvuku")` - "Play without sound"
- `button:has-text("přehrát")` - "play" (lowercase)
- `button:has-text("spustit")` - "start"
- `button[aria-label*="zvuk"]` - Sound-related buttons

#### HTML5 Video Controls
- `video + div button` - Buttons next to video elements
- `.video-container button` - Buttons in video containers

#### Casino-Specific Selectors
- `.game-controls button` - Game control buttons
- `.casino-controls button` - Casino interface buttons
- `.live-controls button` - Live stream controls

### Integration

The method is automatically called during initialization:

```python
async def initialize(self):
    # ... existing code ...
    
    # If credentials are provided, attempt to login
    if self.email and self.password:
        await self.login()
    
    # NEW: Try to click video play buttons to start the stream
    await self.click_video_play_buttons()
    
    await asyncio.sleep(3)  # Additional wait for stream to start
```

## Usage

No changes needed to existing code. The feature is automatically enabled:

```python
# This will now automatically click play buttons
system = RoulettePredictionSystem(url, headless=False, email=email, password=password)
await system.initialize()
```

## Benefits

✅ **Automatic Operation**: No manual intervention required  
✅ **Czech Language Support**: Handles Czech casino interfaces  
✅ **Autoplay Policy Compliance**: Works with browser restrictions  
✅ **Multiple Fallbacks**: Comprehensive button detection  
✅ **Backwards Compatible**: Works if buttons aren't found  
✅ **Error Handling**: Graceful degradation on failures  

## Testing

Run the enhanced system with:

```bash
python main.py
```

The system will automatically:
1. Navigate to the casino
2. Login with credentials
3. Detect and click video play buttons
4. Start analyzing the roulette wheel

No manual "přehrát bez zvuku" clicking required!