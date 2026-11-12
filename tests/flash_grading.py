"""Exact registered-answer grading and synthetic legacy-history compatibility."""
import os
import subprocess
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

old = {'ts':'2026-10-01T00:00:00.000Z','mode':'flash','subject':'社会',
       'unit':'synthetic-old','correct':1,'wrong':0,'total':1,'retry':0}
with ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT))) as server:
    Thread(target=server.serve_forever, daemon=True).start()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
        context = browser.new_context(viewport={'width':768,'height':1024})
        context.add_init_script(path=str(ROOT / 'tests/seed_random.js'))
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda e: (errors.append(str(e)), print('pageerror:', e, flush=True)))
        # Expose actual grading functions and original data only in this routed fixture.
        html = (ROOT / 'index.html').read_text()
        html = html.replace('// --- UTILS ---', '''
window.flashTest = {checkFlashAnswer, flashGradingLabel, UNITS, FLASH_GRADING_VERSION};
// A one-card deck keeps the complete UI/save/reload regression focused.
const fixtureUnit = UNITS.find(u=>u.id==='shakai-env');
fixtureUnit.flashDecks = [{name:'合成テスト', cards:[{q:'合成：中国を答える',a:'中国',alt:['中華人民共和国']}]}];
// --- UTILS ---''')
        # Save original card data before the fixture mutates its deck.
        html = html.replace('window.flashTest = {', 'window.originalCards = UNITS.flatMap(u=>u.flashDecks.flatMap(d=>d.cards));\nwindow.flashTest = {')
        base = f'http://127.0.0.1:{server.server_port}'
        page.route(base+'/index.html', lambda r:r.fulfill(body=html,content_type='text/html'))
        # Browser outbound assets use the same proxy-aware curl path as notification tests.
        assets = {}
        for path in ('react@18/umd/react.production.min.js', 'react-dom@18/umd/react-dom.production.min.js', '@babel/standalone@7/babel.min.js'):
            url = 'https://unpkg.com/' + path
            assets[url] = subprocess.check_output(['curl','--fail','--silent','--show-error','--location','--max-time','30',url])
        page.route('https://unpkg.com/**', lambda r:r.fulfill(body=assets[r.request.url],content_type='application/javascript'))
        page.goto(base+'/index.html')
        page.get_by_role('button', name='環境問題・公害', exact=False).wait_for(timeout=60000)
        page.evaluate('''() => {
          const check=flashTest.checkFlashAnswer;
          const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
          for(const bad of ['国','中','中国ではない','中国以外','中国と日本','中国。','ちゅうごく',''])
            assert(!check(bad,'中国',['中華人民共和国']),bad);
          for(const good of ['中国',' 中 国　','中華人民共和国'])
            assert(check(good,'中国',['中華人民共和国']),good);
          assert(!check('人民共和国','中国',['中華人民共和国']),'partial alt');
          assert(!check('中国ではない','中国'),'negative');
          for(const good of ['ナショナルトラスト','なしょなるとらすと','ﾅｼｮﾅﾙﾄﾗｽﾄ',' ナショナル　トラスト '])
            assert(check(good,'ナショナルトラスト'),good);
          assert(check('２９．７％','29.7%'),'full width');
          assert(check('ガス','がす') && check('ｶﾞｽ','がす') && check('がす','ガス'),'voiced kana');
          for(const bad of ['29.7','297%','29-7%'])assert(!check(bad,'29.7%'),bad);
          assert(!check('土倉','土倉・酒屋'),'no automatic splitting');
          assert(check('読み','漢字',['読み']),'explicit alt');
          assert(flashTest.flashGradingLabel('registered-exact-v2')==='登録された答えで確認','child-friendly current label');
          assert(flashTest.flashGradingLabel() === '以前の方法（版の記録なし）','legacy label');
          assert(flashTest.flashGradingLabel('synthetic-future') === '別の採点方法（版：synthetic-future）','unknown version label');
          for(const card of originalCards){
            assert(check(card.a,card.a,card.alt),card.a);
            for(const alt of card.alt||[])assert(check(alt,card.a,card.alt),alt);
          }
        }''')
        page.evaluate('old=>{localStorage.clear();localStorage.setItem("yuika_sessions",JSON.stringify([old]));localStorage.setItem("synthetic-other","keep")}',old)
        page.reload()
        page.get_by_role('button',name='環境問題・公害',exact=False).click(timeout=60000)
        page.get_by_role('button',name='暗記カード',exact=False).click()
        page.get_by_role('button',name='合成テスト',exact=False).click()
        page.locator('input[placeholder="答えを入力…"]').fill('国')
        page.get_by_role('button',name='答え合わせ',exact=True).click()
        expect(page.get_by_text('中国',exact=True)).to_be_visible()
        page.get_by_role('button',name='結果を見る',exact=False).click()
        # Wrong answer must enter retry, without saving a completed perfect session.
        expect(page.locator('input[placeholder="答えを入力…"]')).to_be_visible()
        assert page.evaluate('JSON.parse(localStorage.getItem("yuika_sessions"))') == [old]
        page.locator('input[placeholder="答えを入力…"]').fill(' 中 国 ')
        page.get_by_role('button',name='答え合わせ',exact=True).click()
        page.get_by_role('button',name='結果を見る',exact=False).click()
        page.wait_for_function('()=>JSON.parse(localStorage.getItem("yuika_sessions")).length===2')
        records = page.evaluate('JSON.parse(localStorage.getItem("yuika_sessions"))')
        assert records[1] == old
        assert records[0]['gradingVersion']=='registered-exact-v2'
        assert records[0]['correct']==0 and records[0]['wrong']==1 and records[0]['retry']==1
        page.reload()
        assert page.evaluate('JSON.parse(localStorage.getItem("yuika_sessions"))') == records
        assert page.evaluate('localStorage.getItem("synthetic-other")')=='keep'
        page.get_by_role('button',name='きろく',exact=False).click()
        expect(page.get_by_text('答えの確認方法：登録された答えで確認',exact=True)).to_be_visible()
        expect(page.get_by_text('答えの確認方法：以前の方法（版の記録なし）',exact=True)).to_be_visible()
        # The learning entry resumes the last social unit with one tap.
        page.goto(base+'/index.html')
        page.get_by_role('button',name='今日の5問をはじめる',exact=True).wait_for()
        page.evaluate("localStorage.setItem('yuika-prototype-v1:last-daily-unit','heian-review.html')")
        page.get_by_role('button',name='今日の5問をはじめる',exact=True).click()
        page.wait_for_url('**/heian-review.html?daily=1')
        assert page.evaluate("run.mode==='daily'&&run.qs.length===5")
        assert not errors, errors
        browser.close()
print('flash-grading: exact answers, registered alts, normalization, UI retry, version and historical preservation PASS')
