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
 Thread(target=server.serve_forever,daemon=True).start();results=[]
 with sync_playwright() as pw:
  with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
   p=browser.new_page(viewport={'width':768,'height':1024});p.on('dialog',lambda d:d.accept());p.goto(f'http://127.0.0.1:{server.server_port}/content-review.html')
   for field in ['answer','aliases','readings']:
    p.locator('#sample-text').click();inp=p.locator('#q-0-'+field)
    if field!='answer':inp.evaluate('(el)=>{el.closest("details").open=true;}')
    inp.fill('㍍'*51);p.locator('#confirm-0').click()
    if field!='answer':inp.evaluate('(el)=>{el.closest("details").open=false;}')
    expect(p.locator('#trial-start')).to_be_disabled();expect(p.locator('#trial-repair')).to_be_visible()
    p.locator('#trial-repair').focus();p.keyboard.press('Enter');expect(inp).to_be_focused();expect(inp).to_be_visible()
    results.append({'field':field,'focus':p.evaluate('document.activeElement.id'),'status':p.locator('#trial-start-status').inner_text()})
   p.screenshot(path=str(OUT/'normalized-candidate-guidance.png'),full_page=True)
   p.locator('#sample-text').click();p.locator('#trial-repair').click();expect(p.locator('#confirm-0')).to_be_focused();p.locator('#confirm-0').click();expect(p.locator('#trial-repair')).to_be_hidden();p.locator('#trial-start').click();expect(p.locator('#editor')).to_be_hidden()
   result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'normalized_repair_paths':results,'unconfirmed_focus':'confirm-0','ready_repair_hidden':True,'trial_editor_hidden':True,'result':'passed'}
   (OUT/'start-guidance-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
 server.shutdown()
