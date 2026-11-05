# Feature status

| Area | Status | Evidence/notes |
|---|---|---|
| Core coordinate mapping | Implemented/tested | Normalized mapping, mirror, calibration bounds, clamping |
| Smoothing | Implemented/tested | Dependency-free exponential smoother |
| Pinch state | Implemented/tested | Hysteresis and confidence gate |
| Gesture cooldown | Implemented/tested | Stateful action cooldown |
| Input safety | Implemented/tested | Explicit enable, confidence threshold, emergency stop |
| Settings | Implemented/tested | Validated local JSON service |
| Camera lifecycle | Implemented | Open/read/close adapter; webcam not run in this session |
| Hand landmarks | Implemented/smoke-tested | MediaPipe Tasks model loads and processes a real webcam frame; person-in-frame quality not measured |
| Qt dashboard | Implemented/smoke-tested | Offscreen UI camera start/stop cycle verified |
| Transparent overlay | Boundary implemented | Click-through window class; visual Windows interaction still manual |
| Virtual keyboard geometry | Implemented/tested indirectly | QWERTY layout and hit rectangles |
| Windows pointer/keyboard injection | Pointer/click adapter implemented | Explicit opt-in and confidence gate; manual ergonomics/safety test remains |
| Real-time performance | Unverified | Benchmark currently covers only smoothing core |
| Packaging | Planned | PyInstaller script not yet added |

