// Cloudflare Worker + Durable Object. Only the server holds the mail-service key.
const MAX_BYTES = 100_000;
const ID = /^[A-Za-z0-9:_-]{8,128}$/;
const reply = (body, status=200) => Response.json(body, {status});
function assert(ok, message) { if (!ok) throw new Error(message); }
function str(s, max) { return typeof s==='string' && s.length<=max; }
export function validateReport(p) {
  assert(p && p.version===1 && typeof p.id==='string' && ID.test(p.id) && ['social','science','legacy'].includes(p.app), 'invalid_report');
  assert(str(p.subject,50) && str(p.unit,200) && str(p.mode,100), 'invalid_labels');
  assert(typeof p.completedAt==='string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(p.completedAt) && Number.isFinite(Date.parse(p.completedAt)) && new Date(p.completedAt).toISOString()===p.completedAt, 'invalid_date');
  assert(Number.isSafeInteger(p.total) && p.total>0 && p.total<=300 && Number.isSafeInteger(p.correct) && p.correct>=0 && p.correct<=p.total, 'invalid_score');
  assert(Array.isArray(p.answers) && p.answers.length<=p.total && ['full','summary'].includes(p.detail), 'invalid_answers');
  const answers=p.answers.map(a=>{
    assert(a && str(a.question,1500) && str(a.response,3000) && str(a.expected,3000) && str(a.explanation,4000) && str(a.mode,100) && typeof a.correct==='boolean' && [null,true,false].includes(a.hint), 'invalid_answer');
    return {question:a.question,response:a.response,expected:a.expected,explanation:a.explanation,correct:a.correct,hint:a.hint,mode:a.mode};
  });
  if(p.detail==='full') assert(answers.length===p.total && answers.filter(a=>a.correct).length===p.correct, 'inconsistent_score');
  return {version:1,id:p.id,app:p.app,subject:p.subject,unit:p.unit,mode:p.mode,completedAt:p.completedAt,total:p.total,correct:p.correct,detail:p.detail,answers};
}
export function mailText(p) {
 const date=new Date(p.completedAt).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'});
 const hints=p.answers.filter(a=>a.hint===true).length;
 return ['ゆいかのチャレンジ結果',`日時：${date}（日本時間）`,`教科・単元：${p.subject} / ${p.unit}`,`練習：${p.mode}`,`正解：${p.correct} / ${p.total}問`,p.detail==='full'?`ヒントを見た問題：${hints}問`:'旧アプリの集計です。選択した誤答・ヒントの有無は記録されていません。', '',...p.answers.map((a,i)=>[`【${i+1}】${a.correct?'正解':'もう一度確認'} ${a.question}`,`回答：${a.response}`,`正解：${a.expected}`,`ヒント：${a.hint===null?'記録なし':a.hint?'あり':'なし'} / モード：${a.mode}`,a.explanation?`解説：${a.explanation}`:'',a.correct&&/復習|もう一度|日をあけて|ヒントなし/.test(a.mode)?'復習で正解できた問題です。':'',''].join('\n')),'このメールは今回のチャレンジの結果です。過去の記録初回や長期的な定着を断定するものではありません。自由記述そのものは自動採点・送信の対象外です。',`通知ID：${p.id}`].join('\n');
}
export async function hash(s) { return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))].map(x=>x.toString(16).padStart(2,'0')).join(''); }
async function tokenEqual(a,b) {
 if(typeof a!=='string'||typeof b!=='string')return false;
 const x=await hash(a),y=await hash(b);let diff=0;for(let i=0;i<x.length;i++)diff|=x.charCodeAt(i)^y.charCodeAt(i);return diff===0;
}
function ready(env) { return typeof env.DEVICE_TOKEN==='string' && env.DEVICE_TOKEN.length>=32 && !!env.RESEND_API_KEY && typeof env.REPORT_TO==='string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(env.REPORT_TO) && typeof env.REPORT_FROM==='string' && env.REPORT_FROM.includes('@'); }
export default {
 async fetch(request,env) {
  const origin=request.headers.get('Origin');
  if(origin!==env.ALLOWED_ORIGIN)return reply({error:'origin_denied'},403);
  const cors={'Access-Control-Allow-Origin':origin,'Vary':'Origin','Access-Control-Allow-Methods':'GET, POST, OPTIONS','Access-Control-Allow-Headers':'Authorization, Content-Type','Cache-Control':'no-store'};
  const wrap=r=>{const out=new Response(r.body,r);for(const [k,v] of Object.entries(cors))out.headers.set(k,v);return out;};
  if(request.method==='OPTIONS')return wrap(new Response(null,{status:204}));
  if(!ready(env))return wrap(reply({error:'not_configured'},503));
  if(!await tokenEqual(request.headers.get('Authorization'),`Bearer ${env.DEVICE_TOKEN}`))return wrap(reply({error:'unauthorized'},401));
  const path=new URL(request.url).pathname;
  if(path==='/health'&&request.method==='GET')return wrap(reply({ready:true,recipient:env.REPORT_TO}));
  if(path!=='/reports'||request.method!=='POST')return wrap(reply({error:'not_found'},404));
  // Bound the stream before allocating a large body, even without Content-Length.
  const reader=request.body?.getReader();if(!reader)return wrap(reply({error:'invalid_report'},400));
  const chunks=[];let length=0;
  while(true){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>MAX_BYTES){await reader.cancel();return wrap(reply({error:'too_large'},413));}chunks.push(value);}
  const bytes=new Uint8Array(length);let pos=0;for(const c of chunks){bytes.set(c,pos);pos+=c.length;}
  let report;try{report=validateReport(JSON.parse(new TextDecoder().decode(bytes)));}catch{return wrap(reply({error:'invalid_report'},400));}
  const stub=env.REPORTS.get(env.REPORTS.idFromName('family-reports'));
  const result=await stub.fetch(new Request('https://internal/reports',{method:'POST',body:JSON.stringify(report)}));
  return wrap(result);
 }
};
// Sent IDs are retained without answer content. Provider requests use a stable idempotency key.
// If acceptance is uncertain beyond the provider's 24-hour window, do NOT resend automatically.
export async function deliver(p,env,storage,send=fetch,now=Date.now()) {
 const key='report:'+p.id,digest=await hash(JSON.stringify(p)),old=await storage.get(key);
 if(old&&old.digest!==digest)return reply({error:'id_conflict'},409);
 if(old?.status==='sent')return reply({accepted:true,duplicate:true});
 if(old&&now-old.firstAttempt>=23*60*60*1000)return reply({error:'needs_review'},409);
 if(old?.lastAttempt&&now-old.lastAttempt<30_000)return reply({error:'retry_later'},429);
 const hour=Math.floor(now/3600000),bucket=await storage.get('rate')||{hour,count:0};
 if(bucket.hour!==hour){bucket.hour=hour;bucket.count=0;}
 if(bucket.count>=60)return reply({error:'rate_limited'},429);
 bucket.count++;await storage.put('rate',bucket);
 const record={digest,status:'pending',firstAttempt:old?.firstAttempt??now,lastAttempt:now};
 await storage.put(key,record); // Durable before contacting the provider.
 let response;
 try{response=await send('https://api.resend.com/emails',{method:'POST',signal:AbortSignal.timeout(12_000),headers:{Authorization:`Bearer ${env.RESEND_API_KEY}`,'Content-Type':'application/json','Idempotency-Key':'yuika-'+await hash(p.id)},body:JSON.stringify({from:env.REPORT_FROM,to:[env.REPORT_TO],subject:`[ゆいか学習] ${p.subject} ${p.correct}/${p.total}問`,text:mailText(p)})});}
 catch{return reply({error:'provider_unavailable'},502);}
 if(!response.ok)return reply({error:response.status===429?'provider_busy':'provider_rejected'},502);
 let result;try{result=await response.json();}catch{return reply({error:'provider_unknown'},502);}
 if(typeof result.id!=='string')return reply({error:'provider_unknown'},502);
 await storage.put(key,{...record,status:'sent',providerId:result.id});
 return reply({accepted:true,duplicate:false}); // Provider acceptance, not proof of inbox delivery.
}
export class ReportDelivery {
 constructor(ctx,env){this.ctx=ctx;this.env=env;}
 async fetch(request){let p;try{p=validateReport(await request.json());}catch{return reply({error:'invalid_report'},400);}
  return this.ctx.blockConcurrencyWhile(()=>deliver(p,this.env,this.ctx.storage));
 }
}
