from __future__ import annotations

import math

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QAction, QImage, QPixmap
    from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
except ImportError as exc:  # pragma: no cover
    raise ImportError("PySide6 is required for the desktop UI") from exc

from gestures.pinch_detector import PinchDetector
from input_control.action_safety import SafetyGate
from input_control.keyboard_controller import WindowsKeyboardController
from input_control.mouse_controller import InputService
from services.diagnostics_service import environment_report
from typing_assist.typing_engine import TypingEngine
from vision.camera_manager import CameraManager
from vision.coordinate_transform import Calibration, normalized_to_screen
from vision.hand_tracker import HandTracker
from vision.smoothing import OneEuroLikeSmoother

HAND_CONNECTIONS = ((0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
                    (0, 9), (9, 10), (10, 11), (11, 12), (0, 13), (13, 14), (14, 15),
                    (15, 16), (0, 17), (17, 18), (18, 19), (19, 20), (5, 9), (9, 13), (13, 17))

# Three bend levels per finger, ordered A-Z from the left hand to the right.
# Empty slots keep the layout at exactly three levels while exposing only A-Z.
LEFT_FINGER_KEYS = (("A", "B", "C"), ("D", "E", "F"), ("G", "H", "I"),
                    ("J", "K", "L"), ("M", "N", "O"))
RIGHT_FINGER_KEYS = (("P", "Q", "R"), ("S", "T", "U"), ("V", "W", "X"),
                     ("Y", "Z", ""), ("", "", ""))
FINGER_LANDMARKS = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12),
                    (13, 14, 15, 16), (17, 18, 19, 20))
COMMON_WORDS = """about after again air all also and animal another any are around as ask at back be because become been before being between big but by call camera can come could day did different do down each even every finger first for from get give go good hand has have he her here high him his how i if in into is it just key know letter like look make many me more most my new no not now of on one only or other our out over people right same say screen select see she so some start take than that the their them then there these they thing think this time to two up use very want was way we well what when where which who will with word would you your""".split()


