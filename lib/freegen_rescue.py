import argparse
"""Main rescue under free (greedy) generation; see experiments/2026-10-16-freegen-rescue/DESIGN.md."""
import json
import os
import time
import traceback
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import ouro_advisor_stagecd as A
from . import patching as L
from . import dense_control as D
OUT = ROOT / 'experiments/2026-10-16-freegen-rescue'
MODEL = 'ouro14'
SEEDS = {'ouro14': 20261017001, 'ouro26': 20261017002}
DONOR, BOOT = (20261017003, 20261017004)
N = 600
INF = 2026092421
COLORS = ('red', 'blue', 'green', 'yellow')

def first_word(text):
    import re
    m = re.findall('[a-z]+', text.lower())
    return m[0] if m else ''

def generate(model, tok, c, depth, rows=None, steps=3):
    """Greedy generation of up to `steps` tokens at a stopped depth; if rows is given, the loop-3 Q rows are inserted at the original final
    prompt position in loop 1 at every step (amendment 1). Returns the first-step logits and the generated text."""
    ids = list(c['ids'])
    n0 = len(ids)
    out = []
    first = None
    HD = 128
    for _ in range(steps):
        n = len(ids)
        z = [False] * n
        q = list(z)
        q[n0 - 1] = True
        cc = dict(ids=ids, q_mask=q, F_mask=z, cq_mask=z, cF_mask=z)
        if rows is None:
            v = L.stopped(model, cc, depth, INF)[0]
        else:
            src = {}
            for l, r in rows.items():
                t = torch.zeros(1, 16, n, HD, dtype=r.dtype, device=r.device)
                t[:, :, n0 - 1, :] = r
                src[l] = {'Q': t}
            v = L.stopped(model, cc, depth, INF, (('Q', 'q', set(rows), tuple(range(16))),), (1,), src)[0]
        if first is None:
            first = v
        t = int(np.argmax(v))
        out.append(t)
        ids = ids + [t]
        if first_word(tok.decode(out)):
            break
    text = tok.decode(out)
    w = first_word(text)
    return (dict(correct=w == COLORS[c['answer_index']], word=w, text=text, is_color=w in COLORS, four=A.score(first, c)['correct']), first)

def gen(v, c):
    raise RuntimeError('replaced by generate() in amendment 1')

def run(name):
    from .ouro_readout import load_model
    cfg = read(OUT / 'CONFIG.json')
    cases = read(OUT / 'INPUTS.json')[name]
    spec = cfg['models'][name]
    assert not (OUT / f'{name}_RUN.json').exists()
    write(OUT / f'{name}_RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(spec['path'], local_files_only=True)
    model, _ = load_model(spec['path'], spec['layers'])
    t0 = time.perf_counter()
    allL = set(range(spec['layers']))
    allH = tuple(range(16))
    scr = {}
    for c in cases:
        scr[c['case_id']] = {d: generate(model, tok, c, d)[0] for d in (1, 3)}
    write(OUT / f'{name}_SCREEN.json', scr)
    T = [c for c in cases if not scr[c['case_id']][1]['correct'] and scr[c['case_id']][3]['correct']]
    donor = D.derange([c['case_id'] for c in T], {c['case_id']: len(c['ids']) for c in T}, DONOR)
    HD = 128

    def qrow(c, loop):
        cap = L.stopped(model, c, loop, INF, capture_loop=loop)[1]
        return {l: cap[l]['Q'][:, :, -1, :].clone() for l in cap}

    def src(c, rows):
        n = len(c['ids'])
        out = {}
        for l, v in rows.items():
            t = torch.zeros(1, 16, n, HD, dtype=v.dtype, device=v.device)
            t[:, :, n - 1, :] = v
            out[l] = {'Q': t}
        return out
    late = {c['case_id']: qrow(c, 3) for c in T}
    for n_, c in enumerate(T):
        k = c['case_id']
        row = dict(case_id=k, donor=donor.get(k))
        if n_ < 3:
            g_own, v = generate(model, tok, c, 1, qrow(c, 1))
            g_nat, v0 = generate(model, tok, c, 1)
            ok = bool(np.array_equal(v, v0) and g_own['text'] == g_nat['text'])
            append(OUT / f'{name}_VALIDATION.jsonl', dict(case_id=k, identity_bitwise=ok))
            assert ok
        row['Q_same'] = generate(model, tok, c, 1, late[k])[0]
        if k in donor:
            row['Q_shuf'] = generate(model, tok, c, 1, late[donor[k]])[0]
        append(OUT / f'{name}_ROWS.jsonl', row)
    write(OUT / f'{name}_RUN.json', dict(status='COMPLETE', commit=os.environ['GIT_HEAD'], targets=len(T), seconds=time.perf_counter() - t0))

def ci(x, q=(0.025, 0.975)):
    x = np.asarray(x, float)
    ix = np.random.default_rng(BOOT).integers(0, len(x), (20000, len(x)))
    return (100 * np.quantile(x[ix].mean(1), q)).tolist()

def analyze():
    res = {}
    for m in A.MODELS:
        S = read(OUT / f'{m}_SCREEN.json')
        R = [json.loads(l) for l in open(OUT / f'{m}_ROWS.jsonl')]
        P_ = [r for r in R if 'Q_shuf' in r]
        acc = {f'gen_loop{d}': float(np.mean([v[str(d)]['correct'] for v in S.values()])) for d in (1, 3)}
        acc.update({f'four_loop{d}': float(np.mean([v[str(d)]['four'] for v in S.values()])) for d in (1, 3)})
        acc['loop1_noncolor'] = float(np.mean([not v['1']['is_color'] for v in S.values()]))
        acc['loop3_noncolor'] = float(np.mean([not v['3']['is_color'] for v in S.values()]))
        from collections import Counter
        acc['loop1_top_words'] = Counter((v['1']['word'] for v in S.values())).most_common(6)
        s = np.array([r['Q_same']['correct'] for r in P_], float)
        sh = np.array([r['Q_shuf']['correct'] for r in P_], float)
        d = s - sh
        i = ci(d, (0.0125, 0.9875))
        res[m] = dict(accuracy=acc, targets=len(R), paired=len(P_), rescue_same=float(np.mean([r['Q_same']['correct'] for r in R])), rescue_same_ci95=ci([r['Q_same']['correct'] for r in R]), rescue_shuf=float(sh.mean()), delta_pp=100 * float(d.mean()), ci_bonf2=i, supported=bool(100 * d.mean() >= 10 and i[0] > 0))
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps(res, indent=1), flush=True)

def campaign():
    log = OUT / 'CAMPAIGN.log'

    def say(x):
        with open(log, 'a') as f:
            f.write(f'{now()} {x}\n')
    try:
        say(f'START {MODEL}')
        run(MODEL)
        say(f'DONE {MODEL}')
        if all(((OUT / f'{m}_RUN.json').exists() and read(OUT / f'{m}_RUN.json')['status'] == 'COMPLETE' for m in A.MODELS)):
            analyze()
            say('CAMPAIGN_DONE')
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
