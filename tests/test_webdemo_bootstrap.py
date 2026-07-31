"""Tests for the in-browser reproduction demo's bootstrap.

``webdemo/bootstrap.py`` is the Python the demo page actually runs under
WebAssembly. It makes two environment adaptations -- a numba stub with
vectorized replacements for the ``@njit`` simulator kernels, and a zlib
fallback for lz4 -- and then drives the same code path as the experiment
suite. ``scripts/verify_webdemo_bootstrap.py`` checks the end-to-end numbers
against the committed CSVs; nothing checked the adaptations themselves, or
that the payload the page consumes is well formed.

These tests cover both. The central claim is the equivalence one: the
vectorized kernels must be *bit-identical* to the numba kernels they replace,
because every number the demo shows a reviewer depends on it.

Importing the bootstrap replaces those kernels process-wide, which is right
for the demo and wrong for the rest of the suite, so the import is confined to
a fixture that restores the originals on teardown.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

from relative_symmetry_repair import ca2d, ca3d, eca

REPO_ROOT = Path(__file__).resolve().parents[1]
WEBDEMO = REPO_ROOT / "webdemo"

PATCHED_KERNELS = (
    (eca, "_simulate_eca_numba"),
    (ca2d, "_simulate_life_numba"),
    (ca2d, "_simulate_life_general_numba"),
    (ca3d, "_simulate_3d_numba"),
    (ca3d, "_simulate_3d_general_numba"),
)


@pytest.fixture(scope="module")
def demo():
    """Import ``webdemo/bootstrap.py`` with its global patching contained.

    Yields a namespace holding the bootstrap module and the *original* numba
    kernels, so tests can compare the two implementations directly.
    """
    originals = {
        (module.__name__, name): getattr(module, name)
        for module, name in PATCHED_KERNELS
    }
    sys.path.insert(0, str(WEBDEMO))
    try:
        import bootstrap

        yield type("Demo", (), {"bootstrap": bootstrap, "originals": originals})
    finally:
        for module, name in PATCHED_KERNELS:
            setattr(module, name, originals[(module.__name__, name)])
        sys.modules.pop("bootstrap", None)
        if str(WEBDEMO) in sys.path:
            sys.path.remove(str(WEBDEMO))


def test_bootstrap_patches_exactly_the_kernels_it_documents(demo):
    """Every kernel the module claims to replace is in fact replaced."""
    for module, name in PATCHED_KERNELS:
        assert getattr(module, name) is not demo.originals[(module.__name__, name)]


# --- The equivalence the demo's credibility rests on --------------------------


@pytest.mark.parametrize("rule", [30, 54, 110, 0, 255, 90, 184])
def test_vectorized_eca_kernel_is_bit_identical_to_numba(demo, rule):
    rng = np.random.default_rng(11)
    initial = (rng.random(97) < 0.5).astype(np.uint8)
    expected = demo.originals[("relative_symmetry_repair.eca", "_simulate_eca_numba")](
        rule, initial, 40
    )
    actual = demo.bootstrap._simulate_eca_vec(rule, initial, 40)
    assert actual.dtype == np.uint8
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize(
    "survive, birth",
    [((2, 3), (3, 3)), ((1, 1), (3, 7)), ((3, 7), (1, 1)), ((9, 9), (2, 2))],
)
def test_vectorized_2d_range_kernel_is_bit_identical_to_numba(demo, survive, birth):
    rng = np.random.default_rng(23)
    initial = (rng.random((29, 31)) < 0.5).astype(np.uint8)
    expected = demo.originals[("relative_symmetry_repair.ca2d", "_simulate_life_numba")](
        initial, 25, survive[0], survive[1], birth[0], birth[1]
    )
    actual = demo.bootstrap._simulate_range_vec(
        initial, 25, survive[0], survive[1], birth[0], birth[1]
    )
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize("rulestring", ["B3/S23", "B36/S23", "B35678/S5678", "B37/S12345"])
def test_vectorized_2d_lut_kernel_is_bit_identical_to_numba(demo, rulestring):
    birth, survive = ca2d.parse_rulestring(rulestring)
    birth_lut, survive_lut = ca2d._make_luts(list(birth), list(survive))
    rng = np.random.default_rng(37)
    initial = (rng.random((28, 33)) < 0.5).astype(np.uint8)
    expected = demo.originals[
        ("relative_symmetry_repair.ca2d", "_simulate_life_general_numba")
    ](initial, 25, birth_lut, survive_lut)
    actual = demo.bootstrap._simulate_life_general_vec(initial, 25, birth_lut, survive_lut)
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize(
    "survive, birth, density",
    [((4, 5), (5, 5), 0.2), ((13, 26), (13, 14), 0.6), ((1, 1), (1, 3), 0.1), ((5, 8), (5, 8), 0.5)],
)
def test_vectorized_3d_range_kernel_is_bit_identical_to_numba(demo, survive, birth, density):
    """Covers all four hard-coded 3D rules at their tuned densities."""
    rng = np.random.default_rng(41)
    initial = (rng.random((11, 12, 13)) < density).astype(np.uint8)
    expected = demo.originals[("relative_symmetry_repair.ca3d", "_simulate_3d_numba")](
        initial, 8, survive[0], survive[1], birth[0], birth[1]
    )
    actual = demo.bootstrap._simulate_range_vec(
        initial, 8, survive[0], survive[1], birth[0], birth[1]
    )
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize("rulestring", ["B5-7,9/S4,6-8", "B5,7,9/S4,6"])
def test_vectorized_3d_lut_kernel_is_bit_identical_to_numba(demo, rulestring):
    birth, survive = ca3d.parse_rulestring_3d(rulestring)
    birth_lut, survive_lut = ca3d._make_luts_3d(list(birth), list(survive))
    rng = np.random.default_rng(43)
    initial = (rng.random((11, 12, 13)) < 0.4).astype(np.uint8)
    expected = demo.originals[
        ("relative_symmetry_repair.ca3d", "_simulate_3d_general_numba")
    ](initial, 8, birth_lut, survive_lut)
    actual = demo.bootstrap._simulate_life_general_vec(initial, 8, birth_lut, survive_lut)
    np.testing.assert_array_equal(actual, expected)


def test_neighbor_totals_wraps_on_the_torus(demo):
    """A single live corner cell must be seen by the opposite corner."""
    grid = np.zeros((5, 5), dtype=np.uint8)
    grid[0, 0] = 1
    totals = demo.bootstrap._neighbor_totals(grid)
    assert totals[0, 0] == 0
    for corner in ((4, 4), (0, 4), (4, 0), (1, 1)):
        assert totals[corner] == 1
    assert totals.sum() == 8  # every cell has exactly 8 neighbors


# --- Case construction --------------------------------------------------------


def test_build_case_eca(demo):
    case = demo.bootstrap.build_case("eca", 110)
    assert case.dimension == 1
    assert case.rule_number == 110


@pytest.mark.parametrize(
    "name", ["Diamoeba", "Maze with Mice", "S24/B11", "S11/B37", "S37/B11",
             "3d-life", "clouds", "crystal", "diamoeba3d"],
)
def test_build_case_reaches_every_named_representative_rule(demo, name):
    """The named cases the page offers are exactly the paper's hard-coded ones."""
    case = demo.bootstrap.build_case("named", name)
    assert case.name == name
    assert case.dimension in (2, 3)


