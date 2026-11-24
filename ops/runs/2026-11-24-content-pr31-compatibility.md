# 教材確認・試し解きとPR31の互換同期

## 目的・受入範囲

既存draft [PR11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11) の合成教材確認・編集・JSON入出力・保存しないテキスト/画像試し解きを保持し、外部PR31の終了時学習報告と両立させる。PR10固有のおすすめ復習・日次実問数機能は持ち込まない。

開始製品HEAD `3920f1642692c88a8d6870480bc3f98f71558d24`、観測main `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`。運用の指定4文書を同じ最新 `e0837f8245fad32541f1b0e8ecc0d616e13c6d06` から読み、run `cycle-20261124T110543Z` のleaseを通常pushで取得した。

PdM `pdm_content_pr31` が既存仕様で実装可能と確認し、PrM `root/coordinator` が以下を受け入れた。Engineer `engineer_content_pr31` は独立checkoutで実装、別担当 `qa_content_pr31` が固定候補を検証する。

- 教材確認・編集による確認失効・JSON入出力・非保存試し解き、およびPR11自身の理科生成元・単位/誤答タグ・旧履歴を保持する。
- 完了/途中終了/未回答/キャンセル/重複終了の回答件数と報告件数を、合成入力・設定と通知mockだけで確認する。
- 親モードは送信・キュー生成を抑止し本人保存領域を保つ。教材試行の回答・点数を保存しない。
- 必須suiteの和集合を保ち、通知・江戸・模試を含む生成列で初回保持と2回目不変を確認する。
- 別担当が最終固定候補の全必須suiteと768×1024の通常/親操作を検証する。

## 環境と権限

選択済み管理クラウドのreadyを確認した。独立worktreeと既存 `/workspace/yuika-study/.venv` の手動再利用は保存済み検証手順に従い、自動snapshot引き継ぎ成功とは扱わない。古い専用checkoutの再調査や再構築は反復しない。

実回答・教材写真・実設定を使わず、mainマージ・公開・デプロイ・実通知・Secrets/権限/設定変更を行わない。CEO新返答の実読・台帳取り込みは0。PR31外部マージは本運用の新承認ではない。製品draft3件を維持し、今回の更新先はPR11のみ。

## 実装・検証・次の仕事

固定候補は `feada5947b237310923f0aa1956487ac8af501af`。旧PR11と観測mainを親とするtopic上の統合で、テキスト競合なし。必須suiteは旧PR11の32本とmainの27本の和集合33本。教材確認HTML・fixture・仕様・既存CONTENT5試験とscience/prototype生成元は開始HEADとbyte一致。PR11の「今日の5問」を維持し、PR10の理由付き復習・日次実問数は移植していない。

生成列を通知・江戸・模試まで広げた初回検査は、江戸/模試/派生進捗に差分を検出してexit1。理科から江戸への複製にてこ専用処理が混入し、親境界が通知marker内に入ることを診断した。江戸は自身の既存HTMLをテンプレートに問題定義を更新し、親境界は通知block全体より前に置く。模試の差分はmarker順のみで、おすすめ表示の削除処理を持ち込む必要はなかった。

江戸のscience/prototypeアダプターは今後明示的な同期が必要。共有history/notification/design/parentの再埋込とは区別してREADME・生成元に明記した。修正後2回目の生成検査で初回全byte保持と2回目不変を確認。assertを弱めていない。

Engineerはcommit前の作業treeで通知7ケース/16mock報告、教材関連5本、てこ、prototype保存を検証し、各exit0と秒数を保存した。初回生成失敗と診断も[Engineer記録](https://github.com/naoyanakajima-cyber/yuika-study/blob/feada5947b237310923f0aa1956487ac8af501af/docs/content-pr31-compatibility.md)に残した。固定候補の全suiteと操作は別担当QAの実行結果を根拠とする。

独立教材probeは通常/親セッションの2新規browser contextでテキスト/画像の計4ケースを成功した。学習画面で実際の親bannerと抑止を確認してから教材確認室へ移動し、試行・終了・JSON再入力・編集による確認失効・再読込を検証した。教材確認室自身は親runtimeを持たずメモリ内のみで動作する。query付与だけを親隔離成功とは扱わず、本人保存の不変と学習画面へ戻った際の親セッション維持を確認した。保存書込・予期しないpageerrorは0。[教材操作結果](../evidence/2026-11-24-content-pr31/content-probe-result.json)。

教材probe初回はStorage監視用evaluateが関数を戻しPlaywrightに呼ばれてIllegal invocationとなる試験コードの問題で、製品操作前に停止した。戻り値をundefinedにする修正後の2回目で全条件を確認。通知probe初回はPR11のてこ終了ボタンを確認ダイアログ付きホーム移動と仮定した。既存契約は終了→結果表示で、キャンセル可能なのはホーム移動である。製品を変えず試験操作を正し、2回目で全8contextを確認した。初回ソース・結果・診断を保存し、assertは弱めていない。

通知の独立操作は通常/親×4画面、768×1024で未回答・キャンセル・途中終了・完了・重複・reloadを確認。通常で8報告をmock内だけで捕捉し、親は0件、本人localStorageはbyte不変。外部要求28件を遮断、予期しないPOST/pageerrorは0。[通知操作結果](../evidence/2026-11-24-content-pr31/report-probe-result.json)。統括も画像試行とテキスト確認後の合成PNG各1枚を目視したが、全画面の目視検証とは扱わない。

固定候補の独立 `bash scripts/check_all.sh` は初回33/33成功、exit0、367.568秒。開始/終了HEAD一致・status空。[全結果](../evidence/2026-11-24-content-pr31/summary.json)と[QA報告](../evidence/2026-11-24-content-pr31/QA.md)へ各suiteのexit/秒数を保存した。過去PR11の32suite成功は今回の成功に算入していない。

拡張生成列の初回/2回目byte一致に加え、独立の使い捨てコピーで江戸build()からの変更反映、未登録版変更の期待拒否、旧版保持とeditorial版追記、共有通知生成元の反映、親境界順を確認した。[生成契約結果](../evidence/2026-11-24-content-pr31/generator-contract-probe-result.json)。期待された拒否exit1は製品試験失敗ではない。

## 保存と次の仕事

既存PR11を同じ固定候補で更新し、製品3件の合成試用判断待ちを維持する。次回は最新main/PR/leaseを確認し、PR12自身のテーマ切替・学習状態・図の可読性と生成元を保つPR31最小互換同期をPdM/PrMで確認する。PR10/11固有機能を他branchへコピーしない。新規製品PRは増やさない。

実機Safari/iPad、本人試用・学習効果、実配送、公開画面は未確認。既存suiteは公開CDNを使い完全オフラインではない。外部CIは今回のクラウドQAと別に台帳/PRへ記録する。PR11と運用PR9のタスク添付は各1回呼び出したが応答せず待機を中断し、成功未確認として記録する。GitHub保存とは区別する。
