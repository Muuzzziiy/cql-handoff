"""Independent check of experiments/2026-10-17-matched-composition-control (does not import the runner): rescoring, equal lengths, M1."""
import json
from pathlib import Path
import numpy as np
OUT = Path(__file__).resolve().parents[1] / 'experiments/2026-10-17-matched-composition-control'
ARMS = ('Native', 'I_Q', 'I_K', 'I_V', 'C_Q', 'C_K', 'C_V')

def main():
    S = json.loads((OUT / 'SUMMARY.json').read_text())
    inp = json.loads((OUT / 'INPUTS.json').read_text())
    ch = {}
    mine = {}
    for m in ('ouro14', 'ouro26'):
        sc = {s['graph']: s for s in inp[m]}
        ch[f'{m}_lengths'] = all((len(s['T']['ids']) == len(s['G']['ids']) and s['T']['answer_index'] == s['G']['answer_index'] for s in inp[m]))
        R = [json.loads(l) for l in (OUT / f'{m}_ROWS.jsonl').read_text().splitlines() if l.strip()]
        acc = {}
        for r in R:
            c = sc[r['graph']][r['question']]
            for l in range(1, 5):
                if (int(np.argmax(r[f'loop{l}']['candidate_logits'])) == c['answer_index']) != r[f'loop{l}']['correct']:
                    ch[f'{m}_rescore'] = False
            acc[r['graph'], r['question'], r['arm']] = int(np.argmax(r['loop3']['candidate_logits'])) == c['answer_index']
        ch.setdefault(f'{m}_rescore', True)
        ch[f'{m}_complete'] = len(acc) == 400 * 2 * len(ARMS)
        d = np.array([acc[g, 'T', 'Native'] - acc[g, 'T', 'I_Q'] - (acc[g, 'G', 'Native'] - acc[g, 'G', 'I_Q']) for g in sorted(sc)], float)
        ix = np.random.default_rng(20261017801).integers(0, len(d), (20000, len(d)))
        i = (100 * np.quantile(d[ix].mean(1), (0.0125, 0.9875))).tolist()
        mine[m] = dict(M1=100 * float(d.mean()), ci=i)
        ch[f'{m}_M1'] = abs(100 * d.mean() - S[m]['M1']['mean_pp']) < 1e-09 and np.allclose(i, S[m]['M1']['ci_bonf2']) and ((i[0] > 0) == S[m]['M1']['supported'])
        ch[f'{m}_identity'] = all((json.loads(l)['exact'] for l in (OUT / f'{m}_VALIDATION.jsonl').read_text().splitlines() if l.strip()))
    ch = {k: bool(v) for k, v in ch.items()}
    out = dict(status='PASS' if all(ch.values()) else 'FAIL', checks=ch, recomputed=mine)
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
if __name__ == '__main__':
    main()
