import argparse
"""NL band control (2.6B); see experiments/2026-10-17-nl-band-control/DESIGN.md."""
import json
import os
import time
import traceback
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import patching as L
from . import rotary as N
from . import natural_scoring as FC
OUT = ROOT / 'experiments/2026-10-17-nl-band-control'
RUN3 = ROOT / 'experiments/2026-10-12-ouro26-natural-rescue-fc-powered'
SEED2, BOOT = (20261017601, 20261017503)
HEADS = 16
BAND = set(range(36, 48))

def lines(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]

def key(it):
    return f"{it['dataset']}_{it['item_index']}"

def run():
    from .ouro_readout import load_model
    cfg = read(RUN3 / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models']['ouro26']
    items = read(RUN3 / 'INPUTS.json')['items']
    by = {key(it): it for it in items}
    assert not (OUT / 'RUN.json').exists()
    write(OUT / 'RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    t0 = time.perf_counter()
    AB_rows = lines(OUT / 'REFERENCE_ROWS.jsonl')
    keys = [r['key'] for r in AB_rows]
    d1 = {r['key']: r['donor'] for r in AB_rows}
    assert len(keys) == 134
    rng = np.random.default_rng(SEED2)
    while True:
        perm = rng.permutation(len(keys))
        if all((perm[i] != i for i in range(len(keys)))):
            break
    d2 = {keys[i]: keys[perm[i]] for i in range(len(keys))}
    write(OUT / 'DONORS2.json', d2)
    Q = (('Q', 'q', BAND, tuple(range(HEADS))),)
    sc = lambda it, src: FC.judge(FC.cand_scores(model, it['two_hop']['prompt_ids'], it['candidate_ids'], 1, seed, Q, src))

    def qrow(it):
        p = it['two_hop']['prompt_ids']
        n = len(p)
        cap = L.stopped(model, dict(ids=p, q_mask=[False] * (n - 1) + [True], F_mask=[False] * n, cq_mask=[False] * n, cF_mask=[False] * n), 3, seed, capture_loop=3)[1]
        return {l: cap[l]['Q'][:, :, n - 1, :].clone() for l in cap}
    late = {k: qrow(by[k]) for k in keys}

    def rot(k, dk):
        delta = len(by[k]['two_hop']['prompt_ids']) - len(by[dk]['two_hop']['prompt_ids'])
        return {l: N.rerotate(model, v, delta) for l, v in late[dk].items()}
    rows = []
    for r in AB_rows:
        k = r['key']
        row = dict(key=k, dataset=r['dataset'], donor1=d1[k], donor2=d2[k], native1=r['native1'], native3=r['native3'], arm1=sc(by[k], late[k]))
        rows.append(row)
    a = sum((x['arm1']['correct'] for x in rows))
    match = all((x['arm1']['correct'] == r['band']['correct'] for x, r in zip(rows, AB_rows)))
    write(OUT / 'CONFIRM.json', dict(arm1=a, n=len(rows), matches_5373_item_by_item=match))
    if a != 84 or not match:
        for x in rows:
            append(OUT / 'ROWS.jsonl', x)
        write(OUT / 'RUN.json', dict(status='STOPPED_CONFIRMATION_MISMATCH', arm1=a, match=match, commit=os.environ['GIT_HEAD']))
        return
    for x in rows:
        k = x['key']
        x['arm2'] = sc(by[k], rot(k, d1[k]))
        x['arm3'] = sc(by[k], rot(k, d2[k]))
        append(OUT / 'ROWS.jsonl', x)
    write(OUT / 'RUN.json', dict(status='COMPLETE', n=len(rows), commit=os.environ['GIT_HEAD'], seconds=time.perf_counter() - t0))

def ci(d):
    d = np.asarray(d, float)
    ix = np.random.default_rng(BOOT).integers(0, len(d), (20000, len(d)))
    return (100 * np.quantile(d[ix].mean(1), [0.025, 0.975])).tolist()

def analyze():
    R = lines(OUT / 'ROWS.jsonl')
    ab = {r['key']: r for r in lines(OUT / 'REFERENCE_ROWS.jsonl')}
    c = lambda a: np.array([r[a]['correct'] for r in R], float)
    al = np.array([ab[r['key']]['all']['correct'] for r in R], float)
    a1, a2, a3 = (c('arm1'), c('arm2'), c('arm3'))
    out = dict(n=len(R), counts=dict(arm1=int(a1.sum()), arm2=int(a2.sum()), arm3=int(a3.sum()), all_layers_5373=int(al.sum())), rescue={k: 100 * float(v.mean()) for k, v in dict(arm1=a1, arm2=a2, arm3=a3, all_layers_5373=al).items()})
    out['C1'] = dict(mean_pp=100 * float((a1 - a2).mean()), ci95=ci(a1 - a2))
    out['C1']['supported'] = out['C1']['ci95'][0] > 0
    out['arm3_minus_arm2'] = dict(mean_pp=100 * float((a3 - a2).mean()), ci95=ci(a3 - a2))
    out['arm1_minus_arm3'] = dict(mean_pp=100 * float((a1 - a3).mean()), ci95=ci(a1 - a3))
    out['arm1_minus_all_layers'] = dict(mean_pp=100 * float((a1 - al).mean()), ci95=ci(a1 - al), band_only=int(((a1 == 1) & (al == 0)).sum()), all_only=int(((a1 == 0) & (al == 1)).sum()), both=int(((a1 == 1) & (al == 1)).sum()))
    out['margin'] = {k: float(np.mean([r[k]['margin'] for r in R])) for k in ('native1', 'arm1', 'arm2', 'arm3', 'native3')}
    out['by_dataset'] = {ds: dict(n=len(rr), **{k: 100 * float(np.mean([r[k]['correct'] for r in rr])) for k in ('arm1', 'arm2', 'arm3')}) for ds in ('2wiki', 'musique') for rr in [[r for r in R if r['dataset'] == ds]]}
    write(OUT / 'SUMMARY.json', out)
    print(json.dumps(out, indent=1), flush=True)
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=('run','analyze')); args=parser.parse_args()
    analyze() if args.action=='analyze' else run()
