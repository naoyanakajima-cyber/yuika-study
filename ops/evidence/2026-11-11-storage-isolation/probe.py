"""Independent synthetic storage-isolation probe. No product edits."""
import copy,json,os,subprocess,sys
from pathlib import Path
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path('/workspace/yuika-review-storage-isolation-20261111')
OUT=Path('/workspace/work/isolation-qa-20261111')
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
NAMES=['onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html']
OLD_KEYS=['yuika-social-540-27-v1','yuika-social-540-25-v1','yuika-social-540-24-v1','yuika-science-review-v2']
OLD_SHA='ba829a1176ff1ead7d312526890afe8792178c99'
old={name:subprocess.check_output(['git','show',OLD_SHA+':'+name],cwd=ROOT) for name in NAMES}
active={name:(ROOT/name).read_bytes() for name in NAMES}
posts=[]
class Handler(PreviewHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  name=self.path.split('?')[0].lstrip('/')
  if name in active:
   body=active[name];self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  else:super().do_GET()
 def do_POST(self):posts.append(self.path);self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=srv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{srv.server_port}/'
MK='''() => {
 const science=typeof byId!=='undefined',q=QUESTIONS.find(q=>q.type===(science?'number':'text')),at='2026-11-10T03:00:00.000Z';
 const base={id:crypto.randomUUID(),sessionId:'independent-isolation',questionId:q.id,unit:q.unit,response:q.answer,correct:true,mode:'normal',questionVersion:currentQuestionVersion(q)};
 const raw=science?{...base,datasetVersion:VERSION,type:q.type,question:q.prompt,inputRaw:String(q.answer),expected:q.answer,explanation:q.explanation,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed:false}:
 {...base,version:VERSION,...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),course:q.course,question:promptOf(q,'normal'),expected:expectedOf(q,'normal'),explanation:q.explanation,variant:'normal',hint:false,...(typeof UNIT_ID==='undefined'?{reflection:''}:{}),at,offset:0,day:at.slice(0,10)};
 const event=validateEvent(raw),legacy=structuredClone(event);delete legacy.questionVersion;
 return {science,key:KEY,event,old:JSON.stringify({... (science?emptyState():empty()),events:[legacy]})};
}'''
COUNT="({blocked,dirty,count:(typeof state==='undefined'?data:state).events.length})"
def events_obj(value):
 if isinstance(value,dict):
  if isinstance(value.get('events'),list):return value
  for v in value.values():
   found=events_obj(v)
   if found is not None:return found
 return None
results=[];attempts=[];external=[];errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for name,legacykey in zip(NAMES,OLD_KEYS):
   ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True)
   def route(r):
    if r.request.method=='POST':attempts.append(r.request.url);r.abort()
    elif not r.request.url.startswith(base):external.append(r.request.url);r.abort()
    else:r.continue_()
   ctx.route('**/*',route);page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base+name);fixture=page.evaluate(MK);assert fixture['key']!=legacykey,(name,'KEY not isolated')
   aggregate=json.dumps({'attempts':1,'correct':[1],'wrong':[]})
   if fixture['science']:
    legacy_state=json.loads(fixture['old']);legacy_state['legacy']=[{'raw':aggregate,'capturedAt':'2026-11-10T03:00:00.000Z'}];fixture['old']=json.dumps(legacy_state)
   sentinels={k:'synthetic untouched old raw' for k in OLD_KEYS}
   sentinels[legacykey]=fixture['old'];sentinels['yuika-science-v1']=aggregate
   sentinels['yuika-last-daily-unit-v1']='heian-review.html';sentinels[legacykey+'-preferences-v1']='{"count":10}'
   page.evaluate('(s)=>{for(const[k,v]of Object.entries(s))localStorage.setItem(k,v);}',sentinels)
   current=active[name];active[name]=old[name];page.reload();assert page.evaluate(COUNT)['count']==1 and not page.evaluate(COUNT)['blocked'],(name,'initial old reader invalid')
   active[name]=current;page.reload();assert page.evaluate(COUNT)['count']==0,(name,'automatic legacy import')
   if fixture['science']:assert page.evaluate('state.legacy.length')==0,'automatic legacy aggregate copy'
   okay=page.evaluate('''e=>{if(typeof state==='undefined'){data=validate({...empty(),events:[e]});return save();}state=validateState({...emptyState(),events:[e]});return persist();}''',fixture['event']);assert okay,(name,'save failed')
   page.reload();assert page.evaluate(COUNT)=={'blocked':False,'dirty':False,'count':1},name
   current=active[name];active[name]=old[name];page.reload();assert page.evaluate(COUNT)['count']==1 and not page.evaluate(COUNT)['blocked'],(name,'old reader blocked')
   active[name]=current;page.reload();assert page.evaluate(COUNT)['count']==1,(name,'trial data not restored')
   if name=='onin-review.html':page.screenshot(path=str(OUT/'onin-prototype-home.png'),full_page=True)
   page.evaluate('records()')
   with page.expect_download() as dl:page.locator('#export').click()
   path=OUT/(name+'.json');dl.value.save_as(path);exported=json.loads(path.read_text());assert exported.get('format')=='yuika-review-prototype' and exported.get('formatVersion')==1,(name,'missing prototype envelope');obj=events_obj(exported);assert obj and obj['events']==[fixture['event']],(name,'export event changed')
   with page.expect_download() as original_dl:page.locator('#prototype-original').click()
   original_path=OUT/(name+'.original.json');original_dl.value.save_as(original_path);assert original_path.read_text()==fixture['old'],(name,'old raw download changed')
   await_input='async text=>{await importFile(new File([text],"synthetic-trial.json",{type:"application/json"}));}'
   page.evaluate('localStorage.removeItem(KEY)');page.reload();assert page.evaluate(COUNT)['count']==0
   page.evaluate('records()');page.locator('#import').set_input_files({'name':'independent-trial.json','mimeType':'application/json','buffer':path.read_bytes()})
   page.wait_for_function('() => rejectedImportRaw===null && (typeof state==="undefined"?data:state).events.length===1')
   assert page.evaluate('(typeof state==="undefined"?data:state).events')==[fixture['event']],(name,'packet did not restore exact event')
   page.evaluate(await_input,path.read_text());assert page.evaluate(COUNT)['count']==1 and page.evaluate('rejectedImportRaw') is None,(name,'roundtrip duplication')
   stored=page.evaluate('localStorage.getItem(KEY)')
   bad=copy.deepcopy(exported);e=events_obj(bad)['events'][0];e['id']='unsupported-field-event';e['unsupportedFutureField']='synthetic'
   page.evaluate(await_input,json.dumps(bad));assert page.evaluate('localStorage.getItem(KEY)')==stored and page.evaluate(COUNT)['count']==1,(name,'unknown field not rejected')
   bad=copy.deepcopy(exported);bad['format']='synthetic-future-format';events_obj(bad)['events'][0]['id']='unsupported-envelope-event'
   page.evaluate(await_input,json.dumps(bad));assert page.evaluate('localStorage.getItem(KEY)')==stored and page.evaluate(COUNT)['count']==1,(name,'unknown envelope fell back')
   bad=copy.deepcopy(exported);e=events_obj(bad)['events'][0];e['id']='unsupported-version-event';e['questionVersion']=999999
   page.evaluate(await_input,json.dumps(bad));assert page.evaluate('localStorage.getItem(KEY)')==stored and page.evaluate(COUNT)['count']==1,(name,'unknown version not rejected')
   with page.expect_download() as rejected_dl:page.locator('#prototype-rejected').click()
   rejected_path=OUT/(name+'.rejected.json');rejected_dl.value.save_as(rejected_path);assert json.loads(rejected_path.read_text())==bad,(name,'rejected raw not retained')
   for key,value in sentinels.items():assert page.evaluate('k=>localStorage.getItem(k)',key)==value,(name,'legacy changed',key)
   peer=ctx.new_page();peer.on('pageerror',lambda e:errors.append(str(e)));peer.goto(base+name)
   other=json.loads(stored);event=copy.deepcopy(fixture['event']);event['id']='independent-cross-tab';other['events'].append(event)
   peer.evaluate('raw=>localStorage.setItem(KEY,raw)',json.dumps(other));page.wait_for_function('() => (typeof state==="undefined"?data:state).events.length===2')
   peer.evaluate('localStorage.setItem(KEY,"{broken-other-tab")');page.wait_for_function('() => blocked===true')
   assert page.evaluate('localStorage.getItem(KEY)')=='{broken-other-tab',(name,'cross-tab invalid overwritten')
   peer.close();page.evaluate('raw=>localStorage.setItem(KEY,raw)',stored);page.reload()
   page.evaluate('(k)=>localStorage.setItem(k,"synthetic broken old raw")',legacykey);page.reload()
   assert page.evaluate(COUNT)=={'blocked':False,'dirty':False,'count':1},(name,'legacy corruption blocked separate trial')
   page.evaluate('localStorage.setItem(KEY,"{broken synthetic trial")');page.reload()
   assert page.evaluate(COUNT)['blocked'],(name,'trial corruption not protected')
   assert page.evaluate('localStorage.getItem(KEY)')=='{broken synthetic trial',(name,'broken trial overwritten')
   assert page.evaluate('k=>localStorage.getItem(k)',legacykey)=='synthetic broken old raw',(name,'broken legacy overwritten')
   results.append({'page':name,'key':fixture['key'],'legacy_unchanged':True,'no_automatic_copy':True,'old_reader_roundtrip':True,'export_import':True,'unknown_field_and_version_rejected':True,'old_and_rejected_raw_downloads':True,'cross_tab_valid_merge_and_invalid_protection':True,'legacy_and_trial_corruption_distinguished':True})
   ctx.close()
  browser.close()
 assert not attempts and not posts and not errors,(attempts,posts,errors)
 result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'results':results,'POST_attempts':len(attempts),'POST_server_arrivals':len(posts),'external_requests':len(external),'page_errors':errors}
 (OUT/'probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
finally:srv.shutdown()
