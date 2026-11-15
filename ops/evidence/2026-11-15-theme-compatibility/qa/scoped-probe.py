"""Independent synthetic compatibility probe. Run only against a frozen candidate."""
import os,json,re,subprocess,importlib.util,time
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-theme-compatibility-20261115')
OUT=Path('/tmp/yuika-cycle24-qa')
THEME='yuika-ui-theme-kamakura-v1'
CHILD='yuika-social-540-25-v1'
PROTO='yuika-prototype-v1:'+CHILD
PREFIX='yuika-parent-check-v1:'
spec=importlib.util.spec_from_file_location('serve',ROOT/'scripts/cloud/serve.py');serve=importlib.util.module_from_spec(spec);spec.loader.exec_module(serve)
posts=[];errors=[];blocked_external=[];rows=[];colors=[]
class Handler(serve.PreviewHandler):
 def log_message(self,*args): pass
 def do_POST(self): posts.append(self.path);self.send_error(405)
def server(path):
 s=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(path)));Thread(target=s.serve_forever,daemon=True).start();return s,f'http://127.0.0.1:{s.server_port}/'
app,BASE=server(ROOT);gold,GOLD=server(OUT/'baseline')
def record(name): rows.append(name)
def local(p): return p.evaluate('Object.fromEntries(Object.entries(localStorage).sort())')
def session(p): return p.evaluate('Object.fromEntries(Object.entries(sessionStorage).sort())')
def state(p):
 return p.evaluate("""()=>({run:JSON.stringify(run),data:JSON.stringify(data),prefs:JSON.stringify(prefs),screen,blocked,dirty,
 html:main.innerHTML,values:[...main.querySelectorAll('input,select,textarea')].map(e=>[e.id,e.value]),notice:document.querySelector('#notice').textContent})""")
def choose(p,value,mode='normal'):
 before=state(p);beforelocal=local(p);p.evaluate('window.qaMain=main.firstElementChild;window.qaBeforeRequests=performance.getEntriesByType("resource").length')
 p.locator('#theme-'+value).click();expect(p.locator('html')).to_have_attribute('data-ui-theme',value)
 assert state(p)==before,'learning state/DOM changed'
 assert p.evaluate('main.firstElementChild===qaMain'),'learning DOM node replaced'
 assert p.evaluate('performance.getEntriesByType("resource").length===qaBeforeRequests'),'theme generated resource requests'
 after=local(p)
 if mode=='normal': assert {k:v for k,v in beforelocal.items() if k!=THEME}=={k:v for k,v in after.items() if k!=THEME}
 else: assert beforelocal==after,'parent theme touched normal storage'
 assert p.evaluate('(k)=>YuikaParent.storage.getItem(k)',THEME)==value
def fresh(browser,mode='normal',seed=None,fault=None,base=BASE):
 c=browser.new_context(viewport={'width':768,'height':1024});c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
 c.route('**/*',lambda r:r.continue_() if r.request.url.startswith((BASE,GOLD)) else (blocked_external.append(r.request.url),r.abort())[-1])
 values={CHILD:'{"synthetic":"child-preserve"}','yuika-social-540-27-v1':'{"synthetic":"other-preserve"}','yuika-mail-config-v1':'{"enabled":false,"synthetic":true}'}
 if seed:values.update(seed)
 c.add_init_script("""(x=>{
 if(!localStorage.getItem('__qaSeed')){Object.entries(x.seed).forEach(([k,v])=>localStorage.setItem(k,v));localStorage.setItem('__qaSeed','1');}
 const g=Storage.prototype.getItem,s=Storage.prototype.setItem;window.qaOps=[];window.qaFault=x.fault;
 Storage.prototype.getItem=function(k){qaOps.push(['get',this===localStorage?'local':'session',k]);if(x.mode==='temporary'&&this===sessionStorage)throw new DOMException('synthetic','SecurityError');if(k===x.key&&qaFault==='get')throw new DOMException('synthetic','SecurityError');return g.call(this,k);};
 Storage.prototype.setItem=function(k,v){qaOps.push(['set',this===localStorage?'local':'session',k]);if(x.mode==='temporary'&&this===sessionStorage)throw new DOMException('synthetic','SecurityError');if(k===x.key&&qaFault==='set')throw new DOMException('synthetic','QuotaExceededError');return s.call(this,k,v);};
 })("""+json.dumps({'seed':values,'mode':mode,'fault':fault,'key':THEME})+");")
 p=c.new_page();p.set_default_timeout(6000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
 p.goto(base+'kamakura-review.html'+('?parent-check=1' if mode=='parent' else ''));expect(p.locator('#start')).to_be_visible();return c,p
def ratio(a,b):
 def lum(c):
  v=[float(x)/255 for x in re.findall(r'[\d.]+',c)[:3]];assert len(v)==3,c
  return sum(w*(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4) for x,w in zip(v,[.2126,.7152,.0722]))
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
STYLE_JS="""e=>{let n=e,bg;while(n){bg=getComputedStyle(n).backgroundColor;if(bg!=='rgba(0, 0, 0, 0)')break;n=n.parentElement;}return {fg:getComputedStyle(e).color,bg,font:getComputedStyle(e).fontSize,line:getComputedStyle(e).lineHeight};}"""
def view(p,name,mode='normal'):
 for theme in ['standard','kamakura']:
  choose(p,theme,mode)
  assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(name,theme,'overflow')
  for selector in ['.theme-description','.theme-choice[aria-pressed=true]','.theme-choice[aria-pressed=false]','#main h1','#main p','#main .muted','#main .note']:
   es=p.locator(selector)
   visible=[es.nth(i) for i in range(es.count()) if es.nth(i).is_visible()]
   if not visible:continue
   s=visible[0].evaluate(STYLE_JS);r=ratio(s['fg'],s['bg']);colors.append({'view':name,'theme':theme,'selector':selector,**s,'ratio':r});assert r>=4.5,(name,theme,selector,s,r)
  p.locator('.theme-panel').scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'{name}-{theme}.png'))
 record('both themes '+name+' visible text/overflow/learning invariance')
