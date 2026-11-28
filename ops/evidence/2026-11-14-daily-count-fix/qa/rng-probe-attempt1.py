"""Independent actual-app old/new selection oracle and event/clock boundaries."""
import os,json,sys,subprocess,traceback,datetime
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-daily-fix-20261114');OUT=Path('/tmp/yuika-daily-fix-qa');sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Quiet(PreviewHandler):
 def log_message(self,*a):pass
 def do_POST(self):raise AssertionError('POST reached server')
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{srv.server_port}/'
report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'cases':[],'errors':[],'blocked_requests':[]}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  ctx=browser.new_context(viewport={'width':768,'height':1024});ctx.route('https://**/*',lambda r:(report['blocked_requests'].append(r.request.url),r.abort()));p=ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.clock.set_fixed_time(datetime.datetime(2030,1,3,tzinfo=datetime.timezone.utc));p.goto(url+'onin-review.html')
  p.evaluate('(source)=>{window.qaOldDaily=eval("("+source+")");}',(OUT/'baseline-dailyQuestions.js').read_text())
  p.evaluate('''()=>{
   const qs=QUESTIONS.filter(q=>q.type==='text'),a=qs[0],b=qs[1];
   window.qaEvent=(q,at,correct=false)=>validateEvent({id:uuid(),sessionId:'qa-daily-count',questionId:q.id,questionVersion:currentQuestionVersion(q),unitId:UNIT_ID,version:VERSION,unit:q.unit,course:q.course,question:promptOf(q,'normal'),response:correct?expectedOf(q,'normal'):'合成の誤答',expected:expectedOf(q,'normal'),explanation:q.explanation,correct,variant:'normal',mode:'normal',hint:false,at,offset:0,day:day(at,0)});
   data.events=[qaEvent(a,'2029-12-20T01:00:00Z'),qaEvent(a,'2029-12-21T01:00:00Z'),qaEvent(a,'2029-12-22T01:00:00Z',true),qaEvent(b,'2029-12-30T01:00:00Z'),qaEvent(b,'2029-12-31T01:00:00Z')];save();
  }''')
  result=p.evaluate('''()=>{
   const assert=(v,m)=>{if(!v)throw Error(m)},native=Math.random,rows=[];let draws=0,seed=0;
   const reset=()=>{draws=0;seed=654321;Math.random=()=>{draws++;seed=(Math.imul(seed,1103515245)+12345)>>>0;return seed/4294967296;}};
   try{
    for(const count of [5,10,15])for(const unit of ['all','応仁の乱','missing'])for(const variant of ['normal','kanji']){
     const p={count,unit,variant,course:'all'},now=Date.now();reset();const actualCount=dailyCount(p,now);assert(draws===0,'count drew');
     const actual=dailyQuestions(p,now).map(q=>q.id),actualDraws=draws;reset();const old=qaOldDaily(p).map(q=>q.id);
     assert(JSON.stringify(actual)===JSON.stringify(old),'ids/order mismatch');assert(draws===actualDraws,'draw mismatch');assert(actualCount===actual.length,'count mismatch');rows.push({count,unit,variant,actualCount,draws,ids:actual});
    }
    reset();render();assert(draws===0,'render drew');
   }finally{Math.random=native;}
   return {rows,due:dueReviews().map(s=>s.originId),weak:additional().map(s=>s.originId)};
  }''')
  assert result['due'] and result['weak'];report['cases'].append({'kind':'old_new_actual_app_oracle','result':result})
  # Valid non-null cross-tab event follows the existing validator and merge path.
  update=p.evaluate('''()=>{const e=qaEvent(QUESTIONS.find(q=>q.type==='text'),'2030-01-03T00:10:00.000Z');return JSON.stringify({...empty(),events:[e]});}''')
  p.evaluate('raw=>window.dispatchEvent(new StorageEvent("storage",{key:KEY,newValue:raw}))',update)
  expect(p.locator('#daily-five')).to_be_disabled();expect(p.locator('#daily-status')).to_be_visible();expect(p.locator('#daily-status')).to_contain_text('端末の日付と時刻')
  before=p.evaluate('({events:data.events.length,screen,run:run===null,raw:YuikaParent.storage.getItem(KEY)})');p.evaluate('startDaily()');assert p.evaluate("screen==='home'&&run===null");report['cases'].append({'kind':'validated_storage_event_future_stops','before':before})
  # Once clock catches up, existing date refresh restores eligibility.
  p.clock.set_fixed_time(datetime.datetime(2030,1,3,0,11,tzinfo=datetime.timezone.utc));p.evaluate('refreshPracticeDate(true)');expect(p.locator('#daily-five')).to_be_enabled();report['cases'].append({'kind':'clock_focus_refresh','count':p.locator('#daily-five').inner_text()})
  p.locator('#daily-five').click();p.locator('#response').fill('合成の未確定入力');p.evaluate('refreshPracticeDate(true)');assert p.locator('#response').input_value()=='合成の未確定入力';report['cases'].append({'kind':'active_quiz_not_repainted'})
  assert not report['errors'];report['result']='PASS';browser.close()
except Exception:report['failure']=traceback.format_exc();raise
finally:
 srv.shutdown();(OUT/'rng-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
