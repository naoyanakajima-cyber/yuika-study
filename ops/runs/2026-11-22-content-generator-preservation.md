# 教材追加PRの生成処理と学習記録の保持

## 目的と範囲

`SCIENCE-GENERATOR-LEVER-01` の前回PR10修正に続き、既存PR11 `ee228ca0a1865d0a56f4302cd9342a4f66738561` を直接照合した。PdMは、PR11でも理科HTMLにあるてこの再開・解放・段階順・挑戦・記録項目が生成元に欠けることを確認。教材案を確認して試し解きする試作でも、再生成によって既存の学習動作や記録を失わないよう修正する。

運用正本 `3d4c954ecc8de309478eb3a17eb13ded7d217a92` の指定4文書を同一commitから取得して確認し、leaseを通常pushで取得。観測mainは `58f8b53b4da69806d15a126fc525b65893a0bf35`。PR10/11/12の3件を照合し、既存PR11の履歴を保持する。新CEO返答の実読・取り込みは0。

PdM `pdm_content_generator` → PrM `root` 受入 → Engineer `engineer_content_generator` の専用checkout実装 → 別担当 `qa_content_generator` の独立QA。PR10は原因と検証方法の参考であり、PR10固有のscienceDailySources・実問数表示・おすすめ復習を持ち込まない。

## 受入条件

1. PR11自身の理科埋込処理をscience.js/runtime.jsへ同期。理科HTML、教材28問・ID・正解・解説・図・保存キー・版・選定設計は不変。
2. 他4HTMLは共通生成に伴うscience条件falseの許可列1行だけ同期。content-review.html、6fixture、schema、固定hash、C1–C11/G–S/画像7条件を維持。
3. 実7本生成列をtrackedの隔離コピーで検証し、最初の成果物保持と2回目差分なし、旧PR11での欠落検出を確認。
4. 固定候補で全32suite（既存31＋生成回帰）を独立実行。既存assert/CSP/固定hash境界を緩めない。
5. 768×1024の合成教材を編集→未確認開始拒否→確認→非保存の試し解き→終了/JSON再入力し、確認失効と学習storage不変、通知抑止を確認。
6. 通常/親で理科unit/tag付き合成回答の保存・reload・JSON往復、項目なし旧形式の受理、不正値/未知項目拒否を限定確認。

## 環境・権限・保存

管理クラウドのreadyを確認し、独立worktreeを手動準備。既存依存の再利用も手動準備として記録し、自動snapshot引き継ぎ成功とはしない。個人回答・教材写真・メール/Drive情報は使用しない。検証は合成データとmockのみ。

本番merge、公開、実送信、課金、Secrets・権限変更はしない。新規PRを作らず製品承認待ちは3件を維持する。PR9/11のタスク添付は各1回呼び出したが応答せず待機を中断、成功未確認。GitHub保存とは区別する。

## 固定候補と実装範囲

固定候補 `3920f1642692c88a8d6870480bc3f98f71558d24` はPR11 ee228caを親とする10pathsの変更。PR11自身のscience埋込を生成元へ同期し、共通prototype理科許可列を同期した。理科HTMLはbyte不変、他4HTMLはscience条件の許可列1行だけ変更、それ以外の基点99pathsはbyte一致。content HTML/fixture/schemaやPR10独自機能は変更・追加していない。

新しい生成回帰はtrackedファイルを一時コピーし、実際の7generatorを実行。初回から元成果物に一致し、2回目も不変であること、元checkoutも不変であることを検査する。Engineerの初回は成功。同一テストを旧PR11の隔離コピーへ移植すると、初回生成で理科HTMLの差分を検出して期待exit1となった。

既存lever testへ単位・タグ付き合成回答の保存後reload→実download→空の試作へfile input import、invalid unit/tag/unknown拒否と記録不変を追加し焦点検証が初回成功。全32suiteは独立QAへ委任した。この焦点検証の再読込は書出し前。取込後の再読込は独立probeで別途確認した。[Engineer証拠](../evidence/2026-11-22-content-generator-preservation/engineer.json)。


## 独立レビュー・追加検証

独立Reviewer `qa_content_generator` は固定候補3920f16を別のdetached checkoutで確認。実7本の生成列を隔離archiveで2回実行し、14コマンドがexit0、各回とも全tracked bytesが元と一致した。同じ回帰テストを旧PR11 ee228caへ移植したnegativeは、初回生成の理科HTML差分を検出し期待exit1となった。

CONTENTのHTML・6fixture・4仕様・5suiteの計16pathsを旧PR11とhash照合し一致。理科HTMLはbyte不変、science/prototype生成元と理科埋込のhashも一致した。他4HTMLの許可列1行差分と、非理科では当該条件がfalseであることをsource読取で確認した。

QA静的補助スクリプトは、変数名を`allowed=`と想定した箇所、理科判定をpathname式と想定した箇所で計2回停止した。製品suite失敗とは分離し、同bundleの3回目は実行していない。実sourceと4差分を読み、未実施だった生成・旧版negativeのみ別途実行した。停止理由・到達点・実スクリプトを証拠へ保存する。

768×1024の新規合成UI probeでは、既存理科の実UI合成回答を保存し、三角形画像とtextの編集・未確認開始拒否・明示確認・非保存採点・終了・JSON再入力による確認失効を確認。教材操作中の保存API書込・POST試行・pageerrorは0、理科記録をbyte保持した。理科seed/readbackのフォントGET2件は遮断して別計数。通常/親の別probeはunit/tag付き合成回答→reload→実download→空の試作へfile-input import→reloadを実施し、項目なし旧形式の受理、不正unit/tag/未知項目の拒否、親モードの子記録不変を確認した。こちらもPOST/pageerrorは0、フォントGET11件は遮断した。

統括は三角形の非保存採点画面と親モードのてこ補助画面の2枚を実見した。独立QAは原本・通常/親てこ・三角形trialの4枚とtext画面を実見し、保存画像は4枚に限定した。実機iPad/Safari、本人試用、学習効果、OCR/実写真処理は未検証。

## 次の一手

既存PR11は合成教材の試用判断待ちを継続し、本番merge/公開は未承認。生成保持の修正はdraft PR10/11内に限る。次回は既存PR12の最新HEADで同じ原因を照合し、テーマ表示とそのbranch固有学習処理を保持する範囲をPdM→PrMで確認する。main/PR12修正済みとは扱わず、新しいPRを増やさない。


## 全体検証・保存結果

独立QAは固定候補3920f16、開始/終了cleanで `bash scripts/check_all.sh` を1回実行し、既存31＋新生成回帰の全32suiteがexit0、全体exit0、318秒で成功。結果記録時刻は2026-11-22 17:14:33 UTC。前回HEADの検証を今回の成功へ流用していない。[各suite結果](../evidence/2026-11-22-content-generator-preservation/suite-result.json)、[独立QA](../evidence/2026-11-22-content-generator-preservation/QA.md)、[全ログ](../evidence/2026-11-22-content-generator-preservation/check-all-attempt1.log)。

統括はremote leaseの所有者・期限・ops HEADを再確認し、検証済み3920f16を既存 `codex/content-review-mvp` へ通常pushした。製品PR11はdraftのまま更新対象。main58f8b53、PR10 d26d10、PR12 e89aa33は再照合時に不変。新規PR0、CEO返答取り込み0、製品判断待ち3件。外部check状態・PR本文更新・lease解除の最終保存情報は同runの台帳に記録する。
