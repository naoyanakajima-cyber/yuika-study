# CONTENT-MVP：確認済み合成案を保存せず試し解きする範囲提案

PdM `pdm_content_trial_delivery`、2026-11-14。運用正本4207084（lease取得0ada897、cycle-20261114T230830Z）と、製品基点62f34de238e9d1d62c796aac3a4b43418043d17fを読み取り照合した。docs/agent-team.md、ops/AGENTS.md、ops/board.json、docs/product/content-try-spec.md、前回content-import-guard仕様、現行content-review.html/AGENTSを確認。製品編集・試験・pushなし。

## 提案と価値

既存PR11内で、確認した合成問題案を出題順に解き、問題文・許容表記・選択肢・ヒント・解説の使い勝手を点検できる全体実装へ進むことを推奨する。保護者役の教材点検であり、児童の理解度測定ではない。前回の非同期読込ガードは完成済み基盤として再利用する。

既存CONTENT-TRY-SPECの全契約を採択候補とし、G01〜G13/S01〜S13を削らない。確認済み合成text/choiceの1〜10問、現在メモリ内の案だけを対象にする。判読不明画像は開始拒否の負例。成功用画像の新規制作、OCR/LLM、実入力、記録読取、外部接続、保存先D02、学習本体への教材登録は含めない。新規製品PRは増やさない。CEO新回答はない。

## 現行HEADへの実装対応

- 現行のvalidateShape/issues/sourceAsset、個別確認、案JSON形式をそのまま開始検査に再利用する。全問現在revisionで確認済み・未解決0・有効type/choice・text候補正規化後1〜200 UTF-16を追加条件とする。disabledだけでなく実行時にも検査し、不成立の理由と修正箇所を示す。
- importGeneration/workGeneration/pendingImportを再利用。pending中は開始不可。試し解き中の案編集・確認・輸入・サンプル・取消・出力を可視性と実行時の両方で拒否し、輸入採用直前にもE状態を検査する。既存の後着結果保護を維持する。
- 試し解き状態をproposalから分離し、全問snapshot、開始revision、session identity、現在question identity/index、状態generationを保持する。開始後の入力/ヒント/採点/次へ/終了は案・確認・generatedFields・unsavedを変えない。採点/次へ前に案全体の内容・revision・確認を再照合。不整合時は試行全消去し理由を表示する。
- 操作closureが発火元session/question/state-generationを保持して現在値と照合する。採点と次問/終了でgenerationを進め、古い問・旧状態・旧sessionの遅延入力/ヒント/採点/次へを無効化する。試行領域の再構築は試行を停止・消去する。通常の入力更新を再開始として扱わない。
- 確認画面全体・原本・転記を試行中はhidden等で可視/keyboard/アクセシビリティツリーから除外。試行側の正答候補一覧と解説は採点後だけ生成し、ヒントは明示操作でのみ開く。文字列をHTML/URLとして解釈しない。768×1024とkeyboard/focus/statusを確認する。
- 短答はNFKC+trim完全一致、answer/aliases/readingsを候補とする。内部空白/大小文字/かな種/句読点を勝手に揃えない。非文字列、空、生200超、正規化後200超は入力エラーで回答保持・未採点・正答非開示。choiceは現在問の整数option index identity、answerとの生文字列一致、未選択/範囲外/旧identityはエラー。
- 現在問の回答・結果・ヒントだけを一時保持し、次問で前問分を消す。終了でsnapshot/session/回答/結果/ヒントと表示DOMを全消去。再開始は全問未回答。累計点・履歴・弱点登録なし。
- beforeunload条件へtrial存在を加え、案をJSON出力済みでも試行消失を知らせる。離脱を取り消した同一文書は状態保持、実離脱/新文書/履歴復帰/BFCache復帰では過去回答を復元しない。pagehide/pageshow等で消去し、実ブラウザー遷移と合成persistedイベントを検証する場合は実施範囲を区別する。
- CSP、6学習HTML、ID/保存KEY/採点/選定/親runtimeを変更しない。試行回答をstorage/cookie/cache/serviceworker/window.name/URL/history/案JSON/download/console/分析へ出さない。既存hash例外2箇所は最終HTML候補へ整合→固定HEAD独立memory-onlyレビュー→PrM受入の順。ガードの許可範囲を拡張しない。

