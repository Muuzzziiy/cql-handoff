"""Native gate and all-head rescue beyond the base template."""
import argparse, json, os, time
import numpy as np
import torch
from .common import ROOT, read, write, append, now, MODELS
from . import ouro_advisor_stagecd as A
from . import patching as L
OUT = ROOT / 'experiments/2026-10-15-ouro-entity-scale'
HEADS = 16
BOOT = 20261015302
DONOR_SEED = 20261015303
VARIANTS = ['E8', 'E16']

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
    started = time.perf_counter()
    for vname, scenes in read(OUT / 'INPUTS.json').items():
        for s in scenes:
            row = dict(variant=vname, graph=s['graph'])
            for q, c in s['cases'].items():
                v = A.all_loops(model, c, (), seed)
                row[q] = {f'loop{l + 1}': A.score(v[l], c) for l in range(4)}
            append(OUT / f'{name}_GATE.jsonl', row)
        cases = [s['cases']['q2'] for s in scenes]
        scr = {}
        for c in cases:
            scr[c['case_id']] = {r: A.score(L.stopped(model, c, r, seed)[0], c) for r in (1, 3)}
        targets = [c for c in cases if not scr[c['case_id']][1]['correct'] and scr[c['case_id']][3]['correct']]
        rng = np.random.default_rng(DONOR_SEED)
        donor = {}
        for Ln in sorted({len(c['ids']) for c in targets}):
            grp = [c for c in targets if len(c['ids']) == Ln]
            if len(grp) < 2:
                continue
            while True:
                perm = rng.permutation(len(grp))
                if all((perm[i] != i for i in range(len(grp)))):
                    break
            donor.update({grp[i]['case_id']: grp[perm[i]] for i in range(len(grp))})
        D = model.config.hidden_size // model.config.num_attention_heads

        def qrow(c):
            cap = L.stopped(model, c, 3, seed, capture_loop=3)[1]
            return {l: cap[l]['Q'][:, :, -1, :].clone() for l in cap}
        late = {c['case_id']: qrow(c) for c in targets}

        def src_of(c, rows):
            n = len(c['ids'])
            out = {}
            for l, v in rows.items():
                t = torch.zeros(1, HEADS, n, D, dtype=v.dtype, device=v.device)
                t[:, :, n - 1, :] = v
                out[l] = {'Q': t}
            return out

        def patch(c, layers, heads, rows):
            return A.score(L.stopped(model, c, 1, seed, (('Q', 'q', layers, heads),), (1,), src_of(c, rows))[0], c)
        for i, c in enumerate(targets):
            k = c['case_id']
            row = dict(variant=vname, case_id=k, native1=scr[k][1], native3=scr[k][3], all=patch(c, allL, allH, late[k]))
            if k in donor:
                d = donor[k]['case_id']
                row['donor'] = d
                row['all_shuffled'] = patch(c, allL, allH, late[d])
            if i < 2:
                full = L.stopped(model, c, 3, seed, capture_loop=3)[1]
                old = A.stopped(model, c, 1, seed, (('Q', 'q'),), (1,), full)[0]
                del full
                assert np.array_equal(old, L.stopped(model, c, 1, seed, (('Q', 'q', allL, allH),), (1,), src_of(c, late[k]))[0])
                append(OUT / f'{name}_VALIDATION.jsonl', dict(case_id=k, all_heads_equals_stage_d=True))
            append(OUT / f'{name}_RESCUE.jsonl', row)
        del late
        print(dict(model=name, variant=vname, targets=len(targets), seconds=round(time.perf_counter() - started)), flush=True)
    write(OUT / f'{name}_RUN.json', dict(status='COMPLETE', seconds=time.perf_counter() - started))

def ci(x, seed=BOOT):
    x = np.asarray(x, float)
    ix = np.random.default_rng(seed).integers(0, len(x), (20000, len(x)))
    return (100 * np.quantile(x[ix].mean(1), [0.025, 0.975])).tolist()

def analyze():
    res = {}
    for m in A.MODELS:
        G = [json.loads(x) for x in (OUT / f'{m}_GATE.jsonl').read_text().splitlines() if x.strip()]
        RS = [json.loads(x) for x in (OUT / f'{m}_RESCUE.jsonl').read_text().splitlines() if x.strip()]
        for vname in VARIANTS:
            g = [r for r in G if r['variant'] == vname]
            acc = lambda q, l, rr: np.array([r[q][f'loop{l}']['correct'] for r in rr], float)
            star = [r for r in g if all((r[q][f'loop{l}']['correct'] for q in ('q1a', 'q1b') for l in range(1, 5)))]
            gain = acc('q2', 3, star) - acc('q2', 1, star)
            gfull = acc('q2', 3, g) - acc('q2', 1, g)
            g1 = np.maximum(acc('q1a', 3, g) - acc('q1a', 1, g), acc('q1b', 3, g) - acc('q1b', 1, g))
            gate = dict(n=len(g), s_star=len(star), gain_s_star_pp=100 * float(gain.mean()) if len(star) else None, gain_ci=ci(gain) if len(star) else None, G_comp_pp=100 * float((gfull - g1).mean()), G_comp_ci=ci(gfull - g1), acc_q2={l: float(acc('q2', l, g).mean()) for l in range(1, 5)}, acc_q1a_l1=float(acc('q1a', 1, g).mean()), acc_q1b_l1=float(acc('q1b', 1, g).mean()))
            gate['pass'] = bool(len(star) and gate['gain_s_star_pp'] >= 15 and (gate['gain_ci'][0] > 0) and (gate['G_comp_pp'] > 0))
            r = [x for x in RS if x['variant'] == vname]
            p = [x for x in r if 'donor' in x]

            def diff(a, b, rows):
                return np.array([x[a]['correct'] - x[b]['correct'] for x in rows], float)
            resc = dict(targets=len(r), paired=len(p), rescue={k: float(np.mean([x[k]['correct'] for x in (p if 'shuffled' in k else r)])) if r else None for k in ('all', 'all_shuffled')})
            if len(p) >= 2:
                for name_, (a, b, rows) in dict(delta_all=('all', 'all_shuffled', p)).items():
                    d = diff(a, b, rows)
                    resc[name_] = dict(mean_pp=100 * float(d.mean()), ci95_pp=ci(d))
                resc['rescue_pass'] = resc['delta_all']['ci95_pp'][0] > 0
            resc['descriptive_only'] = len(p) < 40
            res[f'{m}/{vname}'] = dict(gate=gate, rescue=resc)
    write(OUT / 'SUMMARY.json', res)
    for k, v in res.items():
        g, r = (v['gate'], v['rescue'])
        print(k, 'gate', g['pass'], 'S*', g['s_star'], 'gain', None if g['gain_s_star_pp'] is None else round(g['gain_s_star_pp'], 1), g['gain_ci'] and [round(x, 1) for x in g['gain_ci']], 'Gcomp', round(g['G_comp_pp'], 1), '| targets', r['targets'], {a: round(b, 3) if b is not None else None for a, b in r['rescue'].items()}, {a: (round(r[a]['mean_pp'], 1), [round(x, 1) for x in r[a]['ci95_pp']]) for a in ('delta_all',) if a in r}, flush=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    parser.add_argument('--model', choices=MODELS)
    args = parser.parse_args()
    if args.action == 'run' and args.model is None:
        parser.error('--model is required')
    analyze() if args.action == 'analyze' else run(args.model)
