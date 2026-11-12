import os,json,subprocess,sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1]).resolve()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/'
try:
 assets={}
 for path in ['react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js']:
  u='https://unpkg.com/'+path;assets[u]=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',u])
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium');ctx=browser.new_context();p=ctx.new_page();calls=[]
  def route(r):
   if r.request.url.startswith(base):r.continue_()
   elif r.request.url in assets:r.fulfill(body=assets[r.request.url],content_type='application/javascript')
   else:calls.append(r.request.url);r.abort()
  p.route('**/*',route);ctx.add_init_script("""window.__opened=[];window.open=(u)=>{window.__opened.push(u);return null;};sessionStorage.setItem('yuika-parent-check-v1:yuika_parent-email','synthetic@example.test');""")
  p.goto(base+'index.html?parent-check=1')
  p.get_by_role('button',name='環境問題・公害',exact=False).click(timeout=60000);p.get_by_role('button',name='復習クイズ',exact=False).click()
  for _ in range(10):
   p.get_by_role('button',name='わからない（正解を見る）',exact=False).click()
   p.get_by_role('button',name='次の問題へ',exact=False).or_(p.get_by_role('button',name='結果を見る',exact=False)).click()
  btn=p.get_by_role('button',name='結果を保護者に送る',exact=False);btn.click()
  out={'parent_mode':p.evaluate('YuikaParent.active'),'mailto_open_attempts':p.evaluate("window.__opened.filter(u=>u.startsWith('mailto:')).length"),'actual_open_or_send':False,'external_requests_blocked':len(calls)}
  print(json.dumps(out,ensure_ascii=False));Path('/tmp/yuika-pr24-qa/mailto-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');ctx.close();browser.close()
finally:srv.shutdown()
