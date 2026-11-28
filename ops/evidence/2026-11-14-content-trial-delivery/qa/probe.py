import copy,json,os,runpy,subprocess
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-content-trial-delivery-20261114');OUT=Path('/tmp/yuika-content-trial-qa')
TEXT=json.loads((ROOT/'docs/product/fixtures/synthetic-content.json').read_text())
Handler=runpy.run_path(str(ROOT/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
 posts=0
 def log_message(self,*a):pass
 def do_POST(self):Quiet.posts+=1;self.send_error(405)
INIT='''(()=>{window.qaWrites=[];for(const k of ['setItem','removeItem','clear']){const old=Storage.prototype[k];Storage.prototype[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}const c=Object.getOwnPropertyDescriptor(Document.prototype,'cookie');if(c&&c.set)Object.defineProperty(Document.prototype,'cookie',{get:c.get,set(v){qaWrites.push('cookie');c.set.call(this,v);}});for(const k of ['pushState','replaceState']){const old=history[k];history[k]=function(...a){qaWrites.push('history.'+k);return old.apply(this,a);};}for(const [o,k] of [[indexedDB,'open'],[indexedDB,'deleteDatabase'],[caches,'open'],[caches,'delete'],[navigator.serviceWorker,'register']]){if(o&&o[k]){const old=o[k].bind(o);o[k]=function(...a){qaWrites.push(k);return old(...a);};}}})();'''
results=[];requests=[];errors=[];writes=[];console=[]
def fixture(answer='氷',aliases=None,readings=None,choice=False,count=1):
 p=copy.deepcopy(TEXT);q=p['questions'][0];q.update(answer=answer,aliases=aliases or [],readings=readings or [],prompt='合成問題の登録内容を答えてください',hint='合成ヒント',explanation='合成解説')
 if choice:q.update(type='choice',options=['東','西'],answer='東',aliases=[],readings=[])
 p['questions']=[dict(copy.deepcopy(q),id=f'draft-qa-trial-{i+1:03}') for i in range(count)]
 return p
def snap(p):return p.evaluate('({proposal:JSON.parse(JSON.stringify(proposal)),unsaved})')
def load(p,v,confirm=True):
 if p.evaluate('trial!==null'):p.locator('#trial-exit').click()
 p.locator('#import').set_input_files({'name':'synthetic-trial.json','mimeType':'application/json','buffer':json.dumps(v).encode()})
 expect(p.locator('#import')).to_have_value('')
 if confirm:
  for i in range(len(v['questions'])):p.locator(f'#confirm-{i}').click()
def start(p):p.locator('#trial-start').click();expect(p.locator('#trial-panel')).to_be_visible();assert p.evaluate('trial!==null');expect(p.locator('#trial-title')).to_be_focused()
def phase(p):return p.evaluate('trial&&trial.phase')
def grade(p,value,choice=False):
 if choice:
  if type(value)==int and value in [0,1]:p.locator(f'#trial-choice-{value}').check()
  else:p.evaluate('(v)=>trialInput(trialToken(),v)',value)
 elif isinstance(value,str):p.locator('#trial-answer').fill(value)
 else:p.evaluate('(v)=>trialInput(trialToken(),v)',value)
 p.locator('#trial-grade').click()
def judged(p,expected):
 if expected=='error':assert phase(p)=='A', (expected,phase(p));assert p.locator('#trial-solutions').count()==0 or not p.locator('#trial-solutions').is_visible()
 else:
  expect(p.locator('#trial-result')).to_be_focused();text=p.locator('#trial-result').inner_text();assert ('登録した答えに一致しました' in text) if expected=='match' else ('登録した答えとは一致しません' in text),text
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 with sync_playwright() as pw:
  with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
   ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True);ctx.add_init_script(INIT)
   def route(r):
    if r.request.url==base+'/content-review.html' and r.request.method=='GET':r.continue_()
    else:requests.append([r.request.method,r.request.url]);r.abort()
   ctx.route('**/*',route);p=ctx.new_page();p.set_default_timeout(5000)
   p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:console.append(m.text));accept={'value':True};dialogs=[]
   def dialog(d):dialogs.append(d.type);d.accept() if accept['value'] else d.dismiss()
   p.on('dialog',dialog);p.goto(base+'/content-review.html')
   # Explicit independent grading oracle, not copied from implementation.
   cases=[('G01','氷',['氷','こおり'],'match'),('G02','\u3000こおり\t',['氷','こおり'],'match'),('G03','コオリ',['氷','こおり'],'miss'),('G04','こ おり',['氷','こおり'],'miss'),('G05','氷。',['氷','こおり'],'miss'),('G06','ＡＢＣ',['ABC','A B'],'match'),('G07','abc',['ABC','A B'],'miss'),('G08a','A\u3000B',['ABC','A B'],'match'),('G08b','A  B',['ABC','A B'],'miss'),('G09','ｶﾞﾗｽ',['ガラス'],'match'),('G10a','',['氷'],'error'),('G10b',' \t\u3000',['氷'],'error'),('G11a','x'*200,['氷'],'miss'),('G11b','x'*201,['氷'],'error'),('G12','㍍'*51,['氷'],'error'),('B01','x'*200,['x'*200],'match'),('B02',' '+'x'*200,['x'*200],'error'),('B03','😀'*100,['😀'*100],'match'),('B04','😀'*101,['😀'*100],'error'),('B05','㍍'*50,['メートル'*50],'match'),('B06','カ\u3099ラス',['ガラス'],'match'),('B07','氷\u200b',['氷'],'miss'),('B08','A\tB',['A B'],'miss'),('B09','A\nB',['A B'],'miss'),('B10',None,['氷'],'error'),('B11',1,['氷'],'error')]
   for name,value,answers,expected in cases:
    load(p,fixture(answers[0],aliases=[] if answers[0]=='氷' else answers[1:],readings=answers[1:] if answers[0]=='氷' else []));start(p);prior=snap(p);grade(p,value);judged(p,expected);assert snap(p)==prior
    results.append(name);print('PASS',name,flush=True)
   for value,expected in [(0,'match'),(1,'miss'),(None,'error'),(2,'error'),('東','error'),(0.5,'error'),(-1,'error'),('0','error')]:
    load(p,fixture(choice=True));start(p);grade(p,value,True);judged(p,expected);results.append('G13 '+repr(value))
   # Start gates: draft, partial, stale confirmations, unresolved image, source mismatch, normalized answer/alias/reading length.
   for name,v,confirm,mut in [('draft',fixture(),False,None),('partial',fixture(count=2),False,None),('stale',fixture(),True,"proposal.questions[0].confirmedRevision=0"),('source',fixture(),True,"proposal.source.locator='invalid'"),('shape',fixture(),True,"proposal.extra='unknown'"),('choice-answer',fixture(choice=True),True,"proposal.questions[0].answer='北'"),('norm-answer',fixture('㍍'*51),True,None),('norm-alias',fixture(aliases=['㍍'*51]),True,None),('norm-reading',fixture(readings=['㍍'*51]),True,None)]:
    load(p,v,confirm)
    if name=='partial':p.locator('#confirm-0').click()
    if mut:p.evaluate(mut)
    p.evaluate('startTrial()');assert p.evaluate('trial===null'),name;results.append('S02 '+name)
   p.locator('#sample-image').click();p.evaluate('startTrial()');assert p.evaluate('trial===null');results.append('S02 unresolved image')
   # Confirmed imported JSON must lose confirmations.
   v=fixture();v['questions'][0].update(status='confirmed',confirmedRevision=v['revision']);load(p,v,False);p.evaluate('startTrial()');assert p.evaluate('trial===null');results.append('S02 imported confirmed')
   load(p,fixture());p.evaluate('window.originalFileText=File.prototype.text;File.prototype.text=function(){return new Promise(()=>{});};void 0');p.locator('#import').set_input_files({'name':'pending.json','mimeType':'application/json','buffer':b'{}'});expect(p.locator('#trial-start')).to_be_disabled();p.evaluate('startTrial()');assert p.evaluate('trial===null');p.locator('#cancel-import').click();p.evaluate('File.prototype.text=originalFileText;void 0');results.append('S02 pending import')
   # Whole session: DOM/AX hiding, hint, no skip, grading lock, old event/token isolation, next and final exit.
   v=fixture('qa-secret-answer',count=2);load(p,v);prior=snap(p);start(p)
   p.keyboard.press('Tab');expect(p.locator('#trial-answer')).to_be_focused();expect(p.locator('#editor')).to_be_hidden();assert p.locator('#editor').get_attribute('inert') is not None
   assert 'qa-secret-answer' not in p.locator('body').aria_snapshot();assert '合成解説' not in p.locator('body').aria_snapshot()
   p.evaluate('window.oldToken=trialToken();window.oldGrade=document.getElementById("trial-grade");nextTrial(oldToken)');assert p.evaluate('trial.index')==0
   p.locator('#trial-hint-button').click();expect(p.locator('#trial-hint')).to_contain_text('合成ヒント');assert '合成解説' not in p.locator('body').aria_snapshot()
   p.locator('#trial-answer').fill('qa-secret-answer');p.screenshot(path=str(OUT/'answering-768x1024.png'),full_page=True)
   p.locator('#trial-grade').click();judged(p,'match');expect(p.locator('#trial-answer')).to_have_value('qa-secret-answer');expect(p.locator('#trial-answer')).to_be_disabled();p.evaluate('oldGrade.click();trialInput(oldToken,"late");trialHint(oldToken)');assert snap(p)==prior
   p.locator('#trial-next').click();assert p.evaluate('trial.index')==1;expect(p.locator('#trial-answer')).to_have_value('');assert 'qa-secret-answer' not in p.locator('body').aria_snapshot()
   p.evaluate('oldGrade.click();gradeTrial(oldToken);nextTrial(oldToken);trialInput(oldToken,"old");trialHint(oldToken)');assert p.evaluate('trial.index')==1;expect(p.locator('#trial-answer')).to_have_value('')
   grade(p,'qa-secret-answer');p.evaluate('nextTrial(trialToken())');assert p.evaluate('trial.index')==1;expect(p.locator('#trial-answer')).to_have_value('qa-secret-answer')
   p.screenshot(path=str(OUT/'graded-768x1024.png'),full_page=True);p.locator('#trial-exit').click();assert p.evaluate('trial===null');assert snap(p)==prior;assert p.locator('#trial-panel').inner_text()==''
   with p.expect_download() as dl:p.locator('#export-confirmed').click()
   assert json.loads(Path(dl.value.path()).read_text())==prior['proposal']
   p.evaluate('oldGrade.click();gradeTrial(oldToken);nextTrial(oldToken)');assert p.evaluate('trial===null');start(p);expect(p.locator('#trial-answer')).to_have_value('');p.locator('#trial-exit').click()
   p.locator('#q-0-prompt').fill('合成問題の変更');assert p.evaluate('proposal.questions.every(q=>q.status==="draft"&&q.confirmedRevision===null)');p.evaluate('startTrial()');assert p.evaluate('trial===null')
   results.extend(['S01','S03','S05','S06','S07','S08','S09','S13 old tokens'])
   # Runtime mutation routes cannot act behind the hidden editor.
   load(p,fixture());start(p);prior=snap(p)
   p.evaluate('document.getElementById("sample-image").click();document.getElementById("cancel").click();document.getElementById("confirm-0").click();changed(()=>proposal.unit.title="bad");acceptProposal(SAMPLES[1]);exportProposal(false)')
   assert snap(p)==prior;assert p.evaluate('trial!==null');p.locator('#import').set_input_files({'name':'synthetic.json','mimeType':'application/json','buffer':json.dumps(fixture('new')).encode()});assert snap(p)==prior;assert p.evaluate('trial!==null');p.locator('#trial-exit').click();results.append('S10 runtime guards')
   # Revision/content corruption and explicit editor reconstruction invalidate session.
   for mutation in ['proposal.revision++','proposal.questions[0].prompt="synthetic changed"','proposal.questions[0].status="draft"','render()','drawTrial()',"document.getElementById('trial-answer').replaceWith(document.getElementById('trial-answer').cloneNode(true))"]:
    load(p,fixture());start(p);p.locator('#trial-answer').fill('synthetic ephemeral');p.evaluate(mutation);p.evaluate('gradeTrial(trialToken())');assert p.evaluate('trial===null'),mutation;assert 'synthetic ephemeral' not in p.locator('body').inner_text();results.append('S13 '+mutation)
   # Existing cancel confirmation and saved-state beforeunload + actual reload / synthetic BFCache restoration.
   load(p,fixture());prior=snap(p);accept['value']=False;p.locator('#cancel').click();assert snap(p)==prior;accept['value']=True;p.locator('#cancel').click();assert p.evaluate('proposal===null');results.append('S11 cancel')
   load(p,fixture());
   with p.expect_download() as dl:p.locator('#export-confirmed').click()
   exported=json.loads(Path(dl.value.path()).read_text());start(p);prior=snap(p);assert not prior['unsaved'];p.locator('#trial-answer').fill('synthetic ephemeral')
   prevented=p.evaluate('(()=>{const e=new Event("beforeunload",{cancelable:true});dispatchEvent(e);return e.defaultPrevented;})()');assert prevented;assert snap(p)==prior;assert p.evaluate('trial!==null')
   p.evaluate('dispatchEvent(new PageTransitionEvent("pageshow",{persisted:true}))');assert p.evaluate('trial===null');assert p.locator('#trial-panel').inner_text()=='';assert snap(p)==prior;results.append('S12 synthetic persisted')
   start(p);p.locator('#trial-answer').fill('synthetic ephemeral');accept['value']=False;p.evaluate('setTimeout(()=>location.reload(),0)');p.wait_for_timeout(200);assert p.evaluate('trial!==null');assert 'beforeunload' in dialogs
   writes.extend(p.evaluate('qaWrites'));accept['value']=True;p.reload();assert p.evaluate('trial===null&&proposal===null');results.append('S12 actual reload cancel then accept')
   # Script-like proposal values remain text and never request resources.
   v=fixture();v['questions'][0]['prompt']='<img src="https://invalid.example/test" onerror="window.qaXss=1">';load(p,v);start(p);expect(p.locator('#trial-prompt')).to_have_text(v['questions'][0]['prompt']);assert p.evaluate('window.qaXss===undefined');results.append('safe text rendering')
   writes.extend(p.evaluate('qaWrites'));assert writes==[] and requests==[] and errors==[] and Quiet.posts==0 and console==[],(writes,requests,errors,console)
   assert p.evaluate('window.name')=='';ctx.close()
 result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'cases':results,'case_count':len(results),'nonlocal_or_other_requests':requests,'writes':writes,'posts':Quiet.posts,'page_errors':errors,'console':console,'viewport':[768,1024],'synthetic_only':True,'bfcache':'synthetic persisted event; actual reload cancellation/acceptance separately exercised'}
 (OUT/'probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result),flush=True)
 server.shutdown()
