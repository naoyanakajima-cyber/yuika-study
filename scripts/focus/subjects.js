// Subject views share the complete durable store and revision archive.
// Filter projections and candidates, never the imported/exported event stream.
const focusSubject=new URLSearchParams(location.search).get('subject');
const FOCUS_SUBJECTS={social:'社会',science:'理科',math:'算数',japanese:'国語'};
const focusLabel=Object.hasOwn(FOCUS_SUBJECTS,focusSubject)?FOCUS_SUBJECTS[focusSubject]:null;
const focusQuestions=QUESTIONS.filter(q=>!focusLabel||q.subject===focusLabel);
UNITS=[...new Set(focusQuestions.map(q=>q.unit))];
const inFocus=q=>!!q&&(!focusLabel||q.subject===focusLabel);
const focusEvents=()=>data.events.filter(e=>inFocus(Q.get(e.questionId)));
const focusCandidates=candidates;
candidates=function(...args){return focusCandidates(...args).filter(inFocus);};
const focusGrouped=grouped;
grouped=function(events=data.events){return focusGrouped(events.filter(e=>inFocus(Q.get(e.questionId))));};
const focusWeaknesses=weaknesses;
weaknesses=function(...args){return focusWeaknesses(...args).filter(r=>inFocus(Q.get(r.originId)));};
const focusRetention=retention;
retention=function(...args){return focusRetention(...args).filter(r=>inFocus(Q.get(r.originId)));};
const focusHome=home;
home=function(){
 focusHome();
 if(focusLabel){
  main.querySelector('.hero h1').textContent='模試の弱点対策 '+focusLabel;
  main.querySelector('.hero p').textContent=focusLabel+'の重点分野を、ちがう聞き方で確かめよう。';
  main.querySelector('.hero .tag').textContent=focusQuestions.length+'問・根拠と解説つき';
 }
};
const focusRecords=records;
records=function(){focusRecords();main.querySelector('.note').insertAdjacentHTML('beforeend','<p>JSONは4教科すべての記録を保管します。分析用テキストは表示中の教科が対象です。</p>');};
// Keep per-subject preferences separate from the original mixed daily entry.
const focusRestore=restorePrefs,focusRemember=rememberPrefs;
const focusPrefKey=PREF_KEY+':'+focusSubject;
restorePrefs=function(){
 if(!focusLabel){focusRestore();return;}
 prefs={count:5,course:'all',unit:'all',variant:'normal'};
 try{const p=JSON.parse(window.YuikaParent.storage.getItem(focusPrefKey)||'null');if(!p)return;
  if([5,10,15].includes(p.count))prefs.count=p.count;
  if(Object.hasOwn(COURSES,p.course))prefs.course=p.course;
  if(UNITS.includes(p.unit))prefs.unit=p.unit;
 }catch{note('学習設定を読み取れません。初期設定で始めます。');}
};
rememberPrefs=function(){
 if(!focusLabel){focusRemember();return;}
 try{window.YuikaParent.storage.setItem(focusPrefKey,JSON.stringify(prefs));window.YuikaParent.storage.setItem('yuika-prototype-v1:last-daily-unit','mock-focus-review.html?subject='+focusSubject);}
 catch{note('学習設定を保存できません。次回起動時は初期設定になります。');}
};
restorePrefs();
