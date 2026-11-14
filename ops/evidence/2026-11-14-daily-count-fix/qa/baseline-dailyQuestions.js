function dailyQuestions(p=prefs){
 if(practiceUnavailable())return [];
 const result=[],seen=new Set();
 const push=q=>{const id=q.originId||q.id;if(!seen.has(id)){seen.add(id);result.push(q);}};
 dueReviews(p).forEach(s=>push(EXTRA.get(s.originId)));
 additional(p).forEach(s=>push(s.q));
 shuffle(candidates('normal',p)).forEach(push);
 return result.slice(0,p.count);
}