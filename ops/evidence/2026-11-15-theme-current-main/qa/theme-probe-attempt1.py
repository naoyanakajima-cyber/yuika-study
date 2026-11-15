"""Independent bounded theme/main compatibility probe; synthetic data only."""
import os,json,sys,re,datetime
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-theme-current-main-20261115');OUT=Path('/tmp/yuika-cycle35-qa');sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
KEY='yuika-ui-theme-kamakura-v1';posts=[];external=[];errors=[];rows=[];contrasts=[]
class Quiet(PreviewHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{srv.server_port}/'
def contrast(a,b):
 def lum(c):
  v=[int(x)/255 for x in re.findall(r'\d+',c)[:3]];assert len(v)==3
  return sum((x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)*w for x,w in zip(v,[.2126,.7152,.0722]))
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
def snap(p):
 return p.evaluate("()=>({run:JSON.stringify(run),data:JSON.stringify(data),prefs:JSON.stringify(prefs),dom:main.innerHTML,values:[...main.querySelectorAll('input,select,textarea')].map(x=>[x.id,x.value]),notice:document.getElementById('notice').textContent,blocked,dirty})")
def storage(p):return p.evaluate('Object.fromEntries(Object.entries(localStorage))')
def toggle(p,value,parent=False):
 before=snap(p);disk=storage(p);p.evaluate('window.__themeRequests=[]');p.locator('#theme-'+value).click()
 assert p.locator('html').get_attribute('data-ui-theme')==value and p.locator('#theme-'+value).get_attribute('aria-pressed')=='true'
 assert p.evaluate('document.activeElement.id')=='theme-'+value
 assert snap(p)==before
 after=storage(p);assert after==disk if parent else {k:v for k,v in after.items() if k!=KEY}=={k:v for k,v in disk.items() if k!=KEY}
 assert p.evaluate('window.__themeRequests')==[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'])
  for mode in ['normal','parent','theme-write-fault','session-denied']:
   c=browser.new_context(viewport={'width':768,'height':1024});c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
   def route(r):
    if r.request.method=='POST':posts.append(r.request.url);r.abort()
    elif not r.request.url.startswith(BASE):external.append(r.request.url);r.abort()
    else:r.continue_()
   c.route('**/*',route)
   c.add_init_script("localStorage.setItem('synthetic-other-unit','preserve')")
   if mode=='theme-write-fault':c.add_init_script("(()=>{const set=Storage.prototype.setItem;window.failTheme=true;Storage.prototype.setItem=function(k,v){if(k==='yuika-ui-theme-kamakura-v1'&&failTheme)throw new DOMException('synthetic','QuotaExceededError');return set.call(this,k,v)}})()")
   if mode=='session-denied':c.add_init_script("(()=>{const get=Storage.prototype.getItem,set=Storage.prototype.setItem;Storage.prototype.getItem=function(k){if(this===sessionStorage)throw new DOMException('synthetic','SecurityError');return get.call(this,k)};Storage.prototype.setItem=function(k,v){if(this===sessionStorage)throw new DOMException('synthetic','SecurityError');return set.call(this,k,v)}})()")
   p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.clock.install(time=datetime.datetime(2026,11,15,11,tzinfo=datetime.timezone.utc));p.goto(BASE+'kamakura-review.html'+('?parent-check=1' if mode=='parent' else ''));p.wait_for_load_state('networkidle')
   p.evaluate('window.__themeRequests=[]');p.on('request',lambda req: p.evaluate('(url)=>window.__themeRequests.push(url)',req.url) if not p.is_closed() else None)
   isolated=mode in ['parent','session-denied'];child_before=storage(p);stage=[]
   if mode in ['normal','parent']:
    if isolated:expect(p.locator('#parent-check-banner')).to_be_visible()
    toggle(p,'kamakura',isolated);toggle(p,'standard',isolated)
    p.locator('[data-count="5"]').click();p.locator('#start').click();runid=p.evaluate('run.id');types=[]
    for i in range(5):
     q=p.evaluate('run.qs[run.index]');types.append(q['type'])
     if q['type']=='text':p.locator('#response').fill(q['answer'])
     else:p.locator('.option',has_text=q['answer']).first.click()
     toggle(p,'kamakura',isolated);toggle(p,'standard',isolated)
     if i==0:p.locator('#hint').click();toggle(p,'kamakura',isolated);toggle(p,'standard',isolated)
     p.locator('#check').click();toggle(p,'kamakura',isolated);toggle(p,'standard',isolated);p.locator('#next').click()
    assert p.evaluate('run.id')==runid and p.evaluate('data.events.length')==5
    p.evaluate('window.__enqueues=0;YuikaReports.enqueue=()=>{window.__enqueues++}')
    toggle(p,'kamakura',isolated);toggle(p,'standard',isolated);assert p.evaluate('__enqueues')==0
    if isolated:assert storage(p)==child_before
    p.locator('[data-view="home"]').click()
    if mode=='normal':
     for theme in ['standard','kamakura']:
      toggle(p,theme)
      p.screenshot(path=str(OUT/f'{theme}-home.png'))
      svg=p.locator('svg[role="img"][aria-label^="鎌倉幕府のしくみの模式図"]');assert svg.count()==1
      dom=svg.inner_html()
      for media in ['screen','print']:
       p.emulate_media(media=media)
       labels=svg.locator('text').evaluate_all("es=>es.filter(e=>['将軍','執権（北条氏）'].includes(e.textContent)).map(e=>({label:e.textContent,foreground:getComputedStyle(e).fill,background:getComputedStyle(e.previousElementSibling).fill,fontSize:getComputedStyle(e).fontSize}))")
       assert len(labels)==2
       for label in labels:label['contrast']=contrast(label['foreground'],label['background']);assert label['contrast']>=4.5
       assert svg.inner_html()==dom
       contrasts.append({'theme':theme,'media':media,'labels':labels})
       if media=='screen':svg.screenshot(path=str(OUT/f'{theme}-diagram-screen.png'))
       else:
        assert p.locator('.theme-panel').evaluate("e=>getComputedStyle(e).display")=='none'
        assert p.locator('body').evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(255, 255, 255)'
        svg.screenshot(path=str(OUT/f'{theme}-diagram-print.png'))
      p.emulate_media(media='screen');assert p.evaluate('YuikaParent.storage.getItem('+json.dumps(KEY)+')')==theme
     metrics=p.locator('.theme-choice').evaluate_all('es=>es.map(e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))');assert all(x['w']>=44 and x['h']>=44 for x in metrics)
     assert p.locator('.theme-options').evaluate('e=>parseFloat(getComputedStyle(e).gap)')>=8
     p.locator('#theme-kamakura').focus();focus=p.locator('#theme-kamakura').evaluate('e=>({color:getComputedStyle(e).outlineColor,bg:getComputedStyle(document.body).backgroundColor,offset:parseFloat(getComputedStyle(e).outlineOffset)})');focus['contrast']=contrast(focus['color'],focus['bg']);assert focus['contrast']>=3 and focus['offset']>=3
     assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');rows.append({'mode':mode,'run':runid,'events':5,'question_types':types,'same_run_stages':'input/selection,hint,graded,result','theme_notification_calls':0,'controls':metrics,'focus':focus})
    else:rows.append({'mode':mode,'run':runid,'events':5,'question_types':types,'same_run_stages':'input/selection,hint,graded,result','theme_notification_calls':0,'child_disk_unchanged':True})
   elif mode=='theme-write-fault':
    p.evaluate("document.getElementById('notice').textContent='合成の学習警告'");before=snap(p);p.locator('#theme-kamakura').click();assert snap(p)==before
    expect(p.locator('#theme-status')).to_contain_text('保存できませんでした');assert KEY not in storage(p)
    p.locator('#start').click();q=p.evaluate('run.qs[0]')
    if q['type']=='text':p.locator('#response').fill(q['answer'])
    else:p.locator('.option',has_text=q['answer']).first.click()
    p.locator('#check').click();assert p.evaluate('data.events.length')==1
    p.evaluate('window.failTheme=false');toggle(p,'standard');expect(p.locator('#theme-status')).to_be_empty();rows.append({'mode':mode,'warning_separate_from_learning':True,'one_answer_saved_during_fault':True,'recovery_saved_standard':True})
   else:
    expect(p.locator('#parent-check-banner')).to_be_visible();toggle(p,'kamakura',True);assert p.evaluate('YuikaParent.storage.getItem('+json.dumps(KEY)+')')=='kamakura';assert storage(p)==child_before
    p.reload();assert p.locator('html').get_attribute('data-ui-theme')=='standard' and storage(p)==child_before;rows.append({'mode':mode,'temporary_theme_in_memory':True,'child_disk_unchanged':True,'reload_resets_temporary_theme':True})
   c.close()
  assert not posts and not errors
  result={'head':'9fc4bbf3e6c72e09327b6610338f12937fc7aba5','completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':rows,'diagram_contrasts':contrasts,'posts':posts,'errors':errors,'external_gets_aborted':len(external),'limitations':['representative same-run sequence; not all possible histories','normal/parent five-question runs, existing theme suite covers15 and allT boundaries','Chromium tablet CSS viewport only; no real iPad/Safari','no live publication/actual user preference or learning effectiveness validation']};(OUT/'probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS four modes, same-run switches, faults, temporary storage, diagram screen/print contrast')
  browser.close()
finally:srv.shutdown();srv.server_close()
