# 独立QA：日次練習の実問数表示

担当 `qa_daily_count_fix`。実装者 `engineer_daily_count_fix` と別担当。固定対象 `55435567d44f05dc35f3ea6d73c4ba9cac2dc496`、基点 `132f9f59ebd23b6dab33e7d1e23bf4d077b8070d`。製品checkoutへの書込み/pushなし。

## 差分・保持確認

変更は許可した9ファイルのみ（adaptive生成元、4HTML、design.js、README、テスト1本、check_all登録）。4HTMLのADAPTIVE区間以外が基点と完全一致し、既存推薦・教材・採点・保存・通知・親モードの埋込コードを維持。理科source/HTML、index、progress、親/prototype runtimeの6ファイルも一致。計10の保存確認に加え、その他全repoパスに差分なし。

独立したgit archiveでpractice→build_summary→design→parentを実行。全工程終了0、6HTMLとprogress.jsの前後hash一致。製品checkoutを生成実験に使っていない。

件数はdue/weak/normalをorigin単位で重複排除する。count/guard/選定は同じ呼出し内のnowを共有し、表示ではshuffleを使わない。既存adaptiveStatusの説明用時計読取は維持されるが、数量/選定への新不具合は再現していない。

## 独立した実UI確認

768×1024 Chromium、新しい空履歴contextで実際の設定コントロールだけを操作した。UI問数確認では候補関数やdailyQuestionsを余分に呼ばず、問題・履歴・乱数・時計を差し替えない。

|例|確認した結果|
|---|---|
|A 応仁5選択|開始前5問→実5問|
|B 応仁10選択|開始前10問→実10問|
|C 応仁の乱/漢字/5選択|開始前4問→実4問。回答・採点・daily保存・再読込も成功|
|D 応仁d2/将軍/通常|0問ボタン無効、条件見直し説明が可視、直接開始してもhome維持|
|E 平安ペア/藤原氏と政治/10選択|開始前2問→実2問|
|K 鎌倉初期|開始前5問→実5問|
|F 重点復習初期|開始前5問→実5問。確認方法selectは存在せず、実際のnormal設定を確認|
|P 親確認モードのC|4問で開始・回答・採点・保存・再読込。session側だけ、全localStorage不変|

全例で開始だけでは回答履歴が増えず、C/Pでは旧キーと別キーの合成sentinelを保持した。8例を一発で通したものではない。UI probeは3起動で、初回A/B/C後にDの期待文末「。」を落としたexact locatorが失敗、2回目D/E/K後に重点復習にないvariant selectを待つ汎用ハーネスが失敗。各原因を1回修正し、3回目は未完了F/Pだけ実行。各版のsource/log/resultsを保存し、製品失敗とは区別した。

## 独立した選定同等性・境界確認

実際の応仁アプリへ検証済み形式の合成の期限/弱点履歴を入れ、基点からそのまま抽出した旧dailyQuestionsと候補の関数を同じ固定乱数列で比較した。上限5/10/15×分野all/応仁の乱/不存在×通常/漢字の18例で、問題ID・順序・乱数消費数が一致し、dailyCountの乱数消費0、実長と一致。renderも追加乱数0。これは別のオラクル試験であり、前段の実UI例に乱数を差し替えたものではない。

既存storageイベント経路へ有効な非null合成記録を渡してvalidate/merge/render後の未来停止を確認。直接開始も拒否。時計が追いついた後の既存refreshで再開可能になり、回答途中のrefreshは入力を消さない。新たなstorage同期・削除同期・マイグレーションを検証済みとはしない。

このprobeの初回は合成日時で必須ミリ秒表記を省きvalidatorに拒否された。fixtureのみ1回修正し2回目成功。製品validatorは変更していない。UI2原因とこの1原因の各修正は1回で、同原因を繰り返して通した結果ではない。

UI probe3起動で外部公開font GET12件、選定probe2起動で2件を遮断。UIサーバーPOST受信0、両probeのページ例外0。ハーネス側例外3件は別に記録。全suiteは公開CDN読取りと模擬通知を使うため、全体外部要求0とは扱わない。

## 残る範囲

理科・トップの件数/固定名は対象外で未修正。実機Safari/iPad・CEO本人試用・学習効果・公開環境・私的回答は未検証。親/保存拒否等は既存suiteと今回の対象検証を区別し、全ての複数タブ競合や時刻の原子性を保証しない。依存は手動再利用、自動snapshot継承の成功証拠ではない。

## 必須検証・判定

固定HEADで `bash scripts/check_all.sh` を1回実行し、25/25 suiteが終了0（352秒）。開始 `2026-11-14T20:15:39.715472+00:00`、終了 `2026-11-14T20:21:31.711285+00:00`。実行前後ともHEADは `55435567d44f05dc35f3ea6d73c4ba9cac2dc496`、dirtyなし。suite別の終了値・時間は `suites.json`、完全出力は `suite.log`、固定HEADと時刻は `suite-meta.json` に保存。

**判定：指定した4教材の修正として独立QA合格。** 8実UI例、18選定同等性例、3境界例、10保存確認、独立生成再現、必須25suiteを確認。今回再現した製品不具合・未解消の阻害指摘は0。draft PRでCEO判断へ進める。本番マージ・公開・理科/トップを含む全アプリ解消を承認する判定ではない。

証拠bundleは `/tmp/yuika-daily-fix-qa/`。`sha256.json` は同ファイル自身を除く証拠のSHA-256一覧。
