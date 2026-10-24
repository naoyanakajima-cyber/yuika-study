"""540-27「応仁の乱」ページのブラウザーテスト。python3 tests/onin_review.py で実行（Playwright＋Chromium）。"""
import json
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));Thread(target=srv.serve_forever,daemon=True).start()
BASE=f'http://127.0.0.1:{srv.server_port}/'
OTHER={'yuika-social-540-24-v1':'{"schemaVersion":1,"datasetVersion":"heian-540-24-v1","events":[]}','yuika_sessions':'[{"unit":"shakai-env"}]','yuika-science-v2':'{"keep":true}'}
# 30問ぶんの回答記録をページ内で作る補助関数（正規の validateEvent を通す）。
MK="""(id,correct,variant,at)=>{const q=Q.get(id),v=variantOf(q,variant),d=new Date(at);const response=correct?(q.type==='text'?expectedOf(q,v):q.answer):(q.type==='text'?'ちがう':q.options.find(o=>o!==q.answer));
return validateEvent({id:uuid(),sessionId:'seed-session',questionId:id,unitId:UNIT_ID,version:VERSION,unit:q.unit,course:q.course,question:promptOf(q,v),response,expected:expectedOf(q,v),explanation:q.explanation,correct,variant:v,mode:'normal',hint:false,at:d.toISOString(),offset:0,day:day(d.toISOString(),0)});}"""
with sync_playwright() as pw:
 b=pw.chromium.launch();c=b.new_context(viewport={'width':768,'height':1024});p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.route('https://**/*',lambda r:r.abort())
 p.goto(BASE+'onin-review.html');p.evaluate(f"o=>{{localStorage.clear();for(const[k,v]of Object.entries(o))localStorage.setItem(k,v)}}",OTHER);p.reload()
 # データ：30問・一意ID・必須項目・単元
 qs=p.evaluate('QUESTIONS')
 assert len(qs)==30 and len({q['id'] for q in qs})==30
 for q in qs:
  assert q['unitId']=='sapix-540-27' and q['level'] in (1,2,3) and all(q[k] for k in ['unit','prompt','answer','explanation','pitfall','hint']),q['id']
  assert q['type']=='text' or (len(q['options'])==4 and q['answer'] in q['options']),q['id']
 assert sum(q['type']=='choice' for q in qs)>=5 and sum(q['type']=='text' for q in qs)>=15
 # 表記ゆれ・漢字確認・読み確認
 G=lambda id,r,v='normal':p.evaluate('([id,r,v])=>grade(Q.get(id),r,v)',[id,r,v])
 assert G('54027-12','そう村') and G('54027-12','そうそん') and G('54027-12','惣村','kanji') and G('54027-12','そう村','kanji') and not G('54027-12','そうそん','kanji')
 assert G('54027-08','しょうちょうのつちいっき') and G('54027-08','ショウチョウノドイッキ') and G('54027-08','正長の 土一揆') and not G('54027-08','土一揆')
 assert G('54027-06','下克上') and G('54027-20','土倉・酒屋') and G('54027-20','酒屋と土倉') and not G('54027-20','土倉')
 assert G('54027-12','そうそん','yomi') and not G('54027-12','惣村','yomi') and not G('54027-02','足利義満')
 assert p.evaluate("QUESTIONS.filter(canYomi).length")>=15 and not p.evaluate("canYomi(Q.get('54027-01'))")
 # 出やすさ：前回誤答4、未回答3、連続正解で下がる、ペアの相手を誤答なら2
 w=p.evaluate(f"""()=>{{const mk={MK};const es=[mk('54027-15',true,'normal','2026-10-20T00:00:00.000Z'),mk('54027-17',true,'normal','2026-10-20T00:00:00.000Z'),mk('54027-17',true,'normal','2026-10-21T00:00:00.000Z'),
  mk('54027-18',false,'normal','2026-10-21T00:00:00.000Z'),mk('54027-28',true,'normal','2026-10-21T00:00:00.000Z'),mk('54027-29',false,'normal','2026-10-21T00:00:00.000Z')],g=grouped(es);
  return ['54027-01','54027-18','54027-15','54027-17','54027-28'].map(id=>weight(Q.get(id),g,'normal'));}}""")
 assert w==[3,4,1,0.5,2],w
 # 15問：連続正解3回の15問より、未回答・誤答の15問が優先される
 avg=p.evaluate(f"""()=>{{const mk={MK};const es=[];QUESTIONS.forEach((q,i)=>{{if(i<15)for(const d of [20,21,22])es.push(mk(q.id,true,'normal',`2026-10-${{d}}T00:00:00.000Z`));else if(i<20)es.push(mk(q.id,false,'normal','2026-10-22T00:00:00.000Z'));}});
  const g=grouped(es),weak=new Set(QUESTIONS.slice(15).map(q=>q.id));let n=0;for(let t=0;t<200;t++)n+=pick(QUESTIONS,'normal',15,g,'normal').filter(q=>weak.has(q.id)).length;return n/200;}}""")
 assert avg>=12,avg
 # 画面：15問チャレンジ、誤答時は 正解→なぜ→覚え方 の順
 expect(p.locator('h1')).to_have_text('応仁の乱');expect(p.locator('[data-count="15"]')).to_have_attribute('aria-pressed','true')
 expect(p.locator('svg[role=img]')).to_be_visible();expect(p.get_by_text('慈照寺',exact=True)).to_be_visible()
 p.locator('#start').click();assert p.evaluate('run.qs.length')==15
 for i in range(15):
  q=p.evaluate('run.qs[run.index]')
  if q['type']=='text':p.locator('#response').fill('ちがう答え' if i==0 else q['answer'])
  else:p.locator('.option',has_text=q['options'][1] if i==0 and q['answer']!=q['options'][1] else q['answer']).first.click()
  p.locator('#check').click();fb=p.locator('#feedback').inner_text()
  assert fb.index('① 正解')<fb.index('② なぜ？')<fb.index('③ 覚え方'),fb
  if i==0:assert 'いっしょに見てみよう' in fb and q['explanation'] in fb
  p.locator('#next').click()
 expect(p.locator('.result strong')).to_contain_text('14')
 stored=json.loads(p.evaluate("localStorage.getItem('yuika-social-540-27-v1')"))
 assert len(stored['events'])==15 and all(e['unitId']=='sapix-540-27' for e in stored['events'])
 for k,v in OTHER.items():assert p.evaluate('k=>localStorage.getItem(k)',k)==v,k
 # 再読み込み後、前回誤答が「もう一度」に出る
 p.reload();expect(p.locator('[data-mode="wrong"] b')).to_contain_text('1')
 # 読みの確認
 p.locator('#variant').select_option('yomi');p.locator('[data-count="5"]').click();p.locator('#start').click()
 q=p.evaluate('run.qs[run.index]');expect(p.locator('h1.question')).to_contain_text(f"「{q['answer']}」の読み")
 p.locator('#response').fill(q['readings'][0]);p.locator('#check').click();expect(p.locator('#feedback')).to_contain_text('できたね')
 p.on('dialog',lambda d:d.accept());p.locator('#end').click()
 p.locator('[data-view=parent]').click();expect(p.locator('table')).to_contain_text('村の自治')
 assert not errors,errors
 b.close()
print('onin-review: all checks passed')
