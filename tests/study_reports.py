"""Exercise challenge endings through browser controls and validate mail with stubbed delivery."""

import json
import os
import subprocess
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MOCK = 'https://study-report.example.workers.dev'
CONFIG = {'enabled': True, 'endpoint': MOCK, 'token': 'synthetic-study-key', 'recipient': 'parent@example.test'}
CONFIG_KEY = 'yuika-mail-config-v1'
JOBS = "() => Object.keys(localStorage).filter(k=>k.startsWith('yuika-mail-job-v1:')).map(k=>JSON.parse(localStorage[k]))"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def answer(page, science_engine):
    if science_engine:
        q = page.evaluate('session.questions[session.index]')
        if q['type'] == 'number':
            page.locator('#numeric').fill(str(q['answer']))
        elif q.get('diagram'):
            page.locator(f'[data-fin="{q["answer"]}"]').click()
        elif q['type'] == 'recall':
            page.locator('#recall-text').fill(q['answer'])
        else:
            page.locator(f'[data-choice="{q["options"].index(q["answer"])}"]').click()
    else:
        # Focus and social engines may shuffle their displayed choices.
        page.evaluate("""() => {
            const q=run.qs[run.index];
            const input=document.querySelector('#response');
            if(input)input.value=q.answer;
            else if(q.type==='choice')document.querySelectorAll('[data-choice]')[run.options.indexOf(q.answer)].click();
            else {
                q.items.forEach((_,i)=>document.querySelector('[data-step="'+i+'"]').click());
                document.querySelectorAll('[data-fill]').forEach((el,i)=>el.value=q.blanks[i].answer);
            }
        }""")
    page.locator('#check').click()
    expect(page.locator('#next')).to_be_visible()


def finish(page, science_engine, partial_run, before_end):
    answered = 0
    while True:
        answer(page, science_engine)
        answered += 1
        if partial_run:
            before_end()
            page.locator('#end').click()
            break
        last = page.evaluate('session.index + 1 === session.questions.length' if science_engine
                             else 'run.index + 1 === run.qs.length')
        if last:
            before_end()
        page.locator('#next').click()
        if last:
            break
    return answered


def verify_mail(reports):
    subprocess.run(['node', '--input-type=module', '-e', """
        import assert from 'node:assert/strict';
        import fs from 'node:fs';
        import {validateReport, deliver} from './notifications/worker.mjs';
        const cache=new Map();
        const storage={get:key=>cache.get(key),put:(key,value)=>cache.set(key,value)};
        for (const raw of JSON.parse(fs.readFileSync(0, 'utf8'))) {
            const report=validateReport(raw);
            let mails=0;
            const result=await deliver(report, {REPORT_FROM:'sender@example.test',
                REPORT_TO:'parent@example.test',RESEND_API_KEY:'fake-test-key'}, storage,
                async (_,init)=>{
                    mails++;
                    const mail=JSON.parse(init.body);
                    assert.equal(mail.subject,
                        `[ゆいか学習] ゆいか学習帳 ${report.subject} ${report.correct}/${report.total}問`);
                    assert.ok(mail.text.includes(`教科・単元：${report.subject} / ${report.unit}`));
                    return Response.json({id:'synthetic-delivery'});
                });
            assert.equal(mails,1);
            assert.equal((await result.json()).accepted,true);
        }
    """], input=json.dumps(reports), text=True, check=True, cwd=ROOT)