def style(p): return {s:p.locator(s).first.evaluate(STYLE_JS) for s in ['body','.unit-hero','.unit-hero h1','.unit-hero p','.practice-card','#start']}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  c,p=fresh(browser);g,gp=fresh(browser,base=GOLD)
  standard=style(p);assert standard==style(gp),'standard does not match main';record('standard computed appearance matches main')
  choose(p,'kamakura');assert style(p)!=standard;choose(p,'standard');assert style(p)==standard;record('distinct theme and exact standard restore');g.close();c.close()
  for mode in ['parent','temporary']:
   c,p=fresh(browser,mode,seed={THEME:'kamakura'});initial=local(p);expect(p.locator('#parent-check-banner')).to_be_visible();expect(p.locator('html')).to_have_attribute('data-ui-theme','standard')
   assert not p.evaluate('(k)=>qaOps.some(x=>x[0]==="get"&&x[1]==="local"&&x[2]===k)',THEME),'parent read child theme'
   choose(p,'kamakura',mode);choose(p,'standard',mode);assert local(p)==initial
   if mode=='parent':
    view(p,'parent-mode-home',mode)
    p.locator('[data-count="5"]').click();p.locator('#start').click();view(p,'parent-mode-quiz',mode)
    for i in range(5):
     q=p.evaluate('run.qs[run.index]')
     if q['type']=='text':p.locator('#response').fill('合成の誤答' if i==0 else q['answer'])
     else:p.locator('.option').filter(has_text=(next(x for x in q['options'] if x!=q['answer']) if i==0 else q['answer'])).first.click()
     p.locator('#hint').click();choose(p,'standard',mode);choose(p,'kamakura',mode);p.locator('#check').click()
     if i==0:view(p,'parent-mode-feedback',mode)
     p.locator('#next').click()
    assert p.evaluate('run.results.length')==5
    assert len(json.loads(session(p)[PREFIX+PROTO])['events'])==5 and local(p)==initial
    record('parent answers persist only to session prototype key')
    p.evaluate('()=>{window.qaEnqueues=0;YuikaReports.enqueue=()=>{qaEnqueues++};}')
    view(p,'parent-mode-result',mode);assert p.evaluate('qaEnqueues')==0
    p.locator('#parent').click();view(p,'parent-mode-note',mode)
    p.locator('[data-view="records"]').click();view(p,'parent-mode-records',mode)
    p.locator('[data-view="home"]').click();p.locator('footer a[href="#parent"]').click();expect(p.locator('h1')).to_contain_text('学びのようす');record('actual footer parent-note route')
    choose(p,'kamakura',mode);p.reload();expect(p.locator('html')).to_have_attribute('data-ui-theme','kamakura');assert local(p)==initial
    assert p.evaluate('data.events.length')==5;record('parent reload restores session theme and synthetic records')
    p.locator('#parent-exit').click();expect(p.locator('#parent-check-banner')).to_have_count(0);expect(p.locator('html')).to_have_attribute('data-ui-theme','kamakura');assert local(p)==initial;assert not any(k.startswith(PREFIX) for k in session(p));record('exit clears parent session and restores normal theme')
   else:
    choose(p,'kamakura',mode);p.locator('#start').click();q=p.evaluate('run.qs[run.index]')
    if q['type']=='text':p.locator('#response').fill(q['answer'])
    else:p.locator('.option').filter(has_text=q['answer']).first.click()
    choose(p,'standard',mode);p.locator('#check').click();assert p.evaluate('data.events.length')==1;assert local(p)==initial;record('temporary memory theme/answer never touches child storage')
    choose(p,'kamakura',mode);p.reload();expect(p.locator('html')).to_have_attribute('data-ui-theme','standard');assert p.evaluate('data.events.length')==0;assert local(p)==initial;record('temporary memory reload clears ephemeral theme and answers')
   c.close()
  assert not posts and not errors,(posts,errors)
  assert all(u.startswith(('https://fonts.googleapis.com/','https://fonts.gstatic.com/')) for u in blocked_external),blocked_external
  browser.close()
finally:
 app.shutdown();gold.shutdown();app.server_close();gold.server_close()
 (OUT/'scoped-probe-result.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'checks':rows,'count':len(rows),'colors':colors,'post_arrivals':posts,'pageerrors':errors,'blocked_external_assets':sorted(set(blocked_external)),'scope':'No theme_review.py, check_all, or export execution; independent parent/memory and baseline presentation only'},ensure_ascii=False,indent=2)+'\n')
print('independent scoped theme compatibility probe PASS',len(rows))
