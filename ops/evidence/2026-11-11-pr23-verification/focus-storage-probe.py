"""Synthetic four-app storage isolation and actual JSON file roundtrip."""
import json, os, sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
sys.path.insert(0,'/workspace/yuika-pr23-review-20261111')
from scripts.cloud.serve import PreviewHandler, ROOT
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{srv.server_port}'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for app in ('mock-focus-review.html',):
   ctx=browser.new_context(viewport={'width':768,'height':1024});page=ctx.new_page();posts=[];errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   def route(r):
    if r.request.method=='POST': posts.append(r.request.url);r.abort()
    elif not r.request.url.startswith(base+'/'):r.abort()
    else:r.continue_()
   page.route('**/*',route);page.goto(base+'/'+app)
   seed=page.evaluate('''()=>{
    const q=QUESTIONS.find(q=>prototypeScience?q.type==='number':q.type==='choice'),at='2026-11-01T00:00:00.000Z';
    const e=prototypeScience?{id:'synthetic-isolation-1',sessionId:'synthetic-isolation',questionId:q.id,questionVersion:1,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response:q.answer,inputRaw:String(q.answer),expected:q.answer,correct:true,answeredAt:at,timezoneOffset:0,localDay:localDay(at,0),hintUsed:false,mode:'normal',explanation:q.explanation}:
    {id:'synthetic-isolation-1',sessionId:'synthetic-isolation',questionId:q.id,questionVersion:1,version:VERSION,unit:q.unit,course:q.course,question:prototypeHeian?q.prompt:promptOf(q,'normal'),response:q.answer,expected:q.answer,explanation:q.explanation,correct:true,variant:'normal',mode:'normal',hint:false,at,offset:0,day:day(at,0),...(prototypeHeian?{reflection:''}:{unitId:UNIT_ID})};
    const payload={...(prototypeScience?emptyState():empty()),events:[validateEvent(e)]};
    const old=JSON.stringify(payload);localStorage.setItem(LEGACY_KEY,old);
    localStorage.setItem(LEGACY_KEY+'-preferences-v1','old-preferences');localStorage.setItem('yuika-last-daily-unit-v1','old-unit');
    if(prototypeScience)localStorage.setItem(OLD_KEY,JSON.stringify({attempts:10,correct:[1],wrong:[2]}));
    return {payload,old,key:KEY,oldKey:LEGACY_KEY};
   }''')
   page.reload()
   assert page.evaluate('(prototypeScience?state:data).events.length')==0
   if app=='yuika-review-v2.html':assert page.evaluate('state.legacy.length')==0
   assert not page.evaluate('blocked')
   page.evaluate('async p=>{await importFile(new File([JSON.stringify(p)],"synthetic-old.json"));}',seed['payload'])
   assert page.evaluate('(prototypeScience?state:data).events.length')==1
   page.evaluate('prototypeScience?rememberScience():rememberPrefs()')
   assert page.evaluate('localStorage.getItem(LEGACY_KEY)')==seed['old']
   assert page.evaluate("localStorage.getItem(LEGACY_KEY+'-preferences-v1')")=='old-preferences'
   assert page.evaluate("localStorage.getItem('yuika-last-daily-unit-v1')")=='old-unit'
   assert page.evaluate("localStorage.getItem('yuika-prototype-v1:last-daily-unit')")==app
   page.evaluate('records()')
   with page.expect_download() as dl:page.locator('#export').click()
   exported_bytes=Path(dl.value.path()).read_bytes()
   packet=json.loads(exported_bytes)
   assert packet['format']=='yuika-review-prototype' and packet['formatVersion']==1
   assert packet['payload']==seed['payload'],(app,packet['payload'],seed['payload'])
   # Restore actual downloaded bytes into an empty trial; a no-op cannot pass.
   page.evaluate('localStorage.removeItem(KEY)');page.reload()
   assert page.evaluate('(prototypeScience?state:data).events.length')==0
   assert page.evaluate('localStorage.getItem(LEGACY_KEY)')==seed['old']
   page.evaluate('records()')
   page.locator('#import').set_input_files({'name':'trial.json','mimeType':'application/json','buffer':exported_bytes})
   page.wait_for_function('() => rejectedImportRaw===null && (prototypeScience?state:data).events.length===1')
   assert page.evaluate('prototypeScience?state:data')==seed['payload']
   # A second import of those same bytes must preserve all fields and deduplicate.
   page.evaluate('async raw=>{await importFile(new File([raw],"same-trial.json"));}',exported_bytes.decode())
   assert page.evaluate('prototypeScience?state:data')==seed['payload']
   assert page.evaluate('rejectedImportRaw') is None
   snapshot=page.evaluate('localStorage.getItem(KEY)')
   for mutate in ('unknown_field','unknown_envelope','unknown_id','unknown_mode','collision'):
    bad=json.loads(json.dumps(packet))
    if mutate=='unknown_field':
     bad['payload']['events'][0]['id']='synthetic-unknown-field'
     bad['payload']['events'][0]['futureObservation']='preserve-me'
    elif mutate=='unknown_envelope':bad['formatVersion']=999
    elif mutate=='unknown_id':bad['payload']['events'][0]['questionId']='synthetic-unknown-question'
    elif mutate=='unknown_mode':bad['payload']['events'][0]['mode']='future-mode'
    else:bad['payload']['events'][0]['sessionId']='synthetic-conflict'
    raw=json.dumps(bad)
    page.evaluate('async raw=>{await importFile(new File([raw],"rejected.json"));}',raw)
    assert page.evaluate('localStorage.getItem(KEY)')==snapshot
    assert page.evaluate('rejectedImportRaw')==raw
    with page.expect_download() as rejected:page.locator('#prototype-rejected').click()
    assert Path(rejected.value.path()).read_text()==raw
   # Quota failure cannot partially apply an otherwise valid import.
   good=json.loads(json.dumps(packet));good['payload']['events'][0]['id']='synthetic-isolation-2'
   page.evaluate('''()=>{window.originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===KEY)throw Error('synthetic quota');return originalSet.call(this,k,v);};}''')
   page.evaluate('async p=>{await importFile(new File([JSON.stringify(p)],"quota.json"));}',good)
   assert page.evaluate('localStorage.getItem(KEY)')==snapshot
   assert page.evaluate('(prototypeScience?state:data).events.length')==1
   page.evaluate('()=>{Storage.prototype.setItem=originalSet;}')
   page.evaluate('async p=>{await importFile(new File([JSON.stringify(p)],"retry.json"));}',good)
   assert page.evaluate('(prototypeScience?state:data).events.length')==2
   page.reload();assert page.evaluate('(prototypeScience?state:data).events.length')==2
   assert page.evaluate('localStorage.getItem(LEGACY_KEY)')==seed['old']
   if app=='yuika-review-v2.html':
    old_aggregate=page.evaluate('localStorage.getItem(OLD_KEY)')
    page.evaluate('async raw=>{await importFile(new File([raw],"synthetic-aggregate.json"));}',old_aggregate)
    assert page.evaluate('state.legacy.length')==1
    assert page.evaluate('state.legacy[0].raw')==old_aggregate
    assert page.evaluate('localStorage.getItem(OLD_KEY)')==old_aggregate
    unknown_aggregate=json.dumps({'attempts':10,'correct':[1],'wrong':[2],'schemaVersion':999})
    old_snapshot=page.evaluate('localStorage.getItem(KEY)')
    page.evaluate('async raw=>{await importFile(new File([raw],"unknown-aggregate.json"));}',unknown_aggregate)
    assert page.evaluate('rejectedImportRaw')==unknown_aggregate
    assert page.evaluate('localStorage.getItem(KEY)')==old_snapshot
   # Old malformed storage is separate from a malformed trial store.
   page.evaluate("localStorage.setItem(LEGACY_KEY,'old-invalid');localStorage.removeItem(KEY)")
   page.reload();assert not page.evaluate('blocked')
   assert '元の保存先のJSONは読み取れません' in page.locator('#prototype-notice').inner_text()
   page.evaluate("localStorage.setItem(KEY,'trial-invalid')");page.reload();assert page.evaluate('blocked')
   page.evaluate('records()')
   assert page.evaluate('localStorage.getItem(LEGACY_KEY)')=='old-invalid'
   with page.expect_download() as old:page.locator('#prototype-original').click()
   assert Path(old.value.path()).read_text()=='old-invalid'
   assert page.evaluate('prototypeScience?persist():save()') is False
   assert page.evaluate('localStorage.getItem(KEY)')=='trial-invalid'
   # Empty bytes are corrupt JSON too, never an absent store.
   page.evaluate("localStorage.setItem(KEY,'')");page.reload()
   assert page.evaluate('blocked')
   assert page.evaluate('prototypeScience?persist():save()') is False
   assert page.evaluate('localStorage.getItem(KEY)')==''
   page.evaluate('records()')
   with page.expect_download() as empty_raw:page.locator('#rawBroken' if app=='yuika-review-v2.html' else '#broken').click()
   assert Path(empty_raw.value.path()).read_bytes()==b''
   assert not posts and not errors,(posts,errors)
   ctx.close()
  browser.close()
 print('independent focus storage probe: new focus app, original bytes/prefs intact, envelope/unknown fields, actual downloads/import, quota and broken stores PASS')
finally:srv.shutdown()
