"""Independent candidate integration QA; synthetic only and external requests blocked."""
import os,json,sys,datetime,subprocess,time,urllib.parse
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/qa-rev-lever-checkout');OUT=Path('/workspace/qa-rev-lever-evidence');sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Quiet(PreviewHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{srv.server_port}/';UNIT='てこのつり合い';URL=BASE+'yuika-review-v2.html?'+urllib.parse.urlencode({'unit':UNIT})
rows=[];posts=[];external=[];errors=[];assets={};began=time.monotonic()
# Browser receives public dependency bytes locally. No browser network beyond loopback.
for path in ['react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js']:
 url='https://unpkg.com/'+path;assets[url]=subprocess.check_output(['curl','-fsSL','--max-time','30',url])
def prepare(p,ids):p.evaluate("ids=>{session={id:uid(),mode:'unit',questions:ids.map(id=>byId.get(id)),index:0,results:[],hint:false,selected:null,answered:false,done:false,leverPractice:true};view='quiz';render()}",ids)
def answer(p,wrong=False,hint=False):
 q=p.evaluate('session.questions[session.index]');value=q['answer']
 if wrong:value=99999 if q['type']=='number' else next(o for o in q['options'] if o!=q['answer'])
 if hint:p.locator('#hint').tap()
 if q['type']=='number':p.locator('#numeric').fill(str(value))
 else:p.locator('[data-choice]').nth(q['options'].index(value)).tap()
 p.locator('#check').tap();assert p.evaluate('session.answered');return p.evaluate('session.results.at(-1)')
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'])
  def fresh():
   c=b.new_context(viewport={'width':768,'height':1024},has_touch=True);c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
   def route(r):
    req=r.request
    if req.method!='GET':posts.append({'url':req.url,'method':req.method});r.abort()
    elif req.url in assets:r.fulfill(body=assets[req.url],content_type='application/javascript')
    elif req.url.startswith(BASE):r.continue_()
    else:external.append(req.url);r.abort()
   c.route('**/*',route);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.clock.install(time=datetime.datetime(2026,11,22,3,tzinfo=datetime.timezone.utc));p.goto(URL);return c,p
  c,p=fresh()
  for n in [5,10]:
   p.locator(f'[data-count="{n}"]').tap();raw=p.evaluate('YuikaParent.storage.getItem(KEY)');display=int(p.locator('#daily-five').get_attribute('data-daily-count'));assert display==n
   p.locator('#daily-five').tap();qs=p.evaluate('session.questions.map(q=>({id:q.id,step:q.step,unit:q.unit}))');assert len(qs)==display and qs[0]['step']==0 and all(q['unit']==UNIT and q['step']<4 for q in qs)
   if n==5:assert all(q['step']==0 for q in qs)
   assert p.evaluate('YuikaParent.storage.getItem(KEY)')==raw;rows.append({'case':'initial daily stages','count':n,'questions':qs});p.locator('#end').tap()
  # Persist only a unit preference, then follow the actual top-home resume button.
  p.locator('[data-count="5"]').tap();raw=p.evaluate('YuikaParent.storage.getItem(KEY)');p.goto(BASE+'index.html');expect(p.locator('.daily-panel h2')).to_have_text('今日の復習');p.get_by_role('button',name='今日の復習をはじめる',exact=True).tap();p.wait_for_url('**/yuika-review-v2.html?**');p.wait_for_function("typeof session!=='undefined'&&session!==null")
  qs=p.evaluate('session.questions.map(q=>({id:q.id,unit:q.unit,step:q.step}))');assert len(qs)==5 and all(q['unit']==UNIT and q['step']==0 for q in qs);assert p.evaluate('YuikaParent.storage.getItem(KEY)')==raw;p.screenshot(path=str(OUT/'lever-home-resume.png'));rows.append({'case':'top-home resumes lever preference','url':p.url,'questions':qs});c.close()
  c,p=fresh();ids=p.evaluate("QUESTIONS.filter(q=>isLever(q)&&q.step===3).map(q=>q.id)")
  assert not p.evaluate('leverUnlocked()')
  prepare(p,[ids[0]]);answer(p);assert not p.evaluate('leverUnlocked()')
  prepare(p,[ids[0]]);answer(p);assert not p.evaluate('leverUnlocked()')
  prepare(p,[ids[1]]);answer(p,hint=True);assert not p.evaluate('leverUnlocked()')
  prepare(p,[ids[1]]);answer(p);assert p.evaluate('leverUnlocked()');p.reload();expect(p.locator('#lever-challenge')).to_be_enabled()
  p.locator('#daily-five').tap();qs=p.evaluate('session.questions.map(q=>({id:q.id,unit:q.unit,step:q.step}))');assert len(qs)==5 and all(q['unit']==UNIT for q in qs) and any(q['step']==4 for q in qs);rows.append({'case':'distinct unaided stage3 unlock and daily challenge','questions':qs})
  p.locator('#end').tap();p.locator('#lever-challenge').tap();qs=p.evaluate('session.questions.map(q=>({id:q.id,unit:q.unit,step:q.step}))');assert len(qs)==2 and all(q['step']==4 and q['unit']==UNIT for q in qs);rows.append({'case':'explicit challenge two questions','questions':qs});c.close()
  c,p=fresh();ids=p.evaluate("()=>{const q=QUESTIONS.find(q=>isLever(q)&&q.step===2&&QUESTIONS.some(r=>isLever(r)&&r.step===1&&r.conceptId===q.conceptId));return [q.id,QUESTIONS.find(r=>isLever(r)&&r.step===0&&r.conceptId!==q.conceptId).id]}");prepare(p,ids);q=p.evaluate('session.questions[0]');event=answer(p,wrong=True);assert not event['correct'];qs=p.evaluate('session.questions.map(q=>({id:q.id,step:q.step,conceptId:q.conceptId}))');assert len(qs)==3 and qs[1]['step']==q['step']-1 and qs[1]['conceptId']==q['conceptId'] and qs[2]['id']==ids[1];expect(p.locator('#quiz-count')).to_contain_text('/ 3問');p.locator('#next').tap();expect(p.locator('#quiz-count')).to_contain_text('2 / 3問');answer(p,wrong=True);assert p.evaluate('session.questions.length')==3;assert p.evaluate('state.events.length')==2;p.screenshot(path=str(OUT/'lever-remedial-count.png'));rows.append({'case':'wrong inserts one lower-stage question; remedial wrong no recursion','initial_ids':ids,'expanded_queue':qs,'events':p.evaluate('state.events')});c.close()
  assert not posts and not errors
  result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':round(time.monotonic()-began,2),'cases':rows,'posts':posts,'pageerrors':errors,'blocked_external':external,'method':'three fresh synthetic Chromium 768x1024 touch contexts; PreviewHandler CSP; non-loopback requests aborted except three public libraries locally fulfilled; actual user controls, targeted sessions for unlock/remedial','limitations':['Chromium only; no actual iPad/Safari','no real notifications or deployed app','targeted stage3/stage2 session arrangement, not full learner progression']};(OUT/'lever-probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS independent lever integration cases',len(rows));b.close()
finally:srv.shutdown();srv.server_close()
