"""Independent synthetic recall lifecycle/projection, fixed integration candidate."""
import os,json,sys,datetime
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/qa-rev-lever-checkout');OUT=Path('/workspace/qa-rev-lever-evidence');sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Quiet(PreviewHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{srv.server_port}/'
rows=[];posts=[];external=[];errors=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'])
  for file,qid in [('yuika-review-v2.html','medaka-07'),('edo-review.html','edo-01')]:
   for parent in [False,True]:
    c=browser.new_context(viewport={'width':768,'height':1024},has_touch=True);c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
    def route(r):
     if r.request.method=='POST':posts.append(r.request.url);r.abort()
     elif not r.request.url.startswith(BASE):external.append({'method':r.request.method,'url':r.request.url});r.abort()
     else:r.continue_()
    c.route('**/*',route);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.clock.install(time=datetime.datetime(2026,11,22,3,tzinfo=datetime.timezone.utc))
    p.goto(BASE+file);key=p.evaluate('KEY')
    # Seed a canonical synthetic old choice event only in science, through validator.
    old=p.evaluate('''()=>{const q=QUESTIONS.find(q=>q.type==='choice');if(!q)return null;const at='2026-11-20T03:00:00.000Z';const e=validateEvent({id:'synthetic-legacy-correct',sessionId:'synthetic-legacy',questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response:q.answer,inputRaw:q.answer,expected:q.answer,correct:true,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed:false,mode:'normal',explanation:q.explanation});state.events=[e];persist();return e;}''')
    if parent:
     p.evaluate("localStorage.setItem('synthetic-unrelated','preserve')")
     child_before=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))');p.goto(BASE+file+'?parent-check=1');expect(p.locator('#parent-check-banner')).to_be_visible()
    else:child_before=None
    n0=p.evaluate('state.events.length');raw_before=p.evaluate('YuikaParent.storage.getItem(KEY)')
    def prepare():
     p.evaluate("id=>{session={id:uid(),mode:'unit',questions:[byId.get(id)],index:0,results:[],hint:false,selected:null,answered:false,done:false};view='quiz';render();}",qid)
    def first_wrong():
     p.locator('#recall-text').fill('合成の誤答');p.locator('#check').tap();assert p.locator('[data-choice]').count()>0
    prepare();first_wrong();assert p.evaluate('state.events.length')==n0 and p.evaluate('YuikaParent.storage.getItem(KEY)')==raw_before
    p.reload();assert p.evaluate('state.events.length')==n0 and p.evaluate('YuikaParent.storage.getItem(KEY)')==raw_before
    prepare();first_wrong();q=p.evaluate('session.questions[0]');p.locator('[data-choice]').nth(q['options'].index(q['answer'])).tap();p.locator('#check').tap()
    assert p.evaluate('state.events.length')==n0+1
    e=p.evaluate('state.events.at(-1)');assert e['correct'] and e['recallOutcome']=='assisted' and e['firstResponse']=='合成の誤答' and e['response']==q['answer'] and e['hintUsed']
    assert p.locator('#check').is_disabled();p.evaluate('submit();submit()');assert p.evaluate('state.events.length')==n0+1
    p.screenshot(path=str(OUT/f'{qid}-parent{parent}-assisted.png'))
    p.reload();assert p.evaluate('state.events.length')==n0+1
    raw=p.evaluate('YuikaParent.storage.getItem(KEY)');events=p.evaluate('state.events')
    p.add_script_tag(url=BASE+'assets/progress.js')
    projected=p.evaluate('''()=>({events:data.events,weak:scienceWeak().map(r=>r.originId),daily:scienceDaily().map(q=>q.id),retention:retention(),summary:YuikaDesign.summary(location.pathname.split('/').pop())})''')
    assert qid in projected['weak'] and projected['daily'][0]==qid
    pe=next(x for x in projected['events'] if x['id']==e['id']);assert pe['correct'] is False
    assert p.evaluate('state.events')==events and p.evaluate('YuikaParent.storage.getItem(KEY)')==raw
    if old and not parent:
     old_now=next(x for x in events if x['id']==old['id']);old_projected=next(x for x in projected['events'] if x['id']==old['id']);assert old_now==old and old_projected['correct'] is True and 'recallOutcome' not in old_now and 'firstResponse' not in old_now
    if parent:assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==child_before
    # Missing firstResponse is an acceptance gap not directly asserted in dedicated suites.
    rejected=p.evaluate('''()=>{const raw=YuikaParent.storage.getItem(KEY),copy=JSON.parse(raw);delete copy.events.at(-1).firstResponse;let rejected=false;try{validateState(copy)}catch{rejected=true}return {rejected,unchanged:YuikaParent.storage.getItem(KEY)===raw};}''');assert rejected=={'rejected':True,'unchanged':True}
    upper=10 if file=='edo-review.html' and parent else 5
    p.locator(f'[data-count="{upper}"]').tap()
    label=p.locator('#daily-five').inner_text();display=int(p.locator('#daily-five').get_attribute('data-daily-count'));assert display==upper and '今日の復習' in label
    p.locator('#daily-five').tap();actual=p.evaluate('session.questions.map(q=>q.id)');assert len(actual)==display and actual[0]==qid
    assert p.evaluate('state.events')==events
    if parent:assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==child_before
    rows.append({'daily_display':display,'daily_actual_ids':actual,'daily_label':label,'file':file,'question':qid,'parent':parent,'starting_events':n0,'after_final_events':n0+1,'interrupted_event_not_saved':True,'reload_no_duplicate':True,'submit_guard_no_duplicate':True,'saved_event':e,'projection':projected,'raw_and_state_unchanged_by_projection':True,'legacy_event':old if not parent else None,'child_storage_unchanged':True if parent else None,'missing_firstResponse_rejected_without_write':rejected})
    c.close()
  entry_rows=[]
  import urllib.parse
  for name,query,selection,upper,total,expected in [('instruments','', '実験器具',10,112,8),('valid-medaka','?unit='+urllib.parse.quote('メダカの飼育・ひれ・成長'),None,5,17,5),('unknown','?unit=synthetic-unknown-unit',None,5,112,5)]:
   c=browser.new_context(viewport={'width':768,'height':1024},has_touch=True);c.add_init_script(path=str(ROOT/'tests/seed_random.js'));c.route('**/*',route);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.clock.install(time=datetime.datetime(2026,11,22,3,tzinfo=datetime.timezone.utc));p.goto(BASE+'yuika-review-v2.html'+query)
   if selection:p.locator('#unit').select_option(selection)
   p.locator(f'[data-count="{upper}"]').tap();p.add_script_tag(url=BASE+'assets/progress.js');summary=p.evaluate("f=>YuikaDesign.summary(f)",'yuika-review-v2.html'+query)
   label=p.locator('#daily-five').inner_text();display=int(p.locator('#daily-five').get_attribute('data-daily-count'));badge=p.locator('.unit-hero .tag').all_text_contents();unit=p.locator('#unit').input_value()
   assert display==expected and summary['total']==total and summary['normalCount']==expected
   assert '解説つき・理科全112問' in badge
   if name=='unknown':assert unit=='all'
   p.screenshot(path=str(OUT/f'{name}-home.png'));p.locator('#daily-five').tap();actual=p.evaluate('session.questions.map(q=>({id:q.id,unit:q.unit}))');assert len(actual)==display
   if name=='valid-medaka':assert all(x['id'].startswith('medaka-') for x in actual)
   if name=='instruments':assert all(x['unit']=='実験器具' for x in actual)
   entry_rows.append({'case':name,'unit':unit,'upper':upper,'summary':summary,'label':label,'display':display,'actual':actual,'badges':badge});c.close()
  assert not errors and not posts
  result={'head':__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':rows,'entry_cases':entry_rows,'posts':posts,'errors':errors,'external_aborted':external,'method':'7 fresh synthetic Chromium tablet contexts; controlled single-question session then actual input/tap controls; read-only projection and exact storage-byte checks','limitations':['single representative text recall per new unit; no second full question audit','old/new mixed events checked on science only; Edo has no old pre-recall question type','submit function guard called twice after disabled actual confirm button, not simultaneous multi-tab concurrency','no Safari/real-device or live deployed page test']};(OUT/'recall-probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS 4 recall and 3 entry cases: interrupted no event, final once, assisted weak, legacy preservation, parent byte isolation, missing firstResponse refusal')
  browser.close()
finally:srv.shutdown();srv.server_close()