def test_build_case_life2d_rulestring(demo):
    case = demo.bootstrap.build_case("life2d", "B36/S23")
    assert case.dimension == 2
    assert case.rulestring == "B36/S23"


def test_build_case_rule3d_rulestring_and_legacy_range(demo):
    general = demo.bootstrap.build_case(
        "rule3d", '{"rulestring": "B5,7,9/S4,6", "density": 0.4}'
    )
    assert general.dimension == 3
    assert general.density == pytest.approx(0.4)

    legacy = demo.bootstrap.build_case(
        "rule3d", '{"survive": [4, 5], "birth": [5, 5], "density": 0.5}'
    )
    assert legacy.dimension == 3
    assert legacy.survive == (4, 5)


def test_build_case_rejects_an_out_of_range_3d_neighbor_count(demo):
    with pytest.raises(ValueError):
        demo.bootstrap.build_case("rule3d", '{"survive": [4, 27], "birth": [5, 5]}')


def test_build_case_rejects_an_unknown_family(demo):
    with pytest.raises(ValueError):
        demo.bootstrap.build_case("nonsense", 3)


def test_build_case_validates_a_rulestring_before_running_anything(demo):
    with pytest.raises(ValueError):
        demo.bootstrap.build_case("life2d", "not-a-rulestring")


