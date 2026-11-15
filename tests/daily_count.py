"""Actual daily count UI and no-extra-draw selection regression; synthetic only."""
import json
import os
import subprocess
import sys
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT
BASE='132f9f59ebd23b6dab33e7d1e23bf4d077b8070d'
old=subprocess.check_output(['git','show',f'{BASE}:scripts/practice/adaptive.js'],cwd=ROOT,text=True)
old=old[old.index('function dailyQuestions('):old.index('function startDaily(')].replace('function dailyQuestions(', 'function oldDailyQuestions(')
source=(ROOT/'scripts/practice/adaptive.js').read_text()
new=source[source.index('function dailySources('):source.index('const DAILY_EMPTY=')]
setup=r'''
let blocked=false,draws=0,seed=1,sets;const data={events:[]},prefs={count:5};
const Q=Array.from({length:20},(_,i)=>({id:'q'+i})),EXTRA=new Map(Q.map(q=>[q.id,{id:q.id+'-review-v1',originId:q.id}]));
const practiceUnavailable=()=>blocked;
const dueReviews=()=>sets.due.map(q=>({originId:q.id}));
const additional=()=>sets.weak.map(q=>({q:EXTRA.get(q.id)}));
const candidates=()=>sets.normal;
function shuffle(xs){const a=[...xs];for(let i=a.length-1;i>0;i--){seed=(Math.imul(seed,1664525)+1013904223)>>>0;draws++;const j=Math.floor(seed/4294967296*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
const assert=(v,m)=>{if(!v)throw Error(m)};
'''
checks=r'''
let cases=0;
for(const n of [0,1,4,5,9,20])for(const count of [5,10,15])for(const unavailable of [false,true]){
 sets={due:Q.slice(0,Math.min(n,2)),weak:Q.slice(0,Math.min(n,4)),normal:Q.slice(0,n)};blocked=unavailable;
 const p={count};seed=42;draws=0;const before=dailyCount(p,123);assert(draws===0,'count consumed RNG');
 const actual=dailyQuestions(p,123).map(q=>q.id),actualDraws=draws;
 seed=42;draws=0;const expected=oldDailyQuestions(p).map(q=>q.id);
 assert(JSON.stringify(actual)===JSON.stringify(expected),'selection changed');assert(draws===actualDraws,'draw count changed');assert(before===actual.length,'count differs from start');cases++;
}
console.log('selection oracle:',cases,'cases, original priority/order/draw count preserved');
'''
subprocess.run(['node','-e',setup+old+new+checks],check=True)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=srv.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{srv.server_port}/'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for name in ('onin-review.html','kamakura-review.html','heian-review.html','mock-focus-review.html'):
   context=browser.new_context(viewport={'width':768,'height':1024})
   context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
   context.route('https://**/*',lambda route:route.abort())
   p=context.new_page();errors=[];p.on('pageerror',lambda err:errors.append(str(err)))
   p.goto(url+name)
   expect(p.locator('#daily-five')).to_have_text('今日の復習をはじめる（今回は5問）')
   # Rendering/counting consumes no random draws and writes no answer history.
   p.evaluate('''()=>{window.randomOriginal=Math.random;window.countDraws=0;Math.random=()=>{countDraws++;return randomOriginal()};window.rawBefore=window.YuikaParent.storage.getItem(KEY);render();if(countDraws!==0)throw Error('home draws');if(window.YuikaParent.storage.getItem(KEY)!==rawBefore)throw Error('home saved');Math.random=randomOriginal;}''')
   p.locator('#daily-five').click()
   assert p.evaluate("run.mode==='daily'&&run.qs.length===5")
   p.reload()
   # Same existing explicit daily route still starts once after rendering home.
   p.goto(url+name+'?daily=1')
   assert p.evaluate("screen==='quiz'&&run.qs.length===5")
   p.goto(url+name)
   # A changed display count must not consume random draws or create a session.
   p.evaluate('''()=>{const randomOriginal=Math.random;window.countDraws=0;Math.random=()=>{countDraws++;return randomOriginal()};prefs.count=10;startDaily();if(screen!=='home'||run!==null||countDraws!==0)throw Error('stale count started');Math.random=randomOriginal;}''')
   expect(p.locator('#daily-five')).to_have_text('今日の復習をはじめる（今回は10問）')
   expect(p.locator('#notice')).to_contain_text('問題数が変わりました')
   p.locator('#daily-five').click();assert p.evaluate('run.qs.length===10')
   p.goto(url+name)
   # A direct call still stops unavailable state without waiting for a repaint.
   p.evaluate('dirty=true;startDaily()')
   expect(p.locator('#daily-five')).to_be_disabled()
   expect(p.locator('#daily-status')).to_contain_text('休止')
   expect(p.locator('#daily-status')).to_be_visible()
   assert p.evaluate("screen==='home'&&run===null")
   p.evaluate('dirty=false;render()')
   assert p.evaluate("document.querySelector('#daily-five').nextElementSibling.id==='daily-status'")
   if name=='onin-review.html':
    p.locator('#unit').select_option('応仁の乱');p.locator('#variant').select_option('kanji');p.locator('[data-count="5"]').click()
    expect(p.locator('#daily-five')).to_have_text('今日の復習をはじめる（今回は4問）')
    p.locator('#daily-five').click();assert p.evaluate('run.qs.length===4')
    p.reload();p.locator('#variant').select_option('normal');p.locator('#unit').select_option('将軍');p.locator('#course').select_option('d2')
    expect(p.locator('#daily-five')).to_be_disabled();expect(p.locator('#daily-status')).to_be_visible();expect(p.locator('#daily-status')).to_contain_text('コース・分野・確認方法を見直してください')
    p.evaluate('startDaily()');assert p.evaluate("screen==='home'&&run===null")
   if name=='heian-review.html':
    p.locator('#course').select_option('pairs');p.locator('#unit').select_option('藤原氏と政治');p.locator('[data-count="10"]').click()
    expect(p.locator('#daily-five')).to_have_text('今日の復習をはじめる（今回は2問）')
    p.locator('#daily-five').click();assert p.evaluate('run.qs.length===2')
   assert not errors,errors
   context.close()
  browser.close()
 print('daily_count: 4 generated pages, C/D/E, guards, visible status, zero extra draws, changed-count confirmation and explicit daily route PASS')
finally:
 srv.shutdown()
