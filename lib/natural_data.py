"""Official natural QA normalization for independent item reconstruction."""
import hashlib
import json
import re
RELATIONS = {'mother': 'Who is the mother of {bridge}?', 'father': 'Who is the father of {bridge}?', 'spouse': 'Who is the spouse of {bridge}?', 'child': 'Who is the child of {bridge}?', 'sibling': 'Who is the sibling of {bridge}?', 'place of birth': 'Where was {bridge} born?', 'place of death': 'Where did {bridge} die?', 'date of birth': 'When was {bridge} born?', 'date of death': 'When did {bridge} die?', 'cause of death': 'What was the cause of death of {bridge}?', 'award received': 'What award did {bridge} receive?', 'country of citizenship': 'What is the country of citizenship of {bridge}?', 'employer': 'Who is the employer of {bridge}?', 'place of burial': 'Where was {bridge} buried?', 'educated at': 'Where was {bridge} educated?', 'inception': 'When was {bridge} founded?', 'country': 'In which country is {bridge}?', 'student of': 'Who was the teacher of {bridge}?', 'founded by': 'Who founded {bridge}?', 'place of detention': 'Where was {bridge} detained?'}

def occurrences(needle, text):
    return [[m.start(), m.end()] for m in re.finditer('(?<!\\w)' + re.escape(needle) + '(?!\\w)', text, re.I)]

def canonical(s):
    return ' '.join(s.casefold().split())

def hashed(x):
    return hashlib.sha256(json.dumps(x, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def qa_key(q, a):
    return hashed([canonical(q), canonical(a)])

def facts_text(record):
    return '\n\n'.join(('Title: ' + p['title'] + '\n' + p['text'] for p in record['paragraphs']))

def normalize(dataset, raw, index):
    if dataset == 'musique':
        d = raw['question_decomposition']
        if not raw['answerable'] or len(d) != 2 or any(('>>' in x['question'] for x in d)):
            return (None, 'not_natural_twohop')
        if '#' in d[0]['question'] or '#1' not in d[1]['question'] or any((x != '1' for x in re.findall('#(\\d+)', d[1]['question']))):
            return (None, 'not_linked')
        bridge = d[0]['answer'].strip()
        answer = raw['answer'].strip()
        support = [x['paragraph_support_idx'] for x in d]
        pp = {p['idx']: p for p in raw['paragraphs']}
        if len(set(support)) != 2 or any((x not in pp or not pp[x]['is_supporting'] for x in support)):
            return (None, 'support_invalid')
        if answer != d[1]['answer'].strip():
            return (None, 'answer_disagrees')
        paras = [dict(title=p['title'], text=p['paragraph_text'], official_idx=p['idx'], hop=support.index(p['idx']) + 1) for p in raw['paragraphs'] if p['idx'] in support]
        single = d[1]['question'].replace('#1', bridge)
        identity = raw['id']
        hop_ids = ['musique:' + str(x['id']) for x in d]
    else:
        e = raw.get('evidences', [])
        if raw['type'] not in ('compositional', 'inference') or len(e) != 2:
            return (None, 'not_two_edge_chain')
        orders = [(a, b) for a, b in ((e[0], e[1]), (e[1], e[0])) if a[2] == b[0] and b[2] == raw['answer']]
        if len(orders) != 1:
            return (None, 'ambiguous_chain')
        first, second = orders[0]
        bridge = second[0]
        answer = raw['answer']
        if second[1] not in RELATIONS:
            return (None, 'relation_not_in_frozen_map')
        titles = {x[0] for x in raw['supporting_facts']}
        if len(titles) != 2:
            return (None, 'not_two_support_paragraphs')
        expected = [canonical(first[0]), canonical(bridge)]
        if len(set(expected)) != 2 or {canonical(t) for t in titles} != set(expected):
            return (None, 'support_entity_alignment')
        context = {t: ss for t, ss in raw['context']}
        if any((t not in context or not 0 <= i < len(context[t]) for t, i in raw['supporting_facts'])):
            return (None, 'invalid_support_sentence')
        paras = [dict(title=t, text=' '.join(ss), official_idx=ci, hop=expected.index(canonical(t)) + 1) for ci, (t, ss) in enumerate(raw['context']) if t in titles]
        if len(paras) != 2:
            return (None, 'duplicate_context_title')
        single = RELATIONS[second[1]].format(bridge=bridge)
        identity = raw['_id']
        hop_ids = ['2wiki:' + hashed([canonical(v) for v in edge]) for edge in (first, second)]
    if not bridge or not answer or canonical(bridge) == canonical(answer) or (not any((c.isalpha() for c in bridge))):
        return (None, 'invalid_bridge_answer')
    if occurrences(bridge, raw['question']):
        return (None, 'bridge_already_in_original')
    if not all((occurrences(bridge, p['title'] + '\n' + p['text']) for p in paras)):
        return (None, 'bridge_not_literal_in_both')
    second = next((p for p in paras if p['hop'] == 2))
    if not occurrences(answer, second['title'] + '\n' + second['text']):
        return (None, 'answer_not_literal_in_second')
    r = dict(dataset=dataset, source_id=identity, source_index=index, question=raw['question'], bridge_question=single, bridge=bridge, answer=answer, paragraphs=paras, hop_ids=hop_ids, source_record=raw)
    r['qa_keys'] = [qa_key(q, answer) for q in (r['question'], single)]
    r['evidence_key'] = hashed(sorted((canonical(p['title'] + '\n' + p['text']) for p in paras)))
    return (r, None)
