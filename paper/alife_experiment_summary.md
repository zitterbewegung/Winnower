# ALIFE experiment summary

## Null controls

The null-control panel compares original spacetimes against time-shuffled, space-shuffled, and density-matched Bernoulli controls using the same period-first Bernoulli-NML selector.

| dimension | control_label | runs | mean_margin_bits | mean_defect_rate | stable_winner_fraction |
| --- | --- | --- | --- | --- | --- |
| 1 | Bernoulli i.i.d. | 3 | 597.6761241310354 | 0.4644379340277777 | 1.0 |
| 1 | Original | 3 | 1662.1227177872645 | 0.3277495659722222 | 1.0 |
| 1 | Space shuffled | 3 | 583.4652708953654 | 0.4643467881944443 | 1.0 |
| 1 | Time shuffled | 3 | 581.977307330429 | 0.4470203993055555 | 1.0 |
| 2 | Bernoulli i.i.d. | 5 | 12603.44202330918 | 0.38379296875 | 1.0 |
| 2 | Original | 5 | 18815.859006008355 | 0.0140736694335937 | 1.0 |
| 2 | Space shuffled | 5 | 12772.168098739769 | 0.3837965698242187 | 1.0 |
| 2 | Time shuffled | 5 | 13968.236641370528 | 0.1141841430664062 | 1.0 |
| 3 | Bernoulli i.i.d. | 4 | 8329.312070122642 | 0.0824806213378906 | 1.0 |
| 3 | Original | 4 | 8425.596793377561 | 0.082623291015625 | 1.0 |
| 3 | Space shuffled | 4 | 8259.98061653805 | 0.082623291015625 | 1.0 |
| 3 | Time shuffled | 4 | 8190.61635934338 | 0.082623291015625 | 1.0 |

## Seed stability

Representative rules were re-run across multiple deterministic seeds and stabilization horizons. The table below reports agreement on the final selected period, transition counts, and residual variability.

| rule | final_modal_period | final_modal_period_frequency | mean_transitions_per_seed | final_mean_margin_bits | final_defect_rate_cv |
| --- | --- | --- | --- | --- | --- |
| ECA-110 | 7 | 0.5 | 1.6 | 3763.2212501874137 | 0.1791039194395814 |
| ECA-30 | 1 | 1.0 | 0.7 | 296.9557426192361 | 0.0016115227514234 |
| ECA-54 | 4 | 1.0 | 0.0 | 2274.9794577130015 | 0.0549980749954175 |
| Diamoeba | 1 | 0.8 | 0.2 | 15375.445414089749 | 0.5122530927550835 |
| Maze with Mice | 2 | 1.0 | 1.0 | 22284.322085223717 | 0.2037048818540623 |
| S11/B37 | 4 | 1.0 | 1.0 | 19138.10844992487 | 0.2128098051135818 |
| S24/B11 | 2 | 1.0 | 1.0 | 17451.68571194649 | 0.127011534108428 |
| S37/B11 | 2 | 1.0 | 1.0 | 17570.00609821549 | 0.0861409518300853 |
| 3d-life | 1 | 1.0 | 0.0 | 8593.924748651196 | 0.161279034785174 |
| clouds | 1 | 1.0 | 0.0 | 10081.682638956798 | 0.9656286293574038 |
| crystal | 2 | 1.0 | 0.0 | 11239.162672158036 | 0.0041619610606515 |
| diamoeba3d | 1 | 1.0 | 0.0 | 7398.818423533923 | 0.0149778346425542 |

## Candidate-range robustness

Across the tested nested search ranges, 3 rules showed at least one winner change between the smallest and largest candidate sets.

| rule | period_change_rate | shift_change_rate | modal_period_small | modal_period_large |
| --- | --- | --- | --- | --- |
| ECA-110 | 0.6 | 0.4 | 4 | 4 |
| ECA-30 | 0.0 | 1.0 | 1 | 1 |
| ECA-54 | 0.0 | 0.0 | 4 | 4 |
| Diamoeba | 0.0 | 0.0 | 1 | 1 |
| Maze with Mice | 0.0 | 0.0 | 2 | 2 |
| S11/B37 | 0.0 | 0.0 | 4 | 4 |
| S24/B11 | 0.0 | 0.0 | 2 | 2 |
| S37/B11 | 0.0 | 0.0 | 2 | 2 |
| 3d-life | 0.0 | 0.0 | 1 | 1 |
| clouds | 0.0 | 0.0 | 1 | 1 |
| crystal | 0.0 | 0.0 | 2 | 2 |
| diamoeba3d | 0.0 | 1.0 | 1 | 1 |

## LifeWiki horizon sweep

The named Life-like survey tracks how the selected period distribution evolves as the observation horizon grows.

| selected_period | count_runs | horizon |
| --- | --- | --- |
| 1 | 457 | 800 |
| 2 | 64 | 800 |
| 4 | 4 | 800 |
| 8 | 5 | 800 |

## ECA atlas

The complete ECA atlas reports the modal selected period for each rule across five horizons and five seeds.

| final_modal_period | count_rules |
| --- | --- |
| 1 | 144 |
| 2 | 78 |
| 3 | 4 |
| 4 | 20 |
| 6 | 4 |
| 7 | 2 |
| 8 | 4 |

## 3D survey

| rule | dimension | n_seeds | horizon | modal_period | modal_period_frequency | mean_margin_bits | mean_defect_rate | nonunique_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3d-life | 3 | 5 | 80 | 1 | 1.0 | 8615.114691101433 | 0.0678863525390625 | 0.0 |
| clouds | 3 | 5 | 80 | 1 | 1.0 | 10066.6820659501 | 0.1234942626953125 | 0.0 |
| crystal | 3 | 5 | 80 | 2 | 1.0 | 11270.917409818916 | 0.2107293701171874 | 0.0 |
| diamoeba3d | 3 | 5 | 80 | 1 | 1.0 | 7402.270779430692 | 0.2975018310546874 | 0.0 |

## Counterexample stress

Observed issues: {'candidate_range_instability': 13, 'nonunique_winners': 400, 'null_control_false_positives': 0, 'suspicious_repeated_ties': 16, 'very_small_margins': 0}
