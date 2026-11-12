"""Design C and privacy across every entry, using fresh synthetic storage only."""
import os, re, subprocess, sys
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT

class Quiet(PreviewHandler):
 def log_message(self,*args):pass

css=(ROOT/'assets/design.css').read_text()
for color in ('#F5F6FA','#232733','#5B6274','#E07B39','#A24E17','#1F9A92','#146660','#2C4A8A','#6A3E8E','#FFD34D'):
 assert color in css,color
assert 'M+PLUS+Rounded+1c:wght@500;700;800' in css
# Test readable subject labels and secondary text against white.
def luminance(s):
 rgb=[int(s[i:i+2],16)/255 for i in (1,3,5)]
 return sum(w*(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4) for w,x in zip((.2126,.7152,.0722),rgb))
for color in ('#5B6274','#A24E17','#146660','#2C4A8A','#6A3E8E'):
 assert 1.05/(luminance(color)+.05)>=4.5,color
assets={}
for path in ('react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js'):
 url='https://unpkg.com/'+path
 assets[url]=subprocess.check_output(['curl','-fsSL','--max-time','30',url])
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for width in (390,768,1024):
   c=browser.new_context(viewport={'width':width,'height':1024});c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
   def route(r):
    if r.request.url.startswith(base):r.continue_()
    elif r.request.url in assets:r.fulfill(body=assets[r.request.url],content_type='application/javascript')
    else:r.abort()
   c.route('**/*',route);p=c.new_page();p.on('dialog',lambda d:d.accept());errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   p.goto(base+'index.html');p.locator('.unit-card').first.wait_for()
   p.evaluate('''()=>{localStorage.setItem('yuika_parent-email','hidden-parent@example.test');localStorage.setItem('yuika-mail-config-v1',JSON.stringify({enabled:true,endpoint:'https://example.workers.dev',token:'x'.repeat(32),recipient:'hidden-recipient@example.test'}));}''')
   p.reload();p.locator('.unit-card').first.wait_for()
   before=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
   text=p.locator('body').inner_text()
   assert 'hidden-parent@' not in text and 'hidden-recipient@' not in text
   assert 'Claude' not in text
   assert len(p.locator('.unit-card').all())==14
   assert p.locator('.unit-grid').evaluate("e=>getComputedStyle(e).gridTemplateColumns.split(' ').length")==2
   p.get_by_role('button',name='理科',exact=True).click()
   assert p.locator('.unit-card').count()==8 # seven science units and the four-subject review
   p.get_by_role('button',name='国語',exact=True).click()
   assert p.locator('.unit-card').count()==1
   p.get_by_role('button',name='すべて',exact=True).click()
   # Every original embedded unit still opens its full quiz and flash entry.
   names=p.locator('.unit-card .unit-name').all_text_contents()
   if width==768:
    for name in names:
     if any(s in name for s in ('弱点対策','鎌倉幕府','応仁の乱','貴族の世の中')):continue
     p.get_by_role('button',name=name,exact=False).click()
     expect(p.locator('.unit-hero h1')).to_have_text(name)
     expect(p.get_by_role('button',name='復習クイズ',exact=False)).to_be_visible()
     expect(p.get_by_role('button',name='暗記カード',exact=False)).to_be_visible()
     p.locator('.unit-header button').first.click()
   assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==before
   for entry,subject in [('onin-review.html','social'),('kamakura-review.html','social'),('heian-review.html','social'),('yuika-review-v2.html','science'),('mock-focus-review.html','all')]:
    p.goto(base+entry)
    expect(p.locator('.unit-hero')).to_be_visible()
    assert p.locator('html').get_attribute('data-subject')==subject
    assert p.locator('.stats .stat').count()==3
    assert p.locator('.stats .stat span').all_text_contents()==['できた数','今日の再確認','にがて']
    assert not p.locator('#prototype-notice').count()
    assert not re.search('[\U0001F300-\U0001FAFF]',p.locator('body').inner_text())
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),(entry,width)
    small=p.locator('button,a,input,select,summary').evaluate_all('''els=>els.filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.height&&e.checkVisibility()&&(r.width<44||r.height<44)}).map(e=>e.outerHTML)''')
    assert not small,(entry,width,small)
    if width==768:
     p.add_script_tag(url=base+'assets/progress.js')
     p.evaluate('''() => {
      const science=typeof byId!=='undefined',qs=QUESTIONS.filter(q=>q.type==='text'||q.type==='choice').slice(0,2);
      const mk=(q,days,correct)=>{
       const at=new Date(Date.now()-days*86400000).toISOString();
       const common={id:crypto.randomUUID(),sessionId:'synthetic-design',questionId:q.id,unit:q.unit,question:q.prompt,response:correct?q.answer:(q.type==='choice'?q.options.find(o=>o!==q.answer):'合成誤答'),expected:science?q.answer:expectedOf(q,'normal'),explanation:q.explanation,correct,mode:'normal'};
       return validateEvent(science?{...common,inputRaw:common.response,type:q.type,datasetVersion:VERSION,answeredAt:at,timezoneOffset:0,localDay:localDay(at,0),hintUsed:false}:{...common,...(typeof UNIT_ID==='undefined'?{reflection:''}:{unitId:UNIT_ID}),version:VERSION,course:q.course,variant:'normal',hint:false,at,offset:0,day:day(at,0)});
      };
      const events=[mk(qs[0],4,false),mk(qs[0],3,false),mk(qs[0],2,true),mk(qs[1],4,false),mk(qs[1],3,false)];
      (science?state:data).events=events;
      YuikaParent.storage.setItem(KEY,JSON.stringify(science?state:data));
      const summary=YuikaDesign.summary(location.pathname.split('/').pop());
      if(!summary||summary.correct!==1||summary.due!==(science?scienceDue():dueReviews()).length||summary.weakCount!==(science?scienceWeak():additional()).length)throw Error('Home counts disagree with existing review engine');
      if(summary.due!==1||summary.weakCount!==1||summary.normalCount!==3)throw Error('Synthetic due / weak / normal breakdown');
      home();
     }''')
    p.locator('#start').click();expect(p.locator('#check')).to_be_visible()
    assert p.locator('#check').evaluate("e=>getComputedStyle(e).borderRadius")=='14px'
    p.locator('.unit-footer a').click();expect(p.locator('#prototype-notice')).to_be_visible()
   p.goto(base+'index.html?parent-check=1');p.locator('.unit-card').first.wait_for()
   expect(p.locator('#parent-check-banner')).to_be_visible()
   assert '@example.test' not in p.locator('body').inner_text()
   assert not errors,errors
   c.close()
  browser.close()
print('design_c: all 14 home units, five standalone units, three widths, controls, no writes, colors and recipient privacy PASS')
