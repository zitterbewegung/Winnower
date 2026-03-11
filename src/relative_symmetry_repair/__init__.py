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
from .ca2d import random_initial_grid, simulate_2d, LIFE_RULES
from .ca3d import random_initial_volume, simulate_3d, RULES_3D
from .repair_nd import (
    RelativePeriodicFitND,
    component_labels_nd,
    fit_relative_periodic_background_nd,
    scan_relative_periodicity_nd,
    extract_components_nd,
    summarise_components_nd,
)
from .selection import (
    PeriodScore,
    ResidualDiagnostics,
    SelectionResult,
    SelectionStatus,
    select_period,
    select_period_nd,
    analyze_residual,
    selection_summary,
)

__all__ = [
    # 1D ECA
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
    # 2D CA
    "LIFE_RULES",
    "random_initial_grid",
    "simulate_2d",
    # 3D CA
    "RULES_3D",
    "random_initial_volume",
    "simulate_3d",
    # N-D repair
    "RelativePeriodicFitND",
    "component_labels_nd",
    "fit_relative_periodic_background_nd",
    "scan_relative_periodicity_nd",
    "extract_components_nd",
    "summarise_components_nd",
    # Selection (period-first)
    "PeriodScore",
    "ResidualDiagnostics",
    "SelectionResult",
    "SelectionStatus",
    "select_period",
    "select_period_nd",
    "analyze_residual",
    "selection_summary",
]
