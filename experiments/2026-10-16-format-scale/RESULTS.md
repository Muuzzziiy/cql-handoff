# Preprint results: 2026-10-16-format-scale

Paper: section 8 of [paper materials archive](../../paper/updated-CLQ.zip).

Four formats at 8/16 entities. Preserve all native gates, the 1.4B failed gates, and the same/shuffled rescue in eligible cells.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14/F1_locker_E8": {
    "gate": {
      "n": 400,
      "s_star": 245,
      "gain_s_star_pp": 53.06122448979592,
      "gain_ci": [
        46.53061224489796,
        59.591836734693885
      ],
      "G_comp_pp": 19.75,
      "G_comp_ci": [
        13.0,
        26.5
      ],
      "acc_q2": {
        "1": 0.2325,
        "2": 0.495,
        "3": 0.765,
        "4": 0.745
      },
      "acc_q1a_l1": 0.795,
      "acc_q1b_l1": 0.8175,
      "pass": true
    },
    "rescue": {
      "targets": 217,
      "paired": 217,
      "rescue": {
        "all": 0.31336405529953915,
        "all_shuffled": 0.12903225806451613
      },
      "delta_all": {
        "mean_pp": 18.433179723502306,
        "ci95_pp": [
          11.981566820276496,
          24.88479262672811
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F1_locker_E16": {
    "gate": {
      "n": 400,
      "s_star": 130,
      "gain_s_star_pp": 50.76923076923077,
      "gain_ci": [
        41.53846153846154,
        60.0
      ],
      "G_comp_pp": -15.75,
      "G_comp_ci": [
        -22.5,
        -8.75
      ],
      "acc_q2": {
        "1": 0.125,
        "2": 0.2425,
        "3": 0.605,
        "4": 0.635
      },
      "acc_q1a_l1": 0.7275,
      "acc_q1b_l1": 0.5025,
      "pass": false
    },
    "rescue": {
      "targets": 196,
      "paired": 195,
      "rescue": {
        "all": 0.1989795918367347,
        "all_shuffled": 0.08717948717948718
      },
      "delta_all": {
        "mean_pp": 11.282051282051283,
        "ci95_pp": [
          4.615384615384616,
          17.94871794871795
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F2_room_E8": {
    "gate": {
      "n": 400,
      "s_star": 371,
      "gain_s_star_pp": 43.93530997304582,
      "gain_ci": [
        38.81401617250674,
        49.32614555256065
      ],
      "G_comp_pp": 37.75,
      "G_comp_ci": [
        32.25,
        43.25
      ],
      "acc_q2": {
        "1": 0.43,
        "2": 0.685,
        "3": 0.8775,
        "4": 0.8425
      },
      "acc_q1a_l1": 0.9375,
      "acc_q1b_l1": 0.9925,
      "pass": true
    },
    "rescue": {
      "targets": 184,
      "paired": 184,
      "rescue": {
        "all": 0.41847826086956524,
        "all_shuffled": 0.13043478260869565
      },
      "delta_all": {
        "mean_pp": 28.804347826086957,
        "ci95_pp": [
          21.195652173913043,
          36.95652173913043
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F2_room_E16": {
    "gate": {
      "n": 400,
      "s_star": 288,
      "gain_s_star_pp": 49.65277777777778,
      "gain_ci": [
        43.40277777777778,
        55.90277777777778
      ],
      "G_comp_pp": 26.75,
      "G_comp_ci": [
        20.25,
        33.25
      ],
      "acc_q2": {
        "1": 0.23,
        "2": 0.415,
        "3": 0.735,
        "4": 0.7575
      },
      "acc_q1a_l1": 0.85,
      "acc_q1b_l1": 0.8775,
      "pass": true
    },
    "rescue": {
      "targets": 209,
      "paired": 209,
      "rescue": {
        "all": 0.2535885167464115,
        "all_shuffled": 0.03827751196172249
      },
      "delta_all": {
        "mean_pp": 21.5311004784689,
        "ci95_pp": [
          15.311004784688995,
          27.751196172248804
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F3_car_E8": {
    "gate": {
      "n": 400,
      "s_star": 360,
      "gain_s_star_pp": 32.77777777777778,
      "gain_ci": [
        28.055555555555557,
        37.77777777777778
      ],
      "G_comp_pp": 26.75,
      "G_comp_ci": [
        21.75,
        32.0
      ],
      "acc_q2": {
        "1": 0.62,
        "2": 0.905,
        "3": 0.98,
        "4": 0.9675
      },
      "acc_q1a_l1": 0.9325,
      "acc_q1b_l1": 0.97,
      "pass": true
    },
    "rescue": {
      "targets": 146,
      "paired": 146,
      "rescue": {
        "all": 0.4041095890410959,
        "all_shuffled": 0.136986301369863
      },
      "delta_all": {
        "mean_pp": 26.71232876712329,
        "ci95_pp": [
          18.493150684931507,
          34.93150684931507
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F3_car_E16": {
    "gate": {
      "n": 400,
      "s_star": 270,
      "gain_s_star_pp": 55.18518518518518,
      "gain_ci": [
        49.25925925925926,
        61.111111111111114
      ],
      "G_comp_pp": 33.0,
      "G_comp_ci": [
        27.500000000000004,
        38.5
      ],
      "acc_q2": {
        "1": 0.2825,
        "2": 0.6675,
        "3": 0.92,
        "4": 0.895
      },
      "acc_q1a_l1": 0.83,
      "acc_q1b_l1": 0.8125,
      "pass": true
    },
    "rescue": {
      "targets": 256,
      "paired": 256,
      "rescue": {
        "all": 0.234375,
        "all_shuffled": 0.0390625
      },
      "delta_all": {
        "mean_pp": 19.53125,
        "ci95_pp": [
          14.453125,
          25.0
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F4_story_E8": {
    "gate": {
      "n": 400,
      "s_star": 254,
      "gain_s_star_pp": 47.63779527559055,
      "gain_ci": [
        40.94488188976378,
        54.330708661417326
      ],
      "G_comp_pp": 16.75,
      "G_comp_ci": [
        9.75,
        23.25
      ],
      "acc_q2": {
        "1": 0.2575,
        "2": 0.4775,
        "3": 0.78,
        "4": 0.8275
      },
      "acc_q1a_l1": 0.8025,
      "acc_q1b_l1": 0.8075,
      "pass": true
    },
    "rescue": {
      "targets": 222,
      "paired": 222,
      "rescue": {
        "all": 0.3783783783783784,
        "all_shuffled": 0.12162162162162163
      },
      "delta_all": {
        "mean_pp": 25.675675675675674,
        "ci95_pp": [
          18.91891891891892,
          32.432432432432435
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F4_story_E16": {
    "gate": {
      "n": 400,
      "s_star": 100,
      "gain_s_star_pp": 34.0,
      "gain_ci": [
        24.0,
        44.0
      ],
      "G_comp_pp": -18.0,
      "G_comp_ci": [
        -24.75,
        -11.25
      ],
      "acc_q2": {
        "1": 0.145,
        "2": 0.18,
        "3": 0.5675,
        "4": 0.6525
      },
      "acc_q1a_l1": 0.68,
      "acc_q1b_l1": 0.5675,
      "pass": false
    },
    "rescue": {
      "targets": 180,
      "paired": 179,
      "rescue": {
        "all": 0.15555555555555556,
        "all_shuffled": 0.0670391061452514
      },
      "delta_all": {
        "mean_pp": 8.938547486033519,
        "ci95_pp": [
          2.2346368715083798,
          15.64245810055866
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F1_locker_E8": {
    "gate": {
      "n": 400,
      "s_star": 360,
      "gain_s_star_pp": 58.611111111111114,
      "gain_ci": [
        53.333333333333336,
        63.888888888888886
      ],
      "G_comp_pp": 50.74999999999999,
      "G_comp_ci": [
        45.25,
        56.25
      ],
      "acc_q2": {
        "1": 0.315,
        "2": 0.79,
        "3": 0.9225,
        "4": 0.94
      },
      "acc_q1a_l1": 0.97,
      "acc_q1b_l1": 0.9275,
      "pass": true
    },
    "rescue": {
      "targets": 246,
      "paired": 246,
      "rescue": {
        "all": 0.4715447154471545,
        "all_shuffled": 0.12195121951219512
      },
      "delta_all": {
        "mean_pp": 34.959349593495936,
        "ci95_pp": [
          27.64227642276423,
          42.27642276422765
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F1_locker_E16": {
    "gate": {
      "n": 400,
      "s_star": 266,
      "gain_s_star_pp": 56.766917293233085,
      "gain_ci": [
        50.37593984962406,
        62.78195488721805
      ],
      "G_comp_pp": 28.499999999999996,
      "G_comp_ci": [
        22.25,
        34.75
      ],
      "acc_q2": {
        "1": 0.1675,
        "2": 0.53,
        "3": 0.785,
        "4": 0.84
      },
      "acc_q1a_l1": 0.925,
      "acc_q1b_l1": 0.72,
      "pass": true
    },
    "rescue": {
      "targets": 251,
      "paired": 251,
      "rescue": {
        "all": 0.21912350597609562,
        "all_shuffled": 0.055776892430278883
      },
      "delta_all": {
        "mean_pp": 16.334661354581673,
        "ci95_pp": [
          10.756972111553784,
          21.91235059760956
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F2_room_E8": {
    "gate": {
      "n": 400,
      "s_star": 384,
      "gain_s_star_pp": 45.57291666666667,
      "gain_ci": [
        40.625,
        50.78125
      ],
      "G_comp_pp": 42.75,
      "G_comp_ci": [
        37.5,
        48.0
      ],
      "acc_q2": {
        "1": 0.4425,
        "2": 0.73,
        "3": 0.9,
        "4": 0.9075
      },
      "acc_q1a_l1": 0.98,
      "acc_q1b_l1": 0.99,
      "pass": true
    },
    "rescue": {
      "targets": 185,
      "paired": 185,
      "rescue": {
        "all": 0.3675675675675676,
        "all_shuffled": 0.11891891891891893
      },
      "delta_all": {
        "mean_pp": 24.864864864864867,
        "ci95_pp": [
          17.2972972972973,
          32.972972972972975
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F2_room_E16": {
    "gate": {
      "n": 400,
      "s_star": 340,
      "gain_s_star_pp": 52.05882352941177,
      "gain_ci": [
        46.470588235294116,
        57.647058823529406
      ],
      "G_comp_pp": 39.25,
      "G_comp_ci": [
        33.0,
        45.25
      ],
      "acc_q2": {
        "1": 0.2275,
        "2": 0.5375,
        "3": 0.76,
        "4": 0.7875
      },
      "acc_q1a_l1": 0.9625,
      "acc_q1b_l1": 0.8875,
      "pass": true
    },
    "rescue": {
      "targets": 220,
      "paired": 220,
      "rescue": {
        "all": 0.20454545454545456,
        "all_shuffled": 0.045454545454545456
      },
      "delta_all": {
        "mean_pp": 15.909090909090908,
        "ci95_pp": [
          10.454545454545453,
          21.818181818181817
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F3_car_E8": {
    "gate": {
      "n": 400,
      "s_star": 388,
      "gain_s_star_pp": 33.50515463917525,
      "gain_ci": [
        28.865979381443296,
        38.402061855670105
      ],
      "G_comp_pp": 32.5,
      "G_comp_ci": [
        28.000000000000004,
        37.25
      ],
      "acc_q2": {
        "1": 0.62,
        "2": 0.8975,
        "3": 0.975,
        "4": 0.985
      },
      "acc_q1a_l1": 1.0,
      "acc_q1b_l1": 0.97,
      "pass": true
    },
    "rescue": {
      "targets": 144,
      "paired": 144,
      "rescue": {
        "all": 0.3125,
        "all_shuffled": 0.08333333333333333
      },
      "delta_all": {
        "mean_pp": 22.916666666666664,
        "ci95_pp": [
          15.277777777777779,
          31.25
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F3_car_E16": {
    "gate": {
      "n": 400,
      "s_star": 349,
      "gain_s_star_pp": 62.17765042979943,
      "gain_ci": [
        56.73352435530086,
        67.621776504298
      ],
      "G_comp_pp": 51.74999999999999,
      "G_comp_ci": [
        46.25,
        57.25
      ],
      "acc_q2": {
        "1": 0.2625,
        "2": 0.7025,
        "3": 0.8975,
        "4": 0.9375
      },
      "acc_q1a_l1": 0.9825,
      "acc_q1b_l1": 0.895,
      "pass": true
    },
    "rescue": {
      "targets": 259,
      "paired": 259,
      "rescue": {
        "all": 0.20463320463320464,
        "all_shuffled": 0.04633204633204633
      },
      "delta_all": {
        "mean_pp": 15.83011583011583,
        "ci95_pp": [
          10.81081081081081,
          20.84942084942085
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F4_story_E8": {
    "gate": {
      "n": 400,
      "s_star": 374,
      "gain_s_star_pp": 51.06951871657755,
      "gain_ci": [
        45.98930481283423,
        56.14973262032086
      ],
      "G_comp_pp": 46.25,
      "G_comp_ci": [
        41.0,
        51.5
      ],
      "acc_q2": {
        "1": 0.365,
        "2": 0.735,
        "3": 0.8925,
        "4": 0.91
      },
      "acc_q1a_l1": 0.975,
      "acc_q1b_l1": 0.96,
      "pass": true
    },
    "rescue": {
      "targets": 212,
      "paired": 212,
      "rescue": {
        "all": 0.4811320754716981,
        "all_shuffled": 0.12735849056603774
      },
      "delta_all": {
        "mean_pp": 35.37735849056604,
        "ci95_pp": [
          27.830188679245282,
          42.924528301886795
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F4_story_E16": {
    "gate": {
      "n": 400,
      "s_star": 297,
      "gain_s_star_pp": 50.16835016835017,
      "gain_ci": [
        43.77104377104377,
        56.56565656565656
      ],
      "G_comp_pp": 27.250000000000004,
      "G_comp_ci": [
        20.75,
        33.75
      ],
      "acc_q2": {
        "1": 0.165,
        "2": 0.4425,
        "3": 0.6925,
        "4": 0.775
      },
      "acc_q1a_l1": 0.9675,
      "acc_q1b_l1": 0.7725,
      "pass": true
    },
    "rescue": {
      "targets": 221,
      "paired": 220,
      "rescue": {
        "all": 0.22171945701357465,
        "all_shuffled": 0.04090909090909091
      },
      "delta_all": {
        "mean_pp": 18.181818181818183,
        "ci95_pp": [
          12.272727272727273,
          24.09090909090909
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  }
}
```
