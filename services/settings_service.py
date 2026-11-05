from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Settings:
    camera_index: int = 0
    mirror_camera: bool = True
    overlay_opacity: float = 0.85
    pointer_smoothing: float = 0.35
    input_enabled: bool = False
    keyboard_visible: bool = False

    def validate(self) -> Settings:
        self.camera_index = max(0, int(self.camera_index))
        self.overlay_opacity = min(1.0, max(0.1, float(self.overlay_opacity)))
        self.pointer_smoothing = min(1.0, max(0.01, float(self.pointer_smoothing)))
        return self


def load_settings(path: Path) -> Settings:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Settings(**{k: data[k] for k in Settings.__dataclass_fields__ if k in data}).validate()
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return Settings()


def save_settings(path: Path, settings: Settings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(settings.validate()), indent=2), encoding="utf-8")

