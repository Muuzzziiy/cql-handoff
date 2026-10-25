# Preprint results: 2026-10-12-ouro26-natural-rescue-fc-powered

Paper: section 7 of [paper materials archive](../../paper/updated-CLQ.zip).

The frozen 1,105-item natural QA set, candidate ranking, target screen, same-item query, shuffled donor and same-loop donor. Gold answer is candidate zero; candidates use length-normalized log-likelihood.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "items": 1105,
  "native_two_hop_acc": {
    "1": 0.8289592760180996,
    "3": 0.9438914027149321
  },
  "primary_full": {
    "n": 134,
    "rescue_same": 0.3358208955223881,
    "rescue_shuffled": 0.19402985074626866,
    "rescue_same_loop_donor": 0.029850746268656716,
    "delta_pp": 14.17910447761194,
    "ci95_pp": [
      7.462686567164178,
      20.8955223880597
    ],
    "margin": {
      "native1": -1.6049159240366808,
      "same": -0.4640927528267476,
      "shuffled": -1.257736131326476,
      "native3": 1.8040126125091938
    },
    "pass": true
  },
  "S_star": {
    "n": 34,
    "rescue_same": 0.3235294117647059,
    "rescue_shuffled": 0.20588235294117646,
    "rescue_same_loop_donor": 0.058823529411764705,
    "delta_pp": 11.76470588235294,
    "ci95_pp": [
      2.941176470588235,
      23.52941176470588
    ],
    "margin": {
      "native1": -0.5202709541601294,
      "same": -0.09310285834705129,
      "shuffled": -0.5054068740676431,
      "native3": 1.3237211897092707
    }
  },
  "2wiki": {
    "n": 87,
    "rescue_same": 0.41379310344827586,
    "rescue_shuffled": 0.26436781609195403,
    "rescue_same_loop_donor": 0.034482758620689655,
    "delta_pp": 14.942528735632186,
    "ci95_pp": [
      6.896551724137931,
      24.137931034482758
    ],
    "margin": {
      "native1": -1.8047850488246173,
      "same": -0.2784402452666184,
      "shuffled": -1.091404022841618,
      "native3": 1.97163542163098
    }
  },
  "musique": {
    "n": 47,
    "rescue_same": 0.19148936170212766,
    "rescue_shuffled": 0.06382978723404255,
    "rescue_same_loop_donor": 0.02127659574468085,
    "delta_pp": 12.76595744680851,
    "ci95_pp": [
      4.25531914893617,
      23.404255319148938
    ],
    "margin": {
      "native1": -1.2349454164505005,
      "same": -0.8077473944806038,
      "shuffled": -1.5656274810750435,
      "native3": 1.4937320934965255
    }
  }
}
```
