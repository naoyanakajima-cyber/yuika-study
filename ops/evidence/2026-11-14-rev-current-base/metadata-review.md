# 独立QA：台帳・証拠の最終静的レビュー

担当 `qa_rev_current`。製品候補132f9f59ebd23b6dab33e7d1e23bf4d077b8070dの独立QA後、運用候補 `f31b166d5ba10c843b0a8eca38c7e773608b92f2` を実行前正本 `7c7ad83953a32ae459e9aafb272d5071957f40ac` と比較した。製品再試験なし。

判定：メタデータと証拠は受入。

- 以前の128実行は全件同一、新実行1件のみ追加。decisions/policy/authorization/decision_intake/scheduling/existing_work/unreconciled_prs/operational_findingsは不変。
- チケット集合は不変。変更はREV-MVPだけで、他11件は不変。旧reviewと旧independent_followupを履歴へそのまま追加し、以前のevidenceも維持。
- 新reviewは実際の3役と固定HEAD、24suite・exit0・300秒・独立10ユニークケースを記録。日次件数修正は未実装のまま、次工程へ限定。
- 外側manifestの36hashを全照合。qa配下全ファイルとQA.mdは/tmp原本とバイト一致。ハーネス2原因・3起動と製品失敗0を区別し、一回で10ケース成功したとは記載していない。
- 文書のscopeは現在の保存保護と旧推薦の共存に限定。旧形状validatorと現在JSON/storageの互換性を分け、手動環境準備と自動引継ぎ、Chromiumと実機、draftと採用・公開を区別。
- 候補の両親は旧PR10 ba829a1 とmain86514edで、両方の祖先関係を実際に確認。mainへのmergeではない。

最終化の残作業：統括がPR9本文更新を読戻し確認し、lease解除と完了時刻を保存する。candidate時点のupdated_prsに9が含まれるため、未実施のまま完了扱いにしない。PR10のopen/draft/base main/HEAD132f9f5という統括の読戻し記録は受入。後続の外部check観測は、固定SHAに対する観測結果だけを追記し、ローカル合格や公開成功へ読み替えない。

## 外部読戻し追記のレビュー

運用 `25622a1` も確認。37件のmanifestを再照合。追加pr10-delivery.jsonは固定132f9f5/main/open/draft/unmergedとWorkers Builds failureを保存し、completed_atと実保存recorded_at、観測windowを区別している。台帳はチェック原因を未調査、再実行/デプロイ未実施として記載し、ローカル24suite合格から外部成功を推測していない。受入。

報告の「19:22:23Zにfailureを観測」はチェック完了時刻であることを明記する文言へ直すよう統括へ伝達。JSONと台帳の時刻フィールドは正しい。以後のPR9本文読戻しとlease解除は統括担当。製品・試験の変更はないため全suite再実行不要。
