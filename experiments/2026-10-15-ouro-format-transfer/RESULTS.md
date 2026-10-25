# Preprint results: 2026-10-15-ouro-format-transfer

Paper: section 8 of [paper materials archive](../../paper/updated-CLQ.zip).

Gate and all-head rescue for lockers, rooms, cars and story formats. Donor prompts have the same token length.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14/F1_locker": {
    "gate": {
      "n": 400,
      "s_star": 319,
      "gain_s_star_pp": 42.94670846394985,
      "gain_ci": [
        37.30407523510972,
        48.589341692789965
      ],
      "G_comp_pp": 30.0,
      "G_comp_ci": [
        24.25,
        35.75
      ],
      "acc_q2": {
        "1": 0.43,
        "2": 0.745,
        "3": 0.9025,
        "4": 0.87
      },
      "acc_q1a_l1": 0.955,
      "acc_q1b_l1": 0.87,
      "pass": true
    },
    "rescue": {
      "targets": 196,
      "paired": 196,
      "rescue": {
        "all": 0.5153061224489796,
        "all_shuffled": 0.16326530612244897
      },
      "delta_all": {
        "mean_pp": 35.204081632653065,
        "ci95_pp": [
          27.55102040816326,
          42.857142857142854
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F2_room": {
    "gate": {
      "n": 400,
      "s_star": 392,
      "gain_s_star_pp": 25.255102040816325,
      "gain_ci": [
        20.66326530612245,
        29.846938775510207
      ],
      "G_comp_pp": 24.5,
      "G_comp_ci": [
        19.75,
        29.25
      ],
      "acc_q2": {
        "1": 0.67,
        "2": 0.8875,
        "3": 0.93,
        "4": 0.915
      },
      "acc_q1a_l1": 0.9975,
      "acc_q1b_l1": 0.9875,
      "pass": true
    },
    "rescue": {
      "targets": 111,
      "paired": 111,
      "rescue": {
        "all": 0.5225225225225225,
        "all_shuffled": 0.2882882882882883
      },
      "delta_all": {
        "mean_pp": 23.423423423423422,
        "ci95_pp": [
          13.513513513513514,
          33.33333333333333
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F3_car": {
    "gate": {
      "n": 400,
      "s_star": 386,
      "gain_s_star_pp": 18.911917098445596,
      "gain_ci": [
        15.025906735751295,
        22.797927461139896
      ],
      "G_comp_pp": 16.75,
      "G_comp_ci": [
        12.75,
        20.75
      ],
      "acc_q2": {
        "1": 0.8,
        "2": 0.985,
        "3": 1.0,
        "4": 0.9975
      },
      "acc_q1a_l1": 0.9775,
      "acc_q1b_l1": 0.99,
      "pass": true
    },
    "rescue": {
      "targets": 80,
      "paired": 80,
      "rescue": {
        "all": 0.7125,
        "all_shuffled": 0.45
      },
      "delta_all": {
        "mean_pp": 26.25,
        "ci95_pp": [
          13.750000000000002,
          38.75
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro14/F4_story": {
    "gate": {
      "n": 400,
      "s_star": 300,
      "gain_s_star_pp": 29.666666666666668,
      "gain_ci": [
        23.666666666666668,
        35.66666666666667
      ],
      "G_comp_pp": 13.5,
      "G_comp_ci": [
        7.249999999999999,
        19.5
      ],
      "acc_q2": {
        "1": 0.43,
        "2": 0.5975,
        "3": 0.7675,
        "4": 0.7625
      },
      "acc_q1a_l1": 0.95,
      "acc_q1b_l1": 0.835,
      "pass": true
    },
    "rescue": {
      "targets": 152,
      "paired": 152,
      "rescue": {
        "all": 0.5328947368421053,
        "all_shuffled": 0.32894736842105265
      },
      "delta_all": {
        "mean_pp": 20.394736842105264,
        "ci95_pp": [
          10.526315789473683,
          30.263157894736842
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F1_locker": {
    "gate": {
      "n": 400,
      "s_star": 364,
      "gain_s_star_pp": 35.16483516483517,
      "gain_ci": [
        30.21978021978022,
        40.10989010989011
      ],
      "G_comp_pp": 31.5,
      "G_comp_ci": [
        26.75,
        36.25
      ],
      "acc_q2": {
        "1": 0.585,
        "2": 0.925,
        "3": 0.9825,
        "4": 0.97
      },
      "acc_q1a_l1": 0.985,
      "acc_q1b_l1": 0.93,
      "pass": true
    },
    "rescue": {
      "targets": 159,
      "paired": 159,
      "rescue": {
        "all": 0.7861635220125787,
        "all_shuffled": 0.2578616352201258
      },
      "delta_all": {
        "mean_pp": 52.83018867924528,
        "ci95_pp": [
          44.0251572327044,
          61.63522012578616
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F2_room": {
    "gate": {
      "n": 400,
      "s_star": 395,
      "gain_s_star_pp": 31.89873417721519,
      "gain_ci": [
        27.335443037974688,
        36.708860759493675
      ],
      "G_comp_pp": 31.25,
      "G_comp_ci": [
        26.5,
        36.0
      ],
      "acc_q2": {
        "1": 0.665,
        "2": 0.9275,
        "3": 0.9825,
        "4": 0.9775
      },
      "acc_q1a_l1": 0.995,
      "acc_q1b_l1": 1.0,
      "pass": true
    },
    "rescue": {
      "targets": 130,
      "paired": 130,
      "rescue": {
        "all": 0.6230769230769231,
        "all_shuffled": 0.14615384615384616
      },
      "delta_all": {
        "mean_pp": 47.69230769230769,
        "ci95_pp": [
          36.92307692307693,
          57.692307692307686
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F3_car": {
    "gate": {
      "n": 400,
      "s_star": 400,
      "gain_s_star_pp": 15.75,
      "gain_ci": [
        12.25,
        19.5
      ],
      "G_comp_pp": 15.75,
      "G_comp_ci": [
        12.25,
        19.5
      ],
      "acc_q2": {
        "1": 0.8425,
        "2": 0.98,
        "3": 1.0,
        "4": 1.0
      },
      "acc_q1a_l1": 1.0,
      "acc_q1b_l1": 1.0,
      "pass": true
    },
    "rescue": {
      "targets": 63,
      "paired": 63,
      "rescue": {
        "all": 0.7301587301587301,
        "all_shuffled": 0.20634920634920634
      },
      "delta_all": {
        "mean_pp": 52.38095238095239,
        "ci95_pp": [
          39.682539682539684,
          65.07936507936508
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  },
  "ouro26/F4_story": {
    "gate": {
      "n": 400,
      "s_star": 392,
      "gain_s_star_pp": 38.775510204081634,
      "gain_ci": [
        33.92857142857143,
        43.62244897959184
      ],
      "G_comp_pp": 38.25,
      "G_comp_ci": [
        33.5,
        43.0
      ],
      "acc_q2": {
        "1": 0.58,
        "2": 0.9175,
        "3": 0.9775,
        "4": 0.9625
      },
      "acc_q1a_l1": 0.995,
      "acc_q1b_l1": 0.99,
      "pass": true
    },
    "rescue": {
      "targets": 159,
      "paired": 159,
      "rescue": {
        "all": 0.6037735849056604,
        "all_shuffled": 0.20754716981132076
      },
      "delta_all": {
        "mean_pp": 39.62264150943396,
        "ci95_pp": [
          30.81761006289308,
          48.42767295597484
        ]
      },
      "rescue_pass": true,
      "descriptive_only": false
    }
  }
}
```