# --- The payload the page consumes --------------------------------------------


@pytest.fixture(scope="module")
def eca_result(demo):
    """One small real run through the demo's own entry point."""
    return demo.bootstrap.run_repro("eca", 110, 11, 40)


def test_run_repro_returns_the_reading_the_page_renders(eca_result):
    reading = eca_result["reading"]
    assert set(reading) == {
        "dimension", "template", "confidence", "cost", "complexity",
        "defects", "consistency", "grid", "thresholds",
    }
    assert reading["dimension"] == 1


def test_run_repro_reading_is_self_consistent_with_its_own_mask(eca_result):
    """The invariant the page displays: the rendered mask is the scored mask."""
    assert eca_result["reading"]["consistency"]["ok"] is True


def test_run_repro_reading_agrees_with_the_selection_record(eca_result):
    record = eca_result["record"]
    reading = eca_result["reading"]
    assert reading["template"]["period"] == record["selected_period"]
    assert reading["cost"]["nml_bits"] == pytest.approx(record["selected_nml_bits"])
    assert reading["cost"]["defect_rate"] == pytest.approx(record["selected_defect_rate"])
    assert reading["grid"]["n_candidates"] == eca_result["n_candidates"]


def test_run_repro_defect_series_sums_to_the_scored_defect_rate(eca_result):
    shape = eca_result["fields"]["spacetime"]["shape"]
    n_sites = shape[0] * shape[1]
    assert sum(eca_result["defects_per_frame"]) / n_sites == pytest.approx(
        eca_result["record"]["selected_defect_rate"]
    )


def test_run_repro_payload_survives_the_json_bridge_to_the_page(eca_result):
    """The worker ships this via json.dumps -> JSON.parse, which rejects Infinity."""
    payload = dict(eca_result)
    payload["fields"] = {
        name: {**field, "data": ""} for name, field in payload["fields"].items()
    }
    encoded = json.dumps(payload)
    assert "Infinity" not in encoded
    assert "NaN" not in encoded
    json.loads(encoded)


def test_run_repro_field_shapes_line_up_with_each_other(eca_result):
    fields = eca_result["fields"]
    assert fields["spacetime"]["shape"] == fields["background"]["shape"]
    assert fields["spacetime"]["shape"] == fields["defect"]["shape"]
    assert fields["spacetime"]["shape"][0] == 40
    assert len(eca_result["defects_per_frame"]) == 40


def test_run_repro_matches_the_library_run_for_the_same_case(demo, eca_result):
    """The demo path and the ordinary library path must not disagree."""
    from relative_symmetry_repair.experiment_core import scan_case_spacetime, simulate_case

    case = demo.bootstrap.build_case("eca", 110)
    spacetime = simulate_case(case, steps=40, seed=11)
    outcome = scan_case_spacetime(case, spacetime)
    assert outcome.selection.selected_period == eca_result["record"]["selected_period"]
    assert outcome.selection.selected_nml_bits == pytest.approx(
        eca_result["record"]["selected_nml_bits"]
    )


# --- The lz4 fallback ---------------------------------------------------------


def test_lz4_shim_flag_is_reported_to_the_page(eca_result):
    """The lz4 column is cosmetic, but the page must say when it is approximate."""
    assert isinstance(eca_result["lz4_shimmed"], bool)


