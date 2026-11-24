"""Generate QA report only after all fixed-head evidence is complete."""
import json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
out=Path(__file__).resolve().parent
sha='feada5947b237310923f0aa1956487ac8af501af'
def read(name):return json.loads((out/name).read_text())
execution=read('check-all-attempt1-execution.json');log=(out/'check-all-attempt1.log').read_text()
rows=[{'suite':m[0],'exit_code':int(m[1]),'seconds':int(m[2])} for m in re.findall(r'^(\S+(?:\.py|\.mjs))\s+(\d+)\s+(\d+)\s*$',log,re.M)]
assert execution['exit_code']==0 and len(rows)==33 and all(r['exit_code']==0 for r in rows)
for name in ['check-all-attempt1-execution.json','static-review-attempt1-execution.json','content-probe-attempt2-execution.json','report-probe-attempt2-execution.json','generator-contract-attempt1-execution.json']:
 e=read(name);assert e['head_before']==e['head_after']==sha and e['exit_code']==0 and not e['status_before'] and not e['status_after']
report=read('report-probe-result.json');content=read('content-probe-result.json');generator=read('generator-contract-probe-result.json');static=read('static-review.json')
assert report['result']==content['result']==generator['result']=='passed'
assert len(report['contexts'])==8 and len(content['contexts'])==4
summary={'reviewer':'qa_content_pr31','candidate':sha,'verdict':'PASS','reviewed_at':datetime.now(timezone.utc).isoformat(),'required_suite':dict(execution,suite_count=len(rows),passed=len(rows),suites=rows),'content_probe':{'fresh_browser_contexts':2,'text_image_cases':4,'seconds':content['seconds'],'storage_write_calls':0,'page_errors':content['page_errors'],'requests_blocked':content['requests_blocked'],'actual_parent_study_session_verified':True,'content_has_parent_runtime':False},'independent_reports':{'fresh_contexts':len(report['contexts']),'captured_mock_reports':sum(c['captured_reports'] for c in report['contexts']),'seconds':report['seconds'],'unexpected_posts':report['unexpected_posts'],'page_errors':report['page_errors'],'external_requests_aborted':report['external_requests_aborted']},'generator_contract_probe':'passed','product_mutations_by_qa':False,'product_test_failures':0,'qa_harness_initial_failures':2,'qa_harness_retries':2,'max_attempts_per_cause':2,'expected_negative_checks':1}
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
table='\n'.join(f"| `{r['suite']}` | {r['exit_code']} | {r['seconds']} |" for r in rows)
text=f'''# PR11 / PR31互換同期 — 独立QA

判定 **PASS**。実装者と別担当の `qa_content_pr31` が固定候補 `{sha}` を検証した。製品マージ・公開・実通知の承認ではない。

## 固定候補と必須チェック

クラウド上の独立detached checkout `/workspace/qa-content-pr31` を使用。親は既存PR11 `3920f1642692c88a8d6870480bc3f98f71558d24` と観測main `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`。ignored `.venv/bin` linkで既存 `/workspace/yuika-study/.venv/bin` を手動再利用し、各テストshellで `source scripts/cloud/activate.sh`。自動snapshot引き継ぎ成功とは扱わない。

`bash scripts/check_all.sh` は今回**1回のみ、33/33成功、exit 0、wall {execution['seconds']}秒**。開始 `{execution['started_at']}`、終了 `{execution['finished_at']}`。前後HEAD一致・status空。旧PR11の32本とmainの27本の厳密な和集合33本。各suiteのexit/秒は下表と `summary.json`、完全ログは `check-all-attempt1.log`、時刻は `check-all-attempt1-execution.json`。Engineerのdirty tree実行や旧PR11の成功を今回に算入しない。

## 固定差分と保持

`static-review.json` で、CONTENTのHTMLとhash付きparent除外、science/adaptive/prototype共有元、履歴archive、既存lever試験、progress資産は旧PR11からbyte不変。6学習HTMLの問題定義も全byte不変（{json.dumps(static['question_definitions_byte_unchanged'],ensure_ascii=False)}）。7通知対象はparent runtimeと通知blockが各1つで、親境界は通知開始マーカーより前。`git diff --check` 成功。README/生成元/親試験/報告試験の固定差分も確認した。

PR11の「今日の5問」を保持し、PR10の理由付き復習・日次実問数のコピーは含まない。理科answerUnit/answerTag、旧履歴、てこの進行・再開は変更されていない既存検証をこの固定候補で実行した結果に帰属する。通知対象拡張による旧「通知なし」条件の変更はmainの意図した契約変更であり、親抑止・件数・重複のassertは維持・追加されている。

## 独立CONTENT操作と親セッションの区別

768×1024、touch、Asia/Tokyo、fresh Chromium 2 contextで、通常と実際の学習画面から開始した親セッション中に、合成テキスト/三角形画像の4ケースを操作した。画像は転記・不明箇所を手動修正して確認。全確認前のtrial無効、登録した答えの一致/不一致、JSON書出しと再入力で内容保持・確認失効、編集で全確認失効、終了/pagehideでtrial回答消去、reloadで提案が消えることを確認した。CONTENTでstorage書込呼出し0、localStorage/sessionStorage全体不変、pageerror0。所要{content['seconds']}秒。

CONTENT自体は意図したメモリ内試作で、親runtime/bannerを持たない。親の証拠は、応仁で `?parent-check=1` から実際にbannerとsuppressを確認し、CONTENTへ移動後もsessionを保ち、応仁へ戻ってbannerを確認し、親終了後に本人localStorageがbyte不変であること。**CONTENTのURLにqueryを付けただけの親隔離成功とはしていない。** `content-probe-result.json`。

CONTENTの確認済み編集下部と画像trial結果のPNG2枚を実際に開き、見えている操作欄の可読性と重なりなしを確認した。確認済みPNGはスクロール下部で原本三角形は写らず、全ページ・全問題の目視確認とはしない。`visual-review.json`。

## 独立報告ライフサイクル

応仁・理科てこ・江戸・模試算数を通常/親の8 fresh context、768×1024で操作した。未回答終了では記録・job・報告0。1回答後のホーム移動をキャンセルするとsession ID/回答を保持しjob/報告0。その後の途中終了は通常で回答1件の報告1件。再enqueue2回とreloadで件数不変。日次入口から5問を完了し、回答数・正答数・report内answersが一致、modeはPR11の「今日の5問」。resultを2回呼んでも再送なし。

通常4contextは計8mock報告、親4contextは送信/job0でsessionStorageにも通知jobなし、本人localStorageは全体byte不変。実際の親bannerをassertした。予期しないPOST0、pageerror0、外部GET試行{report['external_requests_aborted']}件は遮断。所要{report['seconds']}秒。`report-probe-result.json`。必須study_reportsの16報告はWorker validator/stub deliveryでも確認したが実配送ではない。

PR11のてこ専用「今日はここまで」は回答済み結果を直ちに表示する既存契約。キャンセル対象はホーム移動操作であり、通常社会の終了ボタンと同じではない。この違いを保持し、製品をPR10の動作へ合わせていない。

## 生成保持と江戸self-template

必須 `generator_preservation.py` は江戸・模試・通知・教科投影を含む12呼出し（practiceは2回）を使い捨てコピーで実行し、**初回の全tracked byte保持と2回目不変**を成功確認。元checkoutも不変。

追加の独立使い捨てコピーで江戸 `questions.build()` の1問に合成の文章訂正を加え、buildがHTMLに反映すること、版未登録のhistory生成が期待どおりexit1で拒否すること、明示editorial登録が旧版を保持して版を1つ追加することを確認。通知clientの合成markerも再埋込され、親境界は通知block全体より前で各1つ。候補全tracked hash不変。probe exit0、{generator['seconds']}秒。`generator-contract-probe-result.json`。意図した拒否exit1は製品失敗/再試行ではない。

江戸の既存HTMLをテンプレートとする方式は、理科のてこ専用処理の混入を防ぐ。共有notification/history/design/parentは再埋込されるが、江戸内science/prototype adapterは今後の共通修正時に明示的な同期が必要。README/Engineer文書と一致し、全runtime自動同期は主張しない。

## QAハーネスの初回失敗と診断

製品チェック失敗0、QAハーネス初回失敗2件。各原因は診断後の2回目で成功し、3回目や無根拠な再試行はない。候補変更・assert弱化なし。

- CONTENT初回exit1、2.058秒、workflow context完了0。Storage計測のevaluateが最後の関数代入値を返し、Playwrightが無束縛呼出ししてIllegal invocation。戻り値をundefinedにするarrow wrapperだけを変更し、2回目exit0、8.869秒。旧source・初回result・診断を保存。
- report初回exit1、13.575秒、応仁通常/親の2context完了後、てこ終了に確認dialogを期待したfixture誤り。固定コードの既存てこend処理を確認し、cancelを実際のホームnavに、部分終了後を既存結果画面のreturn操作に修正。全件数/記録/重複/親assertを保持し、2回目exit0、19.135秒で8context完了。旧source・初回result・診断を保存。

詳しくは `content-probe-diagnosis.json` / `report-probe-diagnosis.json` とattempt別ログ。過去のPR10probeはハーネス設計の参照のみで、成功証拠はこの固定候補で新たに取得したもの。

## 必須suite実測

| Suite | Exit | 秒 |
|---|---:|---:|
{table}

## 限界と権限

実機iPad/Safari/WebKit、本人試用、学習効果、公開画面、実メール配送は未検証。必須suiteの一部は公開CDNをcurl取得するため完全オフラインではない。独立probeはmock/外部abort、合成データのみ。

QAによる製品/board編集・push・設定変更・公開・実通知・子spawnは0。合成生成元変更は削除済みの使い捨てコピーのみ。恒久証拠はこのdirectoryのみ。候補以後の変更は判定対象外。
'''
(out/'QA.md').write_text(text)
files=sorted(p for p in out.iterdir() if p.is_file() and p.name!='SHA256SUMS')
(out/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
print(json.dumps({'candidate':sha,'verdict':'PASS','suites':len(rows),'seconds':execution['seconds'],'report':str(out/'QA.md')},indent=2))
