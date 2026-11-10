"""Daily use regressions: synthetic histories only, all three standalone apps."""
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
  for name in ('onin-review.html', 'kamakura-review.html', 'heian-review.html'):
   context = browser.new_context(viewport={'width':768,'height':1024})
   page = context.new_page()
   errors=[]
   page.on('pageerror', lambda e: errors.append(str(e)))
   page.route('https://**/*', lambda route: route.abort())
   page.goto(f'http://127.0.0.1:{srv.server_port}/{name}')
   assert 'まだ回答記録' in page.locator('#adaptive').inner_text()
   info=page.evaluate('''() => {
    const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
    const now=Date.now(),q=QUESTIONS.find(q=>q.type==='text');
    window.dailyQ=q;
    window.dailyEvent=(days,correct=false,hint=false,question=q)=>{
     const at=new Date(now-days*86400000).toISOString();
     return validateEvent({id:uuid(),sessionId:'synthetic-daily',questionId:question.id,
      ...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),version:VERSION,
      unit:question.unit,course:question.course,question:promptOf(question,'normal'),
      response:correct?question.answer:'ダミー誤答',expected:question.answer,explanation:question.explanation,
      correct,variant:'normal',mode:'normal',hint,reflection:'',at,offset:0,day:day(at,0)});
    };
    const a=dailyEvent(2),b=dailyEvent(1),hint=dailyEvent(0,true,true);
    assert(weaknesses([a,b,hint]).length===1,'hint correct retains practice');
    assert(weaknesses([a,b,dailyEvent(1-0.001,true,true)]).length===1,'hint retry on triggering day retains practice');
    assert(!weaknesses([a,b,dailyEvent(0,true)]).length,'unassisted recovery');
    assert(weaknesses([a,b,dailyEvent(0,true)],now,true)[0].recovered,'recovery summary');
    assert(weaknesses([a,b,dailyEvent(1-0.001,true)],now,true)[0].recovered,'same day recovery summary');
    assert(weaknesses([a,b,dailyEvent(0.5,true),dailyEvent(0)]).length===1,'later error reactivates');
    // Every registered extra preserves grading and JSON validation, including Heian structures.
    for(const extra of EXTRA.values()){
     const response=extra.type==='structure'?{steps:extra.items.map((_,i)=>i),fills:extra.blanks.map(b=>b.answer)}:extra.answer;
     const at=new Date(now).toISOString();
     validateEvent({...dailyEvent(0,true,false,q),questionId:extra.id,unit:extra.unit,course:extra.course,
      question:promptOf(extra,'normal'),expected:extra.answer,explanation:extra.explanation,response,at});
    }
    localStorage.setItem('synthetic-other-unit','keep');
    data.events=[a,b,hint];save();home();
    assert(additional()[0].lastCorrect&&additional()[0].lastHint,'hint evidence');
    assert(document.querySelector('#adaptive').textContent.includes('選んだ理由'),'explanation');
    assert(document.querySelector('#adaptive').textContent.includes('ヒント付き正解'),'hint label');
    adaptiveLevel='3';assert(!additional().length,'level excludes basic');adaptiveLevel='all';
    const es=[];for(const question of QUESTIONS.filter(q=>q.type==='text').slice(0,12))es.push(dailyEvent(2,false,false,question),dailyEvent(1,false,false,question));
    assert(additional(prefs,es).length===10,'candidate cap');
    const saved=data.events;data.events=es;prefs.count=5;start('adaptive');
    assert(run.qs.length===5,'session respects selected count');
    assert(new Set(run.qs.map(q=>q.id)).size===5,'no duplicate questions');
    run=null;screen='home';data.events=saved;
    const q2=QUESTIONS.find(o=>o.type==='text'&&o.id!==q.id);
    assert(!additional({...prefs,unit:'missing'}).length,'unit filter');
    assert(!additional({...prefs,course:'missing'}).length,'course filter');
    assert(validate(JSON.parse(localStorage.getItem(KEY))).events.length===3,'historical compatibility');
    parent();assert(document.querySelector('#adaptive-summary').textContent.includes('要確認 1論点'),'parent summary');home();
    return {id:EXTRA.get(q.id).id,answer:q.answer,key:KEY,count:QUESTIONS.length};
   }''')
   page.select_option('#adaptive-level','3')
   assert page.locator('[data-mode="adaptive"]').is_disabled()
   page.select_option('#adaptive-level','all')
   page.locator('[data-mode="adaptive"]').click()
   assert page.evaluate('run.qs.length') == 1
   page.locator('#response').fill(info['answer'])
   page.locator('#check').click()
   page.reload()
   assert page.evaluate('data.events.length') == 4
   assert not page.evaluate('additional().length')
   page.evaluate('parent()')
   assert 'ヒントなしで正解 1論点' in page.locator('#adaptive-summary').inner_text()
   page.evaluate('home()')
   assert page.evaluate('QUESTIONS.length') == info['count']
   assert page.evaluate("localStorage.getItem('synthetic-other-unit')") == 'keep'
   # Protect broken original bytes, and disable misleading analysis from empty memory.
   page.evaluate("localStorage.setItem(KEY, '{broken-synthetic')")
   page.reload()
   assert page.evaluate('blocked')
   assert page.locator('[data-mode="adaptive"]').is_disabled()
   assert '判定を休止' in page.locator('#adaptive').inner_text()
   page.evaluate('save()')
   assert page.evaluate('localStorage.getItem(KEY)') == '{broken-synthetic'
   page.evaluate('parent()')
   assert '判定を休止' in page.locator('#adaptive-summary').inner_text()
   page.evaluate('''() => {
    localStorage.removeItem(KEY);data=empty();blocked=false;
    Storage.prototype.getItem=function(){throw new DOMException('synthetic denied','SecurityError');};
    load();home();
   }''')
   assert page.evaluate('blocked')
   assert page.locator('[data-mode="adaptive"]').is_disabled()
   assert '判定を休止' in page.locator('#adaptive').inner_text()
   assert not errors, errors
   context.close()
  browser.close()
 print('adaptive_daily: all checks passed (3 apps, levels, explanations, hint/recovery, summaries, caps, corrupt storage, persistence)')
finally:
 srv.shutdown()
