"""Audit of the protocol-coordinate rescue: operand isolation, fresh replication (2.6B), and v1-vs-strict factor split.

See experiments/2026-10-12-ouro-rescue-audit/DESIGN.md.
"""
import argparse
import hashlib
import json
import os
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from .spans import span_mask
from . import ouro_advisor_stagecd as A
OUT = ROOT / 'experiments/2026-10-12-ouro-rescue-audit'
SEED_FRESH = 20261012801
N_FRESH = 300
DONOR_SEED = 20261012802

def load(name):
    from .ouro_readout import load_model
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    spec = read(A.OUT / 'CONFIG.json')['models'][name]
    return load_model(spec['path'], spec['layers'])[0]

def with_span(c, tok):
    text = c['prompt']
    off = tok(text, add_special_tokens=False, return_offsets_mapping=True)['offset_mapping']
    q = text.index('Question:')
    return dict(c, span_mask=span_mask(text, off, q, len(text)))

def masks(c):
    m = A.masks_of(c)
    if 'span_mask' in c:
        m['span'] = torch.tensor(c['span_mask'], dtype=torch.bool, device='cuda')
    return m

@torch.inference_mode()
def stopped(model, c, depth, seed, ops=(), loops=(), source=None, capture_loop=None):
    from .ouro_readout import author_stopped_forward
    with A.Patch(model, masks(c), ops, loops, source, capture_loop) as p:
        v = author_stopped_forward(model, torch.tensor([c['ids']], device='cuda'), depth, seed)
    return (v, p.captured)

def isolation(model, cases, seed):
    """Patched loop-1 forward vs unpatched: all operands at positions other than q must be bit-identical at every layer;
    at q, layer 0 K and V must be identical and Q must equal the late Q exactly."""
    out = []
    for c in cases:
        late = stopped(model, c, 3, seed, capture_loop=3)[1]
        base = stopped(model, c, 1, seed, capture_loop=1)[1]
        pat = stopped(model, c, 1, seed, (('Q', 'q'),), (1,), late, capture_loop=1)[1]
        q = len(c['ids']) - 1
        other = slice(0, q)
        r = dict(case_id=c['case_id'], layers=len(base))
        r['other_positions_identical_all_layers'] = all((torch.equal(base[l][n][:, :, other], pat[l][n][:, :, other]) for l in base for n in 'QKV'))
        r['q_K_V_identical_layer0'] = all((torch.equal(base[0][n][:, :, q], pat[0][n][:, :, q]) for n in 'KV'))
        r['q_K_V_layers_changed_downstream'] = sum((not torch.equal(base[l][n][:, :, q], pat[l][n][:, :, q]) for l in base for n in 'KV'))
        r['late_Q_differs_from_loop1_Q_at_q'] = sum((not torch.equal(base[l]['Q'][:, :, q], late[l]['Q'][:, :, q]) for l in base))
        out.append(r)
    return out

def rescue(model, targets, seed, s, region, donor=None):
    rows = []
    late = {c['case_id']: stopped(model, c, s, seed, capture_loop=s)[1] for c in targets}
    for c in targets:
        x = dict(case_id=c['case_id'], s=s, region=region, same=A.score(stopped(model, c, 1, seed, (('Q', region),), (1,), late[c['case_id']])[0], c))
        if donor and c['case_id'] in donor:
            x['shuffled'] = A.score(stopped(model, c, 1, seed, (('Q', region),), (1,), late[donor[c['case_id']]])[0], c)
        rows.append(x)
    return rows

def derange(targets, seed):
    rng = np.random.default_rng(seed)
    donor = {}
    for L in sorted({len(c['ids']) for c in targets}):
        grp = [c['case_id'] for c in targets if len(c['ids']) == L]
        if len(grp) < 2:
            continue
        while True:
            perm = rng.permutation(len(grp))
            if all((perm[i] != i for i in range(len(grp)))):
                break
        donor.update({grp[i]: grp[perm[i]] for i in range(len(grp))})
    return donor

def run(name):
    from transformers import AutoTokenizer
    cfg = read(A.OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models'][name]
    tok = AutoTokenizer.from_pretrained(spec['path'], local_files_only=True)
    model = load(name)
    old = {c['case_id']: c for c in read(A.OUT / 'INPUTS.json')[name]['stage_d']}
    targets = [with_span(old[r['case_id']], tok) for r in A.jsonlines(A.OUT / f'{name}_D_ROWS.jsonl') if r['r'] == 1]
    write(OUT / f'{name}_ISOLATION.json', isolation(model, targets[:4], seed))
    for s in (3, 4):
        for region in ('q', 'span'):
            for x in rescue(model, targets, seed, s, region):
                append(OUT / f'{name}_FACTORS.jsonl', x)
    print(dict(model=name, factors='done', targets=len(targets)), flush=True)
    if name == 'ouro26':
        inp = read(OUT / 'FRESH_INPUTS.json')['cases']
        fresh = []
        for c in inp:
            l1 = A.score(stopped(model, c, 1, seed)[0], c)
            l3 = A.score(stopped(model, c, 3, seed)[0], c)
            append(OUT / 'ouro26_FRESH_SCREEN.jsonl', dict(case_id=c['case_id'], loop1=l1, loop3=l3))
            if not l1['correct'] and l3['correct']:
                fresh.append(c)
        for x in rescue(model, fresh, seed, 3, 'q', derange(fresh, DONOR_SEED)):
            append(OUT / 'ouro26_FRESH_ROWS.jsonl', x)
        print(dict(model=name, fresh_targets=len(fresh)), flush=True)

def boot(x, seed=20261012803, reps=20000):
    x = np.asarray(x, float)
    ix = np.random.default_rng(seed).integers(0, len(x), (reps, len(x)))
    return np.quantile(x[ix].mean(1), [0.025, 0.975]).tolist()

def analyze():
    res = {}
    for name in A.MODELS:
        iso = read(OUT / f'{name}_ISOLATION.json')
        f = A.jsonlines(OUT / f'{name}_FACTORS.jsonl')
        cell = {}
        for s in (3, 4):
            for region in ('q', 'span'):
                v = [x['same']['correct'] for x in f if x['s'] == s and x['region'] == region]
                m = [x['same']['margin'] for x in f if x['s'] == s and x['region'] == region]
                cell[f'{region}_s{s}'] = dict(n=len(v), rescue=float(np.mean(v)), ci95=boot(v), median_margin=float(np.median(m)))
        res[name] = dict(isolation=iso, factors=cell)
    fr = A.jsonlines(OUT / 'ouro26_FRESH_ROWS.jsonl')
    paired = [x for x in fr if 'shuffled' in x]
    d = [x['same']['correct'] - x['shuffled']['correct'] for x in paired]
    res['ouro26_fresh'] = dict(targets=len(fr), paired=len(paired), rescue_same=float(np.mean([x['same']['correct'] for x in fr])), rescue_shuffled=float(np.mean([x['shuffled']['correct'] for x in paired])), delta_pp=100 * float(np.mean(d)), delta_ci95_pp=(100 * np.array(boot(d))).tolist())
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps(res, indent=1)[:3000], flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=('run','analyze'))
    parser.add_argument('--model',choices=A.MODELS); args=parser.parse_args()
    if args.action=='run' and args.model is None: parser.error('--model is required')
    analyze() if args.action=='analyze' else run(args.model)
