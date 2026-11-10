"""Synthetic iPad WebKit UI regression; never uses personal state or real APIs."""
import sys
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT
from scripts.cloud.check_webkit import launch_webkit

ARTIFACTS = ROOT / 'artifacts/ipad-webkit'
SOCIAL = ('onin-review.html', 'kamakura-review.html', 'heian-review.html')
APPS = (*SOCIAL, 'yuika-review-v2.html')


def layout(page):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), 'horizontal page overflow'
    small = page.locator('button:visible, select:visible, input:not([type=file]):visible, summary:visible, header a:visible').evaluate_all('''els => els.filter(e=>!e.disabled).map(e=>{
      const r=e.getBoundingClientRect();return {text:e.textContent.slice(0,60),w:r.width,h:r.height};
    }).filter(r=>r.w<44 || r.h<44)''')
    assert not small, f'touch targets below 44 CSS px: {small}'


def tap(page, selector):
    locator = page.locator(selector)
    locator.scroll_into_view_if_needed()
    locator.tap()


def keyboard(page, selector):
    original = page.viewport_size
    page.set_viewport_size({'width': original['width'], 'height': max(320, original['height'] - 380)})
    field = page.locator(selector)
    tap(page, selector)
    field.scroll_into_view_if_needed()
    assert field.evaluate('''e=>{const r=e.getBoundingClientRect();const x=r.x+r.width/2,y=r.y+r.height/2;
      return document.activeElement===e && r.top>=0 && r.bottom<=innerHeight && document.elementFromPoint(x,y)===e;
    }'''), 'focused input hidden by header/viewport'
    page.locator('#check').scroll_into_view_if_needed()
    assert page.locator('#check').evaluate('''e=>{const r=e.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)===e;}''')
    layout(page)
    tap(page, '#check')
    page.set_viewport_size(original)


def social(page):
    # Only history is seeded. All answers, navigation and settings use the UI.
    page.evaluate('''() => {
      const q=QUESTIONS.find(q=>q.type==='text' && q.readings?.length);
      const mk=at=>validateEvent({id:uuid(),sessionId:'synthetic-ipad',questionId:q.id,
        ...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),version:VERSION,unit:q.unit,course:q.course,
        question:promptOf(q,'normal'),response:'合成誤答',expected:expectedOf(q,'normal'),explanation:q.explanation,
        correct:false,variant:'normal',mode:'normal',hint:false,...(typeof UNIT_ID==='undefined'?{reflection:''}:{}),at,offset:0,day:day(at,0)});
      data.events=[mk('2026-11-07T00:00:00.000Z'),mk('2026-11-08T00:00:00.000Z')];save();home();
    }''')
    layout(page)
    tap(page, '#daily-five')
    assert page.evaluate("run.mode==='daily' && run.qs.length===5")
    # Weakness comes first. A registered reading is an accepted spelling variant.
    answer = page.evaluate("run.qs[0].readings[0]")
    page.locator('#response').fill(answer)
    keyboard(page, '#response')  # submits the first answer using a tap
    assert page.evaluate('data.events.at(-1).correct')
    assert page.evaluate("retention().some(r=>r.status==='waiting')")
    for index in range(1, 5):
        tap(page, '#next')
        info = page.evaluate('''() => {const q=run.qs[run.index];return {type:q.type,answer:expectedOf(q,run.variant),options:run.options,items:q.items,blanks:q.blanks};}''')
        correct = index != 1
        if info['type'] == 'text':
            page.locator('#response').fill(info['answer'] if correct else '合成の不正解')
        elif info['type'] == 'structure':
            order = list(range(len(info['items'])))
            if not correct:
                order.reverse()
            for step in order:
                tap(page, f'[data-step="{step}"]')
            for i, blank in enumerate(info['blanks']):
                page.locator(f'[data-fill="{i}"]').select_option(blank['answer'])
        else:
            option = info['options'].index(info['answer']) if correct else next(i for i,v in enumerate(info['options']) if v != info['answer'])
            tap(page, f'[data-choice="{option}"]')
        layout(page)
        tap(page, '#check')
        assert page.evaluate('data.events.at(-1).correct') == correct
    tap(page, '#next')
    tap(page, '#parent')
    assert '再確認待ち 1件' in page.locator('#retention-summary').inner_text()
    layout(page)
    tap(page, '[data-view="home"]')
    page.locator('#variant').select_option('kanji')
    tap(page, '[data-count="10"]')
    before = page.evaluate('({prefs:{...prefs}, events:data.events})')
    page.reload()
    assert page.evaluate('({prefs:{...prefs}, events:data.events})') == before
    assert page.locator('#variant').input_value() == 'kanji'
    assert page.locator('[data-count="10"]').get_attribute('aria-pressed') == 'true'


