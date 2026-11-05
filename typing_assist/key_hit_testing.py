from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeyRect:
    key: str
    x: float
    y: float
    width: float
    height: float

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height


def hit_test(keys: list[KeyRect], x: float, y: float) -> str | None:
    return next((key.key for key in keys if key.contains(x, y)), None)

