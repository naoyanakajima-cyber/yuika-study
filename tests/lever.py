"""Original lever data, progression, history, and mock-only report verification."""

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.history.embed import ARCHIVE, questions

PAGE = 'yuika-review-v2.html'
UNIT_NAME = 'てこのつり合い'
UNIT_ID = 'rika-lever'
MOCK = 'https://lever-notify.example.workers.dev'
CONFIG = {
    'enabled': True,
    'endpoint': MOCK,
    'token': 'synthetic-lever-notification-key-0000',
    'recipient': 'parent@example.test',
}

all_questions = questions((ROOT / PAGE).read_text())
lever = [q for q in all_questions if q.get('unitId') == UNIT_ID]
by_id = {q['id']: q for q in lever}
assert list(by_id) == [f'lever-{i:02}' for i in range(1, 29)]
assert Counter(q['step'] for q in lever) == {0: 6, 1: 8, 2: 8, 3: 4, 4: 2}
archive = json.loads(ARCHIVE.read_text())[PAGE]
for q in lever:
    assert q['level'] == 1 and q['unit'] == UNIT_NAME, q['id']
    assert all(q[field].strip() for field in ('conceptId', 'area', 'prompt', 'hint', 'explanation', 'pitfall', 'basis')), q['id']
    assert q['hint'] != 'まず自分で思い出そう。', q['id']
    assert len(q['steps']) == 5 and all(step.strip() for step in q['steps']), q['id']
    assert q['beam']['weights'] and q['beam']['unknown'], q['id']
    assert len(archive[q['id']]) == 1 and archive[q['id']][0]['question'] == q, q['id']
    if q['type'] == 'choice':
        assert len(q['options']) == len(set(q['options'])), q['id']
        assert set(q['optionTags']) == set(q['options']) - {q['answer']}, q['id']
        assert all(q['optionTags'].values()), q['id']


def prepare(page, *ids):
    """Supply a targeted queue but exercise the real quiz and submit controls."""
    page.evaluate(
        """ids => {
            session = {id:uid(), mode:'unit', questions:ids.map(id=>byId.get(id)),
                       index:0, results:[], hint:false, selected:null, answered:false, done:false};
            view='quiz';
            render();
        }""",
        ids,
    )


def answer(page, q, value=None, hint=False):
    if value is None:
        value = q['answer']
    if hint:
        page.locator('#hint').click()
        expect(page.locator('#hintbox')).to_have_text(q['hint'])
    if q['type'] == 'number':
        page.locator('#numeric').fill(str(value))
    else:
        page.locator('[data-choice]').nth(q['options'].index(value)).click()
    page.locator('#check').click()
    expect(page.locator('#feedback')).to_contain_text(q['steps'][-1])
    return page.evaluate('session.results.at(-1)')


def wrong_option(q):
    return next(o for o in q['options'] if o != q['answer'])


def locked(page):
    assert not page.locator('#lever-challenge').is_visible() or page.locator('#lever-challenge').is_disabled()
    assert page.evaluate("""() => {
        return ['normal','unit','unseen','wrong','spaced','hint'].every(mode =>
            candidates(mode, 'てこのつり合い').every(q => q.step < 4)) &&
            scienceDaily().every(q => q.step < 4);
    }""")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}/'
