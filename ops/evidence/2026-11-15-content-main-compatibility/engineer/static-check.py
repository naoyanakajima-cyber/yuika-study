import hashlib,json,re,subprocess,tempfile,shutil
from pathlib import Path
root=Path.cwd(); main='60d1a946cc02ed8acea54c0d7af7d6451fcc30ec';old='ee51e68d7e1eeb21bd0e959ec58166a869947d0a'
def show(ref,p):return subprocess.check_output(['git','show',f'{ref}:{p}'])
def paths(ref):return subprocess.check_output(['git','ls-tree','-r','--name-only',ref],text=True).splitlines()
shared={'README.md','docs/codex-cloud.md','scripts/check_all.sh','scripts/cloud/serve.py','scripts/parent/embed.py','tests/cloud_preview.py','tests/parent_mode.py'}
mainpaths=[p for p in paths(main) if p not in shared]
for p in mainpaths:assert (root/p).read_bytes()==show(main,p),p
content=[p for p in paths(old) if p=='content-review.html' or p.startswith('docs/product/content') or p.startswith('docs/product/fixtures/') or p.startswith('tests/content_')]
for p in content:assert(root/p).read_bytes()==show(old,p),p
getruns=lambda s:re.findall(r'^run (.+)$',s,re.M)
runs=getruns((root/'scripts/check_all.sh').read_text());expected=set(getruns(show(main,'scripts/check_all.sh').decode()))|set(getruns(show(old,'scripts/check_all.sh').decode()))
assert len(runs)==29 and len(set(runs))==29 and set(runs)==expected
with tempfile.TemporaryDirectory(prefix='yuika-cycle33-generator-') as td:
 clone=Path(td)
 for p in set(paths(main))|set(paths(old)):
  if (root/p).is_file():
   (clone/p).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/p,clone/p)
 before={p.name:p.read_bytes() for p in clone.glob('*.html')}
 subprocess.run(['python',str(clone/'scripts/parent/embed.py')],check=True)
 assert all((clone/p).read_bytes()==v for p,v in before.items()),'generator replay changed HTML'
 preflight=(clone/'tests/parent_mode.py').read_text().split('class Quiet(')[0]
 def preflight_run():exec(compile(preflight,'isolated-parent-preflight','exec'),{'__file__':str(clone/'tests/parent_mode.py')})
 preflight_run()
 unknown=clone/'unknown-learning.html';unknown.write_text('<!doctype html><html><head><meta charset="utf-8"><script>void 0;</script></head><body>synthetic</body></html>')
 try:preflight_run();raise RuntimeError('unknown unprotected HTML accepted')
 except AssertionError:pass
 subprocess.run(['python',str(clone/'scripts/parent/embed.py')],check=True);preflight_run()
 unknown.unlink()
 (clone/'content-review.html').write_bytes(before['content-review.html']+b'\n<!-- synthetic mutation -->')
 mutated={p.name:p.read_bytes() for p in clone.glob('*.html')}
 result=subprocess.run(['python',str(clone/'scripts/parent/embed.py')],capture_output=True)
 assert result.returncode!=0 and b'AssertionError' in result.stderr
 assert all((clone/p).read_bytes()==v for p,v in mutated.items()),'mutation rejection wrote HTML'
 try:preflight_run();raise RuntimeError('changed content accepted')
 except AssertionError:pass
print(json.dumps({'main':main,'old_pr11':old,'main_exact_files':len(mainpaths),'old_content_exact_files':content,'suite_union':29,'generator_replay_exact_html':len(before),'unknown_unprotected_html_rejected':True,'unknown_html_protected_by_generator':True,'changed_content_rejected_before_writes':True,'content_sha256':hashlib.sha256((root/'content-review.html').read_bytes()).hexdigest()},indent=2))
