# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Paper Companion Notebook: Approximate Symmetry-Repair Decomposition for Cellular Automata
#
# This notebook reproduces all key results from the paper, including the strengthening experiments.

# %%
from pathlib import Path
import sys
import time

ROOT = Path.cwd()
if not (ROOT / "src").exists() and (ROOT.parent / "src").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from relative_symmetry_repair.eca import random_initial_state, simulate_eca
from relative_symmetry_repair.plotting import plot_decomposition, plot_spacetime, plot_spectrum, save_figure
from relative_symmetry_repair.repair import (
    extract_components,
    fit_reflection_symmetric_state,
    scan_relative_periodicity,
    summarise_components,
)
from relative_symmetry_repair.ca2d import random_initial_grid, simulate_2d, rule_consistency_rate_2d
from relative_symmetry_repair.repair_nd import (
    extract_components_nd,
    fit_relative_periodic_background_nd,
    scan_relative_periodicity_nd,
    summarise_components_nd,
)
from relative_symmetry_repair.plotting_nd import (
    DEFECT_CMAP, BINARY_CMAP,
    plot_2d_decomposition,
    plot_2d_slices,
    plot_spectrum_nd,
)

OUTPUT_DIR = ROOT / "outputs" / "paper"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
pd.set_option("display.max_columns", 20)
print("Setup complete.")

# %% [markdown]
# ## Section 3: 1D ECA Validation
# Reproduce Table 1: Rules 30, 54, 110

# %%
WIDTH = 192
STEPS = 144
SEED = 11

initial = random_initial_state(width=WIDTH, density=0.5, seed=SEED)
rules_1d = [30, 54, 110]
spacetimes_1d = {r: simulate_eca(rule=r, initial=initial, steps=STEPS) for r in rules_1d}

fig, axes = plt.subplots(1, 3, figsize=(15, 4), constrained_layout=True)
for ax, rule in zip(axes, rules_1d):
    ax.imshow(spacetimes_1d[rule], aspect="auto", interpolation="nearest", cmap="binary")
    ax.set_title(f"Rule {rule}")
    ax.set_xlabel("cell index"); ax.set_ylabel("time")
fig.suptitle("Figure 1: 1D ECA spacetimes", fontsize=13)
save_figure(fig, OUTPUT_DIR / "fig1_1d_spacetimes.png")
plt.show()

# %%
SHIFT_RANGE = range(-6, 7)
PERIOD_RANGE = range(1, 11)

spectra_1d, fits_1d = {}, {}
for rule, st in spacetimes_1d.items():
    frame, fit_map = scan_relative_periodicity(st, shifts=SHIFT_RANGE, periods=PERIOD_RANGE, rule=rule)
    spectra_1d[rule] = frame
    fits_1d[rule] = fit_map

summary_rows = []
for rule, frame in spectra_1d.items():
    best = frame.sort_values(["defect_rate", "rule_error", "run_length_bits"]).iloc[0]
    summary_rows.append({
        "Rule": rule,
        "Best (s,p)": f"({int(best['shift'])}, {int(best['period'])})",
        "Defect Rate": f"{best['defect_rate']:.1%}",
        "RL Bits": int(best["run_length_bits"]),
        "Rule Error": f"{best['rule_error']:.3f}",
    })

print("Table 1: 1D ECA results")
display(pd.DataFrame(summary_rows))

# %%
# Decompositions
for rule in rules_1d:
    best = spectra_1d[rule].sort_values(["defect_rate", "rule_error", "run_length_bits"]).iloc[0]
    key = (int(best["shift"]), int(best["period"]))
    fig, _ = plot_decomposition(fits_1d[rule][key], source=spacetimes_1d[rule],
                                 title_prefix=f"Rule {rule} ")
    save_figure(fig, OUTPUT_DIR / f"fig_rule{rule}_decomposition.png")
    plt.show()

# %% [markdown]
# ## Section 3.3: Codelength Distinguishes Geometry

# %%
N, M = 512, 64
rng = np.random.default_rng(1234)

