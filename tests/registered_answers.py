"""Exhaust every current canonical answer and registered social spelling."""
import os
import sys
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(PreviewHandler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
        for name in ('onin-review.html', 'kamakura-review.html', 'heian-review.html', 'yuika-review-v2.html'):
            context = browser.new_context(viewport={'width': 768, 'height': 1024})
            context.add_init_script(path=str(ROOT / 'tests/seed_random.js'))
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.route('https://**/*', lambda route: route.abort())
            page.goto(f'http://127.0.0.1:{server.server_port}/{name}')
            result = page.evaluate('''() => {
              const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
              const science=typeof byId!=='undefined';
              const variants=science?['normal']:typeof VARIANTS==='undefined'?['normal','kanji']:Object.keys(VARIANTS);
              let canonical=0,spellings=0;
              for(const q of QUESTIONS)for(const v of variants){
                if(!science&&!fits(q,v))continue;
                const response=q.type==='structure'
                  ?{steps:q.items.map((_,i)=>i),fills:q.blanks.map(b=>b.answer)}
                  :science?q.answer:expectedOf(q,v);
                assert(grade(q,response,v),q.id+' canonical '+v);canonical++;
                if(q.type!=='text')continue;
                const allowed=v==='yomi'?q.readings:[q.answer,...q.aliases,...(v==='kanji'?[]:q.readings)];
                for(const answer of allowed){
                  assert(grade(q,answer,v),q.id+' registered '+v+': '+answer);spellings++;
                }
              }
              return {canonical,spellings};
            }''')
            assert not errors, errors
            print(name, result, 'all registered answers passed')
            context.close()
        browser.close()
finally:
    server.shutdown()
print('registered_answers: all current questions, supported variants and registered spellings PASS')
