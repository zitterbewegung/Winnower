from __future__ import annotations

import functools
import math
from typing import Iterable

import lz4.frame
import numpy as np
from scipy.special import gammaln


# ── Exact Bernoulli NML for finite samples ────────────────────────────────────

# Cutoff: use exact computation for n <= this, asymptotic for n > this.
# At n=200 the asymptotic approximation error is <0.01 bits per class,
# negligible compared to the O(1) constant in the asymptotic expansion.
EXACT_NML_CUTOFF = 200


@functools.lru_cache(maxsize=4096)
def _exact_bernoulli_regret(n: int) -> float:
    """Exact Bernoulli NML parametric complexity for sample size n, in bits.

    This is log2 of the Shtarkov normalizing constant:
        C(n) = sum_{k=0}^{n} binom(n, k) * (k/n)^k * ((n-k)/n)^(n-k)

    where the k=0 and k=n terms contribute 1 each (using 0^0 = 1).

    For n=0 or n=1, the complexity is 0 (no free parameter to estimate).
    """
    if n <= 1:
        return 0.0
    # Work in log space for numerical stability
    # Each term: binom(n, k) * (k/n)^k * ((n-k)/n)^(n-k)
    # log2(term) = log2_binom(n,k) + k*log2(k/n) + (n-k)*log2((n-k)/n)
    log2_terms = np.empty(n + 1, dtype=np.float64)
    for k in range(n + 1):
        lb = float((gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)) / math.log(2.0))
        if k == 0 or k == n:
            # (k/n)^k = 0^0 = 1, or ((n-k)/n)^(n-k) = 0^0 = 1
            log2_terms[k] = lb  # binom(n,0) = binom(n,n) = 1, rest = 1
        else:
            kf = float(k)
            nf = float(n)
            log2_terms[k] = lb + kf * math.log2(kf / nf) + (nf - kf) * math.log2((nf - kf) / nf)
    # Log-sum-exp in base 2
    max_val = float(np.max(log2_terms))
    shifted = log2_terms - max_val
    total = float(np.sum(np.power(2.0, shifted)))
    return max_val + math.log2(total)


def bernoulli_nml_complexity_single(n: int) -> float:
    """NML parametric complexity for a single Bernoulli class with n observations.

    Uses exact computation for n <= EXACT_NML_CUTOFF, asymptotic (½ log₂ n)
    for larger n. The asymptotic approximation omits the O(1) constant
    (½ log(π/2) ≈ 0.326 bits), which does not affect model selection.
    """
    if n <= 1:
        return 0.0
    if n <= EXACT_NML_CUTOFF:
        return _exact_bernoulli_regret(n)
    return 0.5 * math.log2(n)


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
    *,
    exact: bool = True,
) -> float:
    """NML parametric complexity: Σ_j complexity(n_j).

    When ``exact=True`` (default), uses exact Bernoulli NML for small
    orbit classes (n_j ≤ EXACT_NML_CUTOFF) and asymptotic (½ log₂ n_j)
    for larger ones. When ``exact=False``, uses asymptotic throughout.

    For each orbit class j with n_j observations, the Bernoulli NML
    normalizing constant contributes (1/2) log2(n_j) + O(1) bits
    asymptotically. The exact computation sums binomial coefficients
    weighted by MLE likelihoods (Shtarkov normalizer).
    """
    flat_labels = labels.ravel()
    totals = np.bincount(flat_labels, minlength=n_labels).astype(np.int64)
    if exact:
        return float(sum(bernoulli_nml_complexity_single(int(n)) for n in totals))
    valid = totals[totals > 1].astype(np.float64)
    if valid.size == 0:
        return 0.0
    return float(0.5 * np.sum(np.log2(valid)))


def nml_score_bits(
    spacetime: np.ndarray,
    labels: np.ndarray,
    n_labels: int,
    *,
    exact: bool = True,
) -> tuple[float, float, float]:
    """Bernoulli NML score = NLL + parametric complexity.

    Returns (nll_bits, complexity_bits, total_nml_bits).

    When ``exact=True`` (default), uses finite-sample-corrected NML
    complexity for small orbit classes (n_j ≤ EXACT_NML_CUTOFF) and
    asymptotic for larger ones. When ``exact=False``, uses asymptotic
    throughout (legacy behavior).
    """
    nll = orbit_nll_bits(spacetime, labels, n_labels)
    comp = nml_complexity_bits(labels, n_labels, exact=exact)
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
