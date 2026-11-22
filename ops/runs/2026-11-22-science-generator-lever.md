# 理科てこ復習・記録を再生成から保護する

## 問題と範囲

前cycleの `SCIENCE-GENERATOR-LEVER-01` を継続。既存PR10の `804f9f648c8634ea26d4ca7fc26cf6b473029475` でも、理科HTMLにあるてこ固有の再開・段階順・解放・挑戦・日次進行と記録項目が生成元に欠ける。再生成によって日々の復習や記録の互換性が失われる問題を防ぐ。

観測mainは `58f8b53b4da69806d15a126fc525b65893a0bf35`、開始時運用正本は `a27f063e062723fe3b4df27360ef3d7b7c4e9f88`。指定4文書をこの同一commitから取得して確認し、leaseを通常pushして取得した。新CEO判断の実読・取り込みは0。既存製品draft PR10/11/12の3件を維持する。

PdM `pdm_science_generator` は既存埋込動作を生成元へ反映する最小修正を提案。PrM `root` が受入れ、Engineer `engineer_science_generator` が独立checkoutで実装、別担当 `qa_science_generator` が固定候補を独立検証する。

## 受入条件

1. 既存PR10理科埋込のてこ動作をscience.js/runtime.jsへ反映。教材28問・ID・正解・解説・図・保存キー・版・選定アルゴリズムは変更しない。
2. unit付き再開、初回段階順、誤答補助、期限→弱点優先、step4解放/挑戦、日次の表示件数と実出題を保持する。
3. answerUnit/answerTagを合成回答から保存・reload・JSON往復し、項目なし旧記録を受理、不正値/未知項目を拒否する。
4. 実際の7本生成順を隔離コピーで試し、最初の成果物保持と2回目差分なしを確認。旧HEADで欠落を検出する回帰テストを残す。
5. PR10理由付き復習/count・共通runtime他4ページ・親隔離/通知抑止を保持。共通生成に伴う他4HTMLのscience条件false分岐各1行の同期はPrM受入れ、それ以外は不変とする。
6. 固定候補で全必須suiteと768×1024の合成通常/親経路を独立QA。教材内容・UI・アルゴリズムの新設や本番操作は対象外。

## 環境と保存

管理クラウドのreadyを確認し、既存checkoutから専用worktreeを手動準備した。既存依存を必要な範囲で手動再利用し、自動snapshot引き継ぎ成功とは扱わない。実データ・個人回答・教材写真・実通知は使用しない。

PR9/10のタスク添付は各1回呼び出したが応答せず、待機を中断。添付成功は未確認であり、GitHub保存とは区別する。新規PRは作らない。

## 実装と回帰検証

候補 `f60f6b2bc7c8f0b21d0789b599edf5a13269f5e5` は旧PR10を親とする修正。science.jsに既存埋込のてこ処理を反映し、prototypeの理科専用許可列へanswerUnit/answerTagを同期した。理科HTMLはbyte不変。他4HTMLは非理科画面では実行されないscience条件分岐の許可列1行だけ同期、その他はbyte不変。教材・図・保存キー・選定/採点設計を変更しない。

新しいgenerator_preservationはtrackedファイルを一時コピーし、実7本生成の1回目を元成果物と比較してから2回目の不変も検証する。安定した退行を2回目の冪等性だけで見逃さない。元checkoutを生成で書き換えないことも確認。Engineerは生成元同期後と新規test/docステージ後に実行して成功し、旧804f9fへ同じテストを移植した初回実行は理科HTML変更を検出して期待exit1。失敗を製品候補の失敗とは混同しない。

既存lever suiteへ合成回答の保存後reload、実download、空の試作へfile input取込、単位/tag/未知項目の不正入力拒否・既存データ不変を追加して焦点検証成功。全suiteは別QAへ委任した。[Engineer証拠](../evidence/2026-11-22-science-generator-lever/engineer.json)。

## 独立確認の実行範囲

