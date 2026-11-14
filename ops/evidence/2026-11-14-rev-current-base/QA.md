# 独立 Reviewer/QA: PR10 現行基盤統合

担当: `qa_rev_current`。実装者は `engineer_rev_current`。2026-11-14 UTC。
固定対象: `132f9f59ebd23b6dab33e7d1e23bf4d077b8070d`。main `86514eda054a5a2e09204df3a0668e40624c16de` と旧PR10 `ba829a1176ff1ead7d312526890afe8792178c99` を比較した。製品checkoutへの書込み・pushなし。

## 差分と互換性

mainからの差分はREADME、assets/design.js、応仁/鎌倉HTML、推薦2テスト、check_all登録の7ファイル。許可範囲内。
9ファイル全体と応仁/鎌倉の4区間ずつ、計17項目でmainとのSHA256一致を確認。adaptive生成元、prototype/parent runtime、採点/validator、教材、他4HTMLを維持した。旧recommendedPlanは利用不能ガードをmainのpracticeUnavailableへ置換した点以外、両単元とも同一。

assets/design.jsは推薦案内が存在する場合だけ統計欄の次へ移す1行追加。既存推薦テストの選定・理由・上限・フィルター・保存・keyboard/focusのassertは残っている。旧validator確認は、**新しいnormal eventからoptional questionVersionを除いた旧形状の互換性**。現在のprototype export/rawをそのまま旧HTMLへ戻せるという意味ではない。

旧未来日時テストは1時間先から1分先へ変更され、5分超未来の現main停止条件のテストが追加された。dirtyの既存テストは未来停止と同時のため、それだけではdirty単独の証拠にならない。下記独立quota試験で実際の保存失敗後のdirty単独停止を確認した。公開フォントCSS GETは遮断しつつ観測として許容され、実通知のassertは維持される。

## 独立追加UI検証

768×1024 Chromium、独立した合成履歴・一時ブラウザーで、両単元それぞれ次の5ケース、計10ユニークケースを受入。

- normal: 候補1問で開始、開始だけでは回答履歴不変、理由固定、実回答・採点・normal event保存・再読込、旧キー/他キー不変。
- parent: 同じ推薦を親確認モードで実回答・保存・再読込。session側のみ、全localStorage不変。終了後もlocal不変、通常側履歴0。
- blocked: 不正rawで推薦停止、直接startRecommendedでも画面/セッション/raw不変。
- future: 10分先の合成記録で推薦停止。正常0件とは別の休止説明。直接開始でも状態不変。
- quota: 実際のStorage.setItem例外を注入して回答保存を失敗させ、dirtyと元raw保持を確認。ホームからの推薦ボタン無効、直接開始でも状態不変。

全10ケースを一回で成功したものではない。probeを3回起動した。初回は親モード終了時、親runtimeだけ先にロードされdata未初期化を読むハーネスの待機不足。二回目はそれを修正し応仁4ケースを完了した後、Playwright evaluateへ返したsetter関数が呼び出されるハーネス不備。三回目は明示ブロックで値を返さない形へ修正し、未完了の6ケースだけ続行した。同じ原因は各1回の修正、製品コードの修正・失敗なし。失敗ログと各版probeを保存。

3起動合計24件の外部要求は全て公開Google Fonts CSS GETで遮断。サーバーPOST受信0、ページ例外0。テストハーネスevaluate例外2件と製品ページ例外を区別する。

## 生成整合

固定HEADをgit archiveした独立一時コピーでpractice/embed.py → design/embed.py → parent/embed.pyを実行。各終了0、全6HTMLの前後hash一致。製品checkoutは変更していない。

## 残る限界

日次件数の既知不一致は今回未修正。推薦は元問題だけの従来選定で、review-v1履歴との統合や新しい日次アルゴリズムは含まない。Safari/WebKit/実iPad、CEO本人試用、学習効果、公開環境、私的実記録は未検証。全suiteのネットワーク条件と独立probeの外部遮断は別。依存は統括が既存venvを手動再利用し、自動snapshot引継ぎ成功とは扱わない。

証拠: `/tmp/yuika-rev-current-qa/` のsuite.log、suite-meta.json、probe-summary.json、各attemptのresults/log/source、10ケース画像、static-results.json、recommendation-preservation.json、generator-results.json。

## 必須全suite結果と判定

`bash scripts/check_all.sh` は1回、24/24成功、exit 0、runner300秒（wall300.754秒）。開始2026-11-14T19:15:18.136339+00:00、終了19:20:18.890176+00:00。前後HEADは132f9f59ebd23b6dab33e7d1e23bf4d077b8070d、dirty空を確認。追加推薦2suiteを含む全24を実行し、製品の修正・再試行・試験中commitなし。既存suiteは公開CDN読取りと模擬通知を含み、全体の外部要求0とは扱わない。

**判定: 統合範囲について独立QA合格。** 現mainの保護を維持し、旧PR10の推薦を両単元で利用できる統合候補を受入。日次件数の修正・製品採用・merge・公開の判定ではない。
