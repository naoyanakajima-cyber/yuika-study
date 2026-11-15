from pathlib import Path
import subprocess,json,re,hashlib,tempfile,tarfile,io,sys,xml.etree.ElementTree as ET
R=Path('/workspace/yuika-content-image-trial-20261115');O=Path('/tmp/yuika-cycle34-qa');BASE='d75a5469fbf1e8c5011a6307308546e5ec669ceb'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def old(p):return git('show',BASE+':'+p)
head=git('rev-parse','HEAD').decode().strip();assert head==sys.argv[1];assert not git('status','--porcelain')
paths=git('ls-tree','-r','--name-only',BASE).decode().splitlines();stable=[p for p in paths if (p.endswith('.html') and '/' not in p and p!='content-review.html') or p.startswith(('assets/','scripts/practice/','scripts/history/','notifications/')) or p in ['scripts/parent/runtime.js','scripts/cloud/serve.py'] or p.startswith('docs/product/fixtures/')]
for p in stable:assert old(p)==(R/p).read_bytes(),p
before=old('content-review.html').decode();html=(R/'content-review.html').read_text();csp=lambda s:re.search(r'<meta http-equiv="Content-Security-Policy"[^>]+>',s).group();assert csp(before)==csp(html)
assert html[html.index('function validateShape'):html.index('function sourceAsset')]==before[before.index('function validateShape'):before.index('function sourceAsset')]
assert html[html.index('function trialReady'):]==before[before.index('function trialReady'):], 'trial engine changed'
for forbidden in ['localStorage','sessionStorage','indexedDB','Storage','cookie','YuikaParent','YuikaReports','YUIKA_PARENT_BEGIN','fetch(','XMLHttpRequest','sendBeacon','WebSocket','eval(']:assert forbidden not in html,forbidden
assert not re.search(r'<script\b[^>]*\bsrc\s*=',html,re.I)
h=hashlib.sha256((R/'content-review.html').read_bytes()).hexdigest()
for p in ['scripts/parent/embed.py','tests/parent_mode.py']:
 text=(R/p).read_text();assert h in text
 norm=lambda s:re.sub(r'[0-9a-f]{64}','HASH','\n'.join(x for x in s.splitlines() if not x.lstrip().startswith('#')))
 assert norm(text)==norm(old(p).decode()),p
suites=lambda s:re.findall(r'^run (\S+)',s,re.M);prev=suites(old('scripts/check_all.sh').decode());now=suites((R/'scripts/check_all.sh').read_text());assert len(now)==len(set(now)) and set(now)==set(prev)|{'tests/content_image_trial.py'}
p=R/'docs/product/fixtures/synthetic-triangle-source.svg';svg=ET.fromstring(p.read_text());allowed={'svg','title','desc','rect','g','polygon','line','path','text','tspan'}
for e in svg.iter():
 assert e.tag.split('}')[-1] in allowed,e.tag
 for k,v in e.attrib.items():assert not k.lower().startswith('on') and k.split('}')[-1] not in ['href','src'] and 'url(' not in v,(k,v)
assert svg.find('{http://www.w3.org/2000/svg}title') is not None and svg.find('{http://www.w3.org/2000/svg}desc') is not None
q=json.loads((R/'docs/product/fixtures/synthetic-triangle-content.json').read_text());assert q['schemaVersion']==1 and len(q['questions'])==1;question=q['questions'][0];assert question['status']=='draft' and question['confirmedRevision'] is None and question['answer']=='3';u=q['transcription']['uncertainties'];assert len(u)==1 and u[0]['resolution'] is None and u[0]['candidates']==['3','4'];assert question['aliases']==question['readings']==question['options']==[]
ref=question['sourceRefs'][0];m=re.fullmatch(r'page:1;region:(\d+),(\d+),(\d+),(\d+)',ref['locator']);assert m;rect=tuple(map(int,m.groups()));vb=list(map(float,svg.attrib['viewBox'].split()));assert rect[0]>=0 and rect[1]>=0 and rect[2]>0 and rect[3]>0 and rect[0]+rect[2]<=vb[2] and rect[1]+rect[3]<=vb[3]
archive=git('archive',head);d=Path(tempfile.mkdtemp(prefix='yuika-cycle34-isolated-',dir='/tmp'))
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(d,filter='data')
def preflight():
 code=(d/'tests/parent_mode.py').read_text().split('class Quiet(')[0]
 return subprocess.run([sys.executable,'-c','__file__='+repr(str(d/'tests/parent_mode.py'))+'\n'+code],capture_output=True,text=True)
assert preflight().returncode==0
(d/'unknown.html').write_text('<!doctype html><title>Synthetic unguarded page</title>');p=preflight();assert p.returncode!=0 and 'unknown.html' in p.stderr;(O/'unknown-preflight.log').write_text(p.stderr);(d/'unknown.html').unlink()
f=d/'content-review.html';f.write_text(f.read_text()+'\n<!-- synthetic tamper -->\n');beforefiles={p.name:p.read_bytes() for p in d.glob('*.html')};p=subprocess.run([sys.executable,str(d/'scripts/parent/embed.py')],capture_output=True,text=True);assert p.returncode!=0 and 'AssertionError' in p.stderr;assert beforefiles=={p.name:p.read_bytes() for p in d.glob('*.html')};(O/'modified-generator.log').write_text(p.stderr);p=preflight();assert p.returncode!=0;(O/'modified-preflight.log').write_text(p.stderr)
result={'head':head,'base':BASE,'unchanged_main_and_old_fixtures':stable,'suite_count':len(now),'suites':now,'content_sha256':h,'csp_unchanged':True,'validation_shape_unchanged':True,'trial_engine_unchanged':True,'guard_changes_hash_only':True,'source_ref_region':rect,'svg_viewbox':vb,'svg_safe_elements_attributes':True,'fixture_draft_unresolved':True,'negative_guards_pass':True};(O/'static-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
