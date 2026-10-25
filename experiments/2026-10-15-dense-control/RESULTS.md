# Preprint results: 2026-10-15-dense-control

Paper: section 4 of [paper materials archive](../../paper/updated-CLQ.zip).

Qwen3-1.7B-Base depth-offset control. Retain all specified exits and offsets, same/shuffled queries and the inconclusive 10-point bound.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "qwen": {
    "accuracy": {
      "q2": 0.41333333333333333,
      "q1a": 0.9866666666666667,
      "q1b": 0.6666666666666666
    },
    "targets": 352,
    "per_delta": {
      "4": {
        "best_layer": 17,
        "n_eval": 179,
        "Q_rescue": 0.18435754189944134,
        "Qs_rescue": 0.09497206703910614,
        "delta_pp": 8.938547486033519,
        "delta_ci_bonf3": [
          3.910614525139665,
          15.083798882681565
        ],
        "H_rescue_best_layer": 0.16759776536312848,
        "H_rescue_max_over_layers": 0.4581005586592179
      },
      "8": {
        "best_layer": 17,
        "n_eval": 179,
        "Q_rescue": 0.055865921787709494,
        "Qs_rescue": 0.03910614525139665,
        "delta_pp": 1.675977653631285,
        "delta_ci_bonf3": [
          -2.2346368715083798,
          5.58659217877095
        ],
        "H_rescue_best_layer": 0.07262569832402235,
        "H_rescue_max_over_layers": 0.3854748603351955
      },
      "12": {
        "best_layer": 9,
        "n_eval": 179,
        "Q_rescue": 0.09497206703910614,
        "Qs_rescue": 0.11173184357541899,
        "delta_pp": -1.675977653631285,
        "delta_ci_bonf3": [
          -4.4692737430167595,
          0.0
        ],
        "H_rescue_best_layer": 0.2346368715083799,
        "H_rescue_max_over_layers": 0.29608938547486036
      }
    }
  },
  "ouro14": {
    "accuracy": {
      "q2": 0.5666666666666667,
      "q1a": 0.985,
      "q1b": 0.9383333333333334,
      "q2_loop3": 0.9466666666666667,
      "q1a_loop3": 1.0,
      "q1b_loop3": 0.9816666666666667
    },
    "targets": 233,
    "per_delta": {
      "4": {
        "best_layer": 11,
        "n_eval": 114,
        "Q_rescue": 0.043859649122807015,
        "Qs_rescue": 0.05263157894736842,
        "delta_pp": -0.8771929824561403,
        "delta_ci_bonf3": [
          -3.508771929824561,
          0.0
        ],
        "H_rescue_best_layer": 0.15789473684210525,
        "H_rescue_max_over_layers": 0.22807017543859648
      },
      "8": {
        "best_layer": 11,
        "n_eval": 114,
        "Q_rescue": 0.017543859649122806,
        "Qs_rescue": 0.03508771929824561,
        "delta_pp": -1.7543859649122806,
        "delta_ci_bonf3": [
          -5.263157894736842,
          0.0
        ],
        "H_rescue_best_layer": 0.13157894736842105,
        "H_rescue_max_over_layers": 0.17543859649122806
      },
      "12": {
        "best_layer": 10,
        "n_eval": 114,
        "Q_rescue": 0.07894736842105263,
        "Qs_rescue": 0.07894736842105263,
        "delta_pp": 0.0,
        "delta_ci_bonf3": [
          0.0,
          0.0
        ],
        "H_rescue_best_layer": 0.14912280701754385,
        "H_rescue_max_over_layers": 0.18421052631578946
      }
    }
  },
  "D1_no_dense_rescue": false
}
```
