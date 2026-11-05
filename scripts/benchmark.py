from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vision.smoothing import OneEuroLikeSmoother


def main() -> None:
    smoother = OneEuroLikeSmoother()
    count = 10_000
    started = time.perf_counter()
    for index in range(count):
        smoother.update((index / count, index / count))
    elapsed = time.perf_counter() - started
    print(f"smoothing_iterations={count}")
    print(f"elapsed_seconds={elapsed:.6f}")
    print(f"iterations_per_second={count / elapsed:.0f}")
    print("This is a core microbenchmark, not a webcam FPS result.")


if __name__ == "__main__":
    main()

