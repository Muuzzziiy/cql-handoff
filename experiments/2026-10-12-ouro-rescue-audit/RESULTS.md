# Preprint results: 2026-10-12-ouro-rescue-audit

Paper: section 4 of [paper materials archive](../../paper/updated-CLQ.zip).

Saved operand-isolation diagnostics and the replication on 300 new Ouro-2.6B scenes. Final-position query patches keep all other positions unchanged. The archived factor controls use the original same-scene inputs.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14": {
    "isolation": [
      {
        "case_id": "g003_q2",
        "layers": 24,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 46,
        "late_Q_differs_from_loop1_Q_at_q": 24
      },
      {
        "case_id": "g008_q2",
        "layers": 24,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 46,
        "late_Q_differs_from_loop1_Q_at_q": 24
      },
      {
        "case_id": "g011_q2",
        "layers": 24,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 46,
        "late_Q_differs_from_loop1_Q_at_q": 24
      },
      {
        "case_id": "g013_q2",
        "layers": 24,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 46,
        "late_Q_differs_from_loop1_Q_at_q": 24
      }
    ],
    "factors": {
      "q_s3": {
        "n": 245,
        "rescue": 0.8979591836734694,
        "ci95": [
          0.8571428571428571,
          0.9346938775510204
        ],
        "median_margin": 0.298828125
      },
      "span_s3": {
        "n": 245,
        "rescue": 0.7795918367346939,
        "ci95": [
          0.726530612244898,
          0.8285714285714286
        ],
        "median_margin": 0.14453125
      },
      "q_s4": {
        "n": 245,
        "rescue": 0.6979591836734694,
        "ci95": [
          0.6408163265306123,
          0.7551020408163265
        ],
        "median_margin": 0.1171875
      },
      "span_s4": {
        "n": 245,
        "rescue": 0.5102040816326531,
        "ci95": [
          0.4489795918367347,
          0.5714285714285714
        ],
        "median_margin": 0.0078125
      }
    }
  },
  "ouro26": {
    "isolation": [
      {
        "case_id": "g001_q2",
        "layers": 48,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 94,
        "late_Q_differs_from_loop1_Q_at_q": 48
      },
      {
        "case_id": "g003_q2",
        "layers": 48,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 94,
        "late_Q_differs_from_loop1_Q_at_q": 48
      },
      {
        "case_id": "g005_q2",
        "layers": 48,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 94,
        "late_Q_differs_from_loop1_Q_at_q": 48
      },
      {
        "case_id": "g007_q2",
        "layers": 48,
        "other_positions_identical_all_layers": true,
        "q_K_V_identical_layer0": true,
        "q_K_V_layers_changed_downstream": 94,
        "late_Q_differs_from_loop1_Q_at_q": 48
      }
    ],
    "factors": {
      "q_s3": {
        "n": 223,
        "rescue": 0.968609865470852,
        "ci95": [
          0.9417040358744395,
          0.9910313901345291
        ],
        "median_margin": 2.03125
      },
      "span_s3": {
        "n": 223,
        "rescue": 0.9327354260089686,
        "ci95": [
          0.8968609865470852,
          0.9641255605381166
        ],
        "median_margin": 1.1796875
      },
      "q_s4": {
        "n": 223,
        "rescue": 0.9103139013452914,
        "ci95": [
          0.8699551569506726,
          0.9461883408071748
        ],
        "median_margin": 1.3125
      },
      "span_s4": {
        "n": 223,
        "rescue": 0.7488789237668162,
        "ci95": [
          0.6905829596412556,
          0.8071748878923767
        ],
        "median_margin": 0.625
      }
    }
  },
  "ouro26_fresh": {
    "targets": 91,
    "paired": 91,
    "rescue_same": 0.989010989010989,
    "rescue_shuffled": 0.26373626373626374,
    "delta_pp": 72.52747252747253,
    "delta_ci95_pp": [
      63.73626373626373,
      81.31868131868131
    ]
  }
}
```
