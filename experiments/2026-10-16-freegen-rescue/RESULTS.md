# Preprint results: 2026-10-16-freegen-rescue

Paper: section 4 of [paper materials archive](../../paper/updated-CLQ.zip).

Greedy generation scored from the first alphabetic word under the original rule. Preserve the 1.4B zero-color output and zero rescue, and the 2.6B positive rescue.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14": {
    "accuracy": {
      "gen_loop1": 0.0,
      "gen_loop3": 0.935,
      "four_loop1": 0.5716666666666667,
      "four_loop3": 0.93,
      "loop1_noncolor": 1.0,
      "loop3_noncolor": 0.0016666666666666668,
      "loop1_top_words": [
        [
          "",
          453
        ],
        [
          "the",
          119
        ],
        [
          "a",
          25
        ],
        [
          "b",
          3
        ]
      ]
    },
    "targets": 561,
    "paired": 561,
    "rescue_same": 0.0,
    "rescue_same_ci95": [
      0.0,
      0.0
    ],
    "rescue_shuf": 0.0,
    "delta_pp": 0.0,
    "ci_bonf2": [
      0.0,
      0.0
    ],
    "supported": false
  },
  "ouro26": {
    "accuracy": {
      "gen_loop1": 0.6583333333333333,
      "gen_loop3": 0.99,
      "four_loop1": 0.6416666666666667,
      "four_loop3": 0.9966666666666667,
      "loop1_noncolor": 0.01,
      "loop3_noncolor": 0.005,
      "loop1_top_words": [
        [
          "red",
          188
        ],
        [
          "blue",
          179
        ],
        [
          "yellow",
          134
        ],
        [
          "green",
          93
        ],
        [
          "the",
          6
        ]
      ]
    },
    "targets": 202,
    "paired": 202,
    "rescue_same": 0.8960396039603961,
    "rescue_same_ci95": [
      85.14851485148515,
      93.56435643564357
    ],
    "rescue_shuf": 0.20297029702970298,
    "delta_pp": 69.3069306930693,
    "ci_bonf2": [
      61.88118811881188,
      76.73267326732673
    ],
    "supported": true
  }
}
```
