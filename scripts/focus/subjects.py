"""Embed subject views after practice/history/prototype and before shared design."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
def embed():
 p=ROOT/'mock-focus-review.html';s=p.read_text()
 s=re.sub(r'// FOCUS_SUBJECT_START\n.*?// FOCUS_SUBJECT_END\n','',s,flags=re.S)
 # Keep the full catalog until the subject hook scopes the visible fields.
 s=re.sub(r'(?:const|let) UNITS=.*?;\n',"let UNITS=[...new Set(QUESTIONS.map(q=>q.unit))];\n",s,count=1)
 s=s.replace('const a=analysis(),es=data.events', 'const a=analysis(),es=focusEvents()')
 s=s.replace('function history(){const es=order(data.events)', 'function history(){const es=order(focusEvents())')
 hook='// FOCUS_SUBJECT_START\n'+Path(__file__).with_name('subjects.js').read_text()+'// FOCUS_SUBJECT_END\n'
 s=s.replace('// DESIGN_C_START\n',hook+'// DESIGN_C_START\n') if '// DESIGN_C_START\n' in s else s.replace('load();render();',hook+'load();render();')
 p.write_text(s)
if __name__=='__main__':embed()