url = base + PAGE + '?' + urlencode({'unit': UNIT_NAME})
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
        ctx = browser.new_context(viewport={'width': 768, 'height': 1024}, has_touch=True, timezone_id='UTC')
        ctx.add_init_script(path=str(ROOT / 'tests/seed_random.js'))
        posts = []
        mock_calls = []
        errors = []
        logs = []

        def route(r):
            req = r.request
            if req.url.startswith(base) and req.method == 'GET':
                r.continue_()
            elif req.url.startswith(MOCK + '/'):
                mock_calls.append(req.url)
                if req.method == 'POST':
                    posts.append(req.post_data_json)
                r.fulfill(
                    content_type='application/json',
                    headers={
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'authorization, content-type',
                        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    },
                    body='{"accepted":true,"ready":true,"recipient":"parent@example.test"}',
                )
            else:
                r.abort()

        ctx.route('**/*', route)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda msg: logs.append(msg.text))
        page.clock.install(time=datetime(2026, 11, 22, 3, tzinfo=timezone.utc))
        page.goto(url)
        expect(page.locator('.unit-hero h1')).to_have_text(UNIT_NAME)
        assert page.evaluate("""() => {
            const qs = QUESTIONS.filter(q => q.unitId === 'rika-lever');
            for (const q of qs) {
                if (solveBeam(q.beam) !== q.answer || !grade(q,q.answer)) {
                    throw Error(q.id+' '+JSON.stringify(solveBeam(q.beam))+' != '+q.answer);
                }
            }
            return qs.length;
        }""") == 28
        assert page.evaluate("""() => {
            const daily = scienceDaily();
            return daily.length === 5 && daily.every(q=>q.unitId==='rika-lever' && q.step===0);
        }""")
        locked(page)
        # Counting is read-only and agrees with both initial daily batch sizes.
        for upper in (5, 10):
            page.locator(f'[data-count="{upper}"]').click()
            expect(page.locator('#daily-five')).to_have_text(f'今日の復習をはじめる（今回は{upper}問）')
            assert page.evaluate("""() => {
                const original = Math.random, saved = YuikaParent.storage.getItem(KEY);
                let draws = 0;
                Math.random = () => {draws++; return original();};
                try { render(); return draws === 0 && YuikaParent.storage.getItem(KEY) === saved; }
                finally { Math.random = original; }
            }""")
            page.locator('#daily-five').click()
            assert page.evaluate('session.questions.length') == upper
            assert page.evaluate('session.questions[0].step') == 0
            page.locator('#end').click()
        page.locator('[data-count="5"]').click()

        # Exercise the normal unit start entry point after a real index projection.
        page.add_script_tag(url=base + 'assets/progress.js')
        summary = page.evaluate('target => YuikaDesign.summary(target)', PAGE + '?unit=' + UNIT_NAME)
        assert summary['total'] == 28, summary
        summary = page.evaluate("""target => {
            const make = (id, days, correct) => {
                const q = byId.get(id), at = new Date(Date.now() - days * 86400000).toISOString();
                const response = correct ? q.answer : q.options.find(o => o !== q.answer);
                return validateEvent({
                    id:uid(), sessionId:'synthetic-lever-review', questionId:id, datasetVersion:VERSION,
                    unit:q.unit, type:q.type, question:q.prompt, explanation:q.explanation,
                    response, inputRaw:response, expected:q.answer, correct, answeredAt:at,
                    timezoneOffset:0, localDay:at.slice(0,10), hintUsed:false, mode:'unit',
                });
            };
            const original = state, saved = YuikaParent.storage.getItem(KEY);
            try {
                state = emptyState();
                state.events = [
                    make('lever-07', 4, false), make('lever-07', 3, false), make('lever-07', 2, true),
                    make('lever-08', 3, false), make('lever-08', 2, false),
                ];
                if (scienceDue()[0]?.originId !== 'lever-07' || scienceWeak()[0]?.originId !== 'lever-08') {
                    throw Error('Missing lever recheck or weakness');
                }
                if (scienceDaily().slice(0,2).map(q => q.id).join(',') !== 'lever-07,lever-08') {
                    throw Error('Lever daily does not prioritize rechecks and weaknesses');
                }
                YuikaParent.storage.setItem(KEY, JSON.stringify(state));
                return YuikaDesign.summary(target);
            } finally {
                state = original;
                if (saved === null) YuikaParent.storage.removeItem(KEY);
                else YuikaParent.storage.setItem(KEY, saved);
            }
        }""", PAGE + '?unit=' + UNIT_NAME)
        assert (summary['dueCount'], summary['weakCount'], summary['normalCount']) == (1, 1, 3), summary
        page.locator('#start').click()
        assert page.evaluate("""() => {
            const qs = session.questions;
            return qs[0].step === 0 && qs.every((q,i)=>q.unitId==='rika-lever' && (i===0 || qs[i-1].step<=q.step));
        }""")
        diagram = page.locator('main svg').first
        expect(diagram).to_be_visible()
        assert diagram.bounding_box()['width'] >= 480
        expect(page.locator('#end')).to_contain_text('今日はここまで')
        page.locator('#end').click()
        assert page.evaluate('state.events.length') == 0
        page.locator('#daily-five').click()
        assert page.evaluate("session.mode==='daily' && session.questions[0].step===0")
        page.locator('#end').click()

        # Across sessions, reach all ordinary stages and rotate older answered questions.
        page.evaluate("""() => {
            const original = state;
            state=emptyState();
            const seen = new Set();
            const perBatch = [];
            try {
                for(let i=0;i<7;i++){
                    start('unit','てこのつり合い');
                    const batch=session.questions;
                    perBatch.push(batch.map(q=>q.id));
                    if(batch[0].step!==0||batch.some((q,j)=>j&&q.step<batch[j-1].step)){
                        throw Error('Stage order failed: '+i);
                    }
                    for(const q of batch){
                        seen.add(q.id);
                        const at=new Date(Date.parse('2026-11-22T03:00:00.000Z')+i*60000).toISOString();
                        state.events.push(validateEvent({id:uid(),sessionId:'synthetic-batch-'+i,questionId:q.id,datasetVersion:VERSION,
                            unit:q.unit,type:q.type,question:q.prompt,response:q.answer,inputRaw:String(q.answer),
                            expected:q.answer,correct:true,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),
                            hintUsed:false,mode:'unit',explanation:q.explanation}));
                    }
                }
                if(seen.size!==26||!perBatch[6].includes('lever-02'))throw Error(JSON.stringify(perBatch));
            }finally{
                state=original;
                session=null;
                view='home';
                render();
            }
        }""")

        # One lower-step insertion, followed by the scheduled queue.
        q = next(q for q in lever if q['step'] == 1 and any(
            low['step'] == 0 and low['conceptId'] == q['conceptId'] for low in lever
        ))
        successor = next(o for o in lever if o['step'] == 1 and o['id'] != q['id'])
        prepare(page, q['id'], successor['id'])
        page.evaluate("session.mode='daily';session.leverPractice=true;render()")
        expect(page.locator('#quiz-count')).to_contain_text('1 / 2問')
        wrong = wrong_option(q)
        e = answer(page, q, wrong)
        assert page.evaluate('session.questions.length') == 3
        expect(page.locator('#quiz-count')).to_contain_text('1 / 3問')
        assert not e['correct'] and e['response'] == wrong
        assert e['answerTag'] == q['optionTags'][wrong]
        page.locator('#next').click()
        fallback_id = page.evaluate('session.questions[session.index].id')
        fallback = by_id[fallback_id]
        assert fallback['step'] == q['step'] - 1 and fallback['conceptId'] == q['conceptId']
        expect(page.locator('#quiz-count')).to_contain_text('2 / 3問')
        answer(page, fallback)
        page.locator('#next').click()
        assert page.evaluate('session.questions[session.index].id') == successor['id']
        expect(page.locator('#quiz-count')).to_contain_text('3 / 3問')
        answer(page, successor)
        page.locator('#next').click()
        expect(page.locator('.result strong')).to_contain_text('2 / 3問 正解')
        expect(page.locator('main')).to_contain_text('わかったこと')
        expect(page.locator('main')).to_contain_text(fallback['steps'][-1])
        page.locator('#parent').click()
        fact = page.locator('#history details').filter(has_text='問題 ' + q['id'] + ' ／').first
        expect(fact).to_contain_text(wrong)
        expect(fact).to_contain_text('選んだ選択肢のタグ：' + e['answerTag'])

        # An incorrect remedial answer does not recursively add more questions.
        q = by_id['lever-15']
        successor = by_id['lever-17']
        prepare(page, q['id'], successor['id'])
        assert not answer(page, q, q['answer'] + 1)['correct']
        page.locator('#next').click()
        fallback = by_id[page.evaluate('session.questions[session.index].id')]
        assert fallback['step'] == 1 and fallback['conceptId'] == q['conceptId']
        assert not answer(page, fallback, wrong_option(fallback))['correct']
        page.locator('#next').click()
        assert page.evaluate('session.questions[session.index].id') == successor['id']

        # One aided success and two repeats of the same unaided question cannot unlock.
        first, second = [q for q in lever if q['step'] == 3][:2]
        for q, hinted in [(first, True), (first, False), (first, False), (second, True)]:
            prepare(page, q['id'])
            e = answer(page, q, hint=hinted)
            assert e['correct'] and e['hintUsed'] is hinted
            page.evaluate("view='home';home()")
            locked(page)
        prepare(page, second['id'])
        assert answer(page, second)['correct']
        page.reload()
        expect(page.locator('#lever-challenge')).to_be_enabled()
        assert page.evaluate('scienceDaily().length===5&&scienceDaily().some(q=>q.step===4)')
        expect(page.locator('#daily-five')).to_have_text('今日の復習をはじめる（今回は5問）')
        page.locator('#daily-five').click()
        assert page.evaluate("session.mode==='daily'&&session.questions.length===5&&session.questions.some(q=>q.step===4)")
        page.locator('#end').click()
        assert page.evaluate("candidates('unit','てこのつり合い').every(q=>q.step<4)")
        page.locator('#lever-challenge').click()
        assert page.evaluate('session.questions.length===2&&session.questions.every(q=>q.step===4)')

        # Unit decorations, queue payload, history, and exact-match numeric tags.
        q = next(q for q in lever if q['type'] == 'number' and q['answerUnit'] == 'cm' and q.get('numericTags'))
        typical = next(iter(q['numericTags']))
        prepare(page, q['id'])
        assert 'cm' in page.locator('#numeric').evaluate("el => el.parentElement.textContent")
        e = answer(page, q, typical)
        assert e['answerUnit'] == 'cm' and e['answerTag'] == q['numericTags'][typical]
        prepare(page, q['id'])
        e = answer(page, q, 99999)
        assert not e['correct'] and not e.get('answerTag')

        page.evaluate('cfg=>YuikaParent.storage.setItem("yuika-mail-config-v1",JSON.stringify(cfg))', CONFIG)
        prepare(page, q['id'])
        assert answer(page, q)['correct']
        page.locator('#end').click()
        page.wait_for_function("""() =>
            JSON.parse(YuikaParent.storage.getItem('yuika-mail-job-v1:science:'+session.id)).status==='accepted'
        """)
        assert len(posts) == 1, posts
        report = posts[0]
        assert report['unit'] == UNIT_NAME, report
        assert report['answers'][0]['response'] == report['answers'][0]['expected'] == f"{q['answer']}cm", report
        page.locator('#parent').click()
        row = page.locator('#history details').filter(has_text=q['prompt']).first
        expect(row).to_contain_text(f"{q['answer']}cm")
        assert page.evaluate("""() => {
            const q=QUESTIONS.find(q=>q.id.startsWith('ys2-')&&q.type==='number');
            const at='2026-11-21T03:00:00.000Z';
            const old=validateEvent({id:uid(),sessionId:'synthetic-old-unit',questionId:q.id,
                datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response:q.answer,
                inputRaw:String(q.answer),expected:q.answer,correct:true,answeredAt:at,
                timezoneOffset:0,localDay:at.slice(0,10),hintUsed:false,mode:'unit',explanation:q.explanation});
            return old.correct;
        }""")

        # Existing normal data and notification jobs stay outside parent mode.
        before = page.evaluate('Object.fromEntries(Object.entries(localStorage))')
        calls_before = list(mock_calls)
        page.goto(url + '&parent-check=1')
        expect(page.locator('#parent-check-banner')).to_be_visible()
        assert page.evaluate('YuikaParent.active&&state.events.length===0')
        locked(page)
        page.evaluate('cfg=>YuikaParent.storage.setItem("yuika-mail-config-v1",JSON.stringify(cfg))', CONFIG)
        page.locator('#start').click()
        q = by_id[page.evaluate('session.questions[session.index].id')]
        assert answer(page, q)['correct']
        page.locator('#end').click()
        assert page.evaluate('Object.keys(sessionStorage).some(k=>k.includes(KEY))')
        assert not page.evaluate("Object.keys(sessionStorage).some(k=>k.includes('yuika-mail-job-v1:science:'))")
        assert any('通知を送信しません' in log for log in logs)
        page.reload()
        assert page.evaluate('YuikaParent.active&&state.events.length===1')
        assert page.evaluate('Object.fromEntries(Object.entries(localStorage))') == before
        assert mock_calls == calls_before and not errors, (mock_calls, errors)
        ctx.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()

print('lever: 28 calculations/revisions, recheck/daily, staged quiz and single fallback, challenge gate, tags/units/reports, parent isolation PASS')
