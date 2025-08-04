# Roulette Prediction System

Real-time roulette prediction system that analyzes live casino streams to predict ball landing positions using computer vision and physics simulation.

## Features

- Live stream capture from online casinos
- Real-time ball and wheel detection using OpenCV
- Physics-based trajectory prediction
- Browser automation with Playwright
- Optimized for speed and accuracy

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
python main.py
```

## Components

- `stream_capture.py` - Browser automation and stream capture
- `vision.py` - Computer vision for object detection
- `physics.py` - Physics simulation and prediction
- `main.py` - Main application interface

## Target Stream

Designed to work with: https://www.tokyo.cz/game/tomhornlive_56

## Disclaimer

This software is for educational and research purposes only. Use of prediction systems in actual gambling may be illegal in many jurisdictions.