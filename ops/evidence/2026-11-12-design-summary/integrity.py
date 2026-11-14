import ast, copy, json, os, sys
from pathlib import Path
from threading import Thread
from functools import partial
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT=Path(os.environ.get('YUIKA_QA_ROOT','/workspace/yuika-pr25-review-20261112'));OUT=Path(os.environ.get('YUIKA_QA_OUT','/tmp/yuika-pr25-qa'));OUT.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(ROOT))
from scripts.cloud.serve import PreviewHandler
class Quiet(PreviewHandler):
 def log_message(self,*args):pass
fixture_js=next(n.value for n in ast.walk(ast.parse(Path('/tmp/yuika-pr25-qa/selection.py').read_text())) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('()=>{const science=') and 'synthetic-qa' in n.value)
out=[]
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
 Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'));c=b.new_context();c.route('**/*',lambda r:r.continue_()if r.request.url.startswith(base)else r.abort());p=c.new_page()
  for entry in ['onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html']:
   p.goto(base+entry);p.locator('#start').wait_for();fixture=p.evaluate(fixture_js);valid=fixture['value'];key=fixture['key']
   cases={}
   for field,value in [('questionId','unknown-synthetic'),('correct','yes'),('correct',True),('hintUsed'if entry=='yuika-review-v2.html'else'hint','yes'),('expected','not-the-answer'),('question','wrong-prompt'),('answeredAt'if entry=='yuika-review-v2.html'else'at','not-time'),('response',None)]:
    v=copy.deepcopy(valid);v['events'][0][field]=value;cases[field+':'+str(value)]=v
   v=copy.deepcopy(valid);v['events'].append({**v['events'][0],'correct':True});cases['conflicting_duplicate']=v
   v=copy.deepcopy(valid);v['events'].append(copy.deepcopy(v['events'][0]));cases['identical_duplicate_valid']=v
   v=copy.deepcopy(valid);v['events'][0]=None;cases['null_event']=v
   cases['valid']=valid
   for case,v in cases.items():
    raw=json.dumps(v);p.evaluate('([k,v])=>localStorage.setItem(k,v)',[key,raw]);p.reload();p.locator('#start').wait_for();p.add_script_tag(url=base+'assets/progress.js')
    result=p.evaluate("""()=>({blocked,summary:YuikaDesign.summary(location.pathname.split('/').pop()),raw:YuikaParent.storage.getItem(KEY)})""");result['unchanged']=result.pop('raw')==raw
    result['parity']=(result['summary'] is None or result['summary']['unavailable']) if result['blocked'] else result['summary'] is not None and not result['summary']['unavailable']
    out.append({'entry':entry,'case':case,**result})
  b.close()
(OUT/'integrity-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2));assert all(r['parity']and r['unchanged']for r in out)
