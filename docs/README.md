# Larynx - Real-Time Speech Transcription

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-success.svg)]()

# Prototype Description

Larynx is an Automated Speech Recognition tool designed for real-time dictation. You can speak and it will write it down for you which you can copy and paste somewhere else if wanted to.

Main Benefits are:-
1. Offline Desktop App
2. Real-time speech transcription
3. Made with python only and no other module
4. Easy to debug because of python
5. Model used uses has lesser hardware requirements

Larnyx is very suitable for:-
Doctors, psychiatrists, and other healthcare providers.
Writers & Authors
Legal professionals like lawyers & legal assistants
Individuals with Disabilities or Learning Differences

# Key Features

Real-time transcription
Offline operation
Copy-paste ready text
Modern GUI
Thread-safe architecture
Low latency (<1.5s)
Cross-platform

# Quick Start

Activate Venv:
source venv/bin/activate

Install the required requirements with:
pip install -r requirements.txt

install vosk model with:
pip install vosk

Run main.py or the main application:
./venv/bin/python main.py

Then wait for the model to load and wait until the GUI pops up and then you are good to go.

# Requirements

- Python 3.8 or higher
- Linux/Windows/macOS
- Microphone (built-in or external)
- 2GB+ RAM (for model loading)
- 4GB+ free disk space

## Dependencies
```
vosk==0.3.45
pyaudio==0.2.14
numpy==1.26.4
```

# Installation

## 1. Clone the Repository
```bash
git clone <repository-url>
cd larynx
```

## 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 4. Download Vosk Model
```bash
python setup.py
```
This downloads the vosk-model-en-us-0.22 (1.8GB) to the `models/` directory.

## 5. Install PyAudio Dependencies (Linux)
```bash
sudo apt-get install portaudio19-dev
```

## 6. Test Setup
```bash
# Test microphone
python -m src.test_mic

# Test integration
python test_integration.py
```

# Usage

## Running the Application
```bash
./venv/bin/python main.py
```

## GUI Controls
- **▶ Start**: Begin recording and transcription
- **⏹ Stop**: End recording and finalize text
- **🗑 Clear**: Clear all transcribed text
- **📋 Copy**: Copy text to clipboard

## Tips for Best Results
- Speak clearly and at normal pace
- Position microphone 6-12 inches from mouth
- Minimize background noise
- Pause briefly between sentences for better finalization
- Use in quiet environments for optimal accuracy

## Status Indicators
- **🔴 Recording**: Active transcription
- **🔵 Idle**: Ready to start
- **Word Count**: Shows transcribed words

# Architecture

## Module Overview
```
larynx/
├── src/
│   ├── audio_capture.py    # Microphone streaming with PyAudio
│   ├── vosk_engine.py      # Vosk ASR wrapper
│   ├── text_buffer.py      # Text accumulation & formatting
│   └── gui.py             # Tkinter user interface
├── models/
│   └── vosk-model-en-us-0.22/  # Pre-trained ASR model
├── main.py                 # Application entry point
└── setup.py               # Model download utility
```

## Threading Model
```
[GUI Thread - Tkinter Main Loop]
    ↓
[LarynxApp - Control Logic]
    ↓
├── [Audio Thread] → Audio Queue → [ASR Thread] → Text Queue → [GUI Update Thread]
│   (Continuous capture)     (Chunks)     (Vosk processing)    (Updates)     (Display)
└── [Text Buffer] (Accumulation & Formatting)
```

## Data Flow
1. **Audio Input**: Microphone → PyAudio → Audio chunks (16kHz, 16-bit PCM)
2. **Speech Recognition**: Audio chunks → Vosk → Partial/Final text results
3. **Text Processing**: Raw text → Formatting → Thread-safe buffer
4. **Display**: Formatted text → GUI updates → User interface

# Development

## Project Structure
```
larynx/
├── src/                    # Source modules
├── models/                 # ML models
├── docs/                   # Documentation
├── venv/                   # Virtual environment (gitignored)
├── main.py                 # Main application
├── setup.py               # Setup utilities
├── requirements.txt        # Python dependencies
├── test_*.py              # Test scripts
└── .gitignore             # Git ignore rules
```

## Running Tests
```bash
# Test individual modules
python -m src.audio_capture
python -m src.vosk_engine
python -m src.text_buffer

# Test integration
python test_integration.py

# Test microphone
python -m src.test_mic
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Code Style
- Follow PEP 8 Python style guide
- Use type hints for function parameters
- Add docstrings to all public functions
- Keep functions focused and modular

# Troubleshooting

## Common Issues

### "PortAudio not found" on Linux
```bash
sudo apt-get install portaudio19-dev
pip uninstall pyaudio
pip install pyaudio
```

### Model download fails
- Check internet connection
- Ensure 2GB+ free space in models/
- Run `python setup.py` again

### No microphone detected
- Check system audio settings
- Try different audio device
- Test with `python -m src.test_mic`

### Poor transcription quality
- Speak clearly and closer to microphone
- Reduce background noise
- Test in quiet environment
- Try different microphone

### GUI doesn't start
- Ensure display server is running (X11/Wayland)
- Check Python Tkinter installation
- Try running with `python -c "import tkinter; tkinter.Tk()"` first

# Performance

## System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 2-3GB (model + processing)
- **Storage**: 4GB (model + application)
- **OS**: Linux, Windows 10+, macOS 10.14+

## Expected Performance
- **Latency**: 0.5-1.5 seconds
- **CPU Usage**: 20-30% (one core)
- **Accuracy**: 85-90% (clear speech)
- **Memory**: ~2.5GB peak usage

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Acknowledgments

- **Vosk**: Open-source speech recognition toolkit
- **PyAudio**: Cross-platform audio library
- **NumPy**: Scientific computing library
- **Tkinter**: Python's standard GUI library

## Special Thanks
- Vosk development team for the excellent ASR engine
- Open-source community for audio processing libraries
- Python community for the amazing ecosystem

---

*Built with ❤️ using Python and open-source tools*

