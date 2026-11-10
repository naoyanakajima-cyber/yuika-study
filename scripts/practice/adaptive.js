// Embedded by embed.py. v1 IDs and prompts are durable record contracts.
const EXTRA=new Map();
for(const q of QUESTIONS){
 const extra={...q,id:q.id+'-review-v1',originId:q.id,prompt:'復習：'+q.prompt};
 EXTRA.set(q.id,extra);Q.set(extra.id,extra);
}
MODES.adaptive='弱点に合わせた追加練習';
// Derive Japan dates for analysis only; historical day/offset fields remain intact.
const japanDay=iso=>day(iso,-540);
const adaptiveLabel=iso=>new Date(iso).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'})+'（日本時間）';
function weaknesses(events=data.events,now=Date.now(),includeRecovered=false){
 const groups=new Map(),seen=new Set();
 for(const e of order(events)){
  if(seen.has(e.id))continue;seen.add(e.id);
  const q=Q.get(e.questionId),age=now-Date.parse(e.at);
  if(!q||age<0||age>30*86400000)continue;
  const id=q.originId||q.id,key=id+':'+e.variant;
  if(!groups.has(key))groups.set(key,[]);groups.get(key).push(e);
 }
 const rows=[];
 for(const [key,all] of groups){
  // One observation per Japan day; retain hints/errors from earlier retries.
  const days=new Map();
  for(const e of all){
   const key=japanDay(e.at),previous=days.get(key);
   days.set(key,{last:e,wrong:!e.correct||!!previous?.wrong,hint:e.hint||!!previous?.hint});
  }
  const samples=[...days.values()].slice(-5),last=samples.at(-1).last;
  // A hinted success cannot undo an earlier unassisted success by itself.
  let recovered=false;
  for(const e of all){if(!e.correct)recovered=false;else if(!e.hint)recovered=true;}
  const wrong=samples.filter(d=>!d.last.correct||((d.last.hint||(includeRecovered&&recovered))&&d.wrong)).length;
  if(samples.length<2||wrong<2||(!includeRecovered&&recovered))continue;
  const q=Q.get(last.questionId),origin=Q.get(q.originId||q.id);
  const confusion=QUESTIONS.filter(o=>o.id!==origin.id&&o.pair&&o.pair===origin.pair)
   .some(o=>grade(o,last.response,last.variant));
  rows.push({originId:origin.id,unit:origin.unit,variant:last.variant,wrong,total:samples.length,
   recovered,lastHint:last.hint,lastCorrect:last.correct,level:origin.level||({memory:1,pairs:2,flow:2,reason:3}[origin.course]||1),hintCount:samples.filter(d=>d.hint).length,lastAt:last.at,confusion});
 }
 return rows.sort((a,b)=>b.wrong/b.total-a.wrong/a.total||b.lastAt.localeCompare(a.lastAt)||a.originId.localeCompare(b.originId)||a.variant.localeCompare(b.variant));
}
// A device clock is not a trusted time source. Do not reinterpret future-dated
// history as a recovered/empty weakness set after the clock moves backwards.
function practiceClockIssue(events=data.events,now=Date.now()){
 return events.some(e=>Date.parse(e.at)>now+5*60000);
}
function practiceUnavailable(events=data.events,now=Date.now()){return blocked||dirty||practiceClockIssue(events,now);}
const PRACTICE_CLOCK_NOTICE='今より5分以上先の回答記録があります。端末の日付と時刻を確認してください。弱点の判定と今日の5問はお休みします。記録の時刻は自動で直しません。';
let adaptiveLevel='all';
function additional(p=prefs,events=data.events,now=Date.now()){
 if(practiceUnavailable(events,now))return [];
 return practiceWeaknesses(events,now).filter(r=>r.variant===p.variant).map(r=>({...r,q:EXTRA.get(r.originId)}))
  .filter(r=>(p.unit==='all'||r.q.unit===p.unit)&&(p.course==='all'||r.q.course===p.course)&&fits(r.q,p.variant)&&(adaptiveLevel==='all'||r.level===Number(adaptiveLevel))).slice(0,10);
}
function adaptiveStatus(){
 if(practiceClockIssue())return PRACTICE_CLOCK_NOTICE;
 if(blocked||dirty)return '保存済みの記録を読み取れないため、弱点の判定を休止しています。「記録の保存」で元データを保管してください。';
 if(!data.events.length)return 'まだ回答記録がありません。まず通常練習をしてみよう。';
 return '候補がない場合は、別日の記録が足りない・直近30日の対象外・最後にヒントなしで正解・選択条件の対象外の可能性があります。';
}
function adaptiveSummary(){
 const all=weaknesses(data.events,Date.now(),true),active=practiceWeaknesses(),recovered=all.filter(r=>r.recovered);
 const groups=new Map();for(const r of active){const key=r.unit+' / '+({normal:'通常',kanji:'漢字・正式名',yomi:'読み'}[r.variant]);groups.set(key,(groups.get(key)||0)+1);}
 return `<section class="card" id="adaptive-summary"><h2>保護者向け・追加練習のサマリー</h2>${practiceUnavailable()?`<p>${esc(adaptiveStatus())}</p>`:`<p>要確認 ${active.length}論点・最後にヒントなしで正解 ${recovered.length}論点（直近30日・確認方法別）。絞り込み前の全分野です。</p>${[...groups].map(([k,n])=>`<p>${esc(k)}：${n}論点</p>`).join('')}<p>ヒント付き正解は候補に残し、ヒントなしの正解で追加練習を減らします。１回の正解は定着の証明ではありません。再確認待ちに進み、別の日の再確認で確かめます。</p>`}</section>`;
}
function adaptivePanel(){
 const rows=additional();
 return `<section class="card" id="adaptive"><h2>弱点に合わせた追加練習</h2><p>最近30日で、まちがえた日が2日以上ある問題を練習します。日本時間で日付を分け、最後に答えた5日分を使います。同じ日にヒントを見て正解した場合も、その日のまちがいを数えます。ヒントなしで正解すると候補（こうほ）から外れます。再確認待ちに進み、期限が来たら今日の5問で確かめます。まちがえたら弱点に戻ります。読みと漢字は別々に数えます。記録が少ないので、苦手とは決めつけません。</p><label class="field">追加問題のむずかしさ<select id="adaptive-level">${[['all','すべて'],['1','基本'],['2','標準'],['3','発展']].map(([v,t])=>`<option value="${v}" ${adaptiveLevel===v?'selected':''}>${t}</option>`).join('')}</select></label><p>もとの問題と同じむずかしさです。平安は暗記＝基本、ペア・流れ＝標準、理由＝発展です。１回は選んだ問題数まで、候補は最大10問です。</p>${rows.map(r=>`<details><summary>${esc(r.unit)}：${esc(promptOf(r.q,r.variant))}</summary><p>選んだ理由：${r.wrong}/${r.total}日でまちがい・ヒントを見た日${r.hintCount}日。最後の回答：${esc(adaptiveLabel(r.lastAt))}（${r.lastCorrect?'ヒント付き正解':'まちがい'}）。むずかしさ${r.level}。${r.confusion?'同じペアの別の答えと一致しました。原因は未確定です。':''}</p><p>元問題：${esc(r.originId)} ／ 出典：${esc(r.q.source||'既存の平安単元問題')}</p><p>正解：${esc(expectedOf(r.q,r.variant))}</p><p>説明：${esc(r.q.explanation)}</p></details>`).join('')||`<p>${esc(adaptiveStatus())}</p>`}<button data-mode="adaptive" ${rows.length?'':'disabled'}>追加練習をはじめる（候補${rows.length}問・今回${Math.min(rows.length,prefs.count)}問）</button></section>`;
}
// Bind after each home render; all content remains inside the standalone app.
const originalHome=home;
home=function(){
 const focused=document.activeElement?.id;
 originalHome();
 document.getElementById('adaptive-level').onchange=e=>{adaptiveLevel=e.target.value;home();};
 if(focused)document.getElementById(focused)?.focus({preventScroll:true});
};
const originalParent=parent;
parent=function(){originalParent();main.insertAdjacentHTML('afterbegin',adaptiveSummary());};

