import argparse
"""Dense control: late-query re-projection Q_i(h_{i+Δ}) in Qwen3-1.7B-Base and within Ouro-1.4B loop 1;
see experiments/2026-10-15-dense-control/DESIGN.md."""
import json
import os
import time
import traceback
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import ouro_advisor_stagecd as A
OUT = ROOT / 'experiments/2026-10-15-dense-control'
QWEN = dict(repo='Qwen/Qwen3-1.7B-Base', revision='ea980cb0a6c2ae4b936e82123acc929f1cec04c1', path='models/Qwen3-1.7B-Base', layers=28)
SEED = 20261015401
DONOR_SEED = 20261015402
BOOT = 20261015403
N = 600
DELTAS = (4, 8, 12)
INF = 2026092421
QUERIES = {'q2': 'two_hop', 'q1a': 'person_box', 'q1b': 'box_color'}

class Hooks:
    """Track (loop, layer); capture the final-position input residual of every layer at `cap_loop`; optionally replace layer i's q_proj
    output at the final position by q_proj_i(input_layernorm_i(h)) (mode 'Q') or layer i's input residual at the final position by h ('H'),
    only at loop `loop`. Dense models have a single loop (1)."""

    def __init__(s, model, looped, cap_loop=1, patch=None):
        s.m, s.looped, s.cap_loop, s.patch = (model, looped, cap_loop, patch)
        s.h = {}
        s.handles = []
        s.loop = 1

    def __enter__(s):
        layers = s.m.model.layers
        for i, layer in enumerate(layers):

            def pre(_m, args, kw, i=i):
                if s.looped:
                    s.loop = int(kw['current_ut']) + 1
                hs = args[0] if args else kw['hidden_states']
                if s.loop == s.cap_loop:
                    s.h[i] = hs[:, -1].detach().clone()
                if s.patch and s.patch['mode'] == 'H' and (s.loop == s.patch['loop']) and (i == s.patch['layer']):
                    hs = hs.clone()
                    hs[:, -1] = s.patch['h']
                    if args:
                        return ((hs,) + tuple(args[1:]), kw)
                    kw['hidden_states'] = hs
                    return (args, kw)
            s.handles.append(layer.register_forward_pre_hook(pre, with_kwargs=True))
            if s.patch and s.patch['mode'] == 'Q' and (i == s.patch['layer']):

                def qhook(mod, inp, out, layer=layer):
                    if s.loop != s.patch['loop']:
                        return out
                    x = inp[0].clone()
                    x[:, -1] = layer.input_layernorm(s.patch['h'])
                    return torch.nn.functional.linear(x, mod.weight, mod.bias)
                s.handles.append(layer.self_attn.q_proj.register_forward_hook(qhook))
        return s

    def __exit__(s, *a):
        for h in s.handles:
            h.remove()

@torch.inference_mode()
def logits(model, c, looped, depth, patch=None, cap_loop=1):
    ids = torch.tensor([c['ids']], device='cuda')
    with Hooks(model, looped, cap_loop, patch) as hk:
        if looped:
            from .ouro_readout import author_stopped_forward
            v = author_stopped_forward(model, ids, depth, INF)
        else:
            torch.manual_seed(INF)
            v = model(input_ids=ids, use_cache=False).logits[0, -1].float().cpu().numpy()
    return (v, hk.h)

def derange(ids, length, seed):
    rng = np.random.default_rng(seed)
    donor = {}
    for L_ in sorted(set((length[i] for i in ids))):
        grp = [i for i in ids if length[i] == L_]
        if len(grp) < 2:
            continue
        while True:
            perm = rng.permutation(len(grp))
            if all((perm[k] != k for k in range(len(grp)))):
                break
        donor.update({grp[k]: grp[perm[k]] for k in range(len(grp))})
    return donor

