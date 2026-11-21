import copy,json,os,runpy,subprocess
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-content-trial-20261114')
OUT=Path('/tmp/yuika-content-import-qa')
TEXT=json.loads((ROOT/'docs/product/fixtures/synthetic-content.json').read_text())
Handler=runpy.run_path(str(ROOT/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
    posts=0
    def log_message(self,*a):pass
    def do_POST(self):
        Quiet.posts+=1;self.send_error(405)
INIT='''(()=>{
window.qaReads={};window.qaWrites=[];
File.prototype.text=function(){const name=this.name;return new Promise((resolve,reject)=>{qaReads[name]={resolve,reject};});};
for(const k of ['setItem','removeItem','clear']){const old=Storage.prototype[k];Storage.prototype[k]=function(...a){qaWrites.push(k);return old.apply(this,a);};}
const cookie=Object.getOwnPropertyDescriptor(Document.prototype,'cookie');if(cookie&&cookie.set)Object.defineProperty(Document.prototype,'cookie',{get:cookie.get,set(v){qaWrites.push('cookie');cookie.set.call(this,v);}});
for(const k of ['pushState','replaceState']){const old=history[k];history[k]=function(...a){qaWrites.push('history.'+k);return old.apply(this,a);};}
for(const [object,k] of [[indexedDB,'open'],[indexedDB,'deleteDatabase'],[caches,'open'],[caches,'delete'],[navigator.serviceWorker,'register']]){if(object&&object[k]){const old=object[k].bind(object);object[k]=function(...a){qaWrites.push(k);return old(...a);};}}
})();'''
results=[]; requests=[]; errors=[]; writes=[]
def snap(p):return p.evaluate('({proposal:proposal?JSON.parse(JSON.stringify(proposal)):null,unsaved})')
def inputfile(p,name,value=None,raw=None):
    payload=raw if raw is not None else json.dumps(value or TEXT).encode()
    p.locator('#import').set_input_files({'name':name,'mimeType':'application/json','buffer':payload})
    if len(payload)<=200000:
        p.wait_for_function('(name)=>!!qaReads[name]',arg=name)
        assert p.evaluate('pendingImport')
        expect(p.locator('#cancel-import')).to_be_visible()
        expect(p.locator('#import-status')).to_contain_text('読み込み中')
def done(p,name,value=None,error=False,raw=None):
    p.evaluate('''async x=>{const q=qaReads[x.name];if(x.error)q.reject(Error('synthetic-read-error'));else q.resolve(x.raw);await new Promise(r=>setTimeout(r,0));}''',{'name':name,'raw':raw if raw is not None else json.dumps(value or TEXT),'error':error})
def fixture(label):
    q=copy.deepcopy(TEXT);q['packageId']='draft-'+label;q['unit']['title']='合成案 '+label;return q
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
    Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
    with sync_playwright() as pw:
        with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
            def scenario(name,fn,sample=True):
                ctx=browser.new_context(viewport={'width':768,'height':1024},accept_downloads=True)
                def guard(route):
                    r=route.request
                    if r.url==base+'/content-review.html' and r.method=='GET':route.continue_()
                    else:requests.append([name,r.method,r.url]);route.abort()
                ctx.route('**/*',guard);ctx.add_init_script(INIT)
                p=ctx.new_page();p.on('pageerror',lambda e:errors.append([name,str(e)]))
                dialog={'accept':True}
                p.on('dialog',lambda d:d.accept() if dialog['accept'] else d.dismiss())
                p.goto(base+'/content-review.html')
                if sample:p.locator('#sample-text').click()
                fn(p,dialog)
                assert p.evaluate('innerWidth')==768
                writes.extend([[name,x] for x in p.evaluate('qaWrites')])
                assert p.evaluate('window.name')==''
                results.append(name);ctx.close();print('PASS',name,flush=True)
            def stale_action(action):
                def f(p,d):
                    inputfile(p,'a.json');action(p);prior=snap(p);done(p,'a.json',fixture('old-result'));assert snap(p)==prior
                    expect(p.locator('#import')).to_have_value('')
                    assert '変わ' in p.locator('#notice').inner_text() or '変更' in p.locator('#notice').inner_text()
                return f
            scenario('editing preserves revision/confirm/unsaved',stale_action(lambda p:p.locator('#q-0-prompt').fill('合成の編集中の問い')))
            scenario('confirmation preserved',stale_action(lambda p:p.locator('#confirm-0').click()))
            def export(p):
                prior=snap(p)
                with p.expect_download() as dl:p.locator('#export-draft').click()
                data=json.loads(Path(dl.value.path()).read_text());assert set(data)==set(TEXT)
                assert all(q['status']=='draft' and q['confirmedRevision'] is None for q in data['questions'])
                assert data['revision']==prior['proposal']['revision'];assert not snap(p)['unsaved']
            scenario('export preserves saved state/schema',stale_action(export))
            scenario('sample replacement preserved',stale_action(lambda p:p.locator('#sample-image').click()))
            scenario('proposal cancellation preserved',stale_action(lambda p:p.locator('#cancel').click()))
            def overlap(old_error=False,reverse=False):
                def f(p,d):
                    inputfile(p,'a.json');inputfile(p,'b.json');before=snap(p);message=p.locator('#notice').inner_text();fileval=p.locator('#import').input_value()
                    if reverse:
                        done(p,'b.json',fixture('latest'));adopted=snap(p);notice=p.locator('#notice').inner_text();done(p,'a.json',fixture('old-result'),error=old_error);assert snap(p)==adopted;assert p.locator('#notice').inner_text()==notice
                    else:
                        done(p,'a.json',fixture('old-result'),error=old_error);assert snap(p)==before;assert p.locator('#notice').inner_text()==message;assert p.locator('#import').input_value()==fileval;assert p.evaluate('pendingImport');expect(p.locator('#cancel-import')).to_be_visible()
                        done(p,'b.json',fixture('latest'));assert snap(p)['proposal']['packageId']=='draft-latest'
                    expect(p.locator('#import')).to_have_value('');assert not p.evaluate('pendingImport')
                return f
            scenario('A resolves while B pending',overlap())
            scenario('old error cannot replace B notice/input',overlap(True))
            scenario('B then A reverse completion',overlap(reverse=True))
            scenario('B then stale A error',overlap(True,True))
            def bad_latest(kind):
                def f(p,d):
                    before=snap(p);inputfile(p,'a.json')
                    if kind=='oversize':inputfile(p,'b.json',raw=b' '*200001)
                    else:
                        inputfile(p,'b.json');done(p,'b.json',error=kind=='error',raw='{}' if kind=='shape' else '{' if kind=='json' else None)
                    msg=p.locator('#notice').inner_text();assert snap(p)==before
                    done(p,'a.json',fixture('old-result'));assert snap(p)==before;assert p.locator('#notice').inner_text()==msg
                return f
            for kind in ['error','shape','json','oversize']:scenario('latest '+kind+' never revives A',bad_latest(kind))
            def refuse(p,d):
                before=snap(p);d['accept']=False;inputfile(p,'a.json');done(p,'a.json',fixture('declined'));assert snap(p)==before;expect(p.locator('#import')).to_have_value('')
            scenario('discard refusal preserves all proposal state',refuse)
            def empty(p,d):
                before=snap(p);inputfile(p,'a.json');p.locator('#import').set_input_files([]);done(p,'a.json',fixture('old-result'));assert snap(p)==before
            scenario('empty file selection invalidates pending A',empty)
            def normal(p,d):
                q=fixture('normal');q['questions'][0]['status']='confirmed';q['questions'][0]['confirmedRevision']=q['revision']
                for _ in range(2):
                    inputfile(p,'same.json',q);done(p,'same.json',q);assert snap(p)['proposal']['packageId']=='draft-normal';assert all(x['status']=='draft' and x['confirmedRevision'] is None for x in snap(p)['proposal']['questions']);expect(p.locator('#import')).to_have_value('')
                assert p.evaluate('document.activeElement.id')=='workflow-title'
                p.screenshot(path=str(OUT/'normal-import-768x1024.png'),full_page=True)
            scenario('empty start normal import and same filename repeat',normal,False)
            def explicit(p,d):
                before=snap(p);inputfile(p,'a.json');p.get_by_role('button',name='読み込みを取り消す',exact=True).click();done(p,'a.json',fixture('old-result'));assert snap(p)==before;expect(p.locator('#import')).to_have_value('')
                p.screenshot(path=str(OUT/'cancel-import-768x1024.png'),full_page=True)
            scenario('explicit read cancellation preserves current proposal',explicit)
    server.shutdown()
assert not requests,requests
assert not errors,errors
assert not writes,writes
assert Quiet.posts==0
report={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'scenarios':results,'nonlocal_or_other_requests':requests,'page_errors':errors,'storage_or_history_writes':writes,'posts':Quiet.posts,'viewport':[768,1024],'synthetic_only':True,'file_text':'controlled deferred promises via actual file input; not OS timing'}
(OUT/'probe-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False),flush=True)
