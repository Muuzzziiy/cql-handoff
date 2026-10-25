# Preprint results: 2026-10-17-nl-fresh-replication

Paper: section 7 of [paper materials archive](../../paper/updated-CLQ.zip).

The independent 646-item 2Wiki replication. Retain source/QA/evidence/hop exclusions, all-layer and last-quarter all-head rescue with paired shuffled controls.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "items": 646,
  "by_dataset_items": {
    "2wiki": 646
  },
  "acc1": 77.70897832817337,
  "acc3": 93.65325077399382,
  "acc1_ci": [
    74.45820433436533,
    80.80495356037152
  ],
  "acc3_ci": [
    91.79566563467493,
    95.5108359133127
  ],
  "gate_pp": 15.944272445820435,
  "gate_ci95": [
    12.848297213622292,
    19.040247678018577
  ],
  "targets": 110,
  "rescue": {
    "arm1": 31.818181818181817,
    "arm2": 23.636363636363637,
    "arm3": 63.63636363636363,
    "arm4": 38.18181818181819
  },
  "R1": {
    "mean_pp": 8.181818181818182,
    "ci_bonf2": [
      1.8181818181818181,
      15.454545454545453
    ],
    "supported": true
  },
  "R2": {
    "mean_pp": 25.454545454545453,
    "ci_bonf2": [
      16.363636363636363,
      35.45454545454545
    ],
    "supported": true
  },
  "margin": {
    "native1": -2.1079559575427664,
    "arm1": -0.683208062432029,
    "arm2": -1.2746133533391086,
    "arm3": 0.4703875595873052,
    "arm4": -0.2940210244872353,
    "native3": 2.124669487503442
  },
  "by_dataset": {
    "2wiki": {
      "n": 110,
      "arm1": 31.818181818181817,
      "arm2": 23.636363636363637,
      "arm3": 63.63636363636363,
      "arm4": 38.18181818181819
    }
  },
  "run3_reference": {
    "R1": 14.2,
    "R1_ci95": [
      7.5,
      20.9
    ],
    "R2_3398": 29.9,
    "R2_ci95": [
      20.9,
      38.8
    ]
  }
}
```
