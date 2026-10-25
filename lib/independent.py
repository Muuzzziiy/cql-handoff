"""CPU checks of public records. This module does not import inference runners."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODELS=('ouro14','ouro26')
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def rows(path): return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]
def close(a,b): assert np.allclose(a,b,atol=1e-8,rtol=0),(a,b)
def score(value,gold):
    logits=np.array(value.get('candidate_logits',value.get('scores')),float)
    result=int(np.argmax(logits))==gold
    assert bool(value['correct'])==result
    close(logits[gold]-np.delete(logits,gold).max(),value['margin'])
    return int(result)
def interval(values,seed,quantiles=(.025,.975)):
    values=np.asarray(values,float); indices=np.random.default_rng(seed).integers(0,len(values),(20000,len(values)))
    return np.quantile(values[indices].mean(1),quantiles)
def report(out,checks):
    result=dict(status='PASS',checks=checks)
    (out/'INDEPENDENT_CHECK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2)); return result

def scope(out,seed):
    summary=read(out/'SUMMARY.json'); inputs=read(out/'INPUTS.json')
    for model in MODELS:
        gates=rows(out/f'{model}_GATE.jsonl'); rescued=rows(out/f'{model}_RESCUE.jsonl')
        for variant,scenes in inputs.items():
            expected=summary[f'{model}/{variant}']; by={s['graph']:s['cases'] for s in scenes}
            g=[r for r in gates if r['variant']==variant]
            assert len(g)==len(scenes) and len({r['graph'] for r in g})==len(g)
            a=lambda q,l,group:np.array([score(r[q][f'loop{l}'],by[r['graph']][q]['answer_index']) for r in group],float)
            # All stored native decisions, including negative gate cells, are rescored.
            for q in ('q2','q1a','q1b'):
                for loop in range(1,5): a(q,loop,g)
            star=[r for r in g if all(score(r[q][f'loop{l}'],by[r['graph']][q]['answer_index']) for q in ('q1a','q1b') for l in range(1,5))]
            gain=a('q2',3,star)-a('q2',1,star)
            comp=a('q2',3,g)-a('q2',1,g)-np.maximum(a('q1a',3,g)-a('q1a',1,g),a('q1b',3,g)-a('q1b',1,g))
            assert len(star)==expected['gate']['s_star']
            close(100*comp.mean(),expected['gate']['G_comp_pp'])
            if len(star):
                close(100*gain.mean(),expected['gate']['gain_s_star_pp']); close(100*interval(gain,seed),expected['gate']['gain_ci'])
            assert bool(len(star) and 100*gain.mean()>=15 and interval(gain,seed)[0]>0 and comp.mean()>0)==expected['gate']['pass']
            r=[x for x in rescued if x['variant']==variant]; paired=[x for x in r if 'donor' in x]
            assert len(r)==expected['rescue']['targets']
            answers={c['case_id']:c['answer_index'] for s in scenes for c in s['cases'].values()}
            for row in r:
                gold=answers[row['case_id']]
                assert not score(row['native1'],gold) and score(row['native3'],gold)
                for arm in ('all','all_shuffled'):
                    if arm in row: score(row[arm],gold)
            if len(paired)>=2:
                delta=np.array([score(x['all'],answers[x['case_id']])-score(x['all_shuffled'],answers[x['case_id']]) for x in paired],float)
                close(100*delta.mean(),expected['rescue']['delta_all']['mean_pp'])
                close(100*interval(delta,seed),expected['rescue']['delta_all']['ci95_pp'])
    return report(out,dict(native_logits=True,gate_including_failures=True,all_head_targets=True,paired_delta_and_ci=True))

def controls(out):
    summary=read(out/'SUMMARY.json'); inputs=read(out/'INPUTS.json')
    for model in MODELS:
        answer={c['case_id']:c['answer_index'] for c in inputs[model]}
        records=rows(out/f'{model}_B_ROWS.jsonl')
        for record in records:
            for arm in ('Native','V_F','KV_F','KV_mem'):
                for loop in range(1,5): score(record[arm][f'loop{loop}'],answer[record['case_id']])
        acc=lambda arm,loop:np.array([score(r[arm][f'loop{loop}'],answer[r['case_id']]) for r in records],float)
        gain=acc('Native',3)-acc('Native',1); idx=np.random.default_rng(20261012905).integers(0,len(records),(20000,len(records)))
        delta={arm:acc(arm,3)-acc(arm,1) for arm in ('V_F','KV_F','KV_mem')}
        for arm,value in delta.items():
            close(value.mean()/gain.mean(),summary[model]['B'][arm]['rho'])
            close(np.quantile(value[idx].mean(1)/gain[idx].mean(1),[.025,.975]),summary[model]['B'][arm]['ci95'])
        contrast=(delta['KV_F'][idx].mean(1)-delta['V_F'][idx].mean(1))/gain[idx].mean(1)
        close(np.quantile(contrast,[.0125,.9875]),summary[model]['B']['primary_KV_F_minus_V_F']['ci_family'])
        rescue=rows(out/f'{model}_A1_ROWS.jsonl')
        target={r['case_id'] for r in records if not r['Native']['loop1']['correct'] and r['Native']['loop3']['correct']}
        assert target=={r['case_id'] for r in rescue}
        close(np.mean([score(r['all'],answer[r['case_id']]) for r in rescue]),summary[model]['A1']['all'])
    return report(out,dict(raw_logits=True,cofreeze_means_and_ci=True,all_head_replication=True))

def crossed(out):
    summary=read(out/'SUMMARY.json'); inputs=read(out/'INPUTS.json'); colors=('red','blue','green','yellow')
    for model in MODELS:
        scenes={s['graph']:s for s in inputs['scenes'][model]}; records=rows(out/f'{model}_E1_ROWS.jsonl')
        for row in records:
            recipient=scenes[row['graph']]; donor=scenes[row['donor']]; offset=donor['box_order'].index(donor['box'])
            expected=dict(recipient_composition=recipient['color'],donor_bridge=recipient['colors'][donor['box']],donor_answer=donor['color'],donor_line=recipient['colors'][recipient['box_order'][offset]])
            assert row['predictions']==expected and len(set(expected.values()))==4
            for arm in ('r1_all','r3_all'): assert row[arm]['pred']==colors[int(np.argmax(row[arm]['logits']))]
        for arm in ('r1_all','r3_all'):
            for outcome in ('recipient_composition','donor_bridge','donor_answer','donor_line'):
                v=np.array([r[arm]['pred']==r['predictions'][outcome] for r in records],float)
                close(v.mean(),summary[model]['E1'][arm][outcome]['rate'])
                close(interval(v,20261013003),summary[model]['E1'][arm][outcome]['ci95'])
    return report(out,dict(donor_predictions_reconstructed=True,all_head_choices=True,rates_and_ci=True))

def replication(out):
    inp={s['graph']:s['host'] for s in read(out/'INPUTS.json')}; records=rows(out/'ROWS.jsonl'); summary=read(out/'SUMMARY.json')
    assert len(records)==len(inp)==summary['scenes']
    target=set()
    for row in records:
        gold=inp[row['graph']]['answer_index']; n1=score(row['host']['loop1'],gold); n3=score(row['host']['loop3'],gold)
        if not n1 and n3: target.add(row['graph']); assert 'rescue_all' in row; score(row['rescue_all'],gold)
        else: assert 'rescue_all' not in row
    close(np.mean([r['rescue_all']['correct'] for r in records if r['graph'] in target]),summary['rescue']['rescue_all'])
    assert len(target)==summary['rescue']['targets']
    return report(out,dict(native_and_rescue_logits=True,targets_complete=True,all_head_rate=True))

def nl_boundary(out):
    summary=read(out/'SUMMARY.json')['ouro14']; screen=rows(out/'ouro14_SCREEN.jsonl'); records=rows(out/'ouro14_ROWS.jsonl')
    target={r['key'] for r in screen if not score(r['two_hop']['1'],0) and score(r['two_hop']['3'],0)}
    assert target=={r['key'] for r in records}=={r['donor'] for r in records}
    assert all(r['key']!=r['donor'] for r in records)
    gain=np.array([score(r['two_hop']['3'],0)-score(r['two_hop']['1'],0) for r in screen],float)
    close(100*gain.mean(),summary['gate_pp']); close(100*interval(gain,20261017503),summary['gate_ci95'])
    delta=np.array([score(r['all'],0)-score(r['all_shuf'],0) for r in records],float)
    close(100*delta.mean(),summary['B1']['mean_pp']); close(100*interval(delta,20261017503),summary['B1']['ci95'])
    for arm in ('all','all_shuf'): close(100*np.mean([score(r[arm],0) for r in records]),summary['rescue'][arm])
    return report(out,dict(native_loop_gain=True,target_and_donor_sets=True,rescue_null_with_ci=True))

def converse(out):
    summary=read(out/'SUMMARY.json'); inputs=read(out/'INPUTS.json')
    for model in MODELS:
        answer={c['case_id']:c['answer_index'] for c in inputs[model]}; records=rows(out/f'{model}_ROWS.jsonl')
        for row in records:
            for value in row.values():
                if isinstance(value,dict) and 'candidate_logits' in value: score(value,answer[row['case_id']])
            assert not row['native1']['correct'] and row['native3']['correct']
        delta=[r['Q_late']['correct']-r['KV_late_F']['correct'] for r in records]
        close(100*np.mean(delta),summary[model]['primary_Q_minus_KV_F']['mean_pp'])
        close(100*interval(delta,20261013704,(.0125,.9875)),summary[model]['primary_Q_minus_KV_F']['ci_bonf2_pp'])
    return report(out,dict(logits_rescored=True,targets=True,primary_mean_and_ci=True))

def audit(out):
    inputs={c['case_id']:c for c in read(out/'FRESH_INPUTS.json')['cases']}; records=rows(out/'ouro26_FRESH_ROWS.jsonl'); screen=rows(out/'ouro26_FRESH_SCREEN.jsonl')
    for row in screen:
        for loop in ('loop1','loop3'): score(row[loop],inputs[row['case_id']]['answer_index'])
    target={r['case_id'] for r in screen if not r['loop1']['correct'] and r['loop3']['correct']}
    assert target=={r['case_id'] for r in records}
    for row in records:
        for arm in ('same','shuffled'): score(row[arm],inputs[row['case_id']]['answer_index'])
    result=read(out/'SUMMARY.json')['ouro26_fresh']; delta=[r['same']['correct']-r['shuffled']['correct'] for r in records]
    close(100*np.mean(delta),result['delta_pp']); close(100*interval(delta,20261012803),result['delta_ci95_pp'])
    for model in MODELS:
        isolation=read(out/f'{model}_ISOLATION.json')
        assert len(isolation)==4 and all(r['other_positions_identical_all_layers'] and r['q_K_V_identical_layer0'] for r in isolation)
    return report(out,dict(fresh_targets_and_logits=True,fresh_delta_and_ci=True,saved_isolation_checks=True))
