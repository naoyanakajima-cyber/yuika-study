# CONTENT-MVP：教材案の読み込み競合を防ぐ

実行 cycle-20261114T220551Z、運用開始317916b、製品基点f1e84a7、観測main86514ed。クラウドrunning/connectedと現行観測を確認。lease通常push後、PdM→PrM→Engineer→独立QAの順で分担。新CEO返答なし。

問題案を読み込み中に編集/確認/出力等へ進んだ場合、後着した古い読み込みで作業が置き換わらないよう既存PR11を修正する。試し解き本体は未実装。世代保護だけを既存確認室へ適用し、JSON形式/CSP/学習記録/既存学習6HTMLは保持する。

初期checkpoint時点では実装/検証中。最終候補と受入結果は後続節へ記録する。新規PR枠を増やさず製品待ち10/11/12、追加既存22、旧4〜8/運用PRは別枠。実資料/回答/OCR/外部接続なし。公開/マージ/手動デプロイ/実通知/課金/Secrets/権限変更なし。

## 最終成果・受入

製品commit **62f34de238e9d1d62c796aac3a4b43418043d17f**、基点f1e84a7から7ファイル。問題案のJSON読み込み待ち中に、編集・個別確認・JSON保存・別サンプル採用・案取消をしても、古い読込結果で作業が置き換わらない。読込中表示と明示取消を提供し、新しい読込が失敗しても旧読込を復活させない。

[既存draft PR11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11)へ統括が通常fast-forward pushし、現在HEAD/draft/open/unmergedと説明本文のreadbackを照合した。[運用draft PR9](https://github.com/naoyanakajima-cyber/yuika-study/pull/9)も説明を更新・readback済み。製品は試用判断待ち、merge/公開を行っていない。既存PR9/11へのattachと一覧確認は空応答で、添付成功は未確認。新規PRなし。

## 実際の分担と検証

- PdM `pdm_content_trial_scope` が現行取込の問題と最小保全仕様を整理。PrM `root/coordinator` が範囲・既存PR・権限を確認して採択。
- Engineer `engineer_content_import_guard` が独立checkoutで実装、commit後freeze。修正前は合成File.text待ち→実DOM編集→後着結果採用＋破棄承諾で編集消失を再現、修正後に保持を確認。新回帰・既存確認・案内の3suite各初回成功。
- 独立QA `qa_content_import_guard` が同じ固定clean HEADで `bash scripts/check_all.sh` **25/25成功・初回終了0・257秒**。検証後も同じHEAD/cleanを2026-11-14T22:18:12Zに確認。blocking findingなし。
- QA独自の17分岐実DOM probeが初回成功。編集/確認/出力/サンプル/案取消、A/B両順・旧エラー、新取込の読取/形/構文/サイズ失敗、空files/明示取消、破棄拒否、同じファイル再入力を観測。768×1024 Chromiumで2画像も目視。
- 独立staticと隔離コピーの防御負例が初回成功。6学習HTML・CSP・validator/issues・同梱fixture不変。親検査2箇所は候補HTMLの固定SHA値だけ更新しmemory-onlyを再レビュー。未知HTMLと改変CONTENTを拒否、生成器は書込み前拒否。ガードを緩和していない。
- QA probeの範囲でstorage/history/cookie等監視書込み、非許可要求、POST、pageerror各0。全suiteには公開CDN GETと模擬通知があるため全体の外部要求0とは扱わない。実メール/Chat送信なし。

証拠は [ops/evidence/2026-11-14-content-import-guard](../evidence/2026-11-14-content-import-guard) に合成データのみ保存。Engineerのafter証拠はcommit前観測と明示されており、最終固定HEADの受入根拠はQAのfinal-result/check-all/probe/staticとする。

## 制限・試行・次の一手

Engineerの修正前再現harness初回はPlaywright evaluateの返値関数がPromise待ちとなった。void0終了に直し2回目で再現。同原因3回目なし。製品のfocused/QA全suite/probe/staticは各初回成功。意図した隔離負例の非0は防御成功として区別する。

既存検証済みvenvを手動再利用した。クラウド自動snapshot引継ぎやplatformの定時run完了成功は未検証。制御Promiseを使った合成競合であり、OS実ファイル速度の自然発生、nativeダイアログがchangeなしで閉じる取消、Safari/WebKit/実iPad、本人試用・学習効果は未検証。無change取消は明示取消を使う。

製品push直後のcheck-runsは0件で、外部Workers Builds成功はまだ確認していない。最終観測は台帳external_checks/PR証拠へ保存する。外部チェック再実行・公開・デプロイ・設定変更はしない。新しい権限/接続障害なし、既存D02実入力/保存先未決とPR22のWebKit依存制約は継続し、環境探索を繰り返さない。

次は「保存しない試し解き」の既存G/S契約全体を現行HEADへ照合し、35分内に実装と独立QAまで終えられる範囲をPdM→PrMで確認する。今回の部分保全を試し解き完成と報告しない。製品枠10/11/12、追加既存22、旧4〜8/運用PRは別枠。CEO回答を推測せず、D04方向性採用を本番承認へ広げない。通常報告は朝夕CEOチェックへ集約し、毎時通知なし。

最終外部観測：同じ製品HEADのWorkers Buildsは2026-11-14T22:19:22Zにcompleted/failure。原因未調査、手動再実行/デプロイ/設定変更なし。PR9/11本文とreadback、台帳へ反映済み。クラウド内独立25suite成功と外部failureを分けて保存した。

## 最終整合と終了

独立QAがmetadataも再照合しPASS。旧131runs・決定/権限/方針を保持、変更ticketはCONTENT-MVPのみ。最終完了記録時刻は2026-11-14T22:23:13.407558+00:00。統括がremote leaseと候補clean HEADを再確認し、この最終保存commitでleaseをnullへ戻す。通常push後にremote HEAD/台帳解除をreadback確認する。platformの自動化完了状態とは区別する。
