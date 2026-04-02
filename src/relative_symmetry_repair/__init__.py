"""Relative symmetry-repair analysis for cellular automata."""

from __future__ import annotations

from importlib import import_module


_EXPORT_MAP = {
    # 1D ECA
    "ReflectionFit": (".repair", "ReflectionFit"),
    "RelativePeriodicFit": (".repair", "RelativePeriodicFit"),
    "component_labels": (".repair", "component_labels"),
    "extract_components": (".repair", "extract_components"),
    "fit_reflection_symmetric_state": (".repair", "fit_reflection_symmetric_state"),
    "fit_relative_periodic_background": (".repair", "fit_relative_periodic_background"),
    "random_initial_state": (".eca", "random_initial_state"),
    "rule_consistency_mask": (".eca", "rule_consistency_mask"),
    "rule_consistency_rate": (".eca", "rule_consistency_rate"),
    "scan_relative_periodicity": (".repair", "scan_relative_periodicity"),
    "simulate_eca": (".eca", "simulate_eca"),
    "summarise_components": (".repair", "summarise_components"),
    # 2D CA
    "LIFE_RULES": (".ca2d", "LIFE_RULES"),
    "random_initial_grid": (".ca2d", "random_initial_grid"),
    "simulate_2d": (".ca2d", "simulate_2d"),
    # 3D CA
    "RULES_3D": (".ca3d", "RULES_3D"),
    "RULES_3D_DENSITY": (".ca3d", "RULES_3D_DENSITY"),
    "random_initial_volume": (".ca3d", "random_initial_volume"),
    "simulate_3d": (".ca3d", "simulate_3d"),
    # N-D repair
    "RelativePeriodicFitND": (".repair_nd", "RelativePeriodicFitND"),
    "component_labels_nd": (".repair_nd", "component_labels_nd"),
    "fit_relative_periodic_background_nd": (".repair_nd", "fit_relative_periodic_background_nd"),
    "scan_relative_periodicity_nd": (".repair_nd", "scan_relative_periodicity_nd"),
    "extract_components_nd": (".repair_nd", "extract_components_nd"),
    "summarise_components_nd": (".repair_nd", "summarise_components_nd"),
    # Selection (period-first)
    "PeriodScore": (".selection", "PeriodScore"),
    "ResidualDiagnostics": (".selection", "ResidualDiagnostics"),
    "SelectionResult": (".selection", "SelectionResult"),
    "SelectionStatus": (".selection", "SelectionStatus"),
    "select_period": (".selection", "select_period"),
    "select_period_from_scan": (".selection", "select_period_from_scan"),
    "select_period_nd": (".selection", "select_period_nd"),
    "select_period_nd_from_scan": (".selection", "select_period_nd_from_scan"),
    "analyze_residual": (".selection", "analyze_residual"),
    "selection_summary": (".selection", "selection_summary"),
}

__all__ = list(_EXPORT_MAP)


def __getattr__(name: str):
    try:
        module_name, attr_name = _EXPORT_MAP[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    value = getattr(import_module(module_name, __name__), attr_name)
    globals()[name] = value
    return value
