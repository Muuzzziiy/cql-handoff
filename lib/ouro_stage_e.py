"""All-layer, all-head crossed query swaps reported in section 6."""
import argparse
import json
import os
import time
import numpy as np
import torch
from .common import ROOT, read, write, append, now, jsonlines, MODELS
from .synthetic import COLORS
from . import ouro_advisor_stagecd as A
from . import patching as L
OUT = ROOT / 'experiments/2026-10-12-ouro-stage-e-swap'
BOOT = 20261013003

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
    started = time.perf_counter()
    inp = read(OUT / 'INPUTS.json')
    scenes = {s['graph']: s for s in inp['scenes'][name]}
    donors = {int(k): v for k, v in inp['donors'][name].items()}
    late = {}
    patch = (('Q', 'q', set(range(spec['layers'])), tuple(range(16))),)

    def capture(graph):
        if graph not in late:
            late[graph] = L.stopped(model, scenes[graph]['cases']['q2'], 3, seed, capture_loop=3)[1]
        return late[graph]
    for graph, donor in donors.items():
        c = scenes[graph]['cases']['q2']
        source = capture(donor['donor'])
        row = dict(graph=graph, donor=donor['donor'], predictions=donor['predictions'])
        for loop in (1, 3):
            logits = L.stopped(model, c, loop, seed, patch, (loop,), source)[0]
            scores = np.asarray(logits, dtype=float)[c['candidate_ids']]
            row[f'r{loop}_all'] = dict(pred=COLORS[int(np.argmax(scores))], logits=scores.tolist())
            row[f'r{loop}_native'] = COLORS[int(np.argmax(np.asarray(L.stopped(model, c, loop, seed)[0])[c['candidate_ids']]))]
        if graph < 2:
            ref = A.stopped(model, c, 1, seed, (('Q', 'q'),), (1,), source)[0]
            same = L.stopped(model, c, 1, seed, patch, (1,), source)[0]
            assert np.array_equal(ref, same)
            append(OUT / f'{name}_VALIDATION.jsonl', dict(graph=graph, all_heads_equals_stage_d=True))
        append(OUT / f'{name}_E1_ROWS.jsonl', row)
    write(OUT / f'{name}_RUN.json', dict(status='COMPLETE', seconds=time.perf_counter() - started))

def analyze():
    result = {}
    for model in MODELS:
        rows = jsonlines(OUT / f'{model}_E1_ROWS.jsonl')
        n = len(rows)
        indices = np.random.default_rng(BOOT).integers(0, n, (20000, n))
        cells = {}
        for arm in ('r1_all', 'r3_all'):
            cells[arm] = {}
            for prediction in ('recipient_composition', 'donor_bridge', 'donor_answer', 'donor_line'):
                values = np.array([r[arm]['pred'] == r['predictions'][prediction] for r in rows], float)
                cells[arm][prediction] = dict(rate=float(values.mean()), ci95=np.quantile(values[indices].mean(1), [0.025, 0.975]).tolist())
        for loop in (1, 3):
            cells[f'r{loop}_native'] = {}
            for key in ('recipient_composition', 'donor_bridge', 'donor_answer', 'donor_line'):
                values = np.array([r[f'r{loop}_native'] == r['predictions'][key] for r in rows], float)
                cells[f'r{loop}_native'][key] = dict(rate=float(values.mean()), ci95=np.quantile(values[indices].mean(1), [0.025, 0.975]).tolist())
        result[model] = dict(E1=cells)
    write(OUT / 'SUMMARY.json', result)
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    parser.add_argument('--model', choices=MODELS)
    args = parser.parse_args()
    if args.action == 'run' and args.model is None:
        parser.error('--model is required')
    analyze() if args.action == 'analyze' else run(args.model)
