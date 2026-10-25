# Preprint results: 2026-10-17-nl-ouro14-boundary

Paper: section 7 of [paper materials archive](../../paper/updated-CLQ.zip).

Ouro-1.4B on the same 1,105 items: native loop gain, all-layer same/shuffled query rescue, identity diagnostics and the null rescue result.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14": {
    "items": 1105,
    "acc": {
      "1": 78.28054298642535,
      "3": 93.30316742081448
    },
    "gate_pp": 15.02262443438914,
    "gate_ci95": [
      12.760180995475112,
      17.285067873303166
    ],
    "targets": 176,
    "rescue": {
      "all": 7.386363636363637,
      "all_shuf": 6.25
    },
    "B1": {
      "mean_pp": 1.1363636363636365,
      "ci95": [
        -1.1363636363636365,
        3.4090909090909087
      ],
      "supported": false
    },
    "margin": {
      "native1": -1.6042399880560962,
      "all": -1.5379453924569217,
      "all_shuf": -1.6430269147862087,
      "native3": 1.7731205208057708
    },
    "by_dataset": {
      "2wiki": {
        "n": 107,
        "all": 6.5420560747663545,
        "all_shuf": 4.672897196261682
      },
      "musique": {
        "n": 69,
        "all": 8.695652173913043,
        "all_shuf": 8.695652173913043
      }
    }
  }
}
```
