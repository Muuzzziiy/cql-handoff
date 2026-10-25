import argparse
"""Early-exit-trained dense control, 8B (LayerSkip-Llama3-8B, partial CPU offload); see experiments/2026-10-16-layerskip8b-control/DESIGN.md.
Same code as layerskip_control.py; only the model, exits, seeds and loading differ."""
import json
import os
import time
import traceback
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import ouro_advisor_stagecd as A
from . import dense_control as D
OUT = ROOT / 'experiments/2026-10-16-layerskip8b-control'
MODEL = dict(repo='facebook/layerskip-llama3-8B', path='models/layerskip-llama3-8B')
SEED, DONOR, BOOT = (20261016101, 20261016102, 20261016103)
N = 600
EXITS = (16, 24, 8)
PRIMARY = 16
INF = 2026092421

class QDeep:
    """Capture final-position input residual of every layer; optionally replace the final-position q_proj output of every layer i in
    `layers` by W_Q^i(input_layernorm_i(h[i])) (full-sequence projection, same shapes as native)."""

    def __init__(s, model, h=None, layers=()):
        s.m, s.hsrc, s.layers = (model, h, set(layers))
        s.h = {}
        s.handles = []

    def __enter__(s):
        for i, layer in enumerate(s.m.model.layers):

            def pre(_m, args, kw, i=i):
                hs = args[0] if args else kw['hidden_states']
                s.h[i] = hs[:, -1].detach().clone()
            s.handles.append(layer.register_forward_pre_hook(pre, with_kwargs=True))
            if i in s.layers:

                def qhook(mod, inp, out, layer=layer, i=i):
                    x = inp[0].clone()
                    x[:, -1] = layer.input_layernorm(s.hsrc[i])
                    return torch.nn.functional.linear(x, mod.weight, mod.bias)
                s.handles.append(layer.self_attn.q_proj.register_forward_hook(qhook))
        return s

    def __exit__(s, *a):
        for hd in s.handles:
            hd.remove()

@torch.inference_mode()
def exits(model, c, h=None, layers=()):
    """Logits at every exit e (1..L): norm + head on the final-position state after layer e-1 (= input of layer e; output for e = L)."""
    ids = torch.tensor([c['ids']], device=model.device)
    with QDeep(model, h, layers) as q:
        torch.manual_seed(INF)
        out = model(input_ids=ids, use_cache=False, output_hidden_states=True)
    hs = out.hidden_states
    L = len(model.model.layers)
    res = {}
    for e in range(1, L + 1):
        x = hs[e] if e == L else model.model.norm(hs[e])
        res[e] = model.lm_head(x).float()[0, -1].cpu().numpy()
    assert np.array_equal(res[L], out.logits[0, -1].float().cpu().numpy())
    return (res, q.h)

