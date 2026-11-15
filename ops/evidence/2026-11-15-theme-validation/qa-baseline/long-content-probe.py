"""Cycle25: unverified C6 long diagram/table/explanation only, synthetic state."""
import os,json,subprocess,datetime,importlib.util,re
from pathlib import Path
from http.server import ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path('/workspace/yuika-theme-validation-20261115');OUT=Path('/tmp/yuika-cycle25-qa');HEAD='c81fb6b3a7e9c5c6c5d42431afe1d13a73c780d3'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==HEAD
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
assert json.loads((OUT/'after.json').read_text())['exit_code']==0, 'required suites must finish successfully first'
spec=importlib.util.spec_from_file_location('preview',ROOT/'scripts/cloud/serve.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
posts=[];external=[];errors=[];checks=[];svg_colors=[]
def ratio(a,b):
 def lum(c):
  v=[float(x)/255 for x in re.findall(r"[\d.]+",c)[:3]]
  return sum(w*(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4) for x,w in zip(v,[.2126,.7152,.0722]))
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
class Handler(mod.PreviewHandler):
 def log_message(self,*a):pass
 def do_POST(self):posts.append(self.path);self.send_error(405)
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{srv.server_port}/'
STYLE="""e=>({text:e.textContent,html:e.innerHTML,font:getComputedStyle(e).fontSize,line:getComputedStyle(e).lineHeight,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})"""
def snapshot(p):return p.evaluate('()=>({run:JSON.stringify(run),events:JSON.stringify(data.events),main:main.innerHTML})')
def inspect(p,selector,name):
 node=p.locator(selector);initial=node.evaluate(STYLE);states=snapshot(p);raw=[]
 for theme in ['standard','kamakura','standard']:
  p.locator('#theme-'+theme).click();expect(p.locator('html')).to_have_attribute('data-ui-theme',theme)
  assert snapshot(p)==states
  current=node.evaluate(STYLE);assert current==initial,(name,'content/size/spacing change',initial,current)
  assert p.evaluate('document.documentElement.scrollWidth<=innerWidth'),name
  node.scroll_into_view_if_needed();box=node.bounding_box();assert box and box['x']>=0 and box['x']+box['width']<=768.5,(name,box)
  raw.append({'theme':theme,'style':current,'box':box})
  if name=='organization-diagram':
   for row in node.locator('text').evaluate_all("es=>es.filter(e=>e.previousElementSibling?.tagName==='rect').map(e=>({label:e.textContent,fill:getComputedStyle(e).fill,backgroundFill:getComputedStyle(e.previousElementSibling).fill,fontSize:getComputedStyle(e).fontSize}))"):
    row.update(theme=theme,ratio=ratio(row['fill'],row['backgroundFill']));row['meets_4_5']=row['ratio']>=4.5;svg_colors.append(row)
  if len(raw)<3:p.screenshot(path=str(OUT/f'{name}-{theme}.png'))
  p.locator('#theme-standard').scroll_into_view_if_needed();expect(p.locator('#theme-standard')).to_be_visible()
  p.locator('#theme-standard').focus();assert p.evaluate('document.activeElement.id')=='theme-standard'
 checks.append({'name':name,'samples':raw,'content_size_lineheight_identical':True,'standard_restore':True,'toggle_reachable':True})
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'));c=b.new_context(viewport={'width':768,'height':1024});c.add_init_script(path=str(ROOT/'tests/seed_random.js'))
  c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) else (external.append(r.request.url),r.abort())[-1]);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(BASE+'kamakura-review.html?parent-check=1')
  inspect(p,'svg[role=img]','organization-diagram')
  main_html=subprocess.check_output(['git','show','86514eda054a5a2e09204df3a0668e40624c16de:kamakura-review.html'],cwd=ROOT,text=True)
  candidate_html=(ROOT/'kamakura-review.html').read_text()
  def tree_code(h):return h[h.index('function tree()'):h.index('function home()')]
  assert tree_code(main_html)==tree_code(candidate_html)
  bc=b.new_context(viewport={'width':768,'height':1024})
  def baseline_route(r):
   if r.request.url==BASE+'kamakura-review.html':r.fulfill(body=main_html,content_type='text/html')
   elif r.request.url.startswith(BASE):r.continue_()
   else:r.abort()
  bc.route('**/*',baseline_route);bp=bc.new_page();bp.goto(BASE+'kamakura-review.html')
  baseline_svg=bp.locator('svg[role=img] text').evaluate_all("es=>es.filter(e=>e.previousElementSibling?.tagName==='rect').map(e=>({label:e.textContent,fill:getComputedStyle(e).fill,backgroundFill:getComputedStyle(e.previousElementSibling).fill,fontSize:getComputedStyle(e).fontSize}))")
  for row in baseline_svg:row['ratio']=ratio(row['fill'],row['backgroundFill']);row['meets_4_5']=row['ratio']>=4.5
  for theme in ['standard','kamakura']:
   assert [{k:v for k,v in x.items() if k!='theme'} for x in svg_colors if x['theme']==theme][:len(baseline_svg)]==baseline_svg
  bc.close()
  inspect(p,'.tablewrap >> nth=1','religion-comparison-table')
  # Fixture chooses the longest existing explanation. Actual start/check controls remain used.
  q=p.evaluate('QUESTIONS.reduce((a,b)=>a.explanation.length>=b.explanation.length?a:b)');p.locator('#start').click()
  p.evaluate('(id)=>{run.qs=[Q.get(id)];run.index=0;prepare();quiz();}',q['id'])
  if q['type']=='text':p.locator('#response').fill('合成の誤答')
  else:p.locator('.option').filter(has_text=next(x for x in q['options'] if x!=q['answer'])).first.click()
  p.locator('#check').click();expect(p.locator('#feedback')).to_contain_text(q['explanation']);inspect(p,'#feedback','longest-feedback')
  expect(p.locator('#next')).to_be_visible();p.locator('#next').click();assert p.evaluate('run.done')
  assert not posts and not errors
  result={'head':HEAD,'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'main_svg_tree_code_identical':True,'main_svg_baseline':baseline_svg,'svg_text_contrast':svg_colors,'svg_contrast_findings':[x for x in svg_colors if not x['meets_4_5']],'selected_longest_explanation_question_id':q['id'],'explanation_characters':len(q['explanation']),'synthetic_answers':1,'post_arrivals':posts,'page_errors':errors,'blocked_external_gets':external,'limitation':'Chromium 768x1024 CSS px; existing SVG colors/labels preserved, SVG white label contrast measured against immediately preceding rect; two inherited labels below 4.5 are acceptance findings; not real iPad/zoom certification; test fixture selects longest existing explanation, no selection-engine coverage claim'}
  (OUT/'long-content-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('DISPLAY CHECKS PASS; SVG contrast findings:',len(result['svg_contrast_findings']),'observations; POST/pageerror 0; do not call C6 fully passed')
  c.close();b.close()
finally:srv.shutdown();srv.server_close()
