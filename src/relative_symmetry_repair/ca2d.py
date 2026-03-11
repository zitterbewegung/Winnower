"""2D cellular automaton simulation (totalistic outer-totalistic rules on a torus)."""
from __future__ import annotations

import re

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


@njit(cache=True)
def _simulate_life_general_numba(
    initial: np.ndarray,
    steps: int,
    birth_lut: np.ndarray,
    survive_lut: np.ndarray,
) -> np.ndarray:
    """Simulate an arbitrary Life-like CA using lookup tables on a torus.

    birth_lut[n] = 1 if a dead cell with n neighbors is born.
    survive_lut[n] = 1 if a live cell with n neighbors survives.
    Both are length-9 arrays (neighbor counts 0..8).
    """
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
                    cur[y, x] = survive_lut[total]
                else:
                    cur[y, x] = birth_lut[total]
    return spacetime


def parse_rulestring(rulestring: str) -> tuple[list[int], list[int]]:
    """Parse a B/S rulestring like 'B36/S23' into (birth_counts, survive_counts).

    Returns sorted lists of neighbor counts (each in 0..8).
    """
    m = re.match(r'[Bb](\d*)\s*/\s*[Ss](\d*)', rulestring)
    if not m:
        raise ValueError(f"Cannot parse rulestring: {rulestring!r}. Expected format: B.../S...")
    birth_str, survive_str = m.group(1), m.group(2)
    birth = sorted(set(int(c) for c in birth_str)) if birth_str else []
    survive = sorted(set(int(c) for c in survive_str)) if survive_str else []
    for n in birth + survive:
        if not (0 <= n <= 8):
            raise ValueError(f"Neighbor count must be 0-8, got {n}")
    return birth, survive


def _make_luts(birth: list[int], survive: list[int]) -> tuple[np.ndarray, np.ndarray]:
    """Build lookup tables from birth/survive neighbor count lists."""
    birth_lut = np.zeros(9, dtype=np.uint8)
    survive_lut = np.zeros(9, dtype=np.uint8)
    for n in birth:
        birth_lut[n] = 1
    for n in survive:
        survive_lut[n] = 1
    return birth_lut, survive_lut


# Predefined 2D rules as (survive_lo, survive_hi, birth_lo, birth_hi)
# NOTE: These use contiguous ranges. For rules with non-contiguous B/S sets
# (e.g., B36/S23), use simulate_2d_general() with a rulestring instead.
LIFE_RULES: dict[str, tuple[int, int, int, int]] = {
    "life": (2, 3, 3, 3),         # Conway's Game of Life B3/S23
    "highlife": (2, 3, 3, 6),     # B36/S23 — APPROXIMATE (includes B45)
    "seeds": (9, 9, 2, 2),        # B2/S (nothing survives)
    "daynight": (3, 6, 3, 6),     # B3678/S34678 — APPROXIMATE
    "diamoeba": (5, 8, 5, 8),     # B5678/S5678
}


def simulate_2d(
    initial: np.ndarray,
    steps: int,
    rule: str = "life",
    survive: tuple[int, int] | None = None,
    birth: tuple[int, int] | None = None,
) -> np.ndarray:
    """Simulate a 2D totalistic CA on a torus (contiguous range version).

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

    Notes
    -----
    For rules with non-contiguous birth/survive sets, use simulate_2d_general().
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


def simulate_2d_general(
    initial: np.ndarray,
    steps: int,
    rulestring: str | None = None,
    birth: list[int] | None = None,
    survive: list[int] | None = None,
) -> np.ndarray:
    """Simulate an arbitrary Life-like 2D CA on a torus.

    Accepts any valid B/S rulestring (e.g., 'B36/S23', 'B3678/S34678')
    with non-contiguous birth/survive sets.

    Parameters
    ----------
    initial : 2D uint8 array (H, W)
    steps : number of time steps (including initial)
    rulestring : B/S notation string, e.g., 'B3/S23'
    birth : list of neighbor counts for birth (alternative to rulestring)
    survive : list of neighbor counts for survival (alternative to rulestring)

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

    if rulestring is not None:
        birth, survive = parse_rulestring(rulestring)
    elif birth is None or survive is None:
        raise ValueError("Provide either rulestring or both birth and survive lists")

    birth_lut, survive_lut = _make_luts(birth, survive)

    return _simulate_life_general_numba(
        initial.astype(np.uint8), int(steps),
        birth_lut, survive_lut,
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
