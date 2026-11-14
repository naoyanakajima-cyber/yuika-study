"""Science actual daily count, unchanged selection, and top entry; synthetic only."""
import json
import os
import subprocess
import sys
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler,ROOT
BASE='55435567d44f05dc35f3ea6d73c4ba9cac2dc496'
old=subprocess.check_output(['git','show',f'{BASE}:scripts/practice/science.js'],cwd=ROOT,text=True)
old=old[old.index('function scienceDaily(){'):old.index('const scienceStart=start;')].replace('function scienceDaily(){','function oldScienceDaily(){')
new=(ROOT/'scripts/practice/science.js').read_text()
new=new[new.index('function scienceDailySources('):new.index('const SCIENCE_DAILY_EMPTY=')]
setup=r'''
const Q=new Map(Array.from({length:20},(_,i)=>['q'+i,{id:'q'+i}]));
const questions=[...Q.values()],data={events:[]};let count=5,scienceUnit='all',blocked=false,sets,seed=0,draws=0;
const practiceUnavailable=()=>blocked,scienceDue=()=>sets.due.map(q=>({originId:q.id})),scienceWeak=()=>sets.weak.map(q=>({originId:q.id})),candidates=()=>sets.normal;
Math.random=()=>{draws++;seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
const assert=(v,m)=>{if(!v)throw Error(m)};
'''
checks=r'''
let cases=0;
for(const n of [0,1,4,5,8,9,20])for(count of [5,10])for(blocked of [false,true]){
 sets={due:questions.slice(0,Math.min(2,n)),weak:questions.slice(0,Math.min(4,n)),normal:questions.slice(0,n)};
 seed=91;draws=0;const size=scienceDailyCount([],123);assert(draws===0,'count draws');
 const actual=scienceDaily([],123).map(q=>q.id),actualDraws=draws;
 seed=91;draws=0;const expected=oldScienceDaily().map(q=>q.id);
 assert(JSON.stringify(actual)===JSON.stringify(expected),'selection differs');assert(actualDraws===draws,'draw consumption differs');assert(size===actual.length,'count differs');cases++;
}
console.log('science selection oracle:',cases,'priority/order/draw/count cases PASS');
'''
subprocess.run(['node','-e',setup+old+new+checks],check=True)
class Quiet(PreviewHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  c=browser.new_context(viewport={'width':768,'height':1024});c.add_init_script(path=str(ROOT/'tests/seed_random.js'));c.route('https://**/*',lambda r:r.abort())
  p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
  for unit,upper,actual in [('all',5,5),('all',10,10),('実験器具',10,8),('水溶液と溶解',10,9)]:
   p.goto(base+'yuika-review-v2.html');p.locator('#unit').select_option(unit);p.locator(f'[data-count="{upper}"]').click()
   expect(p.locator('#daily-five')).to_have_text(f'今日の復習をはじめる（今回は{actual}問）')
   p.evaluate('''()=>{const random=Math.random;let draws=0;Math.random=()=>{draws++;return random()};const before=window.YuikaParent.storage.getItem(KEY);render();if(draws||window.YuikaParent.storage.getItem(KEY)!==before)throw Error('home side effects');Math.random=random;}''')
   p.locator('#daily-five').click();assert p.evaluate('session.questions.length')==actual
  p.goto(base+'yuika-review-v2.html');p.locator('#unit').select_option('all');p.locator('[data-count="5"]').click()
  p.evaluate('''()=>{const random=Math.random;let draws=0;Math.random=()=>{draws++;return random()};count=10;start('daily');if(draws||session!==null||view!=='home')throw Error('stale count started');Math.random=random;}''')
  expect(p.locator('#notice')).to_contain_text('問題数が変わりました');expect(p.locator('#daily-five')).to_contain_text('今回は10問')
  for field in ['dirty','blocked']:
   p.evaluate(f"{field}=true;start('daily')")
   expect(p.locator('#daily-five')).to_be_disabled();expect(p.locator('#daily-status')).to_contain_text('休止');expect(p.locator('#daily-status')).to_be_visible()
   assert p.evaluate("session===null&&view==='home'");p.evaluate(f'{field}=false;render()')
  # There is no normal zero-candidate science UI; this is a defensive synthetic boundary.
  p.evaluate("scienceUnit='synthetic-empty';render();start('daily')")
  expect(p.locator('#daily-five')).to_be_disabled();expect(p.locator('#daily-status')).to_contain_text('候補がありません');assert p.evaluate("session===null&&view==='home'")
  p.evaluate("scienceUnit='実験器具';count=10;rememberScience();render()")
  p.goto(base+'yuika-review-v2.html?daily=1');assert p.evaluate("session.mode==='daily'&&session.questions.length===8")
  # Read-only top label changes retain its actual saved science route.
  assets={}
  for path in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
   url='https://unpkg.com/'+path;assets[url]=subprocess.check_output(['curl','-fsSL','--max-time','30',url])
  p.route('https://unpkg.com/**',lambda r:r.fulfill(body=assets[r.request.url],content_type='application/javascript'))
  for suffix in ['', '?parent-check=1']:
   p.goto(base+'yuika-review-v2.html'+suffix);p.locator('#unit').select_option('実験器具');p.locator('[data-count="10"]').click()
   p.goto(base+'index.html'+suffix);expect(p.locator('.daily-panel h2')).to_have_text('今日の復習');p.get_by_role('button',name='今日の復習をはじめる',exact=True).click()
   p.wait_for_url('**/yuika-review-v2.html?*');assert p.evaluate("session.mode==='daily'&&session.questions.length===8")
   assert p.evaluate('window.YuikaParent.suppress()')==bool(suffix)
  assert not errors,errors
  c.close();browser.close()
 print('science_daily_count: four real UI counts, no extra draws, stale confirmation, blocked/dirty/zero boundaries, direct daily and normal/parent top route PASS')
finally:server.shutdown()
