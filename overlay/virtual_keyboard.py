from __future__ import annotations

from typing_assist.key_hit_testing import KeyRect

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover - desktop optional dependency
    Qt = Signal = QGridLayout = QLabel = QPushButton = QVBoxLayout = QWidget = None


def qwerty_layout(origin_x: float = 40, origin_y: float = 40, key_size: float = 48,
                  gap: float = 6) -> list[KeyRect]:
    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    keys: list[KeyRect] = []
    for row_index, row in enumerate(rows):
        offset = row_index * key_size * 0.35
        for column, key in enumerate(row):
            x = origin_x + offset + column * (key_size + gap)
            y = origin_y + row_index * (key_size + gap)
            keys.append(KeyRect(key, x, y, key_size, key_size))
    return keys


def full_keyboard_layout() -> list[list[str]]:
    """Human-sized layout used by the on-screen keyboard widget."""
    return [
        list("QWERTYUIOP"),
        list("ASDFGHJKL"),
        list("ZXCVBNM"),
        ["Shift", "Caps Lock", "Space", "Backspace", "Enter"],
    ]


if QWidget is not None:
    class VirtualKeyboardWindow(QWidget):
        """Always-on-top keyboard that accepts real or injected mouse clicks."""

        key_pressed = Signal(str)

        def __init__(self, typing_engine, parent=None) -> None:
            super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
            self.typing_engine = typing_engine
            self.setWindowTitle("AirOS Virtual Keyboard")
            self.setWindowOpacity(0.94)
            self.setMinimumWidth(760)
            self.output = QLabel("Air typing ready")
            self.output.setObjectName("keyboardOutput")
            self.output.setMinimumHeight(42)
            self.output.setWordWrap(True)
            self.output.setStyleSheet("font-size: 20px; padding: 8px; background: #14202b; color: #f5f7fa;")
            grid = QGridLayout()
            grid.setSpacing(6)
            for row, keys in enumerate(full_keyboard_layout()):
                for column, key in enumerate(keys):
                    button = QPushButton(key)
                    button.setMinimumHeight(48)
                    button.setMinimumWidth(54 if key not in ("Space", "Backspace") else 130)
                    button.setStyleSheet("font-size: 15px; font-weight: 600;")
                    button.clicked.connect(lambda checked=False, value=key: self.press_key(value))
                    grid.addWidget(button, row, column, 1, 2 if key == "Space" else 1)
            layout = QVBoxLayout(self)
            layout.addWidget(self.output)
            layout.addLayout(grid)
            self.setStyleSheet("background: #263746;")

        def press_key(self, key: str) -> None:
            if key == "Enter":
                self.typing_engine.press("Enter")
            else:
                self.typing_engine.press(key)
            text = self.typing_engine.text or "Air typing ready"
            state = []
            if self.typing_engine.shift:
                state.append("SHIFT")
            if self.typing_engine.caps_lock:
                state.append("CAPS")
            self.output.setText(text + (f"   [{', '.join(state)}]" if state else ""))
            self.key_pressed.emit(key)

        def show_at_bottom(self) -> None:
            screen = self.screen() or self.windowHandle().screen()
            if screen is not None:
                area = screen.availableGeometry()
                self.adjustSize()
                self.move(area.center().x() - self.width() // 2,
                          area.bottom() - self.height() - 20)

