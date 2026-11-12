"""Science 47-question adapter: original grading, full-history replay and UI."""
import os
import json
import sys
import subprocess
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT
def verify_storage_access_recovery(browser, base, fixture):
 # A fresh page cannot assume an unreadable disk is empty. Keep a real disk
 # answer/aggregate and an unsaved answer, and exercise the existing retry UI.
 key='yuika-prototype-v1:yuika-science-review-v2'
 pending=dict(fixture['events'][0],id='synthetic-access-pending')
 for case in ('valid','malformed','empty','conflict'):
  disk=json.loads(json.dumps(fixture))
  if case=='conflict':
   disk['events'][0]['id']=pending['id']
   disk['events'][0]['sessionId']='synthetic-conflicting-session'
  raw='{' if case=='malformed' else '' if case=='empty' else json.dumps(disk)
  ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True)
  errors=[];posts=[];external=[]
  def block_external(route):
   if route.request.method=='POST':posts.append(route.request.url);route.abort()
   elif route.request.url.startswith('https://fonts.googleapis.com/css2?') and route.request.resource_type=='stylesheet':route.abort()
   elif not route.request.url.startswith(base+'/'):external.append(route.request.url);route.abort()
   else:route.continue_()
  ctx.route('**/*',block_external)
  ctx.add_init_script("""(() => {
   if(sessionStorage.getItem('synthetic-recovery-seeded'))return;
   sessionStorage.setItem('synthetic-recovery-seeded','yes');
   window.recoveryGet=Storage.prototype.getItem;window.recoverySet=Storage.prototype.setItem;
   const key="""+json.dumps(key)+""",raw="""+json.dumps(raw)+""";
   recoverySet.call(localStorage,key,raw);
   recoverySet.call(localStorage,'yuika-science-review-v2','synthetic old untouched');
   recoverySet.call(localStorage,'yuika-social-540-27-v1','synthetic other untouched');
   Storage.prototype.getItem=function(k){if(k===key)throw Error('synthetic temporary read refusal');return recoveryGet.call(this,k);};
  })();""")
  page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+'/yuika-review-v2.html')
  assert page.evaluate('blocked&&rawBroken===null&&state.events.length===0')
  page.evaluate('(event)=>{state.events.push(validateEvent(event));dirty=true;view="records";render();}',pending)
  before=page.evaluate('JSON.stringify(state)')
  page.locator('#retry').click()
  assert page.evaluate('blocked&&dirty&&JSON.stringify(state)')==before
  assert '保存ができました' not in page.locator('#notice').inner_text()
  assert page.evaluate('(key)=>recoveryGet.call(localStorage,key)',key)==raw
  page.evaluate('()=>{Storage.prototype.getItem=recoveryGet;}')
  if case=='valid':
   # Failed writes must not commit the merged in-memory state or unlock analysis.
   page.evaluate('()=>{Storage.prototype.setItem=function(k,v){if(k===KEY)throw Error("synthetic quota");return recoverySet.call(this,k,v);};}')
   page.locator('#retry').click()
   assert page.evaluate('blocked&&dirty&&JSON.stringify(state)')==before
   assert page.evaluate('localStorage.getItem(KEY)')==raw
   page.evaluate('()=>{Storage.prototype.setItem=recoverySet;}')
   page.locator('#retry').click()
   assert page.evaluate('!blocked&&!dirty')
   assert '保存ができました' in page.locator('#notice').inner_text()
   expected=dict(fixture,events=fixture['events']+[pending])
   assert page.evaluate('state')==expected
   assert json.loads(page.evaluate('localStorage.getItem(KEY)'))==expected
   page.locator('#retry').click()
   assert page.evaluate('state')==expected
   page.reload()
   assert page.evaluate('!blocked&&!dirty')
   assert page.evaluate('state')==expected
   assert page.locator('#daily-five').is_enabled()
  else:
   page.locator('#retry').click()
   assert page.evaluate('blocked&&dirty&&JSON.stringify(state)')==before
   assert page.evaluate('localStorage.getItem(KEY)')==raw
   assert '保存ができました' not in page.locator('#notice').inner_text()
   # Even while disk is unsafe, the pending answer can be backed up as a file.
   with page.expect_download() as download:page.locator('#export').click()
   packet=json.loads(Path(download.value.path()).read_text())
   assert packet['payload']['events']==[pending]
  assert page.evaluate("localStorage.getItem('yuika-science-review-v2')")=='synthetic old untouched'
  assert page.evaluate("localStorage.getItem('yuika-social-540-27-v1')")=='synthetic other untouched'
  assert not errors and not posts and not external,(errors,posts,external)
  ctx.close()

