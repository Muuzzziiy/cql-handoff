"""Independent check of experiments/2026-10-16-freegen-rescue: rescores every generated text, recomputes targets and FG_m."""
import json
import re
import numpy as np
from .common import ROOT, read, write
OUT = ROOT / 'experiments/2026-10-16-freegen-rescue'
COLORS = ('red', 'blue', 'green', 'yellow')

def word(t):
    m = re.findall('[a-z]+', t.lower())
    return m[0] if m else ''

def main():
    cfg = read(OUT / 'CONFIG.json')
    S0 = read(OUT / 'SUMMARY.json')
    boot = cfg['seeds']['boot']
    checks = {}
    mine = {}
    for m in ('ouro14', 'ouro26'):
        cases = {c['case_id']: c for c in read(OUT / 'INPUTS.json')[m]}
        S = read(OUT / f'{m}_SCREEN.json')
        ok = lambda g, k: word(g['text']) == COLORS[cases[k]['answer_index']]
        rescore = all((ok(v[d], k) == v[d]['correct'] for k, v in S.items() for d in ('1', '3')))
        T = sorted((k for k, v in S.items() if not ok(v['1'], k) and ok(v['3'], k)))
        R = [json.loads(l) for l in open(OUT / f'{m}_ROWS.jsonl')]
        rows_ok = sorted((r['case_id'] for r in R)) == T and all((ok(r[a], r['case_id']) == r[a]['correct'] for r in R for a in ('Q_same', 'Q_shuf') if a in r))
        P = [r for r in R if 'Q_shuf' in r]
        d = np.array([ok(r['Q_same'], r['case_id']) for r in P], float) - np.array([ok(r['Q_shuf'], r['case_id']) for r in P], float)
        ix = np.random.default_rng(boot).integers(0, len(d), (20000, len(d)))
        i = (100 * np.quantile(d[ix].mean(1), (0.0125, 0.9875))).tolist()
        g = dict(targets=len(T), delta_pp=100 * float(d.mean()), ci=i, supported=bool(100 * d.mean() >= 10 and i[0] > 0), gen1=float(np.mean([ok(v['1'], k) for k, v in S.items()])), gen3=float(np.mean([ok(v['3'], k) for k, v in S.items()])))
        s = S0[m]
        c = lambda u, v: abs(u - v) < 1e-09
        checks[m] = dict(rescore=rescore, rows=rows_ok, targets=g['targets'] == s['targets'], delta=c(g['delta_pp'], s['delta_pp']), ci=all((c(u, v) for u, v in zip(i, s['ci_bonf2']))), supported=g['supported'] == s['supported'], acc=c(g['gen1'], s['accuracy']['gen_loop1']) and c(g['gen3'], s['accuracy']['gen_loop3']), identity=all((json.loads(l)['identity_bitwise'] for l in open(OUT / f'{m}_VALIDATION.jsonl'))))
        mine[m] = g
    st = 'PASS' if all((all(v.values()) for v in checks.values())) else 'FAIL'
    out = dict(status=st, checks=checks, recomputed=mine)
    write(OUT / 'INDEPENDENT_CHECK.json', out)
    print(json.dumps(out, indent=1))
if __name__ == '__main__':
    main()
