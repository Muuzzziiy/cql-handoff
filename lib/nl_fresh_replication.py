import traceback
import argparse
"""Fresh-data replication of the 2.6B NL rescue; see experiments/2026-10-17-nl-fresh-replication/DESIGN.md.
Item sampling, candidates and scoring follow run 3 (lib/ouro_natural_rescue_fc2.py); only the exclusions and seeds are new."""
import collections
import json
import os
import time
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import patching as L
from . import rotary as N
from . import natural_scoring as FC
OUT = ROOT / 'experiments/2026-10-17-nl-fresh-replication'
RUN3 = ROOT / 'experiments/2026-10-12-ouro26-natural-rescue-fc-powered'
N_PER = 650
SAMPLE_SEED = 20261017
CAND_SEED = 20261017011
DONOR_SEED = 20261017012
BOOT = FC.BOOT
HEADS = 16
BAND = set(range(36, 48))

def run():
    from .ouro_readout import load_model
    cfg = read(OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models']['ouro26']
    items = read(OUT / 'INPUTS.json')['items']
    assert not (OUT / 'RUN.json').exists()
    write(OUT / 'RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    t0 = time.perf_counter()
    allL = set(range(spec['layers']))
    allH = tuple(range(HEADS))
    key = lambda it: f"{it['dataset']}_{it['item_index']}"
    by = {key(it): it for it in items}
    sc = lambda it, depth, sp=(), src=None: FC.judge(FC.cand_scores(model, it['two_hop']['prompt_ids'], it['candidate_ids'], depth, seed, sp, src))
    nat = {}
    for it in items:
        r = dict(key=key(it), dataset=it['dataset'], two_hop={d: sc(it, d) for d in (1, 3)})
        append(OUT / 'SCREEN.jsonl', r)
        nat[r['key']] = r['two_hop']
    T = [it for it in items if not nat[key(it)][1]['correct'] and nat[key(it)][3]['correct']]
    print(dict(targets=len(T), seconds=round(time.perf_counter() - t0)), flush=True)
    if len(T) < 60:
        write(OUT / 'RUN.json', dict(status='COMPLETE', targets=len(T), underpowered=True, commit=os.environ['GIT_HEAD'], seconds=time.perf_counter() - t0))
        return
    rng = np.random.default_rng(DONOR_SEED)
    while True:
        perm = rng.permutation(len(T))
        if all((perm[i] != i for i in range(len(T)))):
            break
    donor = {key(T[i]): key(T[perm[i]]) for i in range(len(T))}

    def qrow(it, depth):
        p = it['two_hop']['prompt_ids']
        n = len(p)
        cap = L.stopped(model, dict(ids=p, q_mask=[False] * (n - 1) + [True], F_mask=[False] * n, cq_mask=[False] * n, cF_mask=[False] * n), depth, seed, capture_loop=depth)[1]
        return {l: cap[l]['Q'][:, :, n - 1, :].clone() for l in cap}
    late = {key(it): qrow(it, 3) for it in T}

    def shuf(it):
        d = by[donor[key(it)]]
        delta = len(it['two_hop']['prompt_ids']) - len(d['two_hop']['prompt_ids'])
        return {l: N.rerotate(model, v, delta) for l, v in late[key(d)].items()}
    Q = lambda layers: (('Q', 'q', set(layers), allH),)
    for i, it in enumerate(T):
        k = key(it)
        row = dict(key=k, dataset=it['dataset'], donor=donor[k], native1=nat[k][1], native3=nat[k][3])
        if i < 2:
            ident = sc(it, 1, Q(allL), qrow(it, 1))
            diff = float(np.max(np.abs(np.array(ident['scores']) - np.array(nat[k][1]['scores']))))
            ok = diff < 0.02 and ident['correct'] == nat[k][1]['correct']
            append(OUT / 'VALIDATION.jsonl', dict(key=k, identity_max_abs_score_diff=diff, same_choice=ok))
            if not ok:
                write(OUT / 'RUN.json', dict(status='STOPPED_IDENTITY', key=k, diff=diff, commit=os.environ['GIT_HEAD']))
                return
        s = shuf(it)
        row.update(arm1=sc(it, 1, Q(allL), late[k]), arm2=sc(it, 1, Q(allL), s), arm3=sc(it, 1, Q(BAND), late[k]), arm4=sc(it, 1, Q(BAND), s))
        append(OUT / 'ROWS.jsonl', row)
    write(OUT / 'RUN.json', dict(status='COMPLETE', targets=len(T), commit=os.environ['GIT_HEAD'], seconds=time.perf_counter() - t0))

def boot(d, q):
    d = np.asarray(d, float)
    ix = np.random.default_rng(BOOT).integers(0, len(d), (20000, len(d)))
    return (100 * np.quantile(d[ix].mean(1), q)).tolist()

def analyze():
    S = [json.loads(x) for x in (OUT / 'SCREEN.jsonl').read_text().splitlines() if x.strip()]
    run_ = read(OUT / 'RUN.json')
    a1, a3 = (np.array([s['two_hop'][d]['correct'] for s in S], float) for d in ('1', '3'))
    out = dict(items=len(S), by_dataset_items=dict(collections.Counter((s['dataset'] for s in S))), acc1=100 * float(a1.mean()), acc3=100 * float(a3.mean()), acc1_ci=boot(a1, (0.025, 0.975)), acc3_ci=boot(a3, (0.025, 0.975)), gate_pp=100 * float((a3 - a1).mean()), gate_ci95=boot(a3 - a1, (0.025, 0.975)), targets=run_['targets'])
    if not run_.get('underpowered'):
        R = [json.loads(x) for x in (OUT / 'ROWS.jsonl').read_text().splitlines() if x.strip()]
        c = lambda a, rr: np.array([r[a]['correct'] for r in rr], float)
        out['rescue'] = {a: 100 * float(c(a, R).mean()) for a in ('arm1', 'arm2', 'arm3', 'arm4')}
        for nm, a, b in (('R1', 'arm1', 'arm2'), ('R2', 'arm3', 'arm4')):
            d = c(a, R) - c(b, R)
            out[nm] = dict(mean_pp=100 * float(d.mean()), ci_bonf2=boot(d, (0.0125, 0.9875)))
            out[nm]['supported'] = bool(out[nm]['ci_bonf2'][0] > 0)
        out['margin'] = {a: float(np.mean([r[a]['margin'] for r in R])) for a in ('native1', 'arm1', 'arm2', 'arm3', 'arm4', 'native3')}
        out['by_dataset'] = {ds: dict(n=len(rr), **{a: 100 * float(c(a, rr).mean()) for a in ('arm1', 'arm2', 'arm3', 'arm4')}) for ds in ('2wiki', 'musique') for rr in [[r for r in R if r['dataset'] == ds]] if rr}
        out['run3_reference'] = dict(R1=14.2, R1_ci95=[7.5, 20.9], R2_3398=29.9, R2_ci95=[20.9, 38.8])
    write(OUT / 'SUMMARY.json', out)
    print(json.dumps(out, indent=1), flush=True)
if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('action', choices=['campaign', 'analyze'])
    x = a.parse_args()
    if x.action == 'campaign':
        log = OUT / 'CAMPAIGN.log'

        def say(s):
            with open(log, 'a') as f:
                f.write(f'{now()} {s}\n')
        try:
            say('START')
            run()
            st = read(OUT / 'RUN.json')['status']
            say(f'RUN {st}')
            if st == 'COMPLETE':
                analyze()
                say('CAMPAIGN_DONE')
        except Exception:
            say('FAILED\n' + traceback.format_exc())
            raise
    else:
        {'analyze': analyze}[x.action]()
