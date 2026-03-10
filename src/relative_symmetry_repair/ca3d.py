"""3D cellular automaton simulation (totalistic rules on a 3-torus)."""
from __future__ import annotations

import numpy as np
from numba import njit


def random_initial_volume(
    sx: int,
    sy: int,
    sz: int,
    density: float = 0.5,
    seed: int | None = None,
) -> np.ndarray:
    """Create a random binary 3D initial condition."""
    rng = np.random.default_rng(seed)
    return (rng.random((sz, sy, sx)) < density).astype(np.uint8)


@njit(cache=True)
def _simulate_3d_numba(
    initial: np.ndarray,
    steps: int,
    survive_lo: int,
    survive_hi: int,
    birth_lo: int,
    birth_hi: int,
) -> np.ndarray:
    """Simulate a 3D totalistic CA (26-neighbor Moore neighborhood) on a 3-torus."""
    Sz, Sy, Sx = initial.shape
    spacetime = np.empty((steps, Sz, Sy, Sx), dtype=np.uint8)
    spacetime[0] = initial
    for t in range(1, steps):
        prev = spacetime[t - 1]
        cur = spacetime[t]
        for z in range(Sz):
            for y in range(Sy):
                for x in range(Sx):
                    total = 0
                    for dz in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            for dx in (-1, 0, 1):
                                if dz == 0 and dy == 0 and dx == 0:
                                    continue
                                total += prev[(z + dz) % Sz, (y + dy) % Sy, (x + dx) % Sx]
                    alive = prev[z, y, x]
                    if alive:
                        cur[z, y, x] = 1 if survive_lo <= total <= survive_hi else 0
                    else:
                        cur[z, y, x] = 1 if birth_lo <= total <= birth_hi else 0
    return spacetime


# Predefined 3D rules as (survive_lo, survive_hi, birth_lo, birth_hi)
RULES_3D: dict[str, tuple[int, int, int, int]] = {
    "3d-life": (4, 5, 5, 5),         # A common 3D analogue
    "clouds": (13, 26, 13, 14),       # Dense, cloud-like
    "crystal": (1, 1, 1, 3),          # Sparse crystal growth
    "diamoeba3d": (5, 8, 5, 8),       # 3D diamoeba analogue
}


def simulate_3d(
    initial: np.ndarray,
    steps: int,
    rule: str = "3d-life",
    survive: tuple[int, int] | None = None,
    birth: tuple[int, int] | None = None,
) -> np.ndarray:
    """Simulate a 3D totalistic CA on a 3-torus.

    Parameters
    ----------
    initial : 3D uint8 array (Sz, Sy, Sx)
    steps : number of time steps (including initial)
    rule : named rule from RULES_3D, or "custom"
    survive/birth : (lo, hi) neighbor counts for custom rules

    Returns
    -------
    spacetime : 4D uint8 array (steps, Sz, Sy, Sx)
    """
    if initial.ndim != 3:
        raise ValueError("initial must be a 3D binary array")
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if np.any((initial != 0) & (initial != 1)):
        raise ValueError("initial must be binary")

    if survive is not None and birth is not None:
        s_lo, s_hi = survive
        b_lo, b_hi = birth
    elif rule in RULES_3D:
        s_lo, s_hi, b_lo, b_hi = RULES_3D[rule]
    else:
        raise ValueError(f"Unknown rule {rule!r}. Choose from {list(RULES_3D)} or pass survive/birth.")

    return _simulate_3d_numba(
        initial.astype(np.uint8), int(steps),
        int(s_lo), int(s_hi), int(b_lo), int(b_hi),
    )


def rule_consistency_mask_3d(
    spacetime: np.ndarray,
    survive: tuple[int, int],
    birth: tuple[int, int],
) -> np.ndarray:
    """Return cells where a 3D spacetime violates the given rule."""
    if spacetime.ndim != 4:
        raise ValueError("spacetime must be 4D (steps, Sz, Sy, Sx)")
    if spacetime.shape[0] < 2:
        return np.zeros((0, *spacetime.shape[1:]), dtype=bool)

    s_lo, s_hi = survive
    b_lo, b_hi = birth
    prev = spacetime[:-1].astype(np.int32)
    actual_next = spacetime[1:].astype(np.uint8)

    neighbor_count = np.zeros_like(prev)
    for dz in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dz == 0 and dy == 0 and dx == 0:
                    continue
                neighbor_count += np.roll(np.roll(np.roll(prev, -dz, axis=1), -dy, axis=2), -dx, axis=3)

    alive = prev.astype(bool)
    predicted = np.where(
        alive,
        ((neighbor_count >= s_lo) & (neighbor_count <= s_hi)).astype(np.uint8),
        ((neighbor_count >= b_lo) & (neighbor_count <= b_hi)).astype(np.uint8),
    )
    return predicted != actual_next


def rule_consistency_rate_3d(
    spacetime: np.ndarray,
    survive: tuple[int, int],
    birth: tuple[int, int],
) -> float:
    mask = rule_consistency_mask_3d(spacetime, survive, birth)
    if mask.size == 0:
        return 0.0
    return float(mask.mean())