def science(page):
    layout(page)
    tap(page, '#daily-five')
    assert page.evaluate("session.mode==='daily' && session.questions.length===5")
    info = page.evaluate('''() => {const q=session.questions[0];return {type:q.type,answer:q.answer,options:q.options};}''')
    if info['type'] == 'number':
        page.locator('#numeric').fill(str(info['answer']))
        keyboard(page, '#numeric')
    else:
        tap(page, f'[data-choice="{info["options"].index(info["answer"])}"]')
        tap(page, '#check')
    assert page.evaluate('state.events.at(-1).correct')
    before = page.evaluate('state.events')
    page.reload()
    assert page.evaluate('state.events') == before
    tap(page, '[data-view="analysis"]')
    assert page.locator('#science-summary').is_visible()
    layout(page)


def run_case(browser, device, app, scenario, base):
    ctx = browser.new_context(**device)
    ctx.add_init_script(path=str(ROOT / 'tests/seed_random.js'))
    errors, forbidden = [], []
    def route(r):
        if not r.request.url.startswith(base + '/') or r.request.method != 'GET':
            forbidden.append(r.request.url)
            r.abort()
        else:
            r.continue_()
    ctx.route('**/*', route)
    page = ctx.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.clock.install(time=datetime(2026, 11, 10, 3, tzinfo=timezone.utc))
    if scenario == 'unavailable':
        ctx.add_init_script('''Object.defineProperty(window,'localStorage',{get(){throw new DOMException('synthetic private mode','SecurityError');}});''')
    try:
        page.goto(base + '/' + app)
        assert page.evaluate('navigator.maxTouchPoints > 0 && /iPad/.test(navigator.userAgent)')
        assert page.evaluate('devicePixelRatio') == device['device_scale_factor']
        if scenario == 'flow':
            (science if app == APPS[-1] else social)(page)
        elif scenario == 'unavailable':
            assert page.locator('#daily-five').is_disabled()
            assert page.locator('#notice').inner_text()
            tap(page, '[data-view="records"]')
            assert page.locator('#export').is_enabled()
            layout(page)
        else:
            # Missing storage is a usable empty state; empty string and bad JSON are protected corruption.
            assert page.locator('#daily-five').is_enabled()
            tap(page, '[data-view="analysis"]' if app == APPS[-1] else '[data-view="parent"]')
            assert '0' in page.locator('main').inner_text()
            layout(page)
            for raw in ('', '{broken'):
                page.evaluate('(raw)=>localStorage.setItem(KEY,raw)', raw)
                page.reload()
                assert page.locator('#daily-five').is_disabled()
                assert page.evaluate('localStorage.getItem(KEY)') == raw
                assert page.locator('#notice').inner_text()
                tap(page, '[data-view="records"]')
                with page.expect_download() as download:
                    tap(page, '#rawBroken' if app == APPS[-1] else '#broken')
                assert Path(download.value.path()).read_text() == raw
                layout(page)
        assert not errors, errors
        assert not forbidden, forbidden
    except Exception:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        label = f'{app}-{scenario}-{device["viewport"]["width"]}'
        page.screenshot(path=str(ARTIFACTS / f'{label}.png'), full_page=True)
        raise
    finally:
        ctx.close()


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(PreviewHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as pw:
        with launch_webkit(pw) as browser:
            total = 0
            failures = []
            for name in ('iPad (gen 7)', 'iPad (gen 7) landscape'):
                for app in APPS:
                    for scenario in ('flow', 'empty-corrupt', 'unavailable'):
                        try:
                            run_case(browser, pw.devices[name], app, scenario, f'http://127.0.0.1:{server.server_port}')
                            total += 1
                            print(f'PASS {name}: {app}: {scenario}', flush=True)
                        except Exception as exc:
                            failures.append(f'{name}: {app}: {scenario}: {exc}')
                            print(f'FAIL {failures[-1]}', flush=True)
            assert not failures, '\n'.join(failures)
            print(f'ipad_webkit: {total} cases passed')
finally:
    server.shutdown()
