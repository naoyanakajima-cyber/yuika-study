# Engineer：確認済み合成案を保存せず試し解き

実装者 engineer_content_trial_delivery。基点62f34de238e9d1d62c796aac3a4b43418043d17f、候補8e2111b4e9c535c4632976a6f384992e839d1329。独立checkout /workspace/yuika-content-trial-delivery-20261114、branch codex/content-trial-delivery-20261114。7ファイルをcommitしclean freeze、以後変更停止。

PdM /tmp/yuika-cycle23-pdm.md をPrM採択した全G01〜G13/S01〜S13契約の実装候補。content-review.htmlの合成案のみ、既存PR11内の変更。

## 実装

- 全問の現revision確認・既存shape/issues/source条件・text正規化後の候補長さ・pending importを開始前と実行時に再検査。原因と該当欄へ案内、閉じたdetails内の欄もfocus可能。
- proposalと別のメモリsnapshot/session/index/状態epoch/現在回答/ヒント/結果を使用。NFKC+trim完全一致とUTF-16生/正規化後200上限、choice整数option indexと生文字列一致。別表記・読みの推定追加なし。
- 試し解き中は確認画面全体をhidden/inertとし、編集/確認/案切替/取消/JSON入出力を実行時にも拒否。JSON取込の既存世代保護を再利用。
- 操作closureをsession/question/index/epochへ結合し旧操作を無効化。採点/次問前に案全体との一致と全確認を再照合。不整合で試行終了・消去。
- 採点前に正答候補・解説をDOMへ作らず、ヒントは明示操作のみ。採点後は入力固定、結果/登録候補/解説を表示。点数・履歴・習熟評価なし。
- 次問で現在回答/結果/ヒントを消去、終了でsnapshot/session/表示DOM含め消去。試行DOM再構築はMutationObserverと要素identity照合で停止消去、既存render()も試行を停止。内部drawTrialは現在tokenを要求する。
- beforeunloadはunsavedまたはtrialで警告。pagehide/persisted pageshowで試行消去。実文書が残るbeforeunload取消では消去しない。
- CSP、validator/issues、6学習HTML、案schema、既存学習のID/採点/保存/親runtimeは変更なし。親検査2箇所は固定hash値のみ整合。最終HTML SHA256 7566a53868976bdfa8feb279c87cc6b4bccaba8fe7777545fef5d4e21ca650a7。
- README、製品用content-try-spec（実装候補・独立QA待ちとして記載）、tests/content_trial.py、check_all登録追加。必須suiteは26。

## Engineerの実測

実資料なし。同梱合成fixture、fresh Chromium 768×1024、loopback。

1. tests/content_trial.py 初回PASS。G01〜G13のliteral oracleとUTF-16/非文字列/choice境界、2問の実DOM出題・ヒント・採点・次問・終了、案/unsaved不変、旧closure拒否、JSON再入力確認失効、合成pagehide/persisted pageshow、DOM再構築停止など。
2. tests/content_review.py、tests/content_guidance.py、tests/content_import_guard.py 各初回PASS。既存C1〜C11/案内/非同期競合保全を確認。
3. 読取りで正規化過長alias/readingsの案内先を該当欄へ改善し、detailsを開くfocusを追加。新trial suiteとguidanceを最終差分で再実行し各PASS。失敗の反復ではなく追加変更に対応する再検証。
4. git diff --check PASS、6学習HTMLの基点バイト一致、hash2箇所一致。commit後git status --short空。

試験失敗・ハーネス修正・同原因再試行は0。全check_allはEngineerでは実行しておらず、freezeした同じHEADを独立QAへ引き渡す。

証拠 /tmp/yuika-cycle23-engineer/{trial-attempt1.log,trial-final.log,content-review.log,content-guidance.log,content-guidance-final.log,import-guard.log}。試験コードは候補commitのtests/content_trial.py。

## 制限と次の手順

現時点の実装候補を、独立QA済み/CEO採用済みと呼ばない。合成page lifecycleイベントは実BFCacheヒットや実機iPad/Safariでの確認とは別。実児童の学習効果・実教材・OCR・既存アプリへの導入は対象外。
既存検証済みvenvは統括が手動symlink再利用した。自動snapshot引継ぎ成功ではない。

QAが固定HEADの26suiteと独立G/S/state/storage/network/境界を確認し、統括が実行権を再確認して必要なpush/既存draft PR/台帳保存を行う。Engineerはpush、ops編集、外部投稿、merge、公開/デプロイ、実通知、設定・権限・Secrets変更をしていない。

## 独立QA指摘への最小修正（最終候補）

最終候補 **ee51e68d7e1eeb21bd0e959ec58166a869947d0a**、clean freeze。初期8e2111bの独立全suite終了通知を統括から受けるまで製品を編集せず、終了後の明示委任で追加commitした。

初期候補は全26suite成功でも、正規化後に長すぎるalias/readings等で開始不可の際、理由表示とdisabled開始buttonしかなく、利用者が該当欄へ移動する導線がなかった。独立QAが実UIで再現した契約未達として受け入れ、初期候補の受入成功とは扱わない。

最小修正は `#trial-repair`「確認・修正する箇所へ」の追加。現在trialReadyの原因があるときだけ表示し、click時にも原因/targetを再取得する。未確認ならconfirm、過長alias/readingsならdetailsを開いて当該欄、pending importならfile inputへ移動。試行中は実行時に拒否する。新しい採点・状態ルールは増やさない。

新回帰に実button click/Enterによる上記4経路、開始可能時の非表示、試行中の呼出拒否を追加し、`python tests/content_trial.py` は修正後初回PASS。`git diff --check` とhash2箇所整合もPASS。製品仕様冒頭を「独立QAの結果は運用台帳・PRへ別途記録。利用者の製品採用・公開承認なし」へ変更し、先行文書成果と区別。

最終HTML SHA256: fea62d048857059b8016f3a36061795bacb18acf160d1bdc0c9997d277abd001。追加証拠 `trial-nav-final.log`。Engineer実行の失敗は0だが、独立QAによる製品指摘は1件・修正1回として区別する。最終ee51e68の独立全26suiteと導線再検証はQAへ再引渡し済み、未実施の結果はここで成功としない。以後製品変更なし、push/ops編集なし。
