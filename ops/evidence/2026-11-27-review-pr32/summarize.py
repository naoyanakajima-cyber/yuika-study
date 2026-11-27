import datetime, hashlib, json, pathlib, re, subprocess
p=pathlib.Path(__file__).resolve().parent
r=json.loads((p/'check-all-attempt1.json').read_text())
s=json.loads((p/'static-review.json').read_text())
log=(p/'check-all-attempt1.log').read_text()
body=log.split('Suite')[1]
rows=[{'suite':m[0],'exit_code':int(m[1]),'seconds':int(m[2])} for m in re.findall(r'^((?:tests/|notifications/test/)\S+)\s+(\d+)\s+(\d+)\s*$',body,re.M)]
expected=re.findall(r'^run (\S+)',pathlib.Path(r['cwd'],'scripts/check_all.sh').read_text(),re.M)
assert len(rows)==33 and [x['suite'] for x in rows]==expected
assert s['exact_union'] and all(x['exit_code']==0 for x in rows)
assert r['exit_code']==0 and r['head_before']==r['head_after']==s['candidate']
assert r['status_before']==r['status_after']==''
summary={'verdict':'PASS','reviewer':'qa_rev_pr32','candidate':s['candidate'],'attempt':1,'total_suites':len(rows),'passed_suites':len(rows),'exact_union_old32_main28':True,'started_at':r['started_at'],'completed_at':r['completed_at'],'elapsed_seconds':r['seconds'],'exit_code':r['exit_code'],'clean_before_after':True,'suites':rows}
(p/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
q=p/'QA.md'; text=q.read_text(); text=text.replace('判定: 全33suiteの終了結果を待機中。完了前の本記録を合格証拠にしない。',f"判定: **PASS**。固定clean HEADで `bash scripts/check_all.sh` を独立に1回実行し、厳密unionの全33suiteがexit0。開始 {r['started_at']}、完了 {r['completed_at']}、経過 {r['seconds']}秒。実行前後HEAD一致・tracked/untracked差分なし。完全logは `check-all-attempt1.log`、実行receiptは `check-all-attempt1.json`、機械可読集計は `summary.json`。")
text+='\n## 全suite実行結果\n\n| Suite | Exit | 秒 |\n|---|---:|---:|\n'+''.join(f"| {x['suite']} | {x['exit_code']} | {x['seconds']} |\n" for x in rows)
text+='\n`generator_preservation` は新算数HTMLを含む全trackedファイルを独立一時コピーで12 generator順に2pass再生成し、初回byte保持と再実行不変を検証してPASS。`math_passage` は24問を別計算で確認、通常stage0完了・stage3途中終了のmock通知、親stage1完了/途中終了のenqueue抑止をPASS。`recommended_review` 等は選定理由・優先順・採点・既存記録保持・reload/import互換性をPASS。必須全suite再試行は行っていない。\n'
q.write_text(text)
files=sorted(x for x in p.iterdir() if x.is_file() and x.name!='SHA256SUMS')
(p/'SHA256SUMS').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.name+'\n' for x in files))
print(json.dumps({k:v for k,v in summary.items() if k!='suites'},ensure_ascii=False))