def main(base, browser):
    cdn = {}
    for path in ('react@18/umd/react.production.min.js', 'react-dom@18/umd/react-dom.production.min.js',
                 '@babel/standalone@7/babel.min.js'):
        url = 'https://unpkg.com/' + path
        cdn[url] = subprocess.check_output(['curl', '-fsSL', '--max-time', '30', url])

    reports = []
    cases = [
        ('heian-review.html', {}, '社会', '540-24 貴族の世の中'),
        ('onin-review.html', {}, '社会', '540-27 応仁の乱'),
        ('kamakura-review.html', {}, '社会', '540-25 鎌倉幕府の成立'),
        ('edo-review.html', {}, '社会', '江戸幕府の成立・幕藩体制・鎖国'),
        ('mock-focus-review.html', {'subject': 'math'}, '算数', '模試の弱点対策'),
        ('yuika-review-v2.html', {'unit': 'てこのつり合い'}, '理科', 'てこのつり合い'),
        ('yuika-review-v2.html', {'unit': 'メダカの飼育・ひれ・成長'}, '理科', 'メダカの飼育・ひれ・成長'),
    ]
    for name, query, subject, unit in cases:
        ctx = browser.new_context(viewport={'width': 768, 'height': 1024}, timezone_id='Asia/Tokyo')
        ctx.add_init_script(path=ROOT / 'tests/seed_random.js')
        daily_unit = name + ('?' + '&'.join(f'{k}={v}' for k, v in query.items()) if query else '')
        page = ctx.new_page()
        errors, posts = [], []
        page.on('pageerror', lambda err: errors.append(str(err)))
        accept_dialog = [True]
        page.on('dialog', lambda dialog: dialog.accept() if accept_dialog[0] else dialog.dismiss())

        def route(r):
            url = r.request.url
            if url == base + '__study-report-fixture__':
                r.fulfill(content_type='text/html', body='<!doctype html><title>Study report fixture</title>')
            elif url.startswith(base):
                r.continue_()
            elif url in cdn:
                r.fulfill(body=cdn[url], content_type='application/javascript')
            elif url == MOCK + '/reports' and r.request.method == 'POST':
                jobs = page.evaluate(JOBS)
                report = r.request.post_data_json
                pending = [job for job in jobs if job['id'] == report['id']]
                assert len(pending) == 1 and pending[0]['status'] == 'pending'
                assert pending[0]['report'] == report
                posts.append(report)
                r.fulfill(json={'accepted': True}, headers={'Access-Control-Allow-Origin': '*'})
            else:
                r.abort()

        page.route('**/*', route)
        page.goto(base + '__study-report-fixture__')
        page.evaluate("([key,config,lastUnit])=>{localStorage.setItem(key,JSON.stringify(config));localStorage.setItem('yuika-prototype-v1:last-daily-unit',lastUnit);}", [CONFIG_KEY, CONFIG, daily_unit])
        url = base + name + ('?' + urlencode(query) if query else '')
        science_engine = name in ('yuika-review-v2.html', 'edo-review.html')
        if name == 'onin-review.html':
            # A real narrow filter yields four questions, not an assumed five.
            page.goto(url)
            page.locator('#unit').select_option('応仁の乱')
            page.locator('#variant').select_option('kanji')
            expect(page.locator('#daily-five')).to_have_attribute('data-daily-count', '4')
        for partial_run in (False, True):
            before = len(posts)
            if partial_run:
                page.goto(url)
                page.locator('#start').click()
            elif query.get('unit', '').startswith('メダカ'):
                page.goto(url + '&daily=1')
            else:
                page.goto(base + 'index.html')
                page.get_by_role('button', name='今日の復習をはじめる').click()
                page.wait_for_url('**/' + name + '*daily=1')

            planned = page.evaluate('session.questions.length' if science_engine else 'run.qs.length')
            if not partial_run and name == 'onin-review.html':
                assert planned == 4

            def before_end():
                assert len(posts) == before
                assert len(page.evaluate(JOBS)) == before
                if partial_run:
                    saved = page.evaluate('JSON.stringify(localStorage)')
                    accept_dialog[0] = False
                    page.locator('[data-view="home"]').click()
                    accept_dialog[0] = True
                    expect(page.locator('#next')).to_be_visible()
                    assert page.evaluate('JSON.stringify(localStorage)') == saved
                    assert len(posts) == len(page.evaluate(JOBS)) == before

            total = finish(page, science_engine, partial_run, before_end)
            expect(page.locator('#yuika-mail-status')).to_contain_text('受け付けました')
            assert len(posts) == before + 1
            report = posts[-1]
            assert total == (1 if partial_run else planned)
            assert report['total'] == len(report['answers']) == report['correct'] == total, report
            assert report['unit'] == unit and report['subject'] == subject, report
            if not partial_run:
                expected_mode = '今日の復習・漢字・正式名確認' if name == 'onin-review.html' else '今日の復習'
                assert report['mode'] == expected_mode
                page.evaluate('result();result()')
            page.reload()
            assert len(page.evaluate(JOBS)) == before + 1
            assert len(posts) == before + 1

        # Ending without an answer must not create a job in any of the engines.
        page.goto(url)
        page.locator('#start').click()
        saved = page.evaluate('JSON.stringify(localStorage)')
        page.locator('#end').click()
        assert len(page.evaluate(JOBS)) == len(posts) == 2
        assert page.evaluate('JSON.stringify(localStorage)') == saved

        # Use the same connected device, and even seed a config inside the sandbox.
        normal_storage = page.evaluate('JSON.stringify(localStorage)')
        page.goto(url + ('&' if query else '?') + 'parent-check=1')
        page.evaluate('c=>YuikaParent.storage.setItem("yuika-mail-config-v1",JSON.stringify(c))', CONFIG)
        page.locator('#start').click()
        finish(page, science_engine, True, lambda: None)
        assert page.evaluate("Object.keys(sessionStorage).every(k=>!k.includes('yuika-mail-job-v1:'))")
        assert len(page.evaluate(JOBS)) == len(posts) == 2
        assert page.evaluate('JSON.stringify(localStorage)') == normal_storage
        page.locator('#parent-exit').click()
        expect(page.locator('#yuika-mail-status')).to_contain_text('接続済み')
        assert page.evaluate('k=>JSON.parse(localStorage.getItem(k))', CONFIG_KEY) == CONFIG

        if name == 'onin-review.html':
            page.goto(base + 'index.html')
            page.get_by_role('button', name='環境問題・公害', exact=False).click()
            page.get_by_role('button', name='復習クイズ', exact=False).click()
            page.get_by_role('button', name='わからない（正解を見る）').click()
            page.get_by_role('button', name='← 戻る', exact=True).click()
            expect(page.locator('#yuika-mail-status')).to_contain_text('受け付けました')
            assert len(posts) == 3 and posts[-1]['total'] == 1 and posts[-1]['correct'] == 0
            page.get_by_role('button', name='暗記カード', exact=False).click()
            page.get_by_role('button', name='条約・制度', exact=False).click()
            page.get_by_role('button', name='わからない').click()
            page.get_by_role('button', name='← 戻る', exact=True).click()
            expect(page.locator('#yuika-mail-status')).to_contain_text('受け付けました')
            assert len(posts) == 4 and posts[-1]['total'] == 1 and posts[-1]['correct'] == 0

            page.goto(url)
            page.locator('#start').click()
            page.locator('#end').click()
            assert len(page.evaluate(JOBS)) == len(posts) == 4
            page.evaluate('key=>localStorage.removeItem(key)', CONFIG_KEY)
            page.reload()
            expect(page.locator('#yuika-mail-status')).to_contain_text('未接続')

        assert not errors, errors
        reports.extend(posts)
        ctx.close()
        print(f'PASS {name} {query}: actual daily count, early end, cancelled navigation, unanswered end, dedup, parent isolation', flush=True)
    verify_mail(reports)
    print(f'PASS {len(reports)} captured reports accepted by Worker contract; subjects verified with mail stub')


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=ROOT))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            with pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')) as browser:
                main(f'http://127.0.0.1:{server.server_port}/', browser)
    finally:
        server.shutdown()
