"""Independent synthetic science storage-access recovery QA; no product edits."""
import copy,json,os,subprocess,sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path('/workspace/yuika-science-storage-recovery-20261111');OUT=Path('/workspace/work/storage-recovery-qa-20261111')
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
posts=[];external=[];attempts=[];errors=[];rows=[]
class Handler(PreviewHandler):
 def log_message(self,*args):pass
 def do_POST(self):posts.append(self.path);self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/'
KEY='yuika-prototype-v1:yuika-science-review-v2'
OLD={'yuika-science-review-v2':'synthetic-original-history','yuika-science-v1':'synthetic-original-aggregate','yuika-social-540-27-v1':'synthetic-other-unit','yuika-last-daily-unit-v1':'synthetic-old-unit'}
INIT='''cfg=>{
 window.qaNativeGet=Storage.prototype.getItem;window.qaNativeSet=Storage.prototype.setItem;
 window.qaDeny=cfg.deny&&!sessionStorage.getItem('qa-reload-safe');window.qaQuota=false;
 if(!sessionStorage.getItem('qa-seeded')){if(cfg.raw!==null)qaNativeSet.call(localStorage,cfg.key,cfg.raw);for(const [k,v]of Object.entries(cfg.old))qaNativeSet.call(localStorage,k,v);sessionStorage.setItem('qa-seeded','1');}
 Storage.prototype.getItem=function(k){if(k===cfg.key&&qaDeny)throw new Error('synthetic read refusal');return qaNativeGet.call(this,k);};
 Storage.prototype.setItem=function(k,v){if(k===cfg.key&&qaQuota)throw new Error('synthetic quota');return qaNativeSet.call(this,k,v);};
}'''
def newpage(browser,raw,deny=True,body=None):
 ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True)
 def route(r):
  if r.request.method=='POST':attempts.append(r.request.url);r.abort()
  elif not r.request.url.startswith(base):external.append(r.request.url);r.abort()
  else:r.continue_()
 ctx.route('**/*',route)
 if body is not None:ctx.route(base+'yuika-review-v2.html',lambda r:r.fulfill(status=200,headers={'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"connect-src 'none'; form-action 'none'; object-src 'none'"},body=body))
 cfg={'key':KEY,'raw':raw,'deny':deny,'old':OLD}
 ctx.add_init_script('('+INIT+')('+json.dumps(cfg)+');')
 p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
 p.goto(base+'yuika-review-v2.html');return ctx,p

def rawdisk(p):return p.evaluate('qaNativeGet.call(localStorage,KEY)')
def answer(p):
 p.locator('#start').click();q=p.evaluate('session.questions[session.index]')
 if q['type']=='number':p.locator('#numeric').fill(str(q['answer']))
 else:p.locator('[data-choice]').nth(q['options'].index(q['answer'])).click()
 p.locator('#check').click()
 assert p.evaluate('state.events.length')==1
 pending=p.evaluate('state.events[0]');assert pending['correct'] is True
 p.locator('[data-view="records"]').click();return pending

def preserve(p,pending,raw):
 assert rawdisk(p)==raw
 assert p.evaluate('state.events')==[pending]
 assert p.evaluate('dirty') is True
 assert p.evaluate('blocked') is True
 assert '保存ができました' not in p.locator('#notice').inner_text()
 assert p.evaluate('Object.fromEntries(Object.keys('+json.dumps(OLD)+').map(k=>[k,qaNativeGet.call(localStorage,k)]))')==OLD

def recover(p):p.evaluate("()=>{qaDeny=false;sessionStorage.setItem('qa-reload-safe','1');}")

try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  ctx,p=newpage(browser,None,False)
  fixture=p.evaluate('''()=>{
   const q=QUESTIONS.find(q=>q.type==='number'),at='2026-11-01T03:00:00.000Z';
   const e=validateEvent({id:'independent-saved-answer',sessionId:'synthetic-storage-recovery',questionId:q.id,questionVersion:currentQuestionVersion(q),datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response:q.answer,inputRaw:String(q.answer),expected:q.answer,correct:true,answeredAt:at,timezoneOffset:0,localDay:localDay(at,0),hintUsed:false,mode:'normal',explanation:q.explanation});
   return {...emptyState(),events:[e],legacy:[{raw:JSON.stringify({attempts:2,correct:[1],wrong:[2]}),capturedAt:at}]};
  }''');ctx.close()
  initial=json.dumps(fixture)
  baseline='408805b06092b9eec5971426a8a1c2cb45194620'
  oldbody=subprocess.check_output(['git','show',baseline+':yuika-review-v2.html'],cwd=ROOT)
  ctx,p=newpage(browser,initial,body=oldbody)
  pending=answer(p);recover(p);p.locator('#retry').click();preserve(p,pending,initial)
  rows.append({'case':'baseline_known_defect','head':baseline,'expected_recovery':False,'observed_blocked':True,'old_raw_unchanged':True})
  ctx.close()
  # Real UI answer remains pending while disk cannot be read. Current disk grows
  # before access resumes; the retry must re-read it, not replace it from memory.
  ctx,p=newpage(browser,initial)
  assert p.evaluate('({blocked,rawBroken,n:state.events.length})')=={'blocked':True,'rawBroken':None,'n':0}
  pending=answer(p);preserve(p,pending,initial)
  late=copy.deepcopy(fixture);late['events'].append({**late['events'][0],'id':'independent-late-answer','sessionId':'synthetic-late-writer'})
  current=json.dumps(late);p.evaluate('raw=>{qaNativeSet.call(localStorage,KEY,raw);}',current)
  recover(p);p.locator('#retry').click()
  saved=json.loads(rawdisk(p));expect={e['id']:e for e in late['events']+[pending]}
  assert {e['id']:e for e in saved['events']}==expect
  assert saved['legacy']==fixture['legacy']
  assert p.evaluate('({blocked,dirty,rawBroken})')=={'blocked':False,'dirty':False,'rawBroken':None}
  before=rawdisk(p);p.locator('#retry').click();assert rawdisk(p)==before
  with p.expect_download() as dl:p.locator('#export').click()
  assert json.loads(Path(dl.value.path()).read_bytes())['payload']==saved
  p.reload();assert p.evaluate('state')==saved
  p.screenshot(path=str(OUT/'recovered-science-home.png'),full_page=True)
  assert p.evaluate('Object.fromEntries(Object.keys('+json.dumps(OLD)+').map(k=>[k,qaNativeGet.call(localStorage,k)]))')==OLD
  rows.append({'case':'real_ui_retry_merges_current_disk_and_pending','passed':True,'events':len(saved['events']),'reload':True,'actual_export':True})
  ctx.close()
  # Continued denial and a later quota failure must preserve original bytes and
  # pending answer; only the successful final retry may clear the blocked flags.
  ctx,p=newpage(browser,initial);pending=answer(p);p.locator('#retry').click();preserve(p,pending,initial)
  recover(p);p.evaluate('()=>{qaQuota=true;}');p.locator('#retry').click();preserve(p,pending,initial)
  p.evaluate('()=>{qaQuota=false;}');p.locator('#retry').click()
  assert {e['id'] for e in json.loads(rawdisk(p))['events']}=={fixture['events'][0]['id'],pending['id']}
  assert p.evaluate('!blocked&&!dirty')
  rows.append({'case':'denial_then_quota_then_ui_retry','passed':True});ctx.close()
  # An invalid value that becomes readable must never be overwritten.
  for raw in ('', '{invalid', json.dumps({**fixture,'schemaVersion':999})):
   ctx,p=newpage(browser,raw);pending=answer(p);recover(p);p.locator('#retry').click();preserve(p,pending,raw)
   p.locator('#retry').click();preserve(p,pending,raw)
   rows.append({'case':'newly_readable_invalid_raw','raw_kind':'empty' if raw=='' else 'invalid','passed':True});ctx.close()
  # Known invalid raw stays protected even if another writer replaces disk.
  for raw in ('','{known-invalid'):
   ctx,p=newpage(browser,raw,False)
   assert p.evaluate('blocked') and p.evaluate('rawBroken')==raw
   pending=answer(p)
   p.evaluate('raw=>{qaNativeSet.call(localStorage,KEY,raw);}',initial)
   p.locator('#retry').click();preserve(p,pending,initial)
   assert p.evaluate('rawBroken')==raw
   with p.expect_download() as dl:p.locator('#rawBroken').click()
   assert Path(dl.value.path()).read_text()==raw
   rows.append({'case':'known_invalid_raw_stays_protected','raw_kind':'empty' if raw=='' else 'invalid','passed':True});ctx.close()
  # Valid payloads with a same-ID conflict must remain separate and unchanged.
  ctx,p=newpage(browser,initial);pending=answer(p)
  conflict=copy.deepcopy(fixture);conflict['events']=[{**pending,'sessionId':'synthetic-conflict'}]
  raw=json.dumps(conflict);p.evaluate('raw=>{qaNativeSet.call(localStorage,KEY,raw);}',raw);recover(p)
  p.locator('#retry').click();preserve(p,pending,raw)
  rows.append({'case':'same_id_conflict','passed':True});ctx.close()
  browser.close()
 assert not attempts and not posts and not external and not errors,(attempts,posts,external,errors)
 result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'cases':rows,'post_attempts':len(attempts),'post_arrivals':len(posts),'external_requests':len(external),'page_errors':errors}
 (OUT/'probe-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:srv.shutdown()
