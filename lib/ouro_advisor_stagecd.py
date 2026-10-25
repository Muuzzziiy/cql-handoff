import argparse
"""Protocol-coordinate Stage C freeze and Stage D late-Q rescue; see experiments/2026-10-12-ouro-advisor-stagecd/DESIGN.md."""
import os
import time
import traceback
import numpy as np
import torch
import torch.nn.functional as F
from .common import ROOT, read, write, append, now
from .common import MODELS, jsonlines
OUT = ROOT / 'experiments/2026-10-12-ouro-advisor-stagecd'
QUERIES = {'q2': 'two_hop', 'q1a': 'person_box', 'q1b': 'box_color'}
FREEZE = {'Native': (), 'I_Q': (('Q', 'q'),), 'I_K': (('K', 'F'),), 'I_V': (('V', 'F'),), 'C_Q': (('Q', 'cq'),), 'C_K': (('K', 'cF'),), 'C_V': (('V', 'cF'),)}
CONFIG = dict(stage_c_seed={'ouro14': 20261012701, 'ouro26': 20261012702}, stage_d_seed={'ouro14': 20261012703, 'ouro26': 20261012704}, donor_seed=20261012705, bootstrap_seed=20261012706, n_c=400, n_d=600, r_primary=1, r_secondary=2, s=3, R=3, inference_seed=2026092421, bootstrap_replicates=20000)

class Patch:
    """At the SDPA boundary: capture operands at loop `capture_loop`; replace (operand, mask) with `source[layer][operand]`
    at loops in `loops`. source=None means use this forward's own loop-1 capture (freeze)."""

    def __init__(self, model, masks, ops, loops, source=None, capture_loop=None):
        self.model, self.masks, self.ops, self.loops, self.source, self.capture_loop = (model, masks, ops, set(loops), source, capture_loop)
        self.own = {}
        self.captured = {}
        self.orig = F.scaled_dot_product_attention
        self.handles = []
        self.calls = 0
        self.replaced = 0

    def __enter__(self):
        for i, layer in enumerate(self.model.model.layers):

            def before(_m, _a, kw, i=i):
                self.active = (int(kw['current_ut']) + 1, i)
            self.handles.append(layer.register_forward_pre_hook(before, with_kwargs=True))
        F.scaled_dot_product_attention = self.call
        return self

    def __exit__(self, *a):
        F.scaled_dot_product_attention = self.orig
        for h in self.handles:
            h.remove()

    def call(self, q, k, v, *args, **kw):
        loop, layer = self.active
        self.calls += 1
        ops = {'Q': q, 'K': k, 'V': v}
        assert not args and kw.get('is_causal') is True
        if loop == 1 and self.source is None and self.ops:
            self.own[layer] = {n: x.detach().clone() for n, x in ops.items()}
        if loop == self.capture_loop:
            self.captured[layer] = {n: x.detach().clone() for n, x in ops.items()}
        if loop in self.loops:
            src = self.own if self.source is None else self.source
            for name, region in self.ops:
                ops[name] = torch.where(self.masks[region][None, None, :, None], src[layer][name], ops[name])
                self.replaced += 1
        return self.orig(ops['Q'], ops['K'], ops['V'], **kw)

def masks_of(case):
    return {k: torch.tensor(case[k + '_mask'], dtype=torch.bool, device='cuda') for k in ('q', 'F', 'cq', 'cF')}

@torch.inference_mode()
def all_loops(model, case, ops, seed):
    from .ouro_readout import read_all_loops
    with Patch(model, masks_of(case), ops, loops=(2, 3, 4)) as p:
        v, _ = read_all_loops(model, torch.tensor([case['ids']], device='cuda'), seed)
    assert p.calls == 4 * len(model.model.layers) and p.replaced == 3 * len(ops) * len(model.model.layers)
    return v

@torch.inference_mode()
def stopped(model, case, depth, seed, ops=(), loops=(), source=None, capture_loop=None):
    from .ouro_readout import author_stopped_forward
    with Patch(model, masks_of(case), ops, loops, source, capture_loop) as p:
        v = author_stopped_forward(model, torch.tensor([case['ids']], device='cuda'), depth, seed)
    n = len(model.model.layers)
    assert p.calls == depth * n and p.replaced == len(ops) * n * len([l for l in loops if l <= depth])
    return (v, p.captured)

