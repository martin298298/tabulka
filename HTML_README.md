# HTML Interface for Roulette Prediction System

This directory contains a complete web interface for the roulette prediction system with four main pages as requested.

## 📁 Files Overview

### HTML Pages
- **`index.html`** - Landing page with system overview and controls
- **`scrolling.html`** - Live data streaming with real-time metrics  
- **`references.html`** - Comprehensive documentation and API reference
- **`podcast.html`** - Podcast generation interface

### Assets
- **`style.css`** - Modern responsive CSS styling
- **`script.js`** - Interactive JavaScript functionality

## 🚀 Quick Start

### Option 1: Local Web Server (Recommended)
```bash
# Navigate to the tabulka directory
cd /path/to/tabulka

# Start a local web server
python3 -m http.server 8000

# Open your browser to
http://localhost:8000/index.html
```

### Option 2: Direct File Access
Simply open `index.html` in your web browser. Some features may be limited due to browser security restrictions.

## 📋 Page Details

### 🏠 Landing Page (index.html)
- **Purpose:** Main entry point and system overview
- **Features:**
  - Welcome section with key features
  - Quick start installation guide
  - Live prediction demo with controls
  - TTS settings interface
  - Performance metrics display
  - Getting started guide

### 📊 Scrolling Page (scrolling.html)  
- **Purpose:** Real-time data monitoring and visualization
- **Features:**
  - Live system status metrics
  - Real-time data stream with auto-scroll
  - Interactive wheel visualization with ball tracking
  - Recent predictions history
  - Performance analytics dashboard
  - Stream information and quality metrics
  - Debug information panel

### 📚 References Page (references.html)
- **Purpose:** Complete documentation and technical reference
- **Features:**
  - Comprehensive table of contents
  - Installation and setup guide
  - Complete API reference (Prediction, TTS, Computer Vision)
  - Academic research papers and citations
  - Technical specifications and architecture
  - Compatibility matrix for OS/browsers/Python versions
  - Troubleshooting guide
  - Contributing guidelines

### 🎙️ Podcast Page (podcast.html)
- **Purpose:** Professional podcast generation from prediction data
- **Features:**
  - Podcast studio interface with audio visualization
  - Multiple podcast format options (Summary, Analysis, Tutorial, News)
  - Advanced audio settings (quality, speed, background music)
  - Generation progress tracking
  - Audio preview player
  - Sharing and distribution options
  - Analytics dashboard

## ✨ Key Features

### 🎨 Modern Design
- **Responsive:** Works on desktop, tablet, and mobile
- **Clean UI:** Professional interface with smooth animations
- **Consistent Theming:** Unified color scheme and typography
- **Interactive Elements:** Buttons, sliders, dropdowns with hover effects

### 🔊 TTS Integration
- **Voice Selection:** Choose from available system voices
- **Real-time Controls:** Volume and speed adjustment
- **Smart Filtering:** Automatic removal of debug content in brackets
- **Prediction Announcements:** Confidence-based voice announcements

### 📊 Live Data Simulation
- **Real-time Updates:** Simulated live streaming data
- **Interactive Charts:** Wheel visualization with ball tracking
- **Performance Metrics:** FPS, accuracy, resource usage
- **Export Functionality:** Save prediction history

### 🎙️ Podcast Generation
- **Multiple Formats:** Choose from 4 different podcast styles
- **Professional Audio:** High-quality synthesis with background music
- **Progress Tracking:** Visual progress indicator during generation
- **Distribution Ready:** Export in multiple formats (MP3, M4A, FLAC, WAV)

## 🔧 Technical Details

### Browser Compatibility
- **Chrome/Chromium:** ✅ Fully supported
- **Firefox:** ✅ Fully supported
- **Safari:** ✅ Supported
- **Edge:** ✅ Supported

### JavaScript Features
- **Web Speech API:** Text-to-speech functionality
- **Local Storage:** Settings persistence
- **Responsive Design:** Mobile-friendly interface
- **Interactive Elements:** Real-time updates and animations

### CSS Features
- **CSS Grid/Flexbox:** Modern layout system
- **CSS Variables:** Consistent theming
- **Animations:** Smooth transitions and effects
- **Media Queries:** Responsive design

## 🎯 Integration with Python Backend

While these HTML files provide a complete frontend interface, they are designed to work alongside the existing Python backend:

- **Main Application:** `python main_with_gui.py`
- **TTS System:** Integration with `tts_system.py`
- **Computer Vision:** Connects to `vision.py` processing
- **Stream Capture:** Works with `stream_capture.py`

## 📱 Mobile Support

All pages are fully responsive and optimized for:
- **Smartphones:** iOS and Android browsers
- **Tablets:** iPad and Android tablets  
- **Touch Interfaces:** Touch-friendly controls and navigation

## ⚠️ Important Notes

1. **Educational Purpose:** This interface is for educational and research purposes only
2. **Local Development:** Best used with a local web server for full functionality
3. **Browser Features:** Some features require modern browser support
4. **Simulated Data:** Live data is simulated for demonstration purposes

## 🔗 Related Files

- **Python Backend:** `main_with_gui.py`, `tts_system.py`, `vision.py`
- **Documentation:** `ENHANCED_README.md`, `TTS_FEATURES.md`, `USAGE_INSTRUCTIONS.md`
- **Testing:** `enhanced_test.py`, `test_complete_solution.py`