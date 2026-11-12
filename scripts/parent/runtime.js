/* Parent-only URL entry. Loaded before every application/notification script. */
(()=>{
'use strict';
const FLAG='yuika-parent-check-v1', PREFIX=FLAG+':';
const url=new URL(location.href);
let active=sessionStorage.getItem(FLAG)==='1';
if(url.searchParams.get('parent-check')==='1'){
 active=true;sessionStorage.setItem(FLAG,'1');
 url.searchParams.delete('parent-check');history.replaceState(null,'',url);
}
// No unload cleanup: reload/navigation must retain the sandbox. sessionStorage
// belongs to this tab and expires with it. Never fall back to child storage.
const storage={
 getItem(k){return active?sessionStorage.getItem(PREFIX+k):window.localStorage.getItem(k);},
 setItem(k,v){if(active)sessionStorage.setItem(PREFIX+k,String(v));else window.localStorage.setItem(k,v);},
 removeItem(k){if(active)sessionStorage.removeItem(PREFIX+k);else window.localStorage.removeItem(k);},
 key(i){return active?Object.keys(sessionStorage).filter(k=>k.startsWith(PREFIX)).map(k=>k.slice(PREFIX.length))[i]??null:window.localStorage.key(i);},
 get length(){return active?Object.keys(sessionStorage).filter(k=>k.startsWith(PREFIX)).length:window.localStorage.length;}
};
let status='通知は送信しません（Workerへの送信・保留登録・再送・接続確認を停止）。';
function suppress(){if(!active)return false;console.info('[保護者確認モード] 通知を送信しません');const el=document.getElementById('parent-notification-status');if(el)el.textContent=status;return true;}
function exit(){for(const k of Object.keys(sessionStorage))if(k===FLAG||k.startsWith(PREFIX))sessionStorage.removeItem(k);location.reload();}
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
 for(const c of plan.changes)window.localStorage.setItem(c.key,c.next);
}
function mount(){
 if(!active)return;
 const banner=document.createElement('section');banner.id='parent-check-banner';banner.style.cssText='position:sticky;top:0;z-index:2147483647;background:#fff1bd;color:#302500;padding:12px;font:16px/1.5 system-ui';
 banner.innerHTML='<strong>保護者確認モード（記録・通知なし）</strong> <button id="parent-exit" type="button">終了</button><div id="parent-notification-status" role="status"></div><details><summary>保護者：既存の子どもの記録を整理</summary><p>このブラウザー内の全単元・旧版・試作の日時付き記録が対象です。先に各画面からJSONを保管し、他の学習タブを閉じてください。日時のない旧集計は保持します。送信済み通知は取り消せません。</p><label>指定日時以降（この端末の時刻）<input id="parent-since" type="datetime-local"></label><button id="parent-count" type="button">削除件数を確認</button><p id="parent-delete-status" role="status"></p><button id="parent-delete" type="button" disabled>子どもの記録を削除</button></details>';
 document.body.prepend(banner);document.getElementById('parent-exit').onclick=exit;
 let pending=null;const result=document.getElementById('parent-delete-status'),button=document.getElementById('parent-delete');
 document.getElementById('parent-since').oninput=()=>{pending=null;button.disabled=true;result.textContent='日時を変更しました。件数を再確認してください。';};
 document.getElementById('parent-count').onclick=()=>{try{pending=plan(document.getElementById('parent-since').value);result.textContent=`削除対象：${pending.count}件`;button.disabled=!pending.count;}catch(e){pending=null;button.disabled=true;result.textContent=e.message;}};
 button.onclick=()=>{if(!pending||!confirm(`${pending.count}件の子どもの記録を削除します。元に戻せません。削除しますか？`))return;try{remove(pending);result.textContent=`${pending.count}件を削除しました。終了すると再集計されます。`;pending=null;button.disabled=true;}catch(e){result.textContent=e.message;pending=null;button.disabled=true;}};
 suppress();
}
window.YuikaParent={get active(){return active;},storage,suppress};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount);else mount();
})();
