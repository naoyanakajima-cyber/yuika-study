# PR26 外部マージの独立静的照合

Reviewer: qa_merge26_reconcile。製品実装・テスト・install・pushなし。

- 既存QA対象HEAD: `acd169882b626ef255ba68cd73c995024c30e515`。
- 観測main/merge commit: `86514eda054a5a2e09204df3a0668e40624c16de`。
- 独立に `git merge-base --is-ancestor` exit 0、`git diff --exit-code` exit 0を確認。両者のtreeは `fc44857441e0f2344e488d141c5c4fa47065a0c6` で一致。前回のテスト準備修正 `5b772250401d9057152d698f07e78456968bbf85` もmainの祖先。製品checkoutはclean。
- 保存済み qa-result.json は同HEAD、全22スイート各exit 0、332秒、全体実行1回、URL境界8ケース成功。台帳latest_reviewの値と一致。これは前回の実行証拠であり今回再実行ではない。
- 現台帳のPR26 open_draft / included_in_observed_main=false / テスト修正提出先draft表記は更新対象。新しい製品コード差分はない。
- Pages run `43223305924` のbuild/deploy/report-build-statusは独立API読取で全てcompleted/success。対象commitとの結合は親が取得したrunメタデータのhead_shaが上記mainに一致した証拠による。公開URL本文や利用者の端末での表示確認とは区別する。
- 既存QAの限界を維持: Chromiumのみ、Safari/WebKit/実機iPad・CEO本人試用は未検証。追加設定probeは13確認後に待機処理で2回失敗し停止、当該probeによる終了後復元は未検証。通常parent_mode suiteの成功と混同しない。
- 外部マージ/Pages成功は観測事実であり、この運用の新しいCEO承認の取り込みや権限拡張ではない。マージ済みの事実は記録できるが、adopted等の承認項目を推測で変更しない。

結論: 検証済み成果のmain包含を静的に確認。今回の差分を理由とする製品再試験は不要。台帳の現況と提出待ち状態を更新し、本人試用・採用整理など未完了範囲を残す方針に阻害事項なし。
