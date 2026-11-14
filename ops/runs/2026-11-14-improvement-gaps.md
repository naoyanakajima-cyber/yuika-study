# 改善候補の具体化と既存PRの照合

2026-11-15 JST（証拠ファイル名はUTC 2026-11-14）。対象 REV-RECONCILE。
運用正本 `fcb57ffff6c2dc1560aec23ed71e16504b2295ab` の4文書を同時点で取得。
managed cloud running/connected/currentを確認し、run `cycle-20261114T150307Z` のleaseを通常pushで取得。

## 学習上の成果とPrM判断

前回の無変更判定だけでは、独立してできる要件整理を十分に扱えていなかった。
改善提案を求める発言を読み、PdM `pdm_improvement_gaps` を起動した。
「今日の3問」の入口追加は既存mainの日次練習と重複するため、件数表示と実際の出題数の整合へ絞った。
PrMはP0の旧PR対応表、P1の件数仕様、P2の合成教材試し解きの次要件候補を確認した。
Engineer `engineer_improvement_delta` は製品実装をせず、固定HEADの技術照合を担当。

[次の改善仕様](../../docs/product/improvement-next-step.md)は要件成果であり、製品改善の完了や学習効果の実証ではない。
新しいCEO承認の取り込みは0。提案要求を案の採用と扱わず、D02は未決のまま。

## 固定した対象

- main `86514eda054a5a2e09204df3a0668e40624c16de`
- PR10 `ba829a1176ff1ead7d312526890afe8792178c99`
- PR11 `3d2ed2f9a62673d2fb086a360ae841096f35b63e`
- PR12 `57171ad9cab02fec6a080ecbe317fe11d3f51dcf`
- 追加draft22 `bd4f48de0404614eb84275969bfccff0a368e866`

製品待ち3件と追加draft22は維持。旧4〜8、運用9/13は別枠。
新しい製品PR、リベース、クローズ、main変更、公開は行っていない。
過去の22suite/URL8ケース成功はPR26時点の証拠として保持し、今回の実行結果に数えない。

## 証拠と限界

- [PdM提案](../evidence/2026-11-14-improvement-gaps/PdM.md)
- [Engineerの固定HEAD対応表](../evidence/2026-11-14-improvement-gaps/Engineer.md)。#10のHTML2件、#11のserve.py、#12のREADME/鎌倉HTMLに仮想3方向統合で競合。実統合は未実施。
- [抽出関数probe](../evidence/2026-11-14-improvement-gaps/count-harness.js) / [24合成ケースの結果](../evidence/2026-11-14-improvement-gaps/count-results.json)。Engineerが1回exit0。表示用設定値と実結果長の差を確認、実教材での到達条件・ブラウザーは未検証。
- [独立QA](../evidence/2026-11-14-improvement-gaps/QA.md)：`qa_improvement_spec` が候補 `592e3dde63bb98921b2d9cb696df5e2d422b82fc` を確認し受入可。24ケースを独立に1回実行、保存JSON・抽出元hash一致、差戻し必須事項なし。
- コードの読み取り・Git統合診断を製品のブラウザーQAと混同しない。
- 統括の初回diffコマンドは欠けた `--` によりexit128。区切りを補った2回目は成功。製品不具合ではない。
- 実機Safari・CEO本人の試用・公開画面は今回未確認。環境・依存の準備変更なし。

## 次の一手

次回は合成教材のメモリ内試し解き契約をPdM→PrM→独立レビューで具体化する。
採点の正規化、確認の失効、戻る/再読込、保存非接続を決め、既存CONTENT-MVPの未解決仕様に対応づける。
新製品PR枠や実データ接続を必要としない。製品コード変更は待ち枠・適切な既存提出先と互換性を確認してから。
通常報告は朝夕CEOチェックへまとめ、外部への別送なし。

REV-RECONCILEは照合文書としてdone。製品PR採用・本人試用は完了しておらず、CONTENT-TRY-SPECはrequirementsとして次回へ渡す。
