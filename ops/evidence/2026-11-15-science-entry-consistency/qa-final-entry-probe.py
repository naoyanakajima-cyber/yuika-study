"""Read-only independent PR27 unit entry probe; fresh synthetic contexts."""
import os,json,subprocess,datetime,urllib.parse,importlib.util
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-pr27-fix-20261115');OUT=Path('/tmp/yuika-cycle30-qa');MAIN='86514eda054a5a2e09204df3a0668e40624c16de';HEAD='69f77d671b66484b501f7a0f5c292bfa96a22273'
spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/cloud/serve.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
posts=[];external=[];errors=[];rows=[]
class Handler(mod.PreviewHandler):
 def log_message(self,*a):pass
 def do_POST(self):posts.append(self.path);self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{srv.server_port}/'
mainfiles={f:subprocess.check_output(['git','show',MAIN+':'+f],cwd=ROOT) for f in ['yuika-review-v2.html','assets/design.js','assets/design.css','assets/progress.js']}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for revision in ['final']:
   for name,query in [('valid','?unit='+urllib.parse.quote('顕微鏡の使い方')),('missing',''),('empty','?unit='),('unknown','?unit=synthetic-unknown-unit')]:
    c=browser.new_context(viewport={'width':768,'height':1024});c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
    def route(r):
     if r.request.method=='POST':posts.append(r.request.url);r.abort();return
     if not r.request.url.startswith(BASE):external.append({'method':r.request.method,'url':r.request.url});r.abort();return
     f=urllib.parse.urlparse(r.request.url).path.lstrip('/')
     if revision=='main' and f in mainfiles:r.fulfill(body=mainfiles[f],content_type='text/html' if f.endswith('.html') else 'text/css' if f.endswith('.css') else 'application/javascript')
     else:r.continue_()
    c.route('**/*',route);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
    target='yuika-review-v2.html'+query;p.goto(BASE+target);expect(p.locator('#start')).to_be_visible()
    # Same generated summary asset used by the top home. Inject only into this fresh test page.
    p.add_script_tag(url=BASE+'assets/progress.js')
    summary=p.evaluate('(f)=>YuikaDesign.summary(f)',target)
    data=p.evaluate('''()=>({scienceUnit,requested:new URLSearchParams(location.search).get('unit'),unitSelect:document.getElementById('unit').value,allQuestionCount:QUESTIONS.length,candidateIDs:candidates('normal',scienceUnit).map(q=>q.id),candidateUnits:[...new Set(candidates('normal',scienceUnit).map(q=>q.unit))],badges:[...document.querySelectorAll('.unit-hero .tag')].map(x=>x.textContent),title:document.querySelector('.unit-hero h1').textContent,stats:[...document.querySelectorAll('.stats .stat')].map(x=>x.innerText),dailyLabel:document.getElementById('daily-five').textContent,normalLabel:document.getElementById('start').textContent,notice:document.getElementById('notice').textContent,events:state.events.length})''')
    p.screenshot(path=str(OUT/f'{revision}-{name}-home.png'))
    p.locator('#start').click();normal=p.evaluate('session.questions.map(q=>({id:q.id,unit:q.unit}))')
    p.reload();p.locator('#daily-five').click();daily=p.evaluate('session.questions.map(q=>({id:q.id,unit:q.unit}))')
    expected_total=20 if name=='valid' else 67
    assert summary['total']==expected_total and summary['normalCount']==5,(name,summary)
    assert len(data['candidateIDs'])==expected_total and data['scienceUnit']==('顕微鏡の使い方' if name=='valid' else 'all'),(name,data)
    assert '解説つき・理科全67問' in data['badges'],(name,data['badges'])
    assert any('0／67' in x for x in data['stats']),(name,data['stats'])
    assert len(normal)==len(daily)==5 and all(q['id'] in data['candidateIDs'] for q in normal+daily),(name,normal,daily)
    if name=='valid':assert all(q['unit']=='顕微鏡の使い方' for q in normal+daily)
    rows.append({'revision':revision,'case':name,'target':target,'summary':summary,'app':data,'normalQuestions':normal,'dailyQuestions':daily,'summary_actual_daily_count_equal':summary['normalCount']==len(daily)})
    c.close()
  assert not posts and not errors
  result={'head':HEAD,'main':MAIN,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':rows,'post_requests_blocked':posts,'page_errors':errors,'blocked_external':external,'method':'Generated top summary asset evaluated on target app in each fresh context; actual start and daily controls clicked, no answers or private data; main files served read-only from git objects','limitations':['empty synthetic histories only; persisted preferences not covered','no actual top React card click in this supplemental probe; mandatory microscope suite covers valid card entry','Chromium 768x1024, not real iPad/Safari']};(OUT/'final-entry-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
  for r in rows:print(r['revision'],r['case'],'summary',r['summary'],'unit',r['app']['scienceUnit'],'stats',r['app']['stats'],'daily',len(r['dailyQuestions']))
  browser.close()
finally:srv.shutdown();srv.server_close()
