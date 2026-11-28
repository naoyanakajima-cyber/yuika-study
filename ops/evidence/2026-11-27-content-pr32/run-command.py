import datetime,json,pathlib,subprocess,sys,time
root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);cmd=sys.argv[3:]
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
git=lambda *args:subprocess.check_output(['git',*args],cwd=root,text=True).strip()
record={'command':cmd,'cwd':str(root),'started_at':now(),'head_before':git('rev-parse','HEAD'),'status_before':git('status','--porcelain')}
started=time.monotonic()
with out.with_suffix('.log').open('w') as log:
 p=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT)
record.update(completed_at=now(),exit_code=p.returncode,seconds=round(time.monotonic()-started,3),head_after=git('rev-parse','HEAD'),status_after=git('status','--porcelain'))
out.with_suffix('.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record));sys.exit(p.returncode)
