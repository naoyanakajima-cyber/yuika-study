"""Synthetic recommendation, persistence and iPad-width checks for both units."""
import json
import os
import subprocess
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = 'edad8065c1f2b726e61c5cf405f8d9ff6d807480'
NOW = datetime(2030, 1, 3, tzinfo=timezone.utc)
OTHER = {'yuika-science-v2': '{"syntheticKeep":true}',
         'yuika-social-540-24-v1': '{"syntheticKeep":true}'}


class Quiet(SimpleHTTPRequestHandler):
    posts = 0

    def log_message(self, *args):
        pass

    def do_POST(self):
        type(self).posts += 1
        self.send_error(405)


srv = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
Thread(target=srv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{srv.server_port}/'
SEED = """rows => {
 data={...empty(),events:rows.map((r,i)=>{
  const q=Q.get(r.id),v=r.variant||'normal',at=r.at||'2030-01-02T23:00:00.000Z';
  const correct=r.correct??false,hint=r.hint??false,offset=r.offset??0;
  const response=correct?expectedOf(q,v):q.type==='text'?'合成の誤答':q.options.find(o=>o!==q.answer);
  return validateEvent({id:'synthetic-'+String(i).padStart(5,'0'),sessionId:'synthetic-session',
   questionId:q.id,unitId:UNIT_ID,version:VERSION,unit:q.unit,course:q.course,
   question:promptOf(q,v),response,expected:expectedOf(q,v),explanation:q.explanation,
   correct,variant:v,mode:'normal',hint,at,offset,day:day(at,offset)});
 })};
 localStorage.setItem(KEY,JSON.stringify(data));go('home');return data;
}"""
PLAN = "recommendedPlan().map(x=>({id:x.q.id,reasons:x.reasons}))"


def row(qid, **values):
    return {'id': qid, **values}


def seed(p, rows):
    return p.evaluate(SEED, rows)


def plan(p):
    return p.evaluate(PLAN)


def answer(p):
    q = p.evaluate('run.qs[run.index]')
    if q['type'] == 'text':
        p.locator('#response').fill(q['answer'])
    else:
        p.locator('[data-choice]').filter(has_text=q['answer']).first.click()
    p.locator('#check').click()


try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
        for filename, prefix in [('onin-review.html', '54027'), ('kamakura-review.html', '54025')]:
            old_html = subprocess.check_output(['git', 'show', f'{BASE_REVISION}:{filename}'], cwd=ROOT, text=True)
            current = (ROOT / filename).read_text()
            # Protect data/schema and grading/validation without freezing unrelated UI/CSS.
            for start, end in [('const QUESTIONS=', 'const Q=new Map'),
                               ('const normalize=', 'const merge=')]:
                assert current[current.index(start):current.index(end)] == old_html[old_html.index(start):old_html.index(end)]
            context = browser.new_context(viewport={'width': 768, 'height': 1024})
            outgoing = []

            def route_request(route):
                request = route.request
                if request.method == 'GET' and request.url.startswith(BASE):
                    route.continue_()
                else:
                    outgoing.append((request.method, urlparse(request.url).hostname))
                    route.abort()

            context.route('**/*', route_request)
            p = context.new_page()
            p.clock.set_fixed_time(NOW)
            errors = []
            p.on('pageerror', lambda e: errors.append(str(e)))
            p.on('dialog', lambda d: d.accept())
            p.goto(BASE + filename)
            p.evaluate('o=>{for(const [k,v] of Object.entries(o))localStorage.setItem(k,v)}', OTHER)
            ids = [f'{prefix}-{i:02}' for i in range(1, 7)]
            q1, q2, q3, q4, q5, q6 = ids
            sample = [row(q1, at='2030-01-02T23:50:00.000Z'),
                      row(q2, correct=True, at='2030-01-01T00:00:00.000Z'),
                      row(q3, correct=True, hint=True),
                      row(q4, correct=True, hint=True, at='2030-01-01T12:00:00.000Z'),
                      row(q5, correct=True)]
            seeded = seed(p, sample)
            got = plan(p)
            assert [x['id'] for x in got] == [q1, q2, q3, q4], got
            assert got[0]['reasons'] == ['前の回答をもう一度確かめよう']
            assert got[1]['reasons'] == ['前の回答から24時間以上たったよ']
            assert got[2]['reasons'] == ['前はヒントを見て正解したよ']
            assert got[3]['reasons'] == ['前の回答から24時間以上たったよ', '前はヒントを見て正解したよ']
            expect(p.locator('#recommended-count')).to_have_text('候補 4問 · 今回は 4問')
            expect(p.get_by_text('おすすめ復習の回答は、記録では通常練習に含まれます。')).to_be_visible()

            # Full synthetic UI flow; viewing/starting doesn't mutate learning records.
            before = p.evaluate('localStorage.getItem(KEY)')
            p.locator('[data-count="5"]').click()
            p.locator('#recommended-start').click()
            assert p.evaluate('localStorage.getItem(KEY)') == before
            assert p.evaluate('run.qs.map(q=>q.id)') == [q1, q2, q3, q4]
            for index in range(4):
                expect(p.locator('#recommended-reasons')).to_be_visible()
                reason = p.locator('#recommended-reasons').inner_text()
                assert p.evaluate('document.documentElement.scrollWidth <= innerWidth')
                answer(p)
                assert p.locator('#recommended-reasons').inner_text() == reason
                expect(p.locator('#feedback')).to_contain_text('回答を保存しました')
                p.locator('#next').click()
            expect(p.locator('.result strong')).to_contain_text('4')
            stored = json.loads(p.evaluate('localStorage.getItem(KEY)'))
            assert len(stored['events']) == len(sample) + 4
            prior = {e['id']: e for e in seeded['events']}
            assert all(e == prior[e['id']] for e in stored['events'] if e['id'] in prior)
            added = [e for e in stored['events'] if e['id'] not in prior]
            assert len(added) == 4 and all(e['mode'] == 'normal' for e in added)
            assert all(set(e) == set(seeded['events'][0]) for e in added)
            for key, value in OTHER.items():
                assert p.evaluate('k=>localStorage.getItem(k)', key) == value
            p.reload()
            assert p.evaluate('data.events') == stored['events']
            assert plan(p) == []
            expect(p.locator('#recommended-start')).to_be_disabled()
            expect(p.get_by_text('この条件で今おすすめする復習はありません。通常練習や未回答の問題も選べます。')).to_be_visible()
            # Run the old page's actual validator on the newly saved events.
            old = context.new_page()
            old.route(BASE + 'baseline.html', lambda route: route.fulfill(content_type='text/html', body=old_html))
            old.goto(BASE + 'baseline.html')
            assert old.evaluate('v=>validate(v)', stored) == stored
            old.close()

            # Download and re-import through the existing public controls, without duplicates.
            p.locator('[data-view="records"]').click()
            with p.expect_download() as dl:
                p.locator('#export').click()
            exported = Path(dl.value.path()).read_text()
            assert json.loads(exported)['events'] == stored['events']
            p.locator('#import').set_input_files({'name': 'synthetic-records.json', 'mimeType': 'application/json', 'buffer': exported.encode()})
            expect(p.locator('#notice')).to_contain_text('新しい回答 0件')
            assert p.evaluate('data.events') == stored['events']

            # All available items: deterministic oldest / ID order and 5/10/15 caps.
            all_ids = p.evaluate('QUESTIONS.map(q=>q.id)')
            seed(p, [row(qid) for qid in reversed(all_ids)])
            assert [x['id'] for x in plan(p)] == sorted(all_ids)
            for count in (5, 10, 15):
                p.locator(f'[data-count="{count}"]').click()
                expect(p.locator('#recommended-count')).to_contain_text(f'今回は {count}問')
                p.locator('#recommended-start').click()
                selected = p.evaluate('run.qs.map(q=>q.id)')
                assert selected == sorted(all_ids)[:count] and len(set(selected)) == count
                p.locator('#end').click()
            seed(p, [row(q1, at='2030-01-02T23:00:00.000Z'), row(q2, at='2030-01-01T23:00:00.000Z')])
            assert [x['id'] for x in plan(p)] == [q2, q1]

            # Boundary, timezone/day boundary, future and multiple factual reasons.
            seed(p, [row(q1, correct=True, at='2030-01-02T00:00:00.001Z'),
                     row(q2, correct=True, at='2030-01-02T00:00:00.000Z'),
                     row(q3, correct=True, at='2030-01-02T23:59:00.000Z', offset=-540),
                     row(q4, hint=True, at='2030-01-03T01:00:00.000Z'),
                     row(q5, correct=True, hint=True, at='2030-01-03T01:00:00.000Z'),
                     row(q6, hint=True, at='2030-01-01T00:00:00.000Z')])
            got = {x['id']: x['reasons'] for x in plan(p)}
            assert q1 not in got and q3 not in got
            assert got[q2] == ['前の回答から24時間以上たったよ']
            assert got[q4] == ['前の回答をもう一度確かめよう', '前の回答はヒントあり']
            assert got[q5] == ['前はヒントを見て正解したよ']
            assert got[q6] == ['前の回答をもう一度確かめよう', '前の回答から24時間以上たったよ', '前の回答はヒントあり']
            seed(p, [row(q1, at='2030-01-01T00:00:00.000Z'), row(q1, correct=True)])
            assert plan(p) == []

            # Course/unit/variant isolation, including separate normal/kanji/yomi histories.
            text_q = p.evaluate('QUESTIONS.find(canYomi)')
            qid = text_q['id']
            seed(p, [row(qid)])
            for variant in ('kanji', 'yomi'):
                p.locator('#variant').select_option(variant)
                assert plan(p) == []
            seed(p, [row(qid, variant='yomi')])
            assert [x['id'] for x in plan(p)] == [qid]
            p.locator('#variant').select_option('normal')
            assert plan(p) == []
            seed(p, [row(qid, variant='kanji')])
            p.locator('#variant').select_option('kanji')
            assert [x['id'] for x in plan(p)] == [qid]
            course = next(c for c in ('d1', 'd2', 'd3') if c != text_q['course'])
            p.locator('#course').select_option(course)
            assert plan(p) == []
            p.locator('#course').select_option('all')
            other_unit = p.evaluate('unit=>UNITS.find(u=>u!==unit)', text_q['unit'])
            p.locator('#unit').select_option(other_unit)
            assert plan(p) == []
            p.locator('#unit').select_option('all')
            p.locator('#variant').select_option('normal')

            # Existing analysis distinctions are unchanged (same-day != elapsed 24h).
            seed(p, [row(qid, at='2030-01-01T20:00:00.000Z'),
                     row(qid, correct=True, at='2030-01-01T20:10:00.000Z'),
                     row(qid, correct=True, at='2030-01-01T23:59:00.000Z'),
                     row(qid, correct=True, at='2030-01-02T00:00:00.000Z')])
            assert p.evaluate('(()=>{const a=analysis();return [a.first.length,a.immediate.length,a.same.length,a.later.length]})()') == [1, 1, 1, 1]

            # Reject invalid history as before; no lossy normalization or overwrite.
            malformed = p.evaluate('(()=>{const v=JSON.parse(localStorage.getItem(KEY));v.events[0].hint=null;return JSON.stringify(v)})()')
            p.evaluate('raw=>localStorage.setItem(KEY,raw)', malformed)
            p.reload()
            expect(p.locator('#recommended-start')).to_be_disabled()
            expect(p.get_by_text('記録を読み取れないため選べません。', exact=True)).to_be_visible()
            p.evaluate('startRecommended()')
            assert p.evaluate('localStorage.getItem(KEY)') == malformed
            p.locator('[data-view="records"]').click()
            with p.expect_download() as dl:
                p.locator('#broken').click()
            assert Path(dl.value.path()).read_text() == malformed
            assert not errors, errors
            assert not [r for r in outgoing if r[0] == 'POST'], outgoing
            context.close()
            print(f'{filename}: R1-R7/R9 synthetic recommendation and compatibility checks passed')
        assert Quiet.posts == 0, Quiet.posts
        browser.close()
finally:
    srv.shutdown()
    srv.server_close()
print('recommended-review: all checks passed; actual POST arrivals 0')
