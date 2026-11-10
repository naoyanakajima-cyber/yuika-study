// Dataset versions/keys retain their existing meaning; revisions are per question.
function currentQuestionVersion(q){
 const id=q.originId||q.id;
 return QUESTION_REVISIONS[id].at(-1).revision;
}
function historicalQuestion(e){
 const science=typeof byId!=='undefined';
 const extra=!science&&e.questionId.endsWith('-review-v1');
 const id=extra?e.questionId.slice(0,-10):e.questionId;
 const records=QUESTION_REVISIONS[id]||[];
 const matches=[];
 for(const r of records){
  if(Object.hasOwn(e,'questionVersion')&&e.questionVersion!==r.revision)continue;
  const q=extra?{...r.question,id:e.questionId,originId:id,prompt:'復習：'+r.question.prompt}:r.question;
  const prompt=science?q.prompt:typeof promptOf==='function'?promptOf(q,e.variant):q.prompt;
  const expected=science?q.answer:typeof expectedOf==='function'?expectedOf(q,e.variant):q.answer;
  if(e.unit===q.unit&&(science?e.type===q.type:e.course===q.course)&&e.question===prompt&&e.expected===expected&&e.explanation===q.explanation)matches.push(q);
 }
 // Versionless histories can match multiple spelling revisions. Select the one
 // whose historical grade matches, without recalculating or rewriting the event.
 return matches.find(q=>e.correct===grade(q,e.response,e.variant));
}
