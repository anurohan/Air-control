# AirOS AI

AirOS AI is a local-first, touchless computer-control and gesture-typing prototype for Windows. It uses a webcam and MediaPipe hand landmarks to move the cursor, detect pinch gestures, and type alphabet characters by bending fingers.

## Highlights

- Real-time two-hand tracking from a standard webcam.
- Left hand controls the cursor; right hand performs pinch/click actions.
- Non-mirrored camera preview with responsive cursor calibration.
- Gesture alphabet guide drawn over the camera preview.
- Three fixed bend-angle levels per finger, mapped to A-Z.
- Stable multi-frame selection to prevent accidental typing from small movements.
- Sends selected letters to the active Windows application.
- Live word prefix and matching word suggestions.
- Local MediaPipe hand-landmarker model included in the repository.
- Emergency stop and confidence-gated desktop input.

## Requirements

- Windows 10 or Windows 11
- Python 3.11
- A webcam
- A working `.venv` environment with the packages in `requirements.txt`

## Quick start

Double-click `start.bat` to launch the application. Or run it from PowerShell:

```powershell
cd "D:\5th sem\airos"
& ".venv\Scripts\python.exe" -m app.main
```

For a fresh setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## How to use

1. Start the app with `start.bat`.
2. Press **START PROJECT / MODEL** to open the camera and load the hand model.
3. Press **Enable two-hand control** when you are ready to control the desktop.
4. Use the left hand to move the cursor.
5. Use the right-hand pinch gesture for a mouse click.
6. Bend a finger through its three angle levels to select a letter from the A-Z guide.
7. Keep the target text field focused; selected letters are sent to the active Windows application.
8. Use **Emergency stop** immediately if desktop input behaves unexpectedly.

The camera preview shows landmarks, pinch state, selected letters, and word suggestions. A finger must remain in a bend-angle band for several frames before a letter is accepted.

## Project layout

```text
app/                Application entry point
ui/                 PySide6 desktop window and camera preview
vision/             Camera, MediaPipe tracking, smoothing and coordinates
gestures/           Pinch and gesture state detection
input_control/      Safety gate, mouse input and Windows keyboard input
typing_assist/      Typing state and word suggestion support
resources/models/   Included MediaPipe hand-landmarker model
tests/              Core automated tests
start.bat           One-click Windows launcher
```

## Safety and privacy

Camera frames are processed locally and are not uploaded by the application. Desktop input is disabled until it is explicitly enabled. Keep the emergency stop button accessible while testing gesture input, and avoid using the prototype in password fields or other sensitive applications until it has been validated for your setup.

## Development

Run tests with:

```powershell
& ".venv\Scripts\python.exe" -m pytest -q
```

Run diagnostics with:

```powershell
& ".venv\Scripts\python.exe" -m app.main --diagnostics
```

## License

See [LICENSE](LICENSE).
