import subprocess,json,re,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
root=Path(sys.argv[1]);out=Path(__file__).resolve().parent;expected=sys.argv[2]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
head=git('rev-parse','HEAD');assert head==expected
old=git('rev-parse','3920f16');main='101c64ef9be86cb7c3502d3eeec498f16e93e7fd'
for ref in [old,main]:subprocess.run(['git','merge-base','--is-ancestor',ref,head],cwd=root,check=True)
def suites(ref):return re.findall(r'^run (\S+)',git('show',ref+':scripts/check_all.sh'),re.M)
actual=suites(head);required=set(suites(old))|set(suites(main));assert set(actual)==required and len(actual)==33
unchanged={p:git('rev-parse',old+':'+p)==git('rev-parse',head+':'+p) for p in ['content-review.html','scripts/practice/embed_science.py','scripts/history/revisions.json','tests/lever.py','scripts/practice/adaptive.js','scripts/practice/science.js','scripts/prototype/runtime.js','assets/progress.js']}
assert all(unchanged.values()),unchanged
source=(root/'scripts/parent/embed.py').read_text();assert "if p.name=='content-review.html':continue" in source
assert "b978ea0ebd725cbe0b0b45275ad19d7be4ee78e64fb5c7e40947fe05475560f4" in source
assert hashlib.sha256((root/'content-review.html').read_bytes()).hexdigest()=='b978ea0ebd725cbe0b0b45275ad19d7be4ee78e64fb5c7e40947fe05475560f4'
questions={};boundaries={}
for name in ['onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html','edo-review.html']:
 a=re.search(r'const QUESTIONS\s*=\s*(\[.*?\n\]);',git('show',old+':'+name),re.S)
 b=re.search(r'const QUESTIONS\s*=\s*(\[.*?\n\]);',(root/name).read_text(),re.S)
 assert a and b and a[1]==b[1],name
 questions[name]=len(json.loads(b[1]))
for name in ['index.html','onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html','edo-review.html']:
 t=(root/name).read_text();assert t.count('<!-- YUIKA_PARENT_BEGIN -->')==t.count('<!-- YUIKA_REPORTS_BEGIN -->')==1
 assert t.index('<!-- YUIKA_PARENT_END -->')<t.index('<!-- YUIKA_REPORTS_BEGIN -->')
 boundaries[name]=True
subprocess.run(['git','diff','--check',old,head],cwd=root,check=True)
result={'question_definitions_byte_unchanged':questions,'parent_precedes_notification_block':boundaries,'candidate':head,'recorded_at':datetime.now(timezone.utc).isoformat(),'old_pr11':old,'main':main,'old_pr11_suite_count':len(suites(old)),'main_suite_count':len(suites(main)),'actual_suite_count':len(actual),'union_exact':True,'suites':actual,'own_branch_contract_files_byte_unchanged':unchanged,'content_parent_exemption_hash_preserved':True,'status':git('status','--porcelain'),'changes_from_old_pr11':git('diff','--stat',old,head),'changes_from_main':git('diff','--stat',main,head),'edo_self_template':'Science/prototype adapters require explicit future synchronization; question build and notification/history/design/parent generated contracts separately probed.'}
(out/'static-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
