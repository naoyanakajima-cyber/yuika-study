# PdM追加判断: parent_mode/生成器の既存CONTENT互換性（許可14・15番目）

2026-11-14 UTC。親から報告された初回全suite失敗を受けた静的調査のみ。tests/parent_mode.py、scripts/parent/embed.py、content-review.html、既存CONTENTテストの保存監視箇所を読んだ。テスト・製品編集は行っていない。

## 原因と判断

parent_mode.pyは全root HTMLに親確認markerがある前提でsplitする。PR11のcontent-review.htmlは、学習記録を扱わないメモリ内の独立確認画面であり、既存親runtimeを持たない。この統合で増えた既知の例外をテスト契約として明示する最小修正を推奨する。一般のmarker欠落を無条件skipする修正は不可。

14番目のmain比許可ファイルとして tests/parent_mode.py の冒頭静的入口検査だけを追加承認候補とする。ブラウザーの6アプリ列挙、保存隔離・削除・通知抑制・異常時fail-closedの全既存assertはそのまま保持する。製品8追加ファイルは原PR11とblob一致を維持する。

## 最小例外契約

1. 必須親確認対象6個を明示し、全て実在することをassertする: index.html、onin-review.html、kamakura-review.html、heian-review.html、yuika-review-v2.html、mock-focus-review.html。各対象に既存runtime同一性、charset位置、app script前の境界、境界外localStorage参照なしの検査を必ず適用する。
2. 例外は正確なファイル名 content-review.html のみ。このファイルも実在必須。例外処理前に下記静的assertを通す。markerの有無で対象を除外したり、失敗をcatchしてcontinueしたりしない。
3. 他のroot HTMLも元の境界検査へ必ず渡す。BEGIN/ENDの存在/順序（推奨: 各1個）を明示assertしてからsplitし、未知のmarkerless HTMLを失敗させる。未知ページの自動例外化は禁止。
4. CONTENT固有の静的assert: `let proposal=null,unsaved=false;` が存在し、localStorage/sessionStorage/indexedDB/Storage/cookieの保存API参照、YuikaParent/YuikaReports、親marker、外部script読込みがない。既存CSPの default-src/connect-src/form-action/object-src 'none' を維持。これらは意図の検査であり、一般的なJavaScript無副作用の証明とは報告しない。
5. 例外のすり抜けを防ぐため、対象をレビュー済みPR11の内容へSHA256で固定する方法を推奨する: `586e626a6759a3c1000f2ec50785627081569df75a71178e6d17482f948b030d`。この固定は新しい任意HTMLへ例外を広げないための境界。将来のCONTENT機能変更時は例外の妥当性を再レビューする。コメントに原PR11 HEAD 3d2ed2f9a62673d2fb086a360ae841096f35b63e と「既存メモリ内試作だけ」を示す。
6. 実際のstorage書込0、再読込、取消、JSON出入は既存 tests/content_review.py と tests/content_guidance.py が担当する。静的例外の導入だけで動的確認済みとはしない。全24suiteの2回目を最終修正commitで独立QAが実行し、初回のparent_mode失敗と修正理由も残す。ユーザーの同原因2試行上限を守り、3回目へ進めない。

この追加は合成教材の確認体験や保存仕様を変えない。mainの6アプリ保護を保ち、保存をしない既存独立試作について別の厳密な契約を課す修正である。

## PrM確認後の確定範囲: 生成器も限定修正する

PrMは14番目 tests/parent_mode.py と15番目 scripts/parent/embed.py の限定修正を承認した。現在のAGENTS.mdが標準生成手順としてparent/embed.py実行を案内しており、その手順が今回保持する既存CONTENTのメモリ内境界を変えるため、生成器も今回修正する。

scripts/parent/embed.pyの変更は「正確なcontent-review.htmlだけ、上記レビュー済みSHA256同一性をassertして生成対象から外す」に限定する。他の全HTMLは従来どおりruntimeを生成し、未知HTMLの処理をskipしない。6既存HTML、runtime.js、CONTENT本文は無変更。未知/変更済みCONTENTを黙って例外とせずassert失敗にする。共通分類moduleの新設・一般除外機構・UI変更は不要。

独立QAは隔離した一時コピーで生成器を実行し、contentを含む全tracked HTMLが実行前後で同一であること（idempotence）を確認する。さらに未知のmarkerless HTMLを置いたnegative probeでparent_mode冒頭の静的検査が失敗することを確認する。既存6アプリ必須条件と元の全assertも保持を照合する。実checkoutの製品を生成変更する必要はない。この原因修正検証後、第2回全24suiteを最終修正commitで独立QAが実行する。元PR11追加8ファイルのblob一致は引き続き必須。広範なリファクタはしない。
