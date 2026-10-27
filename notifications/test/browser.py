"""Real browser UI tests with a mocked mail endpoint; no real email is sent."""
import json,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[2]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{srv.server_port}/'
CONFIG={'enabled':True,'endpoint':'https://test-notify.example.workers.dev','token':'test-device-key-123456789012345678901234','recipient':'parent@example.test, mother@example.test'}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':768,'height':1024});p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 received=[];fail=[False]
 def handle(r):
  if r.request.method=='OPTIONS':r.fulfill(status=204,headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'Authorization, Content-Type','Access-Control-Allow-Methods':'GET, POST, OPTIONS'});return
  if r.request.url.endswith('/health'):body={'ready':True,'recipient':CONFIG['recipient']};status=200
  else:
   received.append(r.request.post_data_json)
   body={'error':'unavailable'} if fail[0] else {'accepted':True};status=502 if fail[0] else 200
  r.fulfill(status=status,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps(body))
 p.route('https://test-notify.example.workers.dev/**',handle)
 p.goto(BASE+'heian-review.html')
 p.evaluate("YuikaReports.enqueue({id:'not-connected-123'})")
 assert not received
 expect(p.locator('#yuika-mail-status')).to_contain_text('未接続')
 # Explicit pairing, credentials stored on device only.
 p.get_by_text('保護者：チャレンジ結果の自動メール',exact=True).click();p.locator('#yuika-mail-url').fill(CONFIG['endpoint']);p.locator('#yuika-mail-token').fill(CONFIG['token']);p.on('dialog',lambda d:d.accept());p.locator('#yuika-mail-form button[type=submit]').click()
 p.wait_for_function("JSON.parse(localStorage.getItem('yuika-mail-config-v1')||'null')?.enabled===true")
 p.locator('#course').select_option('memory');p.locator('#start').click()
 for i in range(5):
  q=p.evaluate('run.qs[run.index]')
  if i==1:p.locator('#hint').click()
  p.locator('#response').fill(q['answer'] if i else '別の答え');p.locator('#check').click()
  if i<4:assert not received
  p.locator('#next').click()
 expect(p.locator('#yuika-mail-status')).to_contain_text('受け付けました')
 assert len(received)==1 and received[0]['app']=='social' and received[0]['correct']==4
 assert received[0]['answers'][0]['response']=='別の答え'
 assert received[0]['answers'][1]['hint'] is True
 p.evaluate('result();result()');p.reload();assert len(received)==1
 print('PASS no send before pairing; pair UI; send once per challenge, not per answer; details/hints; result rerender/reload dedup',flush=True)
 assert p.evaluate("JSON.parse(localStorage.getItem('yuika-mail-config-v1')).recipient")==CONFIG['recipient']
 # Science page shares pairing and durable retry across a page close/reload.
 fail[0]=True;p.goto(BASE+'yuika-review-v2.html');p.locator('#unit').select_option('溶解度の計算');p.locator('#start').click()
 for _ in range(5):
  q=p.evaluate('session.questions[session.index]');p.locator('#numeric').fill(str(q['answer']));p.locator('#check').click();p.locator('#next').click()
 expect(p.locator('#yuika-mail-status')).to_contain_text('保留中')
 science=received[-1];assert science['app']=='science' and science['total']==5
 pending=p.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('yuika-mail-job-v1:')).map(k=>JSON.parse(localStorage.getItem(k))).filter(j=>j.status==='pending')")
 assert len(pending)==1 and pending[0]['report']==science
 learning=p.evaluate("localStorage.getItem('yuika-science-review-v2')")
 assert learning is not None
 # Simulate passage of backoff time and a new visit.
 p.evaluate("()=>{for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('yuika-mail-job-v1:')){const v=JSON.parse(localStorage.getItem(k));if(v.status==='pending'){v.nextAttempt=0;localStorage.setItem(k,JSON.stringify(v));}}}}")
 fail[0]=False;p.reload();expect(p.locator('#yuika-mail-status')).to_contain_text('受け付けました')
 assert received[-1]==science
 assert p.evaluate("localStorage.getItem('yuika-science-review-v2')")==learning
 print('PASS science completion; queued on provider failure; same payload and ID retried on next visit',flush=True)
 # Quota failures do not break learning; accepted receipts contain no answer payload.
 receipts=p.evaluate("Object.keys(localStorage).filter(k=>k.startsWith('yuika-mail-job-v1:')).map(k=>JSON.parse(localStorage.getItem(k)))")
 assert all(v['status']=='accepted' and 'report' not in v for v in receipts)
 p.get_by_text('保護者：チャレンジ結果の自動メール',exact=True).click();p.locator('#yuika-mail-stop').click();n=len(received)
 p.evaluate("YuikaReports.enqueue({id:'disabled-1234567'})");assert len(received)==n
 print('PASS stop setting, no historical bulk send, accepted queue removes answer content',flush=True)
 # Existing React app integration; exact CDN assets fetched with normal TLS verification.
 assets={}
 for path in ['react@18/umd/react.production.min.js','react-dom@18/umd/react-dom.production.min.js','@babel/standalone@7/babel.min.js']:
  url='https://unpkg.com/'+path;assets[url]=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',url])
 p.route('https://unpkg.com/**',lambda r:r.fulfill(body=assets[r.request.url],content_type='application/javascript'))
 p.evaluate('(x)=>localStorage.setItem("yuika-mail-config-v1",JSON.stringify(x))',CONFIG)
 p.goto(BASE+'index.html');p.get_by_role('button',name='環境問題・公害',exact=False).click(timeout=60000);p.get_by_role('button',name='復習クイズ',exact=False).click()
 for _ in range(10):
  p.get_by_role('button',name='わからない（正解を見る）',exact=False).click()
  p.get_by_role('button',name='次の問題へ',exact=False).or_(p.get_by_role('button',name='結果を見る',exact=False)).click()
 expect(p.locator('#yuika-mail-status')).to_contain_text('受け付けました')
 assert received[-1]['app']=='legacy' and received[-1]['correct']==0 and received[-1]['total']==10
 assert received[-1]['answers'][0]['hint'] is None
 print('PASS existing quiz sends summary once, preserves unknown answer/hint fields as unknown',flush=True)
 # Flash cards: wrong final card counted once, log first round, retry completion sends once.
 p.goto(BASE+'index.html');p.get_by_role('button',name='環境問題・公害',exact=False).click(timeout=60000);p.get_by_role('button',name='暗記カード',exact=False).click();p.get_by_role('button',name='条約・制度',exact=False).click()
 answers=['ラムサール条約','世界遺産条約','ワシントン条約','ナショナルトラスト']
 def flash_expected():
  prompt=p.locator('input[placeholder="答えを入力…"]').locator('..').locator('..').inner_text()
  if '湿地' in prompt:return 'ラムサール条約'
  if '国連' in prompt:return 'ユネスコ'
  if '動植物' in prompt:return 'ワシントン条約'
  return 'ナショナルトラスト'
 before=len(received)
 for i in range(4):
  if i in [0,3]:p.get_by_role('button',name='🤔 わからない',exact=True).click()
  else:p.locator('input[placeholder="答えを入力…"]').fill(flash_expected());p.get_by_role('button',name='答え合わせ',exact=True).click()
  p.get_by_role('button',name='次のカード',exact=False).or_(p.get_by_role('button',name='結果を見る',exact=False)).click()
 p.locator('input[placeholder="答えを入力…"]').wait_for();assert len(received)==before
 for _ in range(2):
  p.locator('input[placeholder="答えを入力…"]').fill(flash_expected());p.get_by_role('button',name='答え合わせ',exact=True).click();p.get_by_role('button',name='次のカード',exact=False).or_(p.get_by_role('button',name='結果を見る',exact=False)).click()
 expect(p.locator('#yuika-mail-status')).to_contain_text('受け付けました')
 assert len(received)==before+1 and received[-1]['total']==4 and received[-1]['correct']==2
 assert len(received[-1]['answers'])==4
 assert not errors,errors
 print('PASS flash-card completion after retry, first-round 2/4 score, no duplicate final wrong, no JS errors',flush=True)
 # Validate real browser payloads against the production server contract.
 code="import {validateReport} from './notifications/worker.mjs'; let s=''; for await (const c of process.stdin) s+=c; JSON.parse(s).forEach(validateReport); console.log('PASS actual browser payloads satisfy worker schema');"
 subprocess.run(['node','--input-type=module','-e',code],input=json.dumps(received),text=True,check=True,cwd=ROOT)
 b.close()
