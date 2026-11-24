"""Task 19: all original questions, two-stage UI, revision and review integration."""
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
qs=questions((ROOT/'edo-review.html').read_text())
assert len(qs)==22 and len({q['id'] for q in qs})==22
assert Counter(q['area'] for q in qs)=={'timeline':10,'system':6,'diplomacy':6}
archive=json.loads((ROOT/'scripts/history/revisions.json').read_text())['edo-review.html']
for q in qs:
 assert q['type']=='recall' and q['subject']=='社会' and q['unitId']=='shakai-edo'
 assert len(set(q['options']))==len(q['options']) and q['options'].count(q['answer'])==1
 assert all(q[k].strip() for k in ['basis','explanation','conceptId','source','pitfall'])
 assert archive[q['id']]==[dict(revision=1,kind='initial',reason='Task 19: initial original Edo questions',question=q)]
 assert not re.search(r'@|受験番号|生年月日|住所|電話番号',json.dumps(q,ensure_ascii=False))
text=(ROOT/'edo-review.html').read_text()
assert '<img' not in text and 'medaka-diagram' not in text
page_content=text.split('<!-- YUIKA_REPORTS_END -->',1)[1]
assert 'ゆいか' not in page_content
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
  page.goto(base+'edo-review.html')
  expect(page.locator('.unit-hero h1')).to_have_text('江戸幕府の成立・幕藩体制・鎖国')
  assert page.locator('html').get_attribute('data-subject')=='social'
  assert page.evaluate("scienceDaily().length===5&&scienceDaily().every(q=>q.unitId==='shakai-edo')")
  page.evaluate("YuikaParent.storage.setItem('synthetic-other-unit','preserve')")
  def prepare(q):
   page.evaluate("id=>{session={id:uid(),mode:'unit',questions:[byId.get(id)],index:0,results:[],hint:false,selected:null,answered:false,done:false};view='quiz';render();}",q['id'])
   assert page.locator('[data-choice]').count()==0
  def first(answer):
   page.locator('#recall-text').fill(answer);page.locator('#check').tap()
  def last():return page.evaluate('state.events.at(-1)')
  count=0
  for q in qs:
   prepare(q);page.locator('#check').tap();assert not page.evaluate('session.answered')
   first(q['answer']);e=last();assert e['recallOutcome']=='unaided' and e['correct'] and not e['hintUsed'];count+=1
   expect(page.locator('#feedback')).to_contain_text('自力で正解')
   for option in q['options']:
    prepare(q);first('わからない');assert page.locator('[data-choice]').count()==len(q['options'])
    assert not page.evaluate('session.answered')
    page.locator('[data-choice]').nth(q['options'].index(option)).tap();page.locator('#check').tap();e=last()
    assert e['recallOutcome']==('assisted' if option==q['answer'] else 'incorrect')
    assert e['firstResponse']=='わからない' and e['response']==option and e['hintUsed'] and e['correct']==(option==q['answer']);count+=1
   assert page.evaluate('q=>[q.answer,...q.aliases].every(a=>grade(q,a))&&!grade(q,"わからない")&&!grade(q,q.answer+"ではない")',q)
  page.reload();assert page.evaluate('state.events.length')==count
  assert page.evaluate('validateState(JSON.parse(YuikaParent.storage.getItem(KEY))).events')==page.evaluate('state.events')
  assert page.evaluate('''()=>{
   const rejects=f=>{try{validateEvent(f);return false;}catch{return true;}};
   return state.events.every(e=>rejects({...e,recallOutcome:'forged'})&&rejects({...e,firstResponse:e.recallOutcome==='unaided'?'不明':e.expected})&&rejects({...e,hintUsed:!e.hintUsed}));
  }''')
  # Interrupted choice stage does not save an incomplete outcome.
  prepare(qs[0]);first('わからない');page.reload();assert page.evaluate('state.events.length')==count
  # Assisted attempts remain weak immediately and across days; unaided starts due recheck.
  page.evaluate('''()=>{
   YuikaParent.storage.removeItem(KEY);state=emptyState();const q=QUESTIONS[0];
   const mk=(at,outcome)=>{const response=outcome==='incorrect'?q.options[1]:q.answer;return validateEvent({questionVersion:1,id:uid(),sessionId:'synthetic-edo',questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response,inputRaw:response,expected:q.answer,correct:outcome!=='incorrect',answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed:outcome!=='unaided',mode:'normal',explanation:q.explanation,recallOutcome:outcome,firstResponse:outcome==='unaided'?q.answer:'不明'});};
   state.events=[mk('2026-11-11T03:00:00.000Z','assisted')];
   if(!scienceWeak().some(r=>r.originId===q.id))throw Error('assisted not weak');
   state.events.push(mk('2026-11-12T03:00:00.000Z','incorrect'));
   if(scienceDaily()[0].id!==q.id)throw Error('weak not prioritized');
   state.events.push(mk('2026-11-14T03:00:00.000Z','unaided'));persist();home();
   if(scienceWeak().some(r=>r.originId===q.id)||!scienceDue().some(r=>r.originId===q.id)||scienceDaily()[0].id!==q.id)throw Error('due/weak mismatch '+JSON.stringify({weak:scienceWeak(),due:scienceDue(),states:retention(),clock:practiceClockIssue(),blocked,dirty,now:new Date().toISOString(),daily:scienceDaily().map(q=>q.id)}));
  }''')
  page.reload();page.add_script_tag(url=base+'assets/progress.js')
  assert page.evaluate("scienceDaily()[0].id==='edo-01'")
  assert page.evaluate("YuikaDesign.summary('edo-review.html')")==dict(correct=1,total=22,due=1,dueCount=1,weakCount=0,normalCount=4,unavailable=False),page.evaluate("YuikaDesign.summary('edo-review.html')")
  assert page.evaluate("YuikaParent.storage.getItem('synthetic-other-unit')")=='preserve'
  # Parent verification uses session storage and leaves child records byte-identical.
  saved=page.evaluate('YuikaParent.storage.getItem(KEY)')
  page.goto(base+'edo-review.html?parent-check=1');prepare(qs[1]);first(qs[1]['answer'])
  assert page.evaluate('localStorage.getItem(KEY)')==saved
  assert not posts and not errors,(posts,errors)
  ctx.close();browser.close()
finally:server.shutdown()
print(f'edo: 22 originals, {count} UI answers, aliases, order, revisions, strict import, recall/weak/due/daily/home, isolated records and parent mode PASS')
