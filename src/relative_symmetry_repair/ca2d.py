"""2D cellular automaton simulation (totalistic outer-totalistic rules on a torus)."""
from __future__ import annotations

import numpy as np
from numba import njit


def random_initial_grid(
    width: int,
    height: int,
    density: float = 0.5,
    seed: int | None = None,
) -> np.ndarray:
    """Create a random binary 2D initial condition."""
    rng = np.random.default_rng(seed)
    return (rng.random((height, width)) < density).astype(np.uint8)


@njit(cache=True)
def _simulate_life_numba(
    initial: np.ndarray,
    steps: int,
    survive_lo: int,
    survive_hi: int,
    birth_lo: int,
    birth_hi: int,
) -> np.ndarray:
    """Simulate a Life-like CA with survival/birth ranges on a torus."""
    H, W = initial.shape
    spacetime = np.empty((steps, H, W), dtype=np.uint8)
    spacetime[0] = initial
    for t in range(1, steps):
        prev = spacetime[t - 1]
        cur = spacetime[t]
        for y in range(H):
            for x in range(W):
                total = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        total += prev[(y + dy) % H, (x + dx) % W]
                alive = prev[y, x]
                if alive:
                    cur[y, x] = 1 if survive_lo <= total <= survive_hi else 0
                else:
                    cur[y, x] = 1 if birth_lo <= total <= birth_hi else 0
    return spacetime


# Predefined 2D rules as (survive_lo, survive_hi, birth_lo, birth_hi)
LIFE_RULES: dict[str, tuple[int, int, int, int]] = {
    "life": (2, 3, 3, 3),         # Conway's Game of Life B3/S23
    "highlife": (2, 3, 3, 6),     # B36/S23
    "seeds": (9, 9, 2, 2),        # B2/S (nothing survives)
    "daynight": (3, 6, 3, 6),     # B3678/S34678 (approximate)
    "diamoeba": (5, 8, 5, 8),     # B5678/S5678
}


def simulate_2d(
    initial: np.ndarray,
    steps: int,
    rule: str = "life",
    survive: tuple[int, int] | None = None,
    birth: tuple[int, int] | None = None,
) -> np.ndarray:
    """Simulate a 2D totalistic CA on a torus.

    Parameters
    ----------
    initial : 2D uint8 array (H, W)
    steps : number of time steps (including initial)
    rule : named rule from LIFE_RULES, or "custom"
    survive : (lo, hi) neighbor count range for survival (used if rule="custom")
    birth : (lo, hi) neighbor count range for birth (used if rule="custom")

    Returns
    -------
    spacetime : 3D uint8 array (steps, H, W)
    """
    if initial.ndim != 2:
        raise ValueError("initial must be a 2D binary array")
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if np.any((initial != 0) & (initial != 1)):
        raise ValueError("initial must be binary")

    if survive is not None and birth is not None:
        s_lo, s_hi = survive
        b_lo, b_hi = birth
    elif rule in LIFE_RULES:
        s_lo, s_hi, b_lo, b_hi = LIFE_RULES[rule]
    else:
        raise ValueError(f"Unknown rule {rule!r}. Choose from {list(LIFE_RULES)} or pass survive/birth.")

    return _simulate_life_numba(
        initial.astype(np.uint8), int(steps),
        int(s_lo), int(s_hi), int(b_lo), int(b_hi),
    )


def rule_consistency_mask_2d(
    spacetime: np.ndarray,
    survive: tuple[int, int],
    birth: tuple[int, int],
) -> np.ndarray:
    """Return cells where a 2D spacetime violates the given Life-like rule."""
    if spacetime.ndim != 3:
        raise ValueError("spacetime must be 3D (steps, H, W)")
    if spacetime.shape[0] < 2:
        return np.zeros((0, *spacetime.shape[1:]), dtype=bool)

    s_lo, s_hi = survive
    b_lo, b_hi = birth
    prev = spacetime[:-1].astype(np.int32)
    actual_next = spacetime[1:].astype(np.uint8)

    # Count neighbors with periodic boundary via roll
    neighbor_count = np.zeros_like(prev)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            neighbor_count += np.roll(np.roll(prev, -dy, axis=1), -dx, axis=2)

    alive = prev.astype(bool)
    predicted = np.where(
        alive,
        ((neighbor_count >= s_lo) & (neighbor_count <= s_hi)).astype(np.uint8),
        ((neighbor_count >= b_lo) & (neighbor_count <= b_hi)).astype(np.uint8),
    )
    return predicted != actual_next


def rule_consistency_rate_2d(
    spacetime: np.ndarray,
    survive: tuple[int, int],
    birth: tuple[int, int],
) -> float:
    mask = rule_consistency_mask_2d(spacetime, survive, birth)
    if mask.size == 0:
        return 0.0
    return float(mask.mean())
