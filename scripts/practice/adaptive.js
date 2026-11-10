// Embedded by embed.py. v1 IDs and prompts are durable record contracts.
const EXTRA=new Map();
for(const q of QUESTIONS){
 const extra={...q,id:q.id+'-review-v1',originId:q.id,prompt:'復習：'+q.prompt};
 EXTRA.set(q.id,extra);Q.set(extra.id,extra);
}
MODES.adaptive='弱点に合わせた追加練習';
function weaknesses(events=data.events,now=Date.now()){
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
  const wrong=samples.filter(e=>!e.correct).length;
  if(samples.length<2||wrong<2||last.correct)continue;
  const q=Q.get(last.questionId),origin=Q.get(q.originId||q.id);
  const confusion=QUESTIONS.filter(o=>o.id!==origin.id&&o.pair&&o.pair===origin.pair)
   .some(o=>grade(o,last.response,last.variant));
  rows.push({originId:origin.id,unit:origin.unit,variant:last.variant,wrong,total:samples.length,
   hintCount:samples.filter(e=>e.hint).length,lastAt:last.at,confusion});
 }
 return rows.sort((a,b)=>b.wrong/b.total-a.wrong/a.total||b.lastAt.localeCompare(a.lastAt)||a.originId.localeCompare(b.originId)||a.variant.localeCompare(b.variant));
}
function additional(p=prefs,events=data.events,now=Date.now()){
 return weaknesses(events,now).filter(r=>r.variant===p.variant).map(r=>({...r,q:EXTRA.get(r.originId)}))
  .filter(r=>(p.unit==='all'||r.q.unit===p.unit)&&(p.course==='all'||r.q.course===p.course)&&fits(r.q,p.variant)).slice(0,10);
}
function adaptivePanel(){
 const rows=additional();
 return `<section class="card" id="adaptive"><h2>弱点に合わせた追加練習</h2><p>直近30日・別日の最後の回答（最大5日）のうち、2日以上誤答し、最後も誤答の論点を復習します。確認方法は別集計です。少数の記録から苦手や原因を断定しません。</p>${rows.map(r=>`<details><summary>${esc(r.unit)}：${esc(promptOf(r.q,r.variant))}</summary><p>${r.wrong}/${r.total}日で誤答・ヒントあり${r.hintCount}日。${r.confusion?'同じペアの別の答えと一致しました。原因は未確定です。':''}</p><p>元問題：${esc(r.originId)} ／ 出典：${esc(r.q.source)}</p><p>正解：${esc(expectedOf(r.q,r.variant))}</p><p>根拠：${esc(r.q.explanation)}</p></details>`).join('')||'<p>この条件の追加課題はまだありません。</p>'}<button data-mode="adaptive" ${rows.length?'':'disabled'}>追加練習をはじめる（${rows.length}問）</button></section>`;
}
