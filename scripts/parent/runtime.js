/* Parent-only URL entry. Loaded before every application/notification script. */
(()=>{
'use strict';
const FLAG='yuika-parent-check-v1', PREFIX=FLAG+':';
const url=new URL(location.href);
let active=false,temporary=false;
const memory=new Map();
try{
 active=sessionStorage.getItem(FLAG)==='1';
 if(url.searchParams.get('parent-check')==='1'){active=true;sessionStorage.setItem(FLAG,'1');}
}catch{
 // The previous mode cannot be established safely. Do not read or write child
 // storage or send notifications; keep this page usable in an isolated buffer.
 active=true;temporary=true;
}
if(temporary)url.searchParams.set('parent-check','1');
else url.searchParams.delete('parent-check');
history.replaceState(null,'',url);
function targetURL(target){const next=new URL(target,location.href);if(temporary&&next.origin===location.origin)next.searchParams.set('parent-check','1');return next.href;}
function navigate(target){location.assign(targetURL(target));}
document.addEventListener('click',event=>{const link=event.target.closest?.('a[href]');if(temporary&&link&&!link.download&&new URL(link.href).origin===location.origin)link.href=targetURL(link.href);},true);
// No unload cleanup: reload/navigation must retain a working session sandbox.
const storage={
 getItem(k){return temporary?(memory.get(k)??null):active?sessionStorage.getItem(PREFIX+k):window.localStorage.getItem(k);},
 setItem(k,v){if(temporary)memory.set(k,String(v));else if(active)sessionStorage.setItem(PREFIX+k,String(v));else window.localStorage.setItem(k,v);},
 removeItem(k){if(temporary)memory.delete(k);else if(active)sessionStorage.removeItem(PREFIX+k);else window.localStorage.removeItem(k);},
 key(i){return temporary?([...memory.keys()][i]??null):active?Object.keys(sessionStorage).filter(k=>k.startsWith(PREFIX)).map(k=>k.slice(PREFIX.length))[i]??null:window.localStorage.key(i);},
 get length(){return temporary?memory.size:active?Object.keys(sessionStorage).filter(k=>k.startsWith(PREFIX)).length:window.localStorage.length;}
};
const temporaryNotice='一時保存が使えないため安全な確認モードで開きました。回答はこの画面だけに保持し、再読込・移動で失われます。子どもの記録と通知には触れません。';
let status='通知は送信しません（Workerへの送信・保留登録・再送・接続確認を停止）。';
function suppress(){if(!active)return false;console.info('[保護者確認モード] 通知を送信しません');const el=document.getElementById('parent-notification-status');if(el)el.textContent=temporary?temporaryNotice+' '+status:status;return true;}
function exit(){try{for(const k of Object.keys(sessionStorage))if(k===FLAG||k.startsWith(PREFIX))sessionStorage.removeItem(k);const next=new URL(location.href);next.searchParams.delete('parent-check');location.replace(next.href);}catch{document.getElementById('parent-notification-status').textContent='確認モードを解除できません。このタブを閉じ、保存領域の利用を許可してから開き直してください。子どもの記録と通知には触れません。';}}
const keys=['yuika-social-540-24-v1','yuika-social-540-25-v1','yuika-social-540-27-v1','yuika-science-review-v2','study-mock-focus-v1'];
const recordKeys=[...keys,...keys.map(k=>'yuika-prototype-v1:'+k),'yuika_sessions','yuika_feedback','yuika_cleared'];
// Only known record collections are editable; configuration and unknown data stay intact.
function plan(since){
 const cutoff=new Date(since).getTime();if(!Number.isFinite(cutoff))throw Error('日時を指定してください。');
 const changes=[];let count=0;
 const recent=e=>{const at=e?.answeredAt??e?.at??e?.capturedAt??e?.ts;return typeof at==='string'&&Number.isFinite(Date.parse(at))&&Date.parse(at)>=cutoff;};
 for(const key of recordKeys){const raw=window.localStorage.getItem(key);if(raw===null)continue;let v;try{v=JSON.parse(raw);}catch{throw Error('読み取れない記録があります。先にJSONを保全してください。');}
 let removed=0;
 const filter=a=>a.filter(e=>{if(recent(e)){removed++;return false;}return true;});
 if(Array.isArray(v))v=filter(v);
 else if(v&&typeof v==='object'){
  if(key==='yuika_cleared'){for(const [k,e] of Object.entries(v))if(recent(e)){delete v[k];removed++;}}
  else for(const name of ['events','legacy'])if(Array.isArray(v[name]))v[name]=filter(v[name]);
 }
 if(removed){count+=removed;changes.push({key,raw,next:JSON.stringify(v)});}
 }
 return {count,changes};
}
function remove(plan){
 // Prevent a stale confirmation from overwriting another tab's answers.
 for(const c of plan.changes)if(window.localStorage.getItem(c.key)!==c.raw)throw Error('記録が更新されました。件数を確認し直してください。');
 const written=[];
 try{for(const c of plan.changes){window.localStorage.setItem(c.key,c.next);written.push(c);}}
 catch{
  let restored=true;
  for(const c of written.reverse())try{
   // A different tab's newer value must never be overwritten by rollback.
   if(window.localStorage.getItem(c.key)!==c.next){restored=false;continue;}
   window.localStorage.setItem(c.key,c.raw);
   if(window.localStorage.getItem(c.key)!==c.raw)restored=false;
  }catch{restored=false;}
  const error=Error(restored?'削除は完了していません。変更済みの記録を元に戻しました。削除前のJSONを保全し、件数を確認し直してください。':'削除途中で保存に失敗し、一部の記録の復元を確認できません。この画面を閉じず「削除前のJSONを保全」で原本を保存してください。');
  error.recovery=plan;error.incomplete=!restored;throw error;
 }
}
function exportRecovery(plan){
 const blob=new Blob([JSON.stringify({format:'yuika-parent-cleanup-backup-v1',records:plan.changes.map(c=>({key:c.key,raw:c.raw}))},null,2)],{type:'application/json'});
 const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='yuika-before-cleanup.json';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);
}
function mount(){
 if(!active)return;
 const banner=document.createElement('section');banner.id='parent-check-banner';banner.style.cssText='position:sticky;top:0;z-index:2147483647;background:#fff1bd;color:#302500;padding:12px;font:16px/1.5 system-ui';
 banner.innerHTML='<strong>保護者確認モード（記録・通知なし）</strong> <button id="parent-exit" type="button">終了</button><div id="parent-notification-status" role="status"></div><details><summary>保護者：既存の子どもの記録を整理</summary><p>このブラウザー内の全単元・旧版・試作の日時付き記録が対象です。先に各画面からJSONを保管し、他の学習タブを閉じてください。日時のない旧集計は保持します。送信済み通知は取り消せません。</p><label>指定日時以降（この端末の時刻）<input id="parent-since" type="datetime-local"></label><button id="parent-count" type="button">削除件数を確認</button><p id="parent-delete-status" role="status"></p><button id="parent-delete" type="button" disabled>子どもの記録を削除</button> <button id="parent-backup" type="button" hidden>削除前のJSONを保全</button></details>';
 document.body.prepend(banner);document.getElementById('parent-exit').onclick=exit;
 let pending=null,recovery=null,incomplete=false;const backup=document.getElementById('parent-backup');backup.onclick=()=>{if(recovery)exportRecovery(recovery);};const result=document.getElementById('parent-delete-status'),button=document.getElementById('parent-delete');
 document.getElementById('parent-since').oninput=()=>{pending=null;button.disabled=true;result.textContent='日時を変更しました。件数を再確認してください。';};
 document.getElementById('parent-count').onclick=()=>{if(incomplete){result.textContent='復元未確認の記録があります。先に削除前のJSONを保全し、この画面で追加の削除をしないでください。';return;}try{pending=plan(document.getElementById('parent-since').value);result.textContent=`削除対象：${pending.count}件`;button.disabled=!pending.count;}catch(e){pending=null;button.disabled=true;result.textContent=e.message;}};
 button.onclick=()=>{if(!pending||!confirm(`${pending.count}件の子どもの記録を削除します。元に戻せません。削除しますか？`))return;try{remove(pending);result.textContent=`${pending.count}件を削除しました。終了すると再集計されます。`;pending=null;button.disabled=true;}catch(e){if(e.recovery){recovery=e.recovery;incomplete=e.incomplete;backup.hidden=false;}result.textContent=e.message;pending=null;button.disabled=true;}};
 if(temporary){document.getElementById('parent-count').disabled=true;document.getElementById('parent-since').disabled=true;}
 suppress();
}
window.YuikaParent={get active(){return active;},storage,suppress,navigate};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount);else mount();
})();
