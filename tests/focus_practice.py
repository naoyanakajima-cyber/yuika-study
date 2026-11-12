"""All original questions in the real UI; synthetic retention, JSON and entry."""
import json
import os
import sys
import subprocess
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Quiet(PreviewHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  context=browser.new_context(viewport={'width':768,'height':1024});context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
  page=context.new_page();errors=[];external=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('https://**/*',lambda route:(external.append(route.request.url),route.abort()))
  page.goto(base+'mock-focus-review.html')
  expect(page.locator('h1')).to_have_text('模試の弱点対策')
  # Existing original storage is never read into this new dataset or overwritten.
  page.evaluate("localStorage.setItem('synthetic-other-key','preserved')")
  units=page.evaluate('UNITS')
  answered=set()
  for unit in units:
   page.locator('#unit').select_option(unit)
   page.locator('#start').click()
   n=page.evaluate('run.qs.length')
   for _ in range(n):
    q=page.evaluate('run.qs[run.index]');answered.add(q['id'])
    if 'table' in q:expect(page.locator('caption')).to_contain_text('架空')
    if 'diagram' in q:
     expect(page.locator('figure')).to_be_visible()
     if q['diagram']['kind']!='bar':expect(page.locator('svg[role=img]')).to_be_visible()
    if 'passage' in q:expect(page.locator('[aria-label="説明文"]')).to_be_visible()
    # Answer one wrong per field; all four choices go through the grading function.
    assert page.evaluate('(q)=>q.options.filter(o=>grade(q,o,"normal")).length',q)==1
    choice=q['options'][1] if _==0 else q['answer']
    idx=page.evaluate('(choice)=>run.options.indexOf(choice)',choice)
    page.locator(f'[data-choice="{idx}"]').click()
    page.locator('#check').click()
    expect(page.locator('#feedback')).to_contain_text(q['basis'])
    assert page.evaluate('data.events.at(-1).questionVersion')==1
    page.locator('#next').click()
   page.locator('#again').click()
  assert len(answered)==46 and page.evaluate('data.events.length')==46
  page.reload();assert page.evaluate('data.events.length')==46
  # Export and re-import an actual prototype JSON through the file chooser.
  page.locator('[data-view=records]').click()
  with page.expect_download() as item:page.locator('#export').click()
  packet=json.loads(Path(item.value.path()).read_text());assert len(packet['payload']['events'])==46
  page.locator('input[type=file]').set_input_files({'name':'synthetic-focus.json','mimeType':'application/json','buffer':json.dumps(packet,ensure_ascii=False).encode()})
  # The existing 46 events do not prove the asynchronous file read has finished.
  # Wait for importFile's success before replacing data or leaving records.
  expect(page.locator('#notice')).to_contain_text('試作へ読み込みました。')
  assert page.evaluate('data.events.length')==46
  # Every question can enter weakness -> waiting -> due -> retained.
  page.evaluate('''() => {
   const assert=(v,m)=>{if(!v)throw Error(m);};
   const now=Date.now(),today=japanDay(new Date(now).toISOString());
   const at=n=>new Date(Date.parse(today+'T03:00:00Z')+n*86400000).toISOString();
   window.focusMk=(q,n,correct=false)=>validateEvent({id:uuid(),sessionId:'synthetic-focus',questionId:q.id,questionVersion:1,unitId:UNIT_ID,version:VERSION,unit:q.unit,course:q.course,question:q.prompt,response:correct?q.answer:q.options.find(o=>o!==q.answer),expected:q.answer,explanation:q.explanation,correct,variant:'normal',mode:'normal',hint:false,at:at(n),offset:0,day:at(n).slice(0,10)});
   for(const q of QUESTIONS){
    const es=[focusMk(q,-10),focusMk(q,-9)];
    assert(weaknesses(es,now).length===1,'weakness '+q.id);
    assert(retention(es,now)[0].status==='weak','weak '+q.id);
    es.push(focusMk(q,-8,true));
    assert(retention(es,now)[0].status==='waiting','waiting '+q.id);
    assert(dueReviews({...prefs,unit:'all'},es,now).length===1,'due '+q.id);
    es.push(focusMk(q,-7,true),focusMk(q,-5,true),focusMk(q,-1,true));
    assert(retention(es,now)[0].status==='retained','retained '+q.id);
   }
   localStorage.removeItem(KEY);data=empty();prefs={count:5,course:'all',unit:'all',variant:'normal'};
   const a=QUESTIONS[0],b=QUESTIONS[1];
   data.events=[focusMk(a,-10),focusMk(a,-9),focusMk(a,-8,true),focusMk(b,-3),focusMk(b,-2)];save();
   const daily=dailyQuestions();
   assert(daily.length===5&&daily[0].originId===a.id&&daily[1].originId===b.id,'due/weak/normal order');
   assert(new Set(daily.map(q=>q.originId||q.id)).size===5,'dedup');
  }''')
  page.locator('[data-view=home]').click()
  expect(page.locator('#daily-five')).to_be_visible()
  page.locator('#daily-five').click();assert page.evaluate("run.mode==='daily' && run.qs.length===5")
  # Existing index uses React/Babel; only its public dependencies are fulfilled.
  assets={}
  for path in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
   url='https://unpkg.com/'+path
   assets[url]=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',url])
  page.route('https://unpkg.com/**',lambda r:r.fulfill(body=assets[r.request.url],content_type='application/javascript'))
  page.goto(base+'index.html')
  page.get_by_role('button',name='今日の5問をはじめる',exact=True).click()
  page.wait_for_url('**/mock-focus-review.html?daily=1')
  assert page.evaluate("run.mode==='daily' && run.qs.length===5")
  assert page.evaluate("localStorage.getItem('synthetic-other-key')")=='preserved'
  assert not errors,errors
  # This page contains no notification runtime; index dependencies were aborted.
  assert not any('workers.dev' in url or 'resend' in url for url in external),external
  browser.close()
 print('focus_practice: all 46 UI questions, diagrams/tables, versioned JSON, retention, daily entry PASS')
finally:
 server.shutdown()
