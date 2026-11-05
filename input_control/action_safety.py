from __future__ import annotations


class SafetyGate:
    """Input is opt-in, confidence-gated, and has an immediate stop state."""

    def __init__(self, minimum_confidence: float = 0.65) -> None:
        self.minimum_confidence = minimum_confidence
        self.enabled = False
        self.emergency_stopped = False

    def permit(self, confidence: float) -> bool:
        return self.enabled and not self.emergency_stopped and confidence >= self.minimum_confidence

    def enable(self) -> None:
        self.emergency_stopped = False
        self.enabled = True

    def stop(self) -> None:
        self.enabled = False
        self.emergency_stopped = True

