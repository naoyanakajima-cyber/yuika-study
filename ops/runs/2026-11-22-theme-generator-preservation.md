# テーマ試作の生成処理と学習記録の保持

## 目的と範囲

`SCIENCE-GENERATOR-LEVER-01` のPR10/11修正に続き、既存PR12 `e89aa335936508c6e4984c523ec65da97f510cbd` 自身の生成元と埋込を照合した。理科HTMLにあるてこの再開・段階順・挑戦解放・回答unit/tagが生成元に欠けており、テーマ試作でも教材更新によって学習動作を失わないよう同期する。

正本ops `de44f4aac0a1e1da2b75221383c21b1a1e725847` の指定4文書を同じcommitから読み、空leaseを確認して通常push取得。mainは `58f8b53b4da69806d15a126fc525b65893a0bf35`、PR10 d26d10/PR11 3920f16/PR12 e89aa33はいずれもopen draft。製品判断待ちは3件、新CEO返答の実読・取り込みは0。

PdM `pdm_theme_generator` の直接source調査→PrM `root` の6条件受入→Engineer `engineer_theme_generator` の独立checkout→別担当 `qa_theme_generator` の独立QA。前回のQAを今回の成功へ流用しない。

## 受入条件

1. PR12自身の埋込をscience/prototype生成元へ同期し、理科HTML、28てこ教材・ID・正解・図・保存キー・版を保持。PR10/11の固有機能を取り込まない。
2. 他4HTMLはscience条件falseの許可列1行だけ同期。鎌倉テーマCSS/UI/JS、模式図、印刷、仕様・既存テストをbyte保持。
3. 隔離コピーで実7本生成の初回成果物保持と2回目不変を検証。旧PR12では新回帰が欠落を検出する。
4. 通常/親でunit/tag付き合成回答の保存・再読込・実JSON往復、項目なし旧形式受理、不正/未知項目拒否と記録隔離を確認。
5. 固定候補で既存27＋生成回帰の全28suiteを独立実行。既存assert/CSPを維持。
6. 768×1024の通常/親で、テーマ切替による入力・採点・学習記録の保持、設定復元、図文字・印刷、通知抑止を限定確認。

## 環境と権限

管理クラウドreadyを確認。既存checkout/依存は存在し、今回用独立worktreeと既存venvの再利用は手動準備として扱う。公開snapshotの自動引き継ぎ成功とは報告しない。起動skillの既存手順を参照し、ローカルPCへ代替していない。

合成データ/mockのみ。個人回答・教材写真・メール/Drive情報を取得せず、本番merge・公開・実送信・課金・Secrets/権限変更・旧自動化再開は行わない。新規PRを増やさず既存PR12を更新対象とする。PR12のタスクattachは1回呼び出したが応答せず待機を中断、成功は未確認。

## 次の一手

生成保持を3draftへ保存できた後も、各製品の合成試用判断待ちとmain未修正を残す。具体的な新差分・再現不具合・CEO試用所見がなければ、同じ実装や無目的なQAを反復せず終了する。採用/公開承認は実際に読んだCEO返答が台帳へ取り込まれるまで推測しない。


## 固定候補

Engineer候補 `00c4ccb3b501223366a5f0a736567231ea9b8043` は旧PR12を親とする10paths/130追加11削除。理科HTMLはbyte不変、他4HTMLは理科専用許可列1行のみ、残りの基点85pathsはbyte一致。鎌倉テーマのCSS/UI/JS/模式図/printは保持され、仕様と既存theme testも不変。PR12自身の埋込をsourceへ抽出同期し、PR10の日次実問数/おすすめ復習やPR11教材確認室を持ち込んでいない。

Engineerの新生成回帰は初回成功（実7生成を2回、全tracked bytes保持、元checkout不変）。既存leverへ単位・タグ付き合成回答のreload→実download→空試作へのfile-input importと不正値拒否を追加し、焦点検証は初回成功。旧PR12への新回帰移植は初回理科HTML差分を検出して期待exit1。[Engineer証拠](../evidence/2026-11-22-theme-generator-preservation/engineer.json)。全28suiteは実装者ではなく独立QAへ委任した。


## 独立静的確認・限定probe

独立QAは候補00c4ccbのdetached checkoutでsource/埋込同一、理科HTML不変、他4HTMLの許可列1行差分、テーマ仕様/testと他85paths不変を初回確認した。実7本生成を隔離copyで2回実行し、14コマンドexit0、各回全tracked bytesが元と一致。旧PR12へ同じ回帰を移植したnegativeは初回理科HTML差分の期待exit1となった。

新規theme probeは通常/親の各5問で、入力/選択・ヒント・採点・結果の同じ学習状態をテーマ切替前後で比較し保持した。再読込で鎌倉テーマと5合成記録を復元し、親モードの子localStorageは不変。通常モードでは標準/鎌倉のscreen/printで模式図2ラベルのcontrastを6.26572:1と測定し、printのテーマUI非表示・保存値不変を確認した。同originのテーマ設定値が変わっても、理科代表てこ3図のSVG/文字色/線/寸法は不変だった。

別の理科probeは通常/親でunit/tag付き合成回答→reload→実download→空試作へのfile input import→reload、任意項目なし旧形式受理、不正unit/tag/未知項目拒否と保存済み記録不変を確認した。テーマ操作由来の通知呼出0、両probeのPOST/pageerror0。遮断したフォントGETはtheme側16件・science側11件として別計数した。

独立QAは通常/親の入力途中、模式図、理科てこ図の4画像を実見した。統括は親モード入力途中と鎌倉模式図の2画像を実見した。実機Safari/iPad・native zoom・本人の好み・学習効果は未検証であり、全28問の全面再校閲ではない。


## 全体検証・保存結果

独立Reviewer `qa_theme_generator` は固定候補00c4ccb・開始/終了cleanで `bash scripts/check_all.sh` を1回実行し、既存27＋生成回帰の全28suiteがexit0、全体exit0、326秒で成功。結果記録は2026-11-22 18:18:26 UTC。独立静的確認・実生成2回・旧版negative・theme/science probeも初回成功。[各suite結果](../evidence/2026-11-22-theme-generator-preservation/suite-result.json)、[独立QA](../evidence/2026-11-22-theme-generator-preservation/QA.md)、[全ログ](../evidence/2026-11-22-theme-generator-preservation/check-all-attempt1.log)。

統括はremote leaseの所有者・期限・ops HEADを再確認し、検証済み00c4ccbを既存 `codex/kamakura-theme-mvp` へ通常pushした。既存PR12はdraftのまま更新対象。直前照合ではmain58f8b53/PR12 e89aa33に外部更新なし。新規PR0、新CEO返答取り込み0、製品判断待ち3件。PR本文・外部check・lease解除の最終保存情報は同runの台帳に記録する。
