# 独立QA：理科の日次実問数とトップ名称の整合

担当 `qa_daily_residual`。候補 `73fe2ee9d776b3e3360614752fb722ff4aee4f85`、基点 `55435567d44f05dc35f3ea6d73c4ba9cac2dc496`。合成データだけを使用し、製品編集・commit・push・追加子起動は行わない。

判定：今回の理科日次表示とトップ名称の範囲は独立QA合格。採用、mainへのマージ、公開、実機Safariの成功を意味しない。

## 固定HEADの必須検証

`bash scripts/check_all.sh` を1回実行し26/26 suite成功、全exit 0、runner310秒。開始2026-11-14T21:08:43.174654+00:00、終了2026-11-14T21:13:54.013743+00:00。前後のHEADは73fe2ee9d776b3e3360614752fb722ff4aee4f85で一致、両方clean。検証中の製品編集・commitなし。各suiteの結果はsuites.json、原出力はsuite.log、前後記録はsuite-meta.json。

新しいscience_daily_countは28の純関数オラクル例と実UI4条件・防御境界・通常/親top導線を含む。これはEngineer作成の回帰suiteを独立に実行した結果で、以下の独立ハーネスとは分ける。既存24/25suiteの成功を今回候補へ流用していない。

## 独立実UI：7例

768×1024、fresh Chromium contexts、空の合成履歴。最初の問数確認は実際の単元select・5/10buttonと開始buttonを使い、問題配列・clock・乱数を上書きしていない。

- 全単元5設定：開始前5問、開始後5問。
- 全単元10設定：開始前10問、開始後10問。
- 実験器具10設定：開始前8問、開始後8問。
- 水溶液と溶解10設定：開始前9問、開始後9問。
- 親確認モードの実験器具10設定：開始前8問、開始後8問。
- 通常top→保存済み理科/実験器具10設定：1回クリックでdaily=1経由の8問開始。
- 親top→同条件：1回クリックで8問開始、親active/bannerとlocalStorage非保存を維持。topの実DOMは「再確認0問＋弱点の練習0問＋通常8問」「前回の単元から（問数は単元の設定）」と表示。

全開始時に回答履歴は0件のまま。通常/親の器具例では実際の選択肢回答→答え合わせ→保存→reloadを実施し、mode daily・正解・1件保持を確認。旧キー/無関係キーを保持。親例では全localStorage byte相当のソートJSONが不変で、回答は親storageに保持された。これは合成の回答であり本人データではない。画像はbuttonへスクロール後のviewportで、初期画面の見え方と同義ではない。

## 独立防御境界：5例

別contextの合成状態操作として、表示後5→10へ設定が変わった場合は乱数消費0・sessionなし・home維持で表示更新/再確認案内、blocked/dirtyは直接daily開始拒否と可視の休止理由、存在しない合成単元は0件拒否と説明を確認。未来日時は実際の合成回答をvalidatorが受理する10分先のレコードに変え、日次停止と時計案内を確認し、履歴を空へ戻して開始可能に復帰した。理科の通常UIに0候補単元は存在せず、0件を実UI利用例とは扱わない。blocked/dirtyのこのprobeは内部状態注入であり、実保存例外は必須science_adaptive等の別suiteが対象とする。

## 独立選定同等性：16例

実アプリにvalidator受理の合成履歴（期限/弱点）または空履歴を用い、全単元・実験器具・水溶液と溶解・合成0単元 × 5/10上限 × 履歴あり/なしを比較。基点のscienceDaily本体と候補を同一の固定clock/乱数列で呼び、ID配列・順序・乱数消費が一致。renderの乱数消費0、表示数と実候補数の一致も確認。この固定clock/乱数注入は上の実UI7例とは別。

## 静的保持と生成器

基点相対12ファイルに限定。index、summary生成器、progress生成物、既存4テストは「今日の5問」→「今日の復習」のexact置換以外byte一致。既存4テストはexact locatorを新名称へ合わせたのみで、判定・URL/選定/保存assertは不変。理科HTMLはSCIENCE_ADAPTIVE block以外byte一致。応仁/鎌倉/平安/重点4HTML、adaptive.js、design.js/css、parent生成器はbyte一致。計16項目、その他対象外pathの変更なし。

独立git archiveでembed_science→build_summary→design embed→parent embedを実行し各exit0、6HTMLとassets/progress.jsの生成前後hashが一致。稼働中checkoutは編集しない。

前run終了処理回復2428174→f5aae8eも静的確認。以前129run、全ticket、権限・決定等保持。前runのPR9未実施記録訂正、metadataレビュー保存、中断/次run回復追記を明示し、終了時刻や解除成功を遡及していない。49証拠hash一致。これは新しい製品テストではない。

## 試行・限界

独立probeは3起動で分担した。初回は実UI6例成功後、親モードでURLにparent-check=1が残るとした期待が失敗。既存実装はsessionStorage利用可能時にURLflagを除去し、temporary時だけ付与するため、banner/active/隔離保存を確認するよう1回修正。2回目で残る親topと境界5例成功後、選定fixture sessionId qa-rngが既存の8文字minimumに拒否。synthetic-rng-sessionへ1回修正し、3回目で選定16例のみ完了した。各原因2試行以内、製品不具合0。一発で全例が通ったとは報告しない。失敗時のハーネスと結果も保存。

3起動合計で公開font GET22件を遮断し、top用公開CDN library GETを9回取得（各起動3件、3回目は未使用）。独立probeのサーバーPOST到達・pageerrorは0。上記evaluate/assertハーネス例外2件とpageerror0は別。全suiteは公開CDN読取りとmock通知を含むので、全体外部要求0ではない。実メール/Chat・実通知送信はしていない。

実機iPad/Safari、本人試用、学習効果、公開環境、完全な別タブ/削除同期は未検証。snapshot自動引継ぎの証拠ではなく既存venvの手動再利用。外部Workers Buildsの状態は統括が別途読戻し、ローカル成功から公開成功を推定しない。
