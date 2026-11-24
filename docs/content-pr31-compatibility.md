# PR11とPR31の互換同期

2026-11-24、Engineer `engineer_content_pr31`。PR11の開始HEAD `3920f1642692c88a8d6870480bc3f98f71558d24` にmain `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`をtopic上で統合した。競合なし。mainへのマージではない。

## 保持と変更

教材確認HTML、教材仕様・合成fixture、CONTENTの5試験、PR11自身のscience/prototype生成元は開始HEADとbyte一致を確認した。確認後編集による確認解除、JSON入出力、保存しない文字・画像試行を維持する。PR10の理由付き復習・日次実問数は取り込まず、PR11の「今日の5問」を保持した。

mainの完了・途中終了通知を取り込み、通知試験へ移動取消・全対象の未回答終了・親モード中の本人localStorage不変のassertを追加した。実行時の予定問題数と報告の回答数も照合する。既存32本とmain27本の必須suiteの和集合は33本である。

## 生成保持の診断と修正

通知・江戸・模試・教科別加工を生成列に追加した初回検査はexit 1、0.582秒。初回の差分は `edo-review.html`、`mock-focus-review.html`、`assets/progress.js`。使い捨てコピーのdiffで、理科HTMLから江戸を複製するとてこ専用処理が混入し進捗生成へ伝播すること、親境界が通知マーカー内に入ることを確認した。模試の差分はマーカー順だけであり、PR10固有のおすすめ除去は不要だった。

江戸は既存江戸HTMLをテンプレートとして `questions.build()` の問題定義を更新し、従来どおり履歴archiveを保持する。理科・prototypeアダプターの変更は、江戸への適用可否を検討して明示同期する必要がある。通知・history・design・parentは共有生成元から再埋め込みする。この制約はREADMEと生成元にも記載した。

親境界は通知開始マーカーより前へ置く。CONTENTのhash検証と除外は保持する。修正後の生成検査は初回から全追跡ファイルのbyteを保持し、2回目も不変。strict assertは変更していない。同原因の修正再検証は1回。

## Engineer検証

クラウドの独立worktreeで、無視対象 `.venv/bin` から既存 `/workspace/yuika-study/.venv/bin` を手動再利用した。各Pythonシェルで `source scripts/cloud/activate.sh` を実行した。保存済み環境の自動適用成功は主張しない。

以下はコミット前の作業treeで実行し、各コマンドの終了コード・所要時間を回収した。新規browser context、合成入力・設定、通知mockのみ。通知7ケースで16報告がWorker契約と配信stubを通過し、完了・途中終了・未回答・移動取消・重複抑止・親モード隔離を確認した。CONTENT試験5本、てこ、prototype保存も初回成功。

| コマンド | Exit | 秒 |
| --- | ---: | ---: |
| `python tests/generator_preservation.py` | 0 | 1.02 |
| `python tests/study_reports.py` | 0 | 28.261 |
| `python tests/content_review.py` | 0 | 3.562 |
| `python tests/content_guidance.py` | 0 | 2.384 |
| `python tests/content_import_guard.py` | 0 | 2.917 |
| `python tests/content_trial.py` | 0 | 3.379 |
| `python tests/content_image_trial.py` | 0 | 2.846 |
| `python tests/lever.py` | 0 | 5.028 |
| `python tests/prototype_storage.py` | 0 | 8.538 |

[機械可読の検証記録](verification/content-pr31-engineer.json)にstdout、初回生成失敗、保護対象hashとsuite和集合を保存した。`git diff --check`も成功した。

固定commitでの `bash scripts/check_all.sh` 全33本と768×1024の通常／親操作は独立QA担当が実施する。ここでは実施済みとしない。Safari/WebKit・実機iPad・本人試用・学習効果・実配送・公開画面は未確認。CDN読込みを持つ既存試験があり完全オフラインとは呼ばない。push・mainマージ・公開・設定変更・実通知は実行していない。