class OverlayWindow(QWidget):
    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
                         Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.gate = SafetyGate()
        self.input_service = InputService()
        self.keyboard_input = WindowsKeyboardController()
        self.click_pinch = PinchDetector(press_distance=0.46, release_distance=0.66)
        self.cursor_smoother = OneEuroLikeSmoother(alpha=0.40)
        # Use a tighter camera calibration window so a small camera frame
        # still maps across almost the entire laptop screen.
        self.cursor_calibration = Calibration(left=0.18, top=0.12, right=0.82, bottom=0.88)
        self.typing_engine = TypingEngine()
        self.current_word = ""
        self.camera = CameraManager()
        self.tracker = HandTracker(max_hands=2, min_confidence=0.55)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_frame)
        self.gesture_keyboard_enabled = True
        self.gesture_finger_states: dict[tuple[str, int], int | None] = {}
        self.gesture_pending_states: dict[tuple[str, int], tuple[int | None, int]] = {}
        self.setWindowTitle("AirOS AI")
        self.setMinimumSize(460, 340)
        self.status = QLabel("Tracking stopped - desktop control disabled")
        self.status.setWordWrap(True)
        self.gesture_status = QLabel("Hands: 0 - R=cursor, L=click")
        self.pinch_feedback = QLabel("Pinch: READY | distance: -- | confidence: --")
        self.pinch_feedback.setStyleSheet("font-size: 15px; font-weight: 700; color: #2563eb;")
        self.word_feedback = QLabel("Word: -- | Suggestions: --")
        self.word_feedback.setStyleSheet("font-size: 15px; font-weight: 700; color: #7c3aed;")
        self.preview = QLabel("Camera preview unavailable until safe mode starts")
        self.preview.setMinimumSize(360, 260)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_button = QPushButton("START PROJECT / MODEL")
        self.start_button.setMinimumHeight(48)
        self.start_button.setStyleSheet(
            "QPushButton { background-color: #20a464; color: white; "
            "font-size: 18px; font-weight: 700; border-radius: 8px; padding: 8px; }"
            "QPushButton:disabled { background-color: #6b7280; }"
        )
        self.start_button.clicked.connect(self.start_safe_mode)
        control = QPushButton("Enable two-hand control")
        control.clicked.connect(self.enable_control)
        keyboard = QPushButton("Show / hide virtual keyboard")
        keyboard.setText("Show / hide alphabet guide")
        keyboard.clicked.connect(self.toggle_keyboard)
        stop = QPushButton("Emergency stop")
        stop.clicked.connect(self.stop)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("AirOS AI - local touchless control"))
        layout.addWidget(self.status)
        layout.addWidget(self.gesture_status)
        layout.addWidget(self.pinch_feedback)
        layout.addWidget(self.word_feedback)
        layout.addWidget(self.preview)
        layout.addWidget(self.start_button)
        layout.addWidget(control)
        layout.addWidget(keyboard)
        layout.addWidget(stop)
        layout.addWidget(QLabel(environment_report()))
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        self.menuBar().addAction(quit_action)

    def start_safe_mode(self) -> None:
        try:
            self.camera.open()
            self.tracker.start()
            self.cursor_smoother.reset()
            self.gesture_keyboard_enabled = True
            self.gesture_finger_states.clear()
            self.gesture_pending_states.clear()
            self.timer.start(33)
            self.start_button.setEnabled(False)
            self.status.setText("Project started - camera, hand model and alphabet guide are active")
        except RuntimeError as exc:
            self.camera.close()
            self.tracker.close()
            self.status.setText(f"Camera unavailable - {exc}")

    @staticmethod
    def _roles(observations):
        by_hand = {hand.handedness.lower(): hand for hand in observations}
        cursor_hand = by_hand.get("left")
        click_hand = by_hand.get("right")
        unknown = [hand for hand in observations if hand not in (cursor_hand, click_hand)]
        if cursor_hand is None:
            cursor_hand = unknown.pop(0) if unknown else click_hand
        if click_hand is None:
            # A single hand should still support both pointer and pinch.
            click_hand = unknown.pop(0) if unknown else cursor_hand
        return cursor_hand, click_hand

    @staticmethod
    def _distance(a, b) -> float:
        return math.hypot(a.x - b.x, a.y - b.y)

    @classmethod
    def _finger_curl(cls, landmarks, indices) -> float:
        """Return a 0..1 curl estimate from two finger joint angles."""
        mcp, pip, dip, tip = (landmarks[index] for index in indices)

        def joint_angle(first, middle, last) -> float:
            ax, ay = first.x - middle.x, first.y - middle.y
            bx, by = last.x - middle.x, last.y - middle.y
            denominator = max(math.hypot(ax, ay) * math.hypot(bx, by), 1e-6)
            cosine = max(-1.0, min(1.0, (ax * bx + ay * by) / denominator))
            return math.degrees(math.acos(cosine))

        bend = ((180.0 - joint_angle(mcp, pip, dip)) +
                (180.0 - joint_angle(pip, dip, tip))) / 360.0
        return max(0.0, min(1.0, bend))

    def _gesture_key(self, hand, finger_index, curl: float, cv2, frame) -> str | None:
        handedness = hand.handedness.lower()
        groups = LEFT_FINGER_KEYS if handedness == "left" else RIGHT_FINGER_KEYS
        letters = groups[finger_index]
        # A relaxed finger only previews choices. Medium/high curl selects
        # the first/second/third choice respectively.
        # Fixed angle bands. A finger must stay in a band for several frames
        # before it is accepted, preventing tiny landmark jitters from typing.
        level = None if curl < 0.20 else min(2, int((curl - 0.20) / 0.25))
        state_key = (handedness, finger_index)
        previous = self.gesture_finger_states.get(state_key)
        pending_level, pending_frames = self.gesture_pending_states.get(state_key, (level, 0))
        if pending_level != level:
            pending_level, pending_frames = level, 0
        pending_frames += 1
        self.gesture_pending_states[state_key] = (pending_level, pending_frames)
        if pending_frames < 5:
            level = previous
        else:
            self.gesture_finger_states[state_key] = level
        selected = letters[level] if level is not None else None
        if selected and level != previous:
            typed = self.typing_engine.press(selected)
            if self.gate.permit(hand.confidence):
                try:
                    self.keyboard_input.type_character(typed)
                    self.current_word += typed.lower()
                    self._update_word_recommendations()
                except (OSError, RuntimeError, ValueError) as exc:
                    self.status.setText(f"Laptop keyboard input failed - {exc}")
        return selected

    def _update_word_recommendations(self) -> None:
        if not self.current_word:
            self.word_feedback.setText("Word: -- | Suggestions: --")
            return
        matches = [word for word in COMMON_WORDS if word.startswith(self.current_word)][:3]
        suggestions = ", ".join(matches) if matches else "no match"
        self.word_feedback.setText(f"Word: {self.current_word} | Suggestions: {suggestions}")

    def update_camera_frame(self) -> None:
        try:
            frame = self.camera.read()
            import cv2
            # Use a natural, non-mirrored camera view. Apply the same
            # orientation before tracking so landmarks and cursor agree.
            frame = cv2.flip(frame, 1)
            observations = self.tracker.process(frame)
            cursor_hand, click_hand = self._roles(observations)
            pinch_label = "ACTIVE" if self.click_pinch.active else ("NEAR" if self.click_pinch.near else "READY")
            self.gesture_status.setText(f"Hands: {len(observations)} - LEFT=cursor, RIGHT=pinch")
            self.pinch_feedback.setText(f"Pinch: {pinch_label} | distance: -- | confidence: --")
            if click_hand is None and self.click_pinch.active:
                self.click_pinch.active = False
                self.click_pinch.near = False
                self.input_service.release_left()
            screen = QApplication.primaryScreen().geometry()
            for hand in observations:
                points = [(int(point.x * frame.shape[1]), int(point.y * frame.shape[0]))
                          for point in hand.landmarks]
                for start, end in HAND_CONNECTIONS:
                    cv2.line(frame, points[start], points[end], (70, 220, 120), 2)
                if len(hand.landmarks) < 9:
                    continue
                thumb_tip, index_tip = points[4], points[8]
                palm_scale = ((hand.landmarks[0].x - hand.landmarks[9].x) ** 2 +
                              (hand.landmarks[0].y - hand.landmarks[9].y) ** 2) ** 0.5
                pinch_distance = (((hand.landmarks[4].x - hand.landmarks[8].x) ** 2 +
                                   (hand.landmarks[4].y - hand.landmarks[8].y) ** 2) ** 0.5 /
                                  max(palm_scale, 1e-6))
                is_click_hand = hand is click_hand
                is_active = is_click_hand and (self.click_pinch.active or pinch_distance <= 0.46)
                pinch_color = (255, 40, 220) if self.click_pinch.active and is_click_hand else (40, 180, 255)
                cv2.line(frame, thumb_tip, index_tip, pinch_color, 4 if is_active else 2)
                cv2.circle(frame, index_tip, 8, (0, 255, 255) if hand is cursor_hand else (255, 80, 220), -1)
                for index, point in enumerate(points):
                    if index not in (4, 8):
                        cv2.circle(frame, point, 3, (255, 180, 40), -1)
                if self.gesture_keyboard_enabled and len(hand.landmarks) >= 21:
                    groups = LEFT_FINGER_KEYS if hand.handedness.lower() == "left" else RIGHT_FINGER_KEYS
                    for finger_index, landmark_indices in enumerate(FINGER_LANDMARKS):
                        tip = points[landmark_indices[-1]]
                        curl = self._finger_curl(hand.landmarks, landmark_indices)
                        selected = self._gesture_key(hand, finger_index, curl, cv2, frame)
                        letters = groups[finger_index]
                        label = " ".join(letter or "-" for letter in letters)
                        cv2.putText(frame, label, (max(2, tip[0] - 28), max(18, tip[1] - 18)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.48,
                                    (0, 255, 80) if selected else (255, 255, 255), 2)
                        if selected:
                            cv2.putText(frame, f"[{selected}]", (max(2, tip[0] - 18), tip[1] + 22),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 2)
                if hand is cursor_hand:
                    smoothed = self.cursor_smoother.update((hand.landmarks[8].x, hand.landmarks[8].y))
                    # The camera frame was already un-mirrored above, so do
                    # not mirror the normalized X coordinate a second time.
                    x, y = normalized_to_screen(
                        smoothed[0], smoothed[1], screen.width(), screen.height(),
                        calibration=self.cursor_calibration, mirror=False)
                    self.input_service.move_pointer(x, y, hand.confidence, self.gate)
                if hand is click_hand:
                    self.pinch_feedback.setText(
                        f"Pinch: {pinch_label} | distance: {pinch_distance:.2f} | "
                        f"confidence: {hand.confidence:.2f}"
                    )
                    event = self.click_pinch.update((hand.landmarks[4].x, hand.landmarks[4].y),
                                                    (hand.landmarks[8].x, hand.landmarks[8].y),
                                                    hand.confidence, palm_scale)
                    pinch_label = "ACTIVE" if self.click_pinch.active else (
                        "NEAR" if self.click_pinch.near else "READY")
                    self.pinch_feedback.setText(
                        f"Pinch: {pinch_label} | distance: {pinch_distance:.2f} | "
                        f"confidence: {hand.confidence:.2f}"
                    )
                    if event == "pinch_start":
                        try:
                            held = self.input_service.press_left(hand.confidence, self.gate)
                            self.gesture_status.setText("Click hand pinch - mouse down" if held else "Pinch detected (control disabled)")
                        except (OSError, RuntimeError) as exc:
                            self.gesture_status.setText(f"Click pinch failed: {exc}")
                    elif event == "pinch_release":
                        try:
                            self.input_service.release_left()
                            self.gesture_status.setText("Click hand released - mouse up")
                        except (OSError, RuntimeError) as exc:
                            self.gesture_status.setText(f"Click release failed: {exc}")
            cv2.putText(frame, f"hands: {len(observations)} | bend fingers: A-Z", (12, 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 240, 120), 2)
            suggestions = self.word_feedback.text().replace("Word: ", "").replace(" | Suggestions: ", " -> ")
            cv2.putText(frame, suggestions[:70], (12, 52), cv2.FONT_HERSHEY_SIMPLEX,
                        0.48, (210, 150, 255), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = frame.shape
            image = QImage(frame.data, width, height, channels * width, QImage.Format.Format_RGB888)
            self.preview.setPixmap(QPixmap.fromImage(image).scaled(
                self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        except RuntimeError as exc:
            self.timer.stop()
            self.camera.close()
            self.status.setText(f"Camera disconnected - {exc}")

    def enable_control(self) -> None:
        self.gate.enable()
        self.status.setText("Two-hand control enabled - LEFT hand cursor, RIGHT hand pinch click")

    def toggle_keyboard(self) -> None:
        self.gesture_keyboard_enabled = not self.gesture_keyboard_enabled
        self.gesture_finger_states.clear()
        self.gesture_pending_states.clear()
        state = "active" if self.gesture_keyboard_enabled else "hidden"
        self.status.setText(f"Alphabet guide {state} - bend a finger to select a letter")

    def stop(self) -> None:
        self.gate.stop()
        try:
            self.input_service.release_left()
        except (OSError, RuntimeError):
            pass
        self.timer.stop()
        self.camera.close()
        self.tracker.close()
        self.start_button.setEnabled(True)
        self.preview.clear()
        self.preview.setText("Camera stopped")
        self.status.setText("Emergency stop active - desktop control disabled")

    def closeEvent(self, event) -> None:
        self.stop()
        event.accept()


def run_desktop() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()
