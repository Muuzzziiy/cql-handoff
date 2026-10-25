"""Independent recomputation of the forced-choice K/V primary (does not import ouro_natural_kv_fc)."""
import json
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[1] / 'experiments/2026-10-12-ouro-natural-kv-fc'

def main():
    S = json.loads((OUT / 'SUMMARY.json').read_text())
    for m in ('ouro14', 'ouro26'):
        R = [json.loads(x) for x in (OUT / f'{m}_ROWS.jsonl').read_text().splitlines() if x.strip()]
        for x in R:
            for t in ('two_hop', 'bridge_given'):
                for arm, d in x[t].items():
                    for v in d.values():
                        s = np.array(v['scores'])
                        assert (int(np.argmax(s)) == 0) == v['correct'] and abs(s[0] - s[1:].max() - v['margin']) < 1e-12
        d = np.mean([x['two_hop']['K_facts']['3']['margin'] - x['two_hop']['V_facts']['3']['margin'] for x in R])
        assert abs(d - S[m]['primary_V_vs_K_margin']['mean']) < 1e-09
    rep = dict(status='PASS', scoring_rederived=True, primary_mean=True)
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(rep, indent=1))
    print(rep)
if __name__ == '__main__':
    main()
