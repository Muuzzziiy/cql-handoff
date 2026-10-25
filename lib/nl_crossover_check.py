"""Independent check of experiments/2026-10-17-nl-crossover (does not import the runner): pairs, edits, gates, X1/X2."""
import json
from pathlib import Path
import numpy as np
from .natural_data import normalize, canonical
E = Path(__file__).resolve().parents[1] / 'experiments'
OUT = E / '2026-10-17-nl-crossover'
RUN3 = E / '2026-10-12-ouro26-natural-rescue-fc-powered'
SRC = E.parent / 'data/sources'

def lines(p):
    return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]

def main():
    inp = json.loads((OUT / 'INPUTS.json').read_text(encoding='utf-8'))
    P = inp['pairs']
    S = json.loads((OUT / 'SUMMARY.json').read_text())
    items = {f"{it['dataset']}_{it['item_index']}": it for it in json.loads((RUN3 / 'INPUTS.json').read_text(encoding='utf-8'))['items']}
    need = {items[k]['source_id'] for p in P for k in (p['recipient'], p['donor'])}
    rec = {}
    raw2 = json.loads((SRC / '2wiki_dev.json').read_text(encoding='utf-8'))
    for i, row in enumerate(raw2):
        if row.get('_id') in need:
            rec[row['_id']] = normalize('2wiki', row, i)[0]
    for i, x in enumerate((SRC / 'musique_ans_v1.0_train.jsonl').read_text(encoding='utf-8').splitlines()):
        row = json.loads(x)
        if row['id'] in need:
            rec[row['id']] = normalize('musique', row, i)[0]
    ch = dict(recipient_once=len({p['recipient'] for p in P}) == len(P))
    bad = []
    for p in P:
        r, d = (items[p['recipient']], items[p['donor']])
        R, D = (rec[r['source_id']], rec[d['source_id']])
        P2 = next((x for x in D['paragraphs'] if x['hop'] == 2))
        txt = p['prompt'].casefold()
        c = [canonical(x) for x in p['candidates']]
        ok = r['dataset'] == d['dataset'] and r['type'] == d['type'] and (p['recipient'] != p['donor']) and (p['A_r'] == r['candidates'][0]) and (p['A_d'] == d['candidates'][0]) and (len(set(c)) == 4) and ((P2['title'] + '\n' + P2['text']).count(p['A_d']) == 1) and (p['P_d2_edited']['text'] == P2['text'].replace(p['A_d'], p['A_d2'])) and (p['A_d'].casefold() not in txt) and (p['A_d2'].casefold() in txt) and (p['X'].casefold() not in (p['P_d2_edited']['title'] + '\n' + p['P_d2_edited']['text']).casefold()) and (p['A_d2'].casefold() not in '\n'.join((x['title'] + '\n' + x['text'] for x in R['paragraphs'] + D['paragraphs'])).casefold()) and (items[p['unrelated']]['type'] == r['type']) and (p['unrelated'] not in (p['recipient'], p['donor']))
        if not ok:
            bad.append(p['pair_id'])
    ch['pairs_and_edits'] = not bad
    mine = {}
    for m in ('ouro26',):
        if not (OUT / f'{m}_ROWS.jsonl').exists():
            continue
        R_ = lines(OUT / f'{m}_ROWS.jsonl')
        dscr = {r['key']: r['two_hop']['3']['correct'] for r in lines(RUN3 / 'ouro26_SCREEN.jsonl')}
        byp = {p['pair_id']: p for p in P}
        top = lambda j: int(np.argmax(j['scores']))
        gate = all((r['gated'] == (top(r['native3']) == 0 and bool(dscr[byp[r['pair_id']]['donor']])) for r in R_))
        G = [r for r in R_ if r['gated']]
        ch[f'{m}_gate'] = gate and len(G) == S[m]['gated'] and (len(R_) == len(P))
        ind = lambda a, i: np.array([top(r[a]) == i for r in G], float)
        q = (0.0125, 0.9875) if m == 'ouro26' else (0.025, 0.975)
        g = {}
        for nm, x, y in (('X1', ind('arm1', 1), ind('arm2', 1)), ('X2', ind('arm1', 1), ind('arm1', 2))):
            dd = x - y
            ix = np.random.default_rng(20261013303).integers(0, len(dd), (20000, len(dd)))
            i = (100 * np.quantile(dd[ix].mean(1), q)).tolist()
            g[nm] = (100 * float(dd.mean()), i)
            ch[f'{m}_{nm}'] = abs(g[nm][0] - S[m][nm]['mean_pp']) < 1e-09 and np.allclose(i, S[m][nm]['ci'])
        ch[f'{m}_identity'] = (lambda V: len(V) == 20 and all((v['ok'] and v['same_top'] and (v['max_abs'] < 0.05) for v in V)))(lines(OUT / f'{m}_VALIDATION.jsonl'))
        mine[m] = dict(gated=len(G), **g)
    ch = {k: bool(v) for k, v in ch.items()}
    out = dict(status='PASS' if all(ch.values()) else 'FAIL', checks=ch, bad_pairs=bad[:20], recomputed=mine)
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
if __name__ == '__main__':
    main()
