// JavaScript functionality for Roulette Prediction System Web Interface

class RoulettePredictionApp {
    constructor() {
        this.isRunning = false;
        this.currentPrediction = null;
        this.ttsEnabled = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeTTS();
        this.updateNavigationState();
    }

    setupEventListeners() {
        // Navigation
        document.addEventListener('DOMContentLoaded', () => {
            this.highlightCurrentPage();
        });

        // Prediction system controls
        const startBtn = document.getElementById('start-prediction');
        const stopBtn = document.getElementById('stop-prediction');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startPrediction());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopPrediction());
        }

        // TTS controls
        const ttsToggle = document.getElementById('tts-toggle');
        const voiceSelect = document.getElementById('voice-select');
        const volumeSlider = document.getElementById('volume-slider');
        const rateSlider = document.getElementById('rate-slider');

        if (ttsToggle) {
            ttsToggle.addEventListener('change', (e) => this.toggleTTS(e.target.checked));
        }

        if (voiceSelect) {
            voiceSelect.addEventListener('change', (e) => this.changeVoice(e.target.value));
        }

        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
        }

        if (rateSlider) {
            rateSlider.addEventListener('input', (e) => this.setRate(e.target.value));
        }

        // Podcast generation
        const generateBtn = document.getElementById('generate-podcast');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generatePodcast());
        }
    }

    highlightCurrentPage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('nav a');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath || 
                (currentPath === '/' && link.getAttribute('href') === 'index.html')) {
                link.classList.add('active');
            }
        });
    }

    updateNavigationState() {
        const currentPage = this.getCurrentPageName();
        const pageTitle = document.querySelector('header h1');
        
        if (pageTitle) {
            const pageTitles = {
                'index': '🎰 Roulette Prediction System',
                'scrolling': '📊 Live Data Stream',
                'references': '📚 References & Documentation',
                'podcast': '🎙️ Podcast Generation'
            };
            
            if (pageTitles[currentPage]) {
                pageTitle.textContent = pageTitles[currentPage];
            }
        }
    }

    getCurrentPageName() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        return filename.replace('.html', '');
    }

    // Prediction System Methods
    startPrediction() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.updatePredictionStatus('Starting prediction system...', 'warning');
        
        // Simulate prediction system startup
        setTimeout(() => {
            this.updatePredictionStatus('Prediction system running', 'success');
            this.simulatePredictions();
        }, 2000);

        // Update button states
        const startBtn = document.getElementById('start-prediction');
        const stopBtn = document.getElementById('stop-prediction');
        
        if (startBtn) startBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = false;
    }

    stopPrediction() {
        if (!this.isRunning) return;
        
        this.isRunning = false;
        this.updatePredictionStatus('Prediction system stopped', 'info');
        
        // Update button states
        const startBtn = document.getElementById('start-prediction');
        const stopBtn = document.getElementById('stop-prediction');
        
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
    }

    simulatePredictions() {
        if (!this.isRunning) return;
        
        const numbers = Array.from({length: 37}, (_, i) => i); // 0-36
        const randomNumber = numbers[Math.floor(Math.random() * numbers.length)];
        const confidence = Math.random() * 0.4 + 0.6; // 0.6-1.0
        
        this.currentPrediction = {
            number: randomNumber,
            confidence: confidence,
            timestamp: new Date()
        };
        
        this.displayPrediction(this.currentPrediction);
        this.speakPrediction(this.currentPrediction);
        
        // Schedule next prediction
        setTimeout(() => this.simulatePredictions(), 3000 + Math.random() * 2000);
    }

    displayPrediction(prediction) {
        const predictionDisplay = document.getElementById('current-prediction');
        if (!predictionDisplay) return;
        
        const color = this.getNumberColor(prediction.number);
        const confidencePercent = Math.round(prediction.confidence * 100);
        
        predictionDisplay.innerHTML = `
            <div class="prediction-result">
                <div class="predicted-number roulette-number ${color}">
                    ${prediction.number}
                </div>
                <div class="confidence-info">
                    <div class="confidence-text">Confidence: ${confidencePercent}%</div>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${confidencePercent}%"></div>
                    </div>
                </div>
                <div class="timestamp">${prediction.timestamp.toLocaleTimeString()}</div>
            </div>
        `;
    }

    getNumberColor(number) {
        if (number === 0) return 'green';
        const redNumbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];
        return redNumbers.includes(number) ? 'red' : 'black';
    }

    updatePredictionStatus(message, type) {
        const statusElement = document.getElementById('prediction-status');
        if (!statusElement) return;
        
        statusElement.className = `status status-${type}`;
        statusElement.textContent = message;
    }

    // TTS Methods
    initializeTTS() {
        if ('speechSynthesis' in window) {
            this.ttsEnabled = true;
            this.loadVoices();
        } else {
            console.warn('Text-to-Speech not supported in this browser');
        }
    }

    loadVoices() {
        const voiceSelect = document.getElementById('voice-select');
        if (!voiceSelect) return;
        
        const voices = speechSynthesis.getVoices();
        voiceSelect.innerHTML = '';
        
        voices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${voice.name} (${voice.lang})`;
            voiceSelect.appendChild(option);
        });
    }

    toggleTTS(enabled) {
        this.ttsEnabled = enabled;
        const ttsControls = document.querySelectorAll('.tts-control');
        ttsControls.forEach(control => {
            control.disabled = !enabled;
        });
    }

    changeVoice(voiceIndex) {
        this.selectedVoiceIndex = parseInt(voiceIndex);
    }

    setVolume(volume) {
        this.volume = parseFloat(volume);
        const volumeDisplay = document.getElementById('volume-display');
        if (volumeDisplay) {
            volumeDisplay.textContent = Math.round(volume * 100) + '%';
        }
    }

    setRate(rate) {
        this.rate = parseFloat(rate);
        const rateDisplay = document.getElementById('rate-display');
        if (rateDisplay) {
            rateDisplay.textContent = rate + 'x';
        }
    }

    speakPrediction(prediction) {
        if (!this.ttsEnabled || !('speechSynthesis' in window)) return;
        
        const confidence = Math.round(prediction.confidence * 100);
        let message;
        
        if (confidence >= 80) {
            message = `High confidence prediction: Number ${prediction.number}`;
        } else if (confidence >= 60) {
            message = `Prediction: Number ${prediction.number}`;
        } else {
            message = `Low confidence prediction: Number ${prediction.number}`;
        }
        
        this.speak(message);
    }

    speak(text) {
        if (!this.ttsEnabled || !('speechSynthesis' in window)) return;
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        if (this.selectedVoiceIndex !== undefined) {
            const voices = speechSynthesis.getVoices();
            utterance.voice = voices[this.selectedVoiceIndex];
        }
        
        if (this.volume !== undefined) {
            utterance.volume = this.volume;
        }
        
        if (this.rate !== undefined) {
            utterance.rate = this.rate;
        }
        
        speechSynthesis.speak(utterance);
    }

    // Podcast Generation Methods
    generatePodcast() {
        const generateBtn = document.getElementById('generate-podcast');
        const progressBar = document.querySelector('.podcast-progress .progress-bar');
        const statusDiv = document.getElementById('podcast-status');
        
        if (generateBtn) generateBtn.disabled = true;
        
        this.updatePodcastStatus('Initializing podcast generation...', 'info');
        
        // Simulate podcast generation process
        const steps = [
            { progress: 20, message: 'Collecting prediction data...' },
            { progress: 40, message: 'Processing audio synthesis...' },
            { progress: 60, message: 'Generating commentary...' },
            { progress: 80, message: 'Finalizing audio file...' },
            { progress: 100, message: 'Podcast generated successfully!' }
        ];
        
        let currentStep = 0;
        const processStep = () => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                if (progressBar) {
                    progressBar.style.width = step.progress + '%';
                }
                this.updatePodcastStatus(step.message, currentStep < steps.length - 1 ? 'warning' : 'success');
                currentStep++;
                setTimeout(processStep, 1500);
            } else {
                if (generateBtn) generateBtn.disabled = false;
                this.showDownloadLink();
            }
        };
        
        setTimeout(processStep, 500);
    }

    updatePodcastStatus(message, type) {
        const statusElement = document.getElementById('podcast-status');
        if (!statusElement) return;
        
        statusElement.className = `status status-${type}`;
        statusElement.textContent = message;
    }

    showDownloadLink() {
        const downloadArea = document.getElementById('download-area');
        if (!downloadArea) return;
        
        downloadArea.innerHTML = `
            <div class="card">
                <h3>🎉 Podcast Generated Successfully!</h3>
                <p>Your roulette prediction podcast is ready for download.</p>
                <div style="margin-top: 1rem;">
                    <a href="#" class="btn btn-primary" onclick="app.downloadPodcast()">
                        📥 Download Podcast (MP3)
                    </a>
                    <a href="#" class="btn btn-success" onclick="app.playPodcast()">
                        ▶️ Play Preview
                    </a>
                </div>
            </div>
        `;
    }

    downloadPodcast() {
        // Simulate download
        this.speak('Podcast download started. Check your downloads folder.');
        alert('Podcast download would start here. This is a demo implementation.');
    }

    playPodcast() {
        // Simulate playing
        this.speak('Playing podcast preview. This is a sample of your generated roulette prediction podcast.');
    }

    // Scrolling Page Methods
    initializeScrolling() {
        if (this.getCurrentPageName() !== 'scrolling') return;
        
        this.startDataStream();
    }

    startDataStream() {
        const dataContainer = document.getElementById('live-data');
        if (!dataContainer) return;
        
        setInterval(() => {
            this.addDataPoint();
        }, 1000);
    }

    addDataPoint() {
        const dataContainer = document.getElementById('live-data');
        if (!dataContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const fps = (15 + Math.random() * 5).toFixed(1);
        const wheelDetection = (Math.random() * 0.4 + 0.6).toFixed(2);
        const ballPosition = Math.floor(Math.random() * 360);
        
        const dataPoint = document.createElement('div');
        dataPoint.className = 'data-point';
        dataPoint.innerHTML = `
            <span class="timestamp">${timestamp}</span>
            <span class="fps">FPS: ${fps}</span>
            <span class="detection">Wheel: ${wheelDetection}</span>
            <span class="position">Ball: ${ballPosition}°</span>
        `;
        
        dataContainer.insertBefore(dataPoint, dataContainer.firstChild);
        
        // Keep only last 20 entries
        while (dataContainer.children.length > 20) {
            dataContainer.removeChild(dataContainer.lastChild);
        }
    }
}

// Initialize the application
const app = new RoulettePredictionApp();

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize page-specific functionality
    app.initializeScrolling();
    
    // Load voices when available (for TTS)
    if ('speechSynthesis' in window) {
        speechSynthesis.onvoiceschanged = () => {
            app.loadVoices();
        };
    }
});

// Utility functions
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `status status-${type}`;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '1000';
    toast.style.maxWidth = '300px';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        document.body.removeChild(toast);
    }, 3000);
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatTime(date) {
    return new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }).format(date);
}