"""Synthetic theme regression checks; run with python tests/theme_review.py."""
import importlib.util
import json
import os
import re
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
KEY = 'yuika-ui-theme-kamakura-v1'
LEARNING = 'yuika-social-540-25-v1'
OTHER = {
    'yuika-social-540-27-v1': '{"schemaVersion":1,"datasetVersion":"onin-540-27-v1","events":[]}',
    'yuika-social-540-24-v1': '{"schemaVersion":1,"datasetVersion":"heian-540-24-v1","events":[]}',
    'yuika-science-v2': '{"synthetic":"preserve"}',
    'yuika_sessions': '[{"unit":"synthetic"}]',
}
spec = importlib.util.spec_from_file_location('preview', ROOT / 'scripts/cloud/serve.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)
posts = []
class Handler(preview.PreviewHandler):
    def log_message(self, *_):
        pass
    def do_POST(self):
        posts.append(self.path)
        self.send_error(405)

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{server.server_port}/'
external = []
errors = []

def fresh(browser, initial=None, fault=None):
    context = browser.new_context(viewport={'width': 768, 'height': 1024})
    context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(BASE) else (external.append(route.request.url), route.abort())[-1])
    if initial is not None or fault:
        context.add_init_script(f"""(()=>{{
          const key={json.dumps(KEY)}, seed={json.dumps(initial or {})};
          if(!sessionStorage.getItem('theme-test-seeded')){{for(const[k,v]of Object.entries(seed))localStorage.setItem(k,v);sessionStorage.setItem('theme-test-seeded','yes');}}
          const get=Storage.prototype.getItem,set=Storage.prototype.setItem;
          window.themeFault={json.dumps(fault)};window.themeWrites=0;
          Storage.prototype.getItem=function(k){{if(k===key&&window.themeFault==='get')throw new DOMException('synthetic','SecurityError');return get.call(this,k);}};
          Storage.prototype.setItem=function(k,v){{if(k===key){{window.themeWrites++;if(window.themeFault==='set')throw new DOMException('synthetic','QuotaExceededError');}}return set.call(this,k,v);}};
        }})();""")
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(BASE + 'kamakura-review.html')
    return context, page

def storage(page):
    return page.evaluate('Object.fromEntries(Object.entries(localStorage))')

def state(page):
    return page.evaluate("""()=>({run:JSON.stringify(run),data:JSON.stringify(data),prefs:JSON.stringify(prefs),
      html:document.getElementById('main').innerHTML,values:[...document.querySelectorAll('#main input,#main select,#main textarea')].map(e=>[e.id,e.value]),
      notice:document.getElementById('notice').textContent,blocked,dirty})""")

def theme(page, value):
    before = state(page)
    records = storage(page)
    page.locator('#theme-' + value).click()
    expect(page.locator('html')).to_have_attribute('data-ui-theme', value)
    expect(page.locator('#theme-' + value)).to_have_attribute('aria-pressed', 'true')
    assert state(page) == before, 'theme changed learning state/DOM'
    after = storage(page)
    assert {k:v for k,v in after.items() if k != KEY} == {k:v for k,v in records.items() if k != KEY}
    assert after[KEY] == value


