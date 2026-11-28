"""Independent endpoint-captured report lifecycle QA; synthetic fresh contexts only."""
import json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright, expect
ROOT=Path(sys.argv[1]).resolve(); OUT=Path(__file__).resolve().parent
MOCK='https://independent-qa.example.workers.dev'
CONFIG={'enabled':True,'endpoint':MOCK,'token':'synthetic-independent-qa','recipient':'parent@example.test'}
CONFIG_KEY='yuika-mail-config-v1'
JOBS="Object.keys(localStorage).filter(k=>k.startsWith('yuika-mail-job-v1:')).map(k=>JSON.parse(localStorage[k]))"
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/'
started=time.monotonic();result={'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'started_at':datetime.now(timezone.utc).isoformat(),'contexts':[],'external_requests_aborted':0,'unexpected_posts':[],'page_errors':[]}
def answer(p,science):
 q=p.evaluate('session.questions[session.index]' if science else 'run.qs[run.index]')
 if science:
  if q['type']=='number':p.locator('#numeric').fill(str(q['answer']))
  elif q.get('diagram'):p.locator(f'[data-fin="{q["answer"]}"]').click()
  elif q['type']=='recall':p.locator('#recall-text').fill(q['answer'])
  else:p.locator(f'[data-choice="{q["options"].index(q["answer"])}"]').click()
 else:
  if p.locator('#response').count():p.locator('#response').fill(q['answer'])
  else:
   idx=p.evaluate('run.options.indexOf(run.qs[run.index].answer)')
   p.locator(f'[data-choice="{idx}"]').click()
 p.locator('#check').click();expect(p.locator('#next')).to_be_visible()
def snapshot(p):return p.evaluate('Object.fromEntries(Object.entries(localStorage))')
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH','/usr/bin/chromium'))
  for filename,query,science,expected_count in [('onin-review.html','',False,5),('yuika-review-v2.html','?unit=てこのつり合い',True,5),('edo-review.html','',True,5),('mock-focus-review.html','?subject=math',False,5)]:
   for parent in [False,True]:
    ctx=browser.new_context(viewport={'width':768,'height':1024},is_mobile=True,has_touch=True,timezone_id='Asia/Tokyo')
    ctx.add_init_script(path=ROOT/'tests/seed_random.js');p=ctx.new_page();posts=[];dialogs=[];decision={'accept':True}
    p.set_default_timeout(10000)
    p.on('pageerror',lambda e:result['page_errors'].append(str(e)))
    def dialog(d):
     dialogs.append({'accepted':decision['accept'],'message':d.message})
     d.accept() if decision['accept'] else d.dismiss()
    p.on('dialog',dialog)
    def route(r):
     req=r.request
     if req.url==base+'__independent_fixture__':r.fulfill(body='<!doctype html><title>synthetic fixture</title>',content_type='text/html')
     elif req.url==MOCK+'/reports' and req.method=='POST':
      payload=req.post_data_json
      jobs=p.evaluate(JOBS);pending=[j for j in jobs if j['id']==payload['id']]
      assert len(pending)==1 and pending[0]['status']=='pending' and pending[0]['report']==payload
      posts.append(payload);r.fulfill(json={'accepted':True},headers={'Access-Control-Allow-Origin':'*'})
     elif req.url.startswith(base) and req.method=='GET':r.continue_()
     else:
      result['external_requests_aborted']+=1
      if req.method=='POST':result['unexpected_posts'].append({'url':req.url,'method':req.method})
      r.abort()
    ctx.route('**/*',route);p.goto(base+'__independent_fixture__')
    p.evaluate('([k,c])=>{localStorage.setItem(k,JSON.stringify(c));localStorage.setItem("independent-child-sentinel","synthetic-preserve-byte-for-byte")}',[CONFIG_KEY,CONFIG])
    child_before=snapshot(p)
    url=base+filename+query+('&' if query else '?')+'parent-check=1' if parent else base+filename+query
    p.goto(url)
    if filename=='mock-focus-review.html':
     assert p.locator('.theme-panel,[data-ui-theme],#theme-kamakura,#theme-standard').count()==0
     assert p.evaluate("typeof window.YuikaTheme")== 'undefined'
    if parent:
     expect(p.locator('#parent-check-banner')).to_be_visible()
     p.evaluate('c=>YuikaParent.storage.setItem("yuika-mail-config-v1",JSON.stringify(c))',CONFIG)
    events='state.events' if science else 'data.events';sess='session' if science else 'run'
    assert p.evaluate(events+'.length')==0
    # Empty end must neither save an answer nor queue a notification.
    p.locator('#start').click();p.locator('#end').click()
    expect(p.locator('#start')).to_be_visible();assert p.evaluate(events+'.length')==0 and not posts and not p.evaluate(JOBS)
    # Cancel an answered session's end, then accept: report exactly the answered prefix.
    p.locator('#start').click();answer(p,science)
    event=p.evaluate(events+'[0]');assert p.evaluate(events+'.length')==1 and not posts
    sid=p.evaluate(sess+'.id');decision['accept']=False;p.locator('[data-view="home"]').click()
    expect(p.locator('#next')).to_be_visible();assert p.evaluate(sess+'.id')==sid and p.evaluate(events)==[event] and not posts and not p.evaluate(JOBS)
    assert dialogs[-1]['accepted'] is False
    decision['accept']=True;p.locator('#end').click()
    if filename=='yuika-review-v2.html':
     expect(p.locator('#return')).to_be_visible();p.locator('#return').click()
    expect(p.locator('#start')).to_be_visible()
    if not parent:
     expect(p.locator('#yuika-mail-status')).to_contain_text('受け付けました')
     assert len(posts)==1 and posts[0]['total']==len(posts[0]['answers'])==posts[0]['correct']==1
     # Explicit duplicate enqueue after accepted partial report must remain one delivery/job.
     p.evaluate('r=>{YuikaReports.enqueue(r);YuikaReports.enqueue(r)}',posts[0])
     assert len(p.evaluate(JOBS))==len(posts)==1
    else:assert snapshot(p)==child_before
    p.reload();assert p.evaluate(events)==[event] and len(posts)==(0 if parent else 1)
    # PR12 own daily-five entry; do not import PR10 actual-count/reasoned-review copy.
    if science and filename=='yuika-review-v2.html':
     p.locator('#unit').select_option('てこのつり合い');p.locator('[data-count="5"]').click()
    elif p.locator('[data-count="5"]').count():p.locator('[data-count="5"]').click()
    expect(p.locator('#daily-five')).to_be_visible()
    p.locator('#daily-five').click()
    actual=p.evaluate(sess+('.questions.length' if science else '.qs.length'));assert actual==expected_count
    before=len(posts)
    for i in range(actual):
     answer(p,science);assert len(posts)==before
     p.locator('#next').click()
    assert p.evaluate(events+'.length')==1+actual
    if not parent:
     expect(p.locator('#yuika-mail-status')).to_contain_text('受け付けました')
     assert len(posts)==2 and posts[-1]['total']==len(posts[-1]['answers'])==posts[-1]['correct']==actual
     assert posts[-1]['mode']=='今日の5問'
    p.evaluate('result();result()');p.reload()
    assert len(posts)==(0 if parent else 2) and len(p.evaluate(JOBS))==len(posts)
    assert p.evaluate(events+'.length')==1+actual and p.evaluate(events+'[0]')==event
    if parent:
     assert snapshot(p)==child_before
     assert p.evaluate("Object.keys(sessionStorage).every(k=>!k.includes('yuika-mail-job-v1:'))")
     p.locator('#parent-exit').click();assert snapshot(p)==child_before
    result['contexts'].append({'page':filename,'parent':parent,'empty_end':True,'cancel_retains_answer_session_no_report':True,'partial_answers':1,'complete_answers':actual,'captured_reports':len(posts),'job_count':len(p.evaluate(JOBS)),'duplicate_report_and_reload_stable':True,'events_preserved_on_reload':True,'child_localStorage_byte_preserved':True if parent else None,'dialogs':dialogs})
    p.screenshot(path=str(OUT/f'{filename[:-5]}-{"parent-exited" if parent else "normal"}.png'))
    ctx.close();print('PASS',filename,'parent' if parent else 'normal',flush=True)
  browser.close()
 assert not result['unexpected_posts'] and not result['page_errors'],result
 result['result']='passed'
finally:
 result['finished_at']=datetime.now(timezone.utc).isoformat();result['seconds']=round(time.monotonic()-started,3)
 (OUT/'report-probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 srv.shutdown();srv.server_close()
