from pathlib import Path
import subprocess,json,re,hashlib,tempfile,tarfile,io,sys
R=Path('/workspace/yuika-content-main-compat-20261115');O=Path('/tmp/yuika-cycle33-qa');MAIN='60d1a946cc02ed8acea54c0d7af7d6451fcc30ec';OLD='ee51e68d7e1eeb21bd0e959ec58166a869947d0a'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def blob(ref,p):return git('show',ref+':'+p)
def paths(ref):return git('ls-tree','-r','--name-only',ref).decode().splitlines()
head=git('rev-parse','HEAD').decode().strip();assert head==sys.argv[1];assert not git('status','--porcelain')
for ref in [MAIN,OLD]:subprocess.run(['git','merge-base','--is-ancestor',ref,head],cwd=R,check=True)
mainpaths=[p for p in paths(MAIN) if (p.endswith('.html') and '/' not in p) or p.startswith(('assets/','scripts/practice/','scripts/history/','notifications/')) or p=='scripts/parent/runtime.js']
for p in mainpaths:assert (R/p).read_bytes()==blob(MAIN,p),p
contentpaths=[p for p in paths(OLD) if p=='content-review.html' or p.startswith('docs/product/fixtures/') or (p.startswith('tests/content_') and p.endswith('.py')) or p in ['docs/product/content-spec.md','docs/product/content-try-spec.md','docs/product/content-import-guard-spec.md']]
for p in contentpaths:assert (R/p).read_bytes()==blob(OLD,p),p
suites=lambda t:re.findall(r'^run (\S+)',t,re.M)
a=suites(blob(MAIN,'scripts/check_all.sh').decode());b=suites(blob(OLD,'scripts/check_all.sh').decode());c=suites((R/'scripts/check_all.sh').read_text());assert len(c)==len(set(c)) and set(c)==set(a)|set(b),(a,b,c)
h=hashlib.sha256((R/'content-review.html').read_bytes()).hexdigest();assert h=='fea62d048857059b8016f3a36061795bacb18acf160d1bdc0c9997d277abd001'
for p in ['scripts/parent/embed.py','tests/parent_mode.py']:assert h in (R/p).read_text()
# Preview modifications must be limited to the entry union: all other code equal to main.
serve=(R/'scripts/cloud/serve.py').read_text();mainserve=blob(MAIN,'scripts/cloud/serve.py').decode();assert serve.replace("            'content-review.html',\n",'')==mainserve
archive=git('archive',head)
def stage():
 d=Path(tempfile.mkdtemp(prefix='yuika-cycle33-qa-',dir='/tmp'))
 with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(d,filter='data')
 return d
def preflight(d):
 code=(d/'tests/parent_mode.py').read_text().split('class Quiet(')[0]
 return subprocess.run([sys.executable,'-c','__file__='+repr(str(d/'tests/parent_mode.py'))+'\n'+code],capture_output=True,text=True)
d=stage();before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.glob('*.html')};g=subprocess.run([sys.executable,str(d/'scripts/parent/embed.py')],capture_output=True,text=True);assert g.returncode==0,g.stderr;after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.glob('*.html')};assert before==after,'generator must be idempotent';assert preflight(d).returncode==0
(d/'unknown.html').write_text('<!doctype html><title>Synthetic unknown</title>');p=preflight(d);assert p.returncode!=0 and 'unknown.html' in p.stderr;(O/'unknown-refused.log').write_text(p.stderr)
(d/'unknown.html').unlink();f=d/'content-review.html';f.write_text(f.read_text()+'\n<!-- synthetic tamper -->\n');before={p.name:p.read_bytes() for p in d.glob('*.html')};g=subprocess.run([sys.executable,str(d/'scripts/parent/embed.py')],capture_output=True,text=True);assert g.returncode!=0 and 'AssertionError' in g.stderr;assert before=={p.name:p.read_bytes() for p in d.glob('*.html')};(O/'modified-content-generator-refused.log').write_text(g.stderr);p=preflight(d);assert p.returncode!=0;(O/'modified-content-preflight-refused.log').write_text(p.stderr)
result={'head':head,'main':MAIN,'prior_pr_head':OLD,'main_bytes_identical':mainpaths,'content_bytes_identical':contentpaths,'suite_union':c,'suite_count':len(c),'content_sha256':h,'preview_change_only_content_entry':True,'generator_idempotent':True,'preflight_known_pass':True,'unknown_html_rejected':True,'modified_content_rejected_before_generator_writes':True,'modified_content_preflight_rejected':True};(O/'static-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
