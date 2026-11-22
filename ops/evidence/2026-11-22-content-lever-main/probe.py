from pathlib import Path
import json,os,runpy,subprocess,time
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
R=Path('/workspace/yuika-content-lever-qa');O=Path('/workspace/qa-content-lever-evidence')
HEAD='ee228ca0a1865d0a56f4302cd9342a4f66738561';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==HEAD
Handler=runpy.run_path(str(R/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
 def log_message(self,*a):pass
INIT='''(()=>{if(!location.pathname.endsWith('/content-review.html'))return;window.qaInitial=JSON.stringify(Object.entries(localStorage).sort());window.qaSession=JSON.stringify(Object.entries(sessionStorage).sort());window.qaWrites=[];for(const k of ['setItem','removeItem','clear']){const old=Storage.prototype[k];Storage.prototype[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}const d=Object.getOwnPropertyDescriptor(Document.prototype,'cookie');if(d&&d.set)Object.defineProperty(Document.prototype,'cookie',{get:d.get,set(v){qaWrites.push('cookie');d.set.call(this,v);}});for(const k of ['pushState','replaceState']){const old=history[k];history[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}for(const [o,k] of [[indexedDB,'open'],[indexedDB,'deleteDatabase'],[caches,'open'],[caches,'delete'],[navigator.serviceWorker,'register']]){if(o&&o[k]){const old=o[k].bind(o);o[k]=function(...a){qaWrites.push(k);return old(...a);};}}})();'''
results=[];blocked=[];errors=[];phase='seed';posts=[]
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(R))) as srv:
 Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True)
  ctx.add_init_script(INIT);ctx.add_init_script(path=str(R/'tests/seed_random.js'))
  def route(r):
   if r.request.method!='GET':posts.append({'phase':phase,'url':r.request.url,'method':r.request.method})
   allowed=r.request.url.startswith(base+'/') and r.request.method=='GET' and (phase!='content' or r.request.url==base+'/content-review.html')
   if allowed:r.continue_()
   else:blocked.append({'phase':phase,'url':r.request.url,'method':r.request.method});r.abort()
  ctx.route('**/*',route);p=ctx.new_page();p.set_default_timeout(6000)
  p.on('pageerror',lambda e:errors.append({'phase':phase,'error':str(e)}));p.on('dialog',lambda d:d.accept())
  # Seed an actual synthetic learning event by the real science answer controls.
  p.goto(base+'/yuika-review-v2.html')
  question=p.evaluate("byId.get('lever-01')")
  p.evaluate("session={id:uid(),mode:'unit',questions:[byId.get('lever-01')],index:0,results:[],hint:false,selected:null,answered:false,done:false};view='quiz';render()")
  if question['type']=='number':p.locator('#numeric').fill(str(question['answer']))
  else:p.locator('[data-choice]').nth(question['options'].index(question['answer'])).click()
  p.locator('#check').click();expect(p.locator('#feedback')).to_contain_text('回答を保存しました')
  assert p.evaluate("state.events.length===1&&state.events[0].questionId==='lever-01'")
  stored=p.evaluate('JSON.stringify(Object.entries(localStorage).sort())')
  event=p.evaluate('JSON.stringify(state.events[0])');results.append('Real synthetic lever answer saved through science controls before CONTENT')
  phase='content';response=p.goto(base+'/content-review.html')
  assert "connect-src 'none'" in response.headers['content-security-policy']
  assert p.evaluate('qaInitial')==stored
  def snap():return p.evaluate('JSON.stringify({proposal,unsaved})')
  def export():
   with p.expect_download() as dl:p.locator('#export-confirmed').click()
   return json.loads(Path(dl.value.path()).read_text())
  def load(value):
   p.locator('#import').set_input_files({'name':'synthetic-only.json','mimeType':'application/json','buffer':json.dumps(value,ensure_ascii=False).encode()})
   expect(p.locator('#import')).to_have_value('')
  for source,answer in [('triangle','3'),('text','こおり')]:
   p.locator('#sample-'+source).focus();p.keyboard.press('Enter')
   expect(p.locator('#trial-start')).to_be_disabled();p.evaluate('startTrial()');assert p.evaluate('trial===null')
   if source=='triangle':
    expect(p.locator('#source-preview svg')).to_be_visible();expect(p.locator('#source-preview')).to_contain_text('三角形の辺は3本です。')
    expect(p.locator('#confirm-0')).to_be_disabled();p.locator('.grid').screenshot(path=str(O/'triangle-source-768.png'))
    revision=p.evaluate('proposal.revision');p.locator('#transcription').fill('三角形の辺は3本です。');p.locator('#resolution-0').fill('3')
    assert p.evaluate('proposal.revision')==revision+2
    assert p.evaluate('proposal.transcription.uncertainties[0]')=={'id':'synthetic-triangle-uncertainty-001','quote':'［確認待ち］','candidates':['3','4'],'resolution':'3'}
   expect(p.locator('#trial-start')).to_be_disabled()
   p.locator('#confirm-0').focus();p.keyboard.press('Enter');expect(p.locator('#trial-start')).to_be_enabled()
   before=snap();p.locator('#trial-start').focus();p.keyboard.press('Enter')
   expect(p.locator('#trial-title')).to_be_focused();expect(p.locator('#editor')).to_be_hidden();assert p.locator('#editor').evaluate('e=>e.inert')
   p.keyboard.press('Tab');expect(p.locator('#trial-answer')).to_be_focused();p.locator('#trial-answer').fill(answer)
   p.locator('#trial-grade').click();expect(p.locator('#trial-result')).to_have_text('登録した答えに一致しました')
   assert snap()==before;assert p.evaluate('qaWrites')==[]
   p.wait_for_timeout(150);p.screenshot(path=str(O/(source+'-graded-768x1024.png')),full_page=True)
   p.locator('#trial-exit').click();assert p.evaluate('trial===null');assert p.locator('#trial-panel').inner_html()=='';assert snap()==before
   output=export();assert output['schemaVersion']==1 and set(output)==set(json.loads((R/'docs/product/fixtures/synthetic-content.json').read_text()))
   assert output==p.evaluate('proposal')
   # Exported state is saved; a second start/end must preserve unsaved=false too.
   assert not p.evaluate('unsaved');before=snap();p.locator('#trial-start').click();expect(p.locator('#trial-answer')).to_have_value('');p.locator('#trial-exit').click();assert snap()==before
   load(output);assert p.evaluate('proposal.questions.every(q=>q.status==="draft"&&q.confirmedRevision===null)');expect(p.locator('#trial-start')).to_be_disabled()
   p.locator('#confirm-0').click();p.locator('#q-0-hint').fill('合成QA：原本の内容を確かめてください。');expect(p.locator('#trial-start')).to_be_disabled();p.evaluate('startTrial()');assert p.evaluate('trial===null')
   assert p.evaluate('JSON.stringify(Object.entries(localStorage).sort())')==stored
   results.append(source+': explicit confirmation -> actual answer/grade -> exit clears -> schema1 export/reimport draft; edits refuse; proposal/confirmation/unsaved retained')
  writes=p.evaluate('qaWrites');assert writes==[]
  assert p.evaluate('JSON.stringify(Object.entries(localStorage).sort())===qaInitial&&JSON.stringify(Object.entries(sessionStorage).sort())===qaSession&&window.name===""&&location.search===""&&location.hash===""')
  assert not [x for x in blocked if x['phase']=='content']
  p.reload();assert p.evaluate('proposal===null&&trial===null');assert p.evaluate('JSON.stringify(Object.entries(localStorage).sort())')==stored
  results.append('CONTENT reload clears proposal/trial and preserves existing synthetic science bytes')
  phase='readback';p.goto(base+'/yuika-review-v2.html');assert p.evaluate('JSON.stringify(state.events[0])')==event;assert p.evaluate('state.events.length')==1
  assert p.evaluate('JSON.stringify(Object.entries(localStorage).sort())')==stored
  assert errors==[] and posts==[],(errors,posts)
  results.append('Science reload reads identical real synthetic lever event and no extra history')
  ctx.close();browser.close()
 srv.shutdown()
result={'head':HEAD,'viewport':[768,1024],'cases':results,'writes_during_content':writes,'blocked_requests':blocked,'post_attempts':posts,'page_errors':errors,'real_synthetic_science_record_preserved':True,'no_private_data':True}
(O/'probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
