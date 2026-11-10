"""Independent-review regressions; only synthetic histories and CSP loopback."""
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT

srv = ThreadingHTTPServer(('127.0.0.1', 0), partial(PreviewHandler, directory=str(ROOT)))
Thread(target=srv.serve_forever, daemon=True).start()
try:
 with sync_playwright() as pw:
  browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for timezone in ('Asia/Tokyo', 'America/Los_Angeles'):
   for name in ('onin-review.html', 'kamakura-review.html', 'heian-review.html'):
    context = browser.new_context(viewport={'width':768,'height':1024}, timezone_id=timezone)
    context.add_init_script(path=str(ROOT / 'tests/seed_random.js'))
    page = context.new_page()
    errors=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.route('https://**/*', lambda route: route.abort())
    page.goto(f'http://127.0.0.1:{srv.server_port}/{name}')
    page.evaluate('''() => {
     const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
     const now=Date.parse('2026-11-10T03:00:00.000Z'), q=QUESTIONS.find(q=>q.type==='text');
     const mk=(at,correct=false,hint=false,question=q,offset=0)=>validateEvent({
      id:uuid(),sessionId:'quality-synthetic',questionId:question.id,version:VERSION,
      ...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),unit:question.unit,course:question.course,
      question:promptOf(question,'normal'),expected:question.answer,explanation:question.explanation,
      response:correct?(question.type==='structure'?{steps:question.items.map((_,i)=>i),fills:question.blanks.map(b=>b.answer)}:question.answer):
       question.type==='choice'?question.options.find(o=>o!==question.answer):
        question.type==='structure'?{steps:question.items.map((_,i)=>i).reverse(),fills:question.blanks.map(b=>b.answer)}:'ダミー誤答',
      correct,variant:'normal',mode:'normal',hint,reflection:'',at,offset,day:day(at,offset)});
     const a=mk('2026-11-08T14:59:00.000Z'),b=mk('2026-11-08T15:01:00.000Z');
     assert(a.day===b.day,'fixture UTC same day');
     assert(weaknesses([a,b],now).length===1,'JST midnight creates separate days');
     const c=mk('2026-11-08T01:00:00.000Z',false,false,q,840);
     const d=mk('2026-11-08T02:00:00.000Z',false,false,q,-840);
     assert(c.day!==d.day&&!weaknesses([c,d],now).length,'device dates cannot manufacture evidence');
     assert(adaptiveLabel(b.at).includes('日本時間')&&adaptiveLabel(b.at).includes('0:01'),'JST display');
     const at=delta=>new Date(now-delta).toISOString();
     const boundary=mk(at(30*86400000)),recent=mk(at(86400000));
     assert(weaknesses([boundary,recent],now).length===1,'30-day inclusive boundary');
     assert(!weaknesses([mk(at(30*86400000+1)),recent],now).length,'outside 30 days');
     assert(!weaknesses([mk(at(-1)),recent],now).length,'future millisecond excluded');
     const hints=[mk('2026-11-08T03:00:00.000Z',false,true),mk('2026-11-08T04:00:00.000Z'),recent];
     assert(weaknesses(hints,now)[0].hintCount===1,'earlier same-day hint retained');
     assert(!weaknesses([a,a],now).length,'duplicate cannot count as separate days');
     const recovered=mk(at(0),true,false,EXTRA.get(q.id));
     assert(!weaknesses([a,b,recovered],now).length,'extra recovers original');
     assert(weaknesses([a,b,recovered],now,true)[0].recovered,'recovery summary');
     const recoveryEarlier=mk(at(3600000),true),hintLater=mk(at(1800000),true,true);
     assert(!weaknesses([a,b,recoveryEarlier,hintLater],now).length,'hinted success after recovery cannot reactivate');
     assert(weaknesses([a,b,recoveryEarlier,hintLater],now,true)[0].recovered,'recovery status persists');
     assert(weaknesses([a,b,recoveryEarlier,mk(at(0))],now).length===1,'new error reactivates');
     const six=[6,5,4,3,2,1].map(n=>mk(at(n*86400000),n!==6));
     assert(!weaknesses(six,now).length,'only last five answering days');
     const before=JSON.stringify([a,b,recovered]);
     const validated=validate({...empty(),events:[a,b,recovered,recovered]});
     assert(validated.events.length===3,'import dedup');
     assert(JSON.stringify([a,b,recovered])===before,'analysis leaves historical fields unchanged');
     let conflict=false;try{validate({...empty(),events:[a,{...a,sessionId:'other-synthetic'}]});}catch(e){conflict=true;}
     assert(conflict,'conflicting duplicate rejected');
     data=validated;
     assert(grouped().size===1&&analysis().first.length===1,'canonical first observation');
     assert(!candidates('wrong').some(o=>o.id===q.id),'original wrong filter sees recovery');
     data.events=[recovered];home();
     assert(!candidates('unseen').some(o=>o.id===q.id),'extra-only record counts as seen');
     assert(document.querySelectorAll('.stat strong')[1].textContent.trim().startsWith('1'),'seen total maps origin');
     if(typeof UNIT_ID==='undefined'){
      for(const course of ['memory','pairs','flow','reason']){
       const question=QUESTIONS.find(o=>o.course===course);
       const rows=weaknesses([mk(at(2*86400000),false,false,question),mk(at(86400000),false,false,question)],now);
       assert(rows[0].level==={memory:1,pairs:2,flow:2,reason:3}[course],'course difficulty '+course);
       data.events=rows.length?[mk(at(2*86400000),false,false,question),mk(at(86400000),false,false,question)]:[];
       adaptiveLevel=String(rows[0].level);assert(additional(prefs,data.events,now).length===1,'difficulty includes course');
      }
     }
     adaptiveLevel='all';data=empty();dirty=false;blocked=false;save();home();
    }''')
    # Native select remains focusable after re-render (keyboard/Safari navigation).
    page.locator('#adaptive-level').focus()
    page.select_option('#adaptive-level','2')
    assert page.locator('#adaptive-level').evaluate('(el)=>el===document.activeElement')
    page.evaluate('''() => {
     const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
     localStorage.setItem(KEY,'{broken-synthetic');
     assert(!save()&&blocked&&broken==='{broken-synthetic','late corruption blocks analysis and preserves bytes');
     home();assert(!additional().length&&document.querySelector('[data-mode="adaptive"]').disabled,'analysis blocked');
     records();assert(document.querySelector('#broken'),'original bytes can be exported');
     assert(localStorage.getItem(KEY)==='{broken-synthetic','disk intact');
     localStorage.removeItem(KEY);data=empty();blocked=false;broken=null;dirty=false;
     const set=Storage.prototype.setItem;
     Storage.prototype.setItem=function(){throw new DOMException('synthetic full','QuotaExceededError');};
     assert(!save()&&dirty&&!additional().length,'quota failure pauses analysis');
     Storage.prototype.setItem=set;assert(save()&&!dirty&&!blocked,'explicit retry after storage recovery');
     window.dispatchEvent(new StorageEvent('storage',{key:KEY,newValue:'{broken-tab'}));
     assert(blocked&&broken==='{broken-tab'&&!additional().length,'cross-tab malformed record blocks analysis');
     // Invalid answer strings render only as text, never HTML.
     blocked=false;broken=null;dirty=false;data=empty();
     const q=QUESTIONS.find(q=>q.type==='text'),at=new Date().toISOString();
     data.events=[validateEvent({id:uuid(),sessionId:'xss-synthetic',questionId:q.id,version:VERSION,
      ...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),unit:q.unit,course:q.course,
      question:promptOf(q,'normal'),expected:q.answer,explanation:q.explanation,
      response:'<img src=x onerror="window.syntheticXSS=1">',correct:false,variant:'normal',mode:'normal',hint:false,reflection:'',at,offset:0,day:day(at,0)})];
     parent();assert(!window.syntheticXSS&&!document.querySelector('#history img'),'history escapes synthetic answer');
    }''')
    assert not errors, errors
    context.close()
  browser.close()
 print('adaptive_quality: all checks passed (3 apps x 2 timezones; JST, boundaries, hints, canonical history, storage, focus, XSS)')
finally:
 srv.shutdown()
