# Independent compatibility QA — REV-MVP / PR10

判定: **PASS**。実装者 `engineer_rev_lever_compat` とは別の `qa_pr30_impact` が実行。残るblocking指摘なし。

最終HEAD: `804f9f648c8634ea26d4ca7fc26cf6b473029475`。対象はPR10とてこ追加mainの互換性であり、新規てこ28問の物理・教材内容の独立した完全監査ではない。

## 全suiteの実測

- 初回HEAD `566e4674e9d54482d3043d4be6ff10dcd780d303`: 29/30成功、exit 1、361秒（wall 360.41秒）。
- 2回目HEAD `804f9f648c8634ea26d4ca7fc26cf6b473029475`: 30/30成功、exit 0、323秒（wall 322.62秒）。
- 2回目開始 `2026-11-22T13:15:11.607048+00:00`、終了 `2026-11-22T13:20:34.223585+00:00`。
- 初回の失敗は `tests/science_adaptive.py:209` が旧ボタン名「今日の5問をはじめる」を参照し、30000ms Timeout。実装者が新名称「今日の復習をはじめる」へ1行修正。2回目の全suiteが再試行を兼ね、独立した3回目試行はしていない。
- 両回とも `source scripts/cloud/activate.sh` 後に `bash scripts/check_all.sh`、seed `20261110`。既存検証済みvenvを手動symlinkし、完了後解除。自動snapshot引き継ぎ成功とは扱わない。両checkoutは最終 `git status --short` 空。

| Suite | 初回 exit | 初回秒 | 最終 exit | 最終秒 |
|---|---:|---:|---:|---:|
| `tests/onin_review.py` | 0 | 4 | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 3 | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 3 | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 1 | 0 | 0 |
| `notifications/test/browser.py` | 0 | 14 | 0 | 11 |
| `tests/cloud_bootstrap.py` | 0 | 2 | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 2 | 0 | 2 |
| `tests/adaptive_daily.py` | 0 | 4 | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 | 0 | 4 |
| `tests/flash_grading.py` | 0 | 8 | 0 | 8 |
| `tests/spaced_daily.py` | 0 | 5 | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 | 0 | 4 |
| `tests/edo.py` | 0 | 16 | 0 | 15 |
| `tests/medaka.py` | 0 | 17 | 0 | 17 |
| `tests/lever.py` | 0 | 4 | 0 | 4 |
| `tests/microscope.py` | 0 | 23 | 0 | 22 |
| `tests/science_adaptive.py` | 1 | 38 | 0 | 9 |
| `tests/registered_answers.py` | 0 | 3 | 0 | 2 |
| `tests/history_review_regression.py` | 0 | 3 | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 4 | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 7 | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 | 0 | 0 |
| `tests/focus_practice.py` | 0 | 12 | 0 | 11 |
| `tests/parent_mode.py` | 0 | 20 | 0 | 20 |
| `tests/design_c.py` | 0 | 20 | 0 | 20 |
| `tests/responsive_subjects.py` | 0 | 117 | 0 | 117 |
| `tests/recommended_review.py` | 0 | 6 | 0 | 6 |
| `tests/review_entry.py` | 0 | 3 | 0 | 4 |
| `tests/daily_count.py` | 0 | 6 | 0 | 5 |
| `tests/science_daily_count.py` | 0 | 8 | 0 | 8 |

## 独立ブラウザー操作 — 13ケース、10 fresh contexts

実行HEADは `566e4674e9d54482d3043d4be6ff10dcd780d303`。最終 `804f9f6` でprobeを再実行したとは扱わない。両HEAD差分はテストlocator 1行だけで、製品HTML・生成progress.js・生成元等のblob一致を `product-equivalence.json` に保存した。

- メダカ/江戸 × 通常/親モードの4ケース（4 contexts）: 途中離脱は未保存、補助選択後の最終回答だけ1回保存、reload/重複submitで増えない。保存イベントcorrect=trueを保ち、弱点投影はcorrect=false・日次優先。scienceの旧choice履歴は任意field追加なしで保持。投影によるraw/state変更なし、親モードは本人storage byte一致。不足firstResponseは拒否・保存不変。
- 単元日次入口3ケース（3 contexts）: 器具10問設定→8、メダカ→5、未知単元→全体5。表示・summary・開始実問数が一致。理科全112問、メダカ17問、単元混入なし。
- てこ6ケース（3 contexts）: 初回5問は全てstep0（画面の段階1）、初回10問はstep0から開始し挑戦なし。トップホームからてこ5問へ再開。重複正解/ヒントありで解放せず、異なるstep3（画面の段階4）2問のヒントなし正解で挑戦解放し、日次にも挑戦を含む。挑戦専用はstep4の2問。誤答時に同概念1段階下を1問追加し2→3問へ進行表示が追従、補助問題誤答時の再帰追加なし。

768×1024 touch Chromium、10個の新規context、合成データのみ。PreviewHandler CSPを維持し、ブラウザーの非loopback通信は遮断（トップホームの公開ライブラリ3件はcurl取得したbytesをローカルfulfill）。外部フォントGET試行は遮断、観測POST/pageerrorは0。既存通知suiteはmock。

てこprobe wall時間10.12秒。recall probeは別途所要時間を計測していない。両probeは初回成功。PNG2枚を目視確認し、ホーム再開の問題・図・選択肢と補助問題の解説表示を確認。補助問題PNGは回答後のフォーカススクロール位置であり、件数追従の根拠はDOM assertion。

## 限界と保存

実機iPad/Safari、本人試用、公開画面、実通知は未検証。補助回答・挑戦解放・補助追加では対象sessionを明示設定して実際の操作を行い、全段階の自然な連続学習を再現していない。旧/new混合履歴はscienceで確認し、江戸に旧pre-recall形式はない。過去QAを今回実績へ転用していない。

保存資料: `summary.json`、両attempt-result.json、`product-equivalence.json`、両probe.py/result.json、`lever-home-resume.png`、`lever-remedial-count.png`。完全ログはローカルに保持し、公開保存用の全30行は上表で提供する。QAによるコード・台帳編集/push/公開/通知/子spawnなし。
