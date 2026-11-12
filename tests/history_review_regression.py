"""Review regressions: retired IDs, historical science text, numeric/unit input."""
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
  context = browser.new_context(viewport={'width': 768, 'height': 1024})
  context.add_init_script(path=str(ROOT/'tests/seed_random.js'))
  page = context.new_page()
  page.route('https://**/*', lambda r: r.abort())
  page.goto(f'http://127.0.0.1:{server.server_port}/yuika-review-v2.html')
  page.evaluate('''() => {
   const assert=(x,m)=>{if(!x)throw Error(m);};
   const q=QUESTIONS.find(q=>q.type==='number');
   const make=(i,version)=>{
    const at=`2026-11-0${i+1}T00:00:00.000Z`;
    return validateEvent({...(version?{questionVersion:1}:{}),id:'synthetic-review-'+i,
     sessionId:'synthetic-history-review',questionId:q.id,datasetVersion:VERSION,
     unit:q.unit,type:q.type,question:q.prompt,response:q.answer+1,inputRaw:String(q.answer+1),
     expected:q.answer,correct:false,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),
     hintUsed:false,mode:'normal',explanation:q.explanation});
   };
   state.events=[make(0,false),make(1,true)];
   const bytes=JSON.stringify(state);
   localStorage.setItem(KEY,bytes);
   for(let i=0;i<3;i++){load();assert(persist(),'repeat persist');assert(state.events.length===2,'repeat migration duplicates');}
   assert(!Object.hasOwn(state.events[0],'questionVersion'),'legacy version inserted');
   // Correcting current text must never replace the recorded historical text.
   const prompt=q.prompt,explanation=q.explanation;
   q.prompt='合成の新しい問題文';q.explanation='合成の新しい説明';
   analysis();
   let repeated=[...document.querySelectorAll('section')].find(e=>e.querySelector('h2')?.textContent==='繰り返し確認したい問題');
   assert(repeated.textContent.includes(prompt)&&repeated.textContent.includes(explanation),'historical text missing');
   assert(!repeated.textContent.includes(q.prompt)&&!repeated.textContent.includes(q.explanation),'current text replaces history');
   // Retiring the question leaves history readable/exportable but never reselects it.
   byId.delete(q.id);QUESTIONS.splice(QUESTIONS.indexOf(q),1);
   assert(validateState(state).events.length===2,'retired history rejected');
   home();
   assert(candidates('unseen').length===QUESTIONS.length,'retired IDs reduce remaining questions');
   assert(main.querySelector('.stats .stat strong').textContent==='0／'+QUESTIONS.length,'retired IDs counted in completed display');
   analysis();
   assert(main.querySelectorAll('.stats .stat strong')[1].textContent.trim().startsWith('0'),'retired IDs counted as current questions');
   assert(document.getElementById('history').textContent.includes('問題の版 記録なし'),'legacy version label');
   assert(document.getElementById('history').textContent.includes('問題の版 1'),'versioned label');
   window.download=(_name,text)=>{window.syntheticReport=text;};
   exportReport();
   assert(syntheticReport.includes(prompt)&&syntheticReport.includes(explanation),'retired export missing');
   assert(syntheticReport.includes('問題の版 記録なし')&&syntheticReport.includes('問題の版 1'),'export version labels');
   assert(!scienceDaily().some(x=>x.id===q.id),'retired ID reselected');
   // Valid histories near the storage cap must remain idempotently mergeable.
   const template=state.events[0],large={...emptyState(),events:Array.from({length:10001},(_,i)=>({...template,id:'synthetic-large-'+i}))};
   large.legacy=Array.from({length:51},(_,i)=>({raw:JSON.stringify({attempts:i,correct:[],wrong:[]}),capturedAt:'2026-11-01T00:00:00.000Z'}));
   let merged=large;
   for(let i=0;i<3;i++)merged=merge(merged,large);
   assert(merged.events.length===10001&&merged.legacy.length===51,'large repeated merge');
   const cap={...emptyState(),events:Array.from({length:20000},(_,i)=>({...template,id:'synthetic-cap-'+i}))};
   assert(merge(cap,cap).events.length===20000,'full state cannot be saved');
   const overflow={...emptyState(),events:[{...template,id:'synthetic-overflow'}]};
   let rejected=false;try{merge(cap,overflow);}catch{rejected=true;}
   assert(rejected,'unique event cap exceeded');
   rejected=false;try{validateState({...cap,events:[...cap.events,...overflow.events]});}catch{rejected=true;}
   assert(rejected,'oversize input accepted');
   const conflict=structuredClone(large);conflict.events[0].sessionId='synthetic-conflicting-session';
   rejected=false;try{merge(large,conflict);}catch{rejected=true;}
   assert(rejected,'large collision ignored');

   for(const question of QUESTIONS){assert(grade(question,question.answer),'registered answer rejected');}
   for(const [raw,expected] of [['１．８',1.8],[' .5 ',.5],['０',0],['1.8g',null],['1.8 g',null],['−1',null],['1,8',null],['',null]]){
    assert(numeric(raw)===expected,'numeric/unit parsing: '+raw);
   }
  }''')
  context.close()
  browser.close()
finally:
 server.shutdown()
print('history_review_regression: retired IDs, historical text/version, repeated load/save, numeric units PASS')
