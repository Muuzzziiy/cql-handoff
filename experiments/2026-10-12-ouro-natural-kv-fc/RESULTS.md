# Preprint results: 2026-10-12-ouro-natural-kv-fc

Paper: section 7 of [paper materials archive](../../paper/updated-CLQ.zip).

Natural four-candidate Q/K/V freezes against the bridge-given question. Q freezes the question span; K/V freeze the fact span. Composition selectivity remains near zero.

The following values are an unchanged projection of the saved observations used for the preprint. A release-time CPU checker verifies the published contrasts. This does not constitute a fresh GPU experiment.

```json
{
  "ouro14": {
    "n": 357,
    "primary_V_vs_K_margin": {
      "mean": 0.08913901957477174,
      "ci_bonf2": [
        -0.0018934929440794519,
        0.1804503140423228
      ],
      "supported": false
    },
    "accuracy": {
      "two_hop/Native/loop1": 0.7759103641456583,
      "two_hop/Native/loop3": 0.927170868347339,
      "two_hop/Q_question/loop1": 0.7759103641456583,
      "two_hop/Q_question/loop3": 0.7927170868347339,
      "two_hop/K_facts/loop1": 0.7759103641456583,
      "two_hop/K_facts/loop3": 0.9131652661064426,
      "two_hop/V_facts/loop1": 0.7759103641456583,
      "two_hop/V_facts/loop3": 0.8907563025210085,
      "bridge_given/Native/loop1": 0.8403361344537815,
      "bridge_given/Native/loop3": 0.9467787114845938,
      "bridge_given/Q_question/loop1": 0.8403361344537815,
      "bridge_given/Q_question/loop3": 0.7927170868347339,
      "bridge_given/K_facts/loop1": 0.8403361344537815,
      "bridge_given/K_facts/loop3": 0.9215686274509803,
      "bridge_given/V_facts/loop1": 0.8403361344537815,
      "bridge_given/V_facts/loop3": 0.9131652661064426
    },
    "rho": {
      "Q_question": 0.11111111111111112,
      "K_facts": 0.9074074074074076,
      "V_facts": 0.7592592592592593
    },
    "SCD_vs_bridge": {
      "Q_question": -0.019607843137254916,
      "K_facts": -0.011204481792717087,
      "V_facts": 0.0028011204481792756
    },
    "native_gain_pp": 15.126050420168067
  },
  "ouro26": {
    "n": 357,
    "primary_V_vs_K_margin": {
      "mean": 0.7720826852346668,
      "ci_bonf2": [
        0.6363264034058721,
        0.9179004723060074
      ],
      "supported": true
    },
    "accuracy": {
      "two_hop/Native/loop1": 0.8263305322128851,
      "two_hop/Native/loop3": 0.938375350140056,
      "two_hop/Q_question/loop1": 0.8263305322128851,
      "two_hop/Q_question/loop3": 0.8095238095238095,
      "two_hop/K_facts/loop1": 0.8263305322128851,
      "two_hop/K_facts/loop3": 0.9187675070028011,
      "two_hop/V_facts/loop1": 0.8263305322128851,
      "two_hop/V_facts/loop3": 0.8263305322128851,
      "bridge_given/Native/loop1": 0.8543417366946778,
      "bridge_given/Native/loop3": 0.9523809523809523,
      "bridge_given/Q_question/loop1": 0.8543417366946778,
      "bridge_given/Q_question/loop3": 0.834733893557423,
      "bridge_given/K_facts/loop1": 0.8543417366946778,
      "bridge_given/K_facts/loop3": 0.9355742296918768,
      "bridge_given/V_facts/loop1": 0.8543417366946778,
      "bridge_given/V_facts/loop3": 0.8375350140056023
    },
    "rho": {
      "Q_question": -0.15,
      "K_facts": 0.825,
      "V_facts": 0.0
    },
    "SCD_vs_bridge": {
      "Q_question": 0.011204481792717075,
      "K_facts": 0.002801120448179272,
      "V_facts": -0.0028011204481792618
    },
    "native_gain_pp": 11.204481792717088
  }
}
```