server=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  context=browser.new_context(viewport={'width':768,'height':1024})
  context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
  page=context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('https://**/*',lambda r:r.abort())
  page.clock.install(time=datetime(2026,11,10,3,tzinfo=timezone.utc))
  base=f'http://127.0.0.1:{server.server_port}'
  page.goto(base+'/yuika-review-v2.html')
  page.evaluate('''() => {
   const assert=(x,m)=>{if(!x)throw Error(m);};
   assert(QUESTIONS.length===47,'47 originals');
   window.mk=(q,at,correct=false,hintUsed=false)=>{
    const response=correct?q.answer:q.type==='number'?q.answer+1:q.options.find(o=>o!==q.answer);
    return validateEvent({id:uid(),sessionId:'synthetic-science',questionId:q.id,datasetVersion:VERSION,
     unit:q.unit,type:q.type,question:q.prompt,response,inputRaw:String(response),expected:q.answer,
     correct,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed,mode:'normal',explanation:q.explanation});
   };
   for(const q of QUESTIONS){
    const a=mk(q,'2026-09-01T14:59:00.000Z'),b=mk(q,'2026-09-01T15:00:00.000Z');
    state.events=[a,b];const snapshot=JSON.stringify(state);
    assert(weaknesses().length===0,'30-day extraction expires');
    assert(retention()[0].status==='weak'&&scienceWeak().length===1,'all 47 old weaknesses retained');
    assert(JSON.stringify(state)===snapshot,'adapter mutates history');
    assert(typeof data.events[0].response===(q.type==='number'?'number':'string'),'typed response');
    const c=mk(q,'2026-09-02T14:59:00.000Z',true);
    state.events.push(c);assert(retention()[0].due==='2026-09-03','JST waiting');
    state.events.push(mk(q,'2026-09-02T14:59:59.000Z',true),mk(q,'2026-09-02T15:00:00.000Z',true,true));
    assert(retention()[0].stage===0,'early and hinted do not advance');
    state.events.push(mk(q,'2026-09-02T15:00:00.000Z',true));assert(retention()[0].due==='2026-09-05','day one');
    state.events.push(mk(q,'2026-09-04T15:00:00.000Z',true),mk(q,'2026-09-08T15:00:00.000Z',true));
    assert(retention()[0].status==='retained','day three seven');
    state.events.push(mk(q,'2026-11-09T00:00:00.000Z'));assert(retention()[0].status==='weak','failure returns weak');
    assert(scienceDaily()[0].id===q.id,'weak prioritized');
    assert(new Set(scienceDaily().map(q=>q.id)).size===5,'no duplicate origins');
    assert(merge(state,state).events.length===state.events.length,'dedup');
    state.events=[a,mk(q,'2026-09-01T14:59:59.000Z')];assert(!retention().length,'same JST day');
    assert(grade(q,q.answer)&&!grade(q,q.type==='number'?q.answer+0.1:'unregistered'),'original grade');
   }
   assert(numeric('１．８')===1.8&&numeric('1.8g')===null&&numeric('-1')===null,'original numeric/unit parsing');
   // Due, weak and normal ordering; no fabricated extra questions or answers.
   const q=QUESTIONS.find(q=>q.type==='number'),q2=QUESTIONS.find(q=>q.type==='choice');
   state=emptyState();state.events=[mk(q,'2026-09-01T00:00:00.000Z'),mk(q,'2026-09-02T00:00:00.000Z'),mk(q,'2026-09-03T00:00:00.000Z',true),mk(q2,'2026-11-07T00:00:00.000Z'),mk(q2,'2026-11-08T00:00:00.000Z')];
   const legacy=JSON.stringify({attempts:100,correct:[1,2],wrong:[3]});
   state.legacy=[{raw:legacy,capturedAt:'2026-10-01T00:00:00.000Z'}];
   assert(scienceDaily()[0].id===q.id&&scienceDaily()[1].id===q2.id,'due weak normal priority');
   assert(retention().length===2,'legacy aggregate ignored');
   scienceUnit=q.unit;assert(scienceDaily().every(o=>o.unit===q.unit),'unit filter');scienceUnit='all';
   blocked=true;assert(!scienceWeak().length&&!scienceDue().length,'blocked analysis');blocked=false;
   dirty=true;assert(!scienceWeak().length&&!scienceDue().length,'dirty analysis');dirty=false;
   assert(persist(),'persist old histories');home();
   assert(document.querySelector('#science-summary').textContent.includes('今日の再確認 1問'),'summary');
   // Save failure does not discard pending event or overwrite protected disk.
   const disk=localStorage.getItem(KEY),set=Storage.prototype.setItem;
   Storage.prototype.setItem=function(){throw Error('synthetic quota');};
   state.events.push(mk(q,'2026-11-10T00:00:00.000Z',true));
   assert(!persist()&&dirty&&localStorage.getItem(KEY)===disk,'quota preserves disk');
   assert(!scienceWeak().length,'quota pauses analysis');Storage.prototype.setItem=set;
   assert(persist()&&!dirty,'retry saves');
   // Reset only synthetic state to exercise the numeric UI first.
   state.events=state.events.slice(0,-1);localStorage.setItem(KEY,JSON.stringify(state));
   home();
  }''')
  page.locator('#daily-five').click()
  assert page.evaluate("session.mode==='daily'&&session.questions[0].type==='number'")
  page.locator('#numeric').fill('1g')
  page.locator('#check').click()
  assert page.evaluate('!session.answered')
  page.locator('#hint').click()
  page.locator('#numeric').fill(page.evaluate('String(session.questions[0].answer)'))
  page.locator('#check').click()
  assert page.evaluate("state.events.at(-1).correct&&state.events.at(-1).hintUsed&&state.events.at(-1).questionVersion===1&&state.events.at(-1).mode==='daily'")
  page.locator('#next').click()
  assert page.evaluate("session.questions[session.index].type==='choice'")
  page.locator('[data-choice]').nth(page.evaluate('session.questions[session.index].options.indexOf(session.questions[session.index].answer)')).click()
  page.locator('#check').click()
  assert page.evaluate("state.events.at(-1).correct&&state.events.at(-1).mode==='daily'")
  page.reload()
  page.locator('#unit').select_option(page.evaluate('UNITS[0]'))
  page.locator('[data-count="10"]').click()
  prefs=page.evaluate('({count,scienceUnit})')
  page.reload();assert page.evaluate('({count,scienceUnit})')==prefs
  assert page.locator('#unit').input_value()==prefs['scienceUnit']
  page.evaluate("window.beforeImport=JSON.stringify(state);window.exported=JSON.stringify(validateState(state));")
  page.evaluate("async()=>{await importFile(new File([exported],'synthetic.json'));}")
  assert page.evaluate('JSON.stringify(state)===beforeImport')
  fixture=page.evaluate('({schemaVersion:2,datasetVersion:VERSION,events:[state.events[0]],legacy:state.legacy})')
  verify_storage_access_recovery(browser,base,fixture)
  # The learning entry depends on React/Babel. Fulfill its actual public assets
  # through the proxy-aware curl path, while notification APIs remain blocked.
  assets={}
  for path in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
   url='https://unpkg.com/'+path
   assets[url]=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',url])
  page.route('https://unpkg.com/**',lambda r:r.fulfill(body=assets[r.request.url],content_type='application/javascript'))
  page.goto(base+'/index.html')
  page.get_by_role('button',name='今日の5問をはじめる',exact=True).click()
  page.wait_for_url('**/yuika-review-v2.html?daily=1')
  assert page.evaluate("session.mode==='daily'&&session.questions.length===Math.min(count,candidates('normal',scienceUnit).length)")
  page.close();page=context.new_page();page.goto(base+'/yuika-review-v2.html')
  assert page.evaluate('({count,scienceUnit})')==prefs
  assert not errors,errors
  context.close();browser.close()
finally: server.shutdown()
print('science_adaptive: 47 original questions, grades, JST replay, priority, UI, persistence/import, access recovery UI, legacy exclusion PASS')