## 必須採点受入 G01〜G13

| ID | 合成例と期待値 |
|---|---|
| G01 | T1 answer氷へ氷：一致 |
| G02 | T1 readingこおりへ全角空白＋こおり＋tab：一致 |
| G03 | T1へコオリ：不一致 |
| G04 | T1へこ おり：不一致 |
| G05 | T1へ氷。：不一致 |
| G06 | T2 answerABCへＡＢＣ：一致 |
| G07 | T2へabc：不一致 |
| G08 | T2 alias A BへA全角空白B：一致、A二連空白B：不一致 |
| G09 | T3 answerガラスへｶﾞﾗｽ：一致 |
| G10 | T1へ空/trim空：入力エラー・未採点 |
| G11 | T1へx×200：有効不一致、x×201：生上限エラー |
| G12 | T1へ㍍×51：正規化後204でエラー |
| G13 | C1 options東/西、answer東：index0一致、1不一致、null/2/文字列東/非整数/旧identityはエラー |

追加境界：一致候補/回答が200 code unitで正解、生201でtrim後200でもエラー、😀×100の生200一致/×101の202エラー、非文字列エラー。正規化後200超のanswer/alias/readingは開始時拒否する。配列を跨ぐ候補重複を新エラーにしない。

## 必須状態受入 S01〜S13

| ID | 期待する操作・不変性 |
|---|---|
| S01 | 全確認E→A1、順序固定・未回答・ヒント非表示、案不変 |
| S02 | draft/旧revision/一部確認/未解決/形式不正/再入力confirmedを開始拒否、原因・修正先 |
| S03 | 入力/ヒントは現在A内だけ、案不変・解説非表示 |
| S04 | 空/長すぎ/未選択はA保持、入力保持、正答/次へなし |
| S05 | 有効回答の採点連打は一回Gへ、入力固定・答え/解説表示 |
| S06 | Aから次へ不可、最終Gから次へ不可・終了を提示 |
| S07 | G(i)→A(i+1)、前問回答/結果/ヒント消去・次問未回答 |
| S08 | A/G終了→E、試行全消去、案/確認/unsaved不変、再確認ダイアログ不要 |
| S09 | Eへ戻り編集でrevision+1・全確認失効、再開始は全問明示再確認 |
| S10 | A/Gの輸入/サンプル変更拒否、Eの旧読込競合/失敗/破棄拒否の保全維持 |
| S11 | E案取消は既存mayDiscard、拒否E/了承Ø。試行中はまず終了 |
| S12 | 保存済み案でもtrialなら離脱警告、cancel時維持、実離脱/再読込/履歴/BFCache復帰で試行消去 |
| S13 | 案不一致/試行再構築は終了消去、旧session/問/状態generation操作は無効、通常描画は再開始しない |

## 実施計画と判定

技術的な新依存やCEO未決への接続は不要で、1画面内の状態機械として実装可能と判断する。ただし時間内完了の保証ではない。既存仕様を全面再作成せず本対応表をEngineer/QAへの差分指示とする。実装とfocused合成受入をおよそ15分でfreezeし、独立QAの全G/S・境界probeと必須check_all（現25＋追加suite）に少なくとも7分、保存・PR・lease解除へ5分を残す。時間不足や同一原因2試行で未解決なら受入を縮めず、具体的未完ケースと再開commitを記録する。

実装者とは別のQAが固定clean HEADで機能/副作用/既存回帰を実測するまで「試し解き完成」「QA成功」と報告しない。BFCacheや実機iPadを実測できなければ未検証を明記し、合成イベントを実機確認へ読み替えない。PRはdraft/CEO判断待ち、main merge/公開/実通知/課金/Secrets権限共有変更なし。

今回PdMが実施したのは指定公開仕様・合成データ構造・固定HEADの静的照合と範囲提案だけ。実装・試験の結果はEngineer/QAが実施後に記録する。