def contrast(a, b):
    def luminance(color):
        rgb = [int(x) / 255 for x in re.findall(r'\d+', color)[:3]]
        assert len(rgb) == 3, color
        channels = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in rgb]
        return sum(x*w for x,w in zip(channels, [.2126,.7152,.0722]))
    x,y=sorted([luminance(a),luminance(b)])
    return (y+.05)/(x+.05)

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
        context, page = fresh(browser, OTHER)
        # T1/T2/T4: explicit selection, dedicated key and unchanged synthetic histories.
        expect(page.locator('html')).to_have_attribute('data-ui-theme', 'standard')
        assert KEY not in storage(page) and page.evaluate('themeWrites') == 0
        questions = page.evaluate('QUESTIONS')
        expected_grade = page.evaluate("QUESTIONS.map(q=>[grade(q,q.answer,'normal'),grade(q,'synthetic wrong','normal')])")
        theme(page, 'kamakura')
        theme(page, 'standard')
        theme(page, 'kamakura')
        n = page.evaluate('themeWrites')
        theme(page, 'kamakura')
        assert page.evaluate('themeWrites') == n, 'same saved selection rewrote storage'
        page.reload()
        expect(page.locator('html')).to_have_attribute('data-ui-theme', 'kamakura')
        assert page.evaluate('themeWrites') == 0
        assert page.evaluate('QUESTIONS') == questions
        assert page.evaluate("QUESTIONS.map(q=>[grade(q,q.answer,'normal'),grade(q,'synthetic wrong','normal')])") == expected_grade
        # T8/T9: actual browser colors and controls, including keyboard operation.
        for selector in ['.theme-description', '.theme-choice', '.hero p', '.green-card .muted', '.card h2']:
            colors = page.locator(selector).first.evaluate("e=>{let b=e;while(b&&getComputedStyle(b).backgroundColor==='rgba(0, 0, 0, 0)')b=b.parentElement;return [getComputedStyle(e).color,getComputedStyle(b).backgroundColor];}")
            assert contrast(*colors) >= 4.5, (selector, colors)
        sizes = page.locator('.theme-choice').evaluate_all('es=>es.map(e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))')
        assert all(s['w'] >= 44 and s['h'] >= 44 for s in sizes)
        assert page.locator('.theme-options').evaluate('e=>parseFloat(getComputedStyle(e).gap)') >= 8
        page.locator('#theme-standard').focus();page.keyboard.press('Enter')
        expect(page.locator('#theme-standard')).to_have_attribute('aria-pressed','true')
        page.keyboard.press('Tab');page.keyboard.press('Space')
        expect(page.locator('#theme-kamakura')).to_have_attribute('aria-pressed','true')
        focus = page.locator('#theme-kamakura').evaluate('e=>[getComputedStyle(e).outlineColor,getComputedStyle(document.body).backgroundColor,parseFloat(getComputedStyle(e).outlineOffset)]')
        assert contrast(focus[0],focus[1]) >= 3 and focus[2] >= 3
        border = page.locator('#course').evaluate('e=>[getComputedStyle(e).borderColor,getComputedStyle(e).backgroundColor]')
        assert contrast(*border) >= 3
        page.emulate_media(reduced_motion='reduce')
        theme(page,'standard');theme(page,'kamakura')
        # T5/T6: same run and every input stage survive switches; regular grading persists.
        page.evaluate('Math.random=(()=>{let n=37;return()=>((n=(n*16807)%2147483647)/2147483647);})()')
        page.locator('#start').click()
        seen = set()
        for i in range(15):
            q = page.evaluate('run.qs[run.index]');seen.add(q['type'])
            if q['type'] == 'text': page.locator('#response').fill(q['answer'])
            else: page.locator('.option', has_text=q['answer']).first.click()
            theme(page,'standard');theme(page,'kamakura')
            if i == 0:
                page.locator('#hint').click()
                theme(page,'standard');theme(page,'kamakura')
            page.locator('#check').click()
            assert page.evaluate('run.answered')
            theme(page,'standard');theme(page,'kamakura')
            page.locator('#next').click()
        assert seen == {'text','choice'}
        expect(page.locator('.result strong')).to_contain_text('15')
        saved = storage(page)[LEARNING]
        assert len(json.loads(saved)['events']) == 15
        # T7: switching an existing result never enqueues a notification or makes requests.
        page.evaluate('window.themeEnqueues=0;YuikaReports.enqueue=()=>{themeEnqueues++;};window.themeRequests=0;')
        requests = []
        page.on('request', lambda req: requests.append(req.url))
        theme(page,'standard');theme(page,'kamakura')
        assert page.evaluate('themeEnqueues') == 0 and requests == []
        assert storage(page)[LEARNING] == saved
        for view in ['parent','records','home']:
            page.locator(f'[data-view={view}]').click()
            theme(page,'standard');theme(page,'kamakura')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        # Export schema excludes theme setting.
        page.locator('[data-view=records]').click()
        with page.expect_download() as event: page.locator('#export').click()
        exported=json.loads(Path(event.value.path()).read_text())
        assert KEY not in exported and exported['events'] == json.loads(saved)['events']
        page.reload()
        assert storage(page)[LEARNING] == saved
        # T10: print is neutral without mutating preference.
        page.emulate_media(media='print')
        expect(page.locator('.theme-panel')).to_be_hidden()
        assert page.locator('body').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(255, 255, 255)'
        assert page.locator('body').evaluate('e=>getComputedStyle(e).color') == 'rgb(41, 62, 59)'
        assert storage(page)[KEY] == 'kamakura'
        page.emulate_media(media='screen')
        expect(page.locator('.theme-panel')).to_be_visible()
        # T11: another page does not consume theme setting; return restores only this page.
        page.goto(BASE+'onin-review.html')
        assert page.locator('html').get_attribute('data-ui-theme') is None
        assert storage(page)[KEY] == 'kamakura'
        page.goto(BASE+'kamakura-review.html')
        expect(page.locator('html')).to_have_attribute('data-ui-theme','kamakura')
        for k,v in OTHER.items(): assert storage(page)[k] == v
        context.close()
        # T2/T3: unknown data preserved; synthetic read/write faults do not disable learning.
        for raw in ['unknown','{"theme":"kamakura"}','']:
            context,page=fresh(browser,{KEY:raw})
            expect(page.locator('html')).to_have_attribute('data-ui-theme','standard')
            assert storage(page)[KEY] == raw and page.evaluate('themeWrites') == 0
            theme(page,'standard');context.close()
        context,page=fresh(browser,{KEY:'kamakura'},'get')
        expect(page.locator('html')).to_have_attribute('data-ui-theme','standard')
        assert not page.evaluate('blocked') and page.evaluate('themeWrites') == 0
        page.locator('#start').click();expect(page.locator('#check')).to_be_visible();context.close()
        context,page=fresh(browser,OTHER,'set')
        page.evaluate("document.getElementById('notice').textContent='合成の学習保存警告'")
        original=state(page)
        page.locator('#theme-kamakura').click()
        expect(page.locator('html')).to_have_attribute('data-ui-theme','kamakura')
        expect(page.locator('#theme-status')).to_contain_text('保存できませんでした')
        assert state(page) == original and KEY not in storage(page)
        page.locator('#theme-standard').click()
        expect(page.locator('html')).to_have_attribute('data-ui-theme','standard')
        page.evaluate('themeFault=null')
        theme(page,'standard');expect(page.locator('#theme-status')).to_be_empty()
        assert page.locator('#notice').inner_text() == '合成の学習保存警告'
        context.close()
        assert not external, external
        assert not posts, posts
        assert not errors, errors
        browser.close()
finally:
    server.shutdown();server.server_close()
print('theme-review: all checks passed; external requests 0, POST arrivals 0')
