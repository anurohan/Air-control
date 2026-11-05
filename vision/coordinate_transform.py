from __future__ import annotations

from dataclasses import dataclass


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Calibration:
    left: float = 0.05
    top: float = 0.05
    right: float = 0.95
    bottom: float = 0.95

    def __post_init__(self) -> None:
        if not (0 <= self.left < self.right <= 1 and 0 <= self.top < self.bottom <= 1):
            raise ValueError("calibration bounds must be ordered normalized values")


def normalized_to_screen(x: float, y: float, width: int, height: int,
                         calibration: Calibration | None = None, mirror: bool = True) -> tuple[int, int]:
    if width <= 0 or height <= 0:
        raise ValueError("screen dimensions must be positive")
    calibration = calibration or Calibration()
    x = 1.0 - x if mirror else x
    sx = clamp((x - calibration.left) / (calibration.right - calibration.left), 0, 1)
    sy = clamp((y - calibration.top) / (calibration.bottom - calibration.top), 0, 1)
    return round(sx * (width - 1)), round(sy * (height - 1))