QAは `f60f6b2bc7c8f0b21d0789b599edf5a13269f5e5` の独立detached checkoutで必須31suiteを開始。途中で統括がdocの検証順序の記述誤りを見つけ、配送候補 `15265078a71bb6540b8db90c89eaf351d7f8913d` で説明1行だけ訂正した。製品・テストの変更はなく、全suiteを最終HEADで再実行したとは扱わない。同一性の独立照合と、最終doc入りの生成回帰確認を別に記録する。

新規限定probeはf60候補、通常/親の2contextで初回成功。実UIの数値誤答からcm単位/誤答tagを生成して保存→reload→実JSON download→空保存先へのfile input import→reloadを確認。項目なし旧形式を実importし、不正単位・不正tag・未知項目は全体拒否して既存保存を不変に保つ。親の本人localStorageは不変。POST要求0/pageerror0、外部font GET11件は遮断。通常/親の合成採点画像2枚を統括も目視したが、全画面/全問題の目視成功とは扱わない。

## 次の仕事

PdMの追加確認をPrMが受入。解消は独立QA成功後も既存PR10のdraft候補に限定する。mainやPR11/12へ修正を反映したとは報告しない。次cycleはPR11→PR12の最新HEADで同じ欠落の有無を照合し、存在する場合だけ各branch固有の埋込動作を生成元へ同期する範囲を確認する。PR10のscience.js全体を転載して未マージの理由付き復習などを混入させない。教材確認/試し解き・テーマの各固有機能と生成後の成果物保持を独立QAし、同じ既存draft PRへ保存する。新PRは増やさず、承認待ち上限3件を維持する。

## 初回必須検証で見つかったテスト準備の不足

f60候補の全31suite初回は30/31成功、exit1、308秒。science_daily_countのNode抽出oracleがLEVER_UNIT未定義で停止した。生成元同期により、既に理科HTMLに存在したてこ参照がsource抽出テストにも現れたが、旧fixtureにはその依存がなかった。製品の選定処理変更や通常UI失敗とは区別する。

Engineerは非てこ20問・履歴なしfixtureに単元定数とunlock=falseを明示し、既存の優先順/出題順/乱数消費/件数の28組の比較assertを保持する最小補完を行う。てこ自体は既存lever suiteの検証範囲を維持する。新候補を固定し、独立QAが差分確認と全suite2回目を実行する。初回の失敗結果は削除しない。

修正候補 `d26d10dea80b93cef7a47dbd814f76e3f69d3934` は1526507からtests/science_daily_count.pyのコメント3行とfixture1行だけを変更。Engineerの焦点検証はNode28例と既存UIが初回成功。統括もassert不変と、f60以降の差分がdoc説明とfixtureだけで製品byte不変であることを確認した。最終配送候補はd26とし、途中の1526507を最終成果とは扱わない。

## 最終結果と保存

最終固定 `d26d10dea80b93cef7a47dbd814f76e3f69d3934` で独立QAの必須31suiteは2回目に全件成功、exit0、322秒。前後HEAD一致、開始/終了status空。最終HEADで7本生成列の成果物保持・2回目不変も実行済み。初回失敗の結果と原因を含め [QA.md](../evidence/2026-11-22-science-generator-lever/QA.md) と [final-result.json](../evidence/2026-11-22-science-generator-lever/final-result.json) に各suite終了コード・秒数を保存した。

独立QA自身も旧804f9fへ同一新テストを移植し、初回生成が理科HTMLを変える負例を確認した。通常/親probeの実行HEADはf60、最終d26と製品byte一致を独立照合しており、最終でprobeを再実行したとは扱わない。途中152のdoc-only確認も履歴として保存。最終差分は11paths、製品内容の再設計はない。

統括はremote lease所有・期限、旧PR10 HEAD/draft/open、main不変を再確認して既存 [draft PR10](https://github.com/naoyanakajima-cyber/yuika-study/pull/10) へ通常pushした。外部CIの実状態は今回台帳へ別記し、ローカルQA成功と混同しない。新PR0、製品承認待ち3、新CEO判断0。本番merge・公開・実送信・課金・権限変更なし。

実機Safari/iPad、本人の実回答や学習効果、公開環境は未確認。`SCIENCE-GENERATOR-LEVER-01` の解消はPR10 draft候補だけであり、main/PR11/PR12へ反映済みではない。
