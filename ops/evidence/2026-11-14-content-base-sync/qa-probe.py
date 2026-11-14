import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path('/workspace/yuika-content-base-20261114')
HEAD='f1e84a7b998dfbcd71c6692974015bdd08e1877e'
BASE='86514eda054a5a2e09204df3a0668e40624c16de'
OLD='3d2ed2f9a62673d2fb086a360ae841096f35b63e'
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert not git('status','--short','--untracked-files=all').strip()
source=(ROOT/'tests/parent_mode.py').read_text()
assert source.count('class Quiet(')==1
prefix=source.split('class Quiet(',1)[0]
assert source.split('class Quiet(',1)[1]==git('show',BASE+':tests/parent_mode.py').decode().split('class Quiet(',1)[1]
for f in ('tests/parent_mode.py','scripts/parent/embed.py'):
    assert (ROOT/f).read_bytes()==git('show',HEAD+':'+f)
previous=json.loads(Path('/tmp/yuika-content-base-qa-static.json').read_text())
allowed=set(previous['allowlist_exact'])|{'tests/parent_mode.py','scripts/parent/embed.py'}
assert set(git('diff','--name-only',BASE,HEAD).decode().splitlines())==allowed
for p,blob in previous['original_blobs'].items():
    assert git('rev-parse',HEAD+':'+p).decode().strip()==blob
for ancestor in (BASE,OLD):
    subprocess.run(['git','merge-base','--is-ancestor',ancestor,HEAD],cwd=ROOT,check=True)
def boundary(directory):
    exec(compile(prefix,str(directory/'tests/parent_mode.py'),'exec'),{'__file__':str(directory/'tests/parent_mode.py'),'__name__':'independent_qa_static_probe'})
def snapshots(directory):
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob('*.html')}
results={'head':HEAD,'allowlist_exact':sorted(allowed),'eight_original_blobs_equal':True,'both_ancestors':True,'browser_test_body_main_identical':True,'sources':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ('tests/parent_mode.py','scripts/parent/embed.py')}}
with tempfile.TemporaryDirectory(prefix='yuika-content-qa-probe-') as temp:
    d=Path(temp)
    for name in git('ls-files').decode().splitlines():
        target=d/name; target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    boundary(d);results['reviewed_entries_static_pass']=True
    before=snapshots(d)
    p=subprocess.run([sys.executable,str(d/'scripts/parent/embed.py')],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert snapshots(d)==before
    results['generator_once_all_seven_html_bytes_unchanged']=True
    unexpected=d/'synthetic-unknown.html';unexpected.write_text('<!doctype html><meta charset="utf-8"><title>Synthetic</title>')
    try:boundary(d)
    except AssertionError:results['unknown_markerless_html_rejected']=True
    else:raise AssertionError('unknown markerless HTML was accepted')
    unexpected.unlink()
    content=d/'content-review.html';content.write_bytes(content.read_bytes()+b'\n<!-- synthetic tamper -->\n')
    try:boundary(d)
    except AssertionError:results['tampered_content_test_rejected']=True
    else:raise AssertionError('tampered CONTENT was accepted')
    before=snapshots(d)
    p=subprocess.run([sys.executable,str(d/'scripts/parent/embed.py')],capture_output=True,text=True)
    assert p.returncode!=0 and 'AssertionError' in p.stderr
    assert snapshots(d)==before
    results['tampered_content_generator_rejected_before_html_writes']=True
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert not git('status','--short','--untracked-files=all').strip()
results['product_head_and_clean_state_preserved']=True
Path('/tmp/yuika-content-base-qa-probe.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
