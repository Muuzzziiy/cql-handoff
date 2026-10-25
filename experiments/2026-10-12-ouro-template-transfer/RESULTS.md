# Preprint results: 2026-10-12-ouro-template-transfer

Paper: section 8 of [paper materials archive](../../paper/updated-CLQ.zip).

Native gates and all-head same/shuffled rescue on V1_order_distract, V2_new_surface and V3_both, including the failed 1.4B gates. Rescue on failed-gate cells is descriptive.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14/V1_order_distract": {
    "gate": {
      "n": 400,
      "s_star": 374,
      "gain_s_star_pp": 39.3048128342246,
      "gain_ci": [
        34.22459893048128,
        44.38502673796791
      ],
      "G_comp_pp": 36.5,
      "G_comp_ci": [
        31.5,
        41.5
      ],
      "acc_q2": {
        "1": 0.5425,
        "2": 0.8075,
        "3": 0.955,
        "4": 0.945
      },
      "acc_q1a_l1": 0.98,
      "acc_q1b_l1": 0.97,
      "pass": true
    },
    "rescue": {
      "targets": 169,
      "paired": 169,
      "rescue": {
        "all": 0.650887573964497,
        "all_shuffled": 0.2958579881656805
      },
      "delta_all": {
        "mean_pp": 35.50295857988166,
        "ci95_pp": [
          26.627218934911244,
          44.37869822485207
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/V2_new_surface": {
    "gate": {
      "n": 400,
      "s_star": 147,
      "gain_s_star_pp": 27.2108843537415,
      "gain_ci": [
        18.367346938775512,
        36.054421768707485
      ],
      "G_comp_pp": -6.0,
      "G_comp_ci": [
        -11.5,
        -0.5
      ],
      "acc_q2": {
        "1": 0.2775,
        "2": 0.5375,
        "3": 0.8275,
        "4": 0.795
      },
      "acc_q1a_l1": 0.89,
      "acc_q1b_l1": 0.4375,
      "pass": false
    },
    "rescue": {
      "targets": 230,
      "paired": 230,
      "rescue": {
        "all": 0.41739130434782606,
        "all_shuffled": 0.25217391304347825
      },
      "delta_all": {
        "mean_pp": 16.52173913043478,
        "ci95_pp": [
          9.130434782608695,
          23.91304347826087
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/V3_both": {
    "gate": {
      "n": 400,
      "s_star": 111,
      "gain_s_star_pp": 10.81081081081081,
      "gain_ci": [
        -0.9009009009009009,
        22.52252252252252
      ],
      "G_comp_pp": -8.75,
      "G_comp_ci": [
        -14.249999999999998,
        -3.5000000000000004
      ],
      "acc_q2": {
        "1": 0.28,
        "2": 0.295,
        "3": 0.5525,
        "4": 0.6625
      },
      "acc_q1a_l1": 0.915,
      "acc_q1b_l1": 0.3825,
      "pass": false
    },
    "rescue": {
      "targets": 145,
      "paired": 145,
      "rescue": {
        "all": 0.5586206896551724,
        "all_shuffled": 0.46206896551724136
      },
      "delta_all": {
        "mean_pp": 9.655172413793103,
        "ci95_pp": [
          4.137931034482759,
          15.172413793103448
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/V1_order_distract": {
    "gate": {
      "n": 400,
      "s_star": 397,
      "gain_s_star_pp": 24.68513853904282,
      "gain_ci": [
        20.40302267002519,
        29.219143576826195
      ],
      "G_comp_pp": 24.25,
      "G_comp_ci": [
        20.0,
        28.749999999999996
      ],
      "acc_q2": {
        "1": 0.7375,
        "2": 0.915,
        "3": 0.985,
        "4": 0.985
      },
      "acc_q1a_l1": 1.0,
      "acc_q1b_l1": 0.995,
      "pass": true
    },
    "rescue": {
      "targets": 102,
      "paired": 102,
      "rescue": {
        "all": 0.7647058823529411,
        "all_shuffled": 0.20588235294117646
      },
      "delta_all": {
        "mean_pp": 55.88235294117647,
        "ci95_pp": [
          45.09803921568628,
          66.66666666666666
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/V2_new_surface": {
    "gate": {
      "n": 400,
      "s_star": 383,
      "gain_s_star_pp": 37.85900783289817,
      "gain_ci": [
        32.89817232375979,
        42.81984334203655
      ],
      "G_comp_pp": 36.0,
      "G_comp_ci": [
        31.0,
        41.0
      ],
      "acc_q2": {
        "1": 0.59,
        "2": 0.96,
        "3": 0.9925,
        "4": 0.99
      },
      "acc_q1a_l1": 0.965,
      "acc_q1b_l1": 0.9925,
      "pass": true
    },
    "rescue": {
      "targets": 163,
      "paired": 163,
      "rescue": {
        "all": 0.656441717791411,
        "all_shuffled": 0.1656441717791411
      },
      "delta_all": {
        "mean_pp": 49.079754601226995,
        "ci95_pp": [
          41.104294478527606,
          57.05521472392638
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/V3_both": {
    "gate": {
      "n": 400,
      "s_star": 352,
      "gain_s_star_pp": 40.625,
      "gain_ci": [
        35.22727272727273,
        46.02272727272727
      ],
      "G_comp_pp": 35.75,
      "G_comp_ci": [
        31.0,
        40.75
      ],
      "acc_q2": {
        "1": 0.51,
        "2": 0.8875,
        "3": 0.985,
        "4": 0.98
      },
      "acc_q1a_l1": 0.985,
      "acc_q1b_l1": 0.8975,
      "pass": true
    },
    "rescue": {
      "targets": 193,
      "paired": 193,
      "rescue": {
        "all": 0.44041450777202074,
        "all_shuffled": 0.21243523316062177
      },
      "delta_all": {
        "mean_pp": 22.797927461139896,
        "ci95_pp": [
          15.025906735751295,
          30.569948186528496
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  }
}
```
