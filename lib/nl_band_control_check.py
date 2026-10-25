"""Independent check of experiments/2026-10-17-nl-band-control (does not import the runner): item set, donor maps, C1."""
import json
from pathlib import Path
import numpy as np
E = Path(__file__).resolve().parents[1] / 'experiments'
OUT = E / '2026-10-17-nl-band-control'

def lines(p):
    return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]

def ok(j):
    s = np.asarray(j['scores'])
    return int(np.argmax(s)) == 0

def main():
    S = json.loads((OUT / 'SUMMARY.json').read_text())
    R = lines(OUT / 'ROWS.jsonl')
    ab = {r['key']: r for r in lines(OUT / 'REFERENCE_ROWS.jsonl')}
    keys = [r['key'] for r in lines(OUT / 'REFERENCE_ROWS.jsonl')]
    rng = np.random.default_rng(20261017601)
    while True:
        perm = rng.permutation(len(keys))
        if all((perm[i] != i for i in range(len(keys)))):
            break
    d2 = {keys[i]: keys[perm[i]] for i in range(len(keys))}
    ch = dict(items=[r['key'] for r in R] == keys and len(R) == 134, donor1=all((r['donor1'] == ab[r['key']]['donor'] for r in R)), donor2=all((r['donor2'] == d2[r['key']] for r in R)), arm1_reproduces=all((ok(r['arm1']) == ok(ab[r['key']]['band']) for r in R)) and sum((ok(r['arm1']) for r in R)) == 84, rescored=all((ok(r[a]) == r[a]['correct'] for r in R for a in ('arm1', 'arm2', 'arm3'))))
    d = np.array([ok(r['arm1']) - ok(r['arm2']) for r in R], float)
    ix = np.random.default_rng(20261017503).integers(0, len(d), (20000, len(d)))
    i = (100 * np.quantile(d[ix].mean(1), [0.025, 0.975])).tolist()
    ch['C1'] = abs(100 * d.mean() - S['C1']['mean_pp']) < 1e-09 and np.allclose(i, S['C1']['ci95']) and ((i[0] > 0) == S['C1']['supported'])
    ch = {k: bool(v) for k, v in ch.items()}
    out = dict(status='PASS' if all(ch.values()) else 'FAIL', checks=ch, recomputed=dict(C1=100 * float(d.mean()), ci95=i))
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
if __name__ == '__main__':
    main()