def score(vec, case):
    x = np.asarray(vec, dtype=np.float64)[case['candidate_ids']]
    t = case['answer_index']
    return dict(correct=bool(int(np.argmax(x)) == t), margin=float(x[t] - np.delete(x, t).max()), candidate_logits=x.tolist())

def run(name):
    from .ouro_readout import load_model
    cfg = read(OUT / 'CONFIG.json')
    seed = cfg['inference_seed']
    spec = cfg['models'][name]
    assert not (OUT / f'{name}_RUN.json').exists()
    rec = dict(status='RUNNING', model=name, started_utc=now(), commit=os.environ['GIT_HEAD'])
    write(OUT / f'{name}_RUN.json', rec)
    started = time.perf_counter()
    try:
        torch.set_num_threads(4)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        model, _ = load_model(spec['path'], spec['layers'])
        inp = read(OUT / 'INPUTS.json')[name]
        for c in inp['stage_c']:
            first = None
            for arm, ops in FREEZE.items():
                v = all_loops(model, c, ops, seed)
                first = v[0] if first is None else first
                assert np.array_equal(first, v[0]), ('loop-1 differs', arm)
                append(OUT / f'{name}_C_ROWS.jsonl', dict(case_id=c['case_id'], graph=c['graph'], query=c['query'], arm=arm, **{f'loop{l + 1}': score(v[l], c) for l in range(4)}))
            if c['graph'] < 2 and c['query'] == 'q2':
                with torch.inference_mode(), Patch(model, masks_of(c), (('Q', 'q'), ('K', 'F'), ('V', 'F')), loops=(1,)) as p:
                    from .ouro_readout import read_all_loops
                    nv, _ = read_all_loops(model, torch.tensor([c['ids']], device='cuda'), seed)
                ok = bool(np.array_equal(nv, all_loops(model, c, (), seed)))
                append(OUT / f'{name}_VALIDATION.jsonl', dict(kind='freeze_noop', case_id=c['case_id'], exact=ok))
                assert ok
            if c['graph'] % 50 == 0 and c['query'] == 'q2':
                print(dict(model=name, stage='C', graph=c['graph'], seconds=round(time.perf_counter() - started)), flush=True)
        cases = inp['stage_d']
        byid = {c['case_id']: c for c in cases}
        s = cfg['s']
        screen = {}
        for c in cases:
            res = {d: score(stopped(model, c, d, seed)[0], c) for d in (1, 2, s)}
            screen[c['case_id']] = res
            append(OUT / f'{name}_D_SCREEN.jsonl', dict(case_id=c['case_id'], graph=c['graph'], **{f'loop{d}': r for d, r in res.items()}))
        for r in (cfg['r_primary'], cfg['r_secondary']):
            targets = [c for c in cases if not screen[c['case_id']][r]['correct'] and screen[c['case_id']][s]['correct']]
            rng = np.random.default_rng(cfg['donor_seed'] + r)
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
            late = {}
            for c in targets:
                if c['case_id'] not in late:
                    late[c['case_id']] = stopped(model, c, s, seed, capture_loop=s)[1]
            for c in targets:
                same = score(stopped(model, c, r, seed, (('Q', 'q'),), (r,), late[c['case_id']])[0], c)
                row = dict(case_id=c['case_id'], graph=c['graph'], r=r, s=s, native_r=screen[c['case_id']][r], native_s=screen[c['case_id']][s], same=same)
                if c['case_id'] in donor:
                    d = donor[c['case_id']]
                    row['donor'] = d
                    row['donor_same_answer'] = byid[d]['answer_index'] == c['answer_index']
                    row['shuffled'] = score(stopped(model, c, r, seed, (('Q', 'q'),), (r,), late[d])[0], c)
                    donor_r = stopped(model, byid[d], r, seed, capture_loop=r)[1]
                    row['same_loop_donor'] = score(stopped(model, c, r, seed, (('Q', 'q'),), (r,), donor_r)[0], c)
                own = stopped(model, c, r, seed, capture_loop=r)[1]
                sl, _ = stopped(model, c, r, seed, (('Q', 'q'),), (r,), own)
                base, _ = stopped(model, c, r, seed)
                row['same_loop_exact'] = bool(np.array_equal(sl, base))
                assert row['same_loop_exact']
                append(OUT / f'{name}_D_ROWS.jsonl', row)
            for c in [c for c in cases if screen[c['case_id']][s]['correct']]:
                early = stopped(model, c, r, seed, capture_loop=r)[1]
                append(OUT / f'{name}_D_DIRECTION.jsonl', dict(case_id=c['case_id'], r=r, s=s, patched=score(stopped(model, c, s, seed, (('Q', 'q'),), (s,), early)[0], c)))
            print(dict(model=name, stage='D', r=r, targets=len(targets), donors=len(donor), seconds=round(time.perf_counter() - started)), flush=True)
        rec.update(status='COMPLETE')
    except BaseException:
        rec.update(status='FAILED_INCOMPLETE', traceback=traceback.format_exc())
        raise
    finally:
        rec.update(finished_utc=now(), elapsed_seconds=time.perf_counter() - started)
        write(OUT / f'{name}_RUN.json', rec)

