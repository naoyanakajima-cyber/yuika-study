"""Embed original medaka questions and the scoped recall UI."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from questions import build
p=ROOT/'yuika-review-v2.html';s=p.read_text()
m=re.search(r'const QUESTIONS=(\[.*?\n\]);',s,re.S)
qs=json.loads(m[1]);qs=[q for q in qs if not q['id'].startswith('medaka-')]+build()
s=s[:m.start(1)]+json.dumps(qs,ensure_ascii=False,indent=2)+s[m.end(1):]
body=Path(__file__).with_name('runtime.js').read_text()
start,end='// MEDAKA_START\n','// MEDAKA_END\n'
if start in s:
 before,rest=s.split(start);_,after=rest.split(end);s=before+start+body+end+after
else:s=s.replace('// DESIGN_C_START\n',start+body+end+'// DESIGN_C_START\n')
p.write_text(s)
archive=ROOT/'scripts/history/revisions.json';a=json.loads(archive.read_text())
for q in build():
 a['yuika-review-v2.html'].setdefault(q['id'],[dict(revision=1,kind='initial',reason='Task 18: initial original medaka questions',question=q)])
archive.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
