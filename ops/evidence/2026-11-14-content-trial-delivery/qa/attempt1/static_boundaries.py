import hashlib,json,re,subprocess,tempfile,tarfile,io
from pathlib import Path
ROOT=Path('/workspace/yuika-content-trial-delivery-20261114');OUT=Path('/tmp/yuika-content-trial-qa');BASE='62f34de238e9d1d62c796aac3a4b43418043d17f'
def old(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
apps=['index.html','onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html']
for path in apps:assert (ROOT/path).read_bytes()==old(path),path
html=(ROOT/'content-review.html').read_text();before=old('content-review.html').decode()
assert re.search(r'<meta http-equiv="Content-Security-Policy"[^>]+>',html).group()==re.search(r'<meta http-equiv="Content-Security-Policy"[^>]+>',before).group()
assert before[before.index('function validateShape'):before.index('function clearConfirm')]==html[html.index('function validateShape'):html.index('function clearConfirm')]
assert before[before.index('const SAMPLES='):before.index('const clone=')]==html[html.index('const SAMPLES='):html.index('const clone=')]
for path in ['scripts/parent/embed.py','tests/parent_mode.py']:
    def norm(t):return re.sub(r'[0-9a-f]{64}','HASH','\n'.join(x for x in t.splitlines() if not x.lstrip().startswith('#')))
    assert norm((ROOT/path).read_text())==norm(old(path).decode()),path
    assert hashlib.sha256((ROOT/'content-review.html').read_bytes()).hexdigest() in (ROOT/path).read_text()
archive=subprocess.check_output(['git','archive','HEAD'],cwd=ROOT)
def stage():
    p=Path(tempfile.mkdtemp(prefix='yuika-qa-boundary-',dir='/tmp'))
    with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(p,filter='data')
    return p
p=stage();content=p/'content-review.html';content.write_text(content.read_text()+'\n<!-- synthetic tamper -->\n')
beforehash={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('*.html')}
a=subprocess.run(['python',str(p/'scripts/parent/embed.py')],capture_output=True,text=True)
assert a.returncode!=0 and 'AssertionError' in a.stderr
assert beforehash=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('*.html')}
(OUT/'modified-content-generator-refusal.txt').write_text(a.stderr)
# Execute only the unchanged boundary preflight, not the browser/network suite.
p2=stage();(p2/'unknown.html').write_text('<!doctype html><meta charset="utf-8"><title>Synthetic unguarded page</title>')
code=(p2/'tests/parent_mode.py').read_text().split('class Quiet(')[0]
a=subprocess.run(['python','-c',"__file__="+repr(str(p2/'tests/parent_mode.py'))+'\n'+code],capture_output=True,text=True)
assert a.returncode!=0 and 'AssertionError: unknown.html' in a.stderr,a.stderr
(OUT/'unknown-html-preflight-refusal.txt').write_text(a.stderr)
code=(p/'tests/parent_mode.py').read_text().split('class Quiet(')[0]
a=subprocess.run(['python','-c',"__file__="+repr(str(p/'tests/parent_mode.py'))+'\n'+code],capture_output=True,text=True)
assert a.returncode!=0 and 'AssertionError' in a.stderr
(OUT/'modified-content-preflight-refusal.txt').write_text(a.stderr)
result={'base':BASE,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'six_learning_html_identical':apps,'csp_unchanged':True,'validator_and_issues_unchanged':True,'embedded_fixtures_identical':True,'hash_guard_changes_only_hash_and_comments':True,'modified_content_generator_rejected_before_writes':True,'unknown_html_preflight_rejected':True,'modified_content_preflight_rejected':True}
(OUT/'static-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
