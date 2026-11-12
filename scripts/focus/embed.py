"""Build the offline focus unit using the existing social quiz engine.
Run this before practice/embed.py, history/embed.py and prototype/embed.py.
The question file is the editable source; generated HTML stays self-contained.
"""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
qs=json.loads((ROOT/'scripts/focus/questions.json').read_text())
text=(ROOT/'kamakura-review.html').read_text()
# Notification integration is deliberately absent from this new mixed-subject unit.
text=re.sub(r'<!-- YUIKA_REPORTS_BEGIN -->.*?<!-- YUIKA_REPORTS_END -->','',text,flags=re.S)
for section in ('ADAPTIVE','HISTORY','PROTOTYPE'):
 text=re.sub(r'// '+section+r'_START\n.*?// '+section+r'_END\n','',text,flags=re.S)
text=re.sub(r'const QUESTIONS=\[.*?\n\];',lambda _: 'const QUESTIONS='+json.dumps(qs,ensure_ascii=False,indent=2)+';',text,flags=re.S)
text=text.replace("VERSION='kamakura-540-25-v1',LEGACY_KEY='yuika-social-540-25-v1'","VERSION='mock-focus-v1',LEGACY_KEY='study-mock-focus-v1'").replace("UNIT_ID='sapix-540-25'","UNIT_ID='mock-focus'")
text=re.sub(r'const UNITS=\[.*?\];',lambda _: 'const UNITS='+json.dumps(list(dict.fromkeys(q['unit'] for q in qs)),ensure_ascii=False)+';',text)
text=text.replace("const VARIANTS={normal:'通常練習',kanji:'漢字・正式名',yomi:'読み'};","const VARIANTS={normal:'通常練習'};")
text=text.replace("d1:'用語確認（難度1）',d2:'理由・比較（難度2）',d3:'つながり（難度3）'","d1:'基本',d2:'理由・資料',d3:'発展'")
start=text.index('const ORG=')
end=text.index('function pick(',start)
text=text[:start]+'''function focusMaterial(q){
 let out='';
 if(q.table){const t=q.table;out+=`<div class="tablewrap"><table><caption>${esc(t.caption)}</caption><thead><tr>${t.headers.map(v=>`<th scope="col">${esc(v)}</th>`).join('')}</tr></thead><tbody>${t.rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;}
 if(q.passage)out+=`<section class="note" aria-label="説明文"><p>${esc(q.passage.caption)}</p>${q.passage.paragraphs.map(v=>`<p>${esc(v)}</p>`).join('')}</section>`;
 if(q.diagram){const d=q.diagram;out+=`<figure><figcaption>${esc(d.caption)}</figcaption>`;
 if(d.kind==='wind')out+=`<svg viewBox="0 0 280 240" role="img" aria-label="上が北、右が東。中心の東側で北向き、西側で南向き、北側で西向き、南側で東向きに風がふく模式図。"><text x="130" y="18">北</text><text x="252" y="126">東</text><circle cx="140" cy="120" r="70" fill="none" stroke="#64736e"/><text x="124" y="125">中心</text><text x="198" y="125" font-size="28">↑</text><text x="56" y="125" font-size="28">↓</text><text x="128" y="58" font-size="28">←</text><text x="128" y="201" font-size="28">→</text></svg>`;
 else if(d.kind==='bar')out+=`<pre>${d.lines.map(esc).join('\\n')}</pre>`;
 else out+=`<svg viewBox="0 0 280 240" role="img" aria-label="中心Oから円周上のAとBを結んだ三角形。OAとOBは半径。"><circle cx="140" cy="120" r="95" fill="none" stroke="#64736e" stroke-width="2"/><path d="M140 120 L57.7276 167.5 L222.2724 167.5 Z" fill="#eaf1e9" stroke="#386455" stroke-width="2"/><text x="132" y="112">O</text><text x="40" y="184">A</text><text x="226" y="184">B</text></svg>`;
 out+='</figure>';}
 return out;
}
function home(){
 const n=QUESTIONS.length;
 main.innerHTML=`<section class="hero"><div><div class="eyebrow">ORIGINAL PRACTICE</div><h1>模試の弱点対策</h1><p>社会・理科・算数・国語の重点分野を、ちがう聞き方で確かめよう。</p><span class="tag">${n}問・根拠と解説つき</span></div></section><section class="card"><h2>今日のチャレンジ</h2><label class="field">コース<select id="course">${Object.entries(COURSES).map(([k,v])=>`<option value="${k}" ${prefs.course===k?'selected':''}>${v}</option>`).join('')}</select></label><label class="field">重点分野<select id="unit"><option value="all">ぜんぶ</option>${UNITS.map(u=>`<option ${prefs.unit===u?'selected':''}>${u}</option>`).join('')}</select></label><div class="chips">${[5,10,15].map(c=>`<button data-count="${c}" aria-pressed="${prefs.count===c}">${c}問</button>`).join('')}</div><button id="start" class="primary wide">チャレンジをはじめる →</button><p>候補 ${candidates('normal').length}問。分野の問題が少ないときは、その数で始めます。</p>${[['unseen','まだ答えていない問題'],['wrong','もう一度やってみよう'],['hint','ヒントなしでできるかな']].map(([m,t])=>`<button class="review" data-mode="${m}" ${candidates(m).length?'':'disabled'}>${t}<b>${candidates(m).length}問</b></button>`).join('')}</section><details><summary>問題について</summary><p>教科書の基本的な知識で解けるオリジナル問題です。模試の文章や図表は使っていません。資料の数値は架空の例です。問題データは重点分野のラベルだけを持ち、個人の分析記録は含みません。</p><p>算数と国語も選択式で確かめます。弱点分析はこの単元で答えた問題ごとに行い、同じ概念IDの別問題は別々に記録します。</p></details>`;
 main.insertAdjacentHTML('beforeend',adaptivePanel());
 for(const id of ['course','unit'])document.getElementById(id).onchange=e=>{prefs[id]=e.target.value;home();};
 main.querySelectorAll('[data-count]').forEach(b=>b.onclick=()=>{prefs.count=Number(b.dataset.count);home();});
 document.getElementById('start').onclick=()=>start('normal');
 main.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>start(b.dataset.mode));
}
''' +text[end:]
text=text.replace('<h1 class="question">${esc(promptOf(q,v))}</h1>','<h1 class="question">${esc(promptOf(q,v))}</h1>${focusMaterial(q)}')
text=text.replace('<p>③ 覚え方：${esc(q.pitfall)}</p>','<p>③ 考え方・根拠：${esc(q.basis)}</p>')
# Remove the inherited completion report; no outbound code is included.
text=re.sub(r'window.YuikaReports.enqueue\(.*?\);main.innerHTML=', 'main.innerHTML=',text)
text=text.replace('connect-src https://*.workers.dev','connect-src \'none\'')
text=text.replace('ゆいかの社会','学習ノート').replace('社会ノート','学習ノート').replace('ゆいか','みんな')
text=text.replace('鎌倉幕府の成立','模試の弱点対策').replace('540-25','重点分野').replace('kamakura','mock-focus')
text=text.replace('自動メールに接続した場合だけ、チャレンジ結果を送信サーバー経由で保護者へ送ります。','')
text=text.replace('yuika-prototype-social-重点分野-', 'study-prototype-mock-focus-')
text=text.replace('記録はブラウザー内。メール通知は接続後のみ。','記録はブラウザー内に保存します。')
text=text.replace('通常練習・漢字確認・読み確認を別に扱います。','選択式の通常練習を記録します。')
text=text.replace('学習ノートノート','学習ノート').replace('<span>ゆ</span>','<span>学</span>').replace('おつかれさま、みんな！','おつかれさま！')
(ROOT/'mock-focus-review.html').write_text(text)
