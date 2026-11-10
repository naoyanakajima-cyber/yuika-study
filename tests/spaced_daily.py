"""Retention replay, JST boundaries, migration and daily entry; synthetic records."""
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for name in ('onin-review.html','kamakura-review.html','heian-review.html'):
   context=browser.new_context(viewport={'width':768,'height':1024})
   context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
   page=context.new_page();errors=[]
   page.on('pageerror',lambda e: errors.append(str(e)))
   page.route('https://**/*',lambda route:route.abort())
   page.goto(f'http://127.0.0.1:{srv.server_port}/{name}')
   page.evaluate('''() => {
    const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
    const q=QUESTIONS.find(q=>q.type==='text');
    window.mk=(at,correct=false,hint=false,question=q,variant='normal')=>validateEvent({
     id:uuid(),sessionId:'synthetic-retention',questionId:question.id,
     ...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),version:VERSION,
     unit:question.unit,course:question.course,question:promptOf(question,variant),
     response:correct?expectedOf(question,variant):'ダミー誤答',expected:expectedOf(question,variant),explanation:question.explanation,
     correct,variant,mode:'normal',hint,reflection:'',at,offset:0,day:day(at,0)});
    const a=mk('2026-09-01T14:59:00.000Z'),b=mk('2026-09-01T15:00:00.000Z');
    const state=es=>retention(es,Date.parse('2026-11-10T00:00:00Z'))[0];
    assert(state([a,b]).status==='weak','JST distinct days trigger');
    assert(!retention([a,mk('2026-09-01T14:59:59.000Z')]).length,'same Japan day does not trigger');
    const c=mk('2026-09-02T14:59:00.000Z',true,false,EXTRA.get(q.id));
    assert(state([a,b,c]).status==='waiting'&&state([a,b,c]).due==='2026-09-03','practice to waiting');
    assert(!weaknesses([a,b,c]).length&&state([a,b,c]).status==='waiting','retention survives 30 day expiry');
    assert(state([a,b,c,mk('2026-09-02T14:59:59.000Z',true)]).stage===0,'early success no advance');
    const d=mk('2026-09-02T15:00:00.000Z',true);
    assert(state([a,b,c,d]).due==='2026-09-05','day one then day three');
    assert(state([a,b,c,d,mk('2026-09-04T15:00:00.000Z',true,true)]).stage===1,'hint no advance');
    const e=mk('2026-09-04T15:00:00.000Z',true),f=mk('2026-09-08T15:00:00.000Z',true);
    assert(state([a,b,c,d,e]).due==='2026-09-09','day seven');
    assert(state([a,b,c,d,e,f]).status==='retained','retained after three dates');
    const failed=mk('2026-11-09T00:00:00.000Z');
    assert(state([a,b,c,failed]).status==='weak','error returns weak');
    assert(practiceWeaknesses([a,b,c,failed]).length===1,'old weak restored outside rolling window');
    assert(state([a,b,c,mk('2026-11-09T00:00:00.000Z',true)]).stage===1,'late success only one stage');
    assert(retention([a,b,c,c]).length===1,'duplicate events');
    data.events=[a,b,c];const legacy=JSON.stringify(data);localStorage.setItem(KEY,legacy);load();
    assert(JSON.stringify(data)===legacy&&localStorage.getItem(KEY)===legacy,'legacy bytes and events untouched');
    save();assert(validate(JSON.parse(localStorage.getItem(KEY))).events.length===3,'save and validate legacy');
    const q2=QUESTIONS.find(o=>o.type==='text'&&o.id!==q.id);
    data.events.push(mk('2026-11-07T00:00:00.000Z',false,false,q2),mk('2026-11-08T00:00:00.000Z',false,false,q2));save();
    const qs=dailyQuestions();assert(qs.length===5,'default five');
    assert(qs[0].originId===q.id&&qs[1].originId===q2.id,'due then weak then normal');
    assert(new Set(qs.map(q=>q.originId||q.id)).size===5,'origin deduplication');
    assert(dailyQuestions({...prefs,unit:'missing'}).length===0,'filters');
    parent();assert(document.querySelector('#retention-summary').textContent.includes('今日の再確認 1件'),'all variants due summary');home();
    localStorage.setItem('synthetic-other-key','preserved');
   }''')
   page.locator('#unit').select_option(page.evaluate('UNITS[0]'))
   page.locator('#variant').select_option('kanji')
   page.locator('[data-count="10"]').click()
   expected=page.evaluate('({...prefs})')
   page.reload()
   assert page.evaluate('({...prefs})')==expected
   assert page.locator('[data-count="10"]').get_attribute('aria-pressed')=='true'
   page.locator('#daily-five').click()
   assert page.evaluate("run.mode==='daily'&&run.qs.length===Math.min(10,candidates('normal').length)")
   page.locator('#response').fill(page.evaluate('expectedOf(run.qs[0],run.variant)'))
   page.locator('#check').click()
   assert page.evaluate("data.events.at(-1).mode==='daily'&&data.events.at(-1).correct")
   page.reload()
   assert page.evaluate("data.events.at(-1).mode==='daily'")
   page.goto(f'http://127.0.0.1:{srv.server_port}/{name}?daily=1')
   assert page.evaluate("run.mode==='daily'&&run.qs.length===Math.min(10,candidates('normal').length)")
   assert page.evaluate("localStorage.getItem('synthetic-other-key')")=='preserved'
   # A fresh page in the same context models closing and reopening the application.
   page.close();page=context.new_page();page.goto(f'http://127.0.0.1:{srv.server_port}/{name}')
   assert page.evaluate('({...prefs})')==expected
   assert not errors,errors
   context.close()
  browser.close()
 print('spaced_daily: all checks passed (3 apps, state transitions, JST, migration, daily priority, preference reopen)')
finally:
 srv.shutdown()
