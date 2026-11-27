"""Independent synthetic reason/reload and math parent-isolation spot checks."""
import datetime,json,os,pathlib,sys
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(sys.argv[1]);OUT=pathlib.Path(__file__).parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
results=[]
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for parent in (False,True):
   ctx=browser.new_context(viewport={'width':768,'height':1024});page=ctx.new_page();posts=[];errors=[]
   def route(r):
    if r.request.method=='POST':posts.append(r.request.url);r.abort()
    elif r.request.url.startswith(base):r.continue_()
    else:r.abort()
   ctx.route('**/*',route);page.on('pageerror',lambda e:errors.append(str(e)))
   page.clock.set_fixed_time(datetime.datetime(2030,1,3,tzinfo=datetime.timezone.utc))
   page.goto(base+'onin-review.html'+('?parent-check=1' if parent else ''))
   if parent:expect(page.locator('#parent-check-banner')).to_be_visible()
   before=page.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
   page.evaluate('''()=>{const q=QUESTIONS[0],at='2030-01-02T23:00:00.000Z',v='normal';data={...empty(),events:[validateEvent({id:'synthetic-qa-pr32-00001',sessionId:'synthetic-qa-session',questionId:q.id,questionVersion:currentQuestionVersion(q),unitId:UNIT_ID,version:VERSION,unit:q.unit,course:q.course,question:promptOf(q,v),response:q.type==='text'?'合成の誤答':q.options.find(o=>o!==q.answer),expected:expectedOf(q,v),explanation:q.explanation,correct:false,variant:v,mode:'normal',hint:false,at,offset:0,day:day(at,0)})]};YuikaParent.storage.setItem(KEY,JSON.stringify(data));go('home');}''')
   expect(page.locator('#recommended-count')).to_contain_text('今回は 1問');page.locator('#recommended-start').click()
   expect(page.locator('#recommended-reasons')).to_contain_text('前の回答をもう一度確かめよう')
   q=page.evaluate('run.qs[run.index]')
   if q['type']=='text':page.locator('#response').fill(q['answer'])
   else:page.locator('[data-choice]').filter(has_text=q['answer']).first.click()
   page.locator('#check').click();expect(page.locator('#feedback')).to_contain_text('回答を保存しました')
   page.screenshot(path=str(OUT/('onin-parent.png' if parent else 'onin-normal.png')),full_page=True)
   page.locator('#next').click();assert page.evaluate('data.events.length')==2
   page.reload();assert page.evaluate('data.events.length')==2
   if parent:assert page.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==before
   assert not posts and not errors
   results.append({'page':'onin-review.html','parent':parent,'reason_visible':True,'answered_and_reloaded_events':2,'normal_storage_unchanged':True if parent else None,'posts':len(posts),'pageerrors':errors})
   ctx.close()
  for parent in (False,True):
   ctx=browser.new_context(viewport={'width':768,'height':1024});page=ctx.new_page();posts=[];errors=[]
   ctx.route('**/*',route);page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(base+'math-passage-review.html'+('?parent-check=1' if parent else ''))
   if parent:expect(page.locator('#parent-check-banner')).to_be_visible()
   before=page.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
   page.locator('[data-stage="0"]').click();page.get_by_role('button',name=page.evaluate('QUESTIONS[0].answer'),exact=True).click();page.locator('#check').click()
   page.screenshot(path=str(OUT/('math-parent.png' if parent else 'math-normal.png')),full_page=True)
   page.locator('#end').click();expect(page.locator('#main')).to_contain_text('途中終了')
   assert page.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==before
   assert not posts and not errors
   results.append({'page':'math-passage-review.html','parent':parent,'stage0_answer_and_partial_end':True,'normal_storage_unchanged':True,'posts':len(posts),'pageerrors':errors})
   ctx.close()
  browser.close()
(OUT/'ui-probe-result.json').write_text(json.dumps({'contexts':results,'scope':'Synthetic only; external traffic blocked; math notification config disabled; mock delivery validated by math_passage suite.'},ensure_ascii=False,indent=2)+'\n')
print('independent UI probe PASS: four contexts, zero outgoing POST/pageerror')
