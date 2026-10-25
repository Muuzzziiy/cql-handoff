"""Natural-language semantic crossover; see experiments/2026-10-17-nl-crossover/DESIGN.md."""
import argparse
import json
import os
import time
import traceback
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from .natural_data import normalize
from . import patching as L
from . import rotary as N
from . import natural_scoring as FC
OUT = ROOT / 'experiments/2026-10-17-nl-crossover'
RUN3 = ROOT / 'experiments/2026-10-12-ouro26-natural-rescue-fc-powered'
PAIR, EDIT, SLOT, UNREL = (20261017701, 20261017702, 20261017703, 20261017704)
BOOT = 20261013303
HEADS = 16
MODEL = 'ouro26'
BANDS = {'ouro26': set(range(36, 48))}

def lines(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]

def run(m):
    from .ouro_readout import load_model
    cfg = read(OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models'][m]
    P = read(OUT / 'INPUTS.json')['pairs']
    items = {f"{it['dataset']}_{it['item_index']}": it for it in read(RUN3 / 'INPUTS.json')['items']}
    dscr = {r['key']: r['two_hop']['3']['correct'] for r in lines(RUN3 / 'ouro26_SCREEN.jsonl')}
    assert not (OUT / f'{m}_RUN.json').exists()
    write(OUT / f'{m}_RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    t0 = time.perf_counter()
    allL = set(range(spec['layers']))
    allH = tuple(range(HEADS))
    band = BANDS[m]
    sc = lambda p, depth, sp=(), src=None: FC.judge(FC.cand_scores(model, p['prompt_ids'], p['candidate_ids'], depth, seed, sp, src))

    def qrow(ids, depth):
        n = len(ids)
        cap = L.stopped(model, dict(ids=ids, q_mask=[False] * (n - 1) + [True], F_mask=[False] * n, cq_mask=[False] * n, cF_mask=[False] * n), depth, seed, capture_loop=depth)[1]
        return {l: cap[l]['Q'][:, :, n - 1, :].clone() for l in cap}
    cache = {}

    def late(k):
        if k not in cache:
            cache[k] = qrow(items[k]['two_hop']['prompt_ids'], 3)
        return cache[k]

    def rot(p, k):
        delta = len(p['prompt_ids']) - len(items[k]['two_hop']['prompt_ids'])
        return {l: N.rerotate(model, v, delta) for l, v in late(k).items()}
    Q = lambda layers: (('Q', 'q', set(layers), allH),)
    nid = 0
    gated = 0
    for p in P:
        row = dict(pair_id=p['pair_id'], dataset=p['dataset'], slot=p['slot'], native1=sc(p, 1), native3=sc(p, 3), donor_loop3_correct=bool(dscr[p['donor']]))
        row['gated'] = bool(row['native3']['correct'] and row['donor_loop3_correct'])
        if row['gated']:
            gated += 1
            if nid < 20:
                ident = sc(p, 1, Q(allL), qrow(p['prompt_ids'], 1))
                mx = float(np.max(np.abs(np.array(ident['scores']) - np.array(row['native1']['scores']))))
                ok = choice(ident) == choice(row['native1']) and mx < 0.05
                append(OUT / f'{m}_VALIDATION.jsonl', dict(pair_id=p['pair_id'], max_abs=mx, same_top=choice(ident) == choice(row['native1']), ok=ok))
                nid += 1
                if not ok:
                    append(OUT / f'{m}_ROWS.jsonl', row)
                    write(OUT / f'{m}_RUN.json', dict(status='STOPPED_IDENTITY', pair=p['pair_id'], max_abs=mx, commit=os.environ['GIT_HEAD']))
                    return
            sd, su = (rot(p, p['donor']), rot(p, p['unrelated']))
            row.update(arm1=sc(p, 1, Q(allL), sd), arm2=sc(p, 1, Q(allL), su), arm3=sc(p, 1, Q(band), sd), arm4=sc(p, 1, Q(band), su), arm5=sc(p, 3, Q(allL), sd))
        append(OUT / f'{m}_ROWS.jsonl', row)
        if len(cache) > 400:
            cache.clear()
    st = 'COMPLETE' if m != 'ouro26' or gated >= 150 else 'STOPPED_TOO_FEW_GATED'
    write(OUT / f'{m}_RUN.json', dict(status=st, pairs=len(P), gated=gated, commit=os.environ['GIT_HEAD'], seconds=time.perf_counter() - t0))
NAMES = ('A_r', 'A_d2', 'A_d', 'X')

def choice(j):
    return int(np.argmax(j['scores']))

def boot(d, q):
    d = np.asarray(d, float)
    ix = np.random.default_rng(BOOT).integers(0, len(d), (20000, len(d)))
    return (100 * np.quantile(d[ix].mean(1), q)).tolist()

def summarize(R, m):
    G = [r for r in R if r['gated']]
    arms = ['native1', 'native3', 'arm1', 'arm2', 'arm3', 'arm4', 'arm5']
    share = lambda a, rr: {NAMES[i]: 100 * float(np.mean([choice(r[a]) == i for r in rr])) for i in range(4)} if rr else None
    out = dict(pairs=len(R), gated=len(G), gate_fail=dict(recipient=sum((not r['native3']['correct'] for r in R)), donor=sum((not r['donor_loop3_correct'] for r in R))), unpatched_loop1_all_pairs=share('native1', R), shares={a: share(a, G) for a in arms})
    if not G:
        return out
    ind = lambda a, i: np.array([choice(r[a]) == i for r in G], float)
    q = (0.0125, 0.9875) if m == 'ouro26' else (0.025, 0.975)
    for nm, x, y in (('X1', ind('arm1', 1), ind('arm2', 1)), ('X2', ind('arm1', 1), ind('arm1', 2)), ('band_X1', ind('arm3', 1), ind('arm4', 1)), ('band_X2', ind('arm3', 1), ind('arm3', 2))):
        out[nm] = dict(mean_pp=100 * float((x - y).mean()), ci=boot(x - y, q if nm in ('X1', 'X2') else (0.025, 0.975)))
        if nm in ('X1', 'X2'):
            out[nm]['supported'] = bool(out[nm]['ci'][0] > 0) if m == 'ouro26' else None
    out['margins'] = {a: dict(d2_minus_d=float(np.mean([r[a]['scores'][1] - r[a]['scores'][2] for r in G])), r_margin=float(np.mean([r[a]['margin'] for r in G]))) for a in arms}
    out['by_dataset'] = {ds: dict(n=len(rr), **{a: share(a, rr) for a in ('arm1', 'arm2', 'arm3', 'arm4')}) for ds in ('2wiki', 'musique') for rr in [[r for r in G if r['dataset'] == ds]]}
    out['by_slot'] = {s: dict(n=len(rr), **{a: share(a, rr) for a in ('native1', 'arm1', 'arm2')}) for s in (1, 2, 3) for rr in [[r for r in G if r['slot'] == s]]}
    return out

def analyze():
    res = {m: summarize(lines(OUT / f'{m}_ROWS.jsonl'), m) for m in ('ouro26',) if (OUT / f'{m}_ROWS.jsonl').exists()}
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
        say(f"DONE {MODEL} {read(OUT / f'{MODEL}_RUN.json')['status']}")
        analyze()
    except Exception:
        say('FAILED\n' + traceback.format_exc())
        raise
if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('action', choices=['campaign', 'analyze'])
    a.add_argument('--model', choices=('ouro26',), default='ouro26')
    x = a.parse_args()
    globals()['MODEL'] = x.model
    {'campaign': campaign, 'analyze': analyze}[x.action]()
