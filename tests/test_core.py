from gestures.gesture_engine import GestureEngine
from gestures.pinch_detector import PinchDetector
from input_control.action_safety import SafetyGate
from input_control.mouse_controller import InputService
from services.settings_service import Settings
from typing_assist.key_hit_testing import KeyRect, hit_test
from typing_assist.typing_engine import TypingEngine
from vision.coordinate_transform import Calibration, normalized_to_screen


def test_coordinate_mapping_mirror_and_clamp():
    assert normalized_to_screen(0.05, 0.05, 100, 100, Calibration(), mirror=False) == (0, 0)
    assert normalized_to_screen(2, -1, 100, 100, Calibration(), mirror=False) == (99, 0)


def test_pinch_hysteresis_only_emits_edges():
    detector = PinchDetector()
    assert detector.update((0, 0), (0.03, 0), 1) == "pinch_start"
    assert detector.update((0, 0), (0.04, 0), 1) is None
    assert detector.update((0, 0), (0.10, 0), 1) == "pinch_release"


def test_pinch_adapts_to_hand_scale():
    detector = PinchDetector()
    assert detector.update((0, 0), (0.04, 0), 1, hand_scale=0.1) == "pinch_start"
    assert detector.update((0, 0), (0.05, 0), 1, hand_scale=0.1) is None
    assert detector.update((0, 0), (0.08, 0), 1, hand_scale=0.1) == "pinch_release"


def test_low_confidence_releases_active_pinch():
    detector = PinchDetector()
    assert detector.update((0, 0), (0.03, 0), 1) == "pinch_start"
    assert detector.update((0, 0), (0.03, 0), 0.1) == "pinch_release"


def test_gesture_cooldown_and_safety_gate():
    engine = GestureEngine(cooldown_seconds=1)
    engine.enabled, engine.paused = True, False
    assert engine.allow("click", 10)
    assert not engine.allow("click", 10.5)
    gate = SafetyGate()
    assert not gate.permit(1)
    gate.enable()
    assert gate.permit(1)
    gate.stop()
    assert not gate.permit(1)


def test_key_hit_testing_and_typing_state():
    assert hit_test([KeyRect("A", 0, 0, 10, 10)], 5, 5) == "A"
    assert hit_test([KeyRect("A", 0, 0, 10, 10)], 20, 5) is None
    typing = TypingEngine()
    typing.press("Shift")
    assert typing.press("a") == "A"
    assert typing.press("a") == "a"


def test_settings_validation():
    settings = Settings(overlay_opacity=8, pointer_smoothing=-2).validate()
    assert settings.overlay_opacity == 1
    assert settings.pointer_smoothing == 0.01


def test_input_service_never_calls_backend_when_gate_blocks():
    class FakeMouse:
        def __init__(self):
            self.moves, self.clicks = [], 0
        def move(self, x, y):
            self.moves.append((x, y))
        def left_click(self):
            self.clicks += 1
    fake = FakeMouse()
    service = InputService(fake)
    gate = SafetyGate()
    assert not service.move_pointer(1, 2, 1, gate)
    assert not service.click(1, gate)
    assert fake.moves == [] and fake.clicks == 0


def test_pinch_action_is_explicit_left_click():
    class FakeMouse:
        def __init__(self):
            self.clicks, self.downs, self.ups = 0, 0, 0
        def left_click(self):
            self.clicks += 1
        def left_down(self):
            self.downs += 1
        def left_up(self):
            self.ups += 1
    fake = FakeMouse()
    service = InputService(fake)
    gate = SafetyGate()
    gate.enable()
    assert service.left_click(1.0, gate)
    assert fake.clicks == 1
    assert service.press_left(1.0, gate)
    service.release_left()
    assert fake.downs == 1 and fake.ups == 1

