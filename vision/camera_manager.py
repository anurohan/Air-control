from __future__ import annotations

from typing import Any


class CameraManager:
    def __init__(self, index: int = 0, width: int = 640, height: int = 480, fps: int = 30) -> None:
        self.index, self.width, self.height, self.fps = index, width, height, fps
        self._capture: Any = None

    def open(self) -> None:
        try:
            import cv2  # type: ignore
        except ImportError as exc:
            raise RuntimeError("OpenCV is not installed; install the desktop extra") from exc
        self._capture = cv2.VideoCapture(self.index)
        if not self._capture.isOpened():
            self.close()
            raise RuntimeError(f"unable to open camera {self.index}")
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._capture.set(cv2.CAP_PROP_FPS, self.fps)

    def read(self) -> Any:
        if self._capture is None:
            raise RuntimeError("camera is not open")
        ok, frame = self._capture.read()
        if not ok:
            raise RuntimeError("camera frame unavailable")
        return frame

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

