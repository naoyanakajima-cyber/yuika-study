"""Independent synthetic recommendation boundary probe; no real history/network."""
import json, os, subprocess, traceback
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect
ROOT=Path('/workspace/yuika-rev-current-20261114'); OUT=Path('/tmp/yuika-rev-current-qa')
NOW=datetime(2030,1,3,tzinfo=timezone.utc)
class Quiet(SimpleHTTPRequestHandler):
 posts=0
 def log_message(self,*args):pass
 def do_POST(self):type(self).posts+=1;self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start(); BASE=f'http://127.0.0.1:{srv.server_port}/'
SEED="""at=>{const q=QUESTIONS.find(q=>q.type==='text'),v='normal'; const e=validateEvent({id:'qa-synthetic-wrong',sessionId:'qa-synthetic-session',questionId:q.id,questionVersion:1,unitId:UNIT_ID,version:VERSION,unit:q.unit,course:q.course,question:promptOf(q,v),response:'合成の誤答',expected:expectedOf(q,v),explanation:q.explanation,correct:false,variant:v,mode:'normal',hint:false,at,offset:0,day:day(at,0)});data={...empty(),events:[e]};YuikaParent.storage.setItem(KEY,JSON.stringify(data));go('home');return q.id;}"""
SNAP='JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))'
rows=[];errors=[];outgoing=[];failure=None
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for app in ('onin-review.html','kamakura-review.html'):
   for scenario in ('normal','parent','blocked','future','quota'):
    ctx=browser.new_context(viewport={'width':768,'height':1024},timezone_id='UTC')
    def route(r):
     if r.request.method=='GET' and r.request.url.startswith(BASE):r.continue_()
     else:outgoing.append({'method':r.request.method,'url':r.request.url});r.abort()
    ctx.route('**/*',route);p=ctx.new_page();p.clock.set_fixed_time(NOW);p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
    # Start same-origin neutral fixture before seeding legacy sentinels, no app mounted.
    ctx.route(BASE+'qa-fixture',lambda r:r.fulfill(content_type='text/html',body='<!doctype html><title>synthetic fixture</title>'))
    p.goto(BASE+'qa-fixture');p.evaluate("localStorage.setItem('qa-unrelated','synthetic-keep');localStorage.setItem('yuika-social-540-27-v1','synthetic-legacy-onin');localStorage.setItem('yuika-social-540-25-v1','synthetic-legacy-kamakura')")
    original=p.evaluate(SNAP);p.goto(BASE+app+('?parent-check=1' if scenario=='parent' else ''))
    p.evaluate(SEED,'2030-01-03T00:10:00.000Z' if scenario=='future' else '2030-01-02T23:00:00.000Z')
    if scenario=='blocked':
     p.evaluate("YuikaParent.storage.setItem(KEY,'{synthetic-broken')");p.reload()
    if scenario in ('blocked','future'):
     expect(p.locator('#recommended-start')).to_be_disabled()
     before=p.evaluate('JSON.stringify({screen,run,raw:YuikaParent.storage.getItem(KEY)})')
     p.evaluate('startRecommended()')
     assert p.evaluate('JSON.stringify({screen,run,raw:YuikaParent.storage.getItem(KEY)})')==before
     status=p.locator('#recommendation-entry-status').inner_text();assert '今の条件でおすすめする復習はありません' not in status
     rows.append({'app':app,'scenario':scenario,'disabled':True,'direct_start_preserved':True,'status':status})
    else:
     before=p.evaluate('YuikaParent.storage.getItem(KEY)');p.locator('#recommended-start').click()
     assert p.evaluate('YuikaParent.storage.getItem(KEY)')==before
     assert p.evaluate('run.recommended && run.qs.length===1 && run.mode==="normal"')
     reason=p.locator('#recommended-reasons').inner_text();assert '前の回答をもう一度確かめよう' in reason
     if scenario=='quota':
      p.evaluate("window.qaOriginalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===KEY)throw Error('synthetic quota');return qaOriginalSet.call(this,k,v)}")
     answer=p.evaluate('run.qs[run.index].answer');p.locator('#response').fill(answer);p.locator('#check').click()
     assert p.locator('#recommended-reasons').inner_text()==reason
     if scenario=='quota':
      assert p.evaluate('dirty')
      p.evaluate("go('home')");expect(p.locator('#recommended-start')).to_be_disabled()
      raw=p.evaluate('YuikaParent.storage.getItem(KEY)');assert raw==before
      snapshot=p.evaluate('JSON.stringify({screen,run,data})');p.evaluate('startRecommended()');assert p.evaluate('JSON.stringify({screen,run,data})')==snapshot
      rows.append({'app':app,'scenario':scenario,'dirty':True,'disabled':True,'saved_raw_preserved':True})
     else:
      p.locator('#next').click();saved=p.evaluate('JSON.parse(YuikaParent.storage.getItem(KEY))')
      assert len(saved['events'])==2
      added=[e for e in saved['events'] if e['id']!='qa-synthetic-wrong'];assert len(added)==1 and added[0]['mode']=='normal' and added[0]['correct'] and 'recommended' not in added[0] and 'reasons' not in added[0]
      p.reload();assert p.evaluate('data.events.length')==2
      assert p.evaluate("localStorage.getItem('yuika-social-540-27-v1')")=='synthetic-legacy-onin'
      assert p.evaluate("localStorage.getItem('yuika-social-540-25-v1')")=='synthetic-legacy-kamakura'
      assert p.evaluate("localStorage.getItem('qa-unrelated')")=='synthetic-keep'
      if scenario=='parent':
       assert p.evaluate(SNAP)==original
       assert p.evaluate('YuikaParent.active')
       p.locator('#parent-exit').click();p.wait_for_function('()=>window.YuikaParent&&!YuikaParent.active&&typeof data!=="undefined"')
       assert p.evaluate(SNAP)==original
       assert p.evaluate('data.events.length')==0
      rows.append({'app':app,'scenario':scenario,'started':1,'saved_events':2,'reload':True,'legacy_and_other_preserved':True,'parent_all_local_unchanged':scenario=='parent'})
    p.screenshot(path=str(OUT/f'{app}-{scenario}.png'),full_page=True);ctx.close()
  browser.close()
 assert Quiet.posts==0 and not errors
except Exception as e:
 failure={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
finally:
 srv.shutdown();endhead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 result={'head':head,'end_head':endhead,'cases':rows,'server_posts':Quiet.posts,'blocked_requests':outgoing,'page_errors':errors,'failure':failure}
 (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
 if failure:raise SystemExit(1)
 assert head==endhead
