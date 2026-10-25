"""Independent check of experiments/2026-10-17-matched-control-per-line (does not import the runner): lengths, masks, rescoring, P1."""
import json
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[1] / 'experiments/2026-10-17-matched-control-per-line'

def main():
    S = json.loads((OUT / 'SUMMARY.json').read_text())
    inp = json.loads((OUT / 'INPUTS.json').read_text())
    cfg = json.loads((OUT / 'CONFIG.json').read_text())
    arms = list(cfg['freezes'])
    ch = {}
    mine = {}
    for m in ('ouro14', 'ouro26'):
        sc = {s['graph']: s for s in inp[m]}
        ch[f'{m}_lengths'] = all((len(s['T']['ids']) == len(s['G']['ids']) for s in inp[m])) and len(sc) == 400
        ch[f'{m}_masks'] = all(([a or b for a, b in zip(s[x]['Fbc_mask'], s[x]['Fpb_mask'])] == s[x]['F_mask'] and (not any((a and b for a, b in zip(s[x]['Fbc_mask'], s[x]['Fpb_mask'])))) for s in inp[m] for x in ('T', 'G')))
        R = [json.loads(l) for l in (OUT / f'{m}_ROWS.jsonl').read_text().splitlines() if l.strip()]
        acc = {}
        bad = 0
        for r in R:
            c = sc[r['graph']][r['question']]
            for l in range(1, 5):
                bad += (int(np.argmax(r[f'loop{l}']['candidate_logits'])) == c['answer_index']) != r[f'loop{l}']['correct']
            acc[r['graph'], r['question'], r['arm']] = float(int(np.argmax(r['loop3']['candidate_logits'])) == c['answer_index'])
        ch[f'{m}_rescore'] = bad == 0
        ch[f'{m}_complete'] = len(acc) == 400 * 2 * len(arms)
        Mv = lambda a: np.array([acc[g, 'T', 'Native'] - acc[g, 'T', a] - (acc[g, 'G', 'Native'] - acc[g, 'G', a]) for g in sorted(sc)])
        d = Mv('I_V_bc') - Mv('I_Q')
        ix = np.random.default_rng(cfg['boot']).integers(0, len(d), (20000, len(d)))
        i = (100 * np.quantile(d[ix].mean(1), (0.0125, 0.9875))).tolist()
        mine[m] = dict(P1=100 * float(d.mean()), ci=i)
        ch[f'{m}_P1'] = abs(100 * d.mean() - S[m]['P1']['mean_pp']) < 1e-09 and np.allclose(i, S[m]['P1']['ci_bonf2'])
        ch[f'{m}_M_rows'] = all((abs(100 * Mv(a).mean() - S[m]['rows'][a]['M']) < 1e-09 for a in arms if a != 'Native'))
        ch[f'{m}_identity'] = all((json.loads(l)['exact'] for l in (OUT / f'{m}_VALIDATION.jsonl').read_text().splitlines() if l.strip()))
    ch = {k: bool(v) for k, v in ch.items()}
    out = dict(status='PASS' if all(ch.values()) else 'FAIL', checks=ch, recomputed=mine)
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
if __name__ == '__main__':
    main()
