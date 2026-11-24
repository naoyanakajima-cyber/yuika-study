# 苦手復習PRと終了時学習報告の互換同期

## 目的と範囲

既存draft [PR10](https://github.com/naoyanakajima-cyber/yuika-study/pull/10) の理由付き復習・日次実問数・理科てこの記録を保ち、外部PR31でmainに追加された完了/途中終了報告と両立させる。教材追加PR11・テーマPR12へ機能を混ぜず、新しい製品PRは作らない。

開始製品HEADは `d26d10dea80b93cef7a47dbd814f76e3f69d3934`、観測mainは `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`。指定4運用文書を同じ最新 `4ac34c7a58f2f6c76c33b6728b241574837218d5` から読み、run `cycle-20261124T100555Z` のleaseを通常pushで取得した。

PdM `pdm_rev_pr31` は[保存済み受入条件1〜5](2026-11-24-pr31-impact.md)を再確認し、新仕様は不要と判断。PrM `root/coordinator` が実装範囲を受け入れ、Engineer `engineer_rev_pr31` に独立checkoutを割り当て、別担当 `qa_rev_pr31` が固定候補を検証する。

## 受入条件

- 理由付き復習、日次実問数、てこ進行/単元付き再開、回答単位/誤答タグと旧履歴を維持する。
- 完了/途中終了/未回答/移動キャンセル/重複終了を合成設定と通知mockで確認し、親モードの送信・キュー抑止と本人記録の保護を維持する。
- 「今日の復習」と実問数に通知試験を適合し、件数・modeのassertを弱めない。
- 必須suiteの和集合を保ち、通知/江戸/模試を含む生成順の初回保持・2回目不変を検証する。
- 最終固定候補を別担当QAが必須suiteと768×1024合成通常/親操作で確認する。

## 環境と権限

選択済みクラウドのreadyを確認した。既存checkoutから独立worktreeを手動作成し、保存済み検証手順に従って既存 `/workspace/yuika-study/.venv` を再利用する。旧文書の専用checkout `/workspace/yuika-study-cloud` は今回存在せず、自動snapshot引き継ぎ成功とは扱わない。初回の既存手順確認で手動準備へ進み、古い環境調査を反復しない。

実回答・教材写真・実通知設定を使わず、mainマージ・公開・デプロイ・設定/Secrets変更・実送信は実施しない。CEO新返答の実読・取り込みは0件。外部PR31のマージ観測は新たな承認ではない。

## 実装・独立検証・次の仕事

Engineer候補は `0cd726f558d24999da80c37b1ecdbd2e6090c7bb`。既存PR10と観測mainを親とするtopic上の統合で、README競合を双方の説明を保持して解消した。必須suiteは既存31件と新main27件の和集合32件。新規通知試験は「今日の復習」と4問になる既存条件に適合させ、未回答終了・移動キャンセル・本人保存不変のassertを追加した。

生成保持の初回検査では江戸/模試/派生進捗の差分を検出した。江戸は理科HTMLを複製するとてこ専用動作が混入するため、既存江戸HTMLをテンプレートとして問題定義を更新する。共通notification/history/design/parentは再埋込するが、江戸のscience/prototypeアダプターには今後明示的な同期が必要となる。模試生成では応仁・鎌倉限定のおすすめ表示を除き、親境界を通知マーカーの前へ配置する。生成列を拡張し、初回の全追跡byte保持と2回目の不変を維持した。

Engineerは生成検査の2回目成功と通知7ケース/16模擬報告の成功を確認した。追加通知fixtureの初回は通常応仁filterを4問と仮定して失敗し、既存の漢字filterによる4問条件と対応modeへ修正した。これらはcommit前dirty状態の実行。5本の焦点試験は成功出力を確認したが個別exit未記録であり、今回の合格判断は固定候補の独立QAを根拠とする。[Engineer記録](https://github.com/naoyanakajima-cyber/yuika-study/blob/0cd726f558d24999da80c37b1ecdbd2e6090c7bb/docs/pr31-compatibility.md)に診断・失敗・制限を保存した。

独立QAは固定候補の別detached checkoutで実行した。通常/親の8新規context、768×1024で、未回答終了・回答後の移動キャンセル・1問回答後の終了・完了・重複報告・reloadを初回成功。通常側の報告8件はすべてmock内、親側は0件で本人localStorageのbyte不変を確認した。理科の実問数8問も確認。予期しないPOSTとpageerrorは0、外部GET28件を遮断した。[操作結果](../evidence/2026-11-24-review-pr31/report-probe-result.json)。統括も応仁通常と理科の親終了後の合成画像を目視したが、全画面の目視合格とは扱わない。

独立の使い捨てコピーで、江戸build()の問題変更が反映され、版未登録の変更は期待どおり拒否されること、説明付きeditorial更新で旧版を保持して追記すること、通知生成元の変更が反映され親境界が通知block全体より前になることを初回成功で確認した。元checkoutは不変。[生成契約結果](../evidence/2026-11-24-review-pr31/generator-contract-probe-result.json)。期待された拒否exit1は製品失敗や再試行として数えない。

固定候補で独立 `bash scripts/check_all.sh` は初回32/32成功、exit0、393.749秒（script表示394秒）。前後HEAD一致・status空。[QA報告](../evidence/2026-11-24-review-pr31/QA.md)と[全結果](../evidence/2026-11-24-review-pr31/summary.json)に各suiteのexit/秒数を保存した。QAに予期しない失敗・再試行はなく、過去HEADのQAを今回の成功として扱っていない。

実機iPad/Safari/WebKit、本人試用、学習効果、実配送と公開画面は未確認。CDN資材を使う既存suiteもあり、完全オフラインとは呼ばない。外部CI結果はクラウドで実行したQAとは別に台帳へ記録する。

## 保存と次の仕事

既存製品draftはPR10/11/12の3件を維持し、今回の更新はPR10のみ。PR10の合成試用判断待ちを保持する。次回は最新HEADとleaseを再確認し、PR11自身の教材確認・JSON入出力・保存しない試し解き機能を保ちながらPR31への最小互換同期をPdM/PrMで確認する。PR12はその後。PR10の固有機能を他branchへコピーしない。

運用台帳の中間pushはHTTP503で失敗したが、remoteが旧HEADのままと確認後の2回目に通常push成功。実行権は失われていない。PR10と運用PR9のタスク添付は各1回呼び出したが応答しないため待機を中断し、成功未確認として記録する。GitHubへの保存とは区別する。
