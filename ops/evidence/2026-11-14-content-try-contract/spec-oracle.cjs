'use strict';
const assert = require('node:assert/strict');
const N = s => s.normalize('NFKC').trim();
const cases = [
['G01','氷',['氷','こおり'],'match'],['G02','\u3000こおり\t',['氷','こおり'],'match'],
['G03','コオリ',['氷','こおり'],'miss'],['G04','こ おり',['氷','こおり'],'miss'],['G05','氷。',['氷','こおり'],'miss'],
['G06','ＡＢＣ',['ABC','A B'],'match'],['G07','abc',['ABC','A B'],'miss'],
['G08a','A\u3000B',['ABC','A B'],'match'],['G08b','A  B',['ABC','A B'],'miss'],
['G09','ｶﾞﾗｽ',['ガラス'],'match'],['G10a','',['氷'],'empty'],['G10b',' \t\u3000',['氷'],'empty'],
['G11a','x'.repeat(200),['氷'],'miss'],['G11b','x'.repeat(201),['氷'],'raw-limit'],
['G12','㍍'.repeat(51),['氷'],'normalized-limit'],
['B01','x'.repeat(200),['x'.repeat(200)],'match'],['B02',' '+'x'.repeat(200),['x'.repeat(200)],'raw-limit'],
['B03','😀'.repeat(100),['😀'.repeat(100)],'match'],['B04','😀'.repeat(101),['😀'.repeat(100)],'raw-limit'],
['B05','㍍'.repeat(50),['メートル'.repeat(50)],'match'],['B06','カ\u3099ラス',['ガラス'],'match'],
['B07','氷\u200b',['氷'],'miss'],['B08','A\tB',['A B'],'miss'],['B09','A\nB',['A B'],'miss'],
['B10',null,['氷'],'type'],['B11',1,['氷'],'type']
];
for (const [id,raw,candidates,expected] of cases) {
 const actual=typeof raw!=='string'?'type':raw.length>200?'raw-limit':N(raw).length===0?'empty':N(raw).length>200?'normalized-limit':candidates.some(c=>N(c)===N(raw))?'match':'miss';
 assert.equal(actual,expected,id);
}
const choiceCases=[[0,'match'],[1,'miss'],[null,'error'],[2,'error'],['東','error'],[0.5,'error'],[-1,'error'],['0','error']];
for (const [index,expected] of choiceCases) {
 const actual=!Number.isInteger(index)||index<0||index>=2?'error':['東','西'][index]==='東'?'match':'miss';
 assert.equal(actual,expected,'choice '+String(index));
}
const candidateCases=[['㍍'.repeat(51),false],['㍍'.repeat(50),true],['\u00a8',true],['\u3000',false]];
for(const [s,expected] of candidateCases) assert.equal(N(s).length>0&&N(s).length<=200,expected,'candidate normalized gate');
console.log(JSON.stringify({node:process.version,text:cases.length,choice:choiceCases.length,candidateNormalizedGate:candidateCases.length,total:cases.length+choiceCases.length+candidateCases.length,passed:true}));
