// Read-only adapter: individual science events only. Legacy aggregates are never
// projected. response stays numeric/string, grade and unit display stay original.
const Q=byId;
const data={get events(){return state.events.map(e=>({...e,at:e.answeredAt,hint:e.hintUsed,variant:'normal'}));}};
const order=es=>[...es].sort((a,b)=>a.at.localeCompare(b.at)||a.id.localeCompare(b.id));
const day=localDay;
const japanDay=iso=>localDay(iso,-540);
const REVIEW_INTERVAL_DAYS=Object.freeze([1,3,7]);
const addJapanDays=(d,n)=>new Date(Date.parse(d+'T00:00:00Z')+n*86400000).toISOString().slice(0,10);
MODES.daily='今日の5問';MODES.adaptive='弱点の復習';
let scienceUnit='all';
const SCIENCE_PREF_KEY=KEY+'-preferences-v1';
function rememberScience(){
 try{localStorage.setItem(SCIENCE_PREF_KEY,JSON.stringify({count,unit:scienceUnit}));localStorage.setItem('yuika-last-daily-unit-v1','yuika-review-v2.html');}
 catch{message('学習設定を保存できません。次回は初期設定になります。');}
}
try{const p=JSON.parse(localStorage.getItem(SCIENCE_PREF_KEY)||'null');if(p){if([5,10].includes(p.count))count=p.count;if(p.unit==='all'||UNITS.includes(p.unit))scienceUnit=p.unit;}}catch{message('学習設定を読み取れません。初期設定で始めます。');}
function scienceWeak(events=data.events,now=Date.now()){
 if(practiceUnavailable(events,now))return [];
 return practiceWeaknesses(events,now).filter(r=>scienceUnit==='all'||r.unit===scienceUnit).slice(0,10);
}
function scienceDue(events=data.events,now=Date.now()){
 if(practiceUnavailable(events,now))return [];
 const today=japanDay(new Date(now).toISOString());
 return retention(events,now).filter(s=>s.status==='waiting'&&s.due<=today&&(scienceUnit==='all'||Q.get(s.originId).unit===scienceUnit))
 .sort((a,b)=>a.due.localeCompare(b.due)||a.originId.localeCompare(b.originId));
}
function scienceDaily(){
 if(practiceUnavailable())return [];
 const qs=[],seen=new Set();
 const push=q=>{if(!seen.has(q.id)){seen.add(q.id);qs.push(q);}};
 scienceDue().forEach(s=>push(Q.get(s.originId)));
 scienceWeak().forEach(s=>push(Q.get(s.originId)));
 const normal=[...candidates('normal',scienceUnit)];
 for(let i=normal.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[normal[i],normal[j]]=[normal[j],normal[i]];}
 normal.forEach(push);return qs.slice(0,count);
}
const scienceStart=start;
start=function(mode,unit='all'){
 if(mode!=='daily'&&mode!=='adaptive'){scienceUnit=unit;rememberScience();scienceStart(mode,unit);return;}
 if(practiceUnavailable()){message(practiceClockIssue()?PRACTICE_CLOCK_NOTICE:'記録を保存・読み取りできないため、弱点の復習と今日の5問は休止しています。「記録の引きつぎ」で保管してください。');return;}
 const qs=mode==='daily'?scienceDaily():scienceWeak().slice(0,count).map(s=>Q.get(s.originId));
 if(!qs.length){message('今はこの練習の候補がありません。');return;}
 rememberScience();session={id:uid(),mode,questions:qs,index:0,results:[],hint:false,selected:null,answered:false,done:false};view='quiz';render();main.focus();window.scrollTo(0,0);
};
function scienceSummary(){
 if(practiceClockIssue())return '<section class="card" id="science-summary"><p>'+esc(PRACTICE_CLOCK_NOTICE)+'</p></section>';
 if(blocked||dirty)return '<section class="card" id="science-summary"><p>記録を読み取り・保存できないため弱点の判定を休止しています。記録の引きつぎで元データを保管してください。</p></section>';
 const states=retention(),today=japanDay(new Date().toISOString());
 return `<section class="card" id="science-summary"><h2>理科の弱点と再確認</h2><p>要確認 ${practiceWeaknesses().length}問 ／ 今日の再確認 ${states.filter(s=>s.status==='waiting'&&s.due<=today).length}問（期限超過を含む・全単元）／ 再確認待ち ${states.filter(s=>s.status==='waiting').length}問 ／ 定着 ${states.filter(s=>s.status==='retained').length}問</p><p>直近30日・最後の5回答日を日本時間で確認し、2日以上まちがえた問題を復習します。ヒントなし正解で再確認待ちへ。1・3・7日後の確認は仮の間隔です。期限前・ヒント付き正解では進まず、誤答で弱点に戻ります。定着は理解の保証ではありません。旧クイズの集計は分析に使いません。</p></section>`;
}
const scienceHome=home;
home=function(){
 scienceHome();
 document.getElementById('unit').value=scienceUnit;
 const rows=scienceWeak();
 main.insertAdjacentHTML('afterbegin',`<section class="card"><button id="daily-five" class="primary" ${practiceUnavailable()?'disabled':''}>今日の5問をはじめる（今回は${count}問）</button><p>期限の来た再確認 → 弱点の復習 → 通常問題。既存の47問を使います。下の単元と問題数を適用します。</p><p>今日の再確認：${scienceDue().length}問 ／ 弱点の復習：${rows.length}問</p><button id="science-adaptive" ${rows.length?'':'disabled'}>弱点の復習をはじめる</button>${rows.map(r=>`<details><summary>${esc(r.unit)}：${esc(Q.get(r.originId).prompt)}</summary><p>${r.wrong}/${r.total}日でまちがい・ヒントを見た日${r.hintCount}日。最後の回答：${esc(new Date(r.lastAt).toLocaleString('ja-JP',{timeZone:'Asia/Tokyo'}))}（日本時間）。原因は未確定です。</p></details>`).join('')}</section>`+scienceSummary());
 document.getElementById('daily-five').onclick=()=>start('daily');
 document.getElementById('science-adaptive').onclick=()=>start('adaptive');
 document.getElementById('unit').onchange=e=>{scienceUnit=e.target.value;rememberScience();home();document.getElementById('unit').focus();};
 main.querySelectorAll('[data-count]').forEach(b=>b.onclick=()=>{count=Number(b.dataset.count);rememberScience();home();});
};
const scienceAnalysis=analysis;
analysis=function(){scienceAnalysis();main.insertAdjacentHTML('afterbegin',scienceSummary());};

let practiceDisplayDay=japanDay(new Date().toISOString());
function refreshPracticeDate(force=false){
 const today=japanDay(new Date().toISOString()),changed=today!==practiceDisplayDay;
 practiceDisplayDay=today;
 if((force||changed)&&(view==='home'||view==='analysis'))render();
}
setInterval(()=>refreshPracticeDate(),30000);
window.addEventListener('focus',()=>refreshPracticeDate(true));
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshPracticeDate(true);});
