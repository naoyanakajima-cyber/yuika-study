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
out=[]; assets={}
for path in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
 url='https://unpkg.com/'+path;assets[url]=subprocess.check_output(['curl','-fsSL','--max-time','30',url])
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  c=browser.new_context(viewport={'width':768,'height':1024})
  def route(r):
   if r.request.url.startswith(base):r.continue_()
   elif r.request.url in assets:r.fulfill(body=assets[r.request.url],content_type='application/javascript')
   else:r.abort()
  c.route('**/*',route);p=c.new_page();p.on('dialog',lambda d:d.accept())
  for entry in ['onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html']:
   p.goto(base+entry);p.locator('#start').wait_for()
   fixture=p.evaluate("""()=>{const science=typeof byId!=='undefined',qs=QUESTIONS.filter(q=>q.type==='text'||q.type==='choice').slice(0,4);const mk=(q,days,correct)=>{const at=new Date(Date.now()-days*86400000).toISOString();const common={id:crypto.randomUUID(),sessionId:'synthetic-qa',questionId:q.id,unit:q.unit,question:q.prompt,response:correct?q.answer:(q.type==='choice'?q.options.find(o=>o!==q.answer):'合成誤答'),expected:science?q.answer:expectedOf(q,'normal'),explanation:q.explanation,correct,mode:'normal'};return validateEvent(science?{...common,inputRaw:common.response,type:q.type,datasetVersion:VERSION,answeredAt:at,timezoneOffset:0,localDay:localDay(at,0),hintUsed:false}:{...common,...(typeof UNIT_ID==='undefined'?{reflection:''}:{unitId:UNIT_ID}),version:VERSION,course:q.course,variant:'normal',hint:false,at,offset:0,day:day(at,0)});};const v=science?state:data;v.events=qs.flatMap(q=>[mk(q,4,false),mk(q,3,false)]);v.events.push(mk(qs[0],2,true));return {key:KEY,value:v,unit:qs[0].unit,course:qs[0].course};}""")
   configs=[{'count':10,'course':'all','unit':'all','variant':'normal'},{'count':10,'course':fixture.get('course','all'),'unit':fixture['unit'],'variant':'normal'}]
   if entry!='yuika-review-v2.html':configs +=[{'count':15,'course':'all','unit':'all','variant':'kanji'},{'count':5,'course':'all','unit':'all','variant':'yomi'}]
   for cfg in configs:
    p.evaluate('([k,v,c])=>{localStorage.setItem(k,JSON.stringify(v));localStorage.setItem(k+"-preferences-v1",JSON.stringify(c))}',[fixture['key'],fixture['value'],cfg]);p.reload();p.locator('#daily-five').wait_for();p.add_script_tag(url=base+'assets/progress.js')
    result=p.evaluate("""()=>{const science=typeof byId!=='undefined',due=science?scienceDue():dueReviews(),weak=science?scienceWeak():additional(),qs=science?scienceDaily():dailyQuestions();const ds=new Set(due.map(s=>s.originId)),ws=new Set(weak.map(s=>s.originId)),actual={dueCount:0,weakCount:0,normalCount:0};for(const q of qs){const id=q.originId||q.id;actual[ds.has(id)?'dueCount':ws.has(id)?'weakCount':'normalCount']++;}return {summary:YuikaDesign.summary(location.pathname.split('/').pop()),actual,total:qs.length,button:document.querySelector('#daily-five').textContent}}""")
    p.locator('#daily-five').click(); result['started']=p.evaluate("typeof byId!=='undefined'?session.questions.length:run.qs.length")
    out.append({'entry':entry,'config':cfg,**result})
  p.goto(base+'onin-review.html');p.locator('#start').wait_for();key=p.evaluate('KEY');p.evaluate('k=>{localStorage.setItem(k,JSON.stringify({events:[]}));localStorage.setItem("yuika-prototype-v1:last-daily-unit","onin-review.html")}',key)
  p.goto(base+'index.html');p.locator('.unit-card').first.wait_for()
  out.append({'case':'corrupt_home_actual_text','panel':p.locator('.daily-panel').inner_text(),'card':p.locator('.unit-card').filter(has_text='応仁の乱').inner_text()})
  p.screenshot(path=str(OUT/'corrupt-home.png'))
  p.get_by_role('button',name='今日の5問をはじめる',exact=True).click();p.locator('#daily-five').wait_for();out.append({'case':'corrupt_destination','disabled':p.locator('#daily-five').is_disabled(),'notice':p.locator('body').inner_text()[:300]})
  browser.close()
(OUT/'selection-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
