"""Frozen old definitions -> synthetic histories -> current offline readers."""
import hashlib
import json
import os
import subprocess
import sys
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.cloud.serve import PreviewHandler, ROOT
from scripts.history.embed import APPS, ARCHIVE, editorial, questions
archive=json.loads(ARCHIVE.read_text())
# Frozen fingerprints are independent of the mutable current questions.
frozen=json.loads((ROOT/'tests/history_baseline_sha256.json').read_text())
for name, records in archive.items():
 for id, revisions in records.items():
  for i,r in enumerate(revisions):
   assert r['revision']==i+1 and r['reason'].strip()
   if i:
    assert r['kind']=='editorial'
    editorial(revisions[i-1]['question'],r['question'])
 for id, digest in frozen[name].items():
  assert hashlib.sha256(json.dumps(records[id][0],ensure_ascii=False,sort_keys=True).encode()).hexdigest()==digest
 for q in questions((ROOT/name).read_text()):
  assert records[q['id']][-1]['question']==q, (name,q['id'],'unregistered change')
# Regeneration must be deterministic (including the embedded archives).
before={name:(ROOT/name).read_bytes() for name in APPS}
subprocess.run([sys.executable,str(ROOT/'scripts/history/embed.py')],check=True)
assert all((ROOT/name).read_bytes()==value for name,value in before.items())
q={'id':'synthetic','answer':'a','prompt':'old','aliases':['old']}
editorial(q,{**q,'prompt':'corrected','aliases':['old','equivalent']})
for changed in ({**q,'answer':'b'},{**q,'aliases':[]}):
 try: editorial(q,changed)
 except AssertionError: pass
 else: raise AssertionError('semantic change/removal accepted')
server=ThreadingHTTPServer(('127.0.0.1',0),partial(PreviewHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'))
  for name in APPS:
   context=browser.new_context();page=context.new_page();errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.route('https://**/*',lambda r:r.abort())
   page.goto(f'http://127.0.0.1:{server.server_port}/{name}')
   total=page.evaluate('''() => {
    const assert=(x,m)=>{if(!x)throw Error(m);};
    const science=typeof byId!=='undefined';
    const original=[],variants=typeof VARIANTS==='undefined'?['normal','kanji']:Object.keys(VARIANTS);
    const mk=(q,v,correct,revision)=>{
     let response;
     if(q.type==='structure')response={steps:q.items.map((_,i)=>i),fills:q.blanks.map(b=>b.answer)};
     else response=correct?(science?q.answer:expectedOf(q,v)):q.type==='number'?q.answer+1:q.type==='choice'?q.options.find(x=>x!==q.answer):'合成の誤答';
     if(q.type==='structure'&&!correct)response.steps.reverse();
     const at='2026-10-01T15:00:00.000Z',base={id:crypto.randomUUID(),sessionId:'synthetic-history',questionId:q.id,unit:q.unit,response,correct,mode:'normal'};
     if(revision!==undefined)base.questionVersion=revision;
     return science?{...base,datasetVersion:VERSION,type:q.type,question:q.prompt,inputRaw:String(response),expected:q.answer,explanation:q.explanation,answeredAt:at,timezoneOffset:0,localDay:at.slice(0,10),hintUsed:false}:
      {...base,version:VERSION,...(typeof UNIT_ID==='undefined'?{}:{unitId:UNIT_ID}),course:q.course,question:promptOf(q,v),expected:expectedOf(q,v),explanation:q.explanation,variant:v,hint:false,reflection:'',at,offset:0,day:at.slice(0,10)};
    };
    for(const rs of Object.values(QUESTION_REVISIONS))for(const r of rs){
     const q=r.question;
     const qs=science?[q]:[q,{...q,id:q.id+'-review-v1',prompt:'復習：'+q.prompt}];
     for(const question of qs)for(const v of science?['normal']:variants){
      if(!science&&!fits(question,v))continue;
      for(const correct of [true,false])for(const version of [undefined,r.revision]){
       const raw=mk(question,v,correct,version),result=validateEvent(raw);
       for(const key of Object.keys(result))assert(JSON.stringify(result[key])===JSON.stringify(raw[key]),'history field changed: '+key);
       assert(Object.hasOwn(result,'questionVersion')===(version!==undefined),'legacy version rewritten');
       original.push(result);
      }
     }
    }
    const saved=science?{...emptyState(),events:original}:{...empty(),events:original};
    const checkState=science?validateState:validate;
    const a=checkState(saved),b=merge(a,a);assert(b.events.length===a.events.length,'dedup');
    const conflict=structuredClone(a);conflict.events[0].sessionId='conflicting-session';
    let rejected=false;try{merge(a,conflict);}catch{rejected=true;}assert(rejected,'duplicate collision');
    // Simulate an editorial revision without changing production teaching content.
    const current=QUESTIONS.find(q=>q.type===(science?'number':'text')),old=structuredClone(current);
    const legacy=validateEvent(mk(old,'normal',true));
    const priorWrong=validateEvent(mk(old,'normal',false));
    current.prompt+='（合成訂正）';current.explanation+='（合成訂正）';
    if(current.aliases)current.aliases.push('合成の誤答');
    const rs=QUESTION_REVISIONS[current.id],revision=rs.at(-1).revision+1;
    rs.push({revision,kind:'editorial',question:structuredClone(current)});
    assert(validateEvent(legacy).question===old.prompt,'old correction history');
    if(current.aliases){assert(grade(current,priorWrong.response,'normal'),'new equivalent spelling');assert(validateEvent(priorWrong).correct===false,'old wrong grade preserved after spelling addition');}
    const map=science?byId:Q;map.delete(old.id);
    assert(validateEvent(legacy).question===old.prompt,'retired ID history remains readable');map.set(current.id,current);
    const fresh=validateEvent(mk(current,'normal',true,revision));assert(fresh.questionVersion===revision,'new revision');
    const wrongVersion={...legacy,questionVersion:revision};rejected=false;try{validateEvent(wrongVersion);}catch{rejected=true;}assert(rejected,'wrong revision snapshot');
    const unknown={...legacy,questionVersion:999};rejected=false;try{validateEvent(unknown);}catch{rejected=true;}assert(rejected,'unknown revision');
    const tampered={...legacy,correct:!legacy.correct};rejected=false;try{validateEvent(tampered);}catch{rejected=true;}assert(rejected,'tampered grade');
    // Load must leave disk bytes alone; persist and JSON import preserve old fields.
    const store=science?{...emptyState(),events:[legacy,fresh]}:{...empty(),events:[legacy,fresh]};
    const bytes=JSON.stringify(store);localStorage.setItem(KEY,bytes);load();
    assert(localStorage.getItem(KEY)===bytes,'load rewrites bytes');
    assert(science?persist():save(),'persist after correction');
    assert(checkState(JSON.parse(localStorage.getItem(KEY))).events.length===2,'persisted old/new');
    window.syntheticImport=bytes;window.syntheticBefore=JSON.stringify(science?state.events:data.events);
    return original.length;
   }''')
   page.evaluate("async()=>{const f=new File([syntheticImport],'synthetic.json',{type:'application/json'});await importFile(f);}")
   assert page.evaluate("JSON.stringify(typeof state==='undefined'?data.events:state.events)===syntheticBefore")
   assert not errors,errors
   print(name, total, 'synthetic old/versioned histories passed')
   context.close()
  browser.close()
finally: server.shutdown()
print('history_compat: archive immutability, editorial policy, old grades, merge/load/save/import PASS')
