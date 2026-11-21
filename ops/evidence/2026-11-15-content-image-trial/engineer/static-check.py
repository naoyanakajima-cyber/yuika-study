import hashlib,json,re,subprocess,shutil,tempfile
from pathlib import Path
root=Path.cwd();base='d75a5469fbf1e8c5011a6307308546e5ec669ceb';allowed={'README.md','content-review.html','scripts/check_all.sh','scripts/parent/embed.py','tests/content_review.py','tests/parent_mode.py'}
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base],text=True).splitlines()
def old(p):return subprocess.check_output(['git','show',f'{base}:{p}'])
for p in paths:
 if p not in allowed:assert (root/p).read_bytes()==old(p),p
html=(root/'content-review.html').read_text();prior=old('content-review.html').decode();sha=hashlib.sha256(html.encode()).hexdigest()
assert re.search(r'<meta http-equiv="Content-Security-Policy"[^>]*>',html).group()==re.search(r'<meta http-equiv="Content-Security-Policy"[^>]*>',prior).group()
assert html[html.index('function validateShape'):html.index('const nonempty')]==prior[prior.index('function validateShape'):prior.index('const nonempty')]
assert html[html.index('function setImportPending'):]==prior[prior.index('function setImportPending'):]
for name in ['scripts/parent/embed.py','tests/parent_mode.py']:
 assert (root/name).read_text()==old(name).decode().replace('fea62d048857059b8016f3a36061795bacb18acf160d1bdc0c9997d277abd001',sha)
for forbidden in ['localStorage','sessionStorage','indexedDB','Storage','cookie','fetch(','XMLHttpRequest','sendBeacon','WebSocket','history.']:
 assert forbidden not in html,forbidden
svg=(root/'docs/product/fixtures/synthetic-triangle-source.svg').read_text()
for forbidden in ['<script','<image','href=','url(','<foreignObject']:
 assert forbidden not in svg,forbidden
runs=re.findall('^run (.+)$',(root/'scripts/check_all.sh').read_text(),re.M)
oldruns=re.findall('^run (.+)$',old('scripts/check_all.sh').decode(),re.M)
assert len(runs)==len(set(runs))==30 and set(runs)==set(oldruns)|{'tests/content_image_trial.py python tests/content_image_trial.py'}
with tempfile.TemporaryDirectory(prefix='yuika-cycle34-generator-') as td:
 clone=Path(td)
 for p in paths:
  (clone/p).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/p,clone/p)
 before={p.name:p.read_bytes() for p in clone.glob('*.html')}
 subprocess.run(['python',str(clone/'scripts/parent/embed.py')],check=True)
 assert all((clone/p).read_bytes()==v for p,v in before.items())
 preflight=(clone/'tests/parent_mode.py').read_text().split('class Quiet(')[0]
 def check():exec(compile(preflight,'isolated-parent-preflight','exec'),{'__file__':str(clone/'tests/parent_mode.py')})
 check();unknown=clone/'unknown.html';unknown.write_text('<html><head><meta charset="utf-8"><script>void 0;</script></head><body>synthetic</body></html>')
 try:check();raise RuntimeError('unknown unprotected accepted')
 except AssertionError:pass
 subprocess.run(['python',str(clone/'scripts/parent/embed.py')],check=True);check();unknown.unlink()
 (clone/'content-review.html').write_bytes(before['content-review.html']+b'\n<!-- synthetic alteration -->')
 mutated={p.name:p.read_bytes() for p in clone.glob('*.html')}
 result=subprocess.run(['python',str(clone/'scripts/parent/embed.py')],capture_output=True)
 assert result.returncode!=0 and b'AssertionError' in result.stderr
 assert all((clone/p).read_bytes()==v for p,v in mutated.items())
 try:check();raise RuntimeError('mutated content accepted')
 except AssertionError:pass
print(json.dumps({'base':base,'unchanged_base_files':len(paths)-len(allowed),'content_sha256':sha,'hash_only_changes':['scripts/parent/embed.py','tests/parent_mode.py'],'unchanged':'CSP, shape validator, async import and complete trial engine, main learning pages/assets/runtime, old fixtures','suite_union':30,'isolated_generator_html_unchanged':8,'unknown_boundary_and_mutated_content_rejection':True},ensure_ascii=False,indent=2))
