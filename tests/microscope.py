"""New unit data, tap grading, history and existing review integration."""
import json
import os
import re
import sys
import subprocess
from collections import Counter
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
from scripts.history.embed import questions
html=(ROOT/'yuika-review-v2.html').read_text()
all_qs=questions(html)
qs=[q for q in all_qs if q['id'].startswith('microscope-')]
assert len(qs)==20 and len({q['id'] for q in all_qs})==len(all_qs)
assert len({q['prompt'] for q in qs})==20
assert Counter(q['conceptId'] for q in qs)=={'microscope-focus':4,'microscope-motion':4,'microscope-lenses':2,'microscope-installation':1,'microscope-sequence':3,'microscope-low-power':2,'microscope-magnification':2,'microscope-field':2}
archive=json.loads((ROOT/'scripts/history/revisions.json').read_text())['yuika-review-v2.html']
for q in qs:
 assert q['unitId']=='rika-microscope' and q['unit']=='顕微鏡の使い方'
 assert q['subject']=='理科' and q['type']=='choice'
 assert len(set(q['options']))==len(q['options'])==3 and q['options'].count(q['answer'])==1
 assert all(q[k].strip() for k in ('conceptId','source','basis','explanation','hint','pitfall'))
 assert not re.search(r'@|受験番号|生年月日|住所|電話番号',json.dumps(q,ensure_ascii=False))
 assert archive[q['id']]==[dict(revision=1,kind='initial',reason='Task 17: initial original microscope questions',question=q)]
assert [q['answer'] for q in qs if q['conceptId']=='microscope-magnification']==['400倍','300倍']
server=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
assets={}
for path in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
 url='https://unpkg.com/'+path
 assets[url]=subprocess.check_output(['curl','-fsSL','--max-time','30',url])
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  context=browser.new_context(viewport={'width':768,'height':1024},has_touch=True)
  context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
  requests=[];errors=[]
  def route(r):
   if r.request.method=='POST':requests.append(r.request.url);r.abort()
   elif r.request.url in assets:r.fulfill(body=assets[r.request.url],content_type='application/javascript')
   elif not r.request.url.startswith(base):r.abort()
   else:r.continue_()
  context.route('**/*',route)
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.clock.install(time=datetime(2026,11,15,3,tzinfo=timezone.utc))
  page.goto(base+'index.html');page.locator('.unit-card').first.wait_for()
  summary=page.evaluate("YuikaDesign.summary('yuika-review-v2.html?unit=顕微鏡の使い方')")
  assert summary['total']==20 and summary['normalCount']==5
  page.get_by_role('button',name='顕微鏡の使い方',exact=False).tap()
  expect(page.locator('.unit-hero h1')).to_have_text('顕微鏡の使い方')
  assert page.locator('html').get_attribute('data-subject')=='science'
  assert page.locator('#unit').input_value()=='顕微鏡の使い方'
  assert page.evaluate('scienceDaily().length===5&&scienceDaily().every(q=>q.unitId==="rika-microscope")')
  # Tap through every correct and every incorrect choice, using real submission
  # and persistence. Synthetic isolated sessions avoid real notification APIs.
  for q in qs:
   for option in q['options']:
    page.evaluate('''id=>{const q=byId.get(id);session={id:uid(),mode:'unit',questions:[q],index:0,results:[],hint:false,selected:null,answered:false,done:false};view='quiz';render();}''',q['id'])
    button=page.locator('[data-choice]').nth(q['options'].index(option))
    assert button.bounding_box()['height']>=44
    button.tap();page.locator('#check').tap()
    assert page.evaluate('state.events.at(-1).correct')==(option==q['answer'])
    expect(page.locator('#feedback')).to_contain_text(q['explanation'])
    page.get_by_text('根拠・解説',exact=True).tap()
    expect(page.locator('#feedback')).to_contain_text(q['conceptId'])
    assert page.evaluate('state.events.at(-1).questionVersion')==1
  page.reload();assert page.evaluate('state.events.length')==60
  # Full-history integration: error on two days -> weak -> unaided correct ->
  # waiting -> due tomorrow -> first in daily practice, then persisted reload.
  page.evaluate('''()=>{
   // Reset only this fresh context's synthetic tap history, so disk merge
   // cannot mix it with the separate dated review fixture.
   YuikaParent.storage.removeItem(KEY);state=emptyState();
   const q=byId.get('microscope-04');
   const mk=(at,correct)=>{const r=correct?q.answer:q.options.find(x=>x!==q.answer);return validateEvent({questionVersion:1,id:uid(),sessionId:'synthetic-microscope-review',questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response:r,inputRaw:r,expected:q.answer,correct,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed:false,mode:'normal',explanation:q.explanation});};
   state.events=[mk('2026-11-12T03:00:00.000Z',false),mk('2026-11-13T03:00:00.000Z',false)];
   if(!scienceWeak().some(r=>r.originId===q.id))throw Error('New question not weak');
   state.events.push(mk('2026-11-14T03:00:00.000Z',true));persist();home();
   if(!scienceDue().some(r=>r.originId===q.id))throw Error('New question not due');
   if(scienceDaily()[0].id!==q.id)throw Error('Due question not first');
  }''')
  page.reload();assert page.evaluate("scienceDaily()[0].id==='microscope-04'")
  page.locator('#daily-five').tap();assert page.evaluate("session.questions[0].id==='microscope-04'")
  assert not requests and not errors,(requests,errors)
  context.close();browser.close()
finally:server.shutdown();server.server_close()
print('microscope: 20 originals, revision 1, concepts/basis, 60 tap choices, reload, weakness/recheck/daily PASS')
