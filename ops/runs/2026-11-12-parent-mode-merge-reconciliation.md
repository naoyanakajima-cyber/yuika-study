# 保護者モードの外部マージとホーム表示差分の照合（2026-11-12）

苦手復習の「今日の5問」入口を整える変更が、別担当の作業でPR #24からmainへ取り込まれていた。今回の運用ではマージ・公開・実通知を実施せず、重複実装を避けるため状態を照合した。

- 正本4文書の取得commit: `59f1b9f6e3bab8fcd9a96c2e4e42f042ea3c76fa`。クラウドrunning/current確認、永続lease取得後にPdMと独立Reviewerを実起動。
- PR #24はAPIでclosed/merged、時刻 `2026-11-12T03:43:16Z`。最終HEAD `fc3ffa93dcecc2b64a21a4ac77dc03eec3aec3ca`、main `6ec616d5f24f552306219e3177db4f4041f84428`。両tree `d36f2a2e84d7aab4248f5c2046471bafcb77d54f` は一致。
- 前回独立QAの `314aa13` からの追加差分はindex.htmlの2行。日次ボタンの装飾と説明「前回の続きから5問」のみで、保存・通知・採点・選定・遷移処理に変更なし。`git diff --check`成功。
- PdM `pdm_merge24_reconcile` と独立Reviewer `qa_merge24_reconcile` が実コード差分を読み、対象範囲で阻害所見なしと判定。PrMは状態整理だけで終了する方針を確認。Engineer起動・製品コード変更・製品テスト・手動setupは0。
- 前回の20suite+追加16チェックは314aa13の証拠。PR作者のfc3ffa9での20suite×3回成功は作者報告であり、今回の実行成功とは数えない。
- [参照GitHub Pages workflow](https://github.com/naoyanakajima-cyber/yuika-study/actions/runs/43150073755)のbuild/report-build-status/deployは読み取りAPIでcompleted/success。今回そのworkflowとcommitの結合や配信HTML・公開URL上の表示は独立確認していない。Safari/WebKit/実iPadも未検証。

PR本文の「所有者承認済み」は別担当の報告として扱い、正本チャットのCEO返答を今回読んだことにはしない。新しいCEO判断取り込み0、権限拡張なし。D02の実資料/回答保存先は未決。現在の製品承認待ちは#10/#11/#12の3件、追加open製品draftは#22の1件。PR24を未マージ待ちに数えない。旧#4と運用#9/#13は上限の対象外。

次は保護者モード入口→今日の5問→次の復習→終了の具体的な合成試用フィードバックを確認する。「前回の続き」が前回単元・設定を指し、途中の問題そのものの再開ではない点が伝わるかを観察する。再現不具合と決めつけて修正せず、#10/mainの役割整理、教材追加#11、低優先のテーマ#12へつなぐ。新しい実装対象がないため同じテストを反復しない。

詳細は `../evidence/2026-11-12-parent-mode-merge/PdM.md`、`QA.md`、`observation.json`。PR24のタスクattachは応答せず中断、成功未確認。外部投稿は運用正本への必要なpushのみ。通常報告は朝夕のCEOチェックに集約する。
