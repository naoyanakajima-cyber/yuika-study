# cycle25 独立QA — c81候補の検証とC6指摘

担当 qa_theme_compatibility。実装者とは別。独立clean checkout /workspace/yuika-theme-validation-20261115、固定HEAD c81fb6b3a7e9c5c6c5d42431afe1d13a73c780d3。

## 現時点の判定

全必須23suiteは初回すべて成功したが、追加のC6図可読性確認で低コントラスト2箇所を観測したため、**c81の最終受入は未完**。統括へ即時報告し、製品編集せず候補を凍結保持した。修正版の固定HEAD検証は別途追記する。

## 実行した必須検査

2026-11-15T01:05:55.806551+00:00開始、01:11:07.194227+00:00完了。bash scripts/check_all.sh、312秒、exit0、23suite全件exit0、前後HEAD一致・dirty空。今回初回1回だけで再試行なし。suite別exit/秒数はc81-result.json、完全stdout/stderrはcheck-all-attempt1.log。

theme_reviewは全完了。前回未確認だったyuika-review-prototype/formatVersion1/payload.eventsのJSON書き出しとテーマキー非混入、print、別画面往復、未知3値の保持、get例外の標準起動、set例外時の画面内適用と学習警告保持、保存回復、親セッション復元/終了/通常領域不変、一時メモリのreload消去を含む。15合成回答の入力/選択/ヒント/採点/結果、状態・保存不変、キーボード、44px/8px、focus3:1、本文4.5:1、テーマ操作でのenqueue/request0も通過した。

通知suiteはmockを使う。全suiteには公開JS取得があり、全体通信0とは主張しない。theme suiteは既存font GETを15件遮断、想定外外部要求・POST到達・pageerror0。依存は既存venvを手動再利用したもので、自動snapshot引継ぎの成功証拠ではない。

## 新しいC6指摘

必須検査成功後のlong-content-probe初回は、768×1024の親確認モードで、組織図・仏教比較表・最長既存解説54025-38（81文字）をstandard→kamakura→standardで確認。内容・寸法・文字サイズ・行間の同一性、横overflowなし、切替操作への到達、標準復帰、次へ操作に問題なし。最長問題は合成fixtureで選び、実際のstart/check/next UIを利用した。選定エンジンの試験ではない。合成誤答1件、POST/pageerror0。6枚を独立QAが目視した。

組織図の『将軍』『執権（北条氏）』は13px白文字rgb(255,255,255)、枠背景rgb(181,124,101)で、実computed contrast **3.479281384346954:1**。両テーマとも4.5:1を満たさない。3状態×2ラベルの6観測であり、不具合6件ではなく対象2箇所。main86514edのHTMLを別fresh contextで表示し、該当ノードの実fill/fontを照合した。tree関数も完全一致し、今回テーマ変更による退行ではなく既存の可読性問題。しかし受入C6の未達として保持する。

## 同HEADの既存証拠と限界

cycle24で保存された静的境界検査・限定14検査・文字色68組（最低5.010）の証拠は同HEADとして参照し、今回の新規件数に加算しない。mainの4既存script/CSP/親runtime/通知/共有asset/他HTML保持、親6画面両テーマ、同run/学習DOM・親セッション回答/一時メモリ隔離を参照する。provenance.jsonに参照先とhashを保存。

Chromiumのみ。実機Safari/iPad、native zoom、本人嗜好・学習効果、実データ、公開動作は未確認。標準全体のpixel一致や全SVGの完全なアクセシビリティを保証しない。実メール/Chat、デプロイ、外部変更、pushは行わない。外部Workersの結果はこのクラウドQAと別扱い。

証拠: /tmp/yuika-cycle25-qa。現在のC6指摘に対する修正・新固定候補の検証待ち。
