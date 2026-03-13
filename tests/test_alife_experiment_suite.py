from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from relative_symmetry_repair.experiment_suite import (
    ResumeTable,
    eca_case,
    generate_paper_reports,
    make_null_controls,
    make_search_config,
    period_first_selection_from_frame,
    run_null_controls_suite,
    run_seed_stability_suite,
)


def test_period_first_selection_from_frame_uses_period_first_ordering() -> None:
    frame = pd.DataFrame(
        [
            {"period": 1, "shift": -1, "nml_bits": 9.7, "nll_bits": 8.0, "nml_complexity": 1.7, "defect_rate": 0.11},
            {"period": 1, "shift": 0, "nml_bits": 9.5, "nll_bits": 7.9, "nml_complexity": 1.6, "defect_rate": 0.10},
            {"period": 2, "shift": -1, "nml_bits": 8.4, "nll_bits": 6.9, "nml_complexity": 1.5, "defect_rate": 0.07},
            {"period": 2, "shift": 1, "nml_bits": 8.0, "nll_bits": 6.7, "nml_complexity": 1.3, "defect_rate": 0.06},
            {"period": 3, "shift": -1, "nml_bits": 8.3, "nll_bits": 6.8, "nml_complexity": 1.5, "defect_rate": 0.07},
            {"period": 3, "shift": 1, "nml_bits": 8.1, "nll_bits": 6.9, "nml_complexity": 1.2, "defect_rate": 0.07},
        ]
    )

    result = period_first_selection_from_frame(frame)

    assert result.selected_period == 2
    assert result.selected_shift == 1
    assert abs(result.margin_bits - 0.1) < 1e-9
    assert result.runner_up_period == 3


def test_null_controls_preserve_shape_and_binary_dtype() -> None:
    rng = np.random.default_rng(7)
    spacetime = (rng.random((5, 4, 3)) < 0.4).astype(np.uint8)

    controls = make_null_controls(spacetime, seed=13)

    assert set(controls) == {"original", "time_shuffled", "space_shuffled", "bernoulli_iid"}
    for control in controls.values():
        assert control.shape == spacetime.shape
        assert control.dtype == np.uint8
        assert set(np.unique(control)).issubset({0, 1})


def test_small_null_controls_run_writes_summary_csvs(tmp_path: Path) -> None:
    output_root = tmp_path / "outputs"
    case = eca_case(
        30,
        width=24,
        density=0.5,
        horizons=(12,),
        search=make_search_config(1, shift_radius=1, max_period=3, label="tiny_1d"),
    )

    run_null_controls_suite(
        output_root=output_root,
        cases=[case],
        base_seed=5,
        n_seeds=1,
        resume=False,
        save_decompositions=False,
    )

    rule_level_path = output_root / "null_controls" / "null_controls_rule_level.csv"
    summary_path = output_root / "null_controls" / "null_controls_summary.csv"
    assert rule_level_path.exists()
    assert summary_path.exists()

    rule_level = pd.read_csv(rule_level_path)
    assert set(rule_level["control_type"]) == {"original", "time_shuffled", "space_shuffled", "bernoulli_iid"}
    assert {"selected_period", "selected_shift_str", "margin_bits", "selected_defect_rate"}.issubset(rule_level.columns)


def test_small_seed_stability_run_and_paper_reports(tmp_path: Path) -> None:
    output_root = tmp_path / "outputs"
    paper_dir = tmp_path / "paper"
    case = eca_case(
        54,
        width=24,
        density=0.5,
        horizons=(8, 12),
        search=make_search_config(1, shift_radius=1, max_period=3, label="tiny_stability"),
    )

    run_seed_stability_suite(
        output_root=output_root,
        cases=[case],
        base_seed=9,
        n_seeds=2,
        resume=False,
    )
    generate_paper_reports(output_root=output_root, paper_dir=paper_dir)

    runs_path = output_root / "seed_stability" / "seed_stability_runs.csv"
    summary_path = output_root / "seed_stability" / "seed_stability_summary.csv"
    report_path = paper_dir / "alife_experiment_summary.md"
    tables_path = paper_dir / "alife_table_snippets.md"

    assert runs_path.exists()
    assert summary_path.exists()
    assert report_path.exists()
    assert tables_path.exists()
    assert "Seed stability" in report_path.read_text()


def test_resume_table_loads_existing_csv_keys(tmp_path: Path) -> None:
    path = tmp_path / "runs.csv"
    pd.DataFrame(
        [
            {"rule": "ECA-30", "seed": 11, "control_type": "original", "value": 1.0},
        ]
    ).to_csv(path, index=False)

    table = ResumeTable(
        path,
        key_columns=("rule", "seed", "control_type"),
        resume=True,
    )

    assert table.has_key({"rule": "ECA-30", "seed": 11, "control_type": "original"})
