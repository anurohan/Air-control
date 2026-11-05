from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass
class GestureEngine:
    cooldown_seconds: float = 0.35
    enabled: bool = False
    paused: bool = True
    _last_action: dict[str, float] | None = None

    def __post_init__(self) -> None:
        self._last_action = {}

    def allow(self, action: str, now: float | None = None) -> bool:
        if not self.enabled or self.paused:
            return False
        current = monotonic() if now is None else now
        last = self._last_action.get(action, float("-inf"))
        if current - last < self.cooldown_seconds:
            return False
        self._last_action[action] = current
        return True

