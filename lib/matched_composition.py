import argparse
"""Matched composition control (Stage C freezes on a two-hop T and a matched bridge-given G); see
experiments/2026-10-17-matched-composition-control/DESIGN.md (amendment 1: G without the comma)."""
import json
import os
import time
import traceback
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import ouro_advisor_stagecd as A
OUT = ROOT / 'experiments/2026-10-17-matched-composition-control'
SEEDS = {'ouro14': 20261017, 'ouro26': 20261018}
BOOT = 20261017801
N = 400
MODEL = 'ouro14'
T_Q = 'What color is in the box that {p} has?'
G_Q = 'What color is in box {b} which {p} has?'

def run(m):
    from .ouro_readout import load_model, read_all_loops
    cfg = read(OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models'][m]
    S = read(OUT / 'INPUTS.json')[m]
    assert not (OUT / f'{m}_RUN.json').exists()
    write(OUT / f'{m}_RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    t0 = time.perf_counter()
    for s in S:
        for x in ('T', 'G'):
            c = s[x]
            first = None
            for arm, ops in A.FREEZE.items():
                v = A.all_loops(model, c, ops, seed)
                first = v[0] if first is None else first
                assert np.array_equal(first, v[0])
                append(OUT / f'{m}_ROWS.jsonl', dict(graph=s['graph'], question=x, arm=arm, **{f'loop{l + 1}': A.score(v[l], c) for l in range(4)}))
            if s['graph'] < 2:
                with torch.inference_mode(), A.Patch(model, A.masks_of(c), (('Q', 'q'), ('K', 'F'), ('V', 'F')), loops=(1,)):
                    nv, _ = read_all_loops(model, torch.tensor([c['ids']], device='cuda'), seed)
                ok = bool(np.array_equal(nv, A.all_loops(model, c, (), seed)))
                append(OUT / f'{m}_VALIDATION.jsonl', dict(case_id=c['case_id'], exact=ok))
                assert ok
    write(OUT / f'{m}_RUN.json', dict(status='COMPLETE', commit=os.environ['GIT_HEAD'], seconds=time.perf_counter() - t0))

def boot(d, q):
    d = np.asarray(d, float)
    ix = np.random.default_rng(BOOT).integers(0, len(d), (20000, len(d)))
    return (100 * np.quantile(d[ix].mean(1), q)).tolist()

def analyze():
    res = {}
    old = read(A.OUT / 'SUMMARY.json')
    for m in A.MODELS:
        if not (OUT / f'{m}_ROWS.jsonl').exists():
            continue
        R = [json.loads(l) for l in open(OUT / f'{m}_ROWS.jsonl')]
        acc = {}
        for r in R:
            acc[r['graph'], r['question'], r['arm']] = r
        gs = sorted({r['graph'] for r in R})
        c = lambda g, x, a, l=3: float(acc[g, x, a][f'loop{l}']['correct'])
        star = [g for g in gs if all((c(g, 'G', 'Native', l) for l in range(1, 5)))]
        out = dict(n=len(gs), s_star_n=len(star), native={x: {l: 100 * float(np.mean([c(g, x, 'Native', l) for g in gs])) for l in range(1, 5)} for x in ('T', 'G')})
        for sub, G_ in (('all', gs), ('s_star', star)):
            o = {}
            for arm in [a for a in A.FREEZE if a != 'Native']:
                dT = np.array([c(g, 'T', 'Native') - c(g, 'T', arm) for g in G_])
                dG = np.array([c(g, 'G', 'Native') - c(g, 'G', arm) for g in G_])
                o[arm] = dict(D_T=100 * float(dT.mean()), D_T_ci=boot(dT, (0.025, 0.975)), D_G=100 * float(dG.mean()), D_G_ci=boot(dG, (0.025, 0.975)), M=100 * float((dT - dG).mean()), M_ci95=boot(dT - dG, (0.025, 0.975)))
            mq = lambda a: np.array([c(g, 'T', 'Native') - c(g, 'T', 'I_Q') - (c(g, 'G', 'Native') - c(g, 'G', 'I_Q')) - (c(g, 'T', 'Native') - c(g, 'T', a) - (c(g, 'G', 'Native') - c(g, 'G', a))) for g in G_])
            o['MQ_minus_MK'] = dict(mean_pp=100 * float(mq('I_K').mean()), ci95=boot(mq('I_K'), (0.025, 0.975)))
            o['MQ_minus_MV'] = dict(mean_pp=100 * float(mq('I_V').mean()), ci95=boot(mq('I_V'), (0.025, 0.975)))
            out[sub] = o
        dT = np.array([c(g, 'T', 'Native') - c(g, 'T', 'I_Q') for g in gs])
        dG = np.array([c(g, 'G', 'Native') - c(g, 'G', 'I_Q') for g in gs])
        i = boot(dT - dG, (0.0125, 0.9875))
        out['M1'] = dict(mean_pp=100 * float((dT - dG).mean()), ci_bonf2=i, supported=bool(i[0] > 0))
        out['stage_c_reference'] = {k: old[m].get(k) for k in ('full', 'S_star_n')} if m in old else None
        res[m] = out
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps(res, indent=1)[:4000], flush=True)

def campaign():
    log = OUT / 'CAMPAIGN.log'

    def say(x):
        with open(log, 'a') as f:
            f.write(f'{now()} {x}\n')
    try:
        say(f'START {MODEL}')
        run(MODEL)
        say(f'DONE {MODEL}')
        analyze()
    except Exception:
        say('FAILED\n' + traceback.format_exc())
        raise
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('campaign', 'analyze'))
    parser.add_argument('--model', choices=('ouro14', 'ouro26'))
    args = parser.parse_args()
    if args.action != 'analyze' and args.model is None:
        parser.error('--model is required for inference')
    MODEL = args.model
    {'campaign': campaign, 'analyze': analyze}[args.action]()
