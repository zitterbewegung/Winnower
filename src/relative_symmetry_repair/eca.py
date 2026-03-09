from __future__ import annotations

import numpy as np
from numba import njit


def random_initial_state(
    width: int,
    density: float = 0.5,
    seed: int | None = None,
) -> np.ndarray:
    """Create a random binary initial condition."""
    rng = np.random.default_rng(seed)
    return (rng.random(width) < density).astype(np.uint8)


@njit(cache=True)
def _simulate_eca_numba(rule: int, initial: np.ndarray, steps: int) -> np.ndarray:
    width = initial.size
    spacetime = np.empty((steps, width), dtype=np.uint8)
    spacetime[0] = initial
    for t in range(1, steps):
        previous = spacetime[t - 1]
        current = spacetime[t]
        for i in range(width):
            left = previous[(i - 1) % width]
            center = previous[i]
            right = previous[(i + 1) % width]
            pattern = (left << 2) | (center << 1) | right
            current[i] = (rule >> pattern) & 1
    return spacetime


def simulate_eca(rule: int, initial: np.ndarray, steps: int) -> np.ndarray:
    """Simulate an elementary cellular automaton on a periodic ring."""
    if initial.ndim != 1:
        raise ValueError("initial must be a 1D binary array")
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if np.any((initial != 0) & (initial != 1)):
        raise ValueError("initial must be binary")
    return _simulate_eca_numba(int(rule), initial.astype(np.uint8), int(steps))


def rule_consistency_mask(spacetime: np.ndarray, rule: int) -> np.ndarray:
    """Return the cells where a spacetime field violates the ECA rule."""
    if spacetime.ndim != 2:
        raise ValueError("spacetime must be 2D")
    if spacetime.shape[0] < 2:
        return np.zeros((0, spacetime.shape[1]), dtype=bool)

    previous = spacetime[:-1].astype(np.uint8)
    next_state = spacetime[1:].astype(np.uint8)
    left = np.roll(previous, 1, axis=1)
    center = previous
    right = np.roll(previous, -1, axis=1)
    patterns = (left << 2) | (center << 1) | right
    predicted = ((int(rule) >> patterns) & 1).astype(np.uint8)
    return predicted != next_state


def rule_consistency_rate(spacetime: np.ndarray, rule: int) -> float:
    """Mean local-rule violation rate for a spacetime field."""
    mask = rule_consistency_mask(spacetime, rule)
    if mask.size == 0:
        return 0.0
    return float(mask.mean())
