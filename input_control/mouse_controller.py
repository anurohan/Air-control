from __future__ import annotations

import ctypes
from typing import Protocol


class MouseBackend(Protocol):
    def move(self, x: int, y: int) -> None: ...
    def left_down(self) -> None: ...
    def left_up(self) -> None: ...
    def left_click(self) -> None: ...


class WindowsMouseController:
    """Minimal Windows adapter; callers must gate every operation."""

    _LEFT_DOWN = 0x0002
    _LEFT_UP = 0x0004

    def move(self, x: int, y: int) -> None:
        if not hasattr(ctypes, "windll"):
            raise RuntimeError("Windows mouse input is unavailable on this platform")
        if not ctypes.windll.user32.SetCursorPos(int(x), int(y)):
            raise OSError("SetCursorPos failed")

    def left_click(self) -> None:
        self.left_down()
        self.left_up()

    def left_down(self) -> None:
        if not hasattr(ctypes, "windll"):
            raise RuntimeError("Windows mouse input is unavailable on this platform")
        ctypes.windll.user32.mouse_event(self._LEFT_DOWN, 0, 0, 0, 0)

    def left_up(self) -> None:
        if not hasattr(ctypes, "windll"):
            raise RuntimeError("Windows mouse input is unavailable on this platform")
        ctypes.windll.user32.mouse_event(self._LEFT_UP, 0, 0, 0, 0)


class InputService:
    def __init__(self, backend: MouseBackend | None = None) -> None:
        self.backend = backend or WindowsMouseController()

    def move_pointer(self, x: int, y: int, confidence: float, gate) -> bool:
        if not gate.permit(confidence):
            return False
        self.backend.move(x, y)
        return True

    def click(self, confidence: float, gate) -> bool:
        """Backward-compatible alias for a guarded left click."""
        return self.left_click(confidence, gate)

    def left_click(self, confidence: float, gate) -> bool:
        if not gate.permit(confidence):
            return False
        self.backend.left_click()
        return True

    def press_left(self, confidence: float, gate) -> bool:
        if not gate.permit(confidence):
            return False
        self.backend.left_down()
        return True

    def release_left(self) -> None:
        self.backend.left_up()

