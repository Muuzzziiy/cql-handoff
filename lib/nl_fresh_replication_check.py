"""Independent check of experiments/2026-10-17-nl-fresh-replication (does not import the runner): exclusion, rescue set, donors, R1, R2."""
import json
from pathlib import Path
import numpy as np
E = Path(__file__).resolve().parents[1] / 'experiments'
OUT = E / '2026-10-17-nl-fresh-replication'

def lines(p):
    return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]

def ok(j):
    s = np.asarray(j['scores'])
    return int(np.argmax(s)) == 0

def main():
    S = json.loads((OUT / 'SUMMARY.json').read_text())
    items = json.loads((OUT / 'INPUTS.json').read_text(encoding='utf-8'))['items']
    ch = {}
    old = json.loads((E / '2026-10-12-ouro26-natural-rescue-fc-powered/INPUTS.json').read_text(encoding='utf-8'))['items']
    chat = json.loads((E.parent / 'data/runtime/natural_history.json').read_text(encoding='utf-8'))
    prior_ids = {it['source_id'] for it in old} | {r['source_id'] for v in chat.values() for r in v}
    prior_ev = {r['evidence_key'] for v in chat.values() for r in v}
    prior_qa = {k for v in chat.values() for r in v for k in r['qa_keys']}
    prior_hop = {h for v in chat.values() for r in v for h in r['hop_ids']}
    ch['exclusion'] = all((it['source_id'] not in prior_ids and it['evidence_key'] not in prior_ev and (not set(it['qa_keys']) & prior_qa) and (not set(it['hop_ids']) & prior_hop) for it in items)) and len({it['source_id'] for it in items}) == len(items)
    ch['candidates'] = all((len({c.casefold() for c in it['candidates']}) == 4 for it in items))
    scr = {r['key']: r for r in lines(OUT / 'SCREEN.jsonl')}
    ch['screen_all'] = len(scr) == len(items)
    T = sorted((k for k, r in scr.items() if not ok(r['two_hop']['1']) and ok(r['two_hop']['3'])))
    R = lines(OUT / 'ROWS.jsonl')
    ch['rescue_set'] = sorted((r['key'] for r in R)) == T and S['targets'] == len(T)
    ch['donors'] = sorted((r['donor'] for r in R)) == T and all((r['donor'] != r['key'] for r in R))
    ch['rescored'] = all((ok(r[a]) == r[a]['correct'] for r in R for a in ('arm1', 'arm2', 'arm3', 'arm4')))
    mine = {}
    for nm, a, b in (('R1', 'arm1', 'arm2'), ('R2', 'arm3', 'arm4')):
        d = np.array([ok(r[a]) - ok(r[b]) for r in R], float)
        ix = np.random.default_rng(20261013303).integers(0, len(d), (20000, len(d)))
        i = (100 * np.quantile(d[ix].mean(1), (0.0125, 0.9875))).tolist()
        mine[nm] = (100 * float(d.mean()), i)
        ch[nm] = abs(mine[nm][0] - S[nm]['mean_pp']) < 1e-09 and np.allclose(i, S[nm]['ci_bonf2']) and ((i[0] > 0) == S[nm]['supported'])
    ch['identity'] = all((v['same_choice'] and v['identity_max_abs_score_diff'] < 0.02 for v in lines(OUT / 'VALIDATION.jsonl')))
    ch = {k: bool(v) for k, v in ch.items()}
    out = dict(status='PASS' if all(ch.values()) else 'FAIL', checks=ch, recomputed=mine, targets=len(T))
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
if __name__ == '__main__':
    main()
