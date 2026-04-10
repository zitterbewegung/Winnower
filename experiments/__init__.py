"""Compatibility package for experiment entrypoints.

Historical code and tests import modules from ``experiments.*`` while the
current scripts live under ``scripts/analysis``. Keep this thin package so
those imports continue to resolve without duplicating logic.
"""

