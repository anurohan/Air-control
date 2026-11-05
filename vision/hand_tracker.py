from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Any


@dataclass(frozen=True)
class Landmark:
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0


@dataclass(frozen=True)
class HandObservation:
    handedness: str
    landmarks: tuple[Landmark, ...]
    confidence: float


class HandTracker:
    """MediaPipe adapter. Import is delayed so core tests work offline."""

    def __init__(self, model_path: str | Path | None = None, max_hands: int = 2,
                 min_confidence: float = 0.6) -> None:
        self.model_path = Path(model_path) if model_path else Path(__file__).parents[1] / "resources" / "models" / "hand_landmarker.task"
        self.max_hands = max_hands
        self.min_confidence = min_confidence
        self._landmarker: Any = None
        self._last_timestamp_ms = 0

    def start(self) -> None:
        try:
            import mediapipe as mp  # type: ignore
        except ImportError as exc:
            raise RuntimeError("MediaPipe is not installed; install the tracking extra") from exc
        if not self.model_path.is_file():
            raise RuntimeError(f"hand landmark model not found: {self.model_path}")
        base_options = mp.tasks.BaseOptions(model_asset_path=str(self.model_path))
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=self.max_hands,
            min_hand_detection_confidence=self.min_confidence,
            min_hand_presence_confidence=self.min_confidence,
            min_tracking_confidence=self.min_confidence,
        )
        self._landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self._last_timestamp_ms = 0

    def process(self, frame: Any) -> list[HandObservation]:
        if self._landmarker is None:
            raise RuntimeError("tracker is not started")
        import cv2  # type: ignore
        import mediapipe as mp  # type: ignore

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        # VIDEO mode lets MediaPipe track an existing hand between detections,
        # which is substantially faster and steadier than IMAGE mode per frame.
        timestamp_ms = time.monotonic_ns() // 1_000_000
        timestamp_ms = max(timestamp_ms, self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp_ms
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        observations: list[HandObservation] = []
        for index, landmarks in enumerate(result.hand_landmarks):
            category = result.handedness[index][0] if index < len(result.handedness) and result.handedness[index] else None
            confidence = float(category.score) if category is not None else 0.0
            handedness = str(category.category_name or "Unknown") if category is not None else "Unknown"
            observations.append(HandObservation(
                handedness=handedness,
                confidence=confidence,
                landmarks=tuple(Landmark(float(point.x), float(point.y), float(point.z),
                                          float(point.presence or 1.0)) for point in landmarks),
            ))
        return observations

    def close(self) -> None:
        if self._landmarker is not None:
            self._landmarker.close()
            self._landmarker = None
        self._last_timestamp_ms = 0

