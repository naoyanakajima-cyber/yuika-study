# CONTENT-MVP 合成画像の確認・試し解き：独立QA

Reviewer `qa_content_trial_delivery`、実装者 `engineer_content_trial_delivery` とは別担当。cycle34、2026-11-15。正本仕様・PrM範囲・台帳leaseを読取り、freeze通知後だけ製品候補を検証。対象は独立checkout `/workspace/yuika-content-image-trial-20261115`、固定HEAD `1678519f916471ba6e38044855de240bd6c4a807`、基点d75a546。試験開始時clean。製品/ops編集・push・公開・設定/権限変更・実送信なし。既存venvの手動再利用であり、自動snapshot引継ぎ成功とは扱わない。

## 仕様・差分・memory-only境界

変更10pathsを読み、3つ目の合成サンプル/入口、ASSETSの既知三つ組対応、固定hash2箇所、同梱SVG/JSON、対応する仕様/説明/検証だけの範囲と確認。旧97filesは基点とbyte一致。7学習/ホームHTML、共通assets、問題ID/キー/recall/履歴/親runtime、通知コード、限定serve、旧4fixtureは不変。

変更HTMLのCSPとvalidateShape〜sourceAsset直前、trialReady以降の試行/終了/離脱処理は基点と一致。新しいstorage/cookie/通信APIや外部scriptなし。ASSETSは3つの信頼済みliteralで、kind/sourceId/locatorの三つ組は重複せず、各contentは同梱原本のbyteと一致。SAMPLES全3件はfixture JSONと一致する。画像のinnerHTMLは三つ組完全一致で選んだasset.contentだけを受け取り、JSONの本文/URLを渡さない。note/原本labelは文字列として表示する。

新SVGの要素・属性をXMLとして確認し、script/image/外部参照/イベント属性なし、title/descあり。600×320内の出典領域page:1;region:100,60,400,220は、三辺の図形と「三角形の辺は3本です。」の根拠文を包む。表示の注記は合成の確認待ち転記であってOCR結果ではないと説明する。初期案はdraft/未解決1件、aliases/readings/options空。意味一致の機械保証を新規条件にしていない。

content SHA256 `b978ea0ebd725cbe0b0b45275ad19d7be4ee78e64fb5c7e40947fe05475560f4` が生成器/親preflightの2箇所で一致し、両ファイルのhash以外の実行ロジックは不変。git archive隔離コピーで親preflightが正常候補を受理、保護なし未知HTMLを拒否。content改変を生成器が全HTML書込前に拒否し、親preflightも拒否した。固定hashを合わせただけの自己承認ではなく、上記の差分と動的非書込を独立確認した。

## 独立15ケースと視認

fresh Chromium context、768×1024、合成fixture/合成保存sentinelだけを使用。サンプル選択・転記とresolution修正・確認・回答・採点・終了・JSON保存/再入力は実DOMで操作した。

- 新SVGと確認待ち転記を同時表示。未解決で確認/開始不可。未確認案のdownload→reimportは同じ原本を表示しdraftを維持。
- 転記を「三角形の辺は3本です。」、resolutionを「3」へ手動修正し、各操作でrevisionが1増加、quote/candidates保持。確認前は開始不可、キーボードでの明示確認後に開始可能。
- 回答3は一致、4は不一致。試行中の案/確認/unsavedは不変、終了でtrial/DOMを消去。隠れた新旧sample操作とJSON出力の実行時ガードも拒否。案JSONは元proposalと一致し、回答・結果・assetコードを混入しない。
- 確認済みJSON再入力で全確認失効、再確認後の編集で再び開始拒否。破棄確認の拒否は元案を保持。旧判読不明画像は未解決のまま拒否、旧text/新画像の切替・再入力は正しい原本を表示。
- kind/sourceId/locatorの不一致、URL風locator、SVG風locatorは原本表示/確認/試行を拒否。構造が正しいJSONを修正用の案として読み込める既存仕様は維持する。原本名のHTML風文字列は文字列表示で実行されない。

開始・確認・案内のkeyboard/focusを実測。原本と確認待ち転記の限定PNG `source-and-transcription-768.png`、採点画面 `trial-match-768x1024.png` を目視し、図・辺番号・根拠文・合成/OCR注記、入力値/一致/正答/解説/終了が読めることを確認した。画像は今回の合成fixtureの表示証拠だけで、実写真/OCR/本人理解度の証拠ではない。

