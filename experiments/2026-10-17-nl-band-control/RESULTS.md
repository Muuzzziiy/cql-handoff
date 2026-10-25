# Preprint results: 2026-10-17-nl-band-control

Paper: section 7 of [paper materials archive](../../paper/updated-CLQ.zip).

All heads in the last quarter of Ouro-2.6B layers, with the original shuffled donor and an independent donor map. Keep the strong shuffled-donor baseline.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "n": 134,
  "counts": {
    "arm1": 84,
    "arm2": 44,
    "arm3": 47,
    "all_layers_5373": 45
  },
  "rescue": {
    "arm1": 62.68656716417911,
    "arm2": 32.83582089552239,
    "arm3": 35.07462686567165,
    "all_layers_5373": 33.582089552238806
  },
  "C1": {
    "mean_pp": 29.850746268656714,
    "ci95": [
      20.8955223880597,
      38.80597014925373
    ],
    "supported": true
  },
  "arm3_minus_arm2": {
    "mean_pp": 2.2388059701492535,
    "ci95": [
      -4.477611940298507,
      8.955223880597014
    ]
  },
  "arm1_minus_arm3": {
    "mean_pp": 27.611940298507463,
    "ci95": [
      19.402985074626866,
      35.82089552238806
    ]
  },
  "arm1_minus_all_layers": {
    "mean_pp": 29.1044776119403,
    "ci95": [
      20.8955223880597,
      37.3134328358209
    ],
    "band_only": 42,
    "all_only": 3,
    "both": 42
  },
  "margin": {
    "native1": -1.6049159240366808,
    "arm1": 0.3754585291912307,
    "arm2": -0.4477778228361215,
    "arm3": -0.4543731684115396,
    "native3": 1.8040126125091938
  },
  "by_dataset": {
    "2wiki": {
      "n": 87,
      "arm1": 68.96551724137932,
      "arm2": 44.827586206896555,
      "arm3": 43.67816091954023
    },
    "musique": {
      "n": 47,
      "arm1": 51.06382978723404,
      "arm2": 10.638297872340425,
      "arm3": 19.148936170212767
    }
  }
}
```
