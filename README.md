**Python Webcam Surveillance System**

*A production-ready Python webcam surveillance system designed for continuous monitoring with SOC 2 compliance in mind.*

---

**Features**

* Continuous webcam capture (USB/IP cameras supported via OpenCV)
* Threaded architecture for capture, processing, and storage
* Circular frame buffer to prevent frame loss
* H.264 video compression for efficient storage
* Basic motion detection with metadata logging (timestamps + motion flags)
* Hourly file rotation for manageable storage
* Graceful shutdown via signal handling
* Type-hinted, maintainable Python code
* Ready for SOC 2 compliance extensions (encryption, audit logging, cloud storage)

---

**Installation**

**Prerequisites:**

* Python 3.10+
* OpenCV (`cv2`)
* NumPy

**Install dependencies:**

```bash
pip install opencv-python numpy
```

**Optional for H.264 hardware acceleration:**

* FFmpeg installed and accessible in PATH

---

*Usage*

*Clone the repository:*

```bash
git clone https://github.com/<your-username>/python-webcam-surveillance-system.git
cd python-webcam-surveillance-system
```

*Run the system:*

```bash
python main.py
```

*Directories:*

* `recordings/` → Stores compressed video files (rotated hourly)
* `metadata/` → Stores JSON metadata for motion detection and timestamps

*Terminate gracefully:*

* `Ctrl+C` or system `SIGINT/SIGTERM`

---

*File Structure*

```
python-webcam-surveillance-system/
* main.py              # Entry point; launches capture and processing threads
* README.md            # Repository description and usage
* recordings/          # Video storage directory (auto-created)
* metadata/            # Metadata JSON files (auto-created)
* requirements.txt     # Optional: list of Python dependencies
* LICENSE              # MIT or other license
```

*Optional enhancement files:*

* `motion_ai.py` → AI-based motion detection (future upgrade)
* `config.py` → Configurable parameters (camera index, FPS, buffer size)

---

*Configuration*

*Modify constants in `main.py` (or move to `config.py`):*

```python
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 20.0
BUFFER_SIZE = 128
VIDEO_DIR = Path("recordings")
METADATA_DIR = Path("metadata")
MOTION_THRESHOLD = 0.05
```

---

*SOC 2 Compliance Notes*

* Consider encrypting `recordings/` using AES-256
* Use cryptographic hashes for video integrity
* Secure metadata storage and access controls
* Implement centralized logging and audit trails


*Optional Future Enhancements*

* AI-based motion detection (people, vehicles, pets)
* Real-time alerting via Slack/email/webhooks
* Cloud/NAS integration for storage and compliance
* Multi-camera support
* Docker container for enterprise deployment
