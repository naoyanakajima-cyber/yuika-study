import json,os
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(os.environ.get('YUIKA_QA_ROOT','/workspace/yuika-pr26-review-20261112'))
OUT=Path('/tmp/yuika-pr26-qa')
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
results=[]
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as srv:
 Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for query in ['', '?subject=unknown','?subject=','?subject=social','?subject=constructor','?subject=toString','?subject=__proto__','?subject=math&subject=social']:
   c=browser.new_context(viewport={'width':768,'height':1024});c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort());p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto(base+'mock-focus-review.html'+query)
   result=p.evaluate('''()=>({label:String(focusLabel),questions:focusQuestions.length,candidates:candidates('normal').length,hero:document.querySelector('.hero h1')?.textContent||null,raw:JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))})''')
   p.add_script_tag(url=base+'assets/progress.js');result['summary']=p.evaluate('YuikaDesign.summary(location.pathname.split("/").pop()+location.search)');result.update(query=query,errors=errors);results.append(result);c.close()
  browser.close()
(OUT/'subject-url-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False,indent=2))
