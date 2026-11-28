"""Synthetic theme regression checks; run with python tests/theme_review.py."""
import importlib.util
import json
import os
import re
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect

ROOT = Path('/workspace/yuika-theme-compatibility-20261115')
KEY = 'yuika-ui-theme-kamakura-v1'
LEARNING = 'yuika-prototype-v1:yuika-social-540-25-v1'
OTHER = {
    'yuika-social-540-27-v1': '{"schemaVersion":1,"datasetVersion":"onin-540-27-v1","events":[]}',
    'yuika-social-540-24-v1': '{"schemaVersion":1,"datasetVersion":"heian-540-24-v1","events":[]}',
    'yuika-science-v2': '{"synthetic":"preserve"}',
    'yuika_sessions': '[{"unit":"synthetic"}]',
}
spec = importlib.util.spec_from_file_location('preview', ROOT / 'scripts/cloud/serve.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
posts = []
class Handler(preview.PreviewHandler):
    def log_message(self, *_):
        pass
    def do_POST(self):
        posts.append(self.path)
        self.send_error(405)

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}/'
external = []
blocked_fonts = []
errors = []

def fresh(browser, initial=None, fault=None, parent=False, session_fault=False):
    context = browser.new_context(viewport={'width': 768, 'height': 1024})
    def route_request(route):
        if route.request.url.startswith(BASE): route.continue_()
        elif route.request.url.startswith(('https://fonts.googleapis.com/', 'https://fonts.gstatic.com/')) and route.request.method == 'GET':
            blocked_fonts.append(route.request.url);route.abort()
        else: external.append(route.request.url);route.abort()
    context.route('**/*', route_request)
    context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
    if initial is not None or fault:
        context.add_init_script(f"""(()=>{{
          const key={json.dumps(KEY)}, seed={json.dumps(initial or {})};
          if(!sessionStorage.getItem('theme-test-seeded')){{for(const[k,v]of Object.entries(seed))localStorage.setItem(k,v);sessionStorage.setItem('theme-test-seeded','yes');}}
          const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
          window.themeFault={json.dumps(fault)};window.themeWrites=0;
          Storage.prototype.getItem=function(k){{if(k===key&&window.themeFault==='get')throw new DOMException('synthetic','SecurityError');return get.call(this,k);}};
          Storage.prototype.setItem=function(k,v){{if(k===key){{window.themeWrites++;if(window.themeFault==='set')throw new DOMException('synthetic','QuotaExceededError');}}return set.call(this,k,v);}};
        }})();""")
    if session_fault:
        context.add_init_script("""(()=>{const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
          Storage.prototype.getItem=function(k){if(this===sessionStorage)throw new DOMException('synthetic','SecurityError');return get.call(this,k);};
          Storage.prototype.setItem=function(k,v){if(this===sessionStorage)throw new DOMException('synthetic','SecurityError');return set.call(this,k,v);};})();""")
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE + 'kamakura-review.html' + ('?parent-check=1' if parent else ''))
    return context, page

def storage(page):
    return page.evaluate('Object.fromEntries(Object.entries(localStorage))')

def state(page):
    return page.evaluate("""()=>({run:JSON.stringify(run),data:JSON.stringify(data),prefs:JSON.stringify(prefs),
      html:document.getElementById('main').innerHTML,values:[...document.querySelectorAll('#main input,#main select,#main textarea')].map(e=>[e.id,e.value]),
      notice:document.getElementById('notice').textContent,blocked,dirty})""")

def theme(page, value):
    before = state(page)
    records = storage(page)
    page.locator('#theme-' + value).click()
    expect(page.locator('html')).to_have_attribute('data-ui-theme', value)
    expect(page.locator('#theme-' + value)).to_have_attribute('aria-pressed', 'true')
    assert state(page) == before, 'theme changed learning state/DOM'
    after = storage(page)
    assert {k:v for k,v in after.items() if k != KEY} == {k:v for k,v in records.items() if k != KEY}
    assert after[KEY] == value


def contrast(a, b):
    def luminance(color):
        rgb = [int(x) / 255 for x in re.findall(r'\d+', color)[:3]]
        assert len(rgb) == 3, color
        channels = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in rgb]
        return sum(x*w for x,w in zip(channels, [.2126,.7152,.0722]))
    x,y=sorted([luminance(a),luminance(b)])
    return (y+.05)/(x+.05)

try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  normal={**OTHER,KEY:'kamakura','yuika-social-540-25-v1':'synthetic-child-record'}
  for failed in (False,True):
   context,page=fresh(browser,normal,parent=not failed,session_fault=failed)
   expect(page.locator('#parent-check-banner')).to_be_visible()
   expect(page.locator('html')).to_have_attribute('data-ui-theme','standard')
   before=storage(page);original=state(page)
   page.locator('#theme-kamakura').click()
   assert state(page)==original and storage(page)==before
   assert page.evaluate('YuikaParent.storage.getItem('+json.dumps(KEY)+')')=='kamakura'
   page.reload()
   expect(page.locator('html')).to_have_attribute('data-ui-theme','standard' if failed else 'kamakura')
   assert storage(page)==before
   if not failed:
    page.locator('#theme-standard').click();page.locator('#parent-exit').click()
    expect(page.locator('#parent-check-banner')).to_have_count(0)
    expect(page.locator('html')).to_have_attribute('data-ui-theme','kamakura')
    assert storage(page)==before
    assert page.evaluate("Object.keys(sessionStorage).filter(k=>k.startsWith('yuika-parent-check-v1')).length")==0
   context.close()
  context,page=fresh(browser,{KEY:'kamakura'})
  page.emulate_media(media='print')
  expect(page.locator('.theme-panel')).to_be_hidden()
  assert page.locator('body').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(255, 255, 255)'
  assert page.locator('body').evaluate('e=>getComputedStyle(e).color')=='rgb(41, 62, 59)'
  assert storage(page)[KEY]=='kamakura'
  context.close();assert not errors,errors;assert not external,external;assert not posts,posts
  browser.close()
finally:server.shutdown();server.server_close()
print('parent and print first-run probe PASS')