def run():
    from transformers import AutoModelForCausalLM
    cfg = read(OUT / 'CONFIG.json')
    scenes = read(OUT / 'INPUTS.json')
    assert not (OUT / 'RUN.json').exists()
    write(OUT / 'RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    t0 = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(MODEL['path'], local_files_only=True, dtype=torch.bfloat16, attn_implementation='sdpa', device_map='auto', max_memory={0: '10GiB', 'cpu': '13GiB'}).eval()
    L = len(model.model.layers)
    for s in scenes:
        row = dict(graph=s['graph'])
        for q, c in s['cases'].items():
            ex, _ = exits(model, c)
            row[q] = {f'e{e}': A.score(v, c)['correct'] for e, v in ex.items()}
        append(OUT / 'BEHAVIOR.jsonl', row)
    B = {json.loads(x)['graph']: json.loads(x) for x in open(OUT / 'BEHAVIOR.jsonl')}
    for E in cfg['exits']:
        T = [s['cases']['q2'] for s in scenes if not B[s['graph']]['q2'][f'e{E}'] and B[s['graph']]['q2'][f'e{L}']]
        H = {c['case_id']: exits(model, c)[1] for c in T}
        donor = D.derange([c['case_id'] for c in T], {c['case_id']: len(c['ids']) for c in T}, DONOR + E)
        layers = [i for i in range(E) if i + E < L + 1]
        for n_, c in enumerate(T):
            k = c['case_id']

            def deep(src):
                return {i: src[i + E] for i in layers if i + E < L}
            if n_ < 3:
                nat = exits(model, c)[0][E]
                own = exits(model, c, H[k], range(E))[0][E]
                tr = model.model.layers
                model.model.layers = tr[:E]
                try:
                    trunc, _ = exits(model, c)
                finally:
                    model.model.layers = tr
                ok = bool(np.array_equal(nat, own) and np.array_equal(nat, trunc[E]))
                append(OUT / 'VALIDATION.jsonl', dict(exit=E, case_id=k, identity_bitwise=bool(np.array_equal(nat, own)), truncated_equal=bool(np.array_equal(nat, trunc[E]))))
                assert ok
            hd = deep(H[k])
            row = dict(exit=E, case_id=k, graph=c['graph'], donor=donor.get(k), layers=sorted(hd))
            row['Qdeep'] = A.score(exits(model, c, hd, hd.keys())[0][E], c)['correct']
            if k in donor:
                hs = deep(H[donor[k]])
                row['Qdeep_shuf'] = A.score(exits(model, c, hs, hs.keys())[0][E], c)['correct']
            append(OUT / 'ROWS.jsonl', row)
        print('exit', E, 'targets', len(T), round(time.perf_counter() - t0), flush=True)
    write(OUT / 'RUN.json', dict(status='COMPLETE', commit=os.environ['GIT_HEAD'], seconds=time.perf_counter() - t0, peak_gb=torch.cuda.max_memory_allocated() / 1000000000.0, layers=L))

def analyze():
    cfg = read(OUT / 'CONFIG.json')
    Bh = [json.loads(x) for x in open(OUT / 'BEHAVIOR.jsonl')]
    L = max((int(k[1:]) for k in Bh[0]['q2']))
    acc = {q: {e: float(np.mean([r[q][f'e{e}'] for r in Bh])) for e in range(1, L + 1)} for q in ('q2', 'q1a', 'q1b')}
    R = [json.loads(x) for x in open(OUT / 'ROWS.jsonl')]
    res = dict(accuracy=acc, per_exit={})
    for E in cfg['exits']:
        if not any((r['exit'] == E for r in R)):
            res['per_exit'][E] = dict(not_run=True)
            continue
        rr = [r for r in R if r['exit'] == E and 'Qdeep_shuf' in r]
        d = np.array([r['Qdeep'] for r in rr], float) - np.array([r['Qdeep_shuf'] for r in rr], float)
        ix = np.random.default_rng(BOOT).integers(0, len(d), (20000, len(d))) if len(d) else None
        ci = (100 * np.quantile(d[ix].mean(1), (0.025, 0.975))).tolist() if len(d) else None
        res['per_exit'][E] = dict(targets=len([r for r in R if r['exit'] == E]), n=len(rr), Qdeep=float(np.mean([r['Qdeep'] for r in rr])) if rr else None, Qdeep_shuf=float(np.mean([r['Qdeep_shuf'] for r in rr])) if rr else None, delta_pp=100 * float(d.mean()) if len(d) else None, ci95=ci)
    p = res['per_exit'][PRIMARY]
    res['L1'] = dict(upper_below_33=bool(p['ci95'] and p['ci95'][1] < 33), lower_above_10=bool(p['ci95'] and p['ci95'][0] > 10))
    res['informative'] = bool(acc['q2'][L] >= 0.6 and res['per_exit'][PRIMARY]['targets'] >= 30)
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps(res['per_exit'], indent=1), res['L1'], flush=True)

def campaign():
    log = OUT / 'CAMPAIGN.log'

    def say(x):
        with open(log, 'a') as f:
            f.write(f'{now()} {x}\n')
    try:
        say('START')
        run()
        say('RUN COMPLETE')
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
