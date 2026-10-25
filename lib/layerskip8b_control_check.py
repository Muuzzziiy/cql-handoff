"""Independent check of the LayerSkip control: recompute targets per exit, Δ_rescue and L1 from BEHAVIOR/ROWS."""
import json
import numpy as np
from .common import ROOT, read, write
OUT = ROOT / 'experiments/2026-10-16-layerskip8b-control'

def main():
    cfg = read(OUT / 'CONFIG.json')
    S = read(OUT / 'SUMMARY.json')
    ok = True
    mine = {}
    B = {json.loads(x)['graph']: json.loads(x) for x in open(OUT / 'BEHAVIOR.jsonl')}
    L = max((int(k[1:]) for k in next(iter(B.values()))['q2']))
    R = [json.loads(x) for x in open(OUT / 'ROWS.jsonl')]
    for E in cfg['exits']:
        if S['per_exit'][str(E)].get('not_run'):
            continue
        tg = sorted((g for g, r in B.items() if not r['q2'][f'e{E}'] and r['q2'][f'e{L}']))
        rr = [r for r in R if r['exit'] == E]
        ok &= sorted((r['graph'] for r in rr)) == tg
        p = [r for r in rr if 'Qdeep_shuf' in r]
        ok &= all((r['donor'] != r['case_id'] for r in p))
        d = np.array([r['Qdeep'] for r in p], float) - np.array([r['Qdeep_shuf'] for r in p], float)
        ix = np.random.default_rng(cfg['seeds']['boot']).integers(0, len(d), (20000, len(d)))
        c = (100 * np.quantile(d[ix].mean(1), (0.025, 0.975))).tolist()
        s = S['per_exit'][str(E)]
        mine[E] = dict(targets=len(tg), delta=100 * float(d.mean()), ci=c)
        ok &= abs(100 * d.mean() - s['delta_pp']) < 1e-09 and all((abs(u - v) < 1e-09 for u, v in zip(c, s['ci95'])))
    p = mine[cfg['primary_exit']]
    ok &= (p['ci'][1] < 33) == S['L1']['upper_below_33'] and (p['ci'][0] > 10) == S['L1']['lower_above_10']
    out = dict(status='PASS' if ok else 'FAIL', recomputed=mine)
    write(OUT / 'INDEPENDENT_CHECK.json', out)
    print(out)
if __name__ == '__main__':
    main()
