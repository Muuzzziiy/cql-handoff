"""Length-normalized candidate scoring and fixed-input natural QA replay."""
import os, time
import numpy as np
import torch
from .common import ROOT, read, write, append, now
from . import patching as L
from . import rotary as N
OUT = ROOT / 'data/runtime/natural_fc'
HEADS = 16
BOOT = 20261013303
DONOR_SEED = 20261013302

@torch.inference_mode()
def cand_scores(model, prompt, cand_ids, depth, seed, spec=(), source=None):
    from .ouro_readout import NativeCounter
    from torch.nn.attention import sdpa_kernel, SDPBackend
    out = []
    for cid in cand_ids:
        ids = prompt + cid[:-1]
        n = len(ids)
        q = len(prompt) - 1
        c = dict(ids=ids, q_mask=[i == q for i in range(n)], F_mask=[False] * n, cq_mask=[False] * n, cF_mask=[False] * n)
        src = None
        if source is not None:
            D = model.config.hidden_size // model.config.num_attention_heads
            src = {}
            for l, v in source.items():
                t = torch.zeros(1, HEADS, n, D, dtype=v.dtype, device=v.device)
                t[:, :, q, :] = v
                src[l] = {'Q': t}
        pos = torch.arange(q, q + len(cid), device='cuda')
        orig = (model.model.total_ut_steps, model.config.total_ut_steps)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        try:
            model.model.total_ut_steps = model.config.total_ut_steps = depth
            with L.Sel(model, L.masks(c), spec, (depth,) if spec else (), src), sdpa_kernel(SDPBackend.FLASH_ATTENTION):
                o = model(input_ids=torch.tensor([ids], device='cuda'), attention_mask={'full_attention': None}, use_cache=False, past_key_values=None, use_weighted_exit=False, exit_at_step=depth - 1, exit_threshold=1.0, logits_to_keep=pos)
            lp = torch.log_softmax(o.logits[0].float(), -1)
            t = torch.tensor(cid, device='cuda')
            out.append(float(lp[torch.arange(len(cid)), t].mean()))
        finally:
            model.model.total_ut_steps, model.config.total_ut_steps = orig
    return out

def judge(s):
    s = np.asarray(s)
    return dict(correct=bool(int(np.argmax(s)) == 0), margin=float(s[0] - s[1:].max()), scores=s.tolist())

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
    allL = set(range(spec['layers']))
    allH = tuple(range(HEADS))
    spec_q = (('Q', 'q', allL, allH),)
    items = read(OUT / 'INPUTS.json')['items']
    started = time.perf_counter()
    screen = {}
    for it in items:
        p2, pb = (it['two_hop']['prompt_ids'], it['bridge_given']['prompt_ids'])
        row = dict(key=f"{it['dataset']}_{it['item_index']}", dataset=it['dataset'], two_hop={r: judge(cand_scores(model, p2, it['candidate_ids'], r, seed)) for r in (1, 3)}, bridge={r: judge(cand_scores(model, pb, it['candidate_ids'], r, seed)) for r in (1, 2, 3, 4)})
        screen[row['key']] = row
        append(OUT / f'{name}_SCREEN.jsonl', row)
    targets = [it for it in items if not screen[f"{it['dataset']}_{it['item_index']}"]['two_hop'][1]['correct'] and screen[f"{it['dataset']}_{it['item_index']}"]['two_hop'][3]['correct']]
    print(dict(model=name, items=len(items), targets=len(targets), seconds=round(time.perf_counter() - started)), flush=True)

    def qrow(prompt, depth):
        cap = L.stopped(model, dict(ids=prompt, q_mask=[False] * (len(prompt) - 1) + [True], F_mask=[False] * len(prompt), cq_mask=[False] * len(prompt), cF_mask=[False] * len(prompt)), depth, seed, capture_loop=depth)[1]
        return {l: cap[l]['Q'][:, :, len(prompt) - 1, :].clone() for l in cap}
    late = {}
    early = {}
    for it in targets:
        k = f"{it['dataset']}_{it['item_index']}"
        p = it['two_hop']['prompt_ids']
        late[k] = qrow(p, 3)
        early[k] = qrow(p, 1)
    rng = np.random.default_rng(DONOR_SEED)
    while True:
        perm = rng.permutation(len(targets))
        if len(targets) < 2 or all((perm[i] != i for i in range(len(targets)))):
            break
    for i, it in enumerate(targets):
        k = f"{it['dataset']}_{it['item_index']}"
        d = targets[perm[i]]
        dk = f"{d['dataset']}_{d['item_index']}"
        p = it['two_hop']['prompt_ids']
        delta = len(p) - len(d['two_hop']['prompt_ids'])
        rot = lambda rows: {l: N.rerotate(model, v, delta) for l, v in rows.items()}
        row = dict(key=k, dataset=it['dataset'], donor=dk, native1=screen[k]['two_hop'][1], native3=screen[k]['two_hop'][3], s_star=all((screen[k]['bridge'][r]['correct'] for r in (1, 2, 3, 4))), same=judge(cand_scores(model, p, it['candidate_ids'], 1, seed, spec_q, late[k])), shuffled=judge(cand_scores(model, p, it['candidate_ids'], 1, seed, spec_q, rot(late[dk]))), same_loop_donor=judge(cand_scores(model, p, it['candidate_ids'], 1, seed, spec_q, rot(early[dk]))))
        if i < 2:
            ident = judge(cand_scores(model, p, it['candidate_ids'], 1, seed, spec_q, early[k]))
            diff = float(np.max(np.abs(np.array(ident['scores']) - np.array(screen[k]['two_hop'][1]['scores']))))
            assert diff < 0.02 and ident['correct'] == screen[k]['two_hop'][1]['correct'], ('identity patch changed scores', diff)
            append(OUT / f'{name}_VALIDATION.jsonl', dict(key=k, identity_patch_max_abs_score_diff=diff, same_choice=True))
        append(OUT / f'{name}_ROWS.jsonl', row)
    write(OUT / f'{name}_RUN.json', dict(status='COMPLETE', items=len(items), targets=len(targets), seconds=time.perf_counter() - started))
