from pathlib import Path
import subprocess,json,re,hashlib,tarfile,io,tempfile,sys
R=Path('/workspace/qa-content-generator-checkout');O=Path('/workspace/qa-content-generator-evidence')
OLD='ee228ca0a1865d0a56f4302cd9342a4f66738561'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(b):return hashlib.sha256(b).hexdigest()
HEAD=git('rev-parse','HEAD').decode().strip()
def tree(rev):return {line.split('\t')[1]:line.split()[2] for line in git('ls-tree','-r',rev).decode().splitlines()}
o,h=tree(OLD),tree(HEAD)
assert not git('status','--porcelain','--untracked-files=no')
content_paths=[p for p in o if p=='content-review.html' or p.startswith('docs/product/fixtures/') or p.startswith('tests/content_') or p in ['docs/product/content-image-trial-spec.md','docs/product/content-import-guard-spec.md','docs/product/content-spec.md','docs/product/content-try-spec.md']]
assert all(o[p]==h[p] for p in content_paths)
science=(R/'yuika-review-v2.html').read_text()
assert git('show',OLD+':yuika-review-v2.html')==(R/'yuika-review-v2.html').read_bytes()
adapter=science.split('// SCIENCE_ADAPTIVE_START\n')[1].split('function weaknesses(')[0]
assert adapter==(R/'scripts/practice/science.js').read_text()+'\n'
runtime=(R/'scripts/prototype/runtime.js').read_text()
assert science.split('// PROTOTYPE_START\n')[1].split('// PROTOTYPE_END\n')[0]==runtime
assert 'function scienceDailySources' not in (R/'scripts/practice/science.js').read_text()
other=[]
for p in ['onin-review.html','kamakura-review.html','heian-review.html','mock-focus-review.html']:
 old=git('show',OLD+':'+p).decode();new=(R/p).read_text()
 a=old.splitlines();b=new.splitlines();assert len(a)==len(b)
 delta=[(x,y) for x,y in zip(a,b) if x!=y];assert len(delta)==1,(p,delta)
 x,y=delta[0];assert 'questionVersion' in x and 'answerUnit' not in x and 'answerTag' not in x
 assert y==x.replace("'explanation']:","'explanation','answerUnit','answerTag']:")
 assert "const prototypeScience=location.pathname.endsWith('yuika-review-v2.html');" in new
 assert 'const fields=prototypeScience?\n'+y in new
 assert new.split('// PROTOTYPE_START\n')[1].split('// PROTOTYPE_END\n')[0]==runtime
 other.append({'path':p,'changed_lines':1,'old':x,'new':y})
html=(R/'content-review.html').read_bytes();digest=sha(html)
for p in ['scripts/parent/embed.py','tests/parent_mode.py']:assert digest in (R/p).read_text()
suites=re.findall(r'^run (\S+)',(R/'scripts/check_all.sh').read_text(),re.M)
assert len(suites)==32 and len(set(suites))==32
old_suites=re.findall(r'^run (\S+)',git('show',OLD+':scripts/check_all.sh').decode(),re.M)
assert [x for x in suites if x!='tests/generator_preservation.py']==old_suites
# Independent two passes of actual generators on an archive copy.
generators=['scripts/practice/embed.py','scripts/practice/embed_science.py','scripts/history/embed.py','scripts/prototype/embed.py','scripts/design/build_summary.py','scripts/design/embed.py','scripts/parent/embed.py']
with tempfile.TemporaryDirectory(prefix='cycle191-qa-regeneration-') as d:
 isolated=Path(d)
 with tarfile.open(fileobj=io.BytesIO(git('archive',HEAD))) as t:t.extractall(isolated,filter='data')
 before={p:sha((isolated/p).read_bytes()) for p in h};passes=[]
 for attempt in [1,2]:
  results=[]
  for generator in generators:
   p=subprocess.run([sys.executable,generator],cwd=isolated,capture_output=True,text=True)
   results.append({'generator':generator,'exit':p.returncode});assert p.returncode==0,p.stderr
  actual={p:sha((isolated/p).read_bytes()) for p in h}
  assert actual==before, [p for p in h if actual[p]!=before[p]]
  passes.append({'attempt':attempt,'matches_original_all_tracked_bytes':True,'results':results})
# Transplant the identical test into the old PR11 tree, using only a disposable copy.
with tempfile.TemporaryDirectory(prefix='cycle191-qa-old-negative-') as d:
 isolated=Path(d)
 with tarfile.open(fileobj=io.BytesIO(git('archive',OLD))) as t:t.extractall(isolated,filter='data')
 (isolated/'tests/generator_preservation.py').write_bytes((R/'tests/generator_preservation.py').read_bytes())
 subprocess.run(['git','init','-q'],cwd=isolated,check=True)
 subprocess.run(['git','add','.'],cwd=isolated,check=True)
 p=subprocess.run([sys.executable,'tests/generator_preservation.py'],cwd=isolated,capture_output=True,text=True)
 (O/'old-pr11-generator-negative.log').write_text(p.stdout+p.stderr)
 assert p.returncode!=0 and 'Generator pass 1 changed tracked files' in p.stderr and 'yuika-review-v2.html' in p.stderr
 negative={'base':OLD,'exit':p.returncode,'expected_first_pass_failure':True}
assert not git('status','--porcelain','--untracked-files=no')
result={'head':HEAD,'base':OLD,'delta':git('diff','--name-only',OLD,HEAD).decode().splitlines(),'content_equal_paths':content_paths,'content_sha256':digest,'science_html_identical':True,'source_embedded_identity':True,'no_pr10_science_daily_sources':True,'other_html_one_line_only':other,'suite_count':len(suites),'passes':passes,'old_pr11_negative':negative,'source_tracked_checkout_clean':True}
(O/'static-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
