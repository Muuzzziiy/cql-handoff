import argparse
"""Powered forced-choice natural rescue on fresh items (2.6B); see experiments/2026-10-12-ouro26-natural-rescue-fc-powered/DESIGN.md.

Reuses the n = 43 run's scoring and patch code by pointing it at this directory.
"""
import json
import numpy as np
from .common import ROOT, write
from . import natural_scoring as FC
OUT = ROOT / 'experiments/2026-10-12-ouro26-natural-rescue-fc-powered'
N_PER = 650
SAMPLE_SEED = 20261013401
CAND_SEED = 20261013402
DONOR_SEED = 20261013403

def run(name):
    FC.OUT = OUT
    FC.DONOR_SEED = DONOR_SEED
    FC.run(name)

def analyze():
    FC.OUT = OUT
    res = {}
    R = [json.loads(x) for x in (OUT / 'ouro26_ROWS.jsonl').read_text().splitlines() if x.strip()]
    S = [json.loads(x) for x in (OUT / 'ouro26_SCREEN.jsonl').read_text().splitlines() if x.strip()]
    out = dict(items=len(S), native_two_hop_acc={r: float(np.mean([s['two_hop'][str(r)]['correct'] for s in S])) for r in (1, 3)})
    for sub, rr in (('primary_full', R), ('S_star', [x for x in R if x['s_star']]), ('2wiki', [x for x in R if x['dataset'] == '2wiki']), ('musique', [x for x in R if x['dataset'] == 'musique'])):
        n = len(rr)
        if not n:
            out[sub] = dict(n=0)
            continue
        d = np.array([x['same']['correct'] - x['shuffled']['correct'] for x in rr], float)
        ix = np.random.default_rng(FC.BOOT).integers(0, n, (20000, n))
        out[sub] = dict(n=n, rescue_same=float(np.mean([x['same']['correct'] for x in rr])), rescue_shuffled=float(np.mean([x['shuffled']['correct'] for x in rr])), rescue_same_loop_donor=float(np.mean([x['same_loop_donor']['correct'] for x in rr])), delta_pp=100 * float(d.mean()), ci95_pp=(100 * np.quantile(d[ix].mean(1), [0.025, 0.975])).tolist(), margin={k: float(np.mean([x[k]['margin'] for x in rr])) for k in ('native1', 'same', 'shuffled', 'native3')})
    out['primary_full']['pass'] = out['primary_full']['ci95_pp'][0] > 0
    write(OUT / 'SUMMARY.json', out)
    print(json.dumps(out, indent=1), flush=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    args = parser.parse_args()
    analyze() if args.action == 'analyze' else run('ouro26')