base = np.zeros(N, dtype=np.uint8)
clustered = base.copy(); clustered[40:40+M] = 1
randomised = base.copy()
randomised[rng.choice(np.arange(N//2), size=M, replace=False)] = 1

clustered_fit = fit_reflection_symmetric_state(clustered)
random_fit = fit_reflection_symmetric_state(randomised)

print("Table 2: Same defect count, different codelength")
comparison = pd.DataFrame([
    {"Case": "Clustered", "Defects": clustered_fit.defect_sites,
     "Rate": f"{clustered_fit.defect_rate:.1%}",
     "Comb. Bits": f"{clustered_fit.combinatorial_bits:.1f}",
     "RL Bits": clustered_fit.run_length_bits},
    {"Case": "Random", "Defects": random_fit.defect_sites,
     "Rate": f"{random_fit.defect_rate:.1%}",
     "Comb. Bits": f"{random_fit.combinatorial_bits:.1f}",
     "RL Bits": random_fit.run_length_bits},
])
display(comparison)

fig, axes = plt.subplots(2, 2, figsize=(12, 4), constrained_layout=True)
axes[0,0].imshow(clustered[None,:], aspect="auto", interpolation="nearest", cmap="binary")
axes[0,0].set_title("Clustered state")
axes[0,1].imshow(clustered_fit.defect_mask[None,:], aspect="auto", interpolation="nearest", cmap="Reds")
axes[0,1].set_title(f"Mask (RL={clustered_fit.run_length_bits} bits)")
axes[1,0].imshow(randomised[None,:], aspect="auto", interpolation="nearest", cmap="binary")
axes[1,0].set_title("Random state")
axes[1,1].imshow(random_fit.defect_mask[None,:], aspect="auto", interpolation="nearest", cmap="Reds")
axes[1,1].set_title(f"Mask (RL={random_fit.run_length_bits} bits)")
for ax in axes.ravel(): ax.set_yticks([])
fig.suptitle("Figure 2: Equal defect count, 6x different codelength", fontsize=12)
save_figure(fig, OUTPUT_DIR / "fig2_codelength_comparison.png")
plt.show()

# %% [markdown]
# ## Section 4: 2D Totalistic Rules Survey
# Load pre-computed survey data (from scripts/survey_2d_rules.py)

# %%
survey_path = ROOT / "outputs" / "survey_2d_rules.csv"
if survey_path.exists():
    df_survey = pd.read_csv(survey_path)
    print(f"Loaded {len(df_survey)} non-trivial 2D rules")
    print("\nTable 3: Top 10 by defect rate")
    cols = ["rule_name", "best_shift_0", "best_shift_1", "best_period",
            "defect_rate", "run_length_bits", "rule_error"]
    display(df_survey[cols].head(10))
else:
    print("Survey CSV not found — run scripts/survey_2d_rules.py first")

# %% [markdown]
# ### Visualize top 2D rule: S14/B11

# %%
survive, birth = (1, 4), (1, 1)
initial_2d = random_initial_grid(96, 96, density=0.5, seed=11)
st_2d = simulate_2d(initial_2d, steps=80, rule="custom", survive=survive, birth=birth)

def rule_error_fn(bg):
    return rule_consistency_rate_2d(bg, survive, birth)

shift_range = range(-4, 5)
frame_2d, fits_2d = scan_relative_periodicity_nd(
    st_2d, shift_ranges=[shift_range, shift_range],
    periods=range(1, 9), rule_error_fn=rule_error_fn,
)

best = frame_2d.sort_values(["defect_rate", "run_length_bits"]).iloc[0]
best_shift = (int(best["shift_0"]), int(best["shift_1"]))
best_period = int(best["period"])
best_fit = fits_2d[(best_shift, best_period)]
print(f"S14/B11: shift={best_shift}, period={best_period}, defect_rate={best_fit.defect_rate:.4f}")

fig, _ = plot_2d_slices(st_2d, title="S14/B11 time slices", max_slices=8)
save_figure(fig, OUTPUT_DIR / "fig3_s14b11_slices.png")
plt.show()

fig, _ = plot_2d_decomposition(best_fit, source=st_2d, time_index=60,
                                title_prefix="S14/B11 ")
save_figure(fig, OUTPUT_DIR / "fig4_s14b11_decomposition.png")
plt.show()

# %% [markdown]
# ## Section 5: Persistent Structured Defects
# ### S24/B11 — the most interesting candidate

# %%
survive_24, birth_24 = (2, 4), (1, 1)
initial_big = random_initial_grid(128, 128, density=0.5, seed=11)
st_24 = simulate_2d(initial_big, steps=120, rule="custom", survive=survive_24, birth=birth_24)

def rule_error_fn_24(bg):
    return rule_consistency_rate_2d(bg, survive_24, birth_24)

frame_24, fits_24 = scan_relative_periodicity_nd(
    st_24, shift_ranges=[range(-4, 5), range(-4, 5)],
    periods=range(1, 9), rule_error_fn=rule_error_fn_24,
)
best24 = frame_24.sort_values(["defect_rate", "run_length_bits"]).iloc[0]
best_fit_24 = fits_24[((int(best24["shift_0"]), int(best24["shift_1"])), int(best24["period"]))]

# Defect time series
defects_per_t = best_fit_24.defect_mask.sum(axis=(1, 2))
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(defects_per_t, color='#c83f49', linewidth=1.2)
ax.set_xlabel("time step"); ax.set_ylabel("defect count")
ax.set_title(f"S24/B11 defect count over time (period={int(best24['period'])})")
mid = len(defects_per_t) // 2
late_mean = defects_per_t[mid:].mean()
ax.axhline(late_mean, color='gray', ls='--', alpha=0.7, label=f"late mean={late_mean:.1f}")
ax.legend()
fig.tight_layout()
save_figure(fig, OUTPUT_DIR / "fig5_s24b11_timeseries.png")
plt.show()

# Defect evolution
fig, axes = plt.subplots(2, 5, figsize=(20, 8))
t_indices = np.linspace(0, 119, 10, dtype=int)
for ax, t in zip(axes.ravel(), t_indices):
    ax.imshow(best_fit_24.defect_mask[t].astype(np.uint8), interpolation="nearest",
              cmap=DEFECT_CMAP, vmin=0, vmax=1)
    ax.set_title(f"t={t} ({best_fit_24.defect_mask[t].sum()})", fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle("S24/B11 defect mask evolution", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.95))
save_figure(fig, OUTPUT_DIR / "fig6_s24b11_defect_evolution.png")
plt.show()

print(f"S24/B11: rate={best_fit_24.defect_rate:.4f}, "
      f"early defects={defects_per_t[:20].mean():.1f}, "
      f"late defects={defects_per_t[mid:].mean():.1f} ± {defects_per_t[mid:].std():.1f}")

# %% [markdown]
# ## Strengthening: Multi-seed Robustness (Table 4)

# %%
TOP_RULES = [
    ("S14/B11", (1, 4), (1, 1)),
    ("S25/B12", (2, 5), (1, 2)),
    ("S66/B36", (6, 6), (3, 6)),
    ("S24/B11", (2, 4), (1, 1)),
    ("S11/B37", (1, 1), (3, 7)),
    ("S37/B11", (3, 7), (1, 1)),
]
SEEDS = [11, 42, 73, 99, 137, 200, 314, 500, 777, 1024]

seed_results = []
for name, survive, birth in TOP_RULES:
    rates = []
    for seed in SEEDS:
        ini = random_initial_grid(64, 64, density=0.5, seed=seed)
        st = simulate_2d(ini, steps=60, rule="custom", survive=survive, birth=birth)
        best_rate = min(
            fit_relative_periodic_background_nd(st, shift=(0,0), period=p).defect_rate
            for p in range(1, 9)
        )
        rates.append(best_rate)
    arr = np.array(rates)
    seed_results.append({
        "Rule": name, "Mean Rate": f"{arr.mean():.4f}",
        "Std": f"{arr.std():.4f}", "CV": f"{arr.std()/arr.mean()*100:.1f}%",
        "Min": f"{arr.min():.4f}", "Max": f"{arr.max():.4f}",
    })

print("Table 4: Multi-seed robustness (10 seeds, 64×64, 60 steps)")
display(pd.DataFrame(seed_results))

# %% [markdown]
# ## Strengthening: Size Scaling (Table 5)

# %%
PERSISTENT_RULES = [
    ("S24/B11", (2, 4), (1, 1)),
    ("S11/B37", (1, 1), (3, 7)),
    ("S37/B11", (3, 7), (1, 1)),
]
SIZES = [32, 64, 96, 128, 192]

scale_results = []
for name, survive, birth in PERSISTENT_RULES:
    for size in SIZES:
        ini = random_initial_grid(size, size, density=0.5, seed=11)
        st = simulate_2d(ini, steps=100, rule="custom", survive=survive, birth=birth)
        best_rate, best_p = 1.0, 1
        for p in range(1, 9):
            fit = fit_relative_periodic_background_nd(st, shift=(0,0), period=p)
            if fit.defect_rate < best_rate:
                best_rate, best_p = fit.defect_rate, p
        fit = fit_relative_periodic_background_nd(st, shift=(0,0), period=best_p)
        dpt = fit.defect_mask.sum(axis=(1, 2))
        mid = len(dpt) // 2
        late = dpt[mid:]
        scale_results.append({
            "Rule": name, "Grid": f"{size}×{size}",
            "Rate": f"{best_rate:.4f}", "Period": best_p,
            "Late Defects": f"{late.mean():.1f} ± {late.std():.1f}",
            "Density": f"{late.mean()/(size*size):.5f}",
            "Persist": "Yes" if late.mean() > 5 else "No",
        })

print("Table 5: Size scaling of persistent defects")
display(pd.DataFrame(scale_results))

# %% [markdown]
# ## Strengthening: Autocorrelation Baseline (Table 6)

# %%
def autocorrelation_period(spacetime, max_period=10):
    T = spacetime.shape[0]
    flat = spacetime.reshape(T, -1).astype(np.float64)
    centered = flat - flat.mean(axis=1, keepdims=True)
    autocorrs = []
    for lag in range(1, min(max_period + 1, T)):
        num = (centered[:T-lag] * centered[lag:]).sum()
        den = np.sqrt((centered[:T-lag]**2).sum() * (centered[lag:]**2).sum())
        autocorrs.append(num / den if den > 0 else 0.0)
    return int(np.argmax(autocorrs)) + 1

baseline_results = []
for name, survive, birth in TOP_RULES:
    ini = random_initial_grid(64, 64, density=0.5, seed=11)
    st = simulate_2d(ini, steps=60, rule="custom", survive=survive, birth=birth)

    ac_p = autocorrelation_period(st)
    ac_fit = fit_relative_periodic_background_nd(st, shift=(0,0), period=ac_p)

    best_rate, best_p = 1.0, 1
    for p in range(1, 9):
        fit = fit_relative_periodic_background_nd(st, shift=(0,0), period=p)
        if fit.defect_rate < best_rate:
            best_rate, best_p = fit.defect_rate, p

    improvement = 100 * (ac_fit.defect_rate - best_rate) / ac_fit.defect_rate if ac_fit.defect_rate > 0 else 0
    baseline_results.append({
        "Rule": name,
        "AC Period": ac_p, "AC Rate": f"{ac_fit.defect_rate:.4f}",
        "Our Period": best_p, "Our Rate": f"{best_rate:.4f}",
        "Improvement": f"{improvement:.1f}%",
    })

print("Table 6: Autocorrelation baseline comparison")
display(pd.DataFrame(baseline_results))

# %% [markdown]
# ## Summary
#
# Strengthening experiments support the paper's claims:
# - **Multi-seed**: Defect rate groups remain well-separated across 10 seeds (CV < 17%), though orderings within groups can swap
# - **Size scaling**: Defects persist at all sizes ≥ 64×64, consistent with a genuine dynamical feature
# - **Autocorrelation**: Period scanning finds higher harmonics for persistent-defect rules (3-9% improvement), but the primary value is the decomposition framework, not period detection
# - **Note**: The run-length metric is raster-order dependent (row-major flattening); periods may vary due to subsumption (e.g., period 4 vs 8)

# %%
print("All figures saved to:", OUTPUT_DIR)
print("Done.")
