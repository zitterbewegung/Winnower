"""Catalogued patterns: CA orbits with an analytically known relative period.

Every experiment in this project starts from a random soup, which is fine for
surveying but leaves the selector with no case whose correct answer is known
in advance. ``scripts/alife/ground_truth_benchmark.py`` fills part of that gap
by *planting* a period and displacement in a random tile; these patterns fill
the rest, with orbits a real rule actually produces.

Each entry is a small configuration that is exactly relative-periodic under
the rule it belongs to: it satisfies

    U[t + period, x + displacement] = U[t, x]

for every ``t`` past its (zero-length) transient, so the correct fit is known
without measuring anything --- period, displacement, and a defect rate of
exactly zero. That makes them ground truth for the selector rather than one
more thing to survey.

The 3D entries are for ``3d-life`` (S4-5/B5, Bays' rule 4555). They are useful
beyond testing: seeding ``PATTERNS_3D["glider"]`` instead of a random soup
gives a permanently persistent, spatially localized, *moving* structure ---
the signature the defect-mask claim is about.

Every pattern here was found by random search and then re-verified in
isolation in a clean lattice: constant population, exact translation over the
whole run, and minimal period. ``tests/test_patterns.py`` re-checks all of
that on every run, so nothing in this catalogue is taken on trust.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Literal, Sequence

import numpy as np

__all__ = [
    "PATTERNS_3D",
    "Pattern",
    "PatternKind",
    "pattern_spacetime",
    "patterns_for_rule",
]

PatternKind = Literal["still_life", "oscillator", "spaceship"]


@dataclass(frozen=True, slots=True)
class Pattern:
    """A configuration whose orbit has a known period and displacement."""

    name: str
    rule: str
    period: int
    displacement: tuple[int, ...]
    cells: tuple[tuple[int, ...], ...]
    description: str

    @property
    def dimension(self) -> int:
        return len(self.displacement)

    @property
    def n_cells(self) -> int:
        return len(self.cells)

    @property
    def bounding_box(self) -> tuple[int, ...]:
        array = np.array(self.cells)
        return tuple(int(value) for value in (array.max(axis=0) - array.min(axis=0) + 1))

    @property
    def kind(self) -> PatternKind:
        if any(self.displacement):
            return "spaceship"
        return "still_life" if self.period == 1 else "oscillator"

    @property
    def speed(self) -> tuple[float, ...]:
        """Displacement per step, in cells per step along each axis."""
        return tuple(value / self.period for value in self.displacement)

    def volume(self, size: int | Sequence[int], offset: Sequence[int] | None = None) -> np.ndarray:
        """Render the pattern into an empty lattice.

        ``size`` is a scalar for a cubic lattice or a per-axis sequence. The
        default offset centres the pattern, which keeps a spaceship away from
        the boundary for as long as possible.
        """
        shape = (
            tuple(int(size) for _ in range(self.dimension))
            if isinstance(size, (int, np.integer))
            else tuple(int(value) for value in size)
        )
        if len(shape) != self.dimension:
            raise ValueError(f"size must have {self.dimension} axes, got {len(shape)}")
        box = self.bounding_box
        if any(extent < span for extent, span in zip(shape, box)):
            raise ValueError(f"lattice {shape} is smaller than the pattern's {box}")

        if offset is None:
            offset = tuple((extent - span) // 2 for extent, span in zip(shape, box))
        offset = tuple(int(value) for value in offset)

        array = np.array(self.cells)
        array = array - array.min(axis=0)
        volume = np.zeros(shape, dtype=np.uint8)
        for cell in array:
            volume[tuple((cell + offset) % np.array(shape))] = 1
        return volume

    def to_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "rule": self.rule,
            "kind": self.kind,
            "dimension": self.dimension,
            "period": self.period,
            "displacement": list(self.displacement),
            "n_cells": self.n_cells,
            "bounding_box": list(self.bounding_box),
            "description": self.description,
        }


#: Patterns for ``3d-life`` (S4-5/B5) on the 26-neighbour Moore neighbourhood.
#: Coordinates are ``(x, y, z)`` offsets from the pattern's bounding-box corner.
PATTERNS_3D: dict[str, Pattern] = {
    "still-life": Pattern(
        name="still-life",
        rule="3d-life",
        period=1,
        displacement=(0, 0, 0),
        cells=(
            (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 1, 0),
        ),
        description="Smallest stable configuration found: 6 cells in a 2x2x2 box.",
    ),
    "blinker": Pattern(
        name="blinker",
        rule="3d-life",
        period=2,
        displacement=(0, 0, 0),
        cells=(
            (0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 2), (1, 2, 0), (1, 2, 2), (2, 1, 1),
        ),
        description="Smallest period-2 oscillator found: 7 cells in a 3x3x3 box.",
    ),
    "oscillator-4": Pattern(
        name="oscillator-4",
        rule="3d-life",
        period=4,
        displacement=(0, 0, 0),
        cells=(
            (0, 0, 1), (0, 0, 2), (0, 1, 1), (0, 1, 2), (1, 1, 0),
            (1, 1, 3), (1, 2, 1), (1, 2, 2), (2, 1, 1), (2, 1, 2),
        ),
        description="Period-4 oscillator: 10 cells in a 3x3x4 box, no net motion.",
    ),
    "glider": Pattern(
        name="glider",
        rule="3d-life",
        period=4,
        displacement=(1, 1, 0),
        cells=(
            (0, 0, 0), (0, 0, 3), (0, 1, 1), (0, 1, 2), (1, 0, 0),
            (1, 0, 3), (1, 1, 1), (1, 1, 2), (2, 0, 1), (2, 0, 2),
        ),
        description=(
            "Period-4 spaceship: 10 cells in a 3x2x4 box, translating one cell "
            "along each of two axes every four steps (c/4, diagonal in a "
            "coordinate plane, no z-component). The rule's only known "
            "translating pattern; all others found were its images under the "
            "48 octahedral symmetries."
        ),
    ),
}


def patterns_for_rule(rule: str) -> Iterator[Pattern]:
    """Every catalogued pattern belonging to a named rule."""
    for pattern in PATTERNS_3D.values():
        if pattern.rule == rule:
            yield pattern


def pattern_spacetime(
    pattern: Pattern,
    *,
    size: int | Sequence[int],
    steps: int,
    offset: Sequence[int] | None = None,
) -> np.ndarray:
    """Simulate a catalogued pattern from its own seed.

    The result is exactly relative-periodic under
    ``(pattern.period, pattern.displacement)`` with no transient, so a fit at
    that candidate has a defect rate of exactly zero.
    """
    from .ca3d import RULES_3D, simulate_3d

    if pattern.dimension != 3:
        raise ValueError(f"{pattern.name} is {pattern.dimension}D; only 3D is supported")
    survive_lo, survive_hi, birth_lo, birth_hi = RULES_3D[pattern.rule]
    initial = pattern.volume(size, offset=offset)
    return simulate_3d(
        initial,
        steps=int(steps),
        rule="custom",
        survive=(survive_lo, survive_hi),
        birth=(birth_lo, birth_hi),
    )
