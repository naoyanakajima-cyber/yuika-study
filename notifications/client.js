/* Shared source, embedded in each HTML to preserve single-file use. */
(()=>{
'use strict';
const CONFIG='yuika-mail-config-v1',PREFIX='yuika-mail-job-v1:';
const memory=new Map();let busy=false,last='',timer=null;
const id=()=>crypto.randomUUID?crypto.randomUUID():Array.from(crypto.getRandomValues(new Uint8Array(16)),v=>v.toString(16).padStart(2,'0')).join('');
function config(){try{return JSON.parse(localStorage.getItem(CONFIG)||'null');}catch{return null;}}
function store(job){memory.set(job.report?.id||job.id,job);try{localStorage.setItem(PREFIX+(job.report?.id||job.id),JSON.stringify(job));return true;}catch{last='通知の保留データを保存できません。この画面を閉じる前に接続を確認してください。学習記録の保存状況も確認してください。';return false;}}
function jobs(){const all=new Map(memory);try{for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k?.startsWith(PREFIX)){try{const v=JSON.parse(localStorage.getItem(k));if(v&&typeof v.id==='string'&&!all.has(v.id))all.set(v.id,v);}catch{last='読み取れない通知記録があります。上書きせず保管しています。';}}}}catch{}return [...all.values()];}
function show(){const el=document.getElementById('yuika-mail-status');if(!el)return;const cfg=config(),pending=jobs().filter(j=>j.status!=='accepted').length;
 el.textContent=last||(!cfg?.enabled?'自動メールは未接続です。接続後のチャレンジから通知します。':`自動メール：${cfg.recipient}。${pending?`保留 ${pending}件。アプリを開いている間に再試行します。`:'通知の保留はありません。'}`);
}
function schedule(){clearTimeout(timer);timer=setTimeout(()=>flush(),60_000);}
async function process(){const cfg=config();if(!cfg?.enabled||!navigator.onLine){show();return;}
 for(const job of jobs().filter(j=>j.status==='pending').slice(0,10)){
  if(!config()?.enabled)break;
  if(job.endpoint!==cfg.endpoint||job.recipient!==cfg.recipient){last='以前の送信先向けの保留通知があります。送信先が違うため自動送信していません。';continue;}
  if(job.nextAttempt>Date.now())continue;
  try{
   const r=await fetch(cfg.endpoint+'/reports',{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json',Authorization:'Bearer '+cfg.token},body:JSON.stringify(job.report),signal:AbortSignal.timeout(20_000)});
   const body=await r.json();
   if(r.ok&&body.accepted===true){store({id:job.id,status:'accepted',acceptedAt:new Date().toISOString(),endpoint:job.endpoint,recipient:job.recipient});last='今回の通知を送信サービスが受け付けました（受信箱への到着確認ではありません）。';}
   else if(r.status===401||r.status===403){last='通知の接続認証を確認してください。結果は保留しています。';break;}
   else if(r.status===409||r.status===400||r.status===413){job.status='needs_review';job.error=body.error||'invalid_report';store(job);last='確認が必要な通知があります。二重送信を防ぐため、自動再送を止めています。';}
   else{job.tries=(job.tries||0)+1;job.nextAttempt=Date.now()+Math.min(3600000,60000*2**Math.min(job.tries,6));store(job);last='メール送信は保留中です。次回の起動時などに再試行します。';}
  }catch{job.tries=(job.tries||0)+1;job.nextAttempt=Date.now()+Math.min(3600000,60000*2**Math.min(job.tries,6));store(job);last='通信できないため通知を保留しています。学習は続けられます。';}
 }
 show();
}
async function flush(){if(busy)return;busy=true;try{if(navigator.locks)await navigator.locks.request('yuika-mail-send',process);else await process();}finally{busy=false;schedule();}}
function enqueue(report){
 const cfg=config();if(!cfg?.enabled){last='自動メールは未接続です。今回の結果は学習記録で確認できます。';show();return false;}
 if(!report||!report.id||jobs().some(j=>j.id===report.id)){show();return true;}
 let old;try{old=localStorage.getItem(PREFIX+report.id);}catch{}
 if(old!==null&&old!==undefined){last='同じ通知IDの保存データがあるため、上書きしていません。';show();return false;}
 store({id:report.id,report,endpoint:cfg.endpoint,recipient:cfg.recipient,status:'pending',tries:0,nextAttempt:0});
 last='チャレンジ結果を通知の保留リストに入れました。';show();void flush();return true;
}
function exportPending(){const pending=jobs().filter(j=>j.report).map(j=>({id:j.id,status:j.status,error:j.error||null,report:j.report}));const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,pending},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='yuika-pending-notifications.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);}
function endpoint(value){const u=new URL(value);if(u.protocol!=='https:'||!u.hostname.endsWith('.workers.dev')||u.username||u.password||u.port||u.search||u.hash||u.pathname!=='/')throw Error('設定したCloudflare Workerの https://〜.workers.dev のURLを入力してください。');return u.origin;}
function mount(){
 const wrap=document.createElement('section');wrap.style.cssText='max-width:944px;margin:20px auto;padding:16px;font:13px/1.7 system-ui;color:#394d43';
 wrap.innerHTML='<p id="yuika-mail-status" role="status" aria-live="polite"></p><details><summary style="cursor:pointer">保護者：チャレンジ結果の自動メール</summary><p>接続すると、社会・理科のチャレンジ終了時に、今回の正誤・回答・ヒント等を登録した保護者へ送ります。自由記述は送信しません。以前の単元で記録していない項目は補いません。過去の履歴の一括送信はしません。</p><p>iPadでアプリを閉じている間は再送できません。未送信分は、次に開いたときに再試行します。通知を停止しても学習記録は消しません。</p><form id="yuika-mail-form"><label style="display:block">送信サーバーURL<input id="yuika-mail-url" type="url" required placeholder="https://〜.workers.dev" style="display:block;width:100%;box-sizing:border-box;padding:10px"></label><label style="display:block">この端末の接続キー<input id="yuika-mail-token" type="password" required minlength="32" autocomplete="off" style="display:block;width:100%;box-sizing:border-box;padding:10px"></label><p>メールサービスのAPIキーはここに入れません。接続キーは公開サイトやGitHubに書き込まず、この端末だけに保存します。</p><button type="submit" style="padding:10px;min-height:44px">接続を確認して有効にする</button> <button id="yuika-mail-stop" type="button" style="padding:10px;min-height:44px">自動メールを停止</button> <button id="yuika-mail-retry" type="button" style="padding:10px;min-height:44px">保留分を確認・再試行</button> <button id="yuika-mail-export" type="button" style="padding:10px;min-height:44px">保留通知をJSONで保全</button></form></details>';
 document.body.append(wrap);
 const cfg=config();if(cfg?.endpoint)document.getElementById('yuika-mail-url').value=cfg.endpoint;
 document.getElementById('yuika-mail-form').onsubmit=async e=>{e.preventDefault();const button=e.submitter;if(button)button.disabled=true;try{
  const base=endpoint(document.getElementById('yuika-mail-url').value.trim()),token=document.getElementById('yuika-mail-token').value.trim();if(token.length<32)throw Error('接続キーを確認してください。');
  const r=await fetch(base+'/health',{headers:{Authorization:'Bearer '+token},credentials:'omit',signal:AbortSignal.timeout(15000)}),body=await r.json();
  if(!r.ok||body.ready!==true||typeof body.recipient!=='string')throw Error('送信サーバーの設定・接続キーを確認してください。');
  if(!confirm('送信先：'+body.recipient+'\n今後のチャレンジ結果をこの宛先へ自動送信します。接続しますか？'))return;
  localStorage.setItem(CONFIG,JSON.stringify({enabled:true,endpoint:base,token,recipient:body.recipient}));document.getElementById('yuika-mail-token').value='';last='自動メールを有効にしました。次のチャレンジから通知します。';show();void flush();
 }catch(err){last='接続できませんでした。'+err.message;show();}finally{if(button)button.disabled=false;}};
 document.getElementById('yuika-mail-stop').onclick=()=>{try{const c=config();if(c)localStorage.setItem(CONFIG,JSON.stringify({...c,enabled:false}));last='今後の自動送信を停止しました。送信処理が始まっている通知は取り消せません。';}catch{last='停止設定を保存できません。通信を切って、この画面を閉じてください。';}show();};
 document.getElementById('yuika-mail-retry').onclick=()=>{last='';show();void flush();};document.getElementById('yuika-mail-export').onclick=exportPending;
 show();void flush();
}
window.YuikaReports={enqueue,id};
window.addEventListener('online',()=>void flush());
document.addEventListener('visibilitychange',()=>{if(!document.hidden)void flush();});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount);else mount();
})();
