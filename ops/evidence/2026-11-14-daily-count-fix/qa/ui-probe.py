"""Independent real-UI count acceptance, fresh synthetic contexts only."""
import datetime,json,os,subprocess,sys,traceback
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-daily-fix-20261114'); OUT=Path('/tmp/yuika-daily-fix-qa')
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
report={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'before_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),'viewport':{'width':768,'height':1024},'cases':[],'blocked_requests':[],'server_posts':0,'page_errors':[]}
class Quiet(PreviewHandler):
 def log_message(self,*args):pass
 def do_POST(self):report['server_posts']+=1;self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start()
def route(r):
 u=urlparse(r.request.url)
 if r.request.method!='GET' or u.hostname!='127.0.0.1' or u.port!=srv.server_port:
  report['blocked_requests'].append({'method':r.request.method,'url':r.request.url});r.abort()
 else:r.continue_()
def state(p):
 return p.evaluate("""() => ({prefs:{...prefs},screen,events:data.events.length,history:YuikaParent.storage.getItem(KEY),localHistory:localStorage.getItem(KEY),parent:YuikaParent.active,run:run?{count:run.qs.length,index:run.index,results:run.results.length,ids:run.qs.map(q=>q.id)}:null,notice:document.querySelector('#notice').textContent})""")
CASES=[('A','onin-review.html','all','all','normal',5,5,False),('B','onin-review.html','all','all','normal',10,10,False),('C','onin-review.html','all','応仁の乱','kanji',5,4,False),('D','onin-review.html','d2','将軍','normal',5,0,False),('E','heian-review.html','pairs','藤原氏と政治','normal',10,2,False),('K','kamakura-review.html','all','all','normal',5,5,False),('F','mock-focus-review.html','all','all','normal',5,5,False),('P','onin-review.html','all','応仁の乱','kanji',5,4,True)]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for label,app,course,unit,variant,limit,n,parent in CASES:
   if label not in ('F','P'):continue
   ctx=browser.new_context(viewport=report['viewport']);ctx.route('**/*',route);p=ctx.new_page();p.on('pageerror',lambda e:report['page_errors'].append(str(e)));p.on('dialog',lambda d:d.accept())
   p.goto(f'http://127.0.0.1:{srv.server_port}/{app}'+('?parent-check=1' if parent else ''));p.wait_for_function('typeof data!=="undefined" && typeof prefs!=="undefined"')
   initial=state(p);assert initial['events']==0 and initial['history'] is None
   p.select_option('#course',course);p.select_option('#unit',unit)
   if p.locator('#variant').count():p.select_option('#variant',variant)
   else:assert p.evaluate('prefs.variant')==variant
   p.locator(f'[data-count="{limit}"]').click()
   before=state(p);before.update(button=p.locator('#daily-five').inner_text(),disabled=p.locator('#daily-five').is_disabled())
   assert before['button']==f'今日の復習をはじめる（今回は{n}問）',(label,before)
   assert before['disabled']==(n==0)
   p.locator('#daily-five').scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'{label}-before.png'))
   if n:
    p.locator('#daily-five').click();after=state(p);assert after['screen']=='quiz' and after['run']['count']==n
    assert after['events']==0 and after['history'] is None
   else:
    expect(p.get_by_text('この条件では候補がありません。コース・分野・確認方法を見直してください。',exact=True)).to_be_visible()
    before['zero_visible']=True
    p.evaluate('startDaily()');after=state(p);assert after['screen']=='home' and after['run'] is None
   assert after['events']==0 and after['history'] is None
   p.screenshot(path=str(OUT/f'{label}-after.png'))
   result={'case':label,'app':app,'initial':initial,'before':before,'after_start':after}
   if label in ('C','P'):
    p.evaluate("localStorage.setItem('qa-unrelated','synthetic-preserved');localStorage.setItem(LEGACY_KEY,'synthetic-legacy-preserved')")
    original=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
    p.locator('#response').fill(p.evaluate('expectedOf(run.qs[run.index],run.variant)'));p.locator('#check').click()
    result['after_answer']=state(p);assert p.evaluate("data.events.at(-1).mode==='daily' && data.events.at(-1).correct")
    p.reload();p.wait_for_function('typeof data!=="undefined"');assert p.evaluate('data.events.length')==1
    assert p.evaluate("localStorage.getItem(LEGACY_KEY)")=='synthetic-legacy-preserved';assert p.evaluate("localStorage.getItem('qa-unrelated')")=='synthetic-preserved'
    if parent:assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==original
    result['after_reload']=state(p)
   report['cases'].append(result);ctx.close()
  browser.close()
 assert report['server_posts']==0 and not report['page_errors'];report['result']='PASS'
except Exception:
 report['failure']=traceback.format_exc();raise
finally:
 srv.shutdown();report['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();report['after_status']=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
 (OUT/'ui-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
