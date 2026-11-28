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
   p.locator('#confirm-0').click();p.locator('#trial-start').click();p.locator('#trial-answer').fill('こおり');p.locator('#trial-grade').click()
   print(p.evaluate('({answer:trial.answer,field:document.getElementById("trial-answer").value,phase:trial.phase,result:trial.result})'))
 server.shutdown()
