"""N-dimensional relative-periodic repair for 2D and 3D cellular automata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from scipy import ndimage

from .coding import combinatorial_repair_bits, lz4_mask_bits, run_length_bits, template_bits


@dataclass(slots=True)
class RelativePeriodicFitND:
    """Relative-periodic fit for an N-dimensional CA spacetime."""
    shift: tuple[int, ...]       # spatial shift vector (one per spatial dim)
    period: int                  # temporal period
    background: np.ndarray
    defect_mask: np.ndarray
    defect_sites: int
    total_sites: int
    defect_rate: float
    combinatorial_bits: float
    run_length_bits: int
    lz4_bits: int
    template_bits: int = 0
    mdl_bits: int = 0           # template_bits + run_length_bits
    rule_error: float | None = None

    def to_record(self) -> dict[str, float | int | None]:
        rec: dict[str, float | int | None] = {
            "period": self.period,
        }
        for i, s in enumerate(self.shift):
            rec[f"shift_{i}"] = s
        rec.update({
            "defect_sites": self.defect_sites,
            "total_sites": self.total_sites,
            "defect_rate": self.defect_rate,
            "combinatorial_bits": self.combinatorial_bits,
            "run_length_bits": self.run_length_bits,
            "lz4_bits": self.lz4_bits,
            "template_bits": self.template_bits,
            "mdl_bits": self.mdl_bits,
            "rule_error": self.rule_error,
        })
        return rec


def component_labels_nd(
    shape: tuple[int, ...],
    shift: tuple[int, ...],
    period: int,
) -> np.ndarray:
    """Label each spacetime site by its relative-periodic orbit class.

    shape : (steps, *spatial_dims)
    shift : spatial shift vector (length = number of spatial dims)
    period : temporal period

    The constraint is:
        B[t + p, (x0 + s0) mod D0, (x1 + s1) mod D1, ...] = B[t, x0, x1, ...]
    """
    if period < 1:
        raise ValueError("period must be >= 1")
    steps = shape[0]
    spatial_dims = shape[1:]
    n_spatial = len(spatial_dims)
    if len(shift) != n_spatial:
        raise ValueError(f"shift has {len(shift)} components but spacetime has {n_spatial} spatial dims")

    t = np.arange(steps, dtype=np.int64)
    residue = t % period
    orbit_step = t // period

    # Build index arrays for each dimension
    # Time residue determines the "template row"
    # Spatial start position is (x_i - orbit_step * shift_i) mod dim_i
    coords = np.meshgrid(
        np.arange(steps, dtype=np.int64),
        *[np.arange(d, dtype=np.int64) for d in spatial_dims],
        indexing="ij",
    )
    t_grid = coords[0]
    res_grid = t_grid % period
    ostep_grid = t_grid // period

    label = res_grid.copy()
    multiplier = period
    for i, (dim_size, s) in enumerate(zip(spatial_dims, shift)):
        start = (coords[i + 1] - ostep_grid * s) % dim_size
        label = label + start * multiplier
        multiplier *= dim_size

    return label.astype(np.int32)


def _majority_binary_by_labels_nd(
    spacetime: np.ndarray,
    labels: np.ndarray,
    n_labels: int,
) -> np.ndarray:
    flat_labels = labels.ravel()
    flat_values = spacetime.ravel().astype(np.int64)
    totals = np.bincount(flat_labels, minlength=n_labels)
    ones = np.bincount(flat_labels, weights=flat_values, minlength=n_labels)
    majority_values = (2 * ones >= totals).astype(np.uint8)
    return majority_values[labels]


def fit_relative_periodic_background_nd(
    spacetime: np.ndarray,
    shift: tuple[int, ...],
    period: int,
    *,
    rule_error_fn=None,
) -> RelativePeriodicFitND:
    """Project an N-dimensional binary spacetime onto the nearest relative-periodic background.

    Parameters
    ----------
    spacetime : array of shape (steps, *spatial_dims), binary
    shift : spatial shift vector
    period : temporal period
    rule_error_fn : optional callable(background) -> float for rule consistency
    """
    if spacetime.ndim < 2:
        raise ValueError("spacetime must be at least 2D (time + spatial)")
    if np.any((spacetime != 0) & (spacetime != 1)):
        raise ValueError("spacetime must be binary")

    spatial_dims = spacetime.shape[1:]
    if len(shift) != len(spatial_dims):
        raise ValueError(f"shift has {len(shift)} components but spacetime has {len(spatial_dims)} spatial dims")

    labels = component_labels_nd(spacetime.shape, shift=shift, period=period)
    n_labels = period
    for d in spatial_dims:
        n_labels *= d

    background = _majority_binary_by_labels_nd(spacetime.astype(np.uint8), labels, n_labels)
    defect_mask = spacetime.astype(np.uint8) != background
    defect_sites = int(defect_mask.sum())
    total_sites = int(defect_mask.size)
    rule_error = None if rule_error_fn is None else rule_error_fn(background)

    rl_bits = run_length_bits(defect_mask)
    t_bits = template_bits(period, spatial_dims)
    mdl = t_bits + rl_bits

    return RelativePeriodicFitND(
        shift=tuple(int(s) for s in shift),
        period=int(period),
        background=background.astype(np.uint8),
        defect_mask=defect_mask,
        defect_sites=defect_sites,
        total_sites=total_sites,
        defect_rate=defect_sites / total_sites if total_sites > 0 else 0.0,
        combinatorial_bits=combinatorial_repair_bits(total_sites, defect_sites, alphabet_size=2),
        run_length_bits=rl_bits,
        lz4_bits=lz4_mask_bits(defect_mask),
        template_bits=t_bits,
        mdl_bits=mdl,
        rule_error=rule_error,
    )


def scan_relative_periodicity_nd(
    spacetime: np.ndarray,
    shift_ranges: Sequence[Iterable[int]],
    periods: Iterable[int],
    *,
    rule_error_fn=None,
) -> tuple[pd.DataFrame, dict[tuple, RelativePeriodicFitND]]:
    """Scan an N-D spacetime across a grid of (shift_vector, period) pairs.

    Parameters
    ----------
    spacetime : (steps, *spatial_dims)
    shift_ranges : one iterable of shifts per spatial dimension
    periods : iterable of periods to scan
    rule_error_fn : optional callable(background) -> float
    """
    import itertools

    shift_lists = [list(sr) for sr in shift_ranges]
    period_list = list(periods)

    fits: dict[tuple, RelativePeriodicFitND] = {}
    records: list[dict] = []

    for period in period_list:
        for shift_combo in itertools.product(*shift_lists):
            fit = fit_relative_periodic_background_nd(
                spacetime,
                shift=shift_combo,
                period=period,
                rule_error_fn=rule_error_fn,
            )
            key = (shift_combo, period)
            fits[key] = fit
            records.append(fit.to_record())

    frame = pd.DataFrame.from_records(records)
    sort_cols = ["period"] + [c for c in frame.columns if c.startswith("shift_")]
    return frame.sort_values(sort_cols).reset_index(drop=True), fits


def extract_components_nd(defect_mask: np.ndarray, *, min_size: int = 1) -> tuple[np.ndarray, int]:
    """Label connected defect components with full connectivity in N dimensions."""
    ndim = defect_mask.ndim
    structure = np.ones((3,) * ndim, dtype=np.uint8)
    labels, num_labels = ndimage.label(defect_mask.astype(np.uint8), structure=structure)
    if min_size <= 1:
        return labels, int(num_labels)

    counts = np.bincount(labels.ravel())
    keep = {label for label, count in enumerate(counts) if label != 0 and count >= min_size}
    filtered = np.where(np.isin(labels, list(keep)), labels, 0)
    return filtered, len(keep)


def summarise_components_nd(labels: np.ndarray) -> pd.DataFrame:
    """Summarise connected components from an N-D defect mask."""
    rows: list[dict] = []
    for label_val in np.unique(labels):
        if label_val == 0:
            continue
        coords = np.argwhere(labels == label_val)
        if coords.size == 0:
            continue
        row: dict = {"label": int(label_val), "size": int(coords.shape[0])}
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        for i in range(coords.shape[1]):
            dim_name = ["t", "x", "y", "z"][i] if i < 4 else f"d{i}"
            row[f"{dim_name}_min"] = int(mins[i])
            row[f"{dim_name}_max"] = int(maxs[i])
            row[f"{dim_name}_span"] = int(maxs[i] - mins[i] + 1)
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame.from_records(rows).sort_values(["size"], ascending=False).reset_index(drop=True)
