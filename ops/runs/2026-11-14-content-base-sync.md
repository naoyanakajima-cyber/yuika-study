# CONTENT-MVP：教材確認を現mainと両立させる既存PR修正

2026-11-15 JST（ファイル名はUTC）。run `cycle-20261114T170613Z`。
managed cloud running/connected/currentを確認し、正本4文書を同じ `ba433d7bd8772f9d462878142d07e5033a6729c0` から読んだ。leaseは通常pushで取得。ローカルPCへの代替なし。

## 学習上の価値と変更

原本・転記・問題案を見比べて修正・個別確認・JSON出力する既存教材確認画面を、現在の学習画面と共通アセットを保ったまま検証できるようにする。
既存draft [PR11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11) の履歴を保持し、固定mainをtopicへ統合する。mainへのマージではない。
新しい試し解き採点・OCR・私的資料入力・教材導入は追加しない。前回のCONTENT-TRY-SPECは要件文書のまま。

旧PR11 HEAD `3d2ed2f9a62673d2fb086a360ae841096f35b63e`、旧base `codex/cloud-automatic-bootstrap` / `edad8065c1f2b726e61c5cf405f8d9ff6d807480`。
現main `86514eda054a5a2e09204df3a0668e40624c16de`。
候補 `2f5cb14fd8ab3711752e725536288da47bf0d90e` は旧PR11と現mainの順で両parentを保持。
serve.pyはmainにcontent-review.htmlの許可1行だけを追加し、README/配信文書を整合。
既存22suiteを維持して既存CONTENT 2suiteを必須runnerへ追加、限定配信の回帰確認を追加した。
初期候補のmainとの差分は当初承認13パスのみ。PR11固有の追加8blobは完全一致。他の現mainの製品blobも一致。

## 分担と準備

PdM `pdm_content_base_scope` がU1–U6と13ファイルの境界を提案しPrMが確認。
Engineer `engineer_content_base_sync` が独立checkout `/workspace/yuika-content-base-20261114` で実装しcommit。子はpushなし。
独立Reviewer/QA `qa_content_base_sync` が候補を直接レビューして全24suiteを担当。
依存は既存の検証済みvenvを無追跡symlinkで手動再利用。requirements-dev.txtのSHA256一致とactivate/import成功を確認。自動snapshot引継ぎ成功とは扱わない。

## 証拠と検証境界

- [PdM受入条件](../evidence/2026-11-14-content-base-sync/PdM.md)
- [Engineer](../evidence/2026-11-14-content-base-sync/Engineer.md) / [対象テスト](../evidence/2026-11-14-content-base-sync/engineer-test.log)

Engineerの限定配信テストは候補commitで1回、終了0、3.190秒。syntax/diff検査成功。
独立QAの結果と最終受渡しは以下に記録する。過去PR11テストを今回の成功には算入しない。
全suite中のbrowser.pyは公開JSの読取りがあるため全体の外部要求0とはしない。実通知はmock、教材確認画面の通信/storage計測を別に記録する。
Chromiumの合成検証であり、実機iPad/Safari・CEO本人試用・公開環境確認ではない。

## 権限と次の一手

D04方向性採用は維持。新CEO判断取込み0、D02実資料接続/保存先未決。製品待ちは#10/#11/#12の3件と別途既存draft#22を明示し、新しい待ち枠を作らない。旧#4〜#8・運用PRは別枠。
本番merge・公開/デプロイ・実通知・課金・Secrets/権限/共有変更なし。旧停止中の自律更新は再開しない。
次はこの候補の合成教材確認の使い勝手評価。依存しない改善候補は、既存REV-MVPの日次件数表示と実出題数のずれを、次回PdM/PrM確認後に合成条件で再現し、確認できた不具合だけ既存PR内で扱う。新しい試し解き機能の実装は今回の修正へ混ぜない。
通常の成果/判断待ちは朝夕CEOチェックへまとめる。CEO判断はこの運用を設定した元チャットでチケットID付きの返答を実際に読めた担当が台帳へ反映するまで承認扱いにしない。

## 独立QAで発見した統合時の検査不整合

初回24suiteはparent_mode.pyだけ失敗し23/24、終了1。全root HTMLに親runtimeのmarkerを要求する旧検査が、保存をしないCONTENT画面でIndexErrorとなった。ランダム失敗ではなく対象分類の不整合。
PdM追加判断をPrMが確認し、tests/parent_mode.pyとscripts/parent/embed.pyを追加した15ファイルへ範囲を限定。
教材確認画面は元PR11のSHA256同一性を必須にして例外化し、既存6学習画面と未知HTMLの保護検査は維持する。生成器も同一性をHTML書込み前に確認し、教材確認画面だけを維持する。将来のCONTENT編集時はこの例外の再レビューが必要。
修正commitは `f1e84a7b998dfbcd71c6692974015bdd08e1877e`。元PR11の8追加blobと既存mainの製品HTML/runtimeは変更なし。

初回検証の開始HEADは2f5cb14、終了HEADはf1e84a7。統括の待機指示が届く前にEngineerが修正commitしたため、初回は固定HEADの受入成功とは扱わない。残り実行中のresponsive/contentテストとHTMLには変更がなかったが、その事実で初回の結果を最終候補の証拠に転用しない。
初回結果は診断記録として保存し、その後全製品編集を停止。独立QAは固定された修正HEADで生成器の隔離コピー確認・負例検査と2回目の全24suiteを担当する。同原因の3回目は行わない。

## 最終受入と受渡し

[独立QA](../evidence/2026-11-14-content-base-sync/QA.md)は最終f1e84a7をU1–U5受入。固定clean HEADの2回目全24suiteが24/24、終了0、291秒（wall291.619秒）、2026-11-14T17:17:17.175128〜17:22:08.794453 UTC。実行前後HEAD/clean同一。再試験なし。
[初回診断](../evidence/2026-11-14-content-base-sync/qa-attempt1.log)と[最終実行ログ](../evidence/2026-11-14-content-base-sync/qa-attempt2.log)、[追加probe](../evidence/2026-11-14-content-base-sync/qa-probe.json)、[SHA256](../evidence/2026-11-14-content-base-sync/sha256.json)を保存。

統括がremote leaseと現HEADを再確認し通常push。PR11をmain基点へ更新し、open/draft、HEAD=f1e84a7、base=86514ed、changed_files=15、本文一致、未mergedを読戻し確認した。GitHub raw APIはmergeable=true / mergeable_state=unstable。更新直後の正規化API falseと区別し、競合解消をraw結果と祖先関係で照合した。これはmerge実行の承認ではない。
既存外部Workers Builds checkはin_progress、combined statusesはpending/配列空という観測。外部check結果や公開確認をローカル24suite成功と混同しない。deploy命令・設定変更は行っていない。
既存PR11/9へattachを呼び出したが応答が空で、この呼出の成功確認はできなかった。新規PRなし。
