"""Capture one QA command, fixed revision, clean state, timestamps and exit code."""
import json, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
out=Path(__file__).resolve().parent
label,root,command=sys.argv[1:];root=Path(root)
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
r={'command':command,'cwd':str(root),'head_before':git('rev-parse','HEAD'),'status_before':git('status','--porcelain'),'started_at':datetime.now(timezone.utc).isoformat()}
start=time.monotonic()
with (out/(label+'.log')).open('w') as log:
 p=subprocess.run(['bash','-lc',command],cwd=root,stdout=log,stderr=subprocess.STDOUT)
r.update(exit_code=p.returncode,seconds=round(time.monotonic()-start,3),finished_at=datetime.now(timezone.utc).isoformat(),head_after=git('rev-parse','HEAD'),status_after=git('status','--porcelain'))
(out/(label+'-execution.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2));sys.exit(p.returncode)
