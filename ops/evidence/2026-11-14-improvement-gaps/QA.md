# 独立Reviewer/QA：改善仕様と固定HEAD照合

レビュー対象commit：`592e3dde63bb98921b2d9cb696df5e2d422b82fc`。
比較元：lease取得commit `151ab31`。run：`cycle-20261114T150307Z`。
担当：独立子エージェント `qa_improvement_spec`。2026-11-14 UTC。

判定：文書成果として受入可。重大・中程度の差戻し事項なし。製品の実装完了、ブラウザーQA合格、採用・マージ・公開承認を意味しない。

## 実際に確認したこと

- `docs/agent-team.md`、`ops/AGENTS.md`を読み、改善仕様・run報告・PdM/Engineer文書・harness/resultsの全4証拠ファイル・台帳差分を確認した。
- 差分は7ファイルで、製品コード・既存テスト・設定への変更なし。追加JSは証拠用の合成probe。公開差分に個人の回答・実点数・教材画像・私的URL・通知ID・認証値を認めない。
- 台帳のtop-level変更はticketsのみ。lease、decisions、既存PR集合、既存のQA証拠は変更されず、新CEO承認を追加していない。REV-RECONCILEはreviewへ移行し、今回QAを実施済みと先取りしていない。
- main `86514eda054a5a2e09204df3a0668e40624c16de`、#10 `ba829a1176ff1ead7d312526890afe8792178c99`、#11 `3d2ed2f9a62673d2fb086a360ae841096f35b63e`、#12 `57171ad9cab02fec6a080ecbe317fe11d3f51dcf`の保存済みGitオブジェクトを直接読んだ。各merge-baseは`edad8065c1f2b726e61c5cf405f8d9ff6d807480`で一致。PR固有差分のファイル数・増減行は順に5/+483/-8、11/+849/-3、4/+408/-1で文書と一致。
- #10のrecommendedPlanは最後の誤答・24時間・ヒント正解による選定と理由表示。mainの日次選定と同一ではなく、完全包含・不要との断定を避ける対応表は適切。#11の読込時確認解除、編集revision更新と全確認解除、出力時issues/current revision検査を確認。#12の専用テーマキー/CSSと鎌倉のみの変更を確認。mainのprototype保存キー、親モードのsessionStorage/一時メモリ分離を旧HTMLで巻き戻さないゲートも妥当。
- endpoint diffにmain追加物のD表示があることを確認。merge-base→PR差分にその削除はない。保存済み仮想treeを走査し、競合markerの対象が#10応仁/鎌倉HTML、#11 serve.py、#12 README/鎌倉HTMLと一致した。今回Reviewer自身はmerge-treeを再実行しておらず、Engineerのexit 1は提出証拠として確認した。三方向競合とendpoint差分を混同していない。
- main adaptive.js 140–148行のdailyQuestions、151行の0件停止、171行の設定数ラベルを照合。science.jsは5/10のみ、adaptiveは5/10/15。トップの固定「今日の5問」とprogress.jsの内訳・教材全数totalの区別も一致。
- embed.pyは応仁・鎌倉・平安・重点復習の4出力を生成する。最終改善仕様が4出力の設計確認と生成元/生成物不一致の禁止を明記しており、3出力だけを無条件更新する要求ではない。理科へ15問を増やさない制約も明記されている。

## 実行した限定検証

1. Python標準ライブラリとgit showで抽出関数の文字列、SHA256、台帳差分を照合した。dailyQuestionsは固定mainと文字単位で一致した。
2. source SHA256は`aa82eca8636be227d3bcaf1f0004004d74b55ec8ec325e4cfd8300e74811eac9`、抽出関数SHA256は`d6376c8ec43d06ffff041973720c3429ac93fd767c5d20a51d5c642a32eb4e9f`で証拠と一致した。関数hashは終端改行を含めない抽出文字列の値。
3. `node ops/evidence/2026-11-14-improvement-gaps/count-harness.js`をReviewerが独立に1回実行、exit 0。出力JSONは保存済みcount-results.jsonと構造的に完全一致。5/10/15 × 候補0/1/4/5/9/10/14/15の24件で上限・重複除去を確認した。
4. `git diff --check 151ab31..592e3dd`はexit 0。

probeのlabelは設定値を記録するstubで、DOM表示の実測ではない。due/weak/candidatesは合成stub、shuffleは恒等関数であり、実教材で候補不足に至る条件、抽選順、保存、理科、トップの動作検証ではない。提出文書もこの限界を明記している。

## 次タスクの妥当性と注意点

CONTENT-TRY-SPECはrequirements_onlyで、依存CONTENT-SPEC/CONTENT-CHAT-SPECはいずれもdone。#11固定HEADを参照した確認失効・採点正規化・明示許容表記・表示・戻る/再読込・全storage非書込の契約は、実接続なしで合成例によって文書化できる。既存仕様のtext/choice・aliases/readings条件に対応づける方針は妥当。採点や状態遷移の未確定点を今回決定済みとはしていない。

次回は要件作成→PrM→独立レビューまでに限定する。P2の実装許可ではなく、待ち#10/#11/#12の3件と追加既存draft#22を増やさない。既存PRへの実装修正にも別途対象/基点/互換性/必要テストの確定が要る。

低重要度の運用上の注意：PdM提案中の5/10/15表記は共通adaptiveの条件として読む。理科の5/10制約と4生成物への反映制約は最終改善仕様を優先する。採点正規化は次回の未確定契約であり、今回の文書受入から実装着手可能とは推論しない。

## 未実施・対象外

ブラウザー、768×1024の画面操作、storage実動作、既存アプリsuite、実機Safari、本人試用、公開画面、新しいremote照会は実施していない。PR9本文の新しい草稿は本レビュー対象外。既存22suite/URL8ケースは過去証拠であり今回実行に数えない。

Reviewerは製品編集、台帳編集、生成器実行、merge/rebase/push、外部送信をしていない。このレポートのみ/tmpへ作成し、親が証拠保存と最終台帳更新を行う。
