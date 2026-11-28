import json, os, sys, subprocess
from pathlib import Path
from threading import Thread
from functools import partial
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT=Path(os.environ.get('YUIKA_QA_ROOT','/workspace/yuika-pr25-review-20261112'));sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Quiet(PreviewHandler):
 def log_message(self,*args):pass
OUT=Path(os.environ.get('YUIKA_QA_OUT','/tmp/yuika-pr25-qa'));OUT.mkdir(parents=True,exist_ok=True)
out=[]
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for entry in ['onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html']:
   c=browser.new_context();c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort());p=c.new_page()
   p.goto(base+entry);p.locator('#start').wait_for();p.add_script_tag(url=base+'assets/progress.js')
   initial=p.evaluate("""()=>({key:KEY,empty:typeof state!=='undefined'?state:data,summary:YuikaDesign.summary(location.pathname.split('/').pop())})""")
   key=initial['key'];empty=initial['empty']
   for case,raw in [('missing_schema',{'events':[]}),('wrong_version',{**empty,'datasetVersion':'future-version'}),('valid_empty',empty),('bad_json','{')]:
    rawstring=raw if isinstance(raw,str) else json.dumps(raw)
    p.evaluate('([k,v])=>localStorage.setItem(k,v)',[key,rawstring]);p.reload();p.locator('#start').wait_for();p.add_script_tag(url=base+'assets/progress.js')
    result=p.evaluate("""()=>({summary:YuikaDesign.summary(location.pathname.split('/').pop()),blocked:typeof blocked!=='undefined'?blocked:null,dailyDisabled:document.querySelector('#daily-five')?.disabled??document.querySelector('#science-daily')?.disabled,unchanged:YuikaParent.storage.getItem(KEY)})""")
    result['unchanged']=result['unchanged']==rawstring
    out.append({'entry':entry,'case':case,**result})
   p.evaluate('([k,v])=>localStorage.setItem(k,v)',[key,json.dumps(empty)]);p.reload();p.locator('#start').wait_for();p.add_script_tag(url=base+'assets/progress.js')
   synth=p.evaluate("""()=>{const science=typeof byId!=='undefined',q=QUESTIONS.find(q=>q.type==='text'||q.type==='choice');const at=new Date(Date.now()+86400000).toISOString();const common={id:crypto.randomUUID(),sessionId:'synthetic-qa',questionId:q.id,unit:q.unit,question:q.prompt,response:q.answer,expected:science?q.answer:expectedOf(q,'normal'),explanation:q.explanation,correct:true,mode:'normal'};const e=validateEvent(science?{...common,inputRaw:common.response,type:q.type,datasetVersion:VERSION,answeredAt:at,timezoneOffset:0,localDay:localDay(at,0),hintUsed:false}:{...common,...(typeof UNIT_ID==='undefined'?{reflection:''}:{unitId:UNIT_ID}),version:VERSION,course:q.course,variant:'normal',hint:false,at,offset:0,day:day(at,0)});const v=science?state:data;v.events=[e];return v;}""")
   p.evaluate('([k,v])=>localStorage.setItem(k,v)',[key,json.dumps(synth)]);p.reload();p.locator('#start').wait_for();p.add_script_tag(url=base+'assets/progress.js')
   out.append({'entry':entry,'case':'future_valid',**p.evaluate("""()=>({summary:YuikaDesign.summary(location.pathname.split('/').pop()),dailyDisabled:document.querySelector('#daily-five')?.disabled??document.querySelector('#science-daily')?.disabled})""")})
   out.append({'entry':entry,'case':'read_refusal','summary':p.evaluate("""()=>{const orig=YuikaParent.storage.getItem;YuikaParent.storage.getItem=()=>{throw Error('synthetic refusal')};try{return YuikaDesign.summary(location.pathname.split('/').pop())}finally{YuikaParent.storage.getItem=orig;}}""")})
   before=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
   p.goto(base+entry+'?parent-check=1');p.locator('#start').wait_for();p.add_script_tag(url=base+'assets/progress.js')
   out.append({'entry':entry,'case':'parent_isolation','summary':p.evaluate("YuikaDesign.summary(location.pathname.split('/').pop())"),'child_unchanged':before==p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')})
   c.close()
  browser.close()
(OUT/'probe-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
