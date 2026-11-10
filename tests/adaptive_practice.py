"""Synthetic analysis, generation, persistence and CSP-preview integration tests."""
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT

srv = ThreadingHTTPServer(('127.0.0.1', 0), partial(PreviewHandler, directory=str(ROOT)))
Thread(target=srv.serve_forever, daemon=True).start()
try:
 with sync_playwright() as pw:
  browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for name in ('onin-review.html', 'kamakura-review.html'):
   context = browser.new_context(viewport={'width':768,'height':1024})
   context.add_init_script(path=str(ROOT / 'tests/seed_random.js'))
   page = context.new_page()
   errors=[]
   page.on('pageerror', lambda e: errors.append(str(e)))
   page.route('https://**/*', lambda route: route.abort())
   page.goto(f'http://127.0.0.1:{srv.server_port}/{name}')
   result = page.evaluate('''() => {
    const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
    const q=QUESTIONS.find(q=>q.type==='text'&&canYomi(q)),now=Date.now();
    const mk=(days,correct=false,variant='normal',hint=false,question=q)=>{
     const at=new Date(now-days*86400000).toISOString();
     return validateEvent({id:uuid(),sessionId:'synthetic-session',questionId:question.id,unitId:UNIT_ID,version:VERSION,
      unit:question.unit,course:question.course,question:promptOf(question,variant),response:correct?expectedOf(question,variant):'ダミー誤答',
      expected:expectedOf(question,variant),explanation:question.explanation,correct,variant,mode:'normal',hint,at,offset:0,day:day(at,0)});
    };
    const a=mk(2),b=mk(1,false,'normal',true),es=[a,b];
    assert(!weaknesses([]).length,'empty');
    assert(!weaknesses([a,a]).length,'duplicate IDs');
    assert(!weaknesses([a,mk(2)]).length,'same day');
    assert(!weaknesses([mk(32),b]).length,'old record');
    assert(!weaknesses([mk(-2),b]).length,'future');
    assert(!weaknesses([a,mk(1,false,'kanji')]).length,'separate variants');
    assert(!weaknesses([...es,mk(0,true)]).length,'recovery');
    const r=weaknesses(es)[0];
    assert(r.unit===q.unit&&r.wrong===2&&r.hintCount===1,'evidence');
    data.events=es;save();home();
    const rows=additional(),extra=rows[0].q;
    assert(rows.length===1&&extra.originId===q.id,'generation');
    for(const k of ['answer','explanation','source','hint','pitfall','unit','course','type'])assert(extra[k]===q[k],k);
    assert(JSON.stringify(additional())===JSON.stringify(rows),'stable IDs/dedup');
    assert(!additional({...prefs,unit:'absent'}).length,'filter');
    assert(document.querySelector('#adaptive details'),'preview');
    return {id:extra.id,baseCount:QUESTIONS.length};
   }''')
   page.locator('[data-mode="adaptive"]').click()
   assert page.evaluate('run.qs.length') == 1
   q=page.evaluate('run.qs[0]')
   assert q['id']==result['id']
   page.locator('#response').fill(q['answer'])
   page.locator('#check').click()
   assert page.evaluate('data.events.at(-1).correct')
   # Do not complete a challenge or enqueue a notification.
   page.reload()
   assert not page.evaluate('blocked')
   assert page.evaluate('data.events.length') == 3
   assert page.evaluate('validate(JSON.parse(localStorage.getItem(KEY))).events.length') == 3
   assert page.evaluate('QUESTIONS.length') == result['baseCount']
   assert not page.evaluate('additional().length')
   assert not errors, errors
   context.close()
  browser.close()
 print('adaptive_practice: all checks passed (2 apps, synthetic records, CSP preview)')
finally:
 srv.shutdown()
