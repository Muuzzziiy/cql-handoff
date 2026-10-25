"""All-layer query replication and the fact K/V co-freezes reported in section 4."""
import argparse
import json
import os
import time
import numpy as np
import torch
from .common import ROOT, read, write, append, now, jsonlines, MODELS
from . import ouro_advisor_stagecd as A
from . import patching as L
OUT = ROOT / 'experiments/2026-10-12-ouro-rescue-controls'
BOOT = 20261012905

def run(name):
    from .ouro_readout import load_model
    cfg = read(OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models'][name]
    assert not (OUT / f'{name}_RUN.json').exists()
    write(OUT / f'{name}_RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    layers = set(range(spec['layers']))
    heads = tuple(range(16))
    cases = read(OUT / 'INPUTS.json')[name]
    started = time.perf_counter()
    arms = {'Native': (), 'V_F': (('V', 'F', layers, heads),), 'KV_F': (('K', 'F', layers, heads), ('V', 'F', layers, heads)), 'KV_mem': (('K', 'mem', layers, heads), ('V', 'mem', layers, heads))}
    for c in cases:
        outputs = {arm: L.all_loops(model, c, patch, seed) for arm, patch in arms.items()}
        assert all((np.array_equal(outputs['Native'][0], v[0]) for v in outputs.values()))
        append(OUT / f'{name}_B_ROWS.jsonl', dict(case_id=c['case_id'], graph=c['graph'], **{arm: {f'loop{l + 1}': A.score(v[l], c) for l in range(4)} for arm, v in outputs.items()}))
    rows = {r['case_id']: r for r in jsonlines(OUT / f'{name}_B_ROWS.jsonl')}
    for c in cases:
        native = rows[c['case_id']]['Native']
        if native['loop1']['correct'] or not native['loop3']['correct']:
            continue
        late = L.stopped(model, c, 3, seed, capture_loop=3)[1]
        vector = L.stopped(model, c, 1, seed, (('Q', 'q', layers, heads),), (1,), late)[0]
        append(OUT / f'{name}_A1_ROWS.jsonl', dict(case_id=c['case_id'], graph=c['graph'], all=A.score(vector, c)))
    write(OUT / f'{name}_RUN.json', dict(status='COMPLETE', seconds=time.perf_counter() - started))

def analyze():
    results = {}
    for model in MODELS:
        rows = jsonlines(OUT / f'{model}_B_ROWS.jsonl')
        rescue = jsonlines(OUT / f'{model}_A1_ROWS.jsonl')
        acc = lambda a, l: np.array([r[a][f'loop{l}']['correct'] for r in rows], float)
        gain = acc('Native', 3) - acc('Native', 1)
        indices = np.random.default_rng(BOOT).integers(0, len(rows), (20000, len(rows)))
        delta = {a: acc(a, 3) - acc(a, 1) for a in ('V_F', 'KV_F', 'KV_mem')}
        contrasts = {a: dict(rho=float(v.mean() / gain.mean()), ci95=np.quantile(v[indices].mean(1) / gain[indices].mean(1), [0.025, 0.975]).tolist()) for a, v in delta.items()}
        difference = (delta['KV_F'][indices].mean(1) - delta['V_F'][indices].mean(1)) / gain[indices].mean(1)
        primary = dict(mean=contrasts['KV_F']['rho'] - contrasts['V_F']['rho'], ci_family=np.quantile(difference, [0.0125, 0.9875]).tolist())
        primary['supported'] = primary['ci_family'][0] > 0
        contrasts.update(primary_KV_F_minus_V_F=primary, native_gain_pp=100 * float(gain.mean()))
        results[model] = dict(A1=dict(all=float(np.mean([r['all']['correct'] for r in rescue]))), B=contrasts)
    write(OUT / 'SUMMARY.json', results)
    print(json.dumps(results, indent=2))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    parser.add_argument('--model', choices=MODELS)
    args = parser.parse_args()
    if args.action == 'run' and args.model is None:
        parser.error('--model is required')
    analyze() if args.action == 'analyze' else run(args.model)
