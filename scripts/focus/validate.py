"""Offline checks for original practice content. No personal inputs are needed."""
import json
import re
import unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REQUIRED={'id','unitId','conceptId','focusLabel','subject','unit','course','level','source','basis','type','prompt','answer','options','hint','explanation','pitfall','pair'}
OPTIONAL={'table','diagram','passage'}

def validate(questions):
 assert isinstance(questions,list) and questions, 'empty dataset'
 ids=set();prompts=set()
 for q in questions:
  ident=q.get('id','missing-id')
  assert REQUIRED <= q.keys() and q.keys() <= REQUIRED|OPTIONAL, (ident,'unexpected/missing fields')
  assert all(isinstance(q[k],str) and q[k].strip() for k in REQUIRED-{'options','level','pair'}), (ident,'empty content')
  assert q['id'] not in ids, (ident,'duplicate id')
  ids.add(q['id'])
  key=unicodedata.normalize('NFKC',q['prompt']).strip()
  assert key not in prompts, (ident,'duplicate prompt')
  prompts.add(key)
  assert re.fullmatch(r'focus-([srmk]\d+)-\d{2}',q['id']), ident
  assert re.fullmatch(r'[SRMK][1-9]',q['conceptId']) and q['conceptId'].lower() in q['id'], ident
  assert q['unitId']=='mock-focus' and q['unit']==q['conceptId']+' '+q['focusLabel'], ident
  assert q['subject']=={'S':'社会','R':'理科','M':'算数','K':'国語'}[q['conceptId'][0]], ident
  assert q['level'] in (1,2,3) and q['course']=='d'+str(q['level']), ident
  assert q['type']=='choice' and isinstance(q['options'],list) and len(q['options'])==4, ident
  assert all(isinstance(o,str) and o.strip() for o in q['options']), ident
  options=[unicodedata.normalize('NFKC',o).strip() for o in q['options']]
  assert len(set(options))==4 and options.count(unicodedata.normalize('NFKC',q['answer']).strip())==1, (ident,'answer/options')
  # Allowlisted schema excludes private analysis fields. Scan all nested strings too.
  raw=json.dumps(q,ensure_ascii=False)
  assert not re.search(r'氏名|得点|偏差値|順位|受験番号|生年月日|電話番号|[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\b\d{2,4}-\d{2,4}-\d{4}\b',raw), (ident,'private data marker')
  if 'table' in q:
   t=q['table'];assert set(t)=={'caption','headers','rows'} and '架空' in t['caption'], ident
   assert all(len(row)==len(t['headers']) for row in t['rows']), ident
  if 'passage' in q:
   assert set(q['passage'])=={'caption','paragraphs'} and 'オリジナル' in q['passage']['caption'], ident
  if 'diagram' in q:
   d=q['diagram'];assert d['kind'] in ('circle','bar','wind') and d['caption'], ident
 return len(questions)

if __name__=='__main__':
 print(f'focus data: {validate(json.loads((ROOT/"scripts/focus/questions.json").read_text()))} questions PASS')