def run(which):
    cfg = read(OUT / 'CONFIG.json')
    scenes = read(OUT / 'INPUTS.json')[which]
    looped = which == 'ouro14'
    assert not (OUT / f'{which}_RUN.json').exists()
    write(OUT / f'{which}_RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    t0 = time.perf_counter()
    if looped:
        from .ouro_readout import load_model
        model, _ = load_model(cfg['ouro14']['path'], cfg['ouro14']['layers'])
        nl = cfg['ouro14']['layers']
        depth = 1
    else:
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(QWEN['path'], local_files_only=True, torch_dtype=torch.bfloat16, attn_implementation='sdpa').cuda().eval()
        nl = model.config.num_hidden_layers
        assert nl == QWEN['layers']
        depth = None
    for s in scenes:
        row = dict(graph=s['graph'])
        for q, c in s['cases'].items():
            if looped:
                row[q] = {f'loop{d}': A.score(logits(model, c, True, d)[0], c) for d in (1, 3)}
            else:
                row[q] = {'full': A.score(logits(model, c, False, None)[0], c)}
        append(OUT / f'{which}_BEHAVIOR.jsonl', row)
    B = {r['graph']: r for r in (json.loads(x) for x in open(OUT / f'{which}_BEHAVIOR.jsonl'))}
    key = 'loop1' if looped else 'full'
    targets = [s['cases']['q2'] for s in scenes if not B[s['graph']]['q2'][key]['correct'] and (not looped or B[s['graph']]['q2']['loop3']['correct'])]
    H = {c['case_id']: logits(model, c, looped, depth)[1] for c in targets}
    donor = derange([c['case_id'] for c in targets], {c['case_id']: len(c['ids']) for c in targets}, DONOR_SEED)
    by = {c['case_id']: c for c in targets}
    for n_, c in enumerate(targets):
        k = c['case_id']
        row = dict(case_id=k, graph=c['graph'], half='select' if c['graph'] % 2 == 0 else 'evaluate', donor=donor.get(k))
        if n_ < 3:
            nat = logits(model, c, looped, depth)[0]
            for mode in ('Q', 'H'):
                v = logits(model, c, looped, depth, dict(mode=mode, layer=5, loop=1, h=H[k][5]))[0]
                assert np.array_equal(v, nat), (mode, float(np.abs(v - nat).max()))
            append(OUT / f'{which}_VALIDATION.jsonl', dict(case_id=k, identity_Q_H_bitwise=True))
        for D in DELTAS:
            for i in range(0, nl - D):
                j = i + D
                row[f'Q_{i}_{D}'] = A.score(logits(model, c, looped, depth, dict(mode='Q', layer=i, loop=1, h=H[k][j]))[0], c)['correct']
                row[f'H_{i}_{D}'] = A.score(logits(model, c, looped, depth, dict(mode='H', layer=i, loop=1, h=H[k][j]))[0], c)['correct']
                if k in donor:
                    row[f'Qs_{i}_{D}'] = A.score(logits(model, c, looped, depth, dict(mode='Q', layer=i, loop=1, h=H[donor[k]][j]))[0], c)['correct']
        append(OUT / f'{which}_ROWS.jsonl', row)
        if n_ % 25 == 24:
            print(which, 'targets', n_ + 1, '/', len(targets), round(time.perf_counter() - t0), flush=True)
    write(OUT / f'{which}_RUN.json', dict(status='COMPLETE', commit=os.environ['GIT_HEAD'], targets=len(targets), seconds=time.perf_counter() - t0, peak_gb=torch.cuda.max_memory_allocated() / 1000000000.0))

def ci(x, q):
    x = np.asarray(x, float)
    ix = np.random.default_rng(BOOT).integers(0, len(x), (20000, len(x)))
    return (100 * np.quantile(x[ix].mean(1), q)).tolist()

def analyze():
    cfg = read(OUT / 'CONFIG.json')
    res = {}
    for which in ('qwen', 'ouro14'):
        if not (OUT / f'{which}_ROWS.jsonl').exists():
            continue
        Bh = [json.loads(x) for x in open(OUT / f'{which}_BEHAVIOR.jsonl')]
        key = 'loop1' if which == 'ouro14' else 'full'
        acc = {q: float(np.mean([r[q][key]['correct'] for r in Bh])) for q in QUERIES}
        if which == 'ouro14':
            acc.update({f'{q}_loop3': float(np.mean([r[q]['loop3']['correct'] for r in Bh])) for q in QUERIES})
        R = [json.loads(x) for x in open(OUT / f'{which}_ROWS.jsonl')]
        sel = [r for r in R if r['half'] == 'select' and r['donor']]
        ev = [r for r in R if r['half'] == 'evaluate' and r['donor']]
        per = {}
        for D in cfg['deltas']:
            layers = sorted((int(k.split('_')[1]) for k in R[0] if k.startswith('Q_') and k.endswith(f'_{D}')))
            best = max(layers, key=lambda i: (np.mean([r[f'Q_{i}_{D}'] for r in sel]) - np.mean([r[f'Qs_{i}_{D}'] for r in sel]), -i))
            d = np.array([r[f'Q_{best}_{D}'] for r in ev], float) - np.array([r[f'Qs_{best}_{D}'] for r in ev], float)
            per[D] = dict(best_layer=best, n_eval=len(ev), Q_rescue=float(np.mean([r[f'Q_{best}_{D}'] for r in ev])), Qs_rescue=float(np.mean([r[f'Qs_{best}_{D}'] for r in ev])), delta_pp=100 * float(d.mean()), delta_ci_bonf3=ci(d, (1 / 120, 1 - 1 / 120)), H_rescue_best_layer=float(np.mean([r[f'H_{best}_{D}'] for r in ev])), H_rescue_max_over_layers=float(max((np.mean([r[f'H_{i}_{D}'] for r in ev]) for i in layers))))
        res[which] = dict(accuracy=acc, targets=len(R), per_delta=per)
    if 'qwen' in res:
        res['D1_no_dense_rescue'] = bool(all((v['delta_ci_bonf3'][1] < 10 for v in res['qwen']['per_delta'].values())))
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps(res, indent=1), flush=True)

def campaign():
    log = OUT / 'CAMPAIGN.log'

    def say(x):
        with open(log, 'a') as f:
            f.write(f'{now()} {x}\n')
    try:
        for w in ('qwen', 'ouro14'):
            say(f'START {w}')
            run(w)
            say(f'DONE {w}')
            torch.cuda.empty_cache()
        analyze()
        say('CAMPAIGN_DONE')
    except Exception:
        say('FAILED\n' + traceback.format_exc())
        raise
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('campaign', 'analyze'))
    args = parser.parse_args()
    {'campaign': campaign, 'analyze': analyze}[args.action]()
