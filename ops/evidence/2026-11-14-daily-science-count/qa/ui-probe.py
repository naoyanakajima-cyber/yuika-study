"""Independent synthetic UI, top navigation and selection probes; no repo writes."""
import datetime,json,os,subprocess,sys,traceback
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-daily-science-20261114');OUT=Path('/tmp/yuika-daily-residual-qa')
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
report={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'before_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),'viewport':{'width':768,'height':1024},'ui_cases':[],'boundary_cases':[],'selection_cases':[],'blocked_requests':[],'served_public_assets':[],'server_posts':0,'page_errors':[]}
assets={}
for path in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
 u='https://unpkg.com/'+path;assets[u]=subprocess.check_output(['curl','-fsSL','--max-time','30',u])
class Quiet(PreviewHandler):
 def log_message(self,*args):pass
 def do_POST(self):report['server_posts']+=1;self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/'
def route(r):
 u=urlparse(r.request.url)
 if r.request.method=='GET' and u.hostname=='127.0.0.1' and u.port==srv.server_port:r.continue_()
 elif r.request.method=='GET' and r.request.url in assets:report['served_public_assets'].append(r.request.url);r.fulfill(body=assets[r.request.url],content_type='application/javascript')
 else:report['blocked_requests'].append({'method':r.request.method,'url':r.request.url});r.abort()
def snapshot(p):return p.evaluate("""()=>({count,scienceUnit,view,events:state.events.length,history:YuikaParent.storage.getItem(KEY),localHistory:localStorage.getItem(KEY),parent:YuikaParent.active,session:session?{mode:session.mode,count:session.questions.length,ids:session.questions.map(q=>q.id),results:session.results.length}:null,notice:document.querySelector('#notice').textContent})""")
def answer(p):
 q=p.evaluate('session.questions[session.index]')
 if q['type']=='number':p.locator('#numeric').fill(str(q['answer']))
 else:p.locator('[data-choice="'+str(q['options'].index(q['answer']))+'"]').click()
 p.locator('#check').click();assert p.evaluate("state.events.at(-1).correct&&state.events.at(-1).mode==='daily'")
def new(browser,parent=False):
 ctx=browser.new_context(viewport=report['viewport']);ctx.route('**/*',route);p=ctx.new_page();p.on('pageerror',lambda e:report['page_errors'].append(str(e)));p.on('dialog',lambda d:d.accept());p.goto(base+'yuika-review-v2.html'+('?parent-check=1' if parent else ''));p.wait_for_function("typeof scienceUnit!=='undefined'");return ctx,p
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  # Old vs new selection using real app valid history, fixed Date.now and Math.random only here.
  ctx,p=new(browser);old=subprocess.check_output(['git','show','55435567d44f05dc35f3ea6d73c4ba9cac2dc496:scripts/practice/science.js'],cwd=ROOT,text=True)
  old=old[old.index('function scienceDaily('):old.index('const scienceStart=')].replace('function scienceDaily(', 'function oldScienceDaily(')
  p.evaluate("source=>{window.oldScienceDaily=(0,eval)('('+source+')')}",old)
  result=p.evaluate("""()=>{const assert=(v,m)=>{if(!v)throw Error(m)};const now=Date.now(),realNow=Date.now,realRandom=Math.random;Date.now=()=>now;let seed=1,draws=0;Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;draws++;return seed/4294967296};const qs=QUESTIONS.filter(q=>q.type==='choice').slice(0,2);const mk=(q,days,correct)=>{const at=new Date(now-days*86400000).toISOString(),response=correct?q.answer:q.options.find(o=>o!==q.answer);return validateEvent({questionVersion:currentQuestionVersion(q),id:'qa-'+q.id+'-'+days,sessionId:'synthetic-rng-session',questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response,inputRaw:response,expected:q.answer,correct,answeredAt:at,timezoneOffset:0,localDay:localDay(at,0),hintUsed:false,mode:'normal',explanation:q.explanation});};const out=[];for(const history of [false,true]){state.events=history?[mk(qs[0],4,false),mk(qs[0],3,false),mk(qs[0],2,true),mk(qs[1],4,false),mk(qs[1],3,false)]:[];for(const u of ['all','実験器具','水溶液と溶解','synthetic-no-unit'])for(const n of [5,10]){scienceUnit=u;count=n;seed=42;draws=0;const a=scienceDaily().map(q=>q.id),ad=draws;seed=42;draws=0;const b=oldScienceDaily().map(q=>q.id);assert(JSON.stringify(a)===JSON.stringify(b),'IDs '+u);assert(draws===ad,'draws '+u);seed=42;draws=0;render();assert(draws===0,'render draws');const button=document.querySelector('#daily-five').textContent;assert(button.includes('今回は'+a.length+'問'),'display count '+u);out.push({history,unit:u,limit:n,count:a.length,draws:ad,ids_equal:true,render_draws:draws});}}Math.random=realRandom;Date.now=realNow;return out;}""")
  report['selection_cases']=result;ctx.close();browser.close()
 assert report['server_posts']==0 and not report['page_errors'];report['result']='PASS'
except Exception:report['failure']=traceback.format_exc();raise
finally:
 srv.shutdown();report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();report['after_status']=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
 (OUT/'ui-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
