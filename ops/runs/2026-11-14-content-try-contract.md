# CONTENT-TRY-SPEC：合成教材を保存せず試し解きする契約

2026-11-15 JST（ファイル名の日付はUTC）。managed cloud running/connected/currentを確認。
正本4文書は同じ `cebcab5b3d1984bd252d7ea358841248f3dec8ff` から読み、leaseを通常pushで取得した。
run: `cycle-20261114T160052Z`。対象は前回未完了のCONTENT-TRY-SPEC。

## 学習上の価値と範囲

確認した合成問題を、教材登録の前に保護者役が回答・採点・解説まで試せるようにするための要件成果。
現在のPR11には確認・編集・JSON出力があり、試し解き採点はまだない。
本サイクルは採点と確認失効、状態遷移、保存しない境界を定義する。製品コードの実装は行わない。

比較対象PR11は `3d2ed2f9a62673d2fb086a360ae841096f35b63e`。
mainは `86514eda054a5a2e09204df3a0668e40624c16de`、PR10/12/22も前回とHEAD不変。
製品待ちはPR10/11/12の3件と追加既存draft22。新製品PR枠を増やさない。
新CEO返答の取り込み0、D02実資料接続・保存先は未決のまま。

## 分担と検証

PdM `pdm_content_try_contract` が既存形式・固定PR11を読み、要件案と合成例を作成。
PrMが範囲と保存互換性を確認し、独立Reviewer `qa_content_try_contract` へ渡した。
製品実装がないためEngineerは起動しなかった。独立QAは初回 `5838f02` の前問遅延イベント指摘を行い、修正 `a6ac479` を文書受入可と判断した。
過去PR11のアプリテスト成功を、今回の試し解き機能の成功に数えない。

## 完了条件と残る境界

要件文書と合成の採点/状態遷移例が独立レビューを通過したときだけ文書doneとする。
製品受入は未実施。ブラウザー、実機Safari、本人試用、公開確認は含めない。
未解決画像の転記・正答を推測補完せず、画像の成功経路を実証したとは報告しない。
CSP・既存教材・学習記録・JSON案形式・確認条件は変更しない。
マージ/公開/実通知/課金/権限変更・私的資料取得なし。通常報告は朝夕チェックへまとめる。

## 次の具体的な作業候補

新しい試し解き機能の実装を増やす前に、既存draft PR11のmain基点との配信互換性を扱う。
前回Engineerの固定main/PR11仮想tree `430b786448147fb7a6a58e918e398b0e7569043b` のserve.py競合をPrMが読み直した。
旧PRの固有変更は既存ループバック配信allowlistへのcontent-review.html追加で、mainには共通assetsとmock-focus-review.htmlがある。
双方の既存入口・限定配信・CSPを維持する競合解消範囲を、次回PdM→PrMで確認してから既存PR11だけの修正として進める候補とする。
mainへマージせず、共有範囲を外へ広げず、既存PRの目的を試し解き新機能へ拡張しない。
基点を更新する場合は旧branch履歴を保持した独立checkoutで統合・回帰QAし、最新HEADとleaseを親が再確認する。
未解決の互換性や新たな承認必須操作が判明すれば、その操作を止める。
この候補の実装・競合解消・ブラウザー検証は本サイクルでは行っていない。

## 保存した証拠

- [最終契約](../../docs/product/content-try-spec.md)
- [PdM原案](../evidence/2026-11-14-content-try-contract/PdM.md)
- [独立QA](../evidence/2026-11-14-content-try-contract/QA.md)
- [仕様オラクル](../evidence/2026-11-14-content-try-contract/spec-oracle.cjs) / [結果](../evidence/2026-11-14-content-try-contract/spec-oracle-result.json)

ECMAScriptの文字正規化・入力上限・選択index・開始候補上限の38合成例を独立Reviewerが確認。
結果保存のため同じcheckerを再実行した事実を記録し、2回とも38/38、76別ケースとは数えない。追加反復なし。
状態遷移S01〜S13は机上照合であり、実行済み状態テストではない。
必須指摘（前問/状態世代の古い操作拒否）と任意の表示文言指摘は仕様に反映。未解決必須指摘0。
CONTENT-TRY-SPECは要件文書doneであり、製品実装を完了扱いにしない。
