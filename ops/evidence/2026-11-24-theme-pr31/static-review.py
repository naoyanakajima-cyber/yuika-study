"""Independent fixed-candidate source preservation and exact suite union review."""
import subprocess,json,re,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
root=Path(sys.argv[1]);out=Path(__file__).resolve().parent;expected=sys.argv[2]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
head=git('rev-parse','HEAD');assert head==expected and not git('status','--porcelain')
old='00c4ccb3b501223366a5f0a736567231ea9b8043';main='101c64ef9be86cb7c3502d3eeec498f16e93e7fd'
for ref in [old,main]:subprocess.run(['git','merge-base','--is-ancestor',ref,head],cwd=root,check=True)
def suites(ref):return re.findall(r'^run (\S+)',git('show',ref+':scripts/check_all.sh'),re.M)
actual=suites(head);required=set(suites(old))|set(suites(main));assert set(actual)==required and len(actual)==29
unchanged={p:git('rev-parse',old+':'+p)==git('rev-parse',head+':'+p) for p in ['docs/product/theme-spec.md','tests/theme_review.py','scripts/practice/embed_science.py','scripts/history/revisions.json','tests/lever.py','scripts/practice/adaptive.js','scripts/practice/science.js','scripts/prototype/runtime.js','assets/progress.js','scripts/cloud/serve.py']}
assert all(unchanged.values()),unchanged
patterns=[r'<style>\n/\* Appearance controls are independent of the learning views and records\. \*/.*?</style>',r'<section class="theme-panel" aria-label="見た目">.*?</section>',r'<script>\n/\* Theme preference never calls learning render/save or notification code\. \*/.*?</script>']
oldk=git('show',old+':kamakura-review.html');newk=(root/'kamakura-review.html').read_text();theme_blocks=[]
for pattern in patterns:
 a=re.findall(pattern,oldk,re.S);b=re.findall(pattern,newk,re.S);assert len(a)==len(b)==1 and a==b
 theme_blocks.append(hashlib.sha256(a[0].encode()).hexdigest())
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
 if name!='kamakura-review.html':assert all(x not in t for x in ['theme-panel','data-ui-theme','Theme preference never','Appearance controls are independent'])
assert not (root/'content-review.html').exists()
assert 'scienceDailySources' not in (root/'yuika-review-v2.html').read_text()
subprocess.run(['git','diff','--check',old,head],cwd=root,check=True)
result={'candidate':head,'recorded_at':datetime.now(timezone.utc).isoformat(),'old_pr12':old,'main':main,'old_pr12_suite_count':len(suites(old)),'main_suite_count':len(suites(main)),'actual_suite_count':len(actual),'union_exact':True,'suites':actual,'own_branch_contract_files_byte_unchanged':unchanged,'theme_css_controls_runtime_sha256_unchanged':theme_blocks,'question_definitions_byte_unchanged':questions,'parent_precedes_notification_block':boundaries,'theme_absent_from_other_six_pages':True,'pr10_scienceDailySources_absent':True,'pr11_content_html_absent':True,'status':git('status','--porcelain'),'changes_from_old_pr12':git('diff','--stat',old,head),'changes_from_main':git('diff','--stat',main,head)}
(out/'static-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
