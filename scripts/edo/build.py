"""Reuse task 18's validated two-stage engine with a separate social dataset/key.
Run this before history, summary, design, and parent embedding.
"""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from questions import build,UNIT
s=(ROOT/'yuika-review-v2.html').read_text()
m=re.search(r'const QUESTIONS=(\[.*?\n\]);',s,re.S)
s=s[:m.start(1)]+json.dumps(build(),ensure_ascii=False,indent=2)+s[m.end(1):]
s=re.sub(r'const QUESTION_REVISIONS=.*?;\n', 'const QUESTION_REVISIONS={};\n',s,count=1)
s=s.replace("yuika-science-2026-10-v2","shakai-edo-2026-11-v1").replace('yuika-science-review-v2','yuika-social-edo-v1').replace('yuika-science-v1','yuika-social-edo-legacy-unused')
s=s.replace('yuika-review-v2.html','edo-review.html')
s=s.replace('ゆいかの理科ノート',UNIT).replace('ゆいかの理科学習ノート','社会学習ノート').replace('おつかれさま、ゆいか！','おつかれさま！').replace('YUIKA’S SCIENCE NOTE','社会 · 江戸時代')
s=s.replace('ゆいか','学習者')
s=s.replace('理科','社会').replace('メダカの入力・図問題','この単元の入力問題').replace('メダカ：', '江戸時代：')
s=s.replace('像（ぞう）はレンズを通して見える姿、視野（しや）はのぞいたときに見える範囲です。','年号・政治のしくみ・外交を確かめよう。')
s=s.replace('ヒントを見てもだいじょうぶ。解説まで読んでみよう。','まず自分で答え、まちがえたら選択肢で再挑戦しよう。')
s=re.sub(r'<svg class="art".*?</svg>','',s,flags=re.S)
# No new notification integration; the existing apps and configuration stay intact.
s=re.sub(r'<!-- YUIKA_REPORTS_BEGIN -->.*?<!-- YUIKA_REPORTS_END -->','',s,flags=re.S)
s=re.sub(r'^ window.YuikaReports.enqueue\(.*\n','',s,flags=re.M)
s=re.sub(r'function medakaDiagram\(q\)\{.*?\n\}\n','',s,flags=re.S)
s=s.replace("q.diagram?medakaDiagram(q):",'')
s=s.replace("subject:'社会',code:'水溶液／顕微鏡'", "subject:'社会',code:'江戸時代'")
s=s.replace('data-subject="science"','data-subject="social"')
(ROOT/'edo-review.html').write_text(s)
archive=ROOT/'scripts/history/revisions.json';a=json.loads(archive.read_text());records=a.setdefault('edo-review.html',{})
for q in build():
 records.setdefault(q['id'],[dict(revision=1,kind='initial',reason='Task 19: initial original Edo questions',question=q)])
archive.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
