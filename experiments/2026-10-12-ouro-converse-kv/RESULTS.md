# Preprint results: 2026-10-12-ouro-converse-kv

Paper: section 5.1; Table 4 of [paper materials archive](../../paper/updated-CLQ.zip).

Compare late Q with late K, V and KV at the used facts, and late KV at all positions except the final query. Same-item and shuffled-donor controls and the original primary Bonferroni-2 interval are retained.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14": {
    "targets": 263,
    "primary_Q_minus_KV_F": {
      "mean_pp": 60.45627376425855,
      "ci_bonf2_pp": [
        52.851711026615966,
        68.06083650190115
      ],
      "supported": true
    },
    "rates": {
      "Q_late": {
        "rescue": 0.8669201520912547,
        "n": 263,
        "margin": 0.2774091945401616
      },
      "K_late_F": {
        "rescue": 0.24334600760456274,
        "n": 263,
        "margin": -0.42429375648498535
      },
      "V_late_F": {
        "rescue": 0.22433460076045628,
        "n": 263,
        "margin": -0.49012321211086024
      },
      "KV_late_F": {
        "rescue": 0.2623574144486692,
        "n": 263,
        "margin": -0.3117944985741445
      },
      "KV_late_mem": {
        "rescue": 0.13688212927756654,
        "n": 263,
        "margin": -0.3947619739140848
      },
      "KV_late_F_donor": {
        "rescue": 0.20912547528517111,
        "n": 263,
        "margin": -0.522309626009981
      },
      "Q_late_donor": {
        "rescue": 0.26996197718631176,
        "n": 263,
        "margin": -0.22739082597507723
      },
      "native1": {
        "margin": -0.5284576996197718
      },
      "native3": {
        "margin": 2.9220532319391634
      }
    },
    "KV_F_minus_donor": {
      "mean_pp": 5.323193916349809,
      "ci95_pp": [
        0.7604562737642585,
        9.885931558935361
      ]
    }
  },
  "ouro26": {
    "targets": 223,
    "primary_Q_minus_KV_F": {
      "mean_pp": 65.02242152466367,
      "ci_bonf2_pp": [
        57.847533632286996,
        72.19730941704036
      ],
      "supported": true
    },
    "rates": {
      "Q_late": {
        "rescue": 0.9820627802690582,
        "n": 223,
        "margin": 1.961182735426009
      },
      "K_late_F": {
        "rescue": 0.04932735426008968,
        "n": 223,
        "margin": -0.8352017937219731
      },
      "V_late_F": {
        "rescue": 0.2242152466367713,
        "n": 223,
        "margin": -0.41828405269058294
      },
      "KV_late_F": {
        "rescue": 0.33183856502242154,
        "n": 223,
        "margin": -0.22554652466367714
      },
      "KV_late_mem": {
        "rescue": 0.11210762331838565,
        "n": 223,
        "margin": -0.929241676501629
      },
      "KV_late_F_donor": {
        "rescue": 0.09417040358744394,
        "n": 223,
        "margin": -0.9314742152466368
      },
      "Q_late_donor": {
        "rescue": 0.273542600896861,
        "n": 223,
        "margin": -1.1939461883408071
      },
      "native1": {
        "margin": -0.804652466367713
      },
      "native3": {
        "margin": 3.4649663677130045
      }
    },
    "KV_F_minus_donor": {
      "mean_pp": 23.766816143497756,
      "ci95_pp": [
        17.040358744394617,
        30.493273542600896
      ]
    }
  }
}
```