# --- The demo bundle must carry what the package reads at runtime -------------
#
# The demo ships only bootstrap.py and the package; the repository's data/
# directory does not exist in the browser. A LifeWiki rule-space lookup
# therefore resolved to /home/data/lifewiki_rules.json and raised
# FileNotFoundError inside the worker's init(), taking down the entire
# reproduction demo for the sake of an optional search panel.


def test_lifewiki_rules_resolve_without_the_repository_layout(tmp_path, monkeypatch):
    """The package-local fallback is what makes the browser build work."""
    import relative_symmetry_repair.experiment_core as core

    # Pretend the repository's data/ directory is not there, as in the browser.
    monkeypatch.setattr(core, "_repo_root", lambda: tmp_path)
    fallback = core._lifewiki_rules_path()
    assert fallback.parent.name == "data"
    assert fallback.parent.parent.name == "relative_symmetry_repair"


def test_rule_spaces_never_raises_during_startup(demo, monkeypatch):
    """rule_spaces() runs inside worker init(); it must degrade, not raise."""
    import relative_symmetry_repair.rule_search as rs

    def boom(name):
        raise FileNotFoundError("simulated missing data file")

    monkeypatch.setattr(demo.bootstrap, "count_rule_space", boom)
    spaces = demo.bootstrap.rule_spaces()
    assert spaces == {}          # every family omitted, nothing raised


def test_rule_spaces_reports_every_family_when_data_is_present(demo):
    spaces = demo.bootstrap.rule_spaces()
    assert set(spaces) == {"eca", "life_range", "lifewiki", "rule3d"}
    assert spaces["lifewiki"]["size"] == 106
    assert spaces["rule3d"]["size"] == 142_884


# --- The bundle itself, built the way the site builds it ----------------------
#
# The tests above check code paths; the defect was in *packaging*. The bundle
# shipped only .py files, so data/lifewiki_rules.json was absent in the
# browser and the demo died on start-up. These build the real bundle and run
# it in a bare directory, which is the only shape that would have caught it.


@pytest.fixture(scope="module")
def demo_bundle(tmp_path_factory):
    """Build winnower_src.zip through the site builder's own code path."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import build_review_site
    finally:
        sys.path.remove(str(REPO_ROOT / "scripts"))
    site = tmp_path_factory.mktemp("site")
    build_review_site.write_demo_assets(site)
    return site / "winnower_src.zip"


def test_bundle_ships_the_data_the_package_reads(demo_bundle):
    """The exact omission that broke the deployed demo."""
    import zipfile

    names = set(zipfile.ZipFile(demo_bundle).namelist())
    assert "relative_symmetry_repair/data/lifewiki_rules.json" in names, (
        "the LifeWiki catalogue is missing from the demo bundle; "
        "rule_spaces() will raise FileNotFoundError in the browser"
    )
    assert "bootstrap.py" in names
    assert "relative_symmetry_repair/rule_search.py" in names


def test_bundle_runs_with_no_repository_around_it(demo_bundle, tmp_path):
    """End-to-end: extract the bundle alone, stub numba, call what crashed.

    Runs in a subprocess from a directory that is not inside the repository,
    so ``_repo_root()`` cannot accidentally find the real ``data/``. This is
    the shape Pyodide sees.
    """
    import json as _json
    import subprocess
    import zipfile

    workdir = tmp_path / "bare"
    workdir.mkdir()
    zipfile.ZipFile(demo_bundle).extractall(workdir)

    script = workdir / "check.py"
    script.write_text(
        "import sys, json\n"
        "sys.modules['numba'] = None\n"      # Pyodide has no numba
        "sys.path.insert(0, '.')\n"
        "import bootstrap\n"
        "print(json.dumps(bootstrap.rule_spaces()))\n"
    )
    result = subprocess.run(
        [sys.executable, "check.py"],
        cwd=workdir, capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, f"demo bundle failed to start:\n{result.stderr}"
    spaces = _json.loads(result.stdout.strip().splitlines()[-1])
    assert set(spaces) == {"eca", "life_range", "lifewiki", "rule3d"}
    assert spaces["lifewiki"]["size"] == 106
