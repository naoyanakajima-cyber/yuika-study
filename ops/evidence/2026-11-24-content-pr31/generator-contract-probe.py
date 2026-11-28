"""Independent perturbation of Edo source and shared clients inside disposable tracked copy."""
import json,re,hashlib,shutil,subprocess,sys,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(sys.argv[1]).resolve();OUT=Path(__file__).resolve().parent
names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')[:-1]
def hashes(root):return {n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}
def questions(text):return json.loads(re.search(r'const QUESTIONS=(\[.*?\n\]);',text,re.S)[1])
initial=hashes(ROOT);started=time.monotonic();result={'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'started_at':datetime.now(timezone.utc).isoformat(),'commands':[]}
try:
 with tempfile.TemporaryDirectory(prefix='isolated-generator-',dir=OUT) as tmp:
  copy=Path(tmp)
  for name in names:
   target=copy/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
  old=questions((copy/'edo-review.html').read_text());q_id=old[0]['id'];prompt=old[0]['prompt']
  source=copy/'scripts/edo/questions.py'
  source.write_text(source.read_text()+"\n# Independent disposable synthetic source-propagation fixture.\n_qa_original_build=build\ndef build():\n rows=_qa_original_build()\n rows[0]['prompt']+='（合成の文章訂正確認）'\n return rows\n")
  def run(command,expected=0):
   t=time.monotonic();p=subprocess.run(command,cwd=copy,text=True,capture_output=True)
   result['commands'].append({'command':command,'exit_code':p.returncode,'expected_exit':expected,'seconds':round(time.monotonic()-t,3),'output':p.stdout+p.stderr})
   assert p.returncode==expected,(command,p.returncode,p.stdout,p.stderr)
  run([sys.executable,'scripts/edo/build.py'])
  changed=questions((copy/'edo-review.html').read_text());assert changed[0]['prompt']==prompt+'（合成の文章訂正確認）' and changed[1:]==old[1:]
  archive_before=json.loads((copy/'scripts/history/revisions.json').read_text())['edo-review.html'][q_id]
  # Ordinary generation must reject a source change that has no registered revision.
  run([sys.executable,'scripts/history/embed.py'],expected=1)
  assert '版未登録' in result['commands'][-1]['output']
  run([sys.executable,'scripts/history/embed.py','--record-editorial','--reason','Independent disposable same-meaning text fixture'])
  archive=json.loads((copy/'scripts/history/revisions.json').read_text())['edo-review.html'][q_id]
  assert archive[:-1]==archive_before and archive[-1]['revision']==archive_before[-1]['revision']+1
  assert archive[-1]['question']==changed[0]
  # Active shared client remains generated from client.js, not frozen with the Edo template.
  client=copy/'notifications/client.js';client.write_text(client.read_text()+'\n// INDEPENDENT_SYNTHETIC_CLIENT_PROPAGATION\n')
  run([sys.executable,'notifications/embed.py'])
  run([sys.executable,'scripts/parent/embed.py'])
  edo=(copy/'edo-review.html').read_text()
  assert '// INDEPENDENT_SYNTHETIC_CLIENT_PROPAGATION' in edo
  assert edo.index('<!-- YUIKA_PARENT_END -->')<edo.index('<!-- YUIKA_REPORTS_BEGIN -->')
  assert edo.count('<!-- YUIKA_REPORTS_BEGIN -->')==1
  assert edo.count('<!-- YUIKA_PARENT_BEGIN -->')==1
  result.update(question_build_source_applied=True,unregistered_revision_rejected=True,editorial_revision_appended_prior_versions_retained=True,shared_notification_source_applied=True,parent_boundary_before_entire_report_block=True)
 assert hashes(ROOT)==initial
 result.update(source_checkout_unchanged=True,result='passed')
finally:
 result.update(seconds=round(time.monotonic()-started,3),finished_at=datetime.now(timezone.utc).isoformat())
 (OUT/'generator-contract-probe-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS independent Edo source propagation, revision rejection/append, shared client refresh, parent ordering; candidate unchanged')