probeの監視範囲でStorage/history/cookie/IndexedDB/Cache/SW書込み0、非許可ブラウザー要求0、pageerror0、window.name空、sessionStorage空。試験前に置いた合成の子履歴sentinelはbyte同一。通信許可はloopback content GETのみ、その他はabort。実データは取得していない。

## 試行履歴

独立UI probe初回は、`trial-repair`の移動先をresolution-0と誤期待したハーネスassertで停止した。既存コードを再読すると、trial-repairは一般の不足理由issues-0へ、上部next-stepが未解決resolution-0へ移動する契約だった。製品を変更せず、両導線を分けて検査するよう/tmpハーネスを修正。2回目で15ケース完走。初回は初期表示とdraft出入まで実行し、解決後の試行検証には達していない。初回スクリプト/ログはattempt1に保存。製品不具合や無診断反復による成功とは扱わない。

静的/隔離負例は初回成功。全必須suiteには既存29件と新content_image_trialの1件が含まれ、重複なし30件と直接照合。Engineerのfocused2suiteや旧65ケース独立probeは今回の独立試行数に加算しない。旧65probe全体は再実行しておらず、今回候補の必須content各suiteと変更接点の独立15ケースを根拠とする。

## 限界

合成データとChromiumのみ。実機Safari/WebKit/iPad、本人試用、学習効果、実写真/OCR/教材本体登録、D02実接続、実BFCacheヒットは未確認。全必須suiteには公開JS GETとmock通知試験があり、全体外部要求0とは主張しない。外部Workers Buildsの状態・本番配信の成否を独立QAの合格と同一視しない。

## 最終判定・全suite結果

2026-11-15T10:16:40.297838+00:00 に固定候補HEAD/cleanを再確認。**独立QA PASS、blocking 0、既存draft PR11更新・CEO判断待ちへ進行可**。本番マージ/公開承認ではない。全30suiteは初回で終了0・332秒。開始側ログ作成時刻 2026-11-15 10:10:00.603127602 +0000、全結果書込完了mtime 2026-11-15 10:15:32.316726157 +0000。これはファイル時刻の観測で、shellが報告した総秒数と区別する。

| Suite | Exit | 秒 |
| --- | ---: | ---: |
| tests/onin_review.py | 0 | 5 |
| tests/kamakura_review.py | 0 | 4 |
| tests/cloud_preview.py | 0 | 2 |
| notifications/test/worker.test.mjs | 0 | 1 |
| notifications/test/browser.py | 0 | 11 |
| tests/cloud_bootstrap.py | 0 | 2 |
| tests/adaptive_practice.py | 0 | 2 |
| tests/adaptive_daily.py | 0 | 4 |
| tests/adaptive_quality.py | 0 | 4 |
| tests/flash_grading.py | 0 | 9 |
| tests/spaced_daily.py | 0 | 5 |
| tests/history_compat.py | 0 | 3 |
| tests/edo.py | 0 | 17 |
| tests/medaka.py | 0 | 18 |
| tests/microscope.py | 0 | 23 |
| tests/science_adaptive.py | 0 | 8 |
| tests/registered_answers.py | 0 | 3 |
| tests/history_review_regression.py | 0 | 3 |
| tests/state_review_regression.py | 0 | 4 |
| tests/prototype_storage.py | 0 | 8 |
| tests/focus_data.py | 0 | 0 |
| tests/focus_practice.py | 0 | 13 |
| tests/parent_mode.py | 0 | 21 |
| tests/design_c.py | 0 | 20 |
| tests/responsive_subjects.py | 0 | 125 |
| tests/content_review.py | 0 | 4 |
| tests/content_guidance.py | 0 | 2 |
| tests/content_import_guard.py | 0 | 4 |
| tests/content_trial.py | 0 | 4 |
| tests/content_image_trial.py | 0 | 3 |

証拠は `final-result.json` / `check-all.log` / `static-result.json` / `identity.json` / `asset-review.json` / `probe-result.json`。初回ハーネス診断は `attempt1/`、最終15ケース成功は直下。画像2枚は実表示を目視済み。全証拠のハッシュは `SHA256SUMS`。次は統括がlease/既存PRHEADを再確認し、通常push・draft本文/台帳保存・lease解除を行う。
