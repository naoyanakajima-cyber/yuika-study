# CONTENT-MVP 非同期JSON入力保全：独立QA

Reviewer/QA: qa_content_import_guard（実装者 engineer_content_import_guard とは別担当）。
対象: 62f34de238e9d1d62c796aac3a4b43418043d17f / codex/content-trial-20261114。
基点: f1e84a7b998dfbcd71c6692974015bdd08e1877e（既存draft PR11）。

対象HEADは統括・実装者のfreeze通知後、cleanを確認して検証を開始した。製品ファイルの編集・push・外部通知・設定変更は実施していない。
クラウドの既存venvを手動で有効化して利用した。自動snapshot引き継ぎ成功の証拠ではない。

## 独立試験

`probe.py` の17シナリオは初回実行でPASS。768×1024 Chromium、各シナリオ別の新規context、同梱合成fixtureのみ。File.textを遅延Promiseに差し替え、実際のfile inputへ合成Fileを設定し、実DOM編集・確認・JSONダウンロード・サンプル切替・取消を行った。

- 読込A待ち中の編集、確認、未確認JSON出力、別サンプル採用、案取消後の後着A拒否。操作直後と完了後のproposal全体・revision・確認・unsavedが一致。失効案内を確認。
- A/B同時待ち、A→B/B→A完了、旧Aの失敗を両順序で検証。旧結果がBのpending/入力/noticeへ干渉しない。
- 最新Bの読取失敗・構造不正・JSON構文不正・200KB超過後、Aが復活せず現在案と失敗noticeを保持。
- 破棄拒否、空files change、明示読込取消、案なしからの正常入力、同名ファイル2回入力。全問draft/confirmedRevision=nullへ戻り、正常入力後のworkflow見出しフォーカスを確認。
- 未確認案のダウンロードJSONのトップレベルschema項目一致、revision維持、全問draft/null、世代/pendingを含まないことを確認。

この独立probe範囲で、許可したローカルHTML GET以外の要求0、POST0、pageerror0、Storage API/cookie/history/IndexedDB/Cache/Service Workerへの監視対象操作0、window.name空を確認。全suite一般に外部要求0という意味ではない（既存suiteは公開CDN GETと模擬通知APIを使用）。

`normal-import-768x1024.png` と `cancel-import-768x1024.png` はfull-page画像を目視確認。案内・原本・転記・問題案・保存欄が一列で読み取れ、確認見出しのフォーカス枠と取消案内を確認した。

## 防御境界の独立確認

`static_boundaries.py` 初回PASS。

- 既存学習6HTMLのバイト列は基点と完全一致。問題ID・採点・選定・保存方式・親runtimeの変更なし。
- content-reviewのCSP、validateShape〜issuesの検証コード、同梱SAMPLES/ASSETSは完全一致。
- scripts/parent/embed.pyとtests/parent_mode.pyは固定SHA256値のみ変更。許可範囲は拡大していない。対象HTMLを独立レビューし、追加状態はメモリのみ、保存/API/外部script追加なしを確認。
- git archiveで作成した隔離コピーに合成の改変を加え、改変contentを生成器がAssertionErrorで拒否し、いずれのHTMLも書き換えないことを確認。
- 同じ隔離コピーでparent_modeの既存preflightが改変contentを拒否。別の隔離コピーでguardなしunknown.htmlを追加し、未知HTMLをpreflightが拒否。
- 意図した負例の非0は防御成功であり、製品試験の失敗/再試行ではない。

## 必須全suite

`bash scripts/check_all.sh` は初回1回、25/25 suitesすべてexit0、257秒、全体exit0。追加content_import_guardを含む。全suite名・exit・所要時間は `check-all.log` と `final-result.json` に保存。

2026-11-14T22:18:12Z、終了後HEADが62f34de238e9d1d62c796aac3a4b43418043d17fのまま・working tree cleanを再確認。独立probe・静的境界検査も初回成功で、失敗修復/再試行なし。

## 判定と限界

最終判定: PASS。必須25suite、独立17シナリオ、静的境界・memory-onlyレビューを完了し、blocking findingなし。既存draft PR11への統合を推奨する。製品採用はCEO判断待ちのままとする。
保存しない試し解き本体、OCR/実教材入力、学習アプリへの導入、Safari/WebKit/実iPad、OS実ファイル読込速度による自然発生競合、changeなしで閉じるネイティブ選択ダイアログは未検証/対象外。今回の制御Promiseは実OS速度の再現と区別する。
次の一手は、統括がlease/実行権を再確認し、この固定候補と証拠を既存draft PR11/正本台帳へ保存すること。新規PRは作成しない。mainへのmerge、公開、採用承認は今回実施していない。
