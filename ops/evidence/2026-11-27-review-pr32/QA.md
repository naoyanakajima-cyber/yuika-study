# PR10 / merged PR32 compatibility — independent QA

Reviewer: `qa_rev_pr32`。実装者 `engineer_rev_pr32` とは別担当。対象候補は PrM が固定した `792f438fe648e056ad83a423e55bebe9d53fe43f`。独立 detached checkout `/workspace/qa-rev-pr32-cycle309` で実行した。既存 Cloud venv を手動でリンクしたため、自動 snapshot 引継ぎ成功とは扱わない。

判定: **PASS**。固定clean HEADで `bash scripts/check_all.sh` を独立に1回実行し、厳密unionの全33suiteがexit0。開始 2026-11-27T15:12:16.805526+00:00、完了 2026-11-27T15:18:39.754654+00:00、経過 382.929秒。実行前後HEAD一致・tracked/untracked差分なし。完全logは `check-all-attempt1.log`、実行receiptは `check-all-attempt1.json`、機械可読集計は `summary.json`。

## 独立差分確認

- 旧PR10 `0cd726f558d24999da80c37b1ecdbd2e6090c7bb` の32suiteとmain `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5` の28suiteの厳密unionは33。候補は同一集合で重複・脱落なし。
- `index.html` の旧PR10からの差分は新算数単元と固定24問表示の2行追加のみ。既存の今日の復習ラベルや入口の削除なし。
- 既存復習HTML、共有進捗/理科/試作runtime、recommended_review/daily_count/science_daily_count/generator_preservation tests は旧PR10とbyte一致。新算数HTML、通知generator、Cloud preview allowlist、算数テストはmainとbyte一致。詳細は `static-review.json`。
- 新算数は24問・5段階。親モードが通知モジュールより先に評価される境界が各1つ存在。questions JSON SHA-256は `542c84f59f115dd59977aee96de48bb9c86dfe94d4ce5a168de0a31446c66fd2`。
- `git diff --check` は成功。responsive_subjectsは単元数22と算数選択式/数値入力を追加し、既存幅検査を保持。

## UIおよびデータ確認

独立 `ui-probe.py` を768×1024 Chromium、合成回答だけで実行。通常/親の応仁復習では選定理由表示→開始→回答→採点→保存→reload後2件保持を確認。親では通常領域のbyte保持も確認。算数通常/親ではstage0回答→途中終了と通常領域不変を確認。4contextともPOST 0・pageerror 0。外部通信は遮断。独立probeの算数通知設定は無効であり、通知のmock payloadと親抑止は必須 `math_passage` suiteで別途検証してPASS。

初回probeはchoice問へ自由記述の合成誤答を投入し、既存validatorが「選択肢が不正です。」と正しく拒否してexit1。これはQAfixtureの誤りで、製品修正やassert緩和はしていない。実選択肢から誤答を選ぶfixtureへ修正後、同原因2回目でexit0。両試行のlog/JSONを保存。2回目は2026-11-27 15:13:53–15:13:58 UTC、5.248秒、実行前後HEAD固定・clean。

`onin-parent.png` と `math-normal.png` を実際に視認し、理由・正誤/解説・親表示・算数段階の表示を確認。画像はfull-page captureであり実機iPad/Safari確認とは扱わない。他2画像は取得済み。

## 制約

全て合成データ・localhost・mockで検証。個人回答/教材写真/メール/Driveは未使用。実通知、外部投稿、公開、デプロイ、権限/Secrets変更、product編集、pushは未実施。QA合格はCEO承認・本番確認を意味しない。元チャットのCEO返答は未読で承認扱いにしない。新main由来の製品機能設計の全面再審査、Safari実機、公開先のCloudflare検証は本QAの範囲外。

## 全suite実行結果

| Suite | Exit | 秒 |
|---|---:|---:|
| tests/onin_review.py | 0 | 5 |
| tests/kamakura_review.py | 0 | 4 |
| tests/cloud_preview.py | 0 | 1 |
| notifications/test/worker.test.mjs | 0 | 1 |
| notifications/test/browser.py | 0 | 10 |
| tests/study_reports.py | 0 | 30 |
| tests/cloud_bootstrap.py | 0 | 2 |
| tests/generator_preservation.py | 0 | 0 |
| tests/adaptive_practice.py | 0 | 3 |
| tests/adaptive_daily.py | 0 | 4 |
| tests/adaptive_quality.py | 0 | 4 |
| tests/flash_grading.py | 0 | 9 |
| tests/spaced_daily.py | 0 | 5 |
| tests/history_compat.py | 0 | 4 |
| tests/edo.py | 0 | 16 |
| tests/medaka.py | 0 | 18 |
| tests/lever.py | 0 | 5 |
| tests/math_passage.py | 0 | 4 |
| tests/microscope.py | 0 | 22 |
| tests/science_adaptive.py | 0 | 11 |
| tests/registered_answers.py | 0 | 3 |
| tests/history_review_regression.py | 0 | 3 |
| tests/state_review_regression.py | 0 | 4 |
| tests/prototype_storage.py | 0 | 9 |
| tests/focus_data.py | 0 | 1 |
| tests/focus_practice.py | 0 | 12 |
| tests/parent_mode.py | 0 | 21 |
| tests/design_c.py | 0 | 27 |
| tests/responsive_subjects.py | 0 | 122 |
| tests/recommended_review.py | 0 | 7 |
| tests/review_entry.py | 0 | 3 |
| tests/daily_count.py | 0 | 5 |
| tests/science_daily_count.py | 0 | 8 |

`generator_preservation` は新算数HTMLを含む全trackedファイルを独立一時コピーで12 generator順に2pass再生成し、初回byte保持と再実行不変を検証してPASS。`math_passage` は24問を別計算で確認、通常stage0完了・stage3途中終了のmock通知、親stage1完了/途中終了のenqueue抑止をPASS。`recommended_review` 等は選定理由・優先順・採点・既存記録保持・reload/import互換性をPASS。必須全suite再試行は行っていない。
