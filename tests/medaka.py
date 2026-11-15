"""Task 18: original data, real touch/input grading, strict history and review replay."""
import json,os,re,sys
from collections import Counter
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
from scripts.history.embed import questions
qs=questions((ROOT/'yuika-review-v2.html').read_text());new=[q for q in qs if q['id'].startswith('medaka-')]
assert len(qs)==84 and len({q['id'] for q in qs})==84
assert Counter(q['area'] for q in new)=={'growth':5,'fins':8,'water':4}
archive=json.loads((ROOT/'scripts/history/revisions.json').read_text())['yuika-review-v2.html']
for q in new:
 assert q['type']=='recall' and q['unitId']=='rika-medaka'
 assert len(set(q['options']))==len(q['options']) and q['options'].count(q['answer'])==1
 assert all(q[k].strip() for k in ['basis','explanation','conceptId','source','pitfall'])
 assert archive[q['id']]==[dict(revision=1,kind='initial',reason='Task 18: initial original medaka questions',question=q)]
 assert not re.search(r'@|受験番号|生年月日|住所|電話番号',json.dumps(q,ensure_ascii=False))
server=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  ctx=browser.new_context(viewport={'width':768,'height':1024},has_touch=True)
  posts=[];errors=[]
  def route(r):
   if r.request.method=='POST':posts.append(r.request.url);r.abort()
   elif not r.request.url.startswith(base):r.abort()
   else:r.continue_()
  ctx.route('**/*',route);ctx.add_init_script(path=str(ROOT/'tests/seed_random.js'))
  page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.clock.install(time=datetime(2026,11,15,3,tzinfo=timezone.utc))
  page.goto(base+'yuika-review-v2.html?unit=メダカの飼育・ひれ・成長')
  expect(page.locator('.unit-hero h1')).to_have_text('メダカの飼育・ひれ・成長')
  assert page.evaluate("scienceUnit==='メダカの飼育・ひれ・成長'&&scienceDaily().length===5&&scienceDaily().every(q=>q.unitId==='rika-medaka')")
  def prepare(q):
   page.evaluate("id=>{session={id:uid(),mode:'unit',questions:[byId.get(id)],index:0,results:[],hint:false,selected:null,answered:false,done:false};view='quiz';render();}",q['id'])
   assert page.locator('[data-choice]').count()==0
  def first(q,answer):
   if q.get('diagram'):
    b=page.locator(f'[data-fin="{answer}"]');box=b.bounding_box();assert box['width']>=44 and box['height']>=44
    b.tap()
   else:page.locator('#recall-text').fill(answer)
   page.locator('#check').tap()
  def last():return page.evaluate('state.events.at(-1)')
  # Every original: unaided, assisted, incorrect; real hit regions or text controls.
  expected=[]
  for q in new:
   prepare(q);page.locator('#check').tap();assert not page.evaluate('session.answered')
   first(q,q['answer']);e=last();assert e['recallOutcome']=='unaided' and e['correct'] and not e['hintUsed'];expected.append(e)
   expect(page.locator('#feedback')).to_contain_text('自力で正解')
   for option in q['options']:
    prepare(q);wrong=q['options'][1] if q['options'][0]==q['answer'] else q['options'][0]
    first(q,wrong);assert page.locator('[data-choice]').count()==len(q['options'])
    assert not page.evaluate('session.answered')
    page.locator('[data-choice]').nth(q['options'].index(option)).tap();page.locator('#check').tap();e=last()
    assert e['recallOutcome']==('assisted' if option==q['answer'] else 'incorrect')
    assert e['firstResponse']==wrong and e['response']==option and e['hintUsed']
    assert e['correct']==(option==q['answer']);expected.append(e)
   # All registered aliases + kana/full-width normalization are exact, no substring.
   assert page.evaluate('q=>[q.answer,...q.aliases].every(a=>grade(q,a))&&!grade(q,"わからない")&&!grade(q,q.answer+"ではない")',q)
  assert len(expected)==74,len(expected)
  page.reload();assert page.evaluate('state.events.length')==len(expected)
  assert page.evaluate('validateState(JSON.parse(YuikaParent.storage.getItem(KEY))).events')==page.evaluate('state.events')
  # Strict import/forgery rejection across all three outcomes and old question types.
  assert page.evaluate('''()=>{
   const rejects=f=>{try{validateEvent(f);return false;}catch{return true;}};
   return state.events.every(e=>rejects({...e,recallOutcome:'forged'})&&rejects({...e,firstResponse:e.recallOutcome==='unaided'?'不明':e.expected})&&rejects({...e,hintUsed:!e.hintUsed}));
  }''')
  # Every fin region for both sexes, at tablet and narrow widths; outside taps do not select.
  for sex in ['male','female']:
   for width in [768,375]:
    page.set_viewport_size({'width':width,'height':1024})
    for fin in ['むなびれ','はらびれ','せびれ','しりびれ','おびれ']:
     q=next(q for q in new if q.get('diagram',{}).get('sex')==sex)
     prepare(q);page.locator('#medaka-diagram').tap(position={'x':10,'y':10});assert page.evaluate('session.selected') is None
     b=page.locator(f'[data-fin="{fin}"]');box=b.bounding_box();assert min(box['width'],box['height'])>=44
     b.tap();assert page.evaluate('session.selected')==fin
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.set_viewport_size({'width':768,'height':1024})
  # A single assisted attempt stays weak, across days/reloads; unaided starts spaced recheck.
  page.evaluate('''()=>{
   YuikaParent.storage.removeItem(KEY);state=emptyState();
   const q=byId.get('medaka-07');
   const mk=(at,outcome)=>{const response=outcome==='incorrect'?q.options[1]:q.answer;return validateEvent({questionVersion:1,id:uid(),sessionId:'synthetic-medaka-review',questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response,inputRaw:response,expected:q.answer,correct:outcome!=='incorrect',answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed:outcome!=='unaided',mode:'normal',explanation:q.explanation,recallOutcome:outcome,firstResponse:outcome==='unaided'?q.answer:q.options[1]});};
   state.events=[mk('2026-11-11T03:00:00.000Z','assisted')];
   if(!scienceWeak().some(r=>r.originId===q.id))throw Error('Assisted missing from weak');
   state.events.push(mk('2026-11-12T03:00:00.000Z','assisted'));
   if(scienceDaily()[0].id!==q.id)throw Error('Unassisted recheck absent');
   state.events.push(mk('2026-11-14T03:00:00.000Z','unaided'));persist();home();
   if(!scienceDue().some(r=>r.originId===q.id))throw Error('No spaced due');
   if(scienceWeak().some(r=>r.originId===q.id))throw Error('Unaided still weak');
   if(scienceDaily()[0].id!==q.id)throw Error('Due not first');
  }''')
  page.reload();assert page.evaluate("scienceDaily()[0].id==='medaka-07'")
  # The home projection must accept new fields, count unaided and use identical retention.
  page.add_script_tag(url=base+'assets/progress.js')
  summary=page.evaluate("YuikaDesign.summary('yuika-review-v2.html?unit=メダカの飼育・ひれ・成長')")
  assert summary['total']==17 and summary['correct']==1 and summary['due']==1 and summary['dueCount']==1,summary
  page.locator('#daily-five').tap();assert page.evaluate("session.questions[0].id==='medaka-07'")
  page.evaluate("session.done=true;navigate('analysis')");expect(page.locator('main')).to_contain_text('選択肢で正解：2回答')
  assert not posts and not errors,(posts,errors)
  ctx.close();browser.close()
finally:server.shutdown();server.server_close()
print('medaka: 17 originals (5/8/4), 74 saved outcomes, all fin regions, aliases/strict history, reload, weakness/recheck/daily/home PASS')
