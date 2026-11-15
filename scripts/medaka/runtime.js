// Only the new recall questions use this UI. Existing grading and records stay intact.
const RECALL_LABELS={unaided:'自力で正解',assisted:'選択肢で正解',incorrect:'不正解'};
function medakaDiagram(q){
 const male=q.diagram.sex==='male';
 const fins=[['せびれ',345,45],['むなびれ',120,150],['はらびれ',230,215],['しりびれ',330,210],['おびれ',510,135]];
 return `<div style="overflow-x:auto"><svg id="medaka-diagram" viewBox="0 0 640 340" style="width:100%;min-width:320px;display:block" role="group" aria-label="${male?'オス':'メス'}のメダカの自作模式図。左が頭。ひれの位置を選べます。">
 <g fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round">
 <path d="M55 170 Q100 135 190 137 Q350 135 505 175 L505 200 Q330 235 165 224 Q92 215 55 170Z"/>
 <path d="M505 175 L590 140 L580 185 L590 235 L505 200Z"/>
 <path d="${male?'M355 140 L373 65 L415 63 L425 94 L438 70 L455 151':'M355 140 Q375 65 416 76 L455 151'}"/>
 <path d="${male?'M332 221 L352 300 L459 287 L447 217':'M332 221 L355 280 L447 217'}"/>
 <path d="M253 227 L283 274 L304 226 M155 175 Q204 192 160 226Z"/>
 <path d="M129 148 Q151 181 130 215"/><circle cx="91" cy="165" r="5"/>
 <path d="M513 183 L580 160 M513 190 L578 188 M513 197 L580 218 ${male?'M350 237 L359 283 M376 232 L384 280 M405 229 L413 277':'M347 234 L356 263 M370 233 L375 250 M400 229 L403 235'}"/>
 </g>${fins.map(([name,x,y],i)=>`<g role="button" tabindex="0" aria-label="ひれの位置 ${String.fromCharCode(65+i)}" aria-pressed="false" data-fin="${esc(name)}" style="cursor:pointer"><rect x="${x}" y="${y}" width="${name==='しりびれ'?135:name==='せびれ'?115:100}" height="${name==='せびれ'?115:100}" rx="8" fill="transparent" stroke="transparent" stroke-width="4"/></g>`).join('')}</svg></div><p class="muted">左が頭、右がお。形を見やすくした模式図です。左右一対のひれは片側を中心に示しています。</p>`;
}
const medakaQuiz=quiz;
quiz=function(){
 const s=session,q=s.questions[s.index];
 if(q.type!=='recall'){medakaQuiz();return;}
 // Local stage resets whenever a new question is rendered; no answer words in stage 1.
 s.recallStage='first';s.firstResponse=null;s.selected=null;
 main.innerHTML=`<div class="quiz"><button class="small" id="end">← いったんおしまい</button><p>${s.index+1} / ${s.questions.length}問</p><section class="card"><span class="tag">${esc(q.unit)}</span><h1 class="question">${esc(q.prompt)}</h1><p id="recall-instruction" tabindex="-1">まず選択肢なしで答えよう。</p><div id="recall-input">${q.diagram?medakaDiagram(q):'<label class="field" for="recall-text">思い出した答えを入力</label><input id="recall-text" type="text" autocomplete="off" maxlength="100" style="width:100%">'}</div><div id="answerError" class="error" role="alert"></div><div class="actions"><button class="primary" id="check">答え合わせ</button></div><div id="feedback" aria-live="polite"></div></section></div>`;
 main.querySelectorAll('[data-fin]').forEach(b=>{
  const choose=()=>{if(s.answered||s.recallStage!=='first')return;s.selected=b.dataset.fin;main.querySelectorAll('[data-fin]').forEach(x=>{const on=x===b;x.setAttribute('aria-pressed',String(on));x.querySelector('rect').setAttribute('stroke',on?'var(--subject)':'transparent');});};
  b.onclick=choose;b.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose();}};
 });
 document.getElementById('check').onclick=submit;
 const input=document.getElementById('recall-text');if(input)input.onkeydown=e=>{if(e.key==='Enter'&&!e.isComposing)submit();};
 document.getElementById('end').onclick=()=>navigate('home');
};
const medakaSubmit=submit;
submit=function(){
 const s=session;if(!s||s.answered)return;
 const q=s.questions[s.index];if(q.type!=='recall'){medakaSubmit();return;}
 const raw=s.recallStage==='choice'||q.diagram?s.selected:document.getElementById('recall-text').value;
 if(raw===null||!String(raw).trim()){document.getElementById('answerError').textContent=q.diagram&&s.recallStage==='first'?'ひれの位置をタップしてね。':'答えを入力するか、表示された選択肢を選んでね。';return;}
 if(s.recallStage==='first'&&!grade(q,raw)){
  s.firstResponse=raw;s.recallStage='choice';s.selected=null;
  document.getElementById('recall-instruction').textContent='もう一度、今度は選択肢から選ぼう。';
  document.getElementById('answerError').textContent='';
  document.getElementById('recall-input').innerHTML=`<p>最初の答え：${esc(raw)}</p><div class="stack">${q.options.map((o,i)=>`<button class="option" data-choice="${i}" aria-pressed="false">${esc(o)}</button>`).join('')}</div>`;
  main.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>{if(s.answered)return;s.selected=q.options[Number(b.dataset.choice)];main.querySelectorAll('[data-choice]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));});
  document.getElementById('recall-instruction').focus();return;
 }
 const correct=grade(q,raw),recallOutcome=correct?(s.recallStage==='first'?'unaided':'assisted'):'incorrect';
 const now=new Date(),firstResponse=s.recallStage==='first'?raw:s.firstResponse;
 const e=validateEvent({questionVersion:currentQuestionVersion(q),id:uid(),sessionId:s.id,questionId:q.id,datasetVersion:VERSION,unit:q.unit,type:q.type,question:q.prompt,response:raw,inputRaw:raw,expected:q.answer,correct,answeredAt:now.toISOString(),timezoneOffset:now.getTimezoneOffset(),localDay:localDay(now.toISOString(),now.getTimezoneOffset()),hintUsed:recallOutcome!=='unaided',mode:s.mode,explanation:q.explanation,recallOutcome,firstResponse});
 s.answered=true;state.events.push(e);s.results.push(e);const saved=persist();
 main.querySelectorAll('[data-choice],#recall-text,#check').forEach(b=>b.disabled=true);
 main.querySelectorAll('[data-fin]').forEach(b=>b.setAttribute('aria-disabled','true'));
 document.getElementById('feedback').innerHTML=`<div class="answerbox ${correct?'':'again'}"><h2>${RECALL_LABELS[recallOutcome]}</h2><p>最初の答え：${esc(firstResponse)}<br>最後の答え：${esc(raw)}<br>正しい答え：<b>${esc(q.answer)}</b></p><p>${esc(q.explanation)}</p><details><summary>根拠・解説</summary><p>${esc(q.basis)}</p><small>概念ID：${esc(q.conceptId)} ／ ${esc(q.source)}</small></details><p>${recallOutcome==='unaided'?'自分で思い出せました。':'自力で答えられるまで、再確認の対象に残ります。'}</p><small>${saved?'回答を保存しました':'回答は一時保持です。JSONを書き出してください。'}</small></div><button class="primary wide" id="next">${s.index+1===s.questions.length?'今回のふりかえり →':'次の問題へ →'}</button>`;
 document.getElementById('next').onclick=()=>{s.index++;if(s.index===s.questions.length){s.done=true;result();}else{s.answered=false;s.hint=false;s.selected=null;quiz();}main.focus();window.scrollTo(0,0);};
 document.getElementById('next').focus();
};
const medakaAnalysis=analysis;
analysis=function(){medakaAnalysis();const es=state.events.filter(e=>e.type==='recall');main.insertAdjacentHTML('afterbegin',`<section class="card"><h2>メダカ：思い出す力の記録</h2>${Object.entries(RECALL_LABELS).map(([k,label])=>`<p>${label}：${es.filter(e=>e.recallOutcome===k).length}回答</p>`).join('')}<p>選択肢での正解は自力の正解と分けています。自力で答えられるまで弱点・再確認に残り、その後は別の日にも確認します。</p></section>`);};
const medakaResult=result;
result=function(){medakaResult();if(session.results.some(e=>e.type==='recall'))main.insertAdjacentHTML('afterbegin',`<section class="card">${Object.entries(RECALL_LABELS).map(([k,label])=>`<p>${label}：${session.results.filter(e=>e.recallOutcome===k).length}問</p>`).join('')}</section>`);};
