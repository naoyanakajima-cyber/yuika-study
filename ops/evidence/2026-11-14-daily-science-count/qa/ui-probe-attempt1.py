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
  # Real controls, no fixture/clock/RNG overrides for these user count cases.
  for label,unit,limit,n,parent in [('all5','all',5,5,False),('all10','all',10,10,False),('equipment8','実験器具',10,8,False),('solution9','水溶液と溶解',10,9,False),('parent8','実験器具',10,8,True)]:
   ctx,p=new(browser,parent);assert p.evaluate('state.events.length')==0
   p.select_option('#unit',unit);p.locator(f'[data-count="{limit}"]').click();before=snapshot(p)
   expect(p.locator('#daily-five')).to_have_text(f'今日の復習をはじめる（今回は{n}問）');assert p.locator('#daily-five').is_enabled()
   p.locator('#daily-five').scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'{label}-before.png'))
   p.locator('#daily-five').click();after=snapshot(p);assert after['view']=='quiz' and after['session']['count']==n and after['events']==0 and after['history'] is None
   p.screenshot(path=str(OUT/f'{label}-after.png'));res={'case':label,'before':before,'after_start':after}
   if label in ('equipment8','parent8'):
    p.evaluate("localStorage.setItem('qa-unrelated','synthetic-preserved');localStorage.setItem(LEGACY_KEY,'synthetic-legacy-preserved')")
    local=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))');answer(p);res['after_answer']=snapshot(p)
    p.reload();p.wait_for_function("typeof scienceUnit!=='undefined'");assert p.evaluate('state.events.length')==1
    assert p.evaluate('localStorage.getItem(LEGACY_KEY)')=='synthetic-legacy-preserved';assert p.evaluate("localStorage.getItem('qa-unrelated')")=='synthetic-preserved'
    if parent:assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==local
    res['after_reload']=snapshot(p)
   report['ui_cases'].append(res);ctx.close()
  # Top entry must use saved science preferences and auto-start once, preserving parent mode.
  for parent in (False,True):
   ctx,p=new(browser,parent);p.select_option('#unit','実験器具');p.locator('[data-count="10"]').click();p.goto(base+'index.html'+('?parent-check=1' if parent else ''));p.locator('.daily-panel').wait_for()
   expect(p.locator('.daily-panel h2')).to_have_text('今日の復習');expect(p.locator('.daily-panel')).to_contain_text('前回の単元から（問数は単元の設定）')
   p.get_by_role('button',name='今日の復習をはじめる',exact=True).click();p.wait_for_url('**/yuika-review-v2.html?*');p.wait_for_function("typeof session!=='undefined'&&session!==null")
   s=snapshot(p);assert s['view']=='quiz' and s['session']['mode']=='daily' and s['session']['count']==8 and s['events']==0 and s['parent']==parent
   if parent:assert 'parent-check=1' in p.url;expect(p.locator('#parent-check-banner')).to_be_visible();assert s['localHistory'] is None
   report['ui_cases'].append({'case':'top-parent' if parent else 'top-normal','url_query':urlparse(p.url).query,'after_start':s});ctx.close()
  ctx,p=new(browser)
  # Changed count, unavailable and impossible UI unit are defensive probes only.
  changed=p.evaluate("""()=>{const old=Math.random;let draws=0;Math.random=()=>{draws++;return old()};count=10;start('daily');Math.random=old;return {draws,view,session,button:document.querySelector('#daily-five').textContent,notice:document.querySelector('#notice').textContent}}""")
  assert changed['draws']==0 and changed['view']=='home' and changed['session'] is None and '10問' in changed['button'] and '問題数が変わりました' in changed['notice'];report['boundary_cases'].append({'case':'stale-count-no-start','result':changed})
  for field in ('blocked','dirty'):
   p.evaluate(f'{field}=true;start("daily")');expect(p.locator('#daily-five')).to_be_disabled();expect(p.locator('#daily-status')).to_be_visible();assert p.evaluate("view==='home'&&session===null")
   report['boundary_cases'].append({'case':field,'status':p.locator('#daily-status').inner_text()});p.evaluate(f'{field}=false;render()')
  p.evaluate("scienceUnit='synthetic-no-unit';render();start('daily')");expect(p.locator('#daily-five')).to_be_disabled();expect(p.locator('#daily-status')).to_be_visible();assert p.evaluate("view==='home'&&session===null")
  report['boundary_cases'].append({'case':'synthetic-zero-not-real-ui','status':p.locator('#daily-status').inner_text()});p.evaluate("scienceUnit='all';render()")
  # Actual synthetic answer supplies a valid record, then a future date stops daily entry.
  p.locator('#daily-five').click();answer(p);event=p.evaluate('state.events.at(-1)');p.locator('[data-view="home"]').click()
  p.evaluate("""e=>{const at=new Date(Date.now()+600000).toISOString();e.answeredAt=at;e.timezoneOffset=0;e.localDay=localDay(at,0);state.events=[validateEvent(e)];render();start('daily');}""",event)
  expect(p.locator('#daily-five')).to_be_disabled();expect(p.locator('#daily-status')).to_be_visible();assert p.evaluate("view==='home'&&session===null")
  report['boundary_cases'].append({'case':'future-valid-event','status':p.locator('#daily-status').inner_text()})
  p.evaluate('state.events=[];render()');expect(p.locator('#daily-five')).to_be_enabled();ctx.close()
  # Old vs new selection using real app valid history, fixed Date.now and Math.random only here.
  ctx,p=new(browser);old=subprocess.check_output(['git','show','55435567d44f05dc35f3ea6d73c4ba9cac2dc496:scripts/practice/science.js'],cwd=ROOT,text=True)
  old=old[old.index('function scienceDaily('):old.index('const scienceStart=')].replace('function scienceDaily(', 'function oldScienceDaily(')
  p.evaluate("source=>{window.oldScienceDaily=(0,eval)('('+source+')')}",old)
  result=p.evaluate("""()=>{const assert=(v,m)=>{if(!v)throw Error(m)};const now=Date.now(),realNow=Date.now,realRandom=Math.random;Date.now=()=>now;let seed=1,draws=0;Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;draws++;return seed/4294967296};const qs=QUESTIONS.filter(q=>q.type==='choice').slice(0,2);const mk=(q,days,correct)=>{const at=new Date(now-days*86400000).toISOString(),response=correct?q.answer:q.options.find(o=>o!==q.answer);return validateEvent({questionVersion:currentQuestionVersion(q),id:'qa-'+q.id+'-'+days,sessionId:'qa-rng',questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response,inputRaw:response,expected:q.answer,correct,answeredAt:at,timezoneOffset:0,localDay:localDay(at,0),hintUsed:false,mode:'normal',explanation:q.explanation});};const out=[];for(const history of [false,true]){state.events=history?[mk(qs[0],4,false),mk(qs[0],3,false),mk(qs[0],2,true),mk(qs[1],4,false),mk(qs[1],3,false)]:[];for(const u of ['all','実験器具','水溶液と溶解','synthetic-no-unit'])for(const n of [5,10]){scienceUnit=u;count=n;seed=42;draws=0;const a=scienceDaily().map(q=>q.id),ad=draws;seed=42;draws=0;const b=oldScienceDaily().map(q=>q.id);assert(JSON.stringify(a)===JSON.stringify(b),'IDs '+u);assert(draws===ad,'draws '+u);seed=42;draws=0;render();assert(draws===0,'render draws');const button=document.querySelector('#daily-five').textContent;assert(button.includes('今回は'+a.length+'問'),'display count '+u);out.push({history,unit:u,limit:n,count:a.length,draws:ad,ids_equal:true,render_draws:draws});}}Math.random=realRandom;Date.now=realNow;return out;}""")
  report['selection_cases']=result;ctx.close();browser.close()
 assert report['server_posts']==0 and not report['page_errors'];report['result']='PASS'
except Exception:report['failure']=traceback.format_exc();raise
finally:
 srv.shutdown();report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();report['after_status']=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
 (OUT/'ui-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
