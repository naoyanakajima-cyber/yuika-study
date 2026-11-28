"""Summarize completed independent QA; refuses missing/failed evidence."""
import datetime,hashlib,json,pathlib,re,subprocess
E=pathlib.Path(__file__).resolve().parent
run=json.loads((E/'check-all-attempt1.json').read_text())
log=(E/'check-all-attempt1.log').read_text()
static=json.loads((E/'static-checks.json').read_text())
suites=[{'name':m[0],'exit_code':int(m[1]),'seconds':int(m[2])} for m in re.findall(r'^((?:tests/|notifications/test/)\S+)\s+(\d+)\s+(\d+)\s*$',log,re.M)]
assert len(suites)==34 and {s['name'] for s in suites}==set(static['candidate_suites'])
assert run['exit_code']==0 and all(s['exit_code']==0 for s in suites)
assert run['head_before']==run['head_after']==static['head'] and not run['status_before'] and not run['status_after']
probes={}
for name,result_file in [('content-probe-attempt1','content-probe-result'),('edit-reconfirm-attempt1','edit-reconfirm-result'),('preview-probe-attempt1','preview-probe-result')]:
 record=json.loads((E/(name+'.json')).read_text());result=json.loads((E/(result_file+'.json')).read_text())
 assert record['exit_code']==0 and result['result']=='passed' and record['head_before']==record['head_after']==static['head'] and not record['status_before'] and not record['status_after']
 probes[name]={'execution':record,'result_file':result_file+'.json'}
summary={'reviewer':'qa_content_pr32','implementer':'engineer_content_pr32','reviewer_independent':True,'candidate':static['head'],'result':'PASS','full_suite':run,'suite_count':34,'passed_count':34,'attempt':1,'retries':0,'suites':suites,'strict_suite_union':static['suite_counts'],'probes':probes,'environment':'Cloud; existing venv manually linked; not automatic snapshot handoff','written_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'limits':['Synthetic fixtures only','Chromium desktop emulation, not physical iPad/Safari','Mock notifications only, no real delivery','No merge/deploy/production data validation']}
(E/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
qa=f'''# PR11 / PR32 独立 QA

判定: **PASS**。実装者 `engineer_content_pr32` とは別の `qa_content_pr32` が実行・レビューした。製品編集、push、実通知は行っていない。

- 固定候補: `{static['head']}`。独立 detached checkout `/workspace/qa-content-pr32-cycle310`。
- 実行: `{run['started_at']}` → `{run['completed_at']}`、{run['seconds']} 秒。
- `bash scripts/check_all.sh`: **34 / 34 suite 成功、exit 0、初回のみ、再試行 0**。開始・終了とも同一 HEAD、working tree clean。
- 旧 PR11 33 suite と main 28 suite の厳密な和集合 34 suite。重複・欠落・余分なし。`static-checks.json` と `summary.json` に個別名・終了コード・秒数、`check-all-attempt1.log` に全文ログを保存した。suite 秒数は runner の整数秒であり、個別の絶対開始時刻ではない。

## 内容と互換性

`content-review.html`、教材 fixture / 仕様、5教材テスト、既存 runtime の計18ファイルは旧PR11とbyte一致。新算数HTMLは main とbyte一致。差分は算数ページ追加、22カード入口、生成対象・preview allowlist追加、suite追加、対応する表示テストと引継ぎ文書に限定される。diff --check 成功。

全suiteで生成12段階×2巡の全tracked file保持を確認。算数24問の答え独立再計算、5段階、通常の完了・途中終了mock報告、親モードでenqueueを呼ばないことが成功した。ホームの算数入口から遷移して5段階表示と戻りを確認するdesign_c、通常/親のresponsive_subjectsも成功した。design_cの既存成功ログ文には旧「20 home units」が残っているが、実際のassertは22カード、算数2カードおよび算数遷移を検証している（非阻害のログ表記差）。

独立preview probeは教材確認・算数の両ルートでHTTP200、候補ファイルとbyte一致、CSP `connect-src 'none'; form-action 'none'; object-src 'none'` を確認した。

## 合成教材の独立 UI probe

768×1024 Chromiumの通常contextと、実際の学習ページで親バナーに入ったcontextの各々で、合成textと三角形画像を確認した。contentページ自体には親runtime/バナーがないため、query指定だけを親モード確認とは扱っていない。既存親sessionの保持と学習ページに戻った際の親バナー・退出を確認した。

確認前の試用禁止、画像の転記・解決入力、確認、正誤試用、編集による確認失効、編集後再確認と試用、JSON再入力による確認失効、再確認、終了・pagehide・reload時の試用消去が成功。通常の合成記録/localStorage/sessionStorageは変化なし、観測Storage書込0、POST試行0、page error 0。外部font GETは遮断した。全8スクリーンショットを保存した。

次の4枚をReviewerが目視し、768×1024の確認・試用操作領域の読める表示を確認した。確認画面はスクロール位置のviewport撮影で、ページ全体の一枚撮りではない。

- `content-image-normal-trial.png`
- `content-text-parent-session-confirmed.png`
- `content-image-parent-session-confirmed.png`
- `content-text-normal-trial.png`

## 限界と次の一手

既存venvをignored `.venv/bin`へ手動linkした。自動snapshot引継ぎ成功とは主張しない。旧probeコードは再点検して今回HEADで新規実行し、旧結果は流用していない。実機iPad/Safari、本人回答・教材写真、実通知、公開・デプロイは未実施。QA合格はCEO承認や本番公開の許可を意味しない。

統括がlease/remote HEADを再確認して、この候補と証拠を既存draft PR11/台帳へ保存し、CEO判断待ちを維持する。
'''
(E/'QA.md').write_text(qa)
entries=[]
for p in sorted(E.iterdir()):
 if p.is_file() and p.name!='SHA256SUMS':entries.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name)
(E/'SHA256SUMS').write_text('\n'.join(entries)+'\n')
print(json.dumps({'result':'PASS','head':static['head'],'suites':len(suites),'seconds':run['seconds'],'files':len(entries)},indent=2))
