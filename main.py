import cv2
import numpy as np
from threading import Thread, Event
from queue import Queue, Empty
from datetime import datetime
import json
import signal
import sys
from pathlib import Path
from typing import Optional, Tuple

# -----------------------------
# Configuration
# -----------------------------
CAMERA_INDEX: int = 0
FRAME_WIDTH: int = 640
FRAME_HEIGHT: int = 480
FPS: float = 20.0
BUFFER_SIZE: int = 128
VIDEO_DIR: Path = Path("recordings")
METADATA_DIR: Path = Path("metadata")
MOTION_THRESHOLD: float = 0.05  # 5% of pixels changed triggers motion

# Ensure directories exist
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Frame Buffer
# -----------------------------
frame_buffer: Queue = Queue(maxsize=BUFFER_SIZE)
shutdown_event: Event = Event()

# -----------------------------
# Signal Handling
# -----------------------------
def handle_signal(sig: int, frame: Optional[object]) -> None:
    print(f"Received signal {sig}, shutting down...")
    shutdown_event.set()

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# -----------------------------
# Capture Thread
# -----------------------------
def capture_frames() -> None:
    cap: cv2.VideoCapture = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    if not cap.isOpened():
        print("ERROR: Unable to open webcam.")
        shutdown_event.set()
        return

    while not shutdown_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("WARNING: Frame capture failed.")
            continue

        if frame_buffer.full():
            try:
                frame_buffer.get_nowait()  # discard oldest
            except Empty:
                pass
        frame_buffer.put(frame)

    cap.release()
    print("Capture thread terminated.")

# -----------------------------
# Motion Detection
# -----------------------------
previous_gray: Optional[np.ndarray] = None

def detect_motion(frame: np.ndarray) -> bool:
    global previous_gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if previous_gray is None:
        previous_gray = gray
        return False

    frame_delta: np.ndarray = cv2.absdiff(previous_gray, gray)
    thresh: np.ndarray = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    motion_area: int = cv2.countNonZero(thresh)
    motion_detected: bool = motion_area > (FRAME_WIDTH * FRAME_HEIGHT * MOTION_THRESHOLD)
    previous_gray = gray
    return motion_detected

# -----------------------------
# Video Writer Thread
# -----------------------------
def process_frames() -> None:
    current_time: datetime = datetime.utcnow()
    video_path: Path = VIDEO_DIR / f"{current_time.strftime('%Y%m%d_%H%M%S')}.mp4"
    metadata_path: Path = METADATA_DIR / f"{current_time.strftime('%Y%m%d_%H%M%S')}.json"

    fourcc: int = cv2.VideoWriter_fourcc(*'X264')
    out: cv2.VideoWriter = cv2.VideoWriter(str(video_path), fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

    metadata_list: list = []

    while not shutdown_event.is_set():
        if frame_buffer.empty():
            continue

        frame: np.ndarray = frame_buffer.get()
        timestamp: str = datetime.utcnow().isoformat()
        motion_detected: bool = detect_motion(frame)

        # Write frame to video
        out.write(frame)

        # Append metadata
        metadata_list.append({
            "timestamp": timestamp,
            "motion_detected": motion_detected
        })

        # Optional: rotate file every hour
        if (datetime.utcnow() - current_time).seconds >= 3600:
            # Save current metadata
            with open(metadata_path, 'w') as f:
                json.dump(metadata_list, f, indent=2)

            # Start new file
            current_time = datetime.utcnow()
            video_path = VIDEO_DIR / f"{current_time.strftime('%Y%m%d_%H%M%S')}.mp4"
            metadata_path = METADATA_DIR / f"{current_time.strftime('%Y%m%d_%H%M%S')}.json"
            out.release()
            out = cv2.VideoWriter(str(video_path), fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
            metadata_list = []

    # Save remaining metadata and release
    with open(metadata_path, 'w') as f:
        json.dump(metadata_list, f, indent=2)
    out.release()
    print("Processing thread terminated.")

# -----------------------------
# Main
# -----------------------------
def main() -> None:
    print("Starting webcam surveillance system...")

    capture_thread = Thread(target=capture_frames, daemon=True)
    process_thread = Thread(target=process_frames, daemon=True)

    capture_thread.start()
    process_thread.start()

    while not shutdown_event.is_set():
        try:
            shutdown_event.wait(timeout=1.0)
        except KeyboardInterrupt:
            shutdown_event.set()

    capture_thread.join()
    process_thread.join()
    print("System shutdown complete.")

if __name__ == "__main__":
    main()
