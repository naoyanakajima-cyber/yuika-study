# 教材確認試作とPR32算数教材の互換同期

CONTENT-MVP / 既存draft PR11。PdM pdm_content_pr32 → PrM root/coordinator → Engineer engineer_content_pr32 → 独立Reviewer/QA qa_content_pr32。
既存PR11 `feada5947b237310923f0aa1956487ac8af501af` とmain `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5` を専用topicに統合した候補は `f028aaf3ec973d62ac87839432794ab7644cdb99`。競合なし。

## 学習上の価値と保持

合成教材の原本・転記・生成案を比較し、編集・確認・保存しない試し解きを行う試作を保ちながら、新しい算数24問・5段階の入口を取り込む。教材確認HTML・仕様・fixture・5試験・PR11runtimeは旧HEADとbyte一致。算数を確認室へ自動接続する機能ではない。
教材確認と算数の両previewルートを維持し、CSP・親モード記録隔離・通知遮断を保持。ホームは22card。PR10独自の理由付き復習・実問数とPR12テーマは取り込まない。

## 検証証拠

旧33suiteとmain28の厳密和集合34件を固定候補で独立QAし、初回34/34 exit0、348.367秒、開始終了HEAD一致・clean。通常/親×text/imageの確認・非保存試用4ケース、編集後再確認4ケース、両previewルート/CSPも初回成功。記録書込・POSTは0。新HTMLを含む12段階生成列の初回byte保持・2回目不変が確認対象。Engineerの焦点generator/cloud_preview/math検証はcommit前の実行で個別exit/timing未採取、独立QAの結果とは区別する。
独立検証の対象SHA・全suite結果・合成操作証拠は `ops/evidence/2026-11-27-content-pr32/QA.md` と同ディレクトリへ保存。旧HEADのQA成功を流用しない。

## 制約と次の仕事

既存クラウドvenvを手動再利用し、自動snapshot引き継ぎ成功とはしない。合成データ・モックAPIのみ。実OCR/実画像/本人回答、実配送、Safari/WebKit/iPad実機、本人試用・学習効果、公開画面は未確認。Workers Buildsは別系統として扱う。
既存draftPR11を更新しCEOの合成試用判断待ちを維持。次はPR12のmain58b6d9e互換同期。新製品PR、本番merge、公開、実通知は行わない。

## 保存結果

既存PR11へ検証HEAD f028aafを通常pushし、draft維持と本文更新をAPIで再確認。独立証拠は運用commit 56a9099に保存済み。外部Workers Buildsは同HEADで2026-11-27 16:21:41 UTCにfailure（原因未調査）、独立QA成功とは別記録。PR11/運用PR9のattachは各1回応答待ちを終了し、成功未確認。新規PRなし。台帳を更新しleaseを解除して終了。
