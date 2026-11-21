回答記録から復習候補と理由を示し、開始前に今回の実問数を確認できるようにします。たとえば理科の実験器具で10問を指定して候補が8問の場合、「今回は8問」と表示し、実際にも8問で開始します。

応仁・鎌倉の「おすすめ復習」は誤答、時間を置いた確認、ヒント付き正解の理由を表示し、ホームから到達できます。日次の「今日の復習」は既存の期限到来→弱点→通常問題の順序を維持し、応仁・鎌倉・平安・重点・理科・江戸の実問数を表示します。候補0件と記録を読めない状態を区別し、設定変更後の開始時にも件数を確認します。

現在main `60d1a946cc02ed8acea54c0d7af7d6451fcc30ec` を既存PRの履歴を保持してtopic branchへ統合しました。理科84問・江戸22問と既存問題ID/保存キー/検証処理を維持し、メダカ・江戸の選択肢を使った正解は復習上の弱点に残します。保存済みの最終正誤や回答履歴は書き換えません。理科の生成後に江戸も生成する手順をREADMEに記載しました。

対象は既存draft PR10です。理由付きおすすめ入口は応仁・鎌倉の範囲です。教材追加PR11・テーマPR12の採用は含みません。再確認間隔1/3/7日は仮案です。mainへのマージ・公開は未承認です。

検証対象HEAD: `6d01386dba0bb3cdafa7e8f431a6a17bc81e913f`。実装者とは別の `qa_theme_compatibility` が固定clean HEADで検証しました。

`bash scripts/check_all.sh` 初回29/29成功、exit0、349秒。2026-11-15 08:26:18 UTC完了、前後clean・HEAD一致。

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 0 |
| `notifications/test/browser.py` | 0 | 12 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 2 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 9 |
| `tests/spaced_daily.py` | 0 | 7 |
| `tests/history_compat.py` | 0 | 5 |
| `tests/edo.py` | 0 | 15 |
| `tests/medaka.py` | 0 | 18 |
| `tests/microscope.py` | 0 | 23 |
| `tests/science_adaptive.py` | 0 | 8 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 6 |
| `tests/prototype_storage.py` | 0 | 9 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 13 |
| `tests/parent_mode.py` | 0 | 21 |
| `tests/design_c.py` | 0 | 23 |
| `tests/responsive_subjects.py` | 0 | 129 |
| `tests/recommended_review.py` | 0 | 6 |
| `tests/review_entry.py` | 0 | 4 |
| `tests/daily_count.py` | 0 | 5 |
| `tests/science_daily_count.py` | 0 | 9 |

独立操作確認は7個の新規ブラウザーcontextで実施。器具10問設定→表示8/実8、メダカの有効単元入口、不明単元の全84問へのfallback、メダカ・江戸の通常/親モードでassisted履歴を復習先頭に保持し件数一致、元履歴不変、本人領域隔離を確認しました。独立静的照合では全6画面の問題/ID/キーがmainと一致し、理科・江戸のadaptive領域以外とrecall/parent/history実装の維持を確認しました。

検証はクラウドChromiumと合成データ、通知mockのみ。既存の検証済みvenvを手動再利用し、各shellでactivateしました。自動snapshot引き継ぎ成功の証拠ではありません。実回答・教材写真・実送信なし。実機iPad/Safari、公開画面、本人試用は未確認です。現mainの別検証25/25成功は候補29suiteとは別のbaselineです。旧アプリへの新形式JSONの後方読込や全面的な複数タブ同期は保証しません。

仕様・担当・テスト証拠・次の一手: [運用記録](https://github.com/naoyanakajima-cyber/yuika-study/blob/codex/agent-team-operations/ops/runs/2026-11-15-review-main-compatibility.md)。CEOの返答が正本チャットから台帳へ記録されるまで、新しい採用・公開承認とは扱いません。

外部check（2026-11-15 08:27:48 UTC）: 同HEADの [Workers Builds: yuika-study](https://github.com/naoyanakajima-cyber/yuika-study/runs/132752305706) はfailure。取得情報には原因の詳細がなく、ローカル29suite成功とは区別します。外部ビルドの再実行・設定変更・手動deployは行っていません。旧headの失敗と同一原因とは断定しません。
