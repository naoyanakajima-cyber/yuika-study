"""Refresh Edo questions while preserving its validated standalone engine.
Run this before notification, history, summary, design, and parent embedding.
"""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from questions import build
# Edo's standalone engine is its template. The science engine has since gained
# lever-only progression and record fields; cloning it would change Edo behavior.
# Refresh the original question definitions in place, then re-embed shared code.
s=(ROOT/'edo-review.html').read_text()
m=re.search(r'const QUESTIONS=(\[.*?\n\]);',s,re.S)
assert m, 'Edo question block is missing'
s=s[:m.start(1)]+json.dumps(build(),ensure_ascii=False,indent=2)+s[m.end(1):]
(ROOT/'edo-review.html').write_text(s)
archive=ROOT/'scripts/history/revisions.json';a=json.loads(archive.read_text());records=a.setdefault('edo-review.html',{})
for q in build():
 records.setdefault(q['id'],[dict(revision=1,kind='initial',reason='Task 19: initial original Edo questions',question=q)])
archive.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
