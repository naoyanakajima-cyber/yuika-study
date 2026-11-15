from pathlib import Path
import json,os,runpy,subprocess,sys,copy
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
R=Path('/workspace/yuika-content-image-trial-20261115');O=Path('/tmp/yuika-cycle34-qa');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head==sys.argv[1]
fixture=json.loads((R/'docs/product/fixtures/synthetic-triangle-content.json').read_text());Handler=runpy.run_path(str(R/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
 def log_message(self,*a):pass
INIT='''(()=>{localStorage.setItem('yuika-prototype-v1:yuika-science-review-v2','{"synthetic":"preserve-byte-for-byte"}');window.qaInitial=JSON.stringify(Object.entries(localStorage).sort());window.qaWrites=[];for(const k of ['setItem','removeItem','clear']){const old=Storage.prototype[k];Storage.prototype[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}const d=Object.getOwnPropertyDescriptor(Document.prototype,'cookie');if(d&&d.set)Object.defineProperty(Document.prototype,'cookie',{get:d.get,set(v){qaWrites.push('cookie');d.set.call(this,v);}});for(const k of ['pushState','replaceState']){const old=history[k];history[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}for(const [o,k] of [[indexedDB,'open'],[indexedDB,'deleteDatabase'],[caches,'open'],[caches,'delete'],[navigator.serviceWorker,'register']]){if(o&&o[k]){const old=o[k].bind(o);o[k]=function(...a){qaWrites.push(k);return old(...a);};}}})();'''
results=[];requests=[];errors=[];dialogs=[];accept=True
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(R))) as srv:
 Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'));ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True);ctx.add_init_script(INIT)
  def route(r):
   if r.request.url==base+'/content-review.html' and r.request.method=='GET':r.continue_()
   else:requests.append({'url':r.request.url,'method':r.request.method});r.abort()
  ctx.route('**/*',route);p=ctx.new_page();p.set_default_timeout(5000);p.on('pageerror',lambda e:errors.append(str(e)))
  def dialog(d):dialogs.append(d.type);d.accept() if accept else d.dismiss()
  p.on('dialog',dialog);p.goto(base+'/content-review.html')
  def snap():return p.evaluate('JSON.stringify({proposal,unsaved})')
  def download(selector):
   with p.expect_download() as dl:p.locator(selector).click()
   return json.loads(Path(dl.value.path()).read_text())
  def load(v):
   p.locator('#import').set_input_files({'name':'synthetic-only.json','mimeType':'application/json','buffer':json.dumps(v).encode()});expect(p.locator('#import')).to_have_value('')
  def assert_triangle():expect(p.locator('#source-preview svg')).to_be_visible();expect(p.locator('#source-preview')).to_contain_text('三角形')
  p.locator('#sample-triangle').focus();p.keyboard.press('Enter');assert_triangle();expect(p.locator('#confirm-0')).to_be_disabled();expect(p.locator('#trial-start')).to_be_disabled();assert p.evaluate('proposal.questions[0].status')=='draft';assert p.evaluate('proposal.transcription.uncertainties[0].resolution') is None
  p.locator('.grid').screenshot(path=str(O/'source-and-transcription-768.png'));results.append('initial readable triangle asset, draft/unresolved gate')
  draft=download('#export-draft');assert draft==fixture;load(draft);assert_triangle();expect(p.locator('#trial-start')).to_be_disabled();results.append('draft download/reimport retains correct asset and gate')
  rev=p.evaluate('proposal.revision');p.locator('#transcription').fill('三角形の辺は3本です。');assert p.evaluate('proposal.revision')==rev+1;expect(p.locator('#confirm-0')).to_be_disabled()
  p.locator('#trial-repair').focus();p.keyboard.press('Enter');expect(p.locator('#resolution-0')).to_be_focused();p.locator('#resolution-0').fill('3');assert p.evaluate('proposal.revision')==rev+2;expect(p.locator('#trial-start')).to_be_disabled();assert p.evaluate('proposal.transcription.uncertainties[0].quote')=='［確認待ち］';assert p.evaluate('proposal.transcription.uncertainties[0].candidates')==['3','4'];results.append('explicit transcription+resolution, revision increments, quote/candidates retained')
  p.locator('#confirm-0').focus();p.keyboard.press('Enter');expect(p.locator('#trial-start')).to_be_enabled();confirmed=download('#export-confirmed');assert confirmed['schemaVersion']==1 and confirmed['questions'][0]['status']=='confirmed';assert 'asset' not in confirmed and 'trial' not in confirmed;results.append('explicit keyboard confirmation and schema1 export')
  for answer,match in [('3',True),('4',False)]:
   before=snap();p.locator('#trial-start').focus();p.keyboard.press('Enter');expect(p.locator('#editor')).to_be_hidden();expect(p.locator('#trial-title')).to_be_focused();p.keyboard.press('Tab');expect(p.locator('#trial-answer')).to_be_focused();p.locator('#trial-answer').fill(answer)
   p.evaluate('document.getElementById("sample-triangle").click();document.getElementById("sample-image").click();exportProposal(false)');assert snap()==before
   p.locator('#trial-grade').click();expect(p.locator('#trial-result')).to_contain_text('登録した答えに一致しました' if match else '登録した答えとは一致しません');expect(p.locator('#trial-answer')).to_be_disabled();assert snap()==before
   if match:p.wait_for_timeout(150);p.screenshot(path=str(O/'trial-match-768x1024.png'),full_page=True)
   p.locator('#trial-exit').click();assert p.evaluate('trial===null');assert p.locator('#trial-panel').inner_text()=='';assert snap()==before;results.append('grade '+answer+' and exit, snapshot unchanged, runtime sample/export guards')
  assert download('#export-confirmed')==confirmed;load(confirmed);assert_triangle();assert p.evaluate('proposal.questions.every(q=>q.status==="draft"&&q.confirmedRevision===null)');expect(p.locator('#trial-start')).to_be_disabled();p.locator('#confirm-0').click();p.locator('#q-0-hint').fill('線を1本ずつ確かめましょう。');expect(p.locator('#trial-start')).to_be_disabled();assert p.evaluate('proposal.questions[0].status')=='draft';results.append('confirmed import resets confirmation; editing invalidates')
  before=snap();accept=False;p.locator('#sample-image').click();assert snap()==before;accept=True;p.locator('#sample-image').click();expect(p.locator('#source-preview')).to_contain_text('［判読不明］');assert '三角形の辺' not in p.locator('#source-preview').inner_text();expect(p.locator('#confirm-0')).to_be_disabled();expect(p.locator('#trial-start')).to_be_disabled();results.append('switch discard rejection and old image remains unresolved')
  load(confirmed);assert_triangle();p.locator('#sample-text').click();expect(p.locator('#source-preview pre')).to_contain_text('水を冷やすと氷');assert p.locator('#source-preview svg').count()==0;load(confirmed);assert_triangle();results.append('old text and new image import select exact assets')
  for key,value in [('kind','text'),('sourceId','synthetic-image-source'),('locator','synthetic-source.svg'),('locator','https://invalid.example/synthetic.svg'),('locator','<svg onload="window.qaExecuted=1"></svg>')]:
   v=copy.deepcopy(confirmed);v['source'][key]=value;load(v);assert p.locator('#source-preview svg').count()==0;expect(p.locator('#source-preview')).to_contain_text('対応する同梱原本がありません');expect(p.locator('#confirm-0')).to_be_disabled();expect(p.locator('#trial-start')).to_be_disabled();assert p.evaluate('window.qaExecuted===undefined');results.append('unknown asset tuple refused '+key+' '+value)
  v=copy.deepcopy(confirmed);v['source']['label']='<img src="https://invalid.example/a" onerror="window.qaExecuted=1">';load(v);assert_triangle();assert p.locator('#source-meta img').count()==0;assert p.evaluate('window.qaExecuted===undefined');results.append('untrusted label renders text with known asset')
  assert p.evaluate('JSON.stringify(Object.entries(localStorage).sort())===qaInitial&&sessionStorage.length===0&&window.name===""');writes=p.evaluate('qaWrites');assert writes==[] and requests==[] and errors==[],(writes,requests,errors);ctx.close();browser.close()
 srv.shutdown()
result={'head':head,'cases':results,'case_count':len(results),'writes':writes,'nonallowed_browser_requests':requests,'page_errors':errors,'synthetic_child_history_unchanged':True,'viewport':[768,1024],'dialogs':dialogs,'synthetic_only':True};(O/'probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result),flush=True)
