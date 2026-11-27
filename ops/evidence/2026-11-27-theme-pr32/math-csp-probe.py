"""Independent math preview CSP check; fresh synthetic context, loopback only."""
import sys,os,json,datetime,subprocess
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(sys.argv[1]);OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Handler(PreviewHandler):
 posts=0
 def log_message(self,*args):pass
 def do_POST(self):type(self).posts+=1;self.send_response(204);self.end_headers()
with ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT))) as srv:
 Thread(target=srv.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'])
   context=browser.new_context(viewport={'width':768,'height':1024});context.route('https://**/*',lambda r:r.abort())
   page=context.new_page();response=page.goto(f'http://127.0.0.1:{srv.server_port}/math-passage-review.html')
   assert response.status==200 and "connect-src 'none'" in response.headers['content-security-policy']
   expect(page.locator('[data-stage]')).to_have_count(5)
   blocked=page.evaluate('''async()=>{window.violations=[];document.addEventListener('securitypolicyviolation',e=>violations.push(e.effectiveDirective));try{await fetch('/synthetic-notification-probe',{method:'POST',body:'synthetic'});return false;}catch{return true;}}''')
   assert blocked;page.wait_for_function("violations.includes('connect-src')");assert Handler.posts==0
   result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'status':200,'stage_controls':5,'csp':response.headers['content-security-policy'],'synthetic_fetch_rejected':blocked,'violation_directives':page.evaluate('violations'),'post_arrivals':Handler.posts,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
   (OUT/'math-csp-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS math preview CSP blocks synthetic same-origin POST; arrivals zero');browser.close()
 finally:srv.shutdown()
