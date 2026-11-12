import json,sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright,expect
root=Path(sys.argv[1]);
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root))) as server:
 Thread(target=server.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium');ctx=browser.new_context(viewport={'width':768,'height':1024});p=ctx.new_page();base=f'http://127.0.0.1:{server.server_port}/';p.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort())
  p.goto(base+'mock-focus-review.html?parent-check=1');expect(p.locator('#parent-exit')).to_be_visible();p.locator('#parent-check-banner summary').click()
  boxes={}
  for selector in ['#parent-check-banner','#parent-exit','#parent-since','#parent-count','#parent-delete']:
   el=p.locator(selector);expect(el).to_be_visible();b=el.bounding_box();assert b['x']>=0 and b['x']+b['width']<=768 and b['y']>=0 and b['y']+b['height']<=1024,(selector,b);boxes[selector]=b
  assert p.evaluate('document.documentElement.scrollWidth<=768')
  p.locator('#parent-since').fill('2026-11-11T00:00');p.locator('#parent-count').click();expect(p.locator('#parent-delete-status')).to_have_text('削除対象：0件');assert p.locator('#parent-delete').is_disabled()
  p.locator('#parent-exit').focus();p.keyboard.press('Enter');p.wait_for_function('()=>!YuikaParent.active');assert p.locator('#parent-check-banner').count()==0
  result={'case':'768x1024_parent_controls','result':'pass','boxes':boxes,'horizontal_overflow':False,'keyboard_exit':True};print(json.dumps(result));Path('/tmp/yuika-pr24-qa/candidate/viewport-result.json').write_text(json.dumps(result,indent=2)+'\n');ctx.close();browser.close()
 server.shutdown()