def boot_ci(x, seed, reps):
    ix = np.random.default_rng(seed).integers(0, len(x), (reps, len(x)))
    return np.quantile(x[ix].mean(axis=1), [0.025, 0.975]).tolist()

def analyze():
    assert not (OUT / 'SUMMARY.json').exists()
    cfg = read(OUT / 'CONFIG.json')
    R = cfg['R']
    reps = cfg['bootstrap_replicates']
    bs = cfg['bootstrap_seed']
    out = {}
    for name in MODELS:
        rows = {(r['graph'], r['query'], r['arm']): r for r in jsonlines(OUT / f'{name}_C_ROWS.jsonl')}
        G = sorted({k[0] for k in rows})
        A = lambda q, arm, l: np.array([rows[g, q, arm][f'loop{l}']['correct'] for g in G], dtype=float)
        M = lambda q, arm, l: np.array([rows[g, q, arm][f'loop{l}']['margin'] for g in G])
        sstar = np.array([all((rows[g, q, 'Native'][f'loop{l}']['correct'] for q in ('q1a', 'q1b') for l in range(1, 5))) for g in G])
        ix = np.random.default_rng(bs).integers(0, len(G), (reps, len(G)))
        res = {'S_star_n': int(sstar.sum())}
        for subset, mask in (('full', np.ones(len(G), bool)), ('S_star', sstar)):
            jx = ix[:, :mask.sum()] if subset == 'full' else np.random.default_rng(bs + 1).integers(0, mask.sum(), (reps, mask.sum()))
            sub = {}
            gain = A('q2', 'Native', R)[mask] - A('q2', 'Native', 1)[mask]
            sub['two_hop_gain_pp'] = dict(mean=float(100 * gain.mean()), ci95=(100 * np.quantile(gain[jx].mean(1), [0.025, 0.975])).tolist())
            g1 = np.maximum(A('q1a', 'Native', R)[mask] - A('q1a', 'Native', 1)[mask], A('q1b', 'Native', R)[mask] - A('q1b', 'Native', 1)[mask])
            sub['G_comp_pp'] = dict(mean=float(100 * (gain - g1).mean()), ci95=(100 * np.quantile((gain - g1)[jx].mean(1), [0.025, 0.975])).tolist())
            for arm in [a for a in FREEZE if a != 'Native']:
                num = A('q2', arm, R)[mask] - A('q2', arm, 1)[mask]
                den = gain
                rho = num[jx].mean(1) / (den[jx].mean(1) + 1e-09)
                d2 = A('q2', 'Native', R)[mask] - A('q2', arm, R)[mask]
                d1 = np.maximum(A('q1a', 'Native', R)[mask] - A('q1a', arm, R)[mask], A('q1b', 'Native', R)[mask] - A('q1b', arm, R)[mask])
                d1a = A('q1a', 'Native', R)[mask] - A('q1a', arm, R)[mask]
                d1b = A('q1b', 'Native', R)[mask] - A('q1b', arm, R)[mask]
                scd = d2[jx].mean(1) - np.maximum(d1a[jx].mean(1), d1b[jx].mean(1))
                loss = np.maximum(d1a[jx].mean(1), d1b[jx].mean(1))
                sub[arm] = dict(rho=float(num.mean() / (den.mean() + 1e-09)), rho_ci95=np.quantile(rho, [0.025, 0.975]).tolist(), SCD_pp=float(100 * (d2.mean() - max(d1a.mean(), d1b.mean()))), SCD_ci95=(100 * np.quantile(scd, [0.025, 0.975])).tolist(), one_hop_loss_pp=float(100 * max(d1a.mean(), d1b.mean())), one_hop_loss_ci95=(100 * np.quantile(loss, [0.025, 0.975])).tolist(), two_hop_margin_R=float(M('q2', arm, R)[mask].mean()))
            sub['Native_two_hop_margin'] = {f'loop{l}': float(M('q2', 'Native', l)[mask].mean()) for l in range(1, 5)}
            t = sub
            sub['caseA'] = dict(rho_Q_le_0_5=t['I_Q']['rho'] <= 0.5, rho_K_ge_0_8=t['I_K']['rho'] >= 0.8, rho_V_ge_0_8=t['I_V']['rho'] >= 0.8, K_loss_le_3pp=t['I_K']['one_hop_loss_pp'] <= 3, V_loss_le_3pp=t['I_V']['one_hop_loss_pp'] <= 3, SCD_Q_gt_K=t['I_Q']['SCD_pp'] > t['I_K']['SCD_pp'], SCD_Q_gt_V=t['I_Q']['SCD_pp'] > t['I_V']['SCD_pp'])
            res[subset] = sub
        d = {}
        for r in (cfg['r_primary'], cfg['r_secondary']):
            rr = [x for x in jsonlines(OUT / f'{name}_D_ROWS.jsonl') if x['r'] == r]
            paired = [x for x in rr if 'shuffled' in x]
            same = np.array([x['same']['correct'] for x in rr], float)
            diff = np.array([x['same']['correct'] - x['shuffled']['correct'] for x in paired], float)
            ms = np.array([x['same']['margin'] - x['native_r']['margin'] for x in rr])
            dr = [x for x in jsonlines(OUT / f'{name}_D_DIRECTION.jsonl') if x['r'] == r]
            d[f'r{r}'] = dict(targets=len(rr), paired=len(paired), rescue_same=float(same.mean()), rescue_same_ci95=boot_ci(same, bs, reps), rescue_shuffled=float(np.mean([x['shuffled']['correct'] for x in paired])), delta_rescue_pp=float(100 * diff.mean()), rescue_same_loop_donor=float(np.mean([x['same_loop_donor']['correct'] for x in paired])), delta_ci95_pp=(100 * np.array(boot_ci(diff, bs, reps))).tolist(), delta_bonferroni4_pp=(100 * np.quantile(diff[np.random.default_rng(bs).integers(0, len(diff), (reps, len(diff)))].mean(1), [0.025 / 4, 1 - 0.025 / 4])).tolist(), donor_same_answer=int(sum((x['donor_same_answer'] for x in paired))), margin_shift=float(ms.mean()), margin_shift_ci95=boot_ci(ms, bs, reps), directional_still_correct=float(np.mean([x['patched']['correct'] for x in dr])), directional_n=len(dr), success=bool(boot_ci(diff, bs, reps)[0] > 0))
        res['stage_d'] = d
        out[name] = res
    write(OUT / 'SUMMARY.json', out)
    for m in MODELS:
        print(m, 'S*', out[m]['S_star_n'], {a: (round(out[m]['full'][a]['rho'], 3), round(out[m]['full'][a]['SCD_pp'], 1), round(out[m]['full'][a]['one_hop_loss_pp'], 1)) for a in FREEZE if a != 'Native'}, out[m]['full']['caseA'], {k: (v['targets'], round(v['rescue_same'], 3), round(v['rescue_shuffled'], 3), round(v['delta_rescue_pp'], 1), [round(x, 1) for x in v['delta_ci95_pp']]) for k, v in out[m]['stage_d'].items()}, flush=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    parser.add_argument('--model', choices=('ouro14', 'ouro26'))
    args = parser.parse_args()
    if args.action != 'analyze' and args.model is None:
        parser.error('--model is required for inference')
    analyze() if args.action == 'analyze' else run(args.model)
