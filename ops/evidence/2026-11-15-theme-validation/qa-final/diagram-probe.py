"""Independent actual SVG 2-box contrast and unchanged-content review after C6 fix."""
import os,re,json,subprocess,datetime,importlib.util
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-theme-qa-final-20261115');OUT=Path('/tmp/yuika-cycle25-qa-final');HEAD='b416d3c08a0d3952e5f0153fdc691d6fa0e492b7'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==HEAD
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
assert json.loads((OUT/'after.json').read_text())['exit_code']==0
spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/cloud/serve.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
posts=[];external=[];errors=[];rows=[]
class Handler(mod.PreviewHandler):
 def log_message(self,*a):pass
 def do_POST(self):posts.append(self.path);self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{srv.server_port}/'
def ratio(a,b):
 def lum(c):
  v=[float(x)/255 for x in re.findall(r'[\d.]+',c)[:3]]
  return sum(w*(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4) for x,w in zip(v,[.2126,.7152,.0722]))
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
def rgb(h):return 'rgb('+', '.join(str(int(h[i:i+2],16)) for i in [1,3,5])+')'
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'));c=b.new_context(viewport={'width':768,'height':1024});c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
  c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1]);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(BASE+'kamakura-review.html')
  svg=p.locator('svg[role=img]');expect(svg).to_have_count(1);dom=svg.evaluate('e=>e.outerHTML');main=p.locator('#main').inner_html()
  for theme in ['standard','kamakura']:
   p.locator('#theme-'+theme).click();expect(p.locator('html')).to_have_attribute('data-ui-theme',theme)
   for media in ['screen','print']:
    p.emulate_media(media=media);assert svg.evaluate('e=>e.outerHTML')==dom;assert p.locator('#main').inner_html()==main
    values=svg.locator('text').evaluate_all("es=>es.filter(e=>e.previousElementSibling?.tagName==='rect').map(e=>({label:e.textContent,fill:getComputedStyle(e).fill,backgroundFill:getComputedStyle(e.previousElementSibling).fill,fontSize:getComputedStyle(e).fontSize,rawBackground:e.previousElementSibling.getAttribute('fill'),bbox:{x:e.getBBox().x,y:e.getBBox().y,width:e.getBBox().width,height:e.getBBox().height}}))")
    assert len(values)==10,len(values)
    for x in values:
     x['contrast']=ratio(x['fill'],x['backgroundFill']);assert x['contrast']>=4.5,x
     assert x['fill']=='rgb(255, 255, 255)' and x['fontSize']=='13px'
     assert x['backgroundFill']==rgb('#8f4f3c' if x['label'] in ['将軍','執権（北条氏）'] else x['rawBackground']),x
    assert sum(x['rawBackground']=='#b57c65' for x in values)==2
    assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
    panel=p.locator('section.card').filter(has=svg);panel.scroll_into_view_if_needed();panel.screenshot(path=str(OUT/f'diagram-{theme}-{media}.png'))
    if media=='print':
     expect(p.locator('.theme-panel')).to_be_hidden();assert p.locator('body').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(255, 255, 255)'
    rows.append({'theme':theme,'media':media,'nodes':values})
   p.emulate_media(media='screen');expect(p.locator('.theme-panel')).to_be_visible()
  assert all(x['nodes']==rows[0]['nodes'] for x in rows)
  p.locator('#theme-standard').click();expect(p.locator('html')).to_have_attribute('data-ui-theme','standard');assert p.locator('#main').inner_html()==main
  assert not posts and not errors
  result={'head':HEAD,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'states':rows,'target_minimum_contrast':min(x['contrast'] for r in rows for x in r['nodes'] if x['label'] in ['将軍','執権（北条氏）']),'all_white_node_minimum_contrast':min(x['contrast'] for r in rows for x in r['nodes']),'diagram_dom_and_geometry_unchanged':True,'all_other_box_fills_preserved':True,'standard_restore':True,'post_arrivals':posts,'page_errors':errors,'blocked_external':external,'limitation':'Chromium 768x1024 CSS px; not print-printer/real iPad/native zoom certification'}
  (OUT/'diagram-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS independent SVG actual contrast:',result['target_minimum_contrast'],'other boxes unchanged, both themes/screen/print; POST/pageerror0')
  c.close();b.close()
finally:srv.shutdown();srv.server_close()
