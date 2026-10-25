"""Late-query versus late-key/value rescue reported in section 6.1."""
import argparse, json, os, time
import numpy as np
import torch
from .common import ROOT, read, write, append, now, MODELS
from . import ouro_advisor_stagecd as A
from . import patching as L
OUT = ROOT / 'experiments/2026-10-12-ouro-converse-kv'
HEADS = 16
DONOR_SEED = 20261013703
BOOT = 20261013704

def fwd(model, c, depth, seed, spec=(), loops=(), source=None, capture_loop=None):
    vector, captured = L.stopped(model, c, depth, seed, spec, loops, source, capture_loop)
    return (vector, captured, None)

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
    cases = read(OUT / 'INPUTS.json')[name]
    started = time.perf_counter()
    scr = {}
    for c in cases:
        scr[c['case_id']] = {r: A.score(fwd(model, c, r, seed)[0], c) for r in (1, 3)}
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
    print(dict(model=name, targets=len(targets), donors=len(donor), seconds=round(time.perf_counter() - started)), flush=True)
    for i, c in enumerate(targets):
        k = c['case_id']
        late = fwd(model, c, 3, seed, capture_loop=3)[1]

        def arm(spec_, src):
            return A.score(fwd(model, c, 1, seed, spec_, (1,), src)[0], c)
        n1v = fwd(model, c, 1, seed)[0]
        row = dict(case_id=k, native1=scr[k][1], native3=scr[k][3], Q_late=arm((('Q', 'q', allL, allH),), late), K_late_F=arm((('K', 'F', allL, allH),), late), V_late_F=arm((('V', 'F', allL, allH),), late), KV_late_F=arm((('K', 'F', allL, allH), ('V', 'F', allL, allH)), late), KV_late_mem=arm((('K', 'mem', allL, allH), ('V', 'mem', allL, allH)), late))
        if k in donor:
            dl = fwd(model, donor[k], 3, seed, capture_loop=3)[1]
            row['donor'] = donor[k]['case_id']
            row['KV_late_F_donor'] = arm((('K', 'F', allL, allH), ('V', 'F', allL, allH)), dl)
            row['Q_late_donor'] = arm((('Q', 'q', allL, allH),), dl)
            del dl
        if i < 2:
            own = fwd(model, c, 1, seed, capture_loop=1)[1]
            ident = fwd(model, c, 1, seed, (('Q', 'q', allL, allH), ('K', 'mem', allL, allH), ('V', 'mem', allL, allH)), (1,), own)[0]
            sd = A.stopped(model, c, 1, seed, (('Q', 'q'),), (1,), late)[0]
            ok = bool(np.array_equal(ident, n1v)) and bool(np.array_equal(sd, fwd(model, c, 1, seed, (('Q', 'q', allL, allH),), (1,), late)[0]))
            append(OUT / f'{name}_VALIDATION.jsonl', dict(case_id=k, identity_exact=bool(np.array_equal(ident, n1v)), q_late_equals_stage_d=ok))
            assert ok
        append(OUT / f'{name}_ROWS.jsonl', row)
        del late
        if i % 50 == 0:
            print(dict(model=name, target=i, seconds=round(time.perf_counter() - started)), flush=True)
    write(OUT / f'{name}_RUN.json', dict(status='COMPLETE', targets=len(targets), seconds=time.perf_counter() - started))

def analyze():
    res = {}
    arms = ('Q_late', 'K_late_F', 'V_late_F', 'KV_late_F', 'KV_late_mem', 'KV_late_F_donor', 'Q_late_donor')
    for m in A.MODELS:
        R = [json.loads(x) for x in (OUT / f'{m}_ROWS.jsonl').read_text().splitlines() if x.strip()]
        n = len(R)
        ix = np.random.default_rng(BOOT).integers(0, n, (20000, n))
        d = np.array([x['Q_late']['correct'] - x['KV_late_F']['correct'] for x in R], float)
        prim = dict(mean_pp=100 * float(d.mean()), ci_bonf2_pp=(100 * np.quantile(d[ix].mean(1), [0.0125, 0.9875])).tolist())
        prim['supported'] = prim['ci_bonf2_pp'][0] > 0
        rates = {a: dict(rescue=float(np.mean([x[a]['correct'] for x in R if a in x])), n=sum((a in x for x in R)), margin=float(np.mean([x[a]['margin'] for x in R if a in x]))) for a in arms}
        rates['native1'] = dict(margin=float(np.mean([x['native1']['margin'] for x in R])))
        rates['native3'] = dict(margin=float(np.mean([x['native3']['margin'] for x in R])))
        p = [x for x in R if 'KV_late_F_donor' in x]
        dd = np.array([x['KV_late_F']['correct'] - x['KV_late_F_donor']['correct'] for x in p], float)
        jx = np.random.default_rng(BOOT).integers(0, len(dd), (20000, len(dd)))
        res[m] = dict(targets=n, primary_Q_minus_KV_F=prim, rates=rates, KV_F_minus_donor=dict(mean_pp=100 * float(dd.mean()), ci95_pp=(100 * np.quantile(dd[jx].mean(1), [0.025, 0.975])).tolist()))
    write(OUT / 'SUMMARY.json', res)
    print(json.dumps(res, indent=1), flush=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('run', 'analyze'))
    parser.add_argument('--model', choices=MODELS)
    args = parser.parse_args()
    if args.action == 'run' and args.model is None:
        parser.error('--model is required')
    analyze() if args.action == 'analyze' else run(args.model)
