"""Synthetic trial grading/state regression; current answers never persist."""
import copy
import json
import os
import runpy
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import expect, sync_playwright

ROOT=Path(__file__).resolve().parents[1]
TEXT=json.loads((ROOT/'docs/product/fixtures/synthetic-content.json').read_text())
IMAGE=json.loads((ROOT/'docs/product/fixtures/synthetic-image-content.json').read_text())
Handler=runpy.run_path(str(ROOT/'scripts/cloud/serve.py'))['PreviewHandler']
class Quiet(Handler):
    def log_message(self,*args): pass

with ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server:
    Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/content-review.html'
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
            context=browser.new_context(viewport={'width':768,'height':1024})
            bad=[]
            context.route('**/*',lambda r:r.continue_() if r.request.url==url and r.request.method=='GET' else (bad.append(r.request.url),r.abort()))
            context.add_init_script("""(()=>{window.writes=[];for(const n of ['setItem','removeItem','clear'])Storage.prototype[n]=()=>{writes.push(n);throw Error('write');};})()""")
            p=context.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
            p.goto(url)
            def upload(value):
                p.locator('#import').set_input_files({'name':'synthetic.json','mimeType':'application/json','buffer':json.dumps(value).encode()})
                expect(p.locator('#import')).to_have_value('')
            def confirm_all():
                for i in range(p.locator('[id^="confirm-"]').count()):p.locator(f'#confirm-{i}').click()
            def state():return p.evaluate('({proposal,unsaved})')
            def start():p.locator('#trial-start').click();expect(p.locator('#trial-title')).to_be_focused()
            def end():p.locator('#trial-exit').click();assert p.evaluate('trial') is None
            # Literal oracle: no inference from the comparator under test.
            q=copy.deepcopy(TEXT['questions'][0]);q2=copy.deepcopy(q);q2.update(answer='ABC',aliases=['A B'],readings=[])
            q3=copy.deepcopy(q);q3.update(answer='ガラス',aliases=[],readings=[])
            qc=copy.deepcopy(q);qc.update(type='choice',answer='東',options=['東','西'],aliases=[],readings=[])
            cases=[(q,'氷',True),(q,'　こおり\t',True),(q,'コオリ',False),(q,'こ おり',False),(q,'氷。',False),
                   (q2,'ＡＢＣ',True),(q2,'abc',False),(q2,'A　B',True),(q2,'A  B',False),(q3,'ｶﾞﾗｽ',True),
                   (q,'',None),(q,' \t　',None),(q,'x'*200,False),(q,'x'*201,None),(q,'㍍'*51,None),
                   (qc,0,True),(qc,1,False),(qc,None,None),(qc,2,None),(qc,'東',None),(qc,0.5,None),(q,42,None)]
            longq=copy.deepcopy(q);longq.update(answer='😀'*100,readings=[])
            cases += [(longq,'😀'*100,True),(longq,'😀'*101,None),(longq,' '+'😀'*100,None)]
            for question,value,expected in cases:
                r=p.evaluate('([q,a])=>gradeTrialValue(q,a)',[question,value])
                assert ('error' in r) if expected is None else r=={'match':expected},(value,r,expected)
            # Two-question real UI session; all state remains in proposal unchanged.
            value=copy.deepcopy(TEXT);value['questions'].append(qc);value['questions'][1]['id']='draft-synthetic-choice-002'
            upload(value);expect(p.locator('#trial-start')).to_be_disabled()
            p.evaluate('startTrial()');assert p.evaluate('trial') is None
            p.locator('#confirm-0').click();expect(p.locator('#trial-start')).to_be_disabled();p.locator('#confirm-1').click()
            saved=state();start()
            expect(p.locator('#editor')).to_be_hidden();assert p.locator('#editor').evaluate('e=>e.inert')
            assert p.locator('#trial-solutions').count()==0
            expect(p.locator('#trial-next')).to_be_disabled()
            p.evaluate('window.oldInput=document.getElementById("trial-answer");window.oldHandler=oldInput.oninput;window.oldToken=trialToken()')
            p.locator('#trial-grade').click();assert p.locator('#trial-solutions').count()==0
            p.locator('#trial-answer').fill('㍍'*51);p.locator('#trial-grade').click();expect(p.locator('#trial-error')).to_contain_text('200文字')
            expect(p.locator('#trial-answer')).to_have_value('㍍'*51)
            p.locator('#trial-hint-button').click();expect(p.locator('#trial-hint')).to_be_visible();assert p.locator('#trial-solutions').count()==0
            # Backdoor invocations of editor operations must also be blocked.
            p.evaluate("changed(()=>proposal.unit.title='should not change');acceptProposal(SAMPLES[1]);exportProposal(false);document.getElementById('cancel').onclick();document.getElementById('confirm-0').onclick()")
            assert state()==saved
            p.locator('#trial-answer').fill('こおり');p.locator('#trial-grade').click()
            expect(p.locator('#trial-result')).to_have_text('登録した答えに一致しました');expect(p.locator('#trial-answer')).to_be_disabled()
            p.evaluate('gradeTrial(oldToken);trialInput(oldToken,"stale");trialHint(oldToken)')
            assert p.evaluate('trial.answer')=='こおり'
            p.locator('#trial-next').click();expect(p.locator('#trial-progress')).to_have_text('2 / 2問')
            assert p.evaluate('oldInput.value')==''
            p.evaluate('oldHandler();gradeTrial(oldToken);nextTrial(oldToken)')
            assert p.evaluate('trial.answer') is None
            assert p.locator('#trial-choice-0').is_checked() is False
            p.locator('#trial-grade').click();assert p.locator('#trial-solutions').count()==0
            p.locator('#trial-choice-1').check();p.locator('#trial-grade').click();expect(p.locator('#trial-result')).to_have_text('登録した答えとは一致しません')
            assert p.locator('#trial-next').count()==0;assert state()==saved;end();assert state()==saved
            assert p.locator('#trial-panel').inner_html()=='';expect(p.locator('#trial-start')).to_be_focused()
            p.evaluate('oldHandler();gradeTrial(oldToken)');assert p.evaluate('trial') is None
            start();assert p.evaluate('trial.answer') is None;end()
            # Editing invalidates confirmations. Imported confirmed flags are not accepted.
            p.locator('#q-0-prompt').fill('合成の点検用問題');expect(p.locator('#trial-start')).to_be_disabled()
            confirm_all()
            with p.expect_download() as download:p.locator('#export-confirmed').click()
            exported=json.loads(Path(download.value.path()).read_text());assert set(exported)==set(TEXT)
            assert not state()['unsaved'];start();p.locator('#trial-answer').fill('synthetic transient')
            assert p.evaluate("(()=>{const e=new Event('beforeunload',{cancelable:true});dispatchEvent(e);return e.defaultPrevented})()")
            assert p.evaluate('trial.answer')=='synthetic transient'
            p.evaluate("dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}))")
            assert p.evaluate('trial') is None;assert not state()['unsaved']
            start();p.locator('#trial-answer').fill('synthetic transient');p.evaluate("dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))");assert p.evaluate('trial') is None
            start();p.evaluate('proposal.revision++');p.locator('#trial-grade').click();assert p.evaluate('trial') is None
            upload(exported);expect(p.locator('#trial-start')).to_be_disabled();confirm_all()
            start();p.evaluate('render()');assert p.evaluate('trial') is None
            start();p.evaluate("document.getElementById('trial-panel').replaceChildren()");p.wait_for_function('trial===null')
            start();p.evaluate("document.getElementById('trial-prompt').replaceWith(document.createElement('p'))");p.wait_for_function('trial===null')
            upload(IMAGE);expect(p.locator('#trial-start')).to_be_disabled();p.evaluate('startTrial()');assert p.evaluate('trial') is None
            # Start-only normalized candidate length checks do not alter schema/export policy.
            huge=copy.deepcopy(TEXT);huge['questions'][0]['answer']='㍍'*51
            upload(huge);confirm_all();expect(p.locator('#trial-start')).to_be_disabled();p.evaluate('startTrial()');assert p.evaluate('trial') is None
            aliases=copy.deepcopy(TEXT);aliases['questions'][0]['aliases']=['㍍'*51]
            upload(aliases);confirm_all();p.evaluate('startTrial()');assert p.evaluate('trial') is None
            expect(p.locator('#q-0-aliases')).to_be_focused()
            assert p.evaluate('writes')==[] and bad==[] and errors==[],(bad,errors)
            browser.close()
    finally:server.shutdown()
print('PASS content trial: G01-G13/UTF16 boundaries, all-confirm gate, text/choice UI, stale operations, isolation, exit/page lifecycle/DOM reconstruction')
