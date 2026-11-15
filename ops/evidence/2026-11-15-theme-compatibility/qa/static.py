"""Independent main-to-candidate unchanged-boundary review."""
import json,re,subprocess,hashlib
from pathlib import Path
ROOT=Path('/workspace/yuika-theme-compatibility-20261115');OUT=Path('/tmp/yuika-cycle24-qa');MAIN='86514eda054a5a2e09204df3a0668e40624c16de';OLD='57171ad9cab02fec6a080ecbe317fe11d3f51dcf'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True)
head=git('rev-parse','HEAD').strip();assert not git('status','--porcelain').strip()
subprocess.check_call(['git','merge-base','--is-ancestor',MAIN,head],cwd=ROOT);subprocess.check_call(['git','merge-base','--is-ancestor',OLD,head],cwd=ROOT)
files=git('diff','--name-only',MAIN,head).splitlines();allowed={'README.md','docs/product/theme-spec.md','kamakura-review.html','tests/theme_review.py','scripts/check_all.sh'}
assert set(files)<=allowed,files
baseline=git('show',MAIN+':kamakura-review.html');candidate=(ROOT/'kamakura-review.html').read_text()
for marker in ['YUIKA_PARENT','YUIKA_REPORTS']:
 pat='<!-- '+marker+'_BEGIN -->.*?<!-- '+marker+'_END -->';a=re.findall(pat,baseline,re.S);b=re.findall(pat,candidate,re.S);assert a and a==b,marker
scripts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',baseline,re.S);new=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',candidate,re.S)
for s in scripts: assert s in new,'main script changed'
added=[s for s in new if s not in scripts];assert len(added)==1,len(added);theme=added[0];assert 'YuikaParent.storage' in theme;assert not re.search(r'\blocalStorage\b|\bfetch\s*\(|\brender\s*\(|\bgo\s*\(|\bsave\s*\(',theme),'theme bypass or learning action'
for text in [baseline,candidate]:
 assert '<script' in text
pat=r'<meta[^>]*http-equiv="Content-Security-Policy"[^>]*>';assert re.findall(pat,baseline)==re.findall(pat,candidate)
changed=[p for p in files if p.endswith('.html')];assert changed==['kamakura-review.html']
suite=(ROOT/'scripts/check_all.sh').read_text();old=git('show',MAIN+':scripts/check_all.sh');assert suite.replace('run tests/theme_review.py python tests/theme_review.py\n','')==old,'required check runner differs beyond theme registration'
result={'head':head,'main':MAIN,'old_theme':OLD,'changed_files':files,'ancestor_preserved':True,'main_embedded_scripts_unchanged':len(scripts),'only_added_script':'theme uses YuikaParent.storage','csp_unchanged':True,'other_html_shared_assets_runtime_unchanged':True,'suite_registration_only':True}
(OUT/'static-result.json').write_text(json.dumps(result,indent=2)+'\n');print('static boundary PASS',json.dumps(result))
