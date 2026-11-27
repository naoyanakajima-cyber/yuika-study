"""Independent bounded integration probe; synthetic fresh contexts only."""
import os,json,sys,re,datetime,subprocess
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright,expect
ROOT=Path(sys.argv[1]).resolve();OUT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
KEY='yuika-ui-theme-kamakura-v1';posts=[];external=[];errors=[];rows=[];ratios=[]
class Quiet(PreviewHandler):
 def log_message(self,*a):pass
 def do_POST(self):posts.append(self.path);self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{srv.server_port}/'
def disk(p):return p.evaluate('Object.fromEntries(Object.entries(localStorage))')
def snap(p):return p.evaluate("()=>({run:JSON.stringify(run),data:JSON.stringify(data),prefs:JSON.stringify(prefs),dom:main.innerHTML,values:[...main.querySelectorAll('input,select,textarea')].map(e=>[e.id,e.value]),notice:document.getElementById('notice').textContent,blocked,dirty})")
def toggle(p,value,parent):
 before=snap(p);d=disk(p);count=len(p.requests);p.locator('#theme-'+value).click()
 expect(p.locator('html')).to_have_attribute('data-ui-theme',value)
 expect(p.locator('#theme-'+value)).to_have_attribute('aria-pressed','true')
 assert snap(p)==before,'learning changed on theme switch'
 after=disk(p)
 assert after==d if parent else {k:v for k,v in after.items() if k!=KEY}=={k:v for k,v in d.items() if k!=KEY}
 assert len(p.requests)==count,'theme request'
 assert p.evaluate('window.__themeEnqueues')==0
