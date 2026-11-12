/* Presentation only: move existing controls; never write records or choose questions. */
(()=>{
'use strict';
const subjects={社会:['#E07B39','#A24E17','#FFF0E5'],理科:['#1F9A92','#146660','#E4F5F2'],算数:['#2C4A8A','#2C4A8A','#EAF0FC'],国語:['#6A3E8E','#6A3E8E','#F2EBF8'],すべて:['#232733','#232733','#EAECF2'],'4教科まとめ':['#232733','#232733','#EAECF2']};
const paths={book:'M4 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-3H4z M20 4h-4a3 3 0 0 0-3 3v14a4 4 0 0 1 4-3h3z',chart:'M4 20V10h4v10 M10 20V4h4v16 M16 20v-8h4v8',settings:'M4 7h16 M4 17h16 M8 4v6 M16 14v6',arrow:'M5 12h14 M13 6l6 6-6 6',back:'M19 12H5 M11 6l-6 6 6 6',check:'M5 12l4 4L19 6'};
function icon(name='book'){return `<svg class="line-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${paths[name]||paths.book}"/></svg>`;}
function node(tag,cls,text){const el=document.createElement(tag);el.className=cls||'';if(text)el.textContent=text;return el;}
function unitHome(main,info){
 const focused=document.activeElement?.id;
 const hero=main.querySelector('.hero');if(!hero)return;
 const header=document.querySelector('body>header');header.classList.add('unit-header');
 if(!header.querySelector('.design-home')){const link=node('a','design-home');link.href='index.html';link.innerHTML=icon('back')+'ホーム';header.prepend(link);}
 const record=header.querySelector('[data-view="records"]');record.textContent='きろく';
 const parent=header.querySelector('[data-view="parent"],[data-view="analysis"]');parent.hidden=true;
 main.classList.add('unit-main');hero.classList.add('unit-hero');hero.querySelector('br')?.replaceWith(document.createTextNode(' '));
 if(info.subject==='理科'&&info.code!=='mock-focus'){hero.querySelector('h1').textContent='溶解度・酸とアルカリ';hero.querySelector('p').textContent='水に溶ける量と、水溶液の性質を確かめよう。';}
 document.documentElement.dataset.subject=({社会:'social',理科:'science',算数:'math',国語:'japanese'}[info.subject]||'all');
 const eyebrow=hero.querySelector('.eyebrow');eyebrow.textContent=info.subject+' · '+info.code;
 const oldStats=main.querySelector('.stats');oldStats?.remove();
 const stats=node('div','stats');
 for(const [label,value] of [['できた数',`${info.correct}／${info.total}`],['今日の再確認',info.due],['にがて',info.weak]]){const s=node('div','stat');s.append(node('strong','',String(value)),node('span','',label));stats.append(s);}hero.after(stats);
 const start=main.querySelector('#start'),practice=start.closest('.card');practice.classList.add('practice-card');practice.querySelector('h2').textContent='れんしゅう';
 const chips=practice.querySelector('.chips');practice.querySelectorAll('p,.eyebrow').forEach(el=>el.remove());
 const options=node('div','practice-options');practice.querySelectorAll('.field').forEach(el=>{if(!el.contains(chips))options.append(el);});
 practice.querySelectorAll('.field').forEach(el=>{if(el.contains(chips))el.replaceWith(chips);});
 practice.querySelector('h2').after(chips);chips.after(options);
 // Only expose methods backed by an existing control.
 const methods=node('section','other-methods');methods.append(node('h2','','ほかのやり方'));
 function row(control,label){if(!control)return;const r=control;r.classList.add('method-row');const count=r.querySelector('b')?.cloneNode(true);if(label)r.innerHTML='<span class="method-heading">'+icon()+label+'</span>'+icon('arrow');if(count)r.append(count);methods.append(r);}
 const daily=main.querySelector('#daily-five');row(daily);
 row(main.querySelector('#science-adaptive'),'にがての練習');
 for(const b of main.querySelectorAll('[data-mode]')){const labels={wrong:'まちがえた問題の復習',unseen:'まだ答えていない問題',spaced:'日をあけて思い出す',hint:'ヒントなしで確認',adaptive:'にがての練習'};row(b,labels[b.dataset.mode]);}
 const variant=main.querySelector('#variant');if(variant)for(const opt of variant.options){if(opt.value==='normal')continue;const b=node('button','',opt.value==='kanji'?'漢字・正式名の確認':'読みの確認');b.type='button';b.onclick=()=>{variant.value=opt.value;variant.dispatchEvent(new Event('change'));document.getElementById('start').focus();};row(b);}
 stats.after(practice);practice.after(methods);main.prepend(hero,stats,practice,methods);
 // Keep original diagrams/tables and all detailed learning controls available.
 const adaptive=main.querySelector('#adaptive');if(adaptive){const details=node('details','source-notes');details.open=true;details.append(node('summary','','にがての練習のくわしい設定'));adaptive.replaceWith(details);details.append(adaptive);}
 for(const el of Array.from(main.children)){
  if(el===hero||el===stats||el===practice||el===methods)continue;
  if(el.classList.contains('layout')){el.querySelectorAll('.green-card').forEach(c=>c.remove());if(!el.textContent.trim())el.remove();continue;}
  if(el.contains(practice)||el.querySelector('svg[role="img"],table'))continue;
  if(el.matches('section.card')&&!el.querySelector('button,input,select')){const d=node('details','source-notes');d.append(node('summary','','学習のくわしい説明'));el.replaceWith(d);d.append(el);}
 }
 const footer=document.querySelector('body>.footer,body>.unit-footer');footer.className='unit-footer';footer.replaceChildren(node('span','',info.code));const link=node('a','','保護者のノート');link.href='#parent';link.onclick=e=>{e.preventDefault();parent.click();};footer.append(link);
 if(focused)document.getElementById(focused)?.focus({preventScroll:true});
}
window.YuikaDesign={subjects,icon,unitHome};
})();
