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
let adaptiveLevel='all';
function additional(p=prefs,events=data.events,now=Date.now()){
 if(blocked||dirty)return [];
 return weaknesses(events,now).filter(r=>r.variant===p.variant).map(r=>({...r,q:EXTRA.get(r.originId)}))
  .filter(r=>(p.unit==='all'||r.q.unit===p.unit)&&(p.course==='all'||r.q.course===p.course)&&fits(r.q,p.variant)&&(adaptiveLevel==='all'||r.level===Number(adaptiveLevel))).slice(0,10);
}
function adaptiveStatus(){
 if(blocked||dirty)return '保存済みの記録を読み取れないため、弱点の判定を休止しています。「記録の保存」で元データを保管してください。';
 if(!data.events.length)return 'まだ回答記録がありません。まず通常練習をしてみよう。';
 return '候補がない場合は、別日の記録が足りない・直近30日の対象外・最後にヒントなしで正解・選択条件の対象外の可能性があります。';
}
function adaptiveSummary(){
 const all=weaknesses(data.events,Date.now(),true),active=all.filter(r=>!r.recovered),recovered=all.filter(r=>r.recovered);
 const groups=new Map();for(const r of active){const key=r.unit+' / '+({normal:'通常',kanji:'漢字・正式名',yomi:'読み'}[r.variant]);groups.set(key,(groups.get(key)||0)+1);}
 return `<section class="card" id="adaptive-summary"><h2>保護者向け・追加練習のサマリー</h2>${blocked||dirty?`<p>${esc(adaptiveStatus())}</p>`:`<p>要確認 ${active.length}論点・最後にヒントなしで正解 ${recovered.length}論点（直近30日・確認方法別）。絞り込み前の全分野です。</p>${[...groups].map(([k,n])=>`<p>${esc(k)}：${n}論点</p>`).join('')}<p>ヒント付き正解は候補に残し、ヒントなしの正解で追加練習を減らします。１回の正解は定着の証明ではありません。別の日にも通常練習で確かめてください。</p>`}</section>`;
}
function adaptivePanel(){
 const rows=additional();
 return `<section class="card" id="adaptive"><h2>弱点に合わせた追加練習</h2><p>最近30日で、まちがえた日が2日以上ある問題を練習します。日本時間で日付を分け、最後に答えた5日分を使います。同じ日にヒントを見て正解した場合も、その日のまちがいを数えます。ヒントなしで正解すると候補（こうほ）から外れます。そのあと、またまちがえたら見直します。読みと漢字は別々に数えます。記録が少ないので、苦手とは決めつけません。</p><label class="field">追加問題のむずかしさ<select id="adaptive-level">${[['all','すべて'],['1','基本'],['2','標準'],['3','発展']].map(([v,t])=>`<option value="${v}" ${adaptiveLevel===v?'selected':''}>${t}</option>`).join('')}</select></label><p>もとの問題と同じむずかしさです。平安は暗記＝基本、ペア・流れ＝標準、理由＝発展です。１回は選んだ問題数まで、候補は最大10問です。</p>${rows.map(r=>`<details><summary>${esc(r.unit)}：${esc(promptOf(r.q,r.variant))}</summary><p>選んだ理由：${r.wrong}/${r.total}日でまちがい・ヒントを見た日${r.hintCount}日。最後の回答：${esc(adaptiveLabel(r.lastAt))}（${r.lastCorrect?'ヒント付き正解':'まちがい'}）。むずかしさ${r.level}。${r.confusion?'同じペアの別の答えと一致しました。原因は未確定です。':''}</p><p>元問題：${esc(r.originId)} ／ 出典：${esc(r.q.source||'既存の平安単元問題')}</p><p>正解：${esc(expectedOf(r.q,r.variant))}</p><p>説明：${esc(r.q.explanation)}</p></details>`).join('')||`<p>${esc(adaptiveStatus())}</p>`}<button data-mode="adaptive" ${rows.length?'':'disabled'}>追加練習をはじめる（候補${rows.length}問・今回${Math.min(rows.length,prefs.count)}問）</button></section>`;
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
