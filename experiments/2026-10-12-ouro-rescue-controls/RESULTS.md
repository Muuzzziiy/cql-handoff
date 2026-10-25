# Preprint results: 2026-10-12-ouro-rescue-controls

Paper: section 4, 6; Table 5 of [paper materials archive](../../paper/updated-CLQ.zip).

Same-item all-layer query replication and V_F / KV_F / KV_memory co-freezes. The primary KV_F minus V_F contrast retains the original Bonferroni-2 correction.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14": {
    "A1": {
      "all": 0.8165137614678899
    },
    "B": {
      "V_F": {
        "rho": 0.03381642512077295,
        "ci95": [
          -0.09500595238095239,
          0.14851819641423572
        ]
      },
      "KV_F": {
        "rho": -0.019323671497584544,
        "ci95": [
          -0.14500000000000002,
          0.09049773755656108
        ]
      },
      "KV_mem": {
        "rho": 0.34782608695652173,
        "ci95": [
          0.2718446601941748,
          0.42396313364055294
        ]
      },
      "primary_KV_F_minus_V_F": {
        "mean": -0.053140096618357495,
        "ci_family": [
          -0.17351808459504925,
          0.0670424634722821
        ],
        "supported": false
      },
      "native_gain_pp": 34.5
    }
  },
  "ouro26": {
    "A1": {
      "all": 0.965
    },
    "B": {
      "V_F": {
        "rho": -0.6482412060301508,
        "ci95": [
          -0.8702702702702702,
          -0.4644507447528778
        ]
      },
      "KV_F": {
        "rho": 0.41206030150753764,
        "ci95": [
          0.3128484457814067,
          0.505644194756552
        ]
      },
      "KV_mem": {
        "rho": -0.05527638190954774,
        "ci95": [
          -0.14044943820224717,
          0.021164021164021166
        ]
      },
      "primary_KV_F_minus_V_F": {
        "mean": 1.0603015075376885,
        "ci_family": [
          0.8539823008849557,
          1.298342541436464
        ],
        "supported": true
      },
      "native_gain_pp": 33.166666666666664
    }
  }
}
```
