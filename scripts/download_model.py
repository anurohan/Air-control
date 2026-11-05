from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = Path(__file__).resolve().parents[1] / "resources" / "models" / "hand_landmarker.task"


def main() -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
        print(f"Model already present: {MODEL_PATH}")
        return
    print("Downloading the official MediaPipe hand landmarker model...")
    with urlopen(MODEL_URL, timeout=60) as response:
        MODEL_PATH.write_bytes(response.read())
    print(f"Saved {MODEL_PATH} ({MODEL_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
