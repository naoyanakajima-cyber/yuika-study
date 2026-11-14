"""Apply shared design hooks after application/runtime generators, before parent/embed.py."""
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.focus.subjects import embed
embed()
ROOT=Path(__file__).resolve().parents[2]
UNITS={
 'onin-review.html':('social','社会','540-27'),
 'kamakura-review.html':('social','社会','540-25'),
 'heian-review.html':('social','社会','540-24'),
 'yuika-review-v2.html':('science','理科','溶解度／酸とアルカリ'),
 'mock-focus-review.html':('all','4教科まとめ','mock-focus'),
}
for file,(theme,subject,code) in UNITS.items():
 p=ROOT/file;s=p.read_text()
 s=re.sub(r' data-subject="[^"]*"','',s,count=1).replace('<html lang="ja">',f'<html lang="ja" data-subject="{theme}">',1)
 s=re.sub(r'// DESIGN_C_START\n.*?// DESIGN_C_END\n','',s,flags=re.S)
 science=theme=='science'
 focus=file=='mock-focus-review.html'
 hook=f'''// DESIGN_C_START
const designHome=home;
home=function(){{
 designHome();
 const latest=new Map();for(const e of [...data.events].sort((a,b)=>a.at.localeCompare(b.at)))if(Q.has(e.questionId)&&(e.variant||'normal')==='normal')latest.set(Q.get(e.questionId).originId||e.questionId,e);
 window.YuikaDesign.unitHome(main,{{subject:{"focusLabel||'4教科まとめ'" if focus else repr(subject)},code:'{code}',total:{'focusQuestions' if focus else 'QUESTIONS'}.length,correct:[...latest.values()].filter(e=>e.correct{"&&inFocus(Q.get(e.questionId))" if focus else ''}).length,due:{'scienceDue()' if science else 'dueReviews()'}.length,weak:practiceWeaknesses().length}});
}};
// DESIGN_C_END
'''
 s=s.replace('load();render();',hook+'load();render();')
 p.write_text(s)
