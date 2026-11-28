from pathlib import Path
import subprocess,json,re,hashlib,tarfile,io,tempfile,sys
R=Path('/workspace/yuika-content-lever-qa');O=Path('/workspace/qa-content-lever-evidence')
HEAD='ee228ca0a1865d0a56f4302cd9342a4f66738561';MAIN='58f8b53b4da69806d15a126fc525b65893a0bf35';OLD='1678519f916471ba6e38044855de240bd6c4a807'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def tree(rev):return {line.split('\t')[1]:line.split()[2] for line in git('ls-tree','-r',rev).decode().splitlines()}
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert not git('status','--porcelain','--untracked-files=no')
m,o,h=tree(MAIN),tree(OLD),tree(HEAD)
delta=git('diff','--name-only',MAIN,HEAD).decode().splitlines()
content_paths=[p for p in o if p=='content-review.html' or p.startswith('docs/product/fixtures/') or p.startswith('tests/content_') or p in ['docs/product/content-image-trial-spec.md','docs/product/content-import-guard-spec.md','docs/product/content-spec.md','docs/product/content-try-spec.md']]
assert all(o[p]==h[p] for p in content_paths)
shared=['README.md','docs/codex-cloud.md','scripts/check_all.sh','scripts/cloud/serve.py','scripts/parent/embed.py','tests/cloud_preview.py','tests/parent_mode.py']
stable=[p for p in m if p not in shared]
assert all(m[p]==h[p] for p in stable)
assert set(delta)==set(content_paths)|set(shared)
def suites(rev):return re.findall(r'^run (\S+)',git('show',rev+':scripts/check_all.sh').decode(),re.M)
assert len(suites(HEAD))==31 and len(set(suites(HEAD)))==31
assert suites(HEAD)==suites(MAIN)+[x for x in suites(OLD) if x.startswith('tests/content_')]
for p in shared:
 if p!='scripts/check_all.sh':assert o[p]==h[p],p
html=(R/'content-review.html').read_text();digest=hashlib.sha256(html.encode()).hexdigest()
for p in ['scripts/parent/embed.py','tests/parent_mode.py']:assert digest in (R/p).read_text()
for bad in ['localStorage','sessionStorage','indexedDB','Storage','cookie','YuikaParent','YuikaReports','YUIKA_PARENT_BEGIN','fetch(','XMLHttpRequest','sendBeacon','WebSocket','eval(']:assert bad not in html,bad
for directive in ['default-src','connect-src','form-action','object-src']:assert directive+" 'none'" in html
isolated=Path(tempfile.mkdtemp(prefix='cycle188-qa-static-',dir='/tmp'))
with tarfile.open(fileobj=io.BytesIO(git('archive',HEAD))) as t:t.extractall(isolated,filter='data')
before={p.relative_to(isolated).as_posix():p.read_bytes() for p in isolated.rglob('*') if p.is_file()}
generation=[]
for p in ['scripts/design/build_summary.py','scripts/design/embed.py','scripts/parent/embed.py']:
 run=subprocess.run([sys.executable,p],cwd=isolated,capture_output=True,text=True);generation.append({'script':p,'exit':run.returncode});assert run.returncode==0,run.stderr
assert all((isolated/p).read_bytes()==b for p,b in before.items())
def preflight():
 code=(isolated/'tests/parent_mode.py').read_text().split('class Quiet(')[0]
 return subprocess.run([sys.executable,'-c','__file__='+repr(str(isolated/'tests/parent_mode.py'))+'\n'+code],capture_output=True,text=True)
assert preflight().returncode==0
(isolated/'unknown.html').write_text('<!doctype html><title>Synthetic</title>')
p=preflight();assert p.returncode!=0 and 'unknown.html' in p.stderr
(O/'unknown-html-refused.log').write_text(p.stderr);(isolated/'unknown.html').unlink()
f=isolated/'content-review.html';f.write_text(f.read_text()+'\n<!-- synthetic tamper -->\n')
before_html={p.name:p.read_bytes() for p in isolated.glob('*.html')}
p=subprocess.run([sys.executable,'scripts/parent/embed.py'],cwd=isolated,capture_output=True,text=True)
assert p.returncode!=0 and before_html=={p.name:p.read_bytes() for p in isolated.glob('*.html')}
(O/'modified-content-generator-refused.log').write_text(p.stderr)
p=preflight();assert p.returncode!=0;(O/'modified-content-preflight-refused.log').write_text(p.stderr)
result={'head':HEAD,'main':MAIN,'old_content':OLD,'main_equal_count':len(stable),'main_equal_paths':stable,'content_equal_count':len(content_paths),'content_equal_paths':content_paths,'delta_main':delta,'shared_except_suite_equal_old':True,'suites':suites(HEAD),'content_sha256':digest,'generators':generation,'generation_byte_identical':True,'unknown_html_and_modified_content_rejected':True}
(O/'static-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
