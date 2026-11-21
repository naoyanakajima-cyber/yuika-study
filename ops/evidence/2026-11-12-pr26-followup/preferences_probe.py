"""Independent QA: public UI subject prefs, parent isolation, summary agreement."""
import os,json
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
ROOT=Path(os.environ['YUIKA_QA_ROOT']);OUT=Path('/tmp/yuika-pr26-qa')
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
results=[]
with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as srv:
 Thread(target=srv.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{srv.server_port}/'
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'));c=b.new_context(viewport={'width':768,'height':1024});c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort());p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
  def visit(q=''):p.goto(base+'mock-focus-review.html'+q)
  def prefs():return p.evaluate('({...prefs})')
  def summary():
   p.add_script_tag(url=base+'assets/progress.js')
   return p.evaluate('YuikaDesign.summary(location.pathname.split("/").pop()+location.search)')
  visit();p.locator('[data-count="15"]').click();legacy=prefs();assert legacy['count']==15
  # Save one subject through the actual controls, then change another subject.
  visit('?subject=math');assert prefs()=={'count':5,'course':'all','unit':'all','variant':'normal'},prefs()
  p.locator('[data-count="10"]').click();math_unit=p.evaluate('UNITS[0]');p.locator('#unit').select_option(math_unit);math_prefs=prefs()
  math_summary=summary();assert math_summary['normalCount']==p.evaluate('dailyQuestions().length'),math_summary
  visit('?subject=science');assert prefs()=={'count':5,'course':'all','unit':'all','variant':'normal'},prefs()
  p.locator('[data-count="15"]').click();science_unit=p.evaluate('UNITS[0]');p.locator('#unit').select_option(science_unit);science_prefs=prefs()
  science_summary=summary();assert science_summary['normalCount']==p.evaluate('dailyQuestions().length'),science_summary
  visit('?subject=math');assert prefs()==math_prefs,(prefs(),math_prefs)
  visit('?subject=science');assert prefs()==science_prefs,(prefs(),science_prefs)
  visit();assert prefs()==legacy,(prefs(),legacy)
  before=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')
  # Parent mode must not inherit or mutate normal-mode subject preferences.
  visit('?subject=math&parent-check=1');assert p.evaluate('YuikaParent.active')
  assert prefs()=={'count':5,'course':'all','unit':'all','variant':'normal'},prefs()
  p.locator('[data-count="15"]').click();p.locator('#unit').select_option(math_unit)
  parent_math=prefs();visit('?subject=science');assert p.evaluate('YuikaParent.active')
  assert prefs()=={'count':5,'course':'all','unit':'all','variant':'normal'},prefs()
  visit('?subject=math');assert prefs()==parent_math
  after=p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))');assert after==before
  p.locator('#parent-exit').click();p.wait_for_function('window.YuikaParent && !window.YuikaParent.active');p.locator('#start').wait_for();assert prefs()==math_prefs
  assert p.evaluate('JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort()))')==before
  assert not errors,errors
  results={'legacy':legacy,'math':math_prefs,'science':science_prefs,'math_summary':math_summary,'science_summary':science_summary,'parent_math':parent_math,'normal_storage_unchanged':after==before,'page_errors':errors}
  c.close();b.close()
(OUT/'preferences-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False,indent=2));print('PASS: subject preferences isolate legacy/math/science, summaries match selectable counts, parent preferences persist only in isolated session and exiting restores normal preferences')
