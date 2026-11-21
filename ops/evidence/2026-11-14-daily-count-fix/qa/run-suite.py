import subprocess,sys,json,datetime
from pathlib import Path
root=Path('/workspace/yuika-daily-fix-20261114');out=Path('/tmp/yuika-daily-fix-qa');expected=sys.argv[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
meta={'head_before':git('rev-parse','HEAD'),'dirty_before':git('status','--porcelain'),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
assert meta['head_before']==expected and not meta['dirty_before'];(out/'suite-meta.json').write_text(json.dumps(meta,indent=2)+'\n')
with (out/'suite.log').open('w') as f:code=subprocess.run(['bash','scripts/check_all.sh'],cwd=root,stdout=f,stderr=subprocess.STDOUT).returncode
meta.update(head_after=git('rev-parse','HEAD'),dirty_after=git('status','--porcelain'),finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=code)
(out/'suite-meta.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta));assert meta['head_after']==expected and not meta['dirty_after'];sys.exit(code)
