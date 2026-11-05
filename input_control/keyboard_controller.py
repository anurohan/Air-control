from __future__ import annotations

import ctypes


class WindowsKeyboardController:
    """Send a single safe alphabet character to the active Windows app."""

    _KEYEVENTF_KEYUP = 0x0002
    _VK_SHIFT = 0x10

    def type_character(self, character: str) -> None:
        if not hasattr(ctypes, "windll"):
            raise RuntimeError("Windows keyboard input is unavailable on this platform")
        if len(character) != 1 or not character.isalpha() or not character.isascii():
            raise ValueError("Only ASCII alphabet characters are supported")

        user32 = ctypes.windll.user32
        scan = user32.VkKeyScanW(ord(character.lower()))
        if scan == -1:
            raise OSError(f"No Windows key mapping for {character!r}")
        virtual_key = scan & 0xFF
        modifiers = (scan >> 8) & 0xFF
        if modifiers & 1:
            user32.keybd_event(self._VK_SHIFT, 0, 0, 0)
        user32.keybd_event(virtual_key, 0, 0, 0)
        user32.keybd_event(virtual_key, 0, self._KEYEVENTF_KEYUP, 0)
        if modifiers & 1:
            user32.keybd_event(self._VK_SHIFT, 0, self._KEYEVENTF_KEYUP, 0)
