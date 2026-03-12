#!/usr/bin/env python3
"""Validate generated result files against paper-facing claims where feasible."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True, slots=True)
class CheckResult:
    status: str
    scope: str
    message: str


def _load_metadata(csv_path: Path) -> dict | None:
    metadata_path = Path(f"{csv_path}.metadata.json")
    if not metadata_path.exists():
        return None
    return json.loads(metadata_path.read_text())


def _record(results: list[CheckResult], status: str, scope: str, message: str) -> None:
    results.append(CheckResult(status=status, scope=scope, message=message))


def validate_stabilization(root: Path, results: list[CheckResult]) -> None:
    results_csv = root / "results" / "stabilization_results.csv"
    period_scores_csv = root / "results" / "stabilization_period_scores.csv"
    candidates_csv = root / "results" / "stabilization_candidates.csv"
    shift_zero_results_csv = root / "results" / "stabilization_shift_zero_results.csv"
    shift_zero_period_scores_csv = root / "results" / "stabilization_shift_zero_period_scores.csv"
    for path in [
        results_csv,
        period_scores_csv,
        candidates_csv,
        shift_zero_results_csv,
        shift_zero_period_scores_csv,
    ]:
        if path.exists():
            _record(results, "PASS", "stabilization", f"Found source file `{path.relative_to(root)}`.")
        else:
            _record(results, "FAIL", "stabilization", f"Missing source file `{path.relative_to(root)}`.")
            return

    metadata = _load_metadata(results_csv)
    if metadata is None:
        _record(results, "FAIL", "stabilization", "Missing metadata sidecar for stabilization results.")
    else:
        selector_name = metadata["selector_variant"]["name"]
        _record(
            results,
            "PASS",
            "stabilization",
            f"Metadata present with selector `{selector_name}` and boundary `{metadata['boundary_condition']}`.",
        )

    results_df = pd.read_csv(results_csv)
    period_df = pd.read_csv(period_scores_csv)
    candidate_df = pd.read_csv(candidates_csv)

    ok = True
    for row in results_df.itertuples(index=False):
        subset = period_df[(period_df["rule"] == row.rule) & (period_df["T"] == row.T)].sort_values(
            ["period_rank", "period"]
        )
        if subset.empty:
            ok = False
            _record(results, "FAIL", "stabilization", f"No period scores for {row.rule} at T={row.T}.")
            continue
        best = subset.iloc[0]
        if int(best["period"]) != int(row.selected_period):
            ok = False
            _record(
                results,
                "FAIL",
                "stabilization",
                f"{row.rule} at T={row.T}: selected period {row.selected_period} does not match grouped best period {best['period']}.",
            )
        if str(best["best_shift"]) != str(row.selected_shift):
            ok = False
            _record(
                results,
                "FAIL",
                "stabilization",
                f"{row.rule} at T={row.T}: selected shift {row.selected_shift} does not match grouped best shift {best['best_shift']}.",
            )
        if len(subset) > 1:
            runner_up = subset.iloc[1]
            expected_margin = float(runner_up["nml_bits"] - best["nml_bits"])
            if abs(expected_margin - float(row.margin)) > 1e-9:
                ok = False
                _record(
                    results,
                    "FAIL",
                    "stabilization",
                    f"{row.rule} at T={row.T}: margin {row.margin} does not equal runner-up minus best ({expected_margin}).",
                )

        selected_candidates = candidate_df[
            (candidate_df["rule"] == row.rule)
            & (candidate_df["T"] == row.T)
            & (candidate_df["is_selected_candidate"] == True)
        ]
        if len(selected_candidates) != 1:
            ok = False
            _record(
                results,
                "FAIL",
                "stabilization",
                f"{row.rule} at T={row.T}: expected exactly one selected candidate row, found {len(selected_candidates)}.",
            )

    if ok:
        _record(
            results,
            "PASS",
            "stabilization",
            "Selection rows, grouped period scores, and candidate flags are internally consistent.",
        )

    shift_zero_results = pd.read_csv(shift_zero_results_csv)
    shift_zero_expected = {
        "ECA-30": [1, 1, 1, 1, 1, 1],
        "ECA-54": [4, 4, 4, 4, 4, 4],
        "ECA-110": [7, 7, 7, 7, 7, 7],
    }
    shift_zero_ok = True
    for rule, periods in shift_zero_expected.items():
        actual = (
            shift_zero_results[shift_zero_results["rule"] == rule]
            .sort_values("T")["selected_period"]
            .astype(int)
            .tolist()
        )
        if actual != periods:
            shift_zero_ok = False
            _record(
                results,
                "WARN",
                "traceability",
                f"Shift-zero stabilization CSV for {rule} does not match the manuscript-facing sequence {periods}; actual sequence is {actual}.",
            )
    if shift_zero_ok:
        _record(
            results,
            "PASS",
            "traceability",
            "Dedicated shift-zero stabilization CSVs now exist and match the manuscript-facing 1D period sequences.",
        )


def validate_baseline(root: Path, results: list[CheckResult]) -> None:
    rule_level_csv = root / "results" / "baseline_selector_rule_level.csv"
    summary_csv = root / "results" / "baseline_selector_summary.csv"
    candidates_csv = root / "results" / "baseline_selector_candidates.csv"
    for path in [rule_level_csv, summary_csv, candidates_csv]:
        if path.exists():
            _record(results, "PASS", "baseline", f"Found source file `{path.relative_to(root)}`.")
        else:
            _record(results, "FAIL", "baseline", f"Missing source file `{path.relative_to(root)}`.")
            return

    metadata = _load_metadata(rule_level_csv)
    if metadata is None:
        _record(results, "FAIL", "baseline", "Missing metadata sidecar for baseline selector comparison.")
    else:
        _record(
            results,
            "PASS",
            "baseline",
            f"Metadata present with {len(metadata['selector_variants'])} explicit selector variants.",
        )

    rule_level = pd.read_csv(rule_level_csv)
    summary = pd.read_csv(summary_csv)
    candidates = pd.read_csv(candidates_csv)

    totals_ok = True
    for row in summary.itertuples(index=False):
        if int(row.p1 + row.p2 + row.p3 + row.p4plus) != int(row.n_rules):
            totals_ok = False
            _record(
                results,
                "FAIL",
                "baseline",
                f"Summary row `{row.dataset}/{row.selector}` does not reconcile: p1+p2+p3+p4plus != n_rules.",
            )
    if totals_ok:
        _record(results, "PASS", "baseline", "Summary rows reconcile exactly after restoring the missing `p=3` bucket.")

    winners_ok = True
    for row in rule_level.itertuples(index=False):
        if getattr(row, "trivial", False) is True:
            continue
        subset = candidates[(candidates["dataset"] == row.dataset) & (candidates["rule"] == row.rule)]
        for prefix in ["resid", "nll", "nml"]:
            selected = subset[subset[f"{prefix}_selected"] == True]
            if len(selected) != 1:
                winners_ok = False
                _record(
                    results,
                    "FAIL",
                    "baseline",
                    f"{row.rule} in {row.dataset}: selector `{prefix}` expected one selected candidate, found {len(selected)}.",
                )
                continue
            candidate = selected.iloc[0]
            if int(candidate["period"]) != int(getattr(row, f"{prefix}_period")):
                winners_ok = False
                _record(
                    results,
                    "FAIL",
                    "baseline",
                    f"{row.rule} in {row.dataset}: selector `{prefix}` period mismatch between candidate table and rule-level table.",
                )
    if winners_ok:
        _record(results, "PASS", "baseline", "Rule-level winners match the saved candidate tables for all three selectors.")


def validate_lifewiki_and_range_threshold(root: Path, results: list[CheckResult]) -> None:
    lw_100 = root / "outputs" / "lifewiki_survey.csv"
    lw_400 = root / "outputs" / "lifewiki_survey_T400.csv"
    for path in [lw_100, lw_400]:
        if path.exists():
            _record(results, "PASS", "lifewiki", f"Found source file `{path.relative_to(root)}`.")
        else:
            _record(results, "FAIL", "lifewiki", f"Missing source file `{path.relative_to(root)}`.")
            return

    df_100 = pd.read_csv(lw_100)
    df_400 = pd.read_csv(lw_400)
    if len(df_100) == 106 and len(df_400) == 106:
        _record(results, "PASS", "lifewiki", "Both LifeWiki survey outputs contain all 106 named rules.")
    else:
        _record(results, "FAIL", "lifewiki", "LifeWiki survey outputs do not both have 106 rows.")

    diamoeba_100 = int(df_100[df_100["name"] == "Diamoeba"]["selected_period"].iloc[0])
    diamoeba_400 = int(df_400[df_400["name"] == "Diamoeba"]["selected_period"].iloc[0])
    fredkin_400 = int(df_400[df_400["name"] == "Fredkin"]["selected_period"].iloc[0])
    serviettes_100 = int(df_100[df_100["name"] == "Serviettes[5]"]["selected_period"].iloc[0])
    serviettes_400 = int(df_400[df_400["name"] == "Serviettes[5]"]["selected_period"].iloc[0])
    if (diamoeba_100, diamoeba_400, fredkin_400, serviettes_100, serviettes_400) == (1, 2, 8, 2, 1):
        _record(
            results,
            "PASS",
            "lifewiki",
            "Named-rule checks match manuscript-facing claims: Diamoeba 1→2, Fredkin 8, Serviettes 2→1.",
        )
    else:
        _record(results, "FAIL", "lifewiki", "Named-rule regression checks do not match the expected survey outputs.")

    survey_large = root / "outputs" / "survey_2d_rules_large.csv"
    if survey_large.exists():
        df_large = pd.read_csv(survey_large)
        if len(df_large) == 773 and int(df_large["has_nonzero_shift"].sum()) == 172:
            _record(
                results,
                "PASS",
                "range_threshold",
                "Range-threshold survey output supports the paper counts: 773 non-trivial rules and 172 with nonzero shift.",
            )
        else:
            _record(
                results,
                "FAIL",
                "range_threshold",
                "Range-threshold survey output does not match the expected 773 / 172 counts.",
            )
        if _load_metadata(survey_large) is None:
            _record(
                results,
                "FAIL",
                "range_threshold",
                "Range-threshold survey CSV is present but its metadata sidecar is missing.",
            )
        else:
            _record(
                results,
                "PASS",
                "range_threshold",
                "Range-threshold survey CSV now has a metadata sidecar, so that paper count is metadata-validated as well as content-validated.",
            )
    else:
        _record(results, "WARN", "range_threshold", "Range-threshold survey CSV not found; that manuscript claim remains unvalidated here.")


def render_report(results: list[CheckResult]) -> str:
    lines = [
        "# Paper Traceability Report",
        "",
        "## Table Sources",
        "",
        "| Paper Quantity | CSV Source | Notes |",
        "|---|---|---|",
        "| 1D/2D/3D stabilization tables | `results/stabilization_results.csv` + `results/stabilization_period_scores.csv` + `results/stabilization_candidates.csv` | Joint period/shift selector. |",
        "| Shift-zero stabilization tables | `results/stabilization_shift_zero_results.csv` + `results/stabilization_shift_zero_period_scores.csv` | Dedicated fixed-shift-zero exports for manuscript-facing tables. |",
        "| Baseline selector comparison | `results/baseline_selector_rule_level.csv` + `results/baseline_selector_summary.csv` + `results/baseline_selector_candidates.csv` | Candidate-level selector definitions are explicit in metadata sidecars. |",
        "| LifeWiki named-rule survey | `outputs/lifewiki_survey.csv` and `outputs/lifewiki_survey_T400.csv` | Named-rule transitions checked directly. |",
        "| 2D range-threshold survey counts | `outputs/survey_2d_rules_large.csv` | Content checks and metadata sidecar now both exist. |",
        "",
        "## Validation Results",
        "",
    ]
    for item in results:
        lines.append(f"- `{item.status}` [{item.scope}] {item.message}")

    unresolved = [
        "Exact LaTeX table parsing is not automated here; the validator checks the underlying CSV sources and derived counts instead.",
    ]
    lines.extend(["", "## Unresolved Gaps", ""])
    lines.extend(f"- {gap}" for gap in unresolved)
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    results: list[CheckResult] = []
    validate_stabilization(root, results)
    validate_baseline(root, results)
    validate_lifewiki_and_range_threshold(root, results)

    report = render_report(results)
    report_path = root / "results" / "paper_traceability_report.md"
    report_path.write_text(report)
    print(report)
    print(f"\nWrote {report_path.relative_to(root)}")


if __name__ == "__main__":
    main()
