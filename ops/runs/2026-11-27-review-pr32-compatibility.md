# 理由付き復習とPR32算数教材の互換同期

対象: REV-MVP / 既存draft PR10。PdM pdm_rev_pr32 → PrM root/coordinator → Engineer engineer_rev_pr32 → 独立Reviewer/QA qa_rev_pr32。
既存PR10 `0cd726f558d24999da80c37b1ecdbd2e6090c7bb` とmain `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5` をtopic内で統合した候補は `792f438fe648e056ad83a423e55bebe9d53fe43f`。

## 学習上の価値と実装

応仁・鎌倉の理由付きおすすめ復習と各単元の実問数表示を維持し、新算数24問/5段階の入口をホームに残す。ホームの競合は既存「今日の復習」と算数入口を両立する2行追加で解消した。新教材を復習履歴へ接続する機能追加ではない。既存ID、採点、保存キー、教材、親モードの記録隔離・通知遮断は変更しない。

必須suiteは旧PR10の32と新mainの28の厳密な和集合33件。生成保持の12段階×2passは新HTMLも含む全tracked bytesを照合する。Engineerの予備generator/math検証は候補commit前に各初回成功、最終固定HEADの結果は別担当QA証拠を参照。

## 検証証拠

固定候補で全33suiteが初回exit0、382.929秒。通常/親の独立4contextも成功（QAfixture初回不正を修正後2回目成功、assert変更なし）。全suite実行前後はHEAD一致・clean。

独立QAは `ops/evidence/2026-11-27-review-pr32/QA.md`、全suite実測・操作記録・差分比較は同ディレクトリに保存する。旧HEADの検証は今回成功の証拠へ流用しない。

## 境界と次の仕事

既存クラウドvenvを独立checkoutから手動再利用した。自動snapshot引き継ぎ成功とは扱わない。合成回答とモックAPIのみ。実機iPad/Safari、本人試用・学習効果、実配送・公開画面は未確認。Workers Buildsは別系統の検証で、失敗を製品QA成功と混同しない。

本番merge・公開・実通知・私的資料利用は行わない。新PRは増やさず既存PR10をdraftのまま更新する。次はPR11の新main互換同期、続いてPR12。CEO合成試用判断待ちは3件を維持する。
