import numpy as np

from relative_symmetry_repair.selection import select_period, selection_summary


def test_joint_shift_optimization_finds_translated_background():
    row0 = np.array([1, 0, 0, 1, 1], dtype=np.uint8)
    spacetime = np.vstack([np.roll(row0, t) for t in range(8)]).astype(np.uint8)

    zero_shift_only = select_period(spacetime, shifts=[0], periods=[1, 2], nml_mode="exact")
    joint = select_period(spacetime, shifts=[0, 1], periods=[1, 2], nml_mode="exact")

    assert zero_shift_only.selected.best_shift == 0
    assert zero_shift_only.selected.defect_rate > 0.0
    assert joint.selected.period == 1
    assert joint.selected.best_shift == 1
    assert joint.selected.defect_rate == 0.0


def test_selection_summary_exposes_shift_handling_and_score_mode():
    spacetime = np.zeros((6, 4), dtype=np.uint8)
    result = select_period(
        spacetime,
        shifts=[0],
        periods=[1, 2],
        nml_mode="asymptotic",
    )
    summary = selection_summary(result)
    assert summary["shift_handling"] == "shift_zero_only"
    assert summary["nml_mode"] == "asymptotic"
    assert summary["tie_break_rule"] == "score asc, period asc, shift lex asc"


def test_selection_summary_exposes_paper_mode_candidate_margin_and_majority_tie_break():
    spacetime = np.zeros((6, 4), dtype=np.uint8)
    result = select_period(
        spacetime,
        shifts=[0],
        periods=[1, 2],
        nml_mode="paper",
        majority_tie_break="zeros",
    )
    summary = selection_summary(result)
    assert summary["nml_mode"] == "paper"
    assert summary["resolved_nml_mode"] == "asymptotic"
    assert summary["majority_tie_break"] == "zeros"
    assert "candidate_margin_bits" in summary
    assert "period_margin_bits" in summary
    assert "candidate_runner_up_period" in summary
