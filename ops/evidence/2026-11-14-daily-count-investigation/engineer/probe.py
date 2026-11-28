import os, sys, json, subprocess, itertools
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
ROOT=Path('/workspace/yuika-daily-count-20261114'); OUT=Path('/tmp/yuika-daily-count-engineer')
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
requests=[]; metrics={'server_post_received':0,'blocked_nonlocal':0,'blocked_post':0}; errors=[]; results=[]; discoveries={}
class Handler(PreviewHandler):
 def log_message(self,*args): pass
 def do_GET(self):
  requests.append({'method':'GET','path':self.path}); super().do_GET()
 def do_POST(self):
  metrics['server_post_received']+=1; self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start()
def route(r):
 u=urlparse(r.request.url)
 if r.request.method=='POST': metrics['blocked_post']+=1;r.abort()
 elif u.hostname!='127.0.0.1' or u.port!=srv.server_port: metrics['blocked_nonlocal']+=1;r.abort()
 else:r.continue_()
def snapshot(p):
 return p.evaluate('''() => ({prefs:{...prefs},history:data.events.length,historyRaw:localStorage.getItem(KEY),storageKeys:Object.keys(localStorage),screen,run:run?{count:run.qs.length,ids:run.qs.map(q=>q.id),index:run.index,results:run.results.length}:null,notice:document.querySelector('#notice').textContent,candidateCount:screen==='home'?candidates('normal',prefs).length:null,daily:document.querySelector('#daily-five')?.textContent,disabled:document.querySelector('#daily-five')?.disabled,progress:document.querySelector('.quiz .row.between')?.innerText,uiOptions:screen==='home'?Object.fromEntries(['course','unit','variant'].map(id=>[id,[...document.querySelector('#'+id).options].map(o=>({value:o.value,text:o.text}))])):null,countOptions:[...document.querySelectorAll('[data-count]')].map(x=>x.dataset.count)})''')
def select(p,vals):
 for k,v in vals.items():
  if k=='count':p.locator('[data-count="'+str(v)+'"]').click()
  else:p.select_option('#'+k,v)
def shot(p,name,selector):
 p.locator(selector).scroll_into_view_if_needed();p.screenshot(path=str(OUT/(name+'.png')))
def newpage(browser,name):
 c=browser.new_context(viewport={'width':768,'height':1024});c.route('**/*',route);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{srv.server_port}/{name}');return c,p
def observe(browser,label,name,vals):
 c,p=newpage(browser,name);select(p,vals);before=snapshot(p);shot(p,label+'-before','#daily-five');shot(p,label+'-filters','#start');p.locator('#daily-five').click();after=snapshot(p);shot(p,label+'-after','#main' if after['screen']=='quiz' else '#notice');result={'case':label,'page':name,'before':before,'after':after};results.append(result);(OUT/'results.partial.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));c.close()
def discover(browser,name,count):
 c,p=newpage(browser,name);opts=snapshot(p)['uiOptions'];found={};scanned=[]
 for combo in itertools.product(*[[o['value'] for o in opts[k]] for k in ('course','unit','variant')]):
  vals=dict(zip(('course','unit','variant'),combo));select(p,vals);n=p.evaluate("candidates('normal',prefs).length");scanned.append({**vals,'candidates':n})
  if 0<n<count and 'shortage' not in found:found['shortage']={**vals,'count':count}
  if n==0 and 'zero' not in found:found['zero']={**vals,'count':count}
  if len(found)==2:break
 discoveries[name]={'options':opts,'scanned':scanned,'found':found};c.close();return found
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  observe(b,'A','onin-review.html',{'course':'all','unit':'all','variant':'normal','count':5})
  observe(b,'B','onin-review.html',{'course':'all','unit':'all','variant':'normal','count':10})
  f=discover(b,'onin-review.html',5)
  for label,key in [('C','shortage'),('D','zero')]:
   if key in f:observe(b,label,'onin-review.html',f[key])
   else:results.append({'case':label,'unreachable_in_scanned_options':True})
  f=discover(b,'heian-review.html',10)
  if 'shortage' in f:observe(b,'E','heian-review.html',f['shortage'])
  elif 'zero' in f:observe(b,'E','heian-review.html',f['zero'])
  else:results.append({'case':'E','unreachable_in_scanned_options':True})
  b.close()
finally:
 srv.shutdown()
 report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'dirty':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),'viewport':{'width':768,'height':1024},'results':results,'discoveries':discoveries,'metrics':metrics,'requests':requests,'pageerrors':errors}
 (OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)); print(json.dumps(report,ensure_ascii=False))
