# Preprint results: 2026-10-15-ouro-entity-scale

Paper: section 8 of [paper materials archive](../../paper/updated-CLQ.zip).

Gate and all-head rescue on 8- and 16-entity scenes. Keep the failed 1.4B 16-entity gate. Scoring uses the corresponding number of candidates.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14/E8": {
    "gate": {
      "n": 400,
      "s_star": 309,
      "gain_s_star_pp": 51.45631067961165,
      "gain_ci": [
        45.63106796116505,
        56.957928802588995
      ],
      "G_comp_pp": 31.5,
      "G_comp_ci": [
        25.5,
        37.5
      ],
      "acc_q2": {
        "1": 0.3475,
        "2": 0.605,
        "3": 0.8725,
        "4": 0.875
      },
      "acc_q1a_l1": 0.85,
      "acc_q1b_l1": 0.92,
      "pass": true
    },
    "rescue": {
      "targets": 213,
      "paired": 213,
      "rescue": {
        "all": 0.3755868544600939,
        "all_shuffled": 0.07042253521126761
      },
      "delta_all": {
        "mean_pp": 30.51643192488263,
        "ci95_pp": [
          23.943661971830984,
          37.558685446009385
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/E16": {
    "gate": {
      "n": 400,
      "s_star": 147,
      "gain_s_star_pp": 57.14285714285714,
      "gain_ci": [
        48.29931972789115,
        65.98639455782312
      ],
      "G_comp_pp": -2.5,
      "G_comp_ci": [
        -9.5,
        4.25
      ],
      "acc_q2": {
        "1": 0.11,
        "2": 0.3025,
        "3": 0.6825,
        "4": 0.66
      },
      "acc_q1a_l1": 0.7,
      "acc_q1b_l1": 0.54,
      "pass": false
    },
    "rescue": {
      "targets": 235,
      "paired": 235,
      "rescue": {
        "all": 0.23404255319148937,
        "all_shuffled": 0.08936170212765958
      },
      "delta_all": {
        "mean_pp": 14.468085106382977,
        "ci95_pp": [
          8.51063829787234,
          20.851063829787233
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/E8": {
    "gate": {
      "n": 400,
      "s_star": 386,
      "gain_s_star_pp": 44.559585492227974,
      "gain_ci": [
        39.37823834196891,
        49.740932642487046
      ],
      "G_comp_pp": 42.0,
      "G_comp_ci": [
        36.75,
        47.25
      ],
      "acc_q2": {
        "1": 0.4625,
        "2": 0.7875,
        "3": 0.9175,
        "4": 0.945
      },
      "acc_q1a_l1": 0.98,
      "acc_q1b_l1": 0.985,
      "pass": true
    },
    "rescue": {
      "targets": 186,
      "paired": 186,
      "rescue": {
        "all": 0.4838709677419355,
        "all_shuffled": 0.12903225806451613
      },
      "delta_all": {
        "mean_pp": 35.483870967741936,
        "ci95_pp": [
          27.419354838709676,
          43.54838709677419
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/E16": {
    "gate": {
      "n": 400,
      "s_star": 313,
      "gain_s_star_pp": 49.201277955271564,
      "gain_ci": [
        42.81150159744409,
        55.27156549520767
      ],
      "G_comp_pp": 32.5,
      "G_comp_ci": [
        26.25,
        38.75
      ],
      "acc_q2": {
        "1": 0.21,
        "2": 0.54,
        "3": 0.745,
        "4": 0.8075
      },
      "acc_q1a_l1": 0.945,
      "acc_q1b_l1": 0.835,
      "pass": true
    },
    "rescue": {
      "targets": 224,
      "paired": 224,
      "rescue": {
        "all": 0.3080357142857143,
        "all_shuffled": 0.044642857142857144
      },
      "delta_all": {
        "mean_pp": 26.339285714285715,
        "ci95_pp": [
          20.089285714285715,
          32.589285714285715
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  }
}
```
