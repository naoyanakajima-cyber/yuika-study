# 鎌倉テーマPR12とてこ追加mainの互換性

## 目的と範囲

毎日の復習画面で好みの見た目を選び、読みづらければ標準へ戻せる既存の鎌倉テーマ試作を、新mainの教材を維持して追従する。
元PR12 HEADは `9fc4bbf3e6c72e09327b6610338f12937fc7aba5`、観測mainは `58f8b53b4da69806d15a126fc525b65893a0bf35`。PR10/11の同main互換性は前runまでに確認済みで、今回それらの未マージ独自改善を取り込まない。
外部PR30のmergeは観測事実であり、今回の本番操作や新CEO承認ではない。新CEO返答の実読・取り込み0。

PdM `pdm_theme_lever` は既存C1–C8/T1–T11を再設計せず互換追従する範囲を提案し、PrM `root` が受入。Engineer `engineer_theme_lever` が独立checkoutへ実装し、別担当 `qa_theme_lever` が固定候補を検証する。

## 受入条件

1. PR12履歴を保持し、新mainとの最小統合に留める。mainとの差は既存テーマ5ファイル境界。鎌倉外HTML/assets/通知/履歴/生成元はmainと一致させる。
2. 入力途中・ヒント後・採点後・結果のテーマ切替で、run/問題列/入力/学習DOM/採点/記録を保持する。テーマ操作で回答や再通知を増やさない。
3. テーマ専用キーと親storageの隔離を維持する。未知値・get/set拒否・回復、親session拒否時の一時メモリ、終了時通常設定へ戻る動作を既存suiteの具体assertと対応付ける。
4. aria/keyboard/focus/44px/8px/標準復帰/printと鎌倉模式図2枠限定改善を維持。候補のcomputed色で文字4.5:1・必要UI3:1を確認し、旧実測値を転用しない。
5. 理科画面へのテーマ展開はしない。てこ図生成/ラベル/寸法をmainと同じに保ち、鎌倉設定保存前後の図・配色の非干渉を確認。代表的な支点・おもり・距離・ばねばかりの文字の欠け/重なりを768×1024で限定目視する。
6. 固定候補でmain26＋theme1の全27suiteを実行し、実行者・HEAD・各終了コード・秒数を保存する。全28問の再校閲や旧probeの全面反復は行わない。

## 実行環境と限界

管理クラウドの起動を確認し、指定4文書を運用branchの同一最新commit `700b047b5ea4ff7918e97b8f4b60ea1918a5fe6e` から読んだ。既存checkoutから作業用worktreeを手動準備した。自動snapshot引き継ぎ成功とは報告しない。
合成データ・mock通知のみ。本人の好み・学習効果・実機Safari/iPad・公開画面は今回未検証。本番merge・公開・実送信・課金・Secrets/権限変更なし。
PR9/12のタスク添付を各1回呼び出したが応答せず、待機を中断した。添付成功は未確認、GitHub保存とは区別する。
製品判断待ちはPR10/11/12の3件を維持し、新規製品PRを作らない。今回見つかった理科生成処理の不整合を次の具体的な仕事とする。それ以外の合成試用は、具体的なフィードバック・再現不具合・新main/PR差分・実読して台帳へ反映済みのCEO判断がある場合に進め、根拠のないQA/環境調査は繰り返さない。

## 固定候補と生成処理の新所見

候補 `e89aa335936508c6e4984c523ec65da97f510cbd` は旧PR12と新mainを親とするtopic merge、競合なし。mainとの差は既存5ファイルで、旧theme HTML/test/specはbyte一致。main26＋theme1の27suiteを登録している。
Engineerのdesign/build_summary→design/embed→parent/embedは全追跡ファイルbyte不変。一方、practice/embed→practice/embed_science→history/embed→prototype/embed→design/build_summary→design/embed→parent/embedの7本の列では、理科HTMLだけに7追加/29削除が生じ、てこ固有の再開先・解放filter・daily選定/進行・challenge/sessionとanswerUnit/answerTag許可項目が失われた。
この生成結果は採用せず、自分が生成した理科HTMLだけを統合直後のmainと同じ内容へ戻した。候補の理科HTMLと生成元はmain byte一致、テーマ差分に生成器修正はない。
mainで別に再実行したわけではなく、同じsource/target blobであることから既存main生成元/成果物の不整合と判断した。個別scriptごとの因果切り分けは未実施。全生成処理の整合が成功したとは扱わない。[Engineer証拠](../evidence/2026-11-22-theme-lever-main/engineer.json)。

PdMは読取追加確認でこの所見をgoal1の回答記録・苦手復習保護に直接関係する次cycle候補と判断。現在のテーマ候補はmain教材を保持しており、本件修正は今回へ追加しない。
次cycleは既存PR10の最新差分と照合し、生成元へてこ進行/復習/再開とanswerUnit/answerTag検証・旧記録互換性を反映する最小修正を検討する。実際の生成順序で成果物保持と2回目差分なし、共通runtimeの他画面/親隔離/通知抑止、固定候補の独立QAを受入条件とする。現PR10の理由付き復習を再生成で消さないこともPrM確認する。待ち枠を増やす新PRやmain直接修正はしない。

## 独立画面確認

候補e89aa335で通常/親各5問の入力・hint・採点・結果を通じてテーマを切替・復帰し、再読込後5 eventsを確認。テーマ操作による通知呼出0、親モードの本人localStorage不変。標準→鎌倉→標準の同origin保存前後で代表てこ3図（lever-01/27/28）のSVG DOMとcomputed文字色・線・寸法が一致した。模式図2ラベルは両テーマ/screen/printの候補実測で6.265720821:1。旧実測値の転用ではない。
QAは12枚、統括は通常hint・親home・てこ27/28の4枚を目視。768×1024の限定した範囲で支点・おもり・距離・ばねばかりの文字欠けや重なりは見られなかった。全28問・全画面・実機の目視成功を主張しない。

## 最終検証と保存

独立QA `qa_theme_lever` が固定候補で `bash scripts/check_all.sh` を初回実行し、全27suiteがexit0、323秒。前後HEAD一致、tracked差分なし。冒頭のuntracked `.venv` は手動再利用のruntimeリンクであり、その注記を原ログへ残した。終了時statusは空。新しい限定probeも初回成功。全suite各終了コード・秒数は [final-result.json](../evidence/2026-11-22-theme-lever-main/final-result.json)、保存境界assertとの対応は [QA.md](../evidence/2026-11-22-theme-lever-main/QA.md)。

統括はremote lease所有・期限とPR12旧HEAD/draft/open、新mainの不変を照合後、候補を既存 [draft PR12](https://github.com/naoyanakajima-cyber/yuika-study/pull/12) へ通常pushした。製品HEADは `e89aa335936508c6e4984c523ec65da97f510cbd`。外部CI状態は台帳の今回runへ別記し、クラウドQAと混同しない。新規PR0、製品承認待ち3。

次は `SCIENCE-GENERATOR-LEVER-01` を既存REV-MVP/PR10内で最新差分照合・PrM範囲確定から進める。THEME-MVPは合成試用の具体的フィードバック待ち、方向性D05を公開承認へ拡張しない。今回の修正で本番merge/公開・実送信は実施していない。
