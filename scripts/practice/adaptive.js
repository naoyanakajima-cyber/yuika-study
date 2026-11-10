// Embedded by embed.py. v1 IDs and prompts are durable record contracts.
const EXTRA=new Map();
for(const q of QUESTIONS){
 const extra={...q,id:q.id+'-review-v1',originId:q.id,prompt:'復習：'+q.prompt};
 EXTRA.set(q.id,extra);Q.set(extra.id,extra);
}
MODES.adaptive='弱点に合わせた追加練習';
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
  // One observation per local day prevents immediate retries dominating evidence.
  const days=new Map();for(const e of all)days.set(e.day,e);
  const samples=[...days.values()].slice(-5),last=samples.at(-1);
  const recovered=last.correct&&!last.hint;
  const wrong=samples.filter(e=>!e.correct||((e.hint||(includeRecovered&&recovered))&&all.some(a=>a.day===e.day&&!a.correct))).length;
  if(samples.length<2||wrong<2||(!includeRecovered&&recovered))continue;
  const q=Q.get(last.questionId),origin=Q.get(q.originId||q.id);
  const confusion=QUESTIONS.filter(o=>o.id!==origin.id&&o.pair&&o.pair===origin.pair)
   .some(o=>grade(o,last.response,last.variant));
  rows.push({originId:origin.id,unit:origin.unit,variant:last.variant,wrong,total:samples.length,
   recovered,lastHint:last.hint,lastCorrect:last.correct,level:origin.level||({memory:1,pair:2,flow:2,reason:3}[origin.course]||1),hintCount:samples.filter(e=>e.hint).length,lastAt:last.at,confusion});
 }
 return rows.sort((a,b)=>b.wrong/b.total-a.wrong/a.total||b.lastAt.localeCompare(a.lastAt)||a.originId.localeCompare(b.originId)||a.variant.localeCompare(b.variant));
}
let adaptiveLevel='all';
function additional(p=prefs,events=data.events,now=Date.now()){
 if(blocked)return [];
 return weaknesses(events,now).filter(r=>r.variant===p.variant).map(r=>({...r,q:EXTRA.get(r.originId)}))
  .filter(r=>(p.unit==='all'||r.q.unit===p.unit)&&(p.course==='all'||r.q.course===p.course)&&fits(r.q,p.variant)&&(adaptiveLevel==='all'||r.level===Number(adaptiveLevel))).slice(0,10);
}
function adaptiveStatus(){
 if(blocked)return '保存済みの記録を読み取れないため、弱点の判定を休止しています。「記録の保存」で元データを保管してください。';
 if(!data.events.length)return 'まだ回答記録がありません。まず通常練習をしてみよう。';
 return '候補がない場合は、別日の記録が足りない・直近30日の対象外・最後にヒントなしで正解・選択条件の対象外の可能性があります。';
}
function adaptiveSummary(){
 const all=weaknesses(data.events,Date.now(),true),active=all.filter(r=>!r.recovered),recovered=all.filter(r=>r.recovered);
 const groups=new Map();for(const r of active){const key=r.unit+' / '+({normal:'通常',kanji:'漢字・正式名',yomi:'読み'}[r.variant]);groups.set(key,(groups.get(key)||0)+1);}
 return `<section class="card" id="adaptive-summary"><h2>保護者向け・追加練習のサマリー</h2>${blocked?`<p>${esc(adaptiveStatus())}</p>`:`<p>要確認 ${active.length}論点・最後にヒントなしで正解 ${recovered.length}論点（直近30日・確認方法別）。絞り込み前の全分野です。</p>${[...groups].map(([k,n])=>`<p>${esc(k)}：${n}論点</p>`).join('')}<p>ヒント付き正解は候補に残し、ヒントなしの正解で追加練習を減らします。１回の正解は定着の証明ではありません。別の日にも通常練習で確かめてください。</p>`}</section>`;
}
function adaptivePanel(){
 const rows=additional();
 return `<section class="card" id="adaptive"><h2>弱点に合わせた追加練習</h2><p>直近30日・別日の最後の回答（最大5日）のうち、2日以上誤答した論点（同日にヒント付きで解き直した誤答も含む）を復習します。最後にヒントなしで正解すると候補から外れます。確認方法は別集計です。少数の記録から苦手や原因を断定しません。</p><label class="field">追加問題の難易度<select id="adaptive-level">${[['all','すべて'],['1','基本'],['2','標準'],['3','発展']].map(([v,t])=>`<option value="${v}" ${adaptiveLevel===v?'selected':''}>${t}</option>`).join('')}</select></label><p>原問題の難度を使います。平安はコース別（暗記＝基本、ペア・流れ＝標準、理由＝発展）です。新しい内容への書き換えはしません。１回は選んだ問題数まで、候補は最大10問です。</p>${rows.map(r=>`<details><summary>${esc(r.unit)}：${esc(promptOf(r.q,r.variant))}</summary><p>選んだ理由：${r.wrong}/${r.total}日で誤答・ヒントあり${r.hintCount}日。最後の回答：${esc(label(r.lastAt))}（${r.lastCorrect?'ヒント付き正解':'誤答'}）。難度${r.level}。${r.confusion?'同じペアの別の答えと一致しました。原因は未確定です。':''}</p><p>元問題：${esc(r.originId)} ／ 出典：${esc(r.q.source||'既存の平安単元問題')}</p><p>正解：${esc(expectedOf(r.q,r.variant))}</p><p>根拠：${esc(r.q.explanation)}</p></details>`).join('')||`<p>${esc(adaptiveStatus())}</p>`}<button data-mode="adaptive" ${rows.length?'':'disabled'}>追加練習をはじめる（候補${rows.length}問・今回${Math.min(rows.length,prefs.count)}問）</button></section>`;
}
// Bind after each home render; all content remains inside the standalone app.
const originalHome=home;
home=function(){originalHome();document.getElementById('adaptive-level').onchange=e=>{adaptiveLevel=e.target.value;home();};};
const originalParent=parent;
parent=function(){originalParent();main.insertAdjacentHTML('afterbegin',adaptiveSummary());};
