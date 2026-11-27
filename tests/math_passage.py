"""Independently solve the published prompts and exercise staged reports."""

import json
import os
import re
from collections import Counter
from fractions import Fraction
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from playwright.sync_api import expect, sync_playwright

from study_reports import CONFIG, CONFIG_KEY, MOCK, ROOT, verify_mail

PAGE = 'math-passage-review.html'
UNIT = '通過算・旅人算　進む長さをつかむ'


def solve(q):
    prompt = q['prompt']
    lengths = [int(n) for n in re.findall(r'(?:長さ|は)(\d+)m', prompt)]
    speeds = [Fraction(n) for n in re.findall(r'時速([\d.]+)km', prompt)]
    seconds = [int(n) for n in re.findall(r'秒速(\d+)m', prompt)]
    minutes = [int(n) for n in re.findall(r'分速(\d+)m', prompt)]
    step = q['step']
    if step == 0:
        if '完全に隠れて' in prompt:
            distance = lengths[1] - lengths[0]
        elif 'その窓' in prompt:
            distance = lengths[1]
        else:
            distance = sum(lengths)
        return f'{distance}m'
    if step == 1:
        relative = sum(seconds) if '反対方向' in prompt else max(seconds) - min(seconds)
        return f'秒速{relative}m'
    if step == 2:
        unit = '秒' if '秒速' in prompt else '分'
        divisor = 3600 if unit == '秒' else 60
        return f'{unit}速{speeds[0] * 1000 / divisor}m'
    if step == 3:
        if 'あと何m' in prompt:
            elapsed = int(re.search(r'(\d+)秒たった', prompt)[1])
            return sum(lengths) - (max(seconds) - min(seconds)) * elapsed
        if '景色' in prompt:
            return Fraction(lengths[-1], seconds[0])
        if '反対方向' in prompt:
            return Fraction(sum(lengths), sum(seconds))
        if '追い越します' in prompt:
            return Fraction(sum(lengths)) / ((max(speeds) - min(speeds)) * 1000 / 3600)
        return Fraction(sum(lengths), seconds[0])
    if '何秒で' in prompt:
        gap = int(re.search(r'(\d+)m前', prompt)[1])
        return gap / ((speeds[1] - speeds[0]) * 1000 / 3600)
    departures = [int(n) for n in re.findall(r'午前\d+時(\d+)分', prompt)]
    first = departures[0]
    second = departures[1] if len(departures) == 2 else first + int(re.search(r'(\d+)分後', prompt)[1])
    slow, fast = minutes or [v * 1000 / 60 for v in speeds]
    return second + Fraction(slow * (second - first), fast - slow)


def check_data(markup):
    questions = json.loads(re.search(r'<script id="questions" type="application/json">(.*?)</script>', markup, re.S)[1])
    assert Counter(q['step'] for q in questions) == {0: 8, 1: 3, 2: 4, 3: 5, 4: 4}
    assert len({q['id'] for q in questions}) == len(questions)
    for q in questions:
        assert solve(q) == q['answer'], q['id']
        assert q['hint'] and q['explanation'] and q['pitfall'] and len(q['steps']) >= 2
        if q['type'] == 'choice':
            assert set(q['options']) - {q['answer']} == set(q['optionTags'])
        else:
            assert q['wrongValues'] and str(q['answer']) not in q['wrongValues']
    return questions


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def check_browser(browser, base, questions):
    reports = []
    ctx = browser.new_context(viewport={'width': 768, 'height': 1024})
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))

    def intercept(route):
        if route.request.url.startswith(base):
            route.continue_()
        elif route.request.url == MOCK + '/reports' and route.request.method == 'POST':
            reports.append(route.request.post_data_json)
            route.fulfill(json={'accepted': True}, headers={'Access-Control-Allow-Origin': '*'})
        else:
            route.abort()

    ctx.route('**/*', intercept)
    page.goto(base + PAGE)
    page.evaluate('([k,v]) => localStorage.setItem(k, JSON.stringify(v))', [CONFIG_KEY, CONFIG])

    page.locator('[data-stage="0"]').click()
    for index, q in enumerate(questions[:8]):
        if index == 4:
            page.locator('#hint').click()
            value = '846m'
        else:
            value = q['answer']
        page.get_by_role('button', name=value, exact=True).click()
        page.locator('#check').click()
        if index == 4:
            expect(page.locator('#feedback')).to_contain_text('列車の長さを足した')
        page.locator('#next').click()
    expect(page.locator('#main')).to_contain_text('7 / 8問 正解')
    expect(page.locator('#yuika-mail-status')).to_contain_text('受け付けました')
    assert len(reports) == 1
    assert reports[0]['total'] == 8 and reports[0]['correct'] == 7
    assert reports[0]['answers'][4]['hint'] is True
    assert '途中終了' not in reports[0]['mode']
    page.locator('#return').click()
    page.locator('[data-stage="3"]').click()
    for value in ('２４', '29', '11'):
        page.locator('#numeric').fill(value)
        page.locator('#check').click()
        expect(page.locator('#feedback')).to_contain_text('できたね')
        page.locator('#next').click()
    page.locator('#numeric').fill('0.222')
    page.locator('#check').click()
    expect(page.locator('#feedback')).to_contain_text('長さが小数になったら見直そう')
    expect(page.locator('#feedback')).to_contain_text('kmの値をmに直さなかった')
    page.locator('#end').click()
    expect(page.locator('#main')).to_contain_text('途中終了')
    expect(page.locator('#yuika-mail-status')).to_contain_text('受け付けました')
    assert len(reports) == 2
    assert reports[1]['total'] == 4 and reports[1]['correct'] == 3
    assert '途中終了' in reports[1]['mode']

    page.goto(base + PAGE + '?parent-check=1')
    page.evaluate('() => { window.YuikaReports.enqueue = () => { throw Error("parent-check enqueue"); }; }')
    for count in (1, 3):
        page.locator('[data-stage="1"]').click()
        for q in questions[8:8 + count]:
            page.get_by_role('button', name=q['answer'], exact=True).click()
            page.locator('#check').click()
            if count == 3:
                page.locator('#next').click()
        if count == 1:
            page.locator('#end').click()
        expect(page.locator('#main')).to_contain_text('今回のふりかえり')
        page.locator('#return').click()
    assert len(reports) == 2 and not errors, errors
    assert all(r['subject'] == '算数' and r['unit'] == UNIT for r in reports)
    verify_mail(reports)
    ctx.close()


if __name__ == '__main__':
    assert f'externalPage:"{PAGE}"' in (ROOT / 'index.html').read_text()
    questions = check_data((ROOT / PAGE).read_text())
    with ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT))) as server:
        Thread(target=server.serve_forever, daemon=True).start()
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.getenv('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
            check_browser(browser, f'http://127.0.0.1:{server.server_port}/', questions)
            browser.close()
    print('Math passage: all 24 answers independently recomputed; staged and mock report checks passed')
