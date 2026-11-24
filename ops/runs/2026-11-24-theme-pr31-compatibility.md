# テーマ切替とPR31の互換同期

## 目的と実行範囲

既存draft [PR12](https://github.com/naoyanakajima-cyber/yuika-study/pull/12) の標準／鎌倉テーマ、回答途中の状態・履歴・設定復元、模式図の画面／印刷可読性を保持し、外部PR31の終了時学習報告と両立させる。新しいテーマやPR10の復習・日次件数、PR11の教材入力機能は追加しない。

開始製品HEAD `00c4ccb3b501223366a5f0a736567231ea9b8043`、観測main `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`。運用の指定4文書を同じ最新 `1f04c8fa1f4c256dd87997fdc3032300ed5deea1` から読み、run `cycle-20261124T120549Z` のleaseを通常pushで取得した。

PdM `pdm_theme_pr31` が既存仕様で実装可能と確認し、PrM `root/coordinator` が受入条件を確定。Engineer `engineer_theme_pr31` が独立checkoutを担当し、別担当 `qa_theme_pr31` が固定候補を独立検証する。

- テーマ操作は問題・入力・ヒント・採点・履歴・報告を変えず、保存設定と画面／印刷の文字可読性を維持する。
- 完了・途中終了・未回答・移動キャンセル・重複終了を合成入力とmock通知で確認する。親モードは送信・キュー生成を抑止し本人localStorageを保持する。
- PR12自身の理科生成元、てこ進行・再開、unit/tag、旧履歴互換を保持する。
- 通知・江戸・模試まで含む実生成列で初回成果物保持と2回目不変を確認する。必須検証は旧PR12の28本とmainの27本の和集合29本。
- 固定候補の全必須suiteと768×1024の通常／親操作を別担当が検証する。

## 環境と制限

選択済み管理クラウドのreadyを確認。独立worktreeと既存venvの手動再利用で進め、自動snapshot引き継ぎ成功とは扱わない。個人の回答・教材写真・メール／Drive情報は使用していない。

本番merge・公開・deploy・実通知・課金・Secrets／権限／共有設定変更は対象外。CEO新返答の実読・台帳取り込みは0。PR31の外部mergeはこの運用の新承認ではない。製品draft3件を維持し、更新先は既存PR12のみ。

## 実装・検証結果

固定候補は `df7af2a205f44e8c76b50e96728685efcc7e57d8`。開始PR12と観測mainを親とするtopic上の統合で、テキスト競合なし。鎌倉テーマのCSS・操作部・実行処理、仕様・既存theme test、理科・履歴・prototypeの生成元と6教材の問題定義を静的照合して保持を確認した。

生成列を通知・江戸・模試まで広げた初回検査は、江戸・模試・派生進捗の差分を検出して失敗した。江戸への理科てこ処理の混入、通知marker内への親境界挿入に加え、PR12固有の鎌倉テーマCSS・操作部・実行処理が模試へ複製されていた。江戸は自身の既存HTMLを基に問題定義を更新し、親境界は通知block全体の前へ挿入する。模試生成では鎌倉専用の3ブロックを各1箇所だけ除外し、構造が変わればassertで停止する。

診断後2回目の生成検査で初回全byte保持と2回目不変を確認。README説明追加後の時刻付き再検査も成功。Engineerの検証はcommit前の作業treeに対する事前確認で、[実装記録](https://github.com/naoyanakajima-cyber/yuika-study/blob/df7af2a205f44e8c76b50e96728685efcc7e57d8/docs/theme-pr31-compatibility.md)に初回失敗・修正・各exit/秒数を保存した。江戸のscience/prototypeアダプター更新は今後明示的な同期が必要で、共有history/notification/design/parent再埋込とは区別する。

独立QAは別のclean checkoutで固定候補を実行した。拡張12ステップ生成列の初回／2回目の全tracked byte一致、江戸の問題元更新、未登録版変更の期待拒否、旧版保持とeditorial版追記、共有通知生成元の伝播、親境界の順序を確認した。[生成契約結果](../evidence/2026-11-24-theme-pr31/generator-contract-probe-result.json)。期待された拒否exit1は不具合による試験失敗ではない。

768×1024の独立テーマ操作は通常／親で入力・ヒント・採点・結果・reloadを確認し、切替による学習状態や記録の変化、テーマ由来enqueue、予期しないPOSTを観測しなかった。両テーマとscreen/printの図ラベルcontrastは6.26572:1。理科てこの図にテーマ値の影響はなかった。[テーマ結果](../evidence/2026-11-24-theme-pr31/probe-result.json)。別の理科操作で通常／親のunit/tag付き回答、実JSON書出し・取込・reload、項目なし旧形式、不正値／未知項目の拒否と元記録保持を確認した。[理科結果](../evidence/2026-11-24-theme-pr31/science-probe-result.json)。

通知の独立操作は通常／親×4画面の8新規contextで、未回答・移動キャンセル・途中終了・完了・重複・reloadを検証。通常の8報告をmock内で捕捉し、親は報告／キュー0、本人localStorage不変を確認した。[通知結果](../evidence/2026-11-24-theme-pr31/report-probe-result.json)。追加probeはすべて初回成功。QAが4合成画像を実見し、統括も親モード入力途中と模式図の2画像を実見した。全画面や実機の目視検証ではない。

固定候補の独立 `bash scripts/check_all.sh` は初回29/29成功、exit0、368.253秒。実行12:11:49–12:17:57 UTC、開始／終了HEAD一致・status空。[全suite結果](../evidence/2026-11-24-theme-pr31/summary.json)と[独立QA](../evidence/2026-11-24-theme-pr31/QA.md)へ各exit・秒数を保存した。追加probeを含めQAの製品失敗・ハーネス失敗は0。過去の28suite成功は今回へ算入していない。

## 次の仕事

PR12の互換同期を既存draftへ保存し、3製品の合成試用判断待ちを維持する。具体的な新差分・再現不具合・CEO試用所見があれば既存PRの範囲を確認し、なければ同じ実装やQAを反復しない。mainの生成元未修正、実機Safari/iPad・本人の好み・学習効果・公開動作の未検証は別に残す。

PR12と運用PR9のタスク添付は各1回呼び出したが応答せず待機を中断し、成功未確認。GitHubへの成果保存とは区別する。外部CIの結果はクラウドQAと別に台帳・PR本文へ記録する。

外部 `Workers Builds: yuika-study` は同HEADでfailure、2026-11-24 12:20:11 UTC完了を観測（[check](https://github.com/naoyanakajima-cyber/yuika-study/runs/138439612563)）。原因は今回未調査。クラウド内29/29成功と区別し、再実行・deploy・設定変更は行っていない。
