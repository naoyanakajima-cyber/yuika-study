"""Apply shared design hooks after application/runtime generators, before parent/embed.py."""
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.focus.subjects import embed
embed()
ROOT=Path(__file__).resolve().parents[2]
UNITS={
 'edo-review.html':('social','社会','江戸時代'),
 'onin-review.html':('social','社会','540-27'),
 'kamakura-review.html':('social','社会','540-25'),
 'heian-review.html':('social','社会','540-24'),
 'yuika-review-v2.html':('science','理科','水溶液／顕微鏡'),
 'mock-focus-review.html':('all','4教科まとめ','mock-focus'),
}
for file,(theme,subject,code) in UNITS.items():
 p=ROOT/file;s=p.read_text()
 s=re.sub(r' data-subject="[^"]*"','',s,count=1).replace('<html lang="ja">',f'<html lang="ja" data-subject="{theme}">',1)
 s=re.sub(r'// DESIGN_C_START\n.*?// DESIGN_C_END\n','',s,flags=re.S)
 science=file in ('yuika-review-v2.html','edo-review.html')
 focus=file=='mock-focus-review.html'
 lever=file=='yuika-review-v2.html'
 stats_setup=" const leverSelected=scienceUnit===LEVER_UNIT;\n" if lever else ""
 shown_code=f"leverSelected?LEVER_UNIT:{code!r}" if lever else repr(code)
 shown_total="leverSelected?QUESTIONS.filter(isLever).length:QUESTIONS.length" if lever else ("focusQuestions.length" if focus else "QUESTIONS.length")
 restrict="&&(!leverSelected||isLever(Q.get(e.questionId)))" if lever else ("&&inFocus(Q.get(e.questionId))" if focus else "")
 weak="leverSelected?scienceWeak().length:practiceWeaknesses().length" if lever else "practiceWeaknesses().length"
 lever_title=" if(leverSelected){\n  main.querySelector('.unit-hero h1').textContent=LEVER_UNIT;\n  main.querySelector('.unit-hero p').textContent='図を見て、棒がどちらに回るか考えよう。';\n }\n" if lever else ""
 hook=f'''// DESIGN_C_START
const designHome=home;
home=function(){{
 designHome();
 const latest=new Map();for(const e of [...data.events].sort((a,b)=>a.at.localeCompare(b.at)))if(Q.has(e.questionId)&&(e.variant||'normal')==='normal')latest.set(Q.get(e.questionId).originId||e.questionId,e);
{stats_setup} window.YuikaDesign.unitHome(main,{{subject:{"focusLabel||'4教科まとめ'" if focus else repr(subject)},code:{shown_code},total:{shown_total},correct:[...latest.values()].filter(e=>e.correct{restrict}).length,due:{'scienceDue()' if science else 'dueReviews()'}.length,weak:{weak}}});
{lever_title}}};
// DESIGN_C_END
'''
 s=s.replace('load();render();',hook+'load();render();')
 p.write_text(s)
