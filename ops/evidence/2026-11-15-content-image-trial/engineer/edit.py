import json,hashlib
from pathlib import Path
f=Path('docs/product/fixtures')
p={'format':'yuika-content-proposal','schemaVersion':1,'packageId':'draft-synthetic-triangle-package','revision':1,'source':{'kind':'image','sourceId':'synthetic-triangle-source','label':'合成の教材図：三角形（OCRは実行していません）','locator':'synthetic-triangle-source.svg'},'transcription':{'text':'三角形の辺は［確認待ち］本です。','uncertainties':[{'id':'synthetic-triangle-uncertainty-001','quote':'［確認待ち］','candidates':['3','4'],'resolution':None}]},'unit':{'id':'draft-synthetic-triangle','title':'合成教材：三角形の辺'},'questions':[{'id':'draft-synthetic-triangle-sides-001','questionVersion':1,'type':'text','prompt':'この三角形の辺は何本ですか？ 数字で答えてください。','answer':'3','aliases':[],'readings':[],'options':[],'explanation':'三角形は3本の辺で囲まれた図形です。','hint':'まっすぐな線を1本ずつ数えよう。','sourceRefs':[{'sourceId':'synthetic-triangle-source','locator':'page:1;region:100,60,400,220'}],'generatedFields':['prompt','explanation','hint'],'status':'draft','confirmedRevision':None}]}
(f/'synthetic-triangle-content.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
samples=[json.loads((f/n).read_text()) for n in ['synthetic-content.json','synthetic-image-content.json','synthetic-triangle-content.json']]
assets=[]
for s in samples:
 src=s['source'];assets.append({k:src[k] for k in ['kind','sourceId','locator']}|{'content':(f/src['locator']).read_text(),'note':'この［確認待ち］は照合操作のために作った合成の転記案です。読取不能な原本やOCR結果ではありません。原本を見て転記と読み取りを直し、問題案を確認してください。' if src['sourceId']=='synthetic-triangle-source' else ''})
encode=lambda v:json.dumps(v,ensure_ascii=False).replace('<','\\u003c')
path=Path('content-review.html');s=path.read_text();lines=s.splitlines();lines=[('const SAMPLES='+encode(samples)+';') if l.startswith('const SAMPLES=') else ('const ASSETS='+encode(assets)+';') if l.startswith('const ASSETS=') else l for l in lines];s='\n'.join(lines)+'\n'
s=s.replace('<button id="sample-image">画像・判読不明の例</button>','<button id="sample-image">画像・判読不明の例</button><button id="sample-triangle">画像・読める図形の例</button>')
s=s.replace('return SAMPLES.find(s=>s.source.kind===p.source.kind&&s.source.sourceId===p.source.sourceId&&s.source.locator===p.source.locator);','return ASSETS.find(a=>a.kind===p.source.kind&&a.sourceId===p.source.sourceId&&a.locator===p.source.locator);')
s=s.replace("else if(asset.source.kind==='text')element('pre',ASSETS.text,preview);\n else preview.innerHTML=ASSETS.image; // Only this compile-time trusted SVG; never proposal text/URLs.","else if(asset.kind==='text')element('pre',asset.content,preview);\n else preview.innerHTML=asset.content; // Only compile-time trusted SVG selected by exact source triple; never proposal text/URLs.\n if(asset&&asset.note)element('p',asset.note,preview).className='note';")
s=s.replace("$('sample-image').onclick=()=>acceptProposal(SAMPLES[1]);","$('sample-image').onclick=()=>acceptProposal(SAMPLES[1]);$('sample-triangle').onclick=()=>acceptProposal(SAMPLES[2]);")
path.write_text(s)
h=hashlib.sha256(path.read_bytes()).hexdigest()
for name in ['scripts/parent/embed.py','tests/parent_mode.py']:
 q=Path(name);q.write_text(q.read_text().replace('fea62d048857059b8016f3a36061795bacb18acf160d1bdc0c9997d277abd001',h))
q=Path('tests/content_review.py');s=q.read_text();s=s.replace("IMAGE = json.loads((FIXTURES / 'synthetic-image-content.json').read_text())","IMAGE = json.loads((FIXTURES / 'synthetic-image-content.json').read_text())\nTRIANGLE = json.loads((FIXTURES / 'synthetic-triangle-content.json').read_text())")
s=s.replace("assert p.evaluate('SAMPLES') == [TEXT, IMAGE]\n                assert p.evaluate('ASSETS.text') == (FIXTURES / 'synthetic-source.txt').read_text()\n                assert p.evaluate('ASSETS.image') == (FIXTURES / 'synthetic-source.svg').read_text()","assert p.evaluate('SAMPLES') == [TEXT, IMAGE, TRIANGLE]\n                for sample in [TEXT, IMAGE, TRIANGLE]:\n                    asset = p.evaluate('(p)=>sourceAsset(p)', sample)\n                    assert {k: asset[k] for k in ('kind', 'sourceId', 'locator')} == {k: sample['source'][k] for k in ('kind', 'sourceId', 'locator')}\n                    assert asset['content'] == (FIXTURES / sample['source']['locator']).read_text()")
q.write_text(s)
q=Path('scripts/check_all.sh');s=q.read_text().replace('run tests/content_trial.py python tests/content_trial.py','run tests/content_trial.py python tests/content_trial.py\nrun tests/content_image_trial.py python tests/content_image_trial.py');q.write_text(s)
print(h)
