# Home Security System with Facial Recognition

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A smart home security system featuring real-time person detection, facial recognition, and movement tracking.

## Features

- 🕵️ Real-time person detection using HOG
- 👤 Facial recognition for known individuals
- 📍 Movement tracking and zone monitoring
- 📊 SQLite database logging
- 📅 Entry/exit timestamp recording
- 🚨 Unknown person alerts (TODO)

## Installation

### Prerequisites
- Python 3.8+
- Linux/Windows/MacOS
- Webcam/IP camera

### System Dependencies (Linux)
```bash
sudo apt-get install -y python3-dev build-essential cmake libopenblas-dev liblapack-dev libx11-dev
```

### Project Setup
1. Clone repository:
```bash
git clone https://github.com/elonmasai7/home_security.git
cd home_security
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

### Required Packages (requirements.txt)
```
opencv-python-headless>=4.5
imutils>=0.5.4
numpy>=1.21.0
face-recognition>=1.3.0
python-dotenv>=0.19.0
```

## Configuration

1. Register known faces:
```bash
mkdir known_faces
# Add JPEG images of authorized persons (e.g. known_faces/john_doe.jpg)
```

2. Generate face encodings:
```bash
python register_faces.py
```

3. Configure environment variables (create `.env` file):
```ini
CAMERA_SOURCE=0  # 0 for webcam, RTSP URL for IP cameras
ALERT_THRESHOLD=0.6  # Face recognition confidence threshold
```

## Usage

Start the security system:
```bash
python app.py
```

Command-line options:
```bash
python app.py \
  --source 0 \              # Video source
  --threshold 0.6 \         # Recognition confidence
  --verbose \               # Show debug info
  --headless                # Run without GUI
```

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    entry_time DATETIME,
    exit_time DATETIME
);

CREATE TABLE movements (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    timestamp DATETIME,
    area TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

## Troubleshooting

**Common Issues:**
- "Module not found": Activate virtual environment
- Camera not detected: Check video source in configuration
- Low recognition accuracy: Add better reference images
- Performance issues: Use `--headless` mode

## License

MIT License - See [LICENSE](LICENSE) file

## Acknowledgments

- OpenCV for computer vision components
- face-recognition library by Adam Geitgey
- HOG person detection model

---

**Important Note:** This system must comply with local privacy laws. Always inform visitors about surveillance.
```

This README includes:
1. Badges for quick project overview
2. Clear installation instructions
3. Configuration guidelines
4. Usage examples
5. Database documentation
6. Troubleshooting section
7. License and acknowledgments

You can customize the sections about alerts/TODO features based on your actual implementation status. Would you like me to create any specific additional documentation?
