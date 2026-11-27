"""Assemble receipts only after the fixed candidate's complete independent run."""
import json,re,subprocess,datetime,hashlib
from pathlib import Path
ROOT=Path('/workspace/yuika-theme-pr32-qa-cycle311');OUT=Path(__file__).parent
head='b4deb0df131b1280ab2cc0647851e1d345d06143'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def read(name):return json.loads((OUT/name).read_text())
assert (OUT/'check-all.exit').exists(),'Full suite is still running'
code=int((OUT/'check-all.exit').read_text());log=(OUT/'check-all.log').read_text();static=read('static-review.json');before=read('before.json');probe=read('probe-result.json');csp=read('math-csp-result.json')
rows=[{'name':name,'exit_code':int(exit_code),'seconds':int(seconds)} for name,exit_code,seconds in re.findall(r'^(\S+)\s+(\d+)\s+(\d+)\s*$',log,re.M) if name in static['suites']]
total=re.search(r'^Total: (\d+)s; result=(\d+)$',log,re.M)
assert code==0 and total and total[2]=='0'
assert [r['name'] for r in rows]==static['suites'] and len(rows)==30 and all(r['exit_code']==0 for r in rows)
assert 'HEAD: '+head in log and before['head']==head and before['status']==''
assert git('rev-parse','HEAD')==head and git('status','--porcelain')==''
hashes=read('tracked-sha256.json');assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
assert probe['head']==csp['head']==head and not probe['post_requests_or_arrivals'] and not probe['page_errors']
assert (OUT/'theme-probe.exit').read_text().strip()==(OUT/'math-csp-probe.exit').read_text().strip()=='0'
now=datetime.datetime.now(datetime.timezone.utc).isoformat();completed=datetime.datetime.fromtimestamp((OUT/'check-all.exit').stat().st_mtime,datetime.timezone.utc).isoformat()
after={'head':head,'status':git('status','--porcelain'),'all_tracked_sha256_unchanged':True,'utc':now};(OUT/'after.json').write_text(json.dumps(after,indent=2)+'\n')
full={'command':'bash scripts/check_all.sh','started_at':before['utc'],'completed_at':completed,'exit_code':code,'seconds':int(total[1]),'head':head,'clean_before':True,'clean_after':True,'suite_count':len(rows),'passed_count':len(rows),'attempt':1,'retries':0,'suites':rows}
summary={'reviewer':'qa_theme_pr32','candidate':head,'commit':head,'head':head,'result':'passed_pr32_theme_compatibility_and_generator_preservation','completed_at':now,'full_suite':full,'required_suites':30,'suite_count':30,'passed_count':30,'exit_code':0,'seconds':int(total[1]),'attempt':1,'retries':0,'qa_harness_initial_failures':0,'checkout_before_after_clean':True,'all_tracked_hashes_preserved':True,'independent_theme_contexts':2,'independent_math_navigation_contexts':2,'independent_math_preview_csp_contexts':1,'independent_images_inspected':6,'diagram_contrast':min(x['ratio'] for group in probe['diagram_contrasts'] for x in group['labels']),'generator_contract_probe':'passed_in_full_suite_first_attempt','generator_steps_per_pass':12,'generator_passes':2,'generator_initial_all_tracked_bytes_preserved':True,'generator_second_pass_unchanged':True,'math_byte_equal_main':True,'kamakura_byte_equal_old_pr12':True,'exact_frozen_parent_suite_union':True,'home_cards_asserted':22,'inherited_status_text_stale_counts':{'design_c':20,'responsive_subjects':21},'math_24_answers_recomputed_in_suite':True,'mock_math_reports_in_suite':2,'probes':{'theme':'probe-result.json','math_preview_csp':'math-csp-result.json','static':'static-review.json','visual':'visual-inspection.md'},'limitations':['Synthetic Chromium only; no Safari/WebKit or real iPad','No personal data, user preference or learning effectiveness verified','Existing runtime reused manually; no automatic snapshot handoff claim','No real notification, main merge, deployment or settings changes']}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
table='\n'.join(f"| `{r['name']}` | {r['exit_code']} | {r['seconds']} |" for r in rows)
report=f'''# PR12 / PR32 independent QA

Reviewer: `qa_theme_pr32`. Fixed candidate: `{head}`. Result: **PASS**. Independent detached checkout `/workspace/yuika-theme-pr32-qa-cycle311`; implementation remained untouched.

## Exact revision and static review

The candidate retains old PR12 `df7af2a205f44e8c76b50e96728685efcc7e57d8` and main `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5` as its two parents. The complete Kamakura HTML (CSS/UI/runtime, content, state/storage code and print rules) and theme tests match old PR12 byte for byte. Math HTML matches main byte for byte. Every file changed against one parent matches the opposite parent, except the combined required-suite runner and new compatibility note. No assertion was weakened. Direct diffs and static comparisons are retained alongside this report.

The frozen 29-suite PR12 list and 28-suite main list have an exact 30-suite union. The runner includes that union once each. The added math/home/design/responsive/notification/preview changes are inherited main bytes. Existing focus derivation excludes all Kamakura theme markers. No new theme, PR10/PR11 feature, grading migration or storage key change was added.

## Full required suite

`bash scripts/check_all.sh` ran once, starting {before['utc']}, completed {completed}, exit **0**, **30/30 passed**, total **{int(total[1])} seconds**. No failure, retry, skipped suite or harness repair occurred. HEAD and all 100 tracked-file hashes were unchanged; checkout was clean before and after. `check-all.log` retains all stdout/stderr, suite exit codes and timings. `before.json`, `after.json`, `tracked-sha256.json` and `summary.json` retain receipts.

| Suite | Exit | Seconds |
| --- | ---: | ---: |
{table}

The generator suite ran the audited twelve-step sequence twice in an isolated tracked-file copy. Its first pass preserved **all committed bytes**, including math; its second pass was unchanged. This is stronger than checking only idempotence. It also verified the source checkout stayed unchanged. Existing generator fixes and exclusions remain byte-identical to old PR12.

The math suite independently recomputed all 24 answers and verified five stages with 8/3/4/5/4 questions, normal completion, early completion, two intercepted mock reports and parent notification suppression. Design/responsive checks preserved the 22-card home, five-stage math navigation and layout checks. The inherited design/responsive success lines still say 20/21 units; both executed assertions explicitly require 22 cards and were inspected. These are results of this fixed-HEAD independent run, not engineer or prior-cycle results.

## Bounded independent interaction and visual evidence

`theme-probe.py` was inspected and adapted from the previous synthetic probe, then executed anew on this candidate. Two fresh 768×1024 contexts covered normal and parent modes. Each ran five Kamakura questions (text and choice), toggling standard/Kamakura during entered input, selected choice, hint, graded answer and result. Run, learning DOM, input values, preferences, records and notice were compared before/after every toggle. Five answer events survived reload and every round trip; theme switches made no notification enqueue call or extra network request.

Each context made standard→math→return, Kamakura→math→return, and standard→math→return comparisons. Math had no theme panel/attribute, no theme-storage writes, unchanged measured body color/background/font/width, and preserved the selected preference. The three-question second stage completed while Kamakura was selected, and returning restored the theme and all five Kamakura events. The parent banner persisted; normal localStorage, including a different synthetic child theme, stayed byte-identical through parent interactions.

Computed diagram label contrast was **{summary['diagram_contrast']:.10f}:1** for both themes in screen and print media. Diagram DOM stayed identical and print hid theme controls without storage changes. All six screenshots were opened and inspected; the captured theme input/hint, math result, parent banners and diagram labels were readable without overlap. See `visual-inspection.md` and `image-sha256.json`.

The inherited cloud-preview suite does not directly visit math, so a separate bounded `math-csp-probe.py` used the actual PreviewHandler. Math returned HTTP 200 with five stage controls; a synthetic same-origin POST was rejected by CSP, emitted a `connect-src` policy violation and reached the handler **zero** times. No route intercepted this loopback POST. Both the document CSP and the preview header were active; this verifies their combined blocking, not attribution to the preview policy alone. Theme navigation also checked the connection/form blocking headers.

## Limits and handling

All data and browser contexts were synthetic. The math mock report and Worker suites intercepted APIs; independent previews made no real notification. Existing runtime was manually reused through an ignored `.venv/bin` link; this does not prove automatic environment or snapshot handoff. Real iPad/Safari/WebKit, personal preference, learning effectiveness, physical printing and live deployment remain unverified. No product edit, product push, main merge, deployment, real data/notification, account or environment setting change was performed by QA. Passing QA does not authorize production release.
'''
(OUT/'QA.md').write_text(report)
files=[p for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ['PrM-plan.md','evidence-sha256.json']]
(OUT/'evidence-sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
print(json.dumps({'result':summary['result'],'head':head,'suites':len(rows),'seconds':int(total[1]),'clean':True,'evidence_files':len(files)+1},indent=2))
