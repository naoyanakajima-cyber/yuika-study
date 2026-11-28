"""Check both authorized preview pages and CSP on the exact candidate."""
import json,runpy,sys,subprocess
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
ROOT=Path(sys.argv[1]).resolve();OUT=Path(__file__).resolve().parent
Handler=runpy.run_path(str(ROOT/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
 def log_message(self,*args):pass
result={'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'pages':[]}
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as srv:
 t=Thread(target=srv.serve_forever,daemon=True);t.start()
 try:
  for page in ['content-review.html','math-passage-review.html']:
   with urlopen(f'http://127.0.0.1:{srv.server_port}/{page}') as r:
    assert r.status==200 and r.read()==(ROOT/page).read_bytes()
    csp=r.headers['Content-Security-Policy']
    for directive in ["connect-src 'none'","form-action 'none'","object-src 'none'"]:assert directive in csp
    result['pages'].append({'page':page,'status':200,'byte_identical':True,'csp':csp})
 finally:srv.shutdown();t.join()
result['result']='passed';(OUT/'preview-probe-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
