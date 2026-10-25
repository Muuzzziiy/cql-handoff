import argparse
"""Matched control, per fact line; see experiments/2026-10-17-matched-control-per-line/DESIGN.md.
Scenes, wordings and freeze code as 2026-10-17-matched-composition-control (21b1); only the line-split masks, seeds and folder are new."""
import json
import os
import time
import traceback
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import ouro_advisor_stagecd as A
OUT = ROOT / 'experiments/2026-10-17-matched-control-per-line'
SEEDS = {'ouro14': 20261018001, 'ouro26': 20261018002}
BOOT = 20261018003
N = 400
MODEL = 'ouro14'
REGIONS = ('q', 'F', 'Fbc', 'Fpb', 'cq', 'cF', 'cbc', 'cpb')
FREEZE = {'Native': (), 'I_Q': (('Q', 'q'),), 'I_V_bc': (('V', 'Fbc'),), 'I_V_pb': (('V', 'Fpb'),), 'I_K_bc': (('K', 'Fbc'),), 'I_K_pb': (('K', 'Fpb'),), 'I_V': (('V', 'F'),), 'I_K': (('K', 'F'),), 'C_Q': (('Q', 'cq'),), 'C_V_c': (('V', 'cbc'),), 'C_V_p': (('V', 'cpb'),), 'C_K_c': (('K', 'cbc'),), 'C_K_p': (('K', 'cpb'),), 'C_V': (('V', 'cF'),), 'C_K': (('K', 'cF'),)}

@torch.inference_mode()
def loops4(model, c, ops, seed):
    from .ouro_readout import read_all_loops
    masks = {k: torch.tensor(c[k + '_mask'], dtype=torch.bool, device='cuda') for k in REGIONS}
    with A.Patch(model, masks, ops, loops=(2, 3, 4)) as p:
        v, _ = read_all_loops(model, torch.tensor([c['ids']], device='cuda'), seed)
    assert p.calls == 4 * len(model.model.layers) and p.replaced == 3 * len(ops) * len(model.model.layers)
    return v

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
            for arm, ops in FREEZE.items():
                v = loops4(model, c, ops, seed)
                first = v[0] if first is None else first
                assert np.array_equal(first, v[0])
                append(OUT / f'{m}_ROWS.jsonl', dict(graph=s['graph'], question=x, arm=arm, **{f'loop{l + 1}': A.score(v[l], c) for l in range(4)}))
            if s['graph'] < 2:
                masks = {k: torch.tensor(c[k + '_mask'], dtype=torch.bool, device='cuda') for k in REGIONS}
                with torch.inference_mode(), A.Patch(model, masks, (('Q', 'q'), ('K', 'F'), ('V', 'F')), loops=(1,)):
                    nv, _ = read_all_loops(model, torch.tensor([c['ids']], device='cuda'), seed)
                ok = bool(np.array_equal(nv, loops4(model, c, (), seed)))
                append(OUT / f'{m}_VALIDATION.jsonl', dict(case_id=c['case_id'], exact=ok))
                assert ok
    write(OUT / f'{m}_RUN.json', dict(status='COMPLETE', commit=os.environ['GIT_HEAD'], seconds=time.perf_counter() - t0))

def boot(d, q=(0.025, 0.975)):
    d = np.asarray(d, float)
    ix = np.random.default_rng(BOOT).integers(0, len(d), (20000, len(d)))
    return (100 * np.quantile(d[ix].mean(1), q)).tolist()

def analyze():
    res = {}
    old = read(ROOT / 'experiments/2026-10-17-matched-composition-control/SUMMARY.json')
    for m in A.MODELS:
        if not (OUT / f'{m}_ROWS.jsonl').exists():
            continue
        acc = {(r['graph'], r['question'], r['arm']): r for r in (json.loads(l) for l in open(OUT / f'{m}_ROWS.jsonl'))}
        gs = sorted({k[0] for k in acc})
        c = lambda g, x, a, l=3: float(acc[g, x, a][f'loop{l}']['correct'])
        D = lambda x, a: np.array([c(g, x, 'Native') - c(g, x, a) for g in gs])
        Mv = lambda a: D('T', a) - D('G', a)
        base_gain = np.mean([c(g, 'T', 'Native', 3) - c(g, 'T', 'Native', 1) for g in gs])
        out = dict(n=len(gs), native={x: {l: 100 * float(np.mean([c(g, x, 'Native', l) for g in gs])) for l in range(1, 5)} for x in ('T', 'G')}, rows={}, rho_T={})
        for a in [a for a in FREEZE if a != 'Native']:
            out['rows'][a] = dict(D_T=100 * float(D('T', a).mean()), D_T_ci=boot(D('T', a)), D_G=100 * float(D('G', a).mean()), D_G_ci=boot(D('G', a)), M=100 * float(Mv(a).mean()), M_ci95=boot(Mv(a)))
            out['rho_T'][a] = float(np.mean([c(g, 'T', a, 3) - c(g, 'T', a, 1) for g in gs]) / (base_gain + 1e-09))
        d = Mv('I_V_bc') - Mv('I_Q')
        i = boot(d, (0.0125, 0.9875))
        out['P1'] = dict(mean_pp=100 * float(d.mean()), ci_bonf2=i, verdict='line values more selective' if i[0] > 0 else 'query more selective' if i[1] < 0 else 'comparable')
        for nm, a in (('MKbc_minus_MQ', 'I_K_bc'), ('MVpb_minus_MQ', 'I_V_pb'), ('MKpb_minus_MQ', 'I_K_pb'), ('MV_both_minus_MQ', 'I_V'), ('MK_both_minus_MQ', 'I_K')):
            dd = Mv(a) - Mv('I_Q')
            out[nm] = dict(mean_pp=100 * float(dd.mean()), ci95=boot(dd))
        out['ref_21b1'] = {a: old[m]['all'][a]['M'] for a in ('I_Q', 'I_V', 'I_K')} if m in old else None
        res[m] = out
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps({m: dict(P1=v['P1'], M={a: round(r['M'], 1) for a, r in v['rows'].items()}) for m, v in res.items()}, indent=1), flush=True)

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
