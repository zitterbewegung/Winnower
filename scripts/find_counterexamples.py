#!/usr/bin/env python3
"""Search for counterexamples to false statements in the paper.

Produces explicit, small counterexamples for:
1. False monotonicity (Theorem 2 as stated): same shift, p2=m*p1, but d*(p2,s) > d*(p1,s)
2. Non-refinement of orbit partitions under same-shift doubling
3. Period absorption by structured defects (Theorem D)
"""

import itertools

import numpy as np

from relative_symmetry_repair.repair import (
    component_labels,
    fit_relative_periodic_background,
)
from relative_symmetry_repair.repair_nd import (
    component_labels_nd,
    fit_relative_periodic_background_nd,
)


def search_monotonicity_counterexamples_1d():
    """Search for 1D cases where same-shift monotonicity fails."""
    print("=" * 70)
    print("SEARCH: 1D monotonicity counterexamples (same shift, p2 = m*p1)")
    print("=" * 70)

    found = 0
    for D in range(3, 13):
        for T in range(4, 17):
            for s in range(1, D):
                for p1 in range(1, min(T, 6)):
                    for m in range(2, min(T // p1 + 1, 5)):
                        p2 = m * p1
                        if p2 >= T:
                            continue

                        # Check whether the velocity condition is violated
                        if (m * s) % D == s % D:
                            continue  # velocity matched, monotonicity should hold

                        # Try checkerboard-like spacetimes
                        for freq in range(1, D):
                            spacetime = np.zeros((T, D), dtype=np.uint8)
                            for t in range(T):
                                for x in range(D):
                                    spacetime[t, x] = ((t * s + x) * freq) % 2

                            fit1 = fit_relative_periodic_background(spacetime, shift=s, period=p1)
                            fit2 = fit_relative_periodic_background(spacetime, shift=s, period=p2)

                            if fit2.defect_sites > fit1.defect_sites:
                                found += 1
                                if found <= 10:
                                    print(f"\nCounterexample #{found}:")
                                    print(f"  D={D}, T={T}, s={s}, p1={p1}, p2={p2} (m={m})")
                                    print(f"  d*(p1,s) = {fit1.defect_sites}")
                                    print(f"  d*(p2,s) = {fit2.defect_sites}")
                                    print(f"  Velocity check: m*s mod D = {(m*s)%D}, s = {s}")
                                    print(f"  Spacetime (freq={freq}):")
                                    for t in range(min(T, 6)):
                                        print(f"    {spacetime[t]}")

    print(f"\nTotal counterexamples found: {found}")
    return found


def search_monotonicity_counterexamples_2d():
    """Search for 2D cases where same-shift monotonicity fails."""
    print("\n" + "=" * 70)
    print("SEARCH: 2D monotonicity counterexamples")
    print("=" * 70)

    found = 0
    for D in range(3, 7):
        for T in range(4, 9):
            for sy in range(0, min(D, 3)):
                for sx in range(0, min(D, 3)):
                    if sy == 0 and sx == 0:
                        continue
                    for p1 in range(1, min(T, 4)):
                        p2 = 2 * p1
                        if p2 >= T:
                            continue
                        if (2 * sy) % D == sy and (2 * sx) % D == sx:
                            continue

                        # 3D-diagonal spacetime
                        spacetime = np.zeros((T, D, D), dtype=np.uint8)
                        for t in range(T):
                            for y in range(D):
                                for x in range(D):
                                    spacetime[t, y, x] = (t * (sy + sx) + y + x) % 2

                        fit1 = fit_relative_periodic_background_nd(
                            spacetime, shift=(sy, sx), period=p1
                        )
                        fit2 = fit_relative_periodic_background_nd(
                            spacetime, shift=(sy, sx), period=p2
                        )

                        if fit2.defect_sites > fit1.defect_sites:
                            found += 1
                            if found <= 5:
                                print(f"\nCounterexample #{found}:")
                                print(f"  D={D}, T={T}, shift=({sy},{sx}), p1={p1}, p2={p2}")
                                print(f"  d*(p1) = {fit1.defect_sites}")
                                print(f"  d*(p2) = {fit2.defect_sites}")

    print(f"\nTotal 2D counterexamples found: {found}")
    return found


def verify_velocity_matched_monotonicity():
    """Verify that velocity-matched monotonicity always holds on small examples."""
    print("\n" + "=" * 70)
    print("VERIFY: velocity-matched monotonicity (should always hold)")
    print("=" * 70)

    violations = 0
    tested = 0
    rng = np.random.RandomState(42)

    for D in range(3, 10):
        for T in range(6, 20):
            for s1 in range(D):
                for p1 in range(1, min(T // 2, 5)):
                    for m in range(2, min(T // p1, 5)):
                        p2 = m * p1
                        s2 = (m * s1) % D
                        if p2 >= T:
                            continue

                        spacetime = rng.randint(0, 2, size=(T, D)).astype(np.uint8)
                        fit1 = fit_relative_periodic_background(spacetime, shift=s1, period=p1)
                        fit2 = fit_relative_periodic_background(spacetime, shift=s2, period=p2)

                        tested += 1
                        if fit2.defect_sites > fit1.defect_sites:
                            violations += 1
                            print(f"VIOLATION: D={D}, T={T}, s1={s1}, s2={s2}, p1={p1}, p2={p2}")
                            print(f"  d*(p1,s1) = {fit1.defect_sites}, d*(p2,s2) = {fit2.defect_sites}")

    print(f"\nTested {tested} velocity-matched cases, {violations} violations.")
    if violations == 0:
        print("All velocity-matched cases satisfy monotonicity. (Consistent with Theorem C.2)")
    return violations


def demonstrate_period_absorption():
    """Demonstrate Theorem D: periodic defects are absorbed by higher periods."""
    print("\n" + "=" * 70)
    print("DEMONSTRATE: Period absorption (Theorem D)")
    print("=" * 70)

    D = 12
    for T in [30, 60, 120, 240]:
        # Period-1 background (all zeros) with defects every 3rd step
        spacetime = np.zeros((T, D), dtype=np.uint8)
        for t in range(0, T, 3):
            spacetime[t, 0] = 1
            spacetime[t, 1] = 1

        fit1 = fit_relative_periodic_background(spacetime, shift=0, period=1)
        fit3 = fit_relative_periodic_background(spacetime, shift=0, period=3)

        print(f"\nT={T}:")
        print(f"  p=1: defects={fit1.defect_sites}, nml={fit1.nml_bits:.1f}, mdl={fit1.mdl_bits:.1f}")
        print(f"  p=3: defects={fit3.defect_sites}, nml={fit3.nml_bits:.1f}, mdl={fit3.mdl_bits:.1f}")
        print(f"  p=3 wins NML: {fit3.nml_bits < fit1.nml_bits}")
        print(f"  p=3 wins MDL: {fit3.mdl_bits < fit1.mdl_bits}")


def main():
    n_cex_1d = search_monotonicity_counterexamples_1d()
    n_cex_2d = search_monotonicity_counterexamples_2d()
    n_violations = verify_velocity_matched_monotonicity()
    demonstrate_period_absorption()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Same-shift monotonicity counterexamples (1D): {n_cex_1d}")
    print(f"Same-shift monotonicity counterexamples (2D): {n_cex_2d}")
    print(f"Velocity-matched monotonicity violations: {n_violations}")
    if n_cex_1d > 0:
        print("\nCONCLUSION: Theorem 2 (as stated in paper) is FALSE.")
        print("The correct condition requires velocity-matched shifts: s2 = m*s1 mod D.")
    if n_violations == 0:
        print("The corrected Theorem C.2 (velocity-matched) holds on all tested cases.")


if __name__ == "__main__":
    main()
