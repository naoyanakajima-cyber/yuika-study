from pathlib import Path
import subprocess,json,re,hashlib
R=Path('/workspace/qa-theme-generator-checkout');O=Path('/workspace/qa-theme-generator-evidence');OLD='e89aa335936508c6e4984c523ec65da97f510cbd'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(rev,path):return git('show',rev+':'+path)
HEAD=git('rev-parse','HEAD').decode().strip();assert not git('status','--porcelain')
science=(R/'yuika-review-v2.html').read_bytes();assert science==blob(OLD,'yuika-review-v2.html')
text=science.decode();adapter=text.split('// SCIENCE_ADAPTIVE_START\n')[1].split('function weaknesses(')[0];source=(R/'scripts/practice/science.js').read_text();runtime=(R/'scripts/prototype/runtime.js').read_text()
assert adapter==source+'\n';assert text.split('// PROTOTYPE_START\n')[1].split('// PROTOTYPE_END\n')[0]==runtime
assert 'scienceDailySources' not in source
rows=[]
for path in ['onin-review.html','kamakura-review.html','heian-review.html','mock-focus-review.html']:
 old=blob(OLD,path).decode();new=(R/path).read_text();a=old.splitlines();b=new.splitlines();assert len(a)==len(b)
 delta=[(x,y) for x,y in zip(a,b) if x!=y];assert len(delta)==1,(path,delta)
 x,y=delta[0];assert 'questionVersion' in x and 'answerUnit' not in x
 assert y==x.replace("'explanation']:","'explanation','answerUnit','answerTag']:")
 assert old.replace(x,y)==new
 assert "const prototypeScience=typeof byId!=='undefined';" in new
 assert 'const fields=prototypeScience?\n'+y in new
 assert not re.search(r'(?:const|let|var)\s+byId\b',new)
 assert new.split('// PROTOTYPE_START\n')[1].split('// PROTOTYPE_END\n')[0]==runtime
 rows.append({'path':path,'changed_lines':1,'all_other_bytes_unchanged':True})
assert blob(OLD,'tests/theme_review.py')==(R/'tests/theme_review.py').read_bytes()
assert blob(OLD,'docs/product/theme-spec.md')==(R/'docs/product/theme-spec.md').read_bytes()
oldnames=git('ls-tree','-r','--name-only',OLD).decode().splitlines();changed=git('diff','--name-only',OLD,HEAD).decode().splitlines()
expected={'scripts/practice/science.js','scripts/prototype/runtime.js','tests/generator_preservation.py','tests/lever.py','scripts/check_all.sh','docs/history-compatibility.md','onin-review.html','kamakura-review.html','heian-review.html','mock-focus-review.html'}
assert set(changed)==expected,changed
unchanged=[p for p in oldnames if p not in expected];assert all(blob(OLD,p)==(R/p).read_bytes() for p in unchanged)
suites=re.findall(r'^run (\S+)',(R/'scripts/check_all.sh').read_text(),re.M);old_suites=re.findall(r'^run (\S+)',blob(OLD,'scripts/check_all.sh').decode(),re.M)
assert len(suites)==28 and len(set(suites))==28 and [s for s in suites if s!='tests/generator_preservation.py']==old_suites
result={'head':HEAD,'base':OLD,'changed_paths':changed,'science_html_sha256':sha(science),'science_source_sha256':sha(source.encode()),'source_embedded_identity':True,'prototype_source_embedded_identity':True,'other_html':rows,'theme_css_ui_js_diagram_print_preserved_by_exact_other_bytes':True,'theme_spec_test_hashes':{p:sha((R/p).read_bytes()) for p in ['docs/product/theme-spec.md','tests/theme_review.py']},'other_unchanged_paths':len(unchanged),'suite_count':28,'existing_suite_order_preserved':True,'clean':True}
(O/'static-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
