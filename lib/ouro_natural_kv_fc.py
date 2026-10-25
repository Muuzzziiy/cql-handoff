import argparse
"""Forced-choice natural-language Q/K/V freeze; see experiments/2026-10-12-ouro-natural-kv-fc/DESIGN.md."""
import json
import os
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import patching as L
from . import natural_scoring as FC
OUT = ROOT / 'experiments/2026-10-12-ouro-natural-kv-fc'
KV = ROOT / 'data/runtime/natural'
HEADS = 16
BOOT = 20261013501
ARMS = {'Native': (), 'Q_question': ('Q', 'question'), 'K_facts': ('K', 'facts'), 'V_facts': ('V', 'facts')}

@torch.inference_mode()
def scores(model, case, cand_ids, depth, seed, arm):
    out = []
    allL = set(range(len(model.model.layers)))
    allH = tuple(range(HEADS))
    for cid in cand_ids:
        p = case['prompt_ids']
        ids = p + cid[:-1]
        n = len(ids)
        q = len(p) - 1
        extra = [False] * (n - len(p))
        masks = {'question': torch.tensor(case['question_mask'][:len(p)] + extra, dtype=torch.bool, device='cuda'), 'facts': torch.tensor(case['facts_mask'][:len(p)] + extra, dtype=torch.bool, device='cuda')}
        spec = () if arm == 'Native' else ((ARMS[arm][0], ARMS[arm][1], allL, allH),)
        pos = torch.arange(q, q + len(cid), device='cuda')
        orig = (model.model.total_ut_steps, model.config.total_ut_steps)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        from torch.nn.attention import sdpa_kernel, SDPBackend
        try:
            model.model.total_ut_steps = model.config.total_ut_steps = depth
            sel = L.Sel(model, masks, spec, tuple((l for l in (2, 3, 4) if l <= depth)))
            with sel, sdpa_kernel(SDPBackend.FLASH_ATTENTION):
                o = model(input_ids=torch.tensor([ids], device='cuda'), attention_mask={'full_attention': None}, use_cache=False, past_key_values=None, use_weighted_exit=False, exit_at_step=depth - 1, exit_threshold=1.0, logits_to_keep=pos)
            lp = torch.log_softmax(o.logits[0].float(), -1)
            out.append(float(lp[torch.arange(len(cid)), torch.tensor(cid, device='cuda')].mean()))
        finally:
            model.model.total_ut_steps, model.config.total_ut_steps = orig
    return FC.judge(out)

def run(name):
    from .ouro_readout import load_model
    cfg = read(FC.OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models'][name]
    assert not (OUT / f'{name}_RUN.json').exists()
    write(OUT / f'{name}_RUN.json', dict(status='RUNNING', started=now(), commit=os.environ['GIT_HEAD']))
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    model, _ = load_model(spec['path'], spec['layers'])
    cases = {(c['dataset'], c['item_index'], c['task']): c for c in read(KV / 'INPUTS.json')['cases']}
    items = read(FC.OUT / 'INPUTS.json')['items']
    screen = {x['key']: x for x in (json.loads(l) for l in (FC.OUT / f'{name}_SCREEN.jsonl').read_text().splitlines() if l.strip())}
    for i, it in enumerate(items):
        k = f"{it['dataset']}_{it['item_index']}"
        row = dict(key=k, dataset=it['dataset'])
        for task in ('two_hop', 'bridge_given'):
            c = cases[it['dataset'], it['item_index'], task]
            row[task] = {arm: {r: scores(model, c, it['candidate_ids'], r, seed, arm) for r in (1, 3)} for arm in ARMS}
        if i < 2:
            a = np.array(row['two_hop']['Native'][1]['scores'])
            b = np.array(screen[k]['two_hop']['1']['scores'])
            assert np.max(np.abs(a - b)) < 1e-06, 'Native scores differ from rescue-fc screen'
            append(OUT / f'{name}_VALIDATION.jsonl', dict(key=k, native_matches_screen=True))
        append(OUT / f'{name}_ROWS.jsonl', row)
    write(OUT / f'{name}_RUN.json', dict(status='COMPLETE', items=len(items)))

def analyze():
    res = {}
    for m in ('ouro14', 'ouro26'):
        R = [json.loads(x) for x in (OUT / f'{m}_ROWS.jsonl').read_text().splitlines() if x.strip()]
        n = len(R)
        ix = np.random.default_rng(BOOT).integers(0, n, (20000, n))
        g = lambda task, arm, r, k: np.array([x[task][arm][str(r)][k] for x in R], float)
        d = g('two_hop', 'K_facts', 3, 'margin') - g('two_hop', 'V_facts', 3, 'margin')
        prim = dict(mean=float(d.mean()), ci_bonf2=np.quantile(d[ix].mean(1), [0.0125, 0.9875]).tolist())
        prim['supported'] = prim['ci_bonf2'][0] > 0
        acc = {f'{t}/{a}/loop{r}': float(g(t, a, r, 'correct').mean()) for t in ('two_hop', 'bridge_given') for a in ARMS for r in (1, 3)}
        gain = g('two_hop', 'Native', 3, 'correct') - g('two_hop', 'Native', 1, 'correct')
        rho = {a: float((g('two_hop', a, 3, 'correct') - g('two_hop', a, 1, 'correct')).mean() / gain.mean()) for a in ARMS if a != 'Native'}
        scd = {a: float((g('two_hop', 'Native', 3, 'correct') - g('two_hop', a, 3, 'correct')).mean() - (g('bridge_given', 'Native', 3, 'correct') - g('bridge_given', a, 3, 'correct')).mean()) for a in ARMS if a != 'Native'}
        res[m] = dict(n=n, primary_V_vs_K_margin=prim, accuracy=acc, rho=rho, SCD_vs_bridge=scd, native_gain_pp=100 * float(gain.mean()))
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps(res, indent=1), flush=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    parser.add_argument('--model', choices=('ouro14', 'ouro26'))
    args = parser.parse_args()
    if args.action != 'analyze' and args.model is None:
        parser.error('--model is required for inference')
    analyze() if args.action == 'analyze' else run(args.model)
