合成教材を学習に使う前に、原本・転記・問題案を見比べて編集・個別確認し、確認済みの案を保存せず試し解きできる「教材の確認室」を追加します。問題文・許容表記・選択肢・ヒント・解説を保護者役で点検する試作です。

全問を現在の版で明示確認した案だけを出題します。短答はNFKC＋前後空白除去後の完全一致、選択問題は選択項目と登録正答の一致で判定します。採点前の正答・解説は非表示、ヒントは明示操作で開きます。開始できない場合は原因と確認・修正する欄への導線を示します。

- 回答はメモリ内だけで、次問・終了・ページ離脱時に消去します。案JSON・確認状態・未保存状態を変えず、学習履歴や累計点を保存しません。
- 試行中は編集画面をhidden/inertにし、編集・案切替・JSON入出力を実行時にも遮断します。不整合・表示再構築で試行を終了し、古い操作を無効にします。
- 未解決箇所の確認拒否、編集/再入力時の確認失効、JSON出力、次の作業案内、後着のJSON取込による編集上書き防止を保持します。

現在main `60d1a946cc02ed8acea54c0d7af7d6451fcc30ec` を既存PR11の履歴を保持してtopic branchへ統合しました。江戸・メダカ・顕微鏡とrecall履歴のある学習環境に追従し、限定プレビューで江戸と確認室の両方へ到達できるようにしています。確認室はmainの新回答形式を読み書きしません。mainの教材/学習HTML/共通assets/親runtimeと、旧PR11のcontent HTML/合成fixture/固定hashを保持します。PR10独自改善・テーマPR12は取り込んでいません。

検証対象HEAD: `d75a5469fbf1e8c5011a6307308546e5ec669ceb`。実装者とは別の `qa_content_trial_delivery` が固定clean候補を直接確認しました。

`bash scripts/check_all.sh` 初回29/29成功、exit0、325秒。前後clean・HEAD一致。

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 3 |
| `notifications/test/worker.test.mjs` | 0 | 0 |
| `notifications/test/browser.py` | 0 | 12 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 3 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 9 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 16 |
| `tests/medaka.py` | 0 | 17 |
| `tests/microscope.py` | 0 | 23 |
| `tests/science_adaptive.py` | 0 | 9 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 13 |
| `tests/parent_mode.py` | 0 | 21 |
| `tests/design_c.py` | 0 | 21 |
| `tests/responsive_subjects.py` | 0 | 122 |
| `tests/content_review.py` | 0 | 4 |
| `tests/content_guidance.py` | 0 | 3 |
| `tests/content_import_guard.py` | 0 | 3 |
| `tests/content_trial.py` | 0 | 3 |

独立の限定HTTP/UI・静的照合も初回成功。確認→回答→採点→終了→案JSON出力→未回答で再開始を実DOM操作し、元案/確認状態/unsavedを保持、試行結果のJSON非混入、観測範囲の保存書込・非許可ブラウザー要求・pageerror 0を確認しました。江戸親モードの本人履歴保持は専用suiteで確認。共有接点以外のmain84filesと旧content12pathsはbyte一致。隔離コピーで生成器の冪等性と改変contentの書込前拒否、未知HTMLの親preflight拒否を検証しました。限定HTTPではcontent/江戸GET 200、未知経路404、HEAD405、loopback API POST501を確認。これは実通知ではなく拒否試験です。HTTP本文を早期closeしたハーネス由来のBrokenPipeログ1件を保存し、assert成功・ブラウザー例外0と区別しています。

過去のee51e68（26suite・65ケース）検証は履歴として保持し、今回候補の実行証拠へ読み替えません。今回もクラウドChromiumと合成記録・mock通知のみ。既存検証済venvの手動再利用であり、自動snapshot引き継ぎ成功ではありません。本人試用・実機Safari/WebKit/iPad・実BFCache・学習効果・公開画面は未確認です。

OCR/自動生成/実教材接続/学習アプリへの教材導入は含みません。D04方向性採用は維持し、D02の実入力/非公開保存先は未決です。draft・未マージで、本番マージ/公開/手動deploy/実送信/課金/Secrets・アクセス変更は行っていません。正本チャットの新CEO返答実読は0です。

[仕様・分担・今回のテスト証拠・次の一手](https://github.com/naoyanakajima-cyber/yuika-study/blob/codex/agent-team-operations/ops/runs/2026-11-15-content-main-compatibility.md)。外部ビルドcheckはクラウド内QAと別に記録します。

現在HEADの外部check：2026-11-15 09:16:20 UTCの [Workers Builds: yuika-study](https://github.com/naoyanakajima-cyber/yuika-study/runs/132763996602) はfailureです。取得したcheck情報に原因詳細はなく、旧HEADの失敗と同一原因とは断定しません。クラウド内29/29成功と区別し、外部ビルド再実行・設定変更・手動deployは行っていません。
