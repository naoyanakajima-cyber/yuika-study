"""Clock safety, suspended-tab midnight refresh and retention replay cost."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT

# Preserve #19's projection as an independent oracle. This does not need Git
# branches/network and compares states, rather than measuring machine speed.
BASELINE = r'''
function baselineRetention(events,now){
 const states=new Map(),histories=new Map(),seen=new Set();
 for(const e of order(events)){
  if(seen.has(e.id)||Date.parse(e.at)>now)continue;seen.add(e.id);
  const q=Q.get(e.questionId);if(!q)continue;
  const originId=q.originId||q.id,key=originId+':'+e.variant;
  if(!histories.has(key))histories.set(key,[]);
  const history=histories.get(key);history.push(e);
  let s=states.get(key);
  if(!s){
   if(!weaknesses(history,Date.parse(e.at)).length)continue;
   s={originId,variant:e.variant,status:'weak',stage:0,due:null,anchor:null};states.set(key,s);
  }
  const date=japanDay(e.at);
  if(!e.correct){s.status='weak';s.stage=0;s.due=null;s.anchor=null;}
  else if(!e.hint){
   if(s.status==='weak'){
    s.status='waiting';s.stage=0;s.anchor=date;s.due=addJapanDays(date,REVIEW_INTERVAL_DAYS[0]);
   }else if(s.status==='waiting'&&date>=s.due){
    s.stage++;
    if(s.stage===REVIEW_INTERVAL_DAYS.length){s.status='retained';s.due=null;}
    else s.due=addJapanDays(date,REVIEW_INTERVAL_DAYS[s.stage]-REVIEW_INTERVAL_DAYS[s.stage-1]);
   }
  }
 }
 return [...states.values()];
}
'''
source = (ROOT/'scripts/practice/adaptive.js').read_text()
weak = source[source.index('function weaknesses('):source.index('let adaptiveLevel=')]
retention = source[source.index('function retention('):source.index('function practiceWeaknesses(')]
setup = r'''
const q={id:'q',unit:'u',level:1},Q=new Map([['q',q],['q-review-v1',{...q,id:'q-review-v1',originId:'q'}]]),QUESTIONS=[q];
const data={events:[]};let blocked=false,dirty=false;
const order=es=>[...es].sort((a,b)=>a.at.localeCompare(b.at)||a.id.localeCompare(b.id));
const japanDay=iso=>new Date(Date.parse(iso)+9*3600000).toISOString().slice(0,10);
const grade=()=>false,REVIEW_INTERVAL_DAYS=[1,3,7];
const addJapanDays=(d,n)=>new Date(Date.parse(d+'T00:00:00Z')+n*86400000).toISOString().slice(0,10);
'''
checks = r'''
const assert=(v,m)=>{if(!v)throw Error(m)};
let seed=20261110;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
for(let n=0;n<200;n++){
 let t=Date.UTC(2025,0,1);const events=[];
 for(let i=0;i<200;i++){t+=Math.floor(rand()*7*86400000);events.push({id:String(i).padStart(8,'0'),questionId:rand()<.5?'q':'q-review-v1',variant:rand()<.2?'kanji':'normal',at:new Date(t).toISOString(),correct:rand()<.7,hint:rand()<.3});}
 const now=t+86400000,original=JSON.stringify(events);
 assert(JSON.stringify(retention(events,now))===JSON.stringify(baselineRetention(events,now)),'projection changed '+n);
 assert(JSON.stringify(events)===original,'input mutated');
}
let calls=0;const originalWeaknesses=weaknesses;weaknesses=(...args)=>{calls++;return originalWeaknesses(...args)};
const many=Array.from({length:10000},(_,i)=>({id:String(i),questionId:'q',variant:'normal',at:new Date(Date.UTC(2020,0,1)+i*86400000).toISOString(),correct:true,hint:i%2===0}));
retention(many,Date.UTC(2050,0,1));assert(calls===0,'correct-only history rescanned');
const sameDay=many.map((e,i)=>({...e,correct:false,at:new Date(Date.UTC(2020,0,1)+i).toISOString()}));
retention(sameDay,Date.UTC(2050,0,1));assert(calls===0,'one wrong day rescanned');
console.log('retention projection: 200 histories equivalent; 20,000 records avoid growing rescans');
'''
subprocess.run(['node'],input=setup+weak+retention+BASELINE+checks,text=True,check=True,cwd=ROOT)

server=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for name in ('onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html'):
   context=browser.new_context(viewport={'width':768,'height':1024},timezone_id='America/Los_Angeles')
   context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
   page=context.new_page();errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.route('https://**/*',lambda r:r.abort())
   page.clock.install(time=datetime(2026,11,9,14,59,45,tzinfo=timezone.utc))
   page.goto(f'http://127.0.0.1:{server.server_port}/{name}')
   page.evaluate(r'''() => {
    const assert=(ok,m)=>{if(!ok)throw Error(m)};
    window.isScience=typeof state!=='undefined';
    const q=QUESTIONS.find(q=>q.type===(isScience?'number':'text'));
    window.makeClockEvent=(at,correct=false)=>{
     const response=correct?q.answer:isScience?q.answer+1:'ダミー誤答';
     return isScience?validateEvent({id:uid(),sessionId:'clock-regression',questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response,inputRaw:String(response),expected:q.answer,correct,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed:false,mode:'normal',explanation:q.explanation}):
      validateEvent({id:uuid(),sessionId:'clock-regression',questionId:q.id,...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),version:VERSION,unit:q.unit,course:q.course,question:q.prompt,response,expected:q.answer,explanation:q.explanation,correct,variant:'normal',mode:'normal',hint:false,reflection:'',at,offset:0,day:day(at,0)});
    };
    const es=[makeClockEvent('2026-11-06T00:00:00.000Z'),makeClockEvent('2026-11-07T00:00:00.000Z'),makeClockEvent('2026-11-09T00:00:00.000Z',true)];
    if(isScience)state.events=es;else data.events=es;
    if(isScience){const oldCount=count;count=1000;const qs=scienceDaily();assert(qs.length===QUESTIONS.length,'science candidate shortage uses available');assert(new Set(qs.map(q=>q.id)).size===qs.length,'science shortage dedup');count=oldCount;}
    else{const qs=dailyQuestions({...prefs,count:1000});assert(qs.length===candidates('normal').length,'social candidate shortage uses available');assert(new Set(qs.map(q=>q.originId||q.id)).size===qs.length,'social shortage dedup');}
    home();
    assert(document.querySelector('#daily-five').textContent.includes('5問'),'default five');
    assert((isScience?scienceDue():dueReviews()).length===0,'before JST midnight');
    assert(document.body.textContent.includes('今日の再確認：0'),'before midnight display');
   }''')
   page.clock.fast_forward(30001)
   assert page.locator('body').inner_text().count('今日の再確認：1') >= 1, name
   page.evaluate('''() => {if(isScience){view='analysis';analysis();}else{screen='parent';parent();}}''')
   assert '今日の再確認 1' in page.locator('body').inner_text(), name
   # Focus and visibility restoration repaint summary views, even if the browser
   # suspended its timers. Refresh must not interrupt an in-progress answer.
   page.clock.set_fixed_time(datetime(2026,11,9,14,59,45,tzinfo=timezone.utc))
   page.evaluate("window.dispatchEvent(new Event('focus'))")
   assert '今日の再確認 0' in page.locator('body').inner_text(), name
   page.clock.set_fixed_time(datetime(2026,11,9,15,0,1,tzinfo=timezone.utc))
   page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
   assert '今日の再確認 1' in page.locator('body').inner_text(), name
   page.evaluate("() => {if(isScience)view='home';else screen='home';home();}")
   page.locator('#daily-five').click()
   response=page.locator('#numeric' if name=='yuika-review-v2.html' else '#response')
   response.fill('123')
   page.evaluate("refreshPracticeDate(true)")
   assert response.input_value()=='123', name
   page.evaluate(r'''() => {
    const assert=(ok,m)=>{if(!ok)throw Error(m)};
    if(isScience){view='home';session=null;}else{screen='home';run=null;}
    for(const flag of ['blocked','dirty']){
     if(flag==='blocked')blocked=true;else dirty=true;
     home();assert(document.querySelector('#daily-five').disabled,'disabled '+flag);
     if(isScience){assert(!scienceDaily().length,'no science fallback');start('daily');assert(view==='home','science start blocked');}
     else{assert(!dailyQuestions().length,'no social fallback');startDaily();assert(screen==='home','social start blocked');}
     blocked=false;dirty=false;
    }
    window.clockOriginal=JSON.stringify(isScience?state:data);
   }''')
   page.clock.set_fixed_time(datetime(2026,11,7,1,tzinfo=timezone.utc))
   page.evaluate(r'''() => {
    const assert=(ok,m)=>{if(!ok)throw Error(m)};
    home();assert(practiceClockIssue(),'future timestamps detected');
    assert(document.querySelector('#daily-five').disabled,'clock disables daily');
    assert(document.body.textContent.includes('端末の日付と時刻を確認'),'clock notice');
    assert(!practiceWeaknesses().length,'clock stops weakness projection');
    if(isScience){assert(!scienceWeak().length&&!scienceDue().length&&!scienceDaily().length,'science clock guards');start('daily');assert(view==='home','science direct start clock guard');}
    else{assert(!additional().length&&!dueReviews().length&&!dailyQuestions().length,'social clock guards');startDaily();assert(screen==='home','social direct start clock guard');}
    assert(JSON.stringify(isScience?state:data)===clockOriginal,'clock warning preserves records');
    const future=Date.now()+5*60000;
    assert(!practiceClockIssue([{at:new Date(future).toISOString()}]),'5-minute tolerance');
    assert(practiceClockIssue([{at:new Date(future+1).toISOString()}]),'over 5-minute guard');
    assert(!practiceClockIssue(data.events,Date.parse('2026-11-10T00:00:00Z')),'explicit time honoured');
    if(isScience){view='analysis';analysis();}else{screen='parent';parent();}
    assert(document.body.textContent.includes('端末の日付と時刻を確認'),'parent clock notice');
   }''')
   page.clock.set_fixed_time(datetime(2026,11,10,1,tzinfo=timezone.utc))
   page.evaluate("window.dispatchEvent(new Event('focus'))")
   assert '端末の日付と時刻を確認' not in page.locator('#science-summary' if name=='yuika-review-v2.html' else '#adaptive-summary').inner_text(), name
   assert '今日の再確認 1' in page.locator('body').inner_text(), name
   assert not errors, (name,errors)
   context.close()
  browser.close()
 print('state_review_regression: all checks passed (4 apps, JST refresh, clock safety, blocked starts, replay equivalence and cost)')
finally:
 server.shutdown()
