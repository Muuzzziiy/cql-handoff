"""Independent Stage C/D logits, selections, means and interval reconstruction."""
import json
import numpy as np
from .common import ROOT
E=ROOT/'experiments'
MODELS=('ouro14','ouro26')
stats={'candidate_scores_validated':0,'stage_c':{},'stage_d':{}}

def read(p): return json.loads(p.read_text(encoding='utf-8'))

def lines(p): return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]

def same(a,b): assert np.allclose(a,b,rtol=0,atol=1e-8), (a,b)

def ci(values,seed,quantiles=(.025,.975)):
    values = np.asarray(values,dtype=float)
    indices = np.random.default_rng(seed).integers(len(values),size=(20000,len(values)))
    return np.quantile(values[indices].mean(axis=1),quantiles)

def correct(score,gold):
    values = np.asarray(score.get('candidate_logits',score.get('scores')),dtype=float)
    actual = int(np.argmax(values)) == gold
    assert actual == score['correct'], (actual,score)
    same(values[gold]-max(np.delete(values,gold)),score['margin'])
    stats['candidate_scores_validated'] += 1
    return int(actual)

def validate_scores(obj,gold):
    if isinstance(obj,dict):
        if 'candidate_logits' in obj or 'scores' in obj:
            return correct(obj,gold)
        for value in obj.values(): validate_scores(value,gold)
    elif isinstance(obj,list):
        for value in obj: validate_scores(value,gold)

def main():
    p = E/'2026-10-12-ouro-advisor-stagecd'
    inp, cfg, summary = [read(p/name) for name in ('INPUTS.json','CONFIG.json','SUMMARY.json')]
    for m in MODELS:
        answers = {c['case_id']: c['answer_index'] for c in inp[m]['stage_c']}
        rows = lines(p/f'{m}_C_ROWS.jsonl')
        for row in rows: validate_scores(row,answers[row['case_id']])
        by = {(r['graph'],r['query'],r['arm']):r for r in rows}
        graphs = sorted({r['graph'] for r in rows})
        def values(q,arm,loop): return np.array([correct(by[g,q,arm][f'loop{loop}'],answers[by[g,q,arm]['case_id']]) for g in graphs],dtype=float)
        native = {q:{l:values(q,'Native',l) for l in range(1,5)} for q in ('q2','q1a','q1b')}
        star = np.logical_and.reduce([native[q][l].astype(bool) for q in ('q1a','q1b') for l in range(1,5)])
        assert int(star.sum()) == summary[m]['S_star_n']
        output = {}
        for subset,mask,seed in (('full',np.ones(len(graphs),bool),cfg['bootstrap_seed']),('S_star',star,cfg['bootstrap_seed']+1)):
            n = int(mask.sum()); indices = np.random.default_rng(seed).integers(n,size=(20000,n))
            gain = (native['q2'][3]-native['q2'][1])[mask]
            expected = summary[m][subset]
            same(100*gain.mean(),expected['two_hop_gain_pp']['mean'])
            same(100*np.quantile(gain[indices].mean(1),(.025,.975)),expected['two_hop_gain_pp']['ci95'])
            comp = gain-np.maximum((native['q1a'][3]-native['q1a'][1])[mask],(native['q1b'][3]-native['q1b'][1])[mask])
            same(100*comp.mean(),expected['G_comp_pp']['mean'])
            for arm in ('I_Q','I_K','I_V','C_Q','C_K','C_V'):
                changed = (values('q2',arm,3)-values('q2',arm,1))[mask]
                loss2 = (native['q2'][3]-values('q2',arm,3))[mask]
                loss1a = (native['q1a'][3]-values('q1a',arm,3))[mask]
                loss1b = (native['q1b'][3]-values('q1b',arm,3))[mask]
                rho = changed.mean()/(gain.mean()+1e-9)
                scd = 100*(loss2.mean()-max(loss1a.mean(),loss1b.mean()))
                rho_ci = np.quantile(changed[indices].mean(1)/(gain[indices].mean(1)+1e-9),(.025,.975))
                loss_boot = np.maximum(loss1a[indices].mean(1),loss1b[indices].mean(1))
                scd_ci = 100*np.quantile(loss2[indices].mean(1)-loss_boot,(.025,.975))
                expected_arm = expected[arm]
                for a,b in ((rho,expected_arm['rho']),(scd,expected_arm['SCD_pp']),(rho_ci,expected_arm['rho_ci95']),(scd_ci,expected_arm['SCD_ci95'])): same(a,b)
                if subset == 'full': output[arm] = {'rho':rho,'SCD_pp':scd,'rho_ci95':rho_ci.tolist(),'SCD_ci95':scd_ci.tolist()}
        stats['stage_c'][m] = {'native_two_hop':{str(l):100*v.mean() for l,v in native['q2'].items()},'S_star_n':int(star.sum()),'freezes':output}
        answers = {c['case_id']:c['answer_index'] for c in inp[m]['stage_d']}
        screen = lines(p/f'{m}_D_SCREEN.jsonl'); rescue = lines(p/f'{m}_D_ROWS.jsonl')
        for row in screen+rescue: validate_scores(row,answers[row['case_id']])
        stats['stage_d'][m] = {}
        for loop in (1,2):
            targets = {r['case_id'] for r in screen if not correct(r[f'loop{loop}'],answers[r['case_id']]) and correct(r['loop3'],answers[r['case_id']])}
            rows = [r for r in rescue if r['r']==loop]
            assert targets == {r['case_id'] for r in rows}
            hit = np.array([correct(r['same'],answers[r['case_id']]) for r in rows],float)
            donor = np.array([correct(r['shuffled'],answers[r['case_id']]) for r in rows],float)
            expected = summary[m]['stage_d'][f'r{loop}']
            result = {'n':len(rows),'same_pct':100*hit.mean(),'shuffled_pct':100*donor.mean(),'delta_pp':100*(hit-donor).mean(),'ci95':(100*ci(hit-donor,cfg['bootstrap_seed'])).tolist(),'ci_bonf4':(100*ci(hit-donor,cfg['bootstrap_seed'],(.025/4,1-.025/4))).tolist()}
            same(result['same_pct'],100*expected['rescue_same']); same(result['shuffled_pct'],100*expected['rescue_shuffled']); same(result['ci95'],expected['delta_ci95_pp']); same(result['ci_bonf4'],expected['delta_bonferroni4_pp'])
            stats['stage_d'][m][f'r{loop}'] = result


    result=dict(status='PASS',checks=dict(raw_logits=True,stage_c_means_and_ci=True,stage_d_targets_rates_and_ci=True))
    (E/'2026-10-12-ouro-advisor-stagecd/INDEPENDENT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    main()
