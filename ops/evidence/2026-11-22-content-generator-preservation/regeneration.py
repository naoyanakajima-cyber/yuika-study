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
result={'head':HEAD,'base':OLD,'passes':passes,'old_pr11_negative':negative,'source_tracked_checkout_clean':True}
(O/'regeneration-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
