"""Independent check of the dense control: recompute targets, layer selection, rescue and bounds from BEHAVIOR/ROWS."""
import json
import numpy as np
from .common import ROOT, read, write
OUT = ROOT / 'experiments/2026-10-15-dense-control'

def main():
    cfg = read(OUT / 'CONFIG.json')
    S = read(OUT / 'SUMMARY.json')
    ok = True
    mine = {}
    for w in ('qwen', 'ouro14'):
        B = {json.loads(x)['graph']: json.loads(x) for x in open(OUT / f'{w}_BEHAVIOR.jsonl')}
        key = 'loop1' if w == 'ouro14' else 'full'
        tg = sorted((g for g, r in B.items() if not r['q2'][key]['correct'] and (w == 'qwen' or r['q2']['loop3']['correct'])))
        R = [json.loads(x) for x in open(OUT / f'{w}_ROWS.jsonl')]
        ok &= sorted((r['graph'] for r in R)) == tg and len(R) == S[w]['targets']
        sel = [r for r in R if r['graph'] % 2 == 0 and r['donor']]
        ev = [r for r in R if r['graph'] % 2 == 1 and r['donor']]
        for D in cfg['deltas']:
            layers = sorted((int(k.split('_')[1]) for k in R[0] if k.startswith('Q_') and k.endswith(f'_{D}')))
            sc = {i: np.mean([r[f'Q_{i}_{D}'] for r in sel]) - np.mean([r[f'Qs_{i}_{D}'] for r in sel]) for i in layers}
            best = max(layers, key=lambda i: (sc[i], -i))
            d = np.array([r[f'Q_{best}_{D}'] for r in ev], float) - np.array([r[f'Qs_{best}_{D}'] for r in ev], float)
            ix = np.random.default_rng(cfg['seeds']['boot']).integers(0, len(d), (20000, len(d)))
            c = (100 * np.quantile(d[ix].mean(1), (1 / 120, 1 - 1 / 120))).tolist()
            s = S[w]['per_delta'][str(D)]
            mine[f'{w}/{D}'] = dict(best=best, delta=100 * float(d.mean()), ci=c)
            ok &= best == s['best_layer'] and abs(100 * d.mean() - s['delta_pp']) < 1e-09 and all((abs(u - v) < 1e-09 for u, v in zip(c, s['delta_ci_bonf3'])))
    d1 = all((mine[f'qwen/{D}']['ci'][1] < 10 for D in cfg['deltas']))
    ok &= d1 == S['D1_no_dense_rescue']
    out = dict(status='PASS' if ok else 'FAIL', recomputed=mine, D1=d1)
    write(OUT / 'INDEPENDENT_CHECK.json', out)
    print(out)
if __name__ == '__main__':
    main()
