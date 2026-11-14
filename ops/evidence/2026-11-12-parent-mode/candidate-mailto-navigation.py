import os,json,subprocess,sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(sys.argv[1]).resolve()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/';results=[]
try:
 assets={}
 for path in ['react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js']:
  u='https://unpkg.com/'+path;assets[u]=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',u])
 html=(ROOT/'index.html').read_text().replace('// --- UTILS ---',"const fixtureUnit = UNITS.find(u=>u.id==='shakai-env');fixtureUnit.flashDecks=[{name:'合成確認',cards:[{q:'合成の国名',a:'中国'}]}];\n// --- UTILS ---")
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium')
  for parent in (True,False):
   for kind in ('quiz','flash'):
    ctx=browser.new_context();p=ctx.new_page();calls=[]
    def route(r):
     if r.request.url.startswith(base+'index.html'):r.fulfill(body=html,content_type='text/html')
     elif r.request.url.startswith(base):r.continue_()
     elif r.request.url in assets:r.fulfill(body=assets[r.request.url],content_type='application/javascript')
     else:calls.append(r.request.url);r.abort()
    p.route('**/*',route);ctx.add_init_script("""window.__opened=[];window.open=(u)=>{window.__opened.push(u);return null;};sessionStorage.setItem('yuika-parent-check-v1:yuika_parent-email','synthetic@example.test');localStorage.setItem('yuika_parent-email','synthetic@example.test');""")
    p.goto(base+'index.html'+('?parent-check=1' if parent else ''));p.get_by_role('button',name='環境問題・公害',exact=False).click(timeout=60000)
    if kind=='quiz':
     p.get_by_role('button',name='復習クイズ',exact=False).click()
     for _ in range(10):
      p.get_by_role('button',name='わからない（正解を見る）',exact=False).click()
      p.get_by_role('button',name='次の問題へ',exact=False).or_(p.get_by_role('button',name='結果を見る',exact=False)).click()
    else:
     p.get_by_role('button',name='暗記カード',exact=False).click();p.get_by_role('button',name='合成確認',exact=False).click();p.locator('input[placeholder="答えを入力…"]').fill('中国');p.get_by_role('button',name='答え合わせ',exact=True).click();p.get_by_role('button',name='結果を見る',exact=False).click()
    p.get_by_role('button',name='結果を保護者に送る',exact=False).click()
    count=p.evaluate("window.__opened.filter(u=>u.startsWith('mailto:')).length");assert count==(0 if parent else 1)
    out={'case':kind+('_parent' if parent else '_normal'),'mailto_spy_count':count,'actual_open_or_send':False,'result':'pass'};results.append(out);print(json.dumps(out),flush=True);ctx.close()
  for nav in ('anchor','button'):
   ctx=browser.new_context();p=ctx.new_page();p.route('**/*',route)
   ctx.add_init_script("""if(!localStorage.getItem('qa-once')){localStorage.setItem('qa-once','1');const original=Storage.prototype.setItem;Storage.prototype.setItem=function(...args){if(this===sessionStorage)throw new DOMException('synthetic first-load denial','SecurityError');return original.apply(this,args);};}localStorage.setItem('qa-child','synthetic-original');""")
   if nav=='anchor':
    p.goto(base+'mock-focus-review.html?parent-check=1');p.locator('#socialHome').click();p.wait_for_url('**/index.html*')
   else:
    p.goto(base+'index.html?parent-check=1');p.get_by_role('button',name='今日の5問をはじめる',exact=True).click(timeout=60000);p.wait_for_url('**/onin-review.html*')
   assert p.evaluate('YuikaParent.active&&YuikaParent.suppress()');p.evaluate("YuikaParent.storage.setItem('qa-child','synthetic-parent')");assert p.evaluate("localStorage.getItem('qa-child')")=='synthetic-original'
   out={'case':'temporary_navigation_'+nav,'result':'pass','parent_retained':True,'child_raw_preserved':True};results.append(out);print(json.dumps(out),flush=True);ctx.close()
  browser.close()
finally:srv.shutdown()
Path('/tmp/yuika-pr24-qa/candidate/mailto-navigation-result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
