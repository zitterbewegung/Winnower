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
    """BIC-type parametric penalty for the background template.

    Each of the ``k = period * prod(spatial_shape)`` template parameters is
    estimated from ``steps / period`` observations by majority vote.  The
    penalty ``(k / 2) * log2(n_obs)`` is the BIC / asymptotic stochastic
    complexity for *k* Bernoulli parameters.  This is *not* exact NML: it
    omits constant terms and treats binary template values as continuous
    Bernoulli rates.  It grows logarithmically with *T*, so model selection
    stabilizes.

    Prefer ``nml_score_bits`` (NLL + per-orbit complexity) for model
    selection; this function is retained for the legacy ``mdl_bits`` score.
    """
    k = period
    for d in spatial_shape:
        k *= d
    n_obs = max(steps // period, 1)
    return k / 2.0 * math.log2(n_obs)


# Keep old name as alias for backwards compat in to_record
template_bits = template_bits_raw


# ── Asymptotic Bernoulli NML on orbit classes ────────────────────────────────

def orbit_nll_bits(
    spacetime: np.ndarray,
    labels: np.ndarray,
    n_labels: int,
) -> float:
    """Bernoulli negative log-likelihood over orbit classes, in bits.

    For each orbit class j with n_j observations and empirical frequency
    θ̂_j = n_j^(1) / n_j, the contribution is n_j * H_b(θ̂_j) where H_b is
    binary entropy.  This is the exact Bernoulli MLE data-fit term.
    """
    flat_labels = labels.ravel()
    flat_values = spacetime.ravel().astype(np.float64)
    totals = np.bincount(flat_labels, minlength=n_labels).astype(np.float64)
    ones = np.bincount(flat_labels, weights=flat_values, minlength=n_labels)

    # θ̂_j = ones_j / totals_j
    with np.errstate(divide="ignore", invalid="ignore"):
        theta = np.where(totals > 0, ones / totals, 0.0)

    # H_b(θ) = -θ log2(θ) - (1-θ) log2(1-θ)
    h = np.zeros_like(theta)
    interior = (theta > 0) & (theta < 1)
    h[interior] = (
        -theta[interior] * np.log2(theta[interior])
        - (1 - theta[interior]) * np.log2(1 - theta[interior])
    )
    return float(np.sum(totals * h))


def nml_complexity_bits(
    labels: np.ndarray,
    n_labels: int,
) -> float:
    """Asymptotic NML parametric complexity: Σ_j (1/2) log2(n_j).

    For each orbit class j with n_j observations, the Bernoulli NML
    normalizing constant contributes (1/2) log2(n_j) + O(1) bits.
    The O(1) term ((1/2) log(π/2) ≈ 0.326 bits per class) is omitted;
    this does not affect asymptotic model selection.
    """
    flat_labels = labels.ravel()
    totals = np.bincount(flat_labels, minlength=n_labels).astype(np.float64)
    valid = totals[totals > 1]  # classes with ≤1 observation have zero complexity
    if valid.size == 0:
        return 0.0
    return float(0.5 * np.sum(np.log2(valid)))


def nml_score_bits(
    spacetime: np.ndarray,
    labels: np.ndarray,
    n_labels: int,
) -> tuple[float, float, float]:
    """Asymptotic Bernoulli NML score = NLL + parametric complexity.

    Returns (nll_bits, complexity_bits, total_nml_bits).
    The score is asymptotically equivalent to the normalized maximum
    likelihood code for independent Bernoulli parameters on orbit classes,
    up to O(k) additive bits where k is the number of orbit classes.
    """
    nll = orbit_nll_bits(spacetime, labels, n_labels)
    comp = nml_complexity_bits(labels, n_labels)
    return nll, comp, nll + comp


def mdl_total_bits(
    period: int,
    spatial_shape: tuple[int, ...],
    steps: int,
    defect_mask: np.ndarray,
    defect_encoding: str = "run_length",
) -> tuple[float, int, float]:
    """Legacy two-part score: approximate penalty + defect encoding.

    Retained for backwards compatibility. Prefer nml_score_bits for
    model selection.

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
