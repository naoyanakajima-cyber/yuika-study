import json,os,runpy,subprocess
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-content-trial-delivery-20261114');OUT=Path('/tmp/yuika-content-trial-qa');Handler=runpy.run_path(str(ROOT/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
 def log_message(self,*a):pass
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
   p=browser.new_page(viewport={'width':768,'height':1024});p.goto(f'http://127.0.0.1:{server.server_port}/content-review.html');p.locator('#sample-text').click()
   p.locator('#q-0-aliases').evaluate('(el)=>{el.closest("details").open=true;}');p.locator('#q-0-aliases').fill('㍍'*51);p.locator('#confirm-0').click()
   result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'trial_start_disabled':p.locator('#trial-start').is_disabled(),'trial_status':p.locator('#trial-start-status').inner_text(),'workflow_next':p.locator('#workflow-next').inner_text(),'next_step_label':p.locator('#next-step').inner_text()}
   p.locator('#next-step').click();result['next_step_focus']=p.evaluate('document.activeElement.id');p.screenshot(path=str(OUT/'normalized-candidate-guidance.png'),full_page=True)
   result['repair_actions']=p.locator('#trial-start-status button,#trial-start-status a').count()
   (OUT/'start-guidance-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
 server.shutdown()
