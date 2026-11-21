# CONTENT-MVP：確認済み合成教材の保存しない試し解き

実行 cycle-20261114T230830Z。運用開始4207084、製品基点62f34de、観測main86514ed。クラウドrunning/connectedを確認し、永続lease通常push後にPdM→PrM→Engineer→独立QAを実際に分担。

確認した案を出題順に解き、許容表記/選択肢/ヒント/解説を教材導入前に点検する既存PR11内の改善。全G/S契約を維持し、個人の理解度測定や既存学習記録への接続は行わない。新規PR枠なし、D02実接続/保存先未決。

このcheckpoint時点は実装・検証中。固定候補の独立検証と最終保存結果は後続節へ記録する。

## 最終成果

[既存draft PR11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11)へ **ee51e68d7e1eeb21bd0e959ec58166a869947d0a** を通常fast-forward pushした（基点62f34deから2commit・7ファイル）。合成原本・転記・問題案を確認し、全問を明示確認後に出題順で試し解きできる。短答/選択、明示ヒント、採点後の登録正答・解説、次問・終了を提供し、教材を学習へ導入する前に使い勝手を点検する。児童の理解度・努力を判定しない。

回答は現在問のメモリ内だけで、次問・終了・離脱で消去。案JSON・revision・全確認・unsavedは変えず、既存学習記録への保存や教材導入もしない。試行中の編集・JSON入出力は可視性と実行時の両方で拒否。古いsession/問題/状態世代の操作を無効化し、案不整合・試行DOM再構築時は停止・消去する。開始不可の原因から、確認・修正する欄へ移動できる。

## 実際の分担・検証

PdM `pdm_content_trial_delivery` が既存全G01〜G13/S01〜S13と現行HEADを照合。PrM `root/coordinator` が既存PR11内の改善として採択。Engineer `engineer_content_trial_delivery` が独立checkoutで実装・focused検証・commit freeze。独立QA `qa_content_trial_delivery` が別担当として固定候補の機能・防御・全体回帰を実行した。

初回 **8e2111b** は必須26/26・終了0・296秒、独立65ケースと静的境界も成功したが、正規化後200文字超の候補で開始buttonがdisabledとなり、原因表示から修正欄へ移動できないUX不具合を追加の実UIで発見した。既存「次の作業へ」はJSON保管欄へ案内していた。PrMが契約未達として差戻し、全試験終了と証拠退避を待ってからEngineerへ修正を委任した。テスト中の製品編集なし。

最終 **ee51e68** は固定clean HEADで必須 `bash scripts/check_all.sh` **26/26・終了0・256秒**。最終候補の全suite・独立65ケース・静的/隔離負例・修正導線検査は各初回成功。2026-11-14T23:29:10.778434+00:00にHEAD/cleanを再確認し、blocking0でdraft/CEO判断待ちへ受入可能とした。

65ケースはNFKC/UTF-16上限・選択identity、全問確認/未解決/再入力/取込pendingの開始拒否、入力・ヒント・採点・次問・終了、旧操作、案/確認/unsaved不変、JSON非混入、離脱取消と実reload、合成persisted、文字列安全表示を含む。768×1024の実DOM・キーボード・フォーカスとAX除外を検証。追加修正は正答/別表記/読みの各過長条件から実Enter操作で該当欄へ移動し、閉じたdetailsも開くことを確認。未確認時のconfirm移動、正常時の修正button非表示も確認した。

静的比較で6既存学習HTML・CSP・validator/issues・同梱fixture・親runtimeを維持。親検査/生成器の2固定hashは候補HTMLへ整合した値だけを変更し、独立レビュー。隔離コピーで未知HTML/改変CONTENTを拒否し、生成器は書込み前拒否した。QA probe監視範囲でstorage/history等書込み・非許可要求・POST・pageerror・console各0。全suiteは公開JSのGETとmock通知を含むため、全体の外部要求0とは呼ばない。

## 証拠・試行と未検証事項

[証拠一式](../evidence/2026-11-14-content-trial-delivery)にPdM/PrM/Engineer/QA、ログ、スクリプト、合成スクリーンショット、結果JSON、SHA256を保存。QAの `attempt1/` は初回8eと差戻し・ハーネス診断、直下は最終eeの証拠。初回probeはevaluateの関数返値をPlaywrightが実行してPromise待ちとなり、void0へ修正した2回目で成功。製品不具合と区別し、同原因の無診断3回目なし。最終候補の再検証は修正commitに対するもの。

最終採点直後の `graded-768x1024.png` はblankで、視覚合格根拠にしない。DOMのG状態・回答値・結果/focusは成功していたが、画像blankの原因は特定していない。同じHEADの新contextで実サンプル確認→入力→採点を行い、描画待ち後の `graded-visual-768x1024.png` では回答・結果・正答/読み・解説・終了操作を目視確認した。元画像も保持し、全描画タイミングを保証しない。

合成pagehide/persisted pageshowと実reload/取消を実行した。実BFCacheヒット、WebKit/Safari/実iPad、本人試用、学習効果、実教材/OCR/既存アプリへの導入は未検証/対象外。既存venvは検証済み手順の手動再利用で、自動snapshot引継ぎ成功・platformの定時実行完了成功とは扱わない。外部Workers Buildsは別途現在HEADで観測し、クラウド内QAと分けて保存する。手動再実行/デプロイなし。

## 次の仕事と権限

試し解きの合成試用を朝夕CEOチェックへ提示する。次の独立作業は、既存THEME-MVP PR12（57171ad、base codex/cloud-automatic-bootstrap/edad806）と現在main86514edの互換性を読み取り照合し、必要差分だけをPdM/PrMで範囲確認する。不具合を未再現のまま断定せず、新規製品PRを増やさない。

製品待ち10/11/12・追加既存22、旧4〜8/運用9/13別枠を維持。新CEO返答取り込み0、D04方向性採用を試し解き採用や本番承認へ拡張しない。D02実入力/保存先は未決。新規接続・権限障害なし、既存PR22 WebKit依存の再調査なし。本番マージ/公開/実メール・Chat/課金/Secrets/権限/共有変更なし。既存PR9/11 attachと一覧は空応答で成功未確認、新規PRなし。通常成果は朝夕CEOチェック、毎時通知なし。

## 外部状態の照合

PR11現在HEAD ee51e68 の Workers Builds: yuika-study は2026-11-14T23:30:31Zにfailure（https://github.com/naoyanakajima-cyber/yuika-study/runs/132627134545）。原因未調査、手動再実行/デプロイなし。クラウド内独立QA成功と区別した。PR9/11の説明を更新し、読戻しで本文一致・draft/open/未マージ、PR11 HEAD ee51e68を確認。観測時点を含むpr-readback.jsonに保存した。

## 最終保存

独立メタデータレビュー qa_content_trial_delivery は2026-11-14T23:36:18.484746+00:00にPASS、blocking0。正本仕様の古い未検証表記1点を修正し再読確認。旧132runs・権限・CEO判断を保持し、今回1runを追加した。メタデータ報告と独立PR読戻し比較を証拠へ保存。

保存時刻 2026-11-14T23:36:58.546274+00:00。この保存commitでleaseをnullに戻す。製品最終ee51e68は変更せず、既存draft PR11と運用PR9に成果を保存。新規PRなし。通常の成果・外部check失敗・未検証事項は朝夕CEOチェックに集約し、毎時通知はNO_UPDATE。
