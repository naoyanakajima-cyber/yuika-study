const output=[];
for(const count of [5,10,15])for(const size of [0,1,4,5,9,10,14,15]){
const prefs={count};const pool=Array.from({length:size},(_,i)=>({id:'synthetic-'+i,originId:'synthetic-'+i}));const EXTRA=new Map(pool.map(q=>[q.id,q])); const practiceUnavailable=()=>false; const dueReviews=()=>pool.slice(0,2).map(q=>({originId:q.id})); const additional=()=>pool.slice(0,3).map(q=>({q})); const candidates=()=>pool; const shuffle=x=>x;
function dailyQuestions(p=prefs){
 if(practiceUnavailable())return [];
 const result=[],seen=new Set();
 const push=q=>{const id=q.originId||q.id;if(!seen.has(id)){seen.add(id);result.push(q);}};
 dueReviews(p).forEach(s=>push(EXTRA.get(s.originId)));
 additional(p).forEach(s=>push(s.q));
 shuffle(candidates('normal',p)).forEach(push);
 return result.slice(0,p.count);
}
const result=dailyQuestions(); if(result.length!==Math.min(count,size)||new Set(result.map(q=>q.originId)).size!==result.length)throw Error('count/unique'); output.push({selected:count,candidates:size,label:count,actual:result.length,ids:result.map(q=>q.id)});}
console.log(JSON.stringify({sourceCommit:"86514eda054a5a2e09204df3a0668e40624c16de",sourcePath:'scripts/practice/adaptive.js',sourceSha256:"aa82eca8636be227d3bcaf1f0004004d74b55ec8ec325e4cfd8300e74811eac9",extractedFunctionSha256:"d6376c8ec43d06ffff041973720c3429ac93fd767c5d20a51d5c642a32eb4e9f",limits:'Synthetic dependencies; no browser, storage, real candidate reachability or full algorithm validation',cases:output},null,2));
