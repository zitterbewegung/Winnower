from __future__ import annotations

import math
from typing import Iterable

import lz4.frame
import numpy as np
from scipy.special import gammaln


def log2_binomial(n: int, k: int) -> float:
    """Stable base-2 log of n choose k."""
    if k < 0 or k > n:
        raise ValueError("k must satisfy 0 <= k <= n")
    if k == 0 or k == n:
        return 0.0
    return float((gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)) / math.log(2.0))


def combinatorial_repair_bits(total_sites: int, defect_sites: int, alphabet_size: int = 2) -> float:
    """Idealized repair codelength assuming an incompressible defect mask."""
    bits = log2_binomial(int(total_sites), int(defect_sites))
    if alphabet_size > 2:
        bits += defect_sites * math.log2(alphabet_size - 1)
    return float(bits)


def gamma_bits(n: int) -> int:
    """Bit length of Elias-gamma coding, simplified for positive integers."""
    if n <= 1:
        return 1
    return 2 * int(math.floor(math.log2(int(n)))) + 1


def run_length_bits(mask: np.ndarray) -> int:
    """Simple structured-mask proxy based on run-length coding."""
    flat = np.ravel(mask).astype(np.uint8)
    if flat.size == 0:
        return 0
    changes = np.flatnonzero(flat[1:] != flat[:-1]) + 1
    boundaries = np.concatenate(([0], changes, [flat.size]))
    runs = np.diff(boundaries)
    return int(1 + sum(gamma_bits(int(run)) for run in runs))


def lz4_mask_bits(mask: np.ndarray, compression_level: int = 12) -> int:
    """Practical compressor proxy for the defect mask."""
    packed = np.packbits(np.ravel(mask).astype(np.uint8))
    payload = packed.tobytes()
    compressed = lz4.frame.compress(payload, compression_level=compression_level)
    return int(8 * len(compressed))


def template_bits_raw(period: int, spatial_shape: tuple[int, ...]) -> int:
    """Raw template size: ``period * prod(spatial_shape)`` free binary values."""
    n = period
    for d in spatial_shape:
        n *= d
    return n


def template_bits_nml(period: int, spatial_shape: tuple[int, ...], steps: int) -> float:
    """MDL-motivated parametric penalty for the background template.

    Each of the ``k = period * prod(spatial_shape)`` template parameters is
    estimated from ``steps / period`` observations by majority vote.  The
    penalty ``(k / 2) * log2(n_obs)`` is the asymptotic NML parametric
    complexity for *k* Bernoulli parameters.  Our template values are binary
    choices rather than continuous Bernoulli rates, so this is an
    *approximation* — it works as a complexity penalty but is not exact NML.
    It grows logarithmically with *T*, so model selection stabilizes.
    """
    k = period
    for d in spatial_shape:
        k *= d
    n_obs = max(steps / period, 1)
    return k / 2.0 * math.log2(n_obs)


# Keep old name as alias for backwards compat in to_record
template_bits = template_bits_raw


def mdl_total_bits(
    period: int,
    spatial_shape: tuple[int, ...],
    steps: int,
    defect_mask: np.ndarray,
    defect_encoding: str = "run_length",
) -> tuple[float, int, float]:
    """Two-part MDL score: NML template complexity + defect encoding cost.

    Returns (template_cost, defect_cost, total).
    """
    t_bits = template_bits_nml(period, spatial_shape, steps)
    if defect_encoding == "run_length":
        d_bits = run_length_bits(defect_mask)
    elif defect_encoding == "lz4":
        d_bits = lz4_mask_bits(defect_mask)
    else:
        raise ValueError(f"Unknown encoding: {defect_encoding}")
    return t_bits, d_bits, t_bits + d_bits
