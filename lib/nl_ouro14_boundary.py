"""All-layer natural-QA query rescue boundary for Ouro-1.4B, section 7."""
import argparse
import json
import os
import time
import numpy as np
import torch
from .common import ROOT, read, write, append, now, jsonlines
from . import patching as L
from . import rotary as N
from . import natural_scoring as FC
OUT = ROOT / 'experiments/2026-10-17-nl-ouro14-boundary'
RUN3 = ROOT / 'experiments/2026-10-12-ouro26-natural-rescue-fc-powered'
DONOR_SEED = 20261017502
BOOT = 20261017503

def key(item):
    return f"{item['dataset']}_{item['item_index']}"

def run():
    from .ouro_readout import load_model
    cfg = read(RUN3 / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models']['ouro14']
    items = read(RUN3 / 'INPUTS.json')['items']
    by = {key(item): item for item in items}
    assert not (OUT / 'ouro14_RUN.json').exists()
    write(OUT / 'ouro14_RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    started = time.perf_counter()
    patch = (('Q', 'q', set(range(spec['layers'])), tuple(range(16))),)

    def score(item, depth, source=None):
        return FC.judge(FC.cand_scores(model, item['two_hop']['prompt_ids'], item['candidate_ids'], depth, seed, patch if source is not None else (), source))
    native = {}
    for item in items:
        row = dict(key=key(item), dataset=item['dataset'], two_hop={depth: score(item, depth) for depth in (1, 3)})
        append(OUT / 'ouro14_SCREEN.jsonl', row)
        native[row['key']] = row['two_hop']
    targets = [item for item in items if not native[key(item)][1]['correct'] and native[key(item)][3]['correct']]
    if len(targets) < 40:
        write(OUT / 'ouro14_RUN.json', dict(status='COMPLETE', targets=len(targets), underpowered=True))
        return
    rng = np.random.default_rng(DONOR_SEED)
    while True:
        order = rng.permutation(len(targets))
        if all((order[i] != i for i in range(len(targets)))):
            break
    donors = {key(targets[i]): key(targets[order[i]]) for i in range(len(targets))}

    def capture(item, depth):
        ids = item['two_hop']['prompt_ids']
        n = len(ids)
        case = dict(ids=ids, q_mask=[False] * (n - 1) + [True], F_mask=[False] * n, cq_mask=[False] * n, cF_mask=[False] * n)
        captured = L.stopped(model, case, depth, seed, capture_loop=depth)[1]
        return {layer: value['Q'][:, :, n - 1, :].clone() for layer, value in captured.items()}
    late = {key(item): capture(item, 3) for item in targets}
    for index, item in enumerate(targets):
        k = key(item)
        donor = by[donors[k]]
        delta = len(item['two_hop']['prompt_ids']) - len(donor['two_hop']['prompt_ids'])
        source = {layer: N.rerotate(model, value, delta) for layer, value in late[key(donor)].items()}
        row = dict(key=k, dataset=item['dataset'], donor=donors[k], native1=native[k][1], native3=native[k][3], all=score(item, 1, late[k]), all_shuf=score(item, 1, source))
        if index < 2:
            identity = score(item, 1, capture(item, 1))
            error = float(np.max(np.abs(np.array(identity['scores']) - np.array(native[k][1]['scores']))))
            ok = error < 0.02 and identity['correct'] == native[k][1]['correct']
            append(OUT / 'ouro14_VALIDATION.jsonl', dict(key=k, identity_max_abs_score_diff=error, same_choice=ok))
            assert ok
        append(OUT / 'ouro14_ROWS.jsonl', row)
    write(OUT / 'ouro14_RUN.json', dict(status='COMPLETE', targets=len(targets), seconds=time.perf_counter() - started))

def interval(values):
    values = np.asarray(values, float)
    indices = np.random.default_rng(BOOT).integers(0, len(values), (20000, len(values)))
    return (100 * np.quantile(values[indices].mean(1), [0.025, 0.975])).tolist()

def analyze():
    screen = jsonlines(OUT / 'ouro14_SCREEN.jsonl')
    gain = np.array([r['two_hop']['3']['correct'] - r['two_hop']['1']['correct'] for r in screen], float)
    result = dict(items=len(screen), acc={loop: 100 * float(np.mean([r['two_hop'][loop]['correct'] for r in screen])) for loop in ('1', '3')}, gate_pp=100 * float(gain.mean()), gate_ci95=interval(gain))
    rows = jsonlines(OUT / 'ouro14_ROWS.jsonl')
    result['targets'] = len(rows)
    values = lambda arm, rr: np.array([r[arm]['correct'] for r in rr], float)
    delta = values('all', rows) - values('all_shuf', rows)
    result['rescue'] = {arm: 100 * float(values(arm, rows).mean()) for arm in ('all', 'all_shuf')}
    result['B1'] = dict(mean_pp=100 * float(delta.mean()), ci95=interval(delta))
    result['B1']['supported'] = result['B1']['ci95'][0] > 0
    result['margin'] = {arm: float(np.mean([r[arm]['margin'] for r in rows])) for arm in ('native1', 'all', 'all_shuf', 'native3')}
    result['by_dataset'] = {ds: dict(n=len(rr), **{arm: 100 * float(values(arm, rr).mean()) for arm in ('all', 'all_shuf')} if rr else {}) for ds in ('2wiki', 'musique') for rr in [[r for r in rows if r['dataset'] == ds]]}
    write(OUT / 'SUMMARY.json', {'ouro14': result})
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    args = parser.parse_args()
    analyze() if args.action == 'analyze' else run()
