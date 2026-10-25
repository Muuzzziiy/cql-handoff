"""The all-layer, all-head query rescue replication reported in section 5."""
import argparse
import json
import os
import time
import numpy as np
import torch
from .common import ROOT, read, write, append, now, jsonlines
from . import ouro_advisor_stagecd as A
from . import patching as L
OUT = ROOT / 'experiments/2026-10-15-ouro14-rescue-replication'

def run():
    from .ouro_readout import load_model
    cfg = read(OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['model']
    assert not (OUT / 'RUN.json').exists()
    write(OUT / 'RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    started = time.perf_counter()
    patch = (('Q', 'q', set(range(spec['layers'])), tuple(range(16))),)
    for pair in read(OUT / 'INPUTS.json'):
        c = pair['host']
        native1 = L.stopped(model, c, 1, seed)[0]
        native3, late = L.stopped(model, c, 3, seed, capture_loop=3)
        row = dict(graph=pair['graph'], host=dict(loop1=A.score(native1, c), loop3=A.score(native3, c)))
        if not row['host']['loop1']['correct'] and row['host']['loop3']['correct']:
            row['rescue_all'] = A.score(L.stopped(model, c, 1, seed, patch, (1,), late)[0], c)
        append(OUT / 'ROWS.jsonl', row)
    write(OUT / 'RUN.json', dict(status='COMPLETE', seconds=time.perf_counter() - started))

def analyze():
    rows = jsonlines(OUT / 'ROWS.jsonl')
    targets = [r for r in rows if 'rescue_all' in r]
    result = dict(scenes=len(rows), rescue=dict(targets=len(targets), rescue_all=float(np.mean([r['rescue_all']['correct'] for r in targets]))))
    write(OUT / 'SUMMARY.json', result)
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    args = parser.parse_args()
    analyze() if args.action == 'analyze' else run()
