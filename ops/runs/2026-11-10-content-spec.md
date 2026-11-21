# CONTENT-SPEC 開発サイクル（2026-11-10 JST）

## 成果と学習上の価値

新しい教材を追加するときに、原本・読み取り・問題案を見比べて誤読や未確認の正答を
直せるよう、共通案形式と確認体験を仕様にした。未解決箇所が一件でもあれば確認不可、
内容編集で全問の確認を失効し、確認済み案と本番導入の承認を分離する。

- 成果: `docs/product/content-spec.md`、`docs/product/fixtures/`のJSON2件・TXT・SVG。
- commit: `c79197099537d9ef3a34badb4b7f0ff74cbc615a`。
- 保存先: [既存draft PR #9](https://github.com/naoyanakajima-cyber/yuika-study/pull/9)。新規PRは作成していない。
- CONTENT-SPECは文書成果として完了。CONTENT-MVPは合成試作として着手可能。
- アプリの教材追加・OCR・自由文章からの問題生成が完成したという意味ではない。

## 再開・権限・分担

`provider=cloud`、running/connected、最新観測、network enforcedを確認。
最新運用commit `48acbaf` の4文書を同時点で読み、PR #4〜#10を照合。
PR #10はdraft・未マージ、CEOの新たな承認は未記録。継続修正依頼はないため、
依存しないCONTENT-SPECを選んだ。製品PRの承認待ちは1件。

通常pushでleaseを取得し、独立checkout `/workspace/yuika-content-spec-20261110`で作業。
本サイクルでは依存導入・手動Installやsnapshot復元の再診断は不要だった。
自動snapshot引き継ぎ成功を新たに判定したものではない。

- PdM `pdm_content_spec`: 既存教材/validatorを調査し、案形式・確認失効・ID/版保護・C1〜C11を定義。
- 統括/PrM: D01/D02未決でも着手できる合成サンプル限定の範囲を確認。
  既存学習アプリへの導入adapter・履歴移行は別チケットへ分離。
- Engineer `engineer_content_contract`: 仕様との技術整合を確認し、4件の合成fixtureを作成。
- 独立Reviewer/QA `qa_content_spec`: 文書とfixtureを直接確認し、下記の構造・参照検証を実施。
- レビューでpackageIdの接頭辞不整合と、原文にない読みのgeneratedFields表示を修正。
  最終commitは4 fixturesのhash一致、仕様のレビュー通過状態1行のみの差異を照合済み。
- 子はcommit/pushせず、統括がremote lease所有者と期限を再確認して運用branchへ統合した。
  mainは変更せず、既存draft PR #9の説明も現在の成果へ更新した。

## 今回実施した検証

| 検証 | 結果 |
| --- | --- |
| Python標準jsonでJSON2件のparse、必須項目、ID、参照、未確認状態、原文一致のassert | exit 0 |
| ElementTreeでSVGをparse、転記内容一致、script・外部資産・href・event属性なしのassert | exit 0 |
| `git diff --check` | exit 0 |
| 最終commitとレビュー済みfixtureのhash照合 | 一致 |

Python検証は一時的なinline assertionで、結果はツールstdoutに記録。
アプリ・ブラウザーテスト、OCRは未実施。C1〜C11は次のCONTENT-MVPの受入条件であり、
実行済みテスト結果ではない。アプリ・依存・CI・既存assertは変更していない。

## 次の一手と判断待ち

次はCONTENT-MVPで、同梱の合成サンプル選択→転記/案の比較→編集/検証→個別確認→
JSON出力/再入力/取消を独立試作にする。既存教材・回答記録への接続は行わない。
現行形式の教材追加には別のadapter・ID/版設計と互換テストが必要。

D01（実入力の場所）・D02（私的資料の保管先）・D03（PR #10の採用）は未決を維持。
通常の報告は朝夕のCEOチェックへまとめる。
私的回答・教材写真・メール/Driveは取得せず、fixtureは合成のみ。
実通知、本番マージ・公開・デプロイ、Secrets・課金・権限・共有範囲変更は行っていない。
停止中の旧自動更新も操作していない。
