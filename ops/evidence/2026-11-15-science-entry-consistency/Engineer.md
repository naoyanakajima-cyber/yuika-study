# Cycle30 Engineer: PR27 science entry consistency fix

担当 engineer_theme_compatibility。PdM条件付き範囲・PrM明示依頼と独立QAの再現を受け、独立checkout `/workspace/yuika-pr27-fix-20261115` / `codex/pr27-unit-summary-fix-20261115` で最小修正。基点 `58c3fd4ba10ecfaa249cc3c808c3e8e5fcaf5359`、最終候補 **69f77d671b66484b501f7a0f5c292bfa96a22273**。2026-11-15T06:14:02.320001+00:00 にworking tree cleanを確認。push/main変更/公開/実送信/ops編集/新子/設定変更なし。

## 修正内容

ホーム集計のscience unitフィルターは、要求unitがcatalogの実在単元と一致する場合だけ適用する。アプリのUNITS.includesによる既存fallbackと合わせ、未知/未指定/空unitは全理科へ戻る。valid顕微鏡20問の絞込みは維持。`scripts/design/build_summary.py` と生成物 `assets/progress.js` の同じ2行に反映。保存済み設定の扱い・復習アルゴリズム・採点・履歴キーは変更しない。

追加でPrM承認されたHTML固定tag1箇所を `解説つき・47問` から `解説つき・理科全${QUESTIONS.length}問` へ変更。全理科の件数と明示し、顕微鏡20問の対象範囲と混同しない。HTMLはこの文字列置換以外基点とbyte一致。globalcounterや日次label/count、共有theme/PR10差分を取り込まない。

最終差分は許可4files（build_summary.py、progress.js、microscope.py、yuika-review-v2.html）27行追加/3行削除。archive・問題/ID・共有design assets・science algorithm・親runtimeは基点と同一。static-result.jsonへ照合結果を保存。

## 回帰と実行結果

`tests/microscope.py` に新規context/空合成履歴の4境界を追加。実ホームでsummaryを取得後、対象URLへ遷移し選択単元・実候補ID集合・実startボタンで始まる問題列を照合する。

| unit | summary total | normalCount/実開始 | アプリ範囲 | hero tag |
|---|---:|---:|---|---|
| 顕微鏡の使い方 | 20 | 5/5 | 顕微鏡 | 理科全67問 |
| 未指定 | 67 | 5/5 | all | 理科全67問 |
| 空 | 67 | 5/5 | all | 理科全67問 |
| synthetic-unknown-unit | 67 | 5/5 | all | 理科全67問 |

既存の実顕微鏡カード入口にもtag実値を確認。既存20問・revision/concepts・60通りのtap採点・再読込・弱点/再確認/日次のassertは全て維持。POSTは遮断、他外部ブラウザー要求も遮断し、既存testが必要とする公開JSだけ既存curl経由で取得する。実データ/実通知なし。

1. unknown-unit-only候補で `source scripts/cloud/activate.sh && python tests/microscope.py` 初回exit0。
2. その試験終了後に追加承認されたtag修正/assertを編集。最終候補内容で同command初回exit0。失敗による再試行ではなく、追加表示差分に対する検証。
3. `python scripts/design/build_summary.py` で生成し、同generatorの2回目でprogress.jsのSHA256完全一致を確認。
4. `git diff --check` 成功。依存lockは既存venv checkoutとbyte一致。既存venvを無追跡.venv directory内symlinkで手動再利用し、新規installや環境設定変更なし。自動snapshot成功とは扱わない。

証拠: `/tmp/yuika-cycle30-engineer/microscope-attempt1.log`、`microscope-final.log`、`static-result.json`、`SHA256SUMS`。

## 引継ぎと限界

全必須suiteは新しい固定HEADを別担当QAが実行する。Engineer focused成功だけで独立受入完了とはしない。今回の境界は空合成履歴・保存設定なしであり、全保存済み設定の組合せ・実機Safari/iPad・本人試用/学習効果は未検証。PR27元内容の20問事実確認や統合互換性全体を、この最小修正だけで保証しない。提出先は既存PR27、統括がlease/現在HEADを再確認後に統合する。
