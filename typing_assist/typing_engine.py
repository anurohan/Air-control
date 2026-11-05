from __future__ import annotations


class TypingEngine:
    def __init__(self) -> None:
        self.shift = False
        self.caps_lock = False
        self.text = ""

    def press(self, key: str) -> str:
        if key == "Shift":
            self.shift = not self.shift
            return ""
        if key == "Caps Lock":
            self.caps_lock = not self.caps_lock
            return ""
        if key == "Backspace":
            self.text = self.text[:-1]
            return ""
        if key == "Space":
            self.text += " "
            return " "
        if len(key) == 1:
            value = key.upper() if self.shift or self.caps_lock else key.lower()
            self.text += value
            if self.shift:
                self.shift = False
            return value
        return ""

