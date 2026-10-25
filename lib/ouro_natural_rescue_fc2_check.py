"""Independent recomputation for the powered 2.6B forced-choice rescue (does not import its analysis code)."""
import json
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[1] / 'experiments/2026-10-12-ouro26-natural-rescue-fc-powered'

def lines(p):
    return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]

def main():
    S = json.loads((OUT / 'SUMMARY.json').read_text())
    sc = lines(OUT / 'ouro26_SCREEN.jsonl')
    R = lines(OUT / 'ouro26_ROWS.jsonl')
    for s in sc:
        for blk in (s['two_hop'], s['bridge']):
            for v in blk.values():
                x = np.array(v['scores'])
                assert (int(np.argmax(x)) == 0) == v['correct'] and abs(x[0] - x[1:].max() - v['margin']) < 1e-12
    assert [s['key'] for s in sc if not s['two_hop']['1']['correct'] and s['two_hop']['3']['correct']] == [r['key'] for r in R]
    d = np.mean([r['same']['correct'] - r['shuffled']['correct'] for r in R])
    assert abs(100 * d - S['primary_full']['delta_pp']) < 1e-09
    rep = dict(status='PASS', scoring_rederived=True, targets_reselected=True, delta_recomputed=True)
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(rep, indent=1))
    print(rep)
if __name__ == '__main__':
    main()
