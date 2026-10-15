import test from 'node:test';
import assert from 'node:assert/strict';
import worker,{validateReport,deliver,mailText,ReportDelivery} from '../worker.mjs';
const env={DEVICE_TOKEN:'test-only-device-key-12345678901234567890',RESEND_API_KEY:'test-only-api-key',REPORT_TO:'parent@example.test',REPORT_FROM:'Teacher <reports@example.test>',ALLOWED_ORIGIN:'https://example.test'};
const report=()=>({version:1,id:'challenge:12345678',app:'social',subject:'社会',unit:'平安時代',mode:'もう一度',completedAt:'2026-10-15T01:00:00.000Z',total:1,correct:0,detail:'full',answers:[{question:'望月の歌の作者は？',response:'藤原頼通',expected:'藤原道長',explanation:'歌は道長。',correct:false,hint:true,mode:'もう一度'}]});
function storage(){const m=new Map();return {m,async get(k){return structuredClone(m.get(k));},async put(k,v){m.set(k,structuredClone(v));}};}
const accept=async()=>Response.json({id:'provider-test-1'});
test('strict schema, no inferred correct answers, bounded content',()=>{
 assert.equal(validateReport(report()).answers[0].response,'藤原頼通');
 for(const patch of [{id:undefined},{total:0},{correct:1},{completedAt:'2026-99-01T00:00:00.000Z'},{app:'spam'},{answers:[{...report().answers[0],hint:'yes'}]}])assert.throws(()=>validateReport({...report(),...patch}));
 const text=mailText(report());assert.match(text,/0 \/ 1問/);assert.match(text,/藤原頼通/);assert.match(text,/ヒントを見た問題：1問/);assert.doesNotMatch(text,/能力|集中力/);
});
test('one provider request, fixed destination, no secret leakage, same ID stays deduplicated beyond 24h',async()=>{
 const s=storage(),p=validateReport(report());let calls=0;
 const send=async(url,init)=>{calls++;assert.equal(url,'https://api.resend.com/emails');const body=JSON.parse(init.body);assert.deepEqual(body.to,['parent@example.test']);assert.equal(body.from,env.REPORT_FROM);assert.ok(init.headers['Idempotency-Key']);return accept();};
 assert.equal((await deliver(p,env,s,send,100000)).status,200);
 assert.equal((await deliver(p,env,s,send,100000+3*86400000)).status,200);assert.equal(calls,1);
 assert.equal((await deliver({...p,unit:'changed'},env,s,send,100000)).status,409);
 assert.doesNotMatch(JSON.stringify([...s.m.values()]),/藤原|test-only-api-key/);
});
test('uncertain acceptance retries with SAME provider key; stops after 23h to prevent duplicates',async()=>{
 const s=storage(),p=validateReport(report()),keys=[];
 const send=async(url,init)=>{keys.push(init.headers['Idempotency-Key']);if(keys.length===1)throw Error('connection lost after acceptance');return accept();};
 assert.equal((await deliver(p,env,s,send,100000)).status,502);
 assert.equal((await deliver(p,env,s,send,110000)).status,429);
 assert.equal((await deliver(p,env,s,send,140000)).status,200);assert.equal(keys[0],keys[1]);
 const s2=storage();let calls=0;const failing=async()=>{calls++;throw Error('network');};
 await deliver(p,env,s2,failing,100000);
 assert.equal((await (await deliver(p,env,s2,failing,100000+23*3600000)).json()).error,'needs_review');assert.equal(calls,1);
});
test('provider rejection and invalid success response are never called sent',async()=>{
 for(const send of [async()=>Response.json({error:'bad'}, {status:403}),async()=>Response.json({ok:true})]){
  const s=storage();assert.equal((await deliver(validateReport(report()),env,s,send,100000)).status,502);assert.equal((await s.get('report:'+report().id)).status,'pending');
 }
});
test('destination cannot be supplied by browser; origin, authentication, config, size are enforced',async()=>{
 let called=0;const e={...env,REPORTS:{idFromName:x=>x,get:()=>({fetch:async req=>{called++;const p=await req.json();assert.equal(p.to,undefined);return Response.json({accepted:true});}})}};
 const req=(path='/reports',body={...report(),to:'attacker@example.test'},headers={})=>new Request('https://worker.example'+path,{method:path==='/health'?'GET':'POST',headers:{Origin:env.ALLOWED_ORIGIN,Authorization:'Bearer '+env.DEVICE_TOKEN,...headers},...(path==='/health'?{}:{body:JSON.stringify(body)})});
 assert.equal((await worker.fetch(req('/reports',report(),{Origin:'https://other.test'}),e)).status,403);
 assert.equal((await worker.fetch(req('/reports',report(),{Authorization:'Bearer bad'}),e)).status,401);
 assert.equal((await worker.fetch(req('/health'),{...e,RESEND_API_KEY:''})).status,503);
 assert.equal((await worker.fetch(req('/reports',{...report(),extra:'x'.repeat(100001)}),e)).status,413);
 assert.equal((await worker.fetch(req(),e)).status,200);assert.equal(called,1);
 const health=await worker.fetch(req('/health'),e);assert.equal(health.headers.get('Access-Control-Allow-Origin'),env.ALLOWED_ORIGIN);assert.equal((await health.json()).recipient,env.REPORT_TO);
});
test('concurrent delivery is serialized by Durable Object and rate limit bounds sends',async()=>{
 const s=storage();let chain=Promise.resolve(),calls=0;const ctx={storage:s,blockConcurrencyWhile(fn){const result=chain.then(fn);chain=result.catch(()=>{});return result;}};
 const oldFetch=globalThis.fetch;globalThis.fetch=async()=>{calls++;return accept();};
 try{const object=new ReportDelivery(ctx,env);await Promise.all([1,2].map(()=>object.fetch(new Request('https://internal/reports',{method:'POST',body:JSON.stringify(report())}))));assert.equal(calls,1);}finally{globalThis.fetch=oldFetch;}
 const hour=100;await s.put('rate',{hour,count:60});assert.equal((await deliver({...validateReport(report()),id:'new:challenge123'},env,s,accept,hour*3600000)).status,429);
});
