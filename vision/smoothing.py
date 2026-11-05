from __future__ import annotations


class OneEuroLikeSmoother:
    """Small dependency-free exponential smoother for normalized landmarks."""

    def __init__(self, alpha: float = 0.35) -> None:
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self._value: tuple[float, float] | None = None

    def update(self, point: tuple[float, float]) -> tuple[float, float]:
        if self._value is None:
            self._value = point
        else:
            a = self.alpha
            self._value = (a * point[0] + (1 - a) * self._value[0],
                           a * point[1] + (1 - a) * self._value[1])
        return self._value

    def reset(self) -> None:
        self._value = None

