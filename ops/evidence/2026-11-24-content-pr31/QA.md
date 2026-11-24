# PR11 / PR31互換同期 — 独立QA

判定 **PASS**。実装者と別担当の `qa_content_pr31` が固定候補 `feada5947b237310923f0aa1956487ac8af501af` を検証した。製品マージ・公開・実通知の承認ではない。

## 固定候補と必須チェック

クラウド上の独立detached checkout `/workspace/qa-content-pr31` を使用。親は既存PR11 `3920f1642692c88a8d6870480bc3f98f71558d24` と観測main `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`。ignored `.venv/bin` linkで既存 `/workspace/yuika-study/.venv/bin` を手動再利用し、各テストshellで `source scripts/cloud/activate.sh`。自動snapshot引き継ぎ成功とは扱わない。

`bash scripts/check_all.sh` は今回**1回のみ、33/33成功、exit 0、wall 367.568秒**。開始 `2026-11-24T11:10:52.571179+00:00`、終了 `2026-11-24T11:17:00.139137+00:00`。前後HEAD一致・status空。旧PR11の32本とmainの27本の厳密な和集合33本。各suiteのexit/秒は下表と `summary.json`、完全ログは `check-all-attempt1.log`、時刻は `check-all-attempt1-execution.json`。Engineerのdirty tree実行や旧PR11の成功を今回に算入しない。

## 固定差分と保持

`static-review.json` で、CONTENTのHTMLとhash付きparent除外、science/adaptive/prototype共有元、履歴archive、既存lever試験、progress資産は旧PR11からbyte不変。6学習HTMLの問題定義も全byte不変（{"onin-review.html": 30, "kamakura-review.html": 38, "heian-review.html": 75, "yuika-review-v2.html": 112, "mock-focus-review.html": 46, "edo-review.html": 22}）。7通知対象はparent runtimeと通知blockが各1つで、親境界は通知開始マーカーより前。`git diff --check` 成功。README/生成元/親試験/報告試験の固定差分も確認した。

PR11の「今日の5問」を保持し、PR10の理由付き復習・日次実問数のコピーは含まない。理科answerUnit/answerTag、旧履歴、てこの進行・再開は変更されていない既存検証をこの固定候補で実行した結果に帰属する。通知対象拡張による旧「通知なし」条件の変更はmainの意図した契約変更であり、親抑止・件数・重複のassertは維持・追加されている。

## 独立CONTENT操作と親セッションの区別

768×1024、touch、Asia/Tokyo、fresh Chromium 2 contextで、通常と実際の学習画面から開始した親セッション中に、合成テキスト/三角形画像の4ケースを操作した。画像は転記・不明箇所を手動修正して確認。全確認前のtrial無効、登録した答えの一致/不一致、JSON書出しと再入力で内容保持・確認失効、編集で全確認失効、終了/pagehideでtrial回答消去、reloadで提案が消えることを確認した。CONTENTでstorage書込呼出し0、localStorage/sessionStorage全体不変、pageerror0。所要8.52秒。

CONTENT自体は意図したメモリ内試作で、親runtime/bannerを持たない。親の証拠は、応仁で `?parent-check=1` から実際にbannerとsuppressを確認し、CONTENTへ移動後もsessionを保ち、応仁へ戻ってbannerを確認し、親終了後に本人localStorageがbyte不変であること。**CONTENTのURLにqueryを付けただけの親隔離成功とはしていない。** `content-probe-result.json`。

CONTENTの確認済み編集下部と画像trial結果のPNG2枚を実際に開き、見えている操作欄の可読性と重なりなしを確認した。確認済みPNGはスクロール下部で原本三角形は写らず、全ページ・全問題の目視確認とはしない。`visual-review.json`。

## 独立報告ライフサイクル

応仁・理科てこ・江戸・模試算数を通常/親の8 fresh context、768×1024で操作した。未回答終了では記録・job・報告0。1回答後のホーム移動をキャンセルするとsession ID/回答を保持しjob/報告0。その後の途中終了は通常で回答1件の報告1件。再enqueue2回とreloadで件数不変。日次入口から5問を完了し、回答数・正答数・report内answersが一致、modeはPR11の「今日の5問」。resultを2回呼んでも再送なし。