// Retention v1 is a deterministic projection of durable events, independent of
// the current 30-day extraction window. Replaying legacy JSON migrates without
// rewriting any event, ID, timestamp, key, or historical grade.
const REVIEW_INTERVAL_DAYS=Object.freeze([1,3,7]); // provisional, editable configuration
MODES.daily='今日の5問';
const addJapanDays=(d,n)=>new Date(Date.parse(d+'T00:00:00Z')+n*86400000).toISOString().slice(0,10);
function retention(events=data.events,now=Date.now()){
 const states=new Map(),histories=new Map(),seen=new Set();
 for(const e of order(events)){
  if(seen.has(e.id)||Date.parse(e.at)>now)continue;seen.add(e.id);
  const q=Q.get(e.questionId);if(!q)continue;
  const originId=q.originId||q.id,key=originId+':'+e.variant;
  let s=states.get(key);
  if(!s){
   // A new weakness requires errors on two Japan days. Success cannot add an
   // error day; examine the existing rule only when an error can change it.
   // Keep its rolling window small instead of replaying a growing full history
   // for every success (quadratic on long, previously correct-only histories).
   if(!histories.has(key))histories.set(key,{events:[],start:0,wrongDays:new Map()});
   const history=histories.get(key),stamp=Date.parse(e.at),cutoff=stamp-30*86400000;
   history.events.push(e);
   while(Date.parse(history.events[history.start].at)<cutoff)history.start++;
   if(e.correct)continue;
   history.wrongDays.set(japanDay(e.at),stamp);
   for(const [d,t] of history.wrongDays)if(t<cutoff)history.wrongDays.delete(d);
   if(history.wrongDays.size<2||!weaknesses(history.events.slice(history.start),stamp).length)continue;
   s={originId,variant:e.variant,status:'weak',stage:0,due:null,anchor:null};states.set(key,s);histories.delete(key);
  }
  const date=japanDay(e.at);
  if(!e.correct){s.status='weak';s.stage=0;s.due=null;s.anchor=null;}
  else if(!e.hint){
   if(s.status==='weak'){
    s.status='waiting';s.stage=0;s.anchor=date;s.due=addJapanDays(date,REVIEW_INTERVAL_DAYS[0]);
   }else if(s.status==='waiting'&&date>=s.due){
    s.stage++;
    if(s.stage===REVIEW_INTERVAL_DAYS.length){s.status='retained';s.due=null;}
    else s.due=addJapanDays(date,REVIEW_INTERVAL_DAYS[s.stage]-REVIEW_INTERVAL_DAYS[s.stage-1]);
   }
  }
 }
 return [...states.values()];
}
function practiceWeaknesses(events=data.events,now=Date.now()){
 if(practiceUnavailable(events,now))return [];
 const rows=weaknesses(events,now),keys=new Set(rows.map(r=>r.originId+':'+r.variant));
 for(const s of retention(events,now).filter(s=>s.status==='weak')){
  if(keys.has(s.originId+':'+s.variant))continue;
  const q=Q.get(s.originId),es=order(events).filter(e=>(Q.get(e.questionId)?.originId||e.questionId)===s.originId&&e.variant===s.variant&&Date.parse(e.at)<=now),last=es.at(-1);
  rows.push({...s,unit:q.unit,level:q.level||({memory:1,pairs:2,flow:2,reason:3}[q.course]||1),wrong:1,total:1,hintCount:0,lastAt:last.at,lastCorrect:last.correct,lastHint:last.hint});
 }
 return rows;
}
function dueReviews(p=prefs,events=data.events,now=Date.now()){
 if(practiceUnavailable(events,now))return [];
 const today=japanDay(new Date(now).toISOString());
 return retention(events,now).filter(s=>s.status==='waiting'&&s.due<=today)
  .sort((a,b)=>a.due.localeCompare(b.due)||a.originId.localeCompare(b.originId)||a.variant.localeCompare(b.variant))
  .filter(s=>{const q=Q.get(s.originId);return s.variant===p.variant&&fits(q,p.variant)&&(p.unit==='all'||p.unit===q.unit)&&(p.course==='all'||p.course===q.course);});
}
function dailyQuestions(p=prefs){
 if(practiceUnavailable())return [];
 const result=[],seen=new Set();
 const push=q=>{const id=q.originId||q.id;if(!seen.has(id)){seen.add(id);result.push(q);}};
 dueReviews(p).forEach(s=>push(EXTRA.get(s.originId)));
 additional(p).forEach(s=>push(s.q));
 shuffle(candidates('normal',p)).forEach(push);
 return result.slice(0,p.count);
}
function startDaily(){
 if(practiceUnavailable()){note(adaptiveStatus());return;}
 const qs=dailyQuestions();if(!qs.length){note('この条件では候補がありません。');return;}
 rememberPrefs();run={id:uuid(),mode:'daily',variant:prefs.variant,qs,index:0,results:[],done:false};
 screen='quiz';prepare();render();main.focus();window.scrollTo(0,0);
}
const PREF_KEY=KEY+'-preferences-v1';
function restorePrefs(){
 try{const p=JSON.parse(localStorage.getItem(PREF_KEY)||'null');if(!p)return;
  if([5,10,15].includes(p.count))prefs.count=p.count;
  if(Object.hasOwn(COURSES,p.course))prefs.course=p.course;
  if(p.unit==='all'||UNITS.includes(p.unit))prefs.unit=p.unit;
  if((typeof VARIANTS==='undefined'?['normal','kanji'].includes(p.variant):Object.hasOwn(VARIANTS,p.variant)))prefs.variant=p.variant;
 }catch{note('学習設定を読み取れません。初期設定で始めます。');}
}
function rememberPrefs(){
 try{localStorage.setItem(PREF_KEY,JSON.stringify(prefs));localStorage.setItem('yuika-last-daily-unit-v1',location.pathname.split('/').pop());}
 catch{note('学習設定を保存できません。次回起動時は初期設定になります。');}
}
const retentionHome=home;
home=function(){
 retentionHome();
 main.insertAdjacentHTML('afterbegin',`<section class="card"><button id="daily-five" class="primary wide" ${practiceUnavailable()?'disabled':''}>今日の5問をはじめる（今回は${prefs.count}問）</button><p>期限の来た再確認 → 弱点の追加練習 → 通常問題。分野・確認方法・問題数は下で変更できます。</p><p>今日の再確認：${dueReviews().length}件</p></section>`);
 document.getElementById('daily-five').onclick=startDaily;
 main.querySelectorAll('#course,#unit,#variant,[data-count]').forEach(el=>{
  const type=el.tagName==='SELECT'?'onchange':'onclick',previous=el[type];
  el[type]=e=>{previous(e);rememberPrefs();};
 });
};
const retentionParent=parent;
parent=function(){retentionParent();if(!practiceUnavailable()){
 const states=retention(),today=japanDay(new Date().toISOString());
 document.getElementById('adaptive-summary').insertAdjacentHTML('beforeend',`<p id="retention-summary">今日の再確認 ${states.filter(s=>s.status==='waiting'&&s.due<=today).length}件（期限超過を含む・全分野と確認方法）／再確認待ち ${states.filter(s=>s.status==='waiting').length}件／定着 ${states.filter(s=>s.status==='retained').length}件</p>`);
}};
restorePrefs();
// Normal sessions also remember the last visited learning unit.
const rememberedStart=start;
start=function(mode){rememberPrefs();rememberedStart(mode);};

// Repaint only summary screens. A suspended iPad tab can cross midnight without
// navigation; active answers and entered text must never be replaced by refresh.
let practiceDisplayDay=japanDay(new Date().toISOString());
function refreshPracticeDate(force=false){
 const today=japanDay(new Date().toISOString()),changed=today!==practiceDisplayDay;
 practiceDisplayDay=today;
 if((force||changed)&&(screen==='home'||screen==='parent'))render();
}
setInterval(()=>refreshPracticeDate(),30000);
window.addEventListener('focus',()=>refreshPracticeDate(true));
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshPracticeDate(true);});
