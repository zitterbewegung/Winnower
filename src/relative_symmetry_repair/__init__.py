"""Relative symmetry-repair analysis for cellular automata."""

from .eca import random_initial_state, simulate_eca, rule_consistency_mask, rule_consistency_rate
from .repair import (
    ReflectionFit,
    RelativePeriodicFit,
    component_labels,
    fit_reflection_symmetric_state,
    fit_relative_periodic_background,
    scan_relative_periodicity,
    extract_components,
    summarise_components,
)

__all__ = [
    "ReflectionFit",
    "RelativePeriodicFit",
    "component_labels",
    "extract_components",
    "fit_reflection_symmetric_state",
    "fit_relative_periodic_background",
    "random_initial_state",
    "rule_consistency_mask",
    "rule_consistency_rate",
    "scan_relative_periodicity",
    "simulate_eca",
    "summarise_components",
]
