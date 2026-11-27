# PR32マージ照合・中断復旧文書の独立レビュー

- Reviewer: `qa_pr32_impact`。文書著者root/coordinatorとは別担当。
- 判定: accepted_static_documentation_only。重要な訂正要求なし。
- 日時: 2026-11-27T14:13:28.423530+00:00
- 対象: `ops/runs/2026-11-27-pr32-merge-recovery.md`
- SHA-256: `159695bcb88d419cad8fba0715ea8bd05fa08ea680d0f5258a194c23df018a81`

## 直接確認した証拠

GitHub APIでPR32のmerged=true、merged_at=2026-11-27T13:30:18Z、merge commit `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5`、head `9c34c42dd141499f0022296a830abcafcd73104d` を確認した。
Gitオブジェクトで両treeが `52f2aef501e26eb00b206ba7545b1c0476f19acd` と一致する。旧main `101c64ef9be86cb7c3502d3eeec498f16e93e7fd` との差分は元文書の8ファイルと一致した。

固定製品HEADとの共通変更箇所を再計算した。PR10はindex.html/check_all/responsive_subjects、PR11はcheck_all/cloud/serve、PR12はcheck_all。復習導線、算数入口、preview両ルート、各製品機能、全スイートと生成処理保持を次の互換同期の受入条件とする記述は妥当。PR10→11→12の優先順はPrMの作業順であり、技術的依存順や採用承認とは扱わない。

旧lease commit `f0d43b5140344441e50f79f11f151dc71d7b31dc` の期限13:41:34 UTCと、現台帳の旧run interrupted/新run reconciliationを直接確認した。復旧した旧影響文書のSHA-256が `566eaf3738941986c83bbeb245b7fe9ba90645612dcff1a3dcf16e8edc947eac` と一致するため、前回の静的レビュー対象と同じ文書である。

## 限界

Git認証エラー回数やconnector応答停止は統括の実行記録に基づく記載であり、本Reviewerが再現したものではない。認証回復理由・snapshot自動引き継ぎ成功は未確定のまま。
旧PR10/11/12のQA記録は各旧固定HEADに対するもので、新mainとの組合せを検証済みとする主張がないことを確認した。本レビューでも製品変更・統合・アプリ/ブラウザーテスト・全スイートは行っていない。外部マージから本運用の新たな権限、公開成功、本人試用成功を推定していない。
