"""Page width and subject boundaries, including mixed legacy synthetic histories."""
import json, os, re, subprocess, sys
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Quiet(PreviewHandler):
 def log_message(self,*args):pass
assets={}
for name in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
 url='https://unpkg.com/'+name;assets[url]=subprocess.check_output(['curl','-fsSL','--max-time','30',url])
subjects={'social':'社会','science':'理科','math':'算数','japanese':'国語'}
counts={'social':21,'science':14,'math':6,'japanese':5}
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'),ignore_default_args=['--hide-scrollbars'])
  for width,height in ((390,844),(768,1024),(1024,768),(1280,900)):
   for parent in (False,True):
    c=browser.new_context(viewport={'width':width,'height':height});c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
    def route(r):
     if r.request.url.startswith(base):r.continue_()
     elif r.request.url in assets:r.fulfill(body=assets[r.request.url],content_type='application/javascript')
     else:r.abort()
    c.route('**/*',route);p=c.new_page();p.on('dialog',lambda d:d.accept());errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    def visit(file):
     p.goto(base+file+('&' if '?' in file else '?')+('parent-check=1' if parent else ''))
    def fits(label):
     if parent:p.locator('#parent-check-banner details').evaluate('e=>e.open=true')
     # Reserve a classic scrollbar gutter as well as testing overlay scrollbars.
     # A 100vw bleed includes this gutter and must fail the same measurement.
     for gutter in ('auto','stable'):
      p.evaluate('(g)=>document.documentElement.style.scrollbarGutter=g',gutter)
      result=p.evaluate('''()=>({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,available:document.documentElement.getBoundingClientRect().width,bad:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>document.documentElement.clientWidth+1).slice(0,8).map(e=>e.outerHTML.slice(0,180))})''')
      assert result['scroll']<=result['client'] and result['scroll']<=round(result['available']),(label,width,parent,gutter,result)
     if parent:expect(p.locator('#parent-check-banner')).to_be_visible()
    visit('index.html');p.locator('.unit-card').first.wait_for();fits('home')
    all_names=p.locator('.unit-card .unit-name').all_text_contents();assert len(all_names)==17
    assert not any('社会・理科・算数・国語' in name for name in all_names)
    # Every embedded unit, its question and flash screen.
    for name in all_names:
     if name.startswith('模試の弱点対策') or any(word in name for word in ('応仁の乱','鎌倉幕府の成立','貴族の世の中')) or '溶解度' in name:continue
     p.get_by_role('button',name=name,exact=False).click();fits(name)
     p.get_by_role('button',name='復習クイズ',exact=False).click();fits(name+' quiz')
     p.get_by_role('button',name='← 戻る',exact=True).click()
     p.get_by_role('button',name='暗記カード',exact=False).click();fits(name+' flash select')
     p.get_by_role('button',name=re.compile(r'全\d+問チャレンジ')).click();fits(name+' flash question')
     p.get_by_role('button',name='← 戻る',exact=True).click()
     p.get_by_role('button',name='← 戻る',exact=True).click()
     p.locator('.unit-header button').first.click()
    # Filter membership and actual destination content must agree.
    for key,label in subjects.items():
     p.get_by_role('button',name=label,exact=True).click();fits(label+' home')
     assert set(p.locator('.unit-subject').all_text_contents())=={label}
     p.get_by_role('button',name='模試の弱点対策 '+label,exact=False).click()
     expect(p.locator('.unit-hero h1')).to_have_text('模試の弱点対策 '+label)
     assert p.evaluate('focusQuestions.length')==counts[key]
     assert p.evaluate('candidates("normal").every(q=>q.subject===focusLabel)')
     fits(label+' focus');p.locator('#start').click();fits(label+' question')
     assert p.evaluate('run.qs.every(q=>q.subject===focusLabel)')
     visit('index.html');p.locator('.unit-card').first.wait_for()
    for file in ('onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html'):
     visit(file);expect(p.locator('.unit-hero')).to_be_visible();fits(file)
     p.locator('#start').click();fits(file+' question')
     p.locator('.unit-footer a').click();fits(file+' parent notes')
     p.locator('[data-view=records]').click();fits(file+' records')
    assert not errors,errors
    print(f'width {width}, parent={parent}: all pages PASS',flush=True)
    c.close()
  # Migration is a read-only view of the old combined store, including revisionless
  # and review-v1 events. Saving/importing one subject must retain every other one.
  c=browser.new_context();c.route('**/*',route);p=c.new_page();p.goto(base+'mock-focus-review.html')
  fixture=p.evaluate('''()=>{
   const at=n=>new Date(Date.now()-n*86400000).toISOString();
   const mk=(q,n,correct,extra=false,versioned=true)=>{
    const actual=extra?EXTRA.get(q.id):q,stamp=at(n);
    return validateEvent({id:uuid(),sessionId:'synthetic-task16',questionId:actual.id,...(versioned?{questionVersion:1}:{}),unitId:UNIT_ID,version:VERSION,unit:q.unit,course:q.course,question:actual.prompt,response:correct?q.answer:q.options.find(o=>o!==q.answer),expected:q.answer,explanation:q.explanation,correct,variant:'normal',mode:extra?'adaptive':'normal',hint:false,at:stamp,offset:0,day:day(stamp,0)});
   };
   for(const label of ['社会','理科','算数','国語']){
    const qs=QUESTIONS.filter(q=>q.subject===label);
    data.events.push(mk(qs[0],10,false,false,false),mk(qs[0],9,false),mk(qs[0],8,true,true),mk(qs[1],4,false),mk(qs[1],3,false),mk(qs[2],10,false),mk(qs[2],9,false),mk(qs[2],8,true),mk(qs[2],7,true,true),mk(qs[2],5,true,true),mk(qs[2],1,true,true));
   }
   data.events=order(data.events);const raw=JSON.stringify(data);YuikaParent.storage.setItem(KEY,raw);
   return {raw,states:retention(),weak:practiceWeaknesses(),key:KEY};
  }''')
  original=json.loads(fixture['raw'])
  for key,label in subjects.items():
   p.goto(base+'mock-focus-review.html?subject='+key)
   assert p.evaluate('data.events.length')==44
   assert p.evaluate('YuikaParent.storage.getItem(KEY)')==fixture['raw']
   states=p.evaluate('retention()');assert len(states)==3
   assert {s['status'] for s in states}=={'weak','waiting','retained'}
   assert all(s in fixture['states'] for s in states)
   assert len(p.evaluate('practiceWeaknesses()'))==1
   assert p.evaluate('dueReviews().length')==1
   assert p.evaluate('focusEvents().length')==11
   assert p.evaluate('dailyQuestions().every(q=>q.subject===focusLabel)')
   assert p.evaluate('additional().every(r=>r.q.subject===focusLabel)')
   p.add_script_tag(url=base+'assets/progress.js')
   summary=p.evaluate('YuikaDesign.summary(location.pathname.split("/").pop()+location.search)')
   assert summary['total']==counts[key] and summary['due']==1 and summary['correct']==2,summary
   assert p.evaluate('save()')
   assert p.evaluate('data.events')==original['events']
   p.reload();assert p.evaluate('data.events')==original['events']
   p.locator('[data-view=records]').click()
   with p.expect_download() as item:p.locator('#export').click()
   packet=json.loads(Path(item.value.path()).read_text());assert packet['payload']['events']==original['events']
   p.locator('input[type=file]').set_input_files({'name':'synthetic-old-mixed.json','mimeType':'application/json','buffer':fixture['raw'].encode()})
   expect(p.locator('#notice')).to_contain_text('試作へ読み込みました。')
   assert p.evaluate('data.events')==original['events']
  # New subject answers merge into the same store and preserve old identities.
  p.goto(base+'mock-focus-review.html?subject=math');p.locator('#start').click()
  p.locator('[data-choice]').first.click();p.locator('#check').click()
  new=p.evaluate('data.events');assert len(new)==45
  assert all(e in new for e in original['events'])
  p.goto(base+'index.html');p.locator('.unit-card').first.wait_for()
  p.get_by_role('button',name='今日の5問をはじめる',exact=True).click()
  p.wait_for_url('**/mock-focus-review.html?subject=math&daily=1')
  assert p.evaluate('run.mode==="daily" && run.qs.every(q=>q.subject==="算数")')
  p.goto(base+'mock-focus-review.html');assert p.evaluate('QUESTIONS.length')==46
  assert len(p.evaluate('candidates("normal")'))==46
  assert p.evaluate('new Set(QUESTIONS.map(q=>q.subject)).size')==4
  c.close();browser.close()
print('responsive_subjects: all 17 units + questions/flash, 4 widths, parent banner, scrollbar gutters, subject boundaries and unchanged mixed histories PASS')
