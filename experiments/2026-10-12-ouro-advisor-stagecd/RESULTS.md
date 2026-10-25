# Preprint results: 2026-10-12-ouro-advisor-stagecd

Paper: section 3–4, 6; Tables 2, 5, 7 of [paper materials archive](../../paper/updated-CLQ.zip).

Native one-hop/two-hop gate; Q, K and V freezes with matched-size controls; same-example and shuffled late-query rescue at loop 1 and loop 2. Original bootstrap seed and Bonferroni-4 rescue intervals are retained.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14": {
    "S_star_n": 364,
    "full": {
      "two_hop_gain_pp": {
        "mean": 35.5,
        "ci95": [
          30.5,
          40.5
        ]
      },
      "G_comp_pp": {
        "mean": 28.749999999999996,
        "ci95": [
          23.5,
          34.0
        ]
      },
      "I_Q": {
        "rho": -0.11971830952192027,
        "rho_ci95": [
          -0.2290116087170654,
          -0.02325581388137732
        ],
        "SCD_pp": 27.500000000000004,
        "SCD_ci95": [
          22.249999999999996,
          32.75
        ],
        "one_hop_loss_pp": 12.25,
        "one_hop_loss_ci95": [
          8.75,
          15.75
        ],
        "two_hop_margin_R": 0.052265625
      },
      "I_K": {
        "rho": 0.7183098571315215,
        "rho_ci95": [
          0.6241134734067703,
          0.8059724082793168
        ],
        "SCD_pp": 5.75,
        "SCD_ci95": [
          2.25,
          9.25
        ],
        "one_hop_loss_pp": 4.25,
        "one_hop_loss_ci95": [
          2.5,
          6.25
        ],
        "two_hop_margin_R": 1.779453125
      },
      "I_V": {
        "rho": 0.007042253501289427,
        "rho_ci95": [
          -0.16176470540657437,
          0.14765100631503084
        ],
        "SCD_pp": 30.75,
        "SCD_ci95": [
          25.75,
          35.75000000000001
        ],
        "one_hop_loss_pp": 4.5,
        "one_hop_loss_ci95": [
          2.5,
          6.75
        ],
        "two_hop_margin_R": 0.362578125
      },
      "C_Q": {
        "rho": 1.0352112646895457,
        "rho_ci95": [
          1.0069444416473765,
          1.0725806417013528
        ],
        "SCD_pp": -1.25,
        "SCD_ci95": [
          -2.5,
          -0.25
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.133046875
      },
      "C_K": {
        "rho": 0.9647887296766515,
        "rho_ci95": [
          0.8968253939783319,
          1.033557044205216
        ],
        "SCD_pp": 1.25,
        "SCD_ci95": [
          -1.25,
          3.5000000000000004
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.75
        ],
        "two_hop_margin_R": 3.05671875
      },
      "C_V": {
        "rho": 0.9788732366792302,
        "rho_ci95": [
          0.906034186844046,
          1.0551181069130138
        ],
        "SCD_pp": 0.75,
        "SCD_ci95": [
          -1.7500000000000002,
          3.5000000000000004
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 2.937734375
      },
      "Native_two_hop_margin": {
        "loop1": 0.17841796875,
        "loop2": 1.55671875,
        "loop3": 3.10609375,
        "loop4": 2.1121875
      },
      "caseA": {
        "rho_Q_le_0_5": true,
        "rho_K_ge_0_8": false,
        "rho_V_ge_0_8": false,
        "K_loss_le_3pp": false,
        "V_loss_le_3pp": false,
        "SCD_Q_gt_K": true,
        "SCD_Q_gt_V": false
      }
    },
    "S_star": {
      "two_hop_gain_pp": {
        "mean": 33.791208791208796,
        "ci95": [
          28.846153846153843,
          39.010989010989015
        ]
      },
      "G_comp_pp": {
        "mean": 33.791208791208796,
        "ci95": [
          28.846153846153843,
          39.010989010989015
        ]
      },
      "I_Q": {
        "rho": -0.13008130042805208,
        "rho_ci95": [
          -0.25641592840509475,
          -0.02142857137285714
        ],
        "SCD_pp": 28.57142857142857,
        "SCD_ci95": [
          23.35164835164835,
          33.791208791208796
        ],
        "one_hop_loss_pp": 9.615384615384617,
        "one_hop_loss_ci95": [
          6.593406593406594,
          12.637362637362637
        ],
        "two_hop_margin_R": 0.20763221153846154
      },
      "I_K": {
        "rho": 0.6991869898007799,
        "rho_ci95": [
          0.5968992231219277,
          0.7916736557186246
        ],
        "SCD_pp": 6.868131868131869,
        "SCD_ci95": [
          3.5714285714285707,
          10.439560439560438
        ],
        "one_hop_loss_pp": 3.296703296703297,
        "one_hop_loss_ci95": [
          1.6483516483516485,
          5.21978021978022
        ],
        "two_hop_margin_R": 1.9541552197802199
      },
      "I_V": {
        "rho": -0.01626016255350651,
        "rho_ci95": [
          -0.2058940235451247,
          0.14285714248571427
        ],
        "SCD_pp": 31.043956043956044,
        "SCD_ci95": [
          25.82417582417583,
          36.26373626373626
        ],
        "one_hop_loss_pp": 3.296703296703297,
        "one_hop_loss_ci95": [
          1.6483516483516485,
          5.21978021978022
        ],
        "two_hop_margin_R": 0.5816449175824175
      },
      "C_Q": {
        "rho": 1.0406504034244166,
        "rho_ci95": [
          1.0079365050246913,
          1.0840336101295105
        ],
        "SCD_pp": -1.3736263736263736,
        "SCD_ci95": [
          -2.7472527472527473,
          -0.27472527472527475
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.3436641483516483
      },
      "C_K": {
        "rho": 0.9674796719336373,
        "rho_ci95": [
          0.8999999972699999,
          1.0357142823482142
        ],
        "SCD_pp": 1.098901098901099,
        "SCD_ci95": [
          -1.098901098901099,
          3.296703296703297
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.2683722527472527
      },
      "C_V": {
        "rho": 0.9593495906568841,
        "rho_ci95": [
          0.8833333306538889,
          1.0359728406169273
        ],
        "SCD_pp": 1.3736263736263736,
        "SCD_ci95": [
          -1.098901098901099,
          3.8461538461538463
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.1226820054945055
      },
      "Native_two_hop_margin": {
        "loop1": 0.2628133585164835,
        "loop2": 1.8164491758241759,
        "loop3": 3.319368131868132,
        "loop4": 2.32134271978022
      },
      "caseA": {
        "rho_Q_le_0_5": true,
        "rho_K_ge_0_8": false,
        "rho_V_ge_0_8": false,
        "K_loss_le_3pp": false,
        "V_loss_le_3pp": false,
        "SCD_Q_gt_K": true,
        "SCD_Q_gt_V": false
      }
    },
    "stage_d": {
      "r1": {
        "targets": 245,
        "paired": 245,
        "rescue_same": 0.8979591836734694,
        "rescue_same_ci95": [
          0.8571428571428571,
          0.9346938775510204
        ],
        "rescue_shuffled": 0.23673469387755103,
        "delta_rescue_pp": 66.12244897959184,
        "rescue_same_loop_donor": 0.09795918367346938,
        "delta_ci95_pp": [
          60.0,
          72.24489795918367
        ],
        "delta_bonferroni4_pp": [
          58.36734693877551,
          73.87755102040816
        ],
        "donor_same_answer": 76,
        "margin_shift": 0.8090370956732302,
        "margin_shift_ci95": [
          0.7523681570559131,
          0.8672309205969985
        ],
        "directional_still_correct": 0.6216216216216216,
        "directional_n": 555,
        "success": true
      },
      "r2": {
        "targets": 91,
        "paired": 91,
        "rescue_same": 1.0,
        "rescue_same_ci95": [
          1.0,
          1.0
        ],
        "rescue_shuffled": 0.1978021978021978,
        "delta_rescue_pp": 80.21978021978022,
        "rescue_same_loop_donor": 0.06593406593406594,
        "delta_ci95_pp": [
          71.42857142857143,
          87.91208791208791
        ],
        "delta_bonferroni4_pp": [
          69.23076923076923,
          90.10989010989012
        ],
        "donor_same_answer": 26,
        "margin_shift": 3.6229395604395602,
        "margin_shift_ci95": [
          3.3152472527472527,
          3.9385388049450545
        ],
        "directional_still_correct": 0.8054054054054054,
        "directional_n": 555,
        "success": true
      }
    }
  },
  "ouro26": {
    "S_star_n": 393,
    "full": {
      "two_hop_gain_pp": {
        "mean": 34.25,
        "ci95": [
          29.5,
          39.0
        ]
      },
      "G_comp_pp": {
        "mean": 33.0,
        "ci95": [
          28.499999999999996,
          37.75
        ]
      },
      "I_Q": {
        "rho": -0.13868613098193827,
        "rho_ci95": [
          -0.2639999991552,
          -0.02962962954183813
        ],
        "SCD_pp": 36.0,
        "SCD_ci95": [
          31.25,
          40.75
        ],
        "one_hop_loss_pp": 3.0,
        "one_hop_loss_ci95": [
          1.5,
          4.75
        ],
        "two_hop_margin_R": 0.574921875
      },
      "I_K": {
        "rho": 0.5401459838243912,
        "rho_ci95": [
          0.42104218753729733,
          0.6439393919880624
        ],
        "SCD_pp": 12.5,
        "SCD_ci95": [
          9.000000000000002,
          16.0
        ],
        "one_hop_loss_pp": 3.25,
        "one_hop_loss_ci95": [
          1.7500000000000002,
          5.0
        ],
        "two_hop_margin_R": 1.46890625
      },
      "I_V": {
        "rho": -0.6204379543928817,
        "rho_ci95": [
          -0.8813559292157426,
          -0.41290322474089486
        ],
        "SCD_pp": 15.750000000000004,
        "SCD_ci95": [
          11.500000000000005,
          20.0
        ],
        "one_hop_loss_pp": 39.75,
        "one_hop_loss_ci95": [
          35.0,
          44.5
        ],
        "two_hop_margin_R": -1.12421875
      },
      "C_Q": {
        "rho": 0.9927007270286109,
        "rho_ci95": [
          0.9763779496806992,
          0.9999999973509933
        ],
        "SCD_pp": 0.25,
        "SCD_ci95": [
          0.0,
          0.75
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.8778125
      },
      "C_K": {
        "rho": 0.978102186925249,
        "rho_ci95": [
          0.9508196690137058,
          0.9999999970149253
        ],
        "SCD_pp": 0.75,
        "SCD_ci95": [
          0.0,
          1.7500000000000002
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.820078125
      },
      "C_V": {
        "rho": 0.9927007270286109,
        "rho_ci95": [
          0.9668818958930427,
          1.016129028980229
        ],
        "SCD_pp": 0.25,
        "SCD_ci95": [
          -0.5,
          1.25
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.433359375
      },
      "Native_two_hop_margin": {
        "loop1": 0.5015625,
        "loop2": 3.27796875,
        "loop3": 3.903671875,
        "loop4": 3.23203125
      },
      "caseA": {
        "rho_Q_le_0_5": true,
        "rho_K_ge_0_8": false,
        "rho_V_ge_0_8": false,
        "K_loss_le_3pp": false,
        "V_loss_le_3pp": false,
        "SCD_Q_gt_K": true,
        "SCD_Q_gt_V": true
      }
    },
    "S_star": {
      "two_hop_gain_pp": {
        "mean": 33.33333333333333,
        "ci95": [
          28.75318066157761,
          38.16793893129771
        ]
      },
      "G_comp_pp": {
        "mean": 33.33333333333333,
        "ci95": [
          28.75318066157761,
          38.16793893129771
        ]
      },
      "I_Q": {
        "rho": -0.1450381675038168,
        "rho_ci95": [
          -0.276785713314493,
          -0.031249999904052733
        ],
        "SCD_pp": 35.6234096692112,
        "SCD_ci95": [
          30.788804071246823,
          40.458015267175576
        ],
        "one_hop_loss_pp": 2.5445292620865136,
        "one_hop_loss_ci95": [
          1.0178117048346056,
          4.325699745547073
        ],
        "two_hop_margin_R": 0.6271469465648855
      },
      "I_K": {
        "rho": 0.549618318961832,
        "rho_ci95": [
          0.4263565878483865,
          0.6573426555361143
        ],
        "SCD_pp": 11.704834605597966,
        "SCD_ci95": [
          8.396946564885496,
          15.267175572519081
        ],
        "one_hop_loss_pp": 3.307888040712468,
        "one_hop_loss_ci95": [
          1.7811704834605597,
          5.089058524173027
        ],
        "two_hop_margin_R": 1.4947519083969465
      },
      "I_V": {
        "rho": -0.6717557231755725,
        "rho_ci95": [
          -0.9464285681076212,
          -0.45454545329624924
        ],
        "SCD_pp": 16.030534351145043,
        "SCD_ci95": [
          11.70483460559797,
          20.356234096692116
        ],
        "one_hop_loss_pp": 39.69465648854962,
        "one_hop_loss_ci95": [
          34.86005089058524,
          44.529262086513995
        ],
        "two_hop_margin_R": -1.1184001272264632
      },
      "C_Q": {
        "rho": 0.9923664092366412,
        "rho_ci95": [
          0.9749999968068749,
          0.999999997289655
        ],
        "SCD_pp": 0.2544529262086514,
        "SCD_ci95": [
          0.0,
          0.7633587786259541
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.8964694656488548
      },
      "C_K": {
        "rho": 0.9847328214732824,
        "rho_ci95": [
          0.9609374970496215,
          0.9999999971521738
        ],
        "SCD_pp": 0.5089058524173028,
        "SCD_ci95": [
          0.0,
          1.2722646310432568
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.8454993638676847
      },
      "C_V": {
        "rho": 0.999999997,
        "rho_ci95": [
          0.9777777749313579,
          1.0232558108361276
        ],
        "SCD_pp": 0.0,
        "SCD_ci95": [
          -0.7633587786259541,
          0.7633587786259541
        ],
        "one_hop_loss_pp": 0.0,
        "one_hop_loss_ci95": [
          0.0,
          0.0
        ],
        "two_hop_margin_R": 3.4533237913486006
      },
      "Native_two_hop_margin": {
        "loop1": 0.5415871501272265,
        "loop2": 3.312977099236641,
        "loop3": 3.922312340966921,
        "loop4": 3.2509541984732824
      },
      "caseA": {
        "rho_Q_le_0_5": true,
        "rho_K_ge_0_8": false,
        "rho_V_ge_0_8": false,
        "K_loss_le_3pp": false,
        "V_loss_le_3pp": false,
        "SCD_Q_gt_K": true,
        "SCD_Q_gt_V": true
      }
    },
    "stage_d": {
      "r1": {
        "targets": 223,
        "paired": 223,
        "rescue_same": 0.968609865470852,
        "rescue_same_ci95": [
          0.9461883408071748,
          0.9910313901345291
        ],
        "rescue_shuffled": 0.2062780269058296,
        "delta_rescue_pp": 76.23318385650224,
        "rescue_same_loop_donor": 0.18385650224215247,
        "delta_ci95_pp": [
          70.4035874439462,
          81.61434977578476
        ],
        "delta_bonferroni4_pp": [
          69.05829596412556,
          82.95964125560538
        ],
        "donor_same_answer": 70,
        "margin_shift": 2.6764293721973096,
        "margin_shift_ci95": [
          2.5372757847533634,
          2.817057875560538
        ],
        "directional_still_correct": 0.7090301003344481,
        "directional_n": 598,
        "success": true
      },
      "r2": {
        "targets": 12,
        "paired": 12,
        "rescue_same": 1.0,
        "rescue_same_ci95": [
          1.0,
          1.0
        ],
        "rescue_shuffled": 0.25,
        "delta_rescue_pp": 75.0,
        "rescue_same_loop_donor": 0.16666666666666666,
        "delta_ci95_pp": [
          50.0,
          100.0
        ],
        "delta_bonferroni4_pp": [
          41.66666666666667,
          100.0
        ],
        "donor_same_answer": 2,
        "margin_shift": 3.2109375,
        "margin_shift_ci95": [
          2.59375,
          3.8255208333333335
        ],
        "directional_still_correct": 0.9749163879598662,
        "directional_n": 598,
        "success": true
      }
    }
  }
}
```