def spy(p):p.evaluate('() => {window.__themeEnqueues=0;YuikaReports.enqueue=()=>{window.__themeEnqueues++;};}')
def contrast(a,b):
 def lum(c):
  v=[int(x)/255 for x in re.findall(r'\d+',c)[:3]];assert len(v)==3
  return sum((x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)*w for x,w in zip(v,[.2126,.7152,.0722]))
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
def kamakura(p,parent):
 p.goto(BASE+'kamakura-review.html'+('?parent-check=1' if parent else ''));p.wait_for_load_state('networkidle');spy(p)
 if parent:expect(p.locator('#parent-check-banner')).to_be_visible()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'])
  for parent in [False,True]:
   mode='parent' if parent else 'normal';c=browser.new_context(viewport={'width':768,'height':1024})
   c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
   c.add_init_script('''(()=>{window.__themeStorageWrites=[];for(const method of ['setItem','removeItem','clear']){const original=Storage.prototype[method];Storage.prototype[method]=function(...args){if(method==='clear'||String(args[0]).includes('yuika-ui-theme-kamakura-v1'))window.__themeStorageWrites.push({method,key:args[0]||null});return original.apply(this,args);};}})();''')
   def route(r):
    if r.request.method=='POST':posts.append(r.request.url);r.abort()
    elif not r.request.url.startswith(BASE):external.append(r.request.url);r.abort()
    else:r.continue_()
   c.route('**/*',route);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
   p.requests=[];p.on('request',lambda req,b=p.requests:b.append(req.url))
   p.clock.install(time=datetime.datetime(2026,11,27,17,tzinfo=datetime.timezone.utc));kamakura(p,parent)
   p.evaluate("localStorage.setItem('synthetic-other-unit','preserve');if(YuikaParent.active)localStorage.setItem('yuika-ui-theme-kamakura-v1','standard')");original=disk(p)
   for theme in ['kamakura','standard']:
    toggle(p,theme,parent)
   p.locator('[data-count="5"]').click();p.locator('#start').click();rid=p.evaluate('run.id');types=[]
   for i in range(5):
    q=p.evaluate('run.qs[run.index]');types.append(q['type'])
    if q['type']=='text':p.locator('#response').fill(q['answer'])
    else:p.locator('.option',has_text=q['answer']).first.click()
    toggle(p,'kamakura',parent);toggle(p,'standard',parent)
    if i==0:
     p.locator('#hint').click();toggle(p,'kamakura',parent);p.screenshot(path=str(OUT/f'{mode}-kamakura-hint.png'));toggle(p,'standard',parent)
    p.locator('#check').click();toggle(p,'kamakura',parent);toggle(p,'standard',parent);p.locator('#next').click()
   assert p.evaluate('run.id')==rid and p.evaluate('data.events.length')==5
   spy(p);toggle(p,'kamakura',parent);toggle(p,'standard',parent)
   if parent:assert disk(p)==original
   toggle(p,'kamakura',parent);p.reload();p.wait_for_load_state('networkidle');assert p.evaluate('data.events.length')==5;expect(p.locator('html')).to_have_attribute('data-ui-theme','kamakura');spy(p)
   if parent:assert disk(p)==original
   if not parent:
    for theme in ['standard','kamakura']:
     toggle(p,theme,parent);svg=p.locator('svg[aria-label^="鎌倉幕府のしくみの模式図"]');dom=svg.inner_html()
     for media in ['screen','print']:
      before_print=disk(p);p.emulate_media(media=media)
      if media=='print':assert p.locator('.theme-panel').evaluate('e=>getComputedStyle(e).display')=='none'
      assert disk(p)==before_print
      labels=svg.locator('text').evaluate_all("es=>es.filter(e=>['将軍','執権（北条氏）'].includes(e.textContent)).map(e=>({text:e.textContent,fill:getComputedStyle(e).fill,bg:getComputedStyle(e.previousElementSibling).fill,size:getComputedStyle(e).fontSize}))")
      assert len(labels)==2
      for label in labels:label['ratio']=contrast(label['fill'],label['bg']);assert label['ratio']>=4.5
      assert svg.inner_html()==dom;ratios.append({'theme':theme,'media':media,'labels':labels})
      if theme=='kamakura':svg.screenshot(path=str(OUT/f'kamakura-diagram-{media}.png'))
     p.emulate_media(media='screen')
   # Same-origin new math must neither consume nor write theme preferences.
   baseline=None;math_sets=[]
   for theme in ['standard','kamakura','standard']:
    kamakura(p,parent);toggle(p,theme,parent)
    before_math=disk(p);stored=p.evaluate("YuikaParent.storage.getItem('yuika-ui-theme-kamakura-v1')")
    response=p.goto(BASE+'math-passage-review.html');p.wait_for_load_state('networkidle')
    assert "connect-src 'none'" in response.headers['content-security-policy']
    assert "form-action 'none'" in response.headers['content-security-policy']
    assert p.locator('[data-ui-theme]').count()==0 and p.locator('.theme-panel').count()==0
    assert p.evaluate('window.__themeStorageWrites')==[]
    assert disk(p)==before_math
    if parent:expect(p.locator('#parent-check-banner')).to_be_visible();assert disk(p)==original
    current=p.locator('body').evaluate("e=>{const s=getComputedStyle(e);return {color:s.color,background:s.backgroundColor,font:s.fontFamily,width:e.getBoundingClientRect().width}}")
    if baseline is None:baseline=current
    else:assert current==baseline,'non-target math appearance changed with theme'
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
    if theme=='kamakura':
     p.locator('[data-stage="1"]').click()
     questions=p.locator('#questions').text_content();qs=json.loads(questions)
     for q in [q for q in qs if q['step']==1]:
      p.get_by_role('button',name=q['answer'],exact=True).click();p.locator('#check').click();p.locator('#next').click()
     expect(p.locator('#main')).to_contain_text('今回のふりかえり')
     assert p.evaluate('window.__themeStorageWrites')==[] and disk(p)==before_math
     p.screenshot(path=str(OUT/f'{mode}-math-result.png'))
    assert p.evaluate("YuikaParent.storage.getItem('yuika-ui-theme-kamakura-v1')")==stored
    assert p.evaluate('window.__themeStorageWrites')==[]
    kamakura(p,parent)
    expect(p.locator('html')).to_have_attribute('data-ui-theme',theme)
    assert p.evaluate('data.events.length')==5
    assert p.evaluate('window.__themeStorageWrites')==[] and disk(p)==before_math
    if parent:assert disk(p)==original
    math_sets.append({'selected_theme':theme,'math_appearance_equal_baseline':True,'math_theme_ui_count':0,'math_theme_writes':0,'theme_restored_on_return':True,'kamakura_events_after_return':5,'preview_csp_blocks_connections':True})
   rows.append({'mode':mode,'question_types':types,'events_after_reload':5,'theme_restored_after_reload':'kamakura','stages':'input/selection,hint,graded,result','theme_notification_calls':0,'child_local_storage_unchanged':True if parent else None,'math_comparisons':math_sets});c.close()
  assert not posts and not errors
  result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'cases':rows,'diagram_contrasts':ratios,'post_requests_or_arrivals':posts,'page_errors':errors,'external_gets_aborted':len(external),'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  (OUT/'probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS normal/parent same-run/reload, theme-to-math-return noninterference, diagram contrasts');browser.close()
finally:srv.shutdown();srv.server_close()
