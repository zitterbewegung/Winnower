from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from .coding import bernoulli_nml_complexity_single, resolve_nml_mode


@dataclass(slots=True)
class OrbitReduction:
    """Grouped orbit statistics and derived candidate score terms."""

    class_sizes: np.ndarray
    ones_per_class: np.ndarray
    majority_bits: np.ndarray
    background_flat: np.ndarray
    defect_flat: np.ndarray
    defect_sites: int
    nll_bits: float
    nml_complexity: float
    nml_bits: float


@dataclass(slots=True)
class PeriodOrbitCache:
    """Per-period orbit metadata reused across all shifts."""

    period: int
    residue_flat: np.ndarray
    orbit_step_flat: np.ndarray
    class_sizes: np.ndarray
    class_sizes_float: np.ndarray
    complexity_by_mode: dict[str, float] = field(default_factory=dict)

    def complexity(self, mode: str) -> float:
        nml_mode = resolve_nml_mode(mode=mode)
        cached = self.complexity_by_mode.get(nml_mode)
        if cached is not None:
            return cached
        value = float(
            sum(
                bernoulli_nml_complexity_single(int(size), mode=nml_mode)
                for size in self.class_sizes
            )
        )
        self.complexity_by_mode[nml_mode] = value
        return value


def residue_class_counts(steps: int, period: int) -> np.ndarray:
    """Exact orbit-class sizes induced by time residues for a given period."""
    counts = np.full(int(period), int(steps) // int(period), dtype=np.int64)
    counts[: int(steps) % int(period)] += 1
    return counts


def class_sizes_1d(shape: tuple[int, int], period: int) -> np.ndarray:
    """Return class sizes in the public 1D label order: residue-major."""
    steps, width = shape
    return np.repeat(residue_class_counts(steps, period), int(width))


def class_sizes_nd(shape: tuple[int, ...], period: int) -> np.ndarray:
    """Return class sizes in the public N-D label order: residue-minor."""
    steps = int(shape[0])
    spatial_volume = int(np.prod(shape[1:], dtype=np.int64))
    return np.tile(residue_class_counts(steps, period), spatial_volume)


def orbit_nll_from_class_counts(
    class_sizes: np.ndarray,
    ones_per_class: np.ndarray,
) -> float:
    """Bernoulli orbit NLL computed from grouped counts."""
    class_sizes_float = np.asarray(class_sizes, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        theta = np.where(class_sizes_float > 0, ones_per_class / class_sizes_float, 0.0)

    h = np.zeros_like(theta)
    interior = (theta > 0.0) & (theta < 1.0)
    h[interior] = (
        -theta[interior] * np.log2(theta[interior])
        - (1.0 - theta[interior]) * np.log2(1.0 - theta[interior])
    )
    return float(np.sum(class_sizes_float * h))


def reduce_binary_spacetime_by_orbits(
    binary_flat: np.ndarray,
    orbit_ids: np.ndarray,
    class_sizes: np.ndarray,
    *,
    nml_mode: str,
    nml_complexity: float | None = None,
    background_out: np.ndarray | None = None,
    defect_out: np.ndarray | None = None,
) -> OrbitReduction:
    """Reduce a flattened binary spacetime by orbit ids in a single hot pass."""
    binary_flat = np.asarray(binary_flat, dtype=np.uint8)
    ones_per_class = np.bincount(
        np.asarray(orbit_ids, dtype=np.int32),
        weights=binary_flat,
        minlength=int(class_sizes.size),
    )
    majority_bits = (2.0 * ones_per_class >= class_sizes).astype(np.uint8)

    if background_out is None:
        background_flat = majority_bits[np.asarray(orbit_ids, dtype=np.int32)]
    else:
        np.take(majority_bits, orbit_ids, out=background_out)
        background_flat = background_out

    if defect_out is None:
        defect_flat = np.bitwise_xor(binary_flat, background_flat)
    else:
        np.bitwise_xor(binary_flat, background_flat, out=defect_out)
        defect_flat = defect_out

    complexity = (
        float(nml_complexity)
        if nml_complexity is not None
        else float(
            sum(
                bernoulli_nml_complexity_single(int(size), mode=resolve_nml_mode(mode=nml_mode))
                for size in class_sizes
            )
        )
    )
    nll = orbit_nll_from_class_counts(class_sizes, ones_per_class)
    return OrbitReduction(
        class_sizes=np.asarray(class_sizes, dtype=np.int64),
        ones_per_class=ones_per_class,
        majority_bits=majority_bits,
        background_flat=background_flat,
        defect_flat=defect_flat,
        defect_sites=int(np.sum(defect_flat, dtype=np.int64)),
        nll_bits=nll,
        nml_complexity=complexity,
        nml_bits=nll + complexity,
    )


class RelativePeriodicOrbitWorkspace:
    """Reusable orbit-id workspace for candidate scans.

    The flattened layout is always C-order on the input spacetime. For 1D
    scans we preserve the public residue-major label numbering used by
    ``component_labels``. For N-D scans we preserve the public residue-minor
    numbering used by ``component_labels_nd``.
    """

    def __init__(
        self,
        spacetime: np.ndarray,
        *,
        residue_major: bool,
    ) -> None:
        self.binary = np.ascontiguousarray(spacetime, dtype=np.uint8)
        self.flat = self.binary.reshape(-1)
        self.shape = tuple(int(dim) for dim in self.binary.shape)
        self.steps = int(self.shape[0])
        self.spatial_dims = tuple(int(dim) for dim in self.shape[1:])
        self.spatial_volume = int(np.prod(self.spatial_dims, dtype=np.int64))
        self.residue_major = bool(residue_major)

        coords = np.indices(self.shape, dtype=np.int32).reshape(self.binary.ndim, -1)
        self._time_flat = coords[0]
        self._spatial_coords = tuple(coords[axis] for axis in range(1, coords.shape[0]))
        self._period_cache: dict[int, PeriodOrbitCache] = {}

        self._orbit_ids = np.empty(self.flat.size, dtype=np.int32)
        self._spatial_linear = np.empty(self.flat.size, dtype=np.int32)
        self._work = np.empty(self.flat.size, dtype=np.int32)
        self._background_flat = np.empty(self.flat.size, dtype=np.uint8)
        self._defect_flat = np.empty(self.flat.size, dtype=np.uint8)

    def _get_period_cache(self, period: int) -> PeriodOrbitCache:
        period = int(period)
        cached = self._period_cache.get(period)
        if cached is not None:
            return cached

        if period < 1:
            raise ValueError("period must be >= 1")

        residue_flat = np.remainder(self._time_flat, period)
        orbit_step_flat = np.floor_divide(self._time_flat, period)
        residue_counts = residue_class_counts(self.steps, period)
        if self.residue_major:
            class_sizes = np.repeat(residue_counts, self.spatial_volume)
        else:
            class_sizes = np.tile(residue_counts, self.spatial_volume)

        cached = PeriodOrbitCache(
            period=period,
            residue_flat=residue_flat,
            orbit_step_flat=orbit_step_flat,
            class_sizes=class_sizes,
            class_sizes_float=class_sizes.astype(np.float64),
        )
        self._period_cache[period] = cached
        return cached

    def orbit_ids(
        self,
        shift: Sequence[int],
        period: int,
    ) -> tuple[np.ndarray, PeriodOrbitCache]:
        cache = self._get_period_cache(period)
        shift_tuple = tuple(int(component) for component in shift)
        if len(shift_tuple) != len(self.spatial_dims):
            raise ValueError(
                f"shift has {len(shift_tuple)} components but spacetime has "
                f"{len(self.spatial_dims)} spatial dims"
            )

        multiplier = 1
        for axis, (coord, dim_size, shift_component) in enumerate(
            zip(self._spatial_coords, self.spatial_dims, shift_tuple)
        ):
            np.multiply(cache.orbit_step_flat, shift_component, out=self._work)
            np.subtract(coord, self._work, out=self._work)
            np.mod(self._work, dim_size, out=self._work)

            if axis == 0:
                np.copyto(self._spatial_linear, self._work)
            else:
                np.multiply(self._work, multiplier, out=self._orbit_ids)
                np.add(self._spatial_linear, self._orbit_ids, out=self._spatial_linear)
            multiplier *= dim_size

        if self.residue_major:
            np.multiply(cache.residue_flat, self.spatial_volume, out=self._orbit_ids)
            np.add(self._orbit_ids, self._spatial_linear, out=self._orbit_ids)
        else:
            np.multiply(self._spatial_linear, int(period), out=self._orbit_ids)
            np.add(self._orbit_ids, cache.residue_flat, out=self._orbit_ids)
        return self._orbit_ids, cache

    def evaluate_candidate(
        self,
        shift: Sequence[int],
        period: int,
        *,
        nml_mode: str,
    ) -> OrbitReduction:
        orbit_ids, cache = self.orbit_ids(shift, period)
        return reduce_binary_spacetime_by_orbits(
            self.flat,
            orbit_ids,
            cache.class_sizes,
            nml_mode=nml_mode,
            nml_complexity=cache.complexity(nml_mode),
            background_out=self._background_flat,
            defect_out=self._defect_flat,
        )
