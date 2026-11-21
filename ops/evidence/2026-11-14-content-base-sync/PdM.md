# PdM: CONTENT-MVP / 既存 draft PR #11 の基点互換性修正

2026-11-14 UTC。read-only調査。製品編集・テスト・pushなし。
参照: docs/agent-team.md、ops/AGENTS.md、ops/board.json の independent_followup、ops/runs/2026-11-14-content-try-contract.md、ops/evidence/2026-11-14-improvement-gaps/Engineer.md、固定mainのAGENTS.md/check_all.sh/serve.py/cloud_preview.py、固定PR11のcontent-specと旧基点差分。

## 推奨と学習上の価値

既存PR11の履歴を保持し、独立topic checkoutへ現mainを取り込む互換性修正を推奨する。旧教材確認画面の「原本・転記・問題案を区別し、修正して個別確認し、確認済みJSONを出す」価値を、現在の学習アプリの入口・共通資産・安全なプレビューと共存させる。試し解きという新しい学習体験は追加しない。

旧基点は edad8065c1f2b726e61c5cf405f8d9ff6d807480、PR11 HEADは 3d2ed2f9a62673d2fb086a360ae841096f35b63e、取り込み候補mainは 86514eda054a5a2e09204df3a0668e40624c16de。初期基点を永久固定しない運用方針に従い、両HEADを保持するmerge commitで基点を進める。mainへmergeする操作ではない。PrMがこのtopic内統合を今回の既存修正範囲として明示確認する。

修正後、同じdraft PR11のbaseをmainに変更する案を推奨する。旧baseのままではmainの既採用成果までPR差分に混ざり、教材確認の審査範囲を誤認しやすい。代償は現main全体との回帰QAと既存レビューの再照合が必要な点。base変更はQA後、現remote HEAD/lease再確認後に親が行い、旧baseと新base、統合commit、レビュー範囲を保存する。新PR・force/rebase・履歴置換は不要。

## 受入条件 U1–U6

- U1 履歴/差分: 両固定HEADが候補commitの祖先。mainとの差分が下記allowlist内に収まり、現mainの採用成果を落とさない。元PR11の追加8ファイルは原則blob一致。READMEの教材確認説明を保持し、main側説明も保持する。
- U2 配信互換性: serve.pyはmainの全既存入口、mock-focus-review.html、assets/design.css/design.js/progress.jsに既存content-review.htmlだけを追加した厳密allowlist。127.0.0.1 bind、CSP connect-src/form-action/object-src、no-store、HEAD 405を維持。任意ファイル・ディレクトリ・private pathsは配信不可。
- U3 教材確認体験: 既存C1–C11と案内機能を維持。合成text/image、未解決箇所保留、編集revision増加/全確認失効、読込confirmedの失効、個別確認/取消、draftと確認済みJSON出力/再入力、keyboard/focus、768×1024での利用を既存2suiteで再確認する。新しい採点・試し解き状態は存在しない。
- U4 現main保全: 現mainの教材HTML、assets、親確認/保存隔離、prototype/history検証、採点・選定・通知コード・問題ID/版/キーは候補とblob一致。既存CONTENT画面はメモリ内の案だけを保持し、既存学習記録の読み書き・自動教材反映なし。共通デザインへの刷新や親確認機能の追加をこの修正へ混ぜない。
- U5 実行証拠: 現main AGENTS.mdに従い候補確定commitで bash scripts/check_all.sh 全suiteを実行し、HEAD/dirty state/個別exit/time/全体結果を保存する。main runnerの既存22suiteは削除/緩和せず、既存content_review.py/content_guidance.pyも必須実行へ追加する。配信allowlistの両側入口・資産、未許可パス、CSP/POST遮断を直接確認。ブラウザーはfresh context/合成データ/768×1024、外部要求・実通知POST・CONTENT経由storage書込0。独立QAが対象revisionを自ら照合/実行する。Safari/実iPad/本人試用/公開確認は未検証と明記。
- U6 受渡し: remote HEAD/lease一致を親が確認して同じbranchへ通常pushし、同じPR11をdraft維持。main向けdiff/競合状態を再確認してbase/本文を更新・読戻し。方向性採用D04は維持、merge/deploy未承認とceo_waitを保持する。同じ原因の試行上限はユーザー/運用の2回を適用し、現mainのローカル3回ルールを使って増やさない。失敗を診断せず再試行しない。

## main比の許可ファイルと編集境界

元PRの11ファイル:
1. README.md — main文面を保ち、既存教材確認説明を統合。
2. content-review.html — PR11 HEADとblob一致。
3. docs/codex-cloud.md — main文面を保ち、厳密allowlistにcontent入口が加わる事実へ最小修正。旧「5つだけ」の文をそのまま現在の配信説明にしない。
4. docs/product/content-spec.md — PR11 HEADとblob一致（旧調査時点の記述を現在mainの事実と誤認しない）。
5–8. docs/product/fixtures/synthetic-content.json、synthetic-image-content.json、synthetic-source.svg、synthetic-source.txt — PR11 HEADとblob一致。
9. scripts/cloud/serve.py — mainを基礎にcontent-review.htmlをallowlistへ足すだけ。
10–11. tests/content_review.py、tests/content_guidance.py — PR11 HEADとblob一致。

補助の許可候補2ファイル（PrMが確認）:
12. scripts/check_all.sh — 上記既存CONTENT 2suiteを追加するだけ。旧22suite/seed/集計/失敗伝播を保持。
13. tests/cloud_preview.py — 現main検証を維持しつつ、両側の全許可入口/資産とcontent入口のCSP、未許可パスの限定配信を確認する最小回帰追加。既存assert弱化なし。

13ファイル以外のmain比差分が必要なら、原因と最小対応をPrMへ返す。運用報告/boardは運用branch上で親が別管理する。

## 静的照合と非対象

git merge-base --is-ancestorで両HEAD保持を確認。git diff --name-status main..candidateで範囲確認。元PRの追加8ファイルをgit blob SHAで照合。許可ファイル以外はmain treeと一致を確認し、README/cloud文書は両側意味保存を目視確認。serve.pyのmain比差分はallowlist 1項目追加に限定。runnerは2suite追加のみ、cloud-previewの追加は既存assertを残す。端点比較のD表示を実削除と取り違えない。

新試し解き/新採点、OCR/自動生成、実教材入力・私的資料・実回答、D02接続/保管先、教材導入、UI刷新、保存方式/通知変更、実通知、Secrets/課金/共有範囲、main merge/公開、旧PRのcloseや新製品PRは対象外。PR固有コードが無変更でも基点が大きく進むので、過去PR11の5suite成功を今回の現main回帰成功に転用しない。