通常4contextは計8mock報告、親4contextは送信/job0でsessionStorageにも通知jobなし、本人localStorageは全体byte不変。実際の親bannerをassertした。予期しないPOST0、pageerror0、外部GET試行28件は遮断。所要18.608秒。`report-probe-result.json`。必須study_reportsの16報告はWorker validator/stub deliveryでも確認したが実配送ではない。

PR11のてこ専用「今日はここまで」は回答済み結果を直ちに表示する既存契約。キャンセル対象はホーム移動操作であり、通常社会の終了ボタンと同じではない。この違いを保持し、製品をPR10の動作へ合わせていない。

## 生成保持と江戸self-template

必須 `generator_preservation.py` は江戸・模試・通知・教科投影を含む12呼出し（practiceは2回）を使い捨てコピーで実行し、**初回の全tracked byte保持と2回目不変**を成功確認。元checkoutも不変。

追加の独立使い捨てコピーで江戸 `questions.build()` の1問に合成の文章訂正を加え、buildがHTMLに反映すること、版未登録のhistory生成が期待どおりexit1で拒否すること、明示editorial登録が旧版を保持して版を1つ追加することを確認。通知clientの合成markerも再埋込され、親境界は通知block全体より前で各1つ。候補全tracked hash不変。probe exit0、0.447秒。`generator-contract-probe-result.json`。意図した拒否exit1は製品失敗/再試行ではない。

江戸の既存HTMLをテンプレートとする方式は、理科のてこ専用処理の混入を防ぐ。共有notification/history/design/parentは再埋込されるが、江戸内science/prototype adapterは今後の共通修正時に明示的な同期が必要。README/Engineer文書と一致し、全runtime自動同期は主張しない。

## QAハーネスの初回失敗と診断

製品チェック失敗0、QAハーネス初回失敗2件。各原因は診断後の2回目で成功し、3回目や無根拠な再試行はない。候補変更・assert弱化なし。

- CONTENT初回exit1、2.058秒、workflow context完了0。Storage計測のevaluateが最後の関数代入値を返し、Playwrightが無束縛呼出ししてIllegal invocation。戻り値をundefinedにするarrow wrapperだけを変更し、2回目exit0、8.869秒。旧source・初回result・診断を保存。
- report初回exit1、13.575秒、応仁通常/親の2context完了後、てこ終了に確認dialogを期待したfixture誤り。固定コードの既存てこend処理を確認し、cancelを実際のホームnavに、部分終了後を既存結果画面のreturn操作に修正。全件数/記録/重複/親assertを保持し、2回目exit0、19.135秒で8context完了。旧source・初回result・診断を保存。

詳しくは `content-probe-diagnosis.json` / `report-probe-diagnosis.json` とattempt別ログ。過去のPR10probeはハーネス設計の参照のみで、成功証拠はこの固定候補で新たに取得したもの。

## 必須suite実測

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 5 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 0 |
| `notifications/test/browser.py` | 0 | 11 |
| `tests/study_reports.py` | 0 | 30 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/generator_preservation.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 3 |
| `tests/adaptive_daily.py` | 0 | 7 |
| `tests/adaptive_quality.py` | 0 | 5 |
| `tests/flash_grading.py` | 0 | 8 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 16 |
| `tests/medaka.py` | 0 | 18 |
| `tests/lever.py` | 0 | 5 |
| `tests/microscope.py` | 0 | 25 |
| `tests/science_adaptive.py` | 0 | 10 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 12 |
| `tests/parent_mode.py` | 0 | 20 |
| `tests/design_c.py` | 0 | 20 |
| `tests/responsive_subjects.py` | 0 | 120 |
| `tests/content_review.py` | 0 | 4 |
| `tests/content_guidance.py` | 0 | 2 |
| `tests/content_import_guard.py` | 0 | 4 |
| `tests/content_trial.py` | 0 | 4 |
| `tests/content_image_trial.py` | 0 | 3 |

## 限界と権限

実機iPad/Safari/WebKit、本人試用、学習効果、公開画面、実メール配送は未検証。必須suiteの一部は公開CDNをcurl取得するため完全オフラインではない。独立probeはmock/外部abort、合成データのみ。

QAによる製品/board編集・push・設定変更・公開・実通知・子spawnは0。合成生成元変更は削除済みの使い捨てコピーのみ。恒久証拠はこのdirectoryのみ。候補以後の変更は判定対象外。
