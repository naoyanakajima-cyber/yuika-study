"""Independent UI-only reproduction on unchanged main, empty ephemeral histories."""
import datetime,json,os,subprocess,sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
ROOT=Path('/workspace/yuika-daily-count-20261114')
OUT=Path('/tmp/yuika-daily-count-qa')
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
report={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'before_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),'viewport':{'width':768,'height':1024},'cases':[],'blocked_requests':[],'server_posts':0,'page_errors':[]}
class Quiet(PreviewHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  report['server_posts']+=1
  self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start()
def route(r):
 u=urlparse(r.request.url)
 if r.request.method!='GET' or u.hostname!='127.0.0.1' or u.port!=srv.server_port:
  report['blocked_requests'].append({'method':r.request.method,'url':r.request.url});r.abort()
 else:r.continue_()
def state(p):
 return p.evaluate("""() => ({prefs:{...prefs},screen,events:data.events.length,history:localStorage.getItem(KEY),storageKeys:Object.keys(localStorage),run:run?{count:run.qs.length,index:run.index,results:run.results.length,ids:run.qs.map(q=>q.id)}:null,notice:document.querySelector('#notice').textContent})""")
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for label,course,unit,variant,n in [('C','all','応仁の乱','kanji',4),('D','d2','将軍','normal',0)]:
   context=browser.new_context(viewport=report['viewport'])
   context.route('**/*',route)
   p=context.new_page()
   p.on('pageerror',lambda e:report['page_errors'].append(str(e)))
   p.goto(f'http://127.0.0.1:{srv.server_port}/onin-review.html')
   initial=state(p)
   assert initial['events']==0 and initial['history'] is None
   p.select_option('#course',course)
   p.select_option('#unit',unit)
   p.select_option('#variant',variant)
   p.locator('[data-count="5"]').click()
   before=state(p)
   before.update(daily=p.locator('#daily-five').inner_text(),disabled=p.locator('#daily-five').is_disabled(),normal_disabled=p.locator('#start').is_disabled(),unseen_text=p.locator('[data-mode="unseen"]').inner_text(),unseen_visible=p.locator('[data-mode="unseen"]').is_visible(),unseen_count=p.locator('[data-mode="unseen"] b').inner_text(),candidate_runtime=p.evaluate("candidates('normal',prefs).length"),legacy_candidate_paragraphs=p.locator('.practice-card p').count())
   assert before['prefs']=={'count':5,'course':course,'unit':unit,'variant':variant}
   assert before['candidate_runtime']==n and before['unseen_count'].split()[0]==str(n)
   assert before['daily']=='今日の5問をはじめる（今回は5問）' and before['disabled'] is False
   p.locator('#daily-five').scroll_into_view_if_needed()
   p.screenshot(path=str(OUT/f'{label}-before.png'))
   p.locator('[data-mode="unseen"]').scroll_into_view_if_needed()
   p.screenshot(path=str(OUT/f'{label}-count.png'))
   p.locator('#daily-five').click()
   after=state(p)
   if n:
    after['progress']=p.locator('.quiz .row.between').inner_text()
    assert after['screen']=='quiz' and after['run']['count']==n and '1 / 4問' in after['progress']
   else:
    assert after['screen']=='home' and after['run'] is None and after['notice']=='この条件では候補がありません。'
   assert after['events']==0 and after['history'] is None
   p.locator('#main' if n else '#notice').scroll_into_view_if_needed()
   p.screenshot(path=str(OUT/f'{label}-after.png'))
   report['cases'].append({'case':label,'initial':initial,'before':before,'after':after})
   context.close()
  browser.close()
 assert report['server_posts']==0 and not report['page_errors']
 report['result']='PASS: existing shortage and zero behavior independently reproduced; no fix acceptance'
finally:
 srv.shutdown()
 report['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 report['after_status']=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
 (OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps(report,ensure_ascii=False))
