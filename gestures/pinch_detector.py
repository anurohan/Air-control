from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class PinchDetector:
    press_distance: float = 0.065
    release_distance: float = 0.100
    active: bool = False
    near: bool = False
    last_distance: float = 1.0

    def update(self, thumb: tuple[float, float], index: tuple[float, float], confidence: float,
               hand_scale: float | None = None) -> str | None:
        distance = math.dist(thumb, index)
        if hand_scale is not None and hand_scale > 1e-6:
            distance /= hand_scale
            press_distance, release_distance = 0.52, 0.75
        else:
            press_distance, release_distance = self.press_distance, self.release_distance
        self.last_distance = distance
        self.near = distance <= release_distance
        if confidence < 0.5:
            was_active = self.active
            self.active = False
            self.near = False
            return "pinch_release" if was_active else None
        if not self.active and distance <= press_distance:
            self.active = True
            return "pinch_start"
        if self.active and distance >= release_distance:
            self.active = False
            self.near = False
            return "pinch_release"
        return None

