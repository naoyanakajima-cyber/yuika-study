"""Independent synthetic lever record roundtrip, normal and parent modes."""
import json, os, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright, expect
ROOT=Path('/workspace/qa-theme-generator-checkout')
OUT=Path('/workspace/qa-theme-generator-evidence')
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class QuietHandler(PreviewHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{srv.server_port}'
result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'cases':[],'post_requests':[],'page_errors':[],'external_gets_aborted':0}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH','/usr/bin/chromium'))
  for mode in ('normal','parent'):
   ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True)
   page=ctx.new_page();page.on('pageerror',lambda e:result['page_errors'].append(str(e)))
   def route(r):
    if r.request.method=='POST':result['post_requests'].append(r.request.url);r.abort()
    elif not r.request.url.startswith(base+'/'):result['external_gets_aborted']+=1;r.abort()
    else:r.continue_()
   page.route('**/*',route)
   page.goto(base+'/yuika-review-v2.html?unit=rika-lever')
   page.evaluate("localStorage.setItem('qa-child-sentinel','synthetic-unchanged')")
   before_disk=page.evaluate('Object.fromEntries(Object.entries(localStorage))')
   if mode=='parent':
    page.goto(base+'/yuika-review-v2.html?unit=rika-lever&parent-check=1')
    expect(page.locator('#parent-check-banner')).to_be_visible()
   q=page.evaluate("""() => {const q=QUESTIONS.find(q=>q.id.startsWith('lever-')&&q.type==='number'&&q.answerUnit==='cm'&&q.numericTags);
    session={id:uid(),mode:'unit',questions:[q],index:0,results:[],hint:false,selected:null,answered:false,done:false};view='quiz';render();return q;}""")
   wrong=next(iter(q['numericTags']))
   page.locator('#numeric').fill(wrong);page.locator('#check').click()
   expect(page.locator('#feedback')).to_contain_text(q['steps'][-1])
   event=page.evaluate('session.results.at(-1)')
   assert event['answerUnit']=='cm' and event['answerTag']==q['numericTags'][wrong] and not event['correct']
   # Unit/tag flow measured; no extra screenshot beyond theme artifacts.
   page.reload();assert page.evaluate('state.events')==[event]
   page.evaluate('records()')
   with page.expect_download() as d:page.locator('#export').click()
   data=Path(d.value.path()).read_bytes();packet=json.loads(data)
   assert packet['payload']['events']==[event]
   page.evaluate('YuikaParent.storage.removeItem(KEY)');page.reload()
   assert page.evaluate('state.events.length')==0
   page.evaluate('records()')
   page.locator('#import').set_input_files({'name':'synthetic-lever.json','mimeType':'application/json','buffer':data})
   page.wait_for_function('rejectedImportRaw===null && state.events.length===1')
   assert page.evaluate('state.events')==[event]
   page.reload();assert page.evaluate('state.events')==[event]
   # Fieldless previous schema is still valid; same question/answer and a distinct synthetic ID.
   fieldless=json.loads(json.dumps(packet));old=fieldless['payload']['events'][0]
   old.pop('answerUnit');old.pop('answerTag');old['id']='synthetic-fieldless-lever-1'
   page.evaluate('async p=>await importFile(new File([JSON.stringify(p)],"fieldless.json"))',fieldless)
   assert page.evaluate('rejectedImportRaw') is None
   assert page.evaluate('state.events.length')==2
   accepted=page.evaluate('state.events');saved=page.evaluate('YuikaParent.storage.getItem(KEY)')
   rejected=[]
   for label,field,value in [('invalid_unit','answerUnit','kg'),('invalid_tag','answerTag','synthetic-unregistered-tag'),('unknown_field','unregisteredField','synthetic-only')]:
    bad=json.loads(json.dumps(packet));bad['payload']['events'][0]['id']='synthetic-rejected-'+label;bad['payload']['events'][0][field]=value
    raw=json.dumps(bad,ensure_ascii=False)
    page.evaluate('async raw=>await importFile(new File([raw],"invalid.json"))',raw)
    assert page.evaluate('rejectedImportRaw')==raw
    assert page.evaluate('state.events')==accepted
    assert page.evaluate('YuikaParent.storage.getItem(KEY)')==saved
    rejected.append(label)
   page.reload();assert page.evaluate('state.events')==accepted
   if mode=='parent':assert page.evaluate('Object.fromEntries(Object.entries(localStorage))')==before_disk
   result['cases'].append({'mode':mode,'question_id':q['id'],'actual_numeric_answer_unit_tag_saved':True,'reload_preserved':True,'actual_export_and_file_import_preserved':True,'fieldless_record_accepted':True,'invalid_packets_rejected_without_writes':rejected,'record_count_after_roundtrip':2,'parent_child_storage_unchanged':True if mode=='parent' else None})
   ctx.close()
  browser.close()
 assert not result['post_requests'] and not result['page_errors'],result
 result['completed_at']=datetime.now(timezone.utc).isoformat();result['result']='passed'
 (OUT/'science-probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('PASS independent normal/parent lever units/tags, actual JSON download/import, fieldless old record, invalid rejection, no POST/pageerror')
finally:srv.shutdown();srv.server_close()
