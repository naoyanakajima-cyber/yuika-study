// Draft-only records are isolated from the original application's storage.
const PROTOTYPE_FORMAT='yuika-review-prototype';
const prototypeScience=typeof byId!=='undefined';
const prototypeHeian=VERSION==='heian-540-24-v1';
let rejectedImportRaw=null;
function prototypeCheck(ok,message){if(!ok)throw Error(message);}
function prototypeFields(value,allowed){
 prototypeCheck(value&&typeof value==='object'&&!Array.isArray(value),'記録の形式が不正です。');
 prototypeCheck(Object.keys(value).every(k=>allowed.includes(k)),'未対応の項目があります。元ファイルを保管してください。');
}
const prototypeEventValidator=validateEvent;
validateEvent=function(e){
 const fields=prototypeScience?
  ['questionVersion','id','sessionId','questionId','datasetVersion','unit','type','question','response','inputRaw','expected','correct','answeredAt','timezoneOffset','localDay','hintUsed','mode','explanation']:
  ['questionVersion','id','sessionId','questionId','version','unit','course','question','response','expected','explanation','correct','variant','mode','hint','at','offset','day',...(prototypeHeian?['reflection']:['unitId'])];
 prototypeFields(e,fields);
 if(prototypeHeian&&e.response&&typeof e.response==='object')prototypeFields(e.response,['steps','fills']);
 return prototypeEventValidator(e);
};
function prototypeStateFields(v){
 prototypeFields(v,['schemaVersion','datasetVersion','events','exportedAt',...(prototypeScience?['legacy']:[])]);
 if(prototypeScience&&Array.isArray(v.legacy))for(const item of v.legacy)prototypeFields(item,['raw','capturedAt']);
}
if(prototypeScience){
 const original=validateState;
 validateState=function(v){prototypeStateFields(v);return original(v);};
}else{
 const original=validate;
 validate=function(v){prototypeStateFields(v);return original(v);};
}
function prototypePacket(payload){return {format:PROTOTYPE_FORMAT,formatVersion:1,datasetVersion:VERSION,payload,exportedAt:new Date().toISOString()};}
function prototypeUnpack(v){
 if(v&&Object.hasOwn(v,'format')){
  prototypeFields(v,['format','formatVersion','datasetVersion','payload','exportedAt']);
  prototypeCheck(v.format===PROTOTYPE_FORMAT&&v.formatVersion===1&&v.datasetVersion===VERSION,'別の試作・版のJSONです。元ファイルを保管してください。');
  return v.payload;
 }
 return v; // Only the existing strict legacy validator can accept this branch.
}
function prototypeNotice(){
 let old='元の回答は自動で取り込まず、試作の記録は空から始まります。';
 try{const raw=window.YuikaParent.storage.getItem(LEGACY_KEY);if(raw!==null){old='元の保存先に記録があります。自動では取り込まず、試作の履歴とは別に保管しています。';try{JSON.parse(raw);}catch{old='元の保存先のJSONは読み取れません。元データは変更せず、この試作とは別に保護しています。';}}}
 catch{old='元の保存先を確認できません。変更はしていません。';}
 return `<section class="note" id="prototype-notice"><strong>合成データで試す復習</strong><p>この試作の回答・設定は元のアプリと別に保存します。旧画面には試作の回答は表示されません。</p><p>${old}</p><p>追加練習の試作用JSONは旧版へ取り込めません。既に混在した元記録の復旧は行いません。</p>${blocked?'<p>試作の記録を読み取れないため、分析と保存を休止しています。元データを書き出してください。</p>':''}</section>`;
}
const prototypeHome=home;
home=function(){prototypeHome();main.insertAdjacentHTML('afterbegin',prototypeNotice());};
const prototypeRecords=records;
records=function(){
 prototypeRecords();main.insertAdjacentHTML('afterbegin',prototypeNotice());
 main.insertAdjacentHTML('beforeend',`<section class="card"><h2>元データをそのまま保管</h2><p>読み取れない・旧版で開けない記録も変換しません。合成データだけを明示的に取り込んで試してください。</p><button id="prototype-original">元の回答データを保存</button>${rejectedImportRaw!==null?'<button id="prototype-rejected">取り込めなかったファイルを保存</button>':''}</section>`);
 document.getElementById('prototype-original').onclick=()=>{
  try{const raw=window.YuikaParent.storage.getItem(LEGACY_KEY);prototypeCheck(raw!==null,'元の回答データはこの場所にありません。');download('yuika-original-unchanged.json',raw);}
  catch(e){(prototypeScience?message:note)(e.message);}
 };
 if(rejectedImportRaw!==null)document.getElementById('prototype-rejected').onclick=()=>download('yuika-rejected-original.json',rejectedImportRaw);
};
importFile=async function(file){
 if(!file)return;
 let raw=null;
 try{
  prototypeCheck(file.size<=(prototypeScience?10000000:25000000),'JSONのサイズが上限を超えています。');
  raw=await file.text();const value=JSON.parse(raw),v=prototypeUnpack(value);let incoming;
  if(prototypeScience&&v&&Object.hasOwn(v,'attempts')&&!Object.hasOwn(value,'format')){
   // Explicit legacy aggregate import only; never infer individual responses.
   prototypeFields(v,['attempts','correct','wrong']);legacyData(raw);incoming=emptyState();incoming.legacy=[{raw,capturedAt:new Date().toISOString()}];
  }else incoming=prototypeScience?validateState(v):validate(v);
  prototypeCheck(!blocked,'試作の保存済み記録が読み取れません。先に元データを保管してください。');
  const diskRaw=window.YuikaParent.storage.getItem(KEY),disk=diskRaw!==null?(prototypeScience?validateState(JSON.parse(diskRaw)):validate(JSON.parse(diskRaw))):(prototypeScience?emptyState():empty());
  const next=merge(merge(disk,prototypeScience?state:data),incoming);
  // Commit only after complete validation and a successful atomic setItem.
  window.YuikaParent.storage.setItem(KEY,JSON.stringify(next));
  if(prototypeScience)state=next;else data=next;
  dirty=false;rejectedImportRaw=null;
  (prototypeScience?message:note)('試作へ読み込みました。同じ回答IDは重複させず、元の保存先は変更していません。');records();
 }catch(e){
  rejectedImportRaw=raw;(prototypeScience?message:note)('読み込みを中止しました。保存済み記録は変更していません。'+e.message);records();
 }
};
