"""Validate the authoring source, embedded data and frozen first revisions."""
import copy
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.focus.validate import validate
qs=json.loads((ROOT/'scripts/focus/questions.json').read_text())
assert validate(qs)==46
assert {s:sum(q['subject']==s for q in qs) for s in ('社会','理科','算数','国語')}=={'社会':21,'理科':14,'算数':6,'国語':5}
html=(ROOT/'mock-focus-review.html').read_text()
embedded=json.loads(re.search(r'const QUESTIONS=(\[.*?\n\]);',html,re.S)[1]);assert embedded==qs
assert 'YuikaReports' not in html and "connect-src 'none'" in html
archive=json.loads((ROOT/'scripts/history/revisions.json').read_text())['mock-focus-review.html']
for q in qs: assert archive[q['id']][-1]['question']==q
# Prove the guard rejects each required failure category, including nested text.
for mutate in (
 lambda x:x.append(copy.deepcopy(x[0])),
 lambda x:x[1].update(prompt=x[0]['prompt']),
 lambda x:x[0].update(answer='not an option'),
 lambda x:x[0]['options'].__setitem__(1,x[0]['answer']),
 lambda x:x[0].update(basis=''),
 lambda x:x[0].update(source=''),
 lambda x:x[0].update(studentName='synthetic'),
 lambda x:x[0].update(explanation='受験番号: synthetic'),
 lambda x:x[0].update(explanation='synthetic@example.invalid'),
):
 bad=copy.deepcopy(qs);mutate(bad)
 try:validate(bad)
 except AssertionError:pass
 else:raise AssertionError('bad content accepted')
print('focus_data: 46 originals, unique answers/IDs/prompts, basis, private-data guards PASS')
