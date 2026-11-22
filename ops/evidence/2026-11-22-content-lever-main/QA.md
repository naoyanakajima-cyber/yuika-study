# 独立Reviewer/QA — CONTENTと現mainてこ教材の互換性

対象固定候補 `ee228ca0a1865d0a56f4302cd9342a4f66738561`。
両親は既存PR11 `1678519f916471ba6e38044855de240bd6c4a807` と現main `58f8b53b4da69806d15a126fc525b65893a0bf35`。
実装者とは別のqa_content_leverが、独立detached checkout `/workspace/yuika-content-lever-qa` で検査した。

## 環境と試行

既存 `/workspace/yuika-study/.venv` を手動でsymlink再利用。依存定義SHA256一致と `pip check` 成功を確認した。新しい自動Install/Startやsnapshot継承成功とは扱わない。追跡ファイルは開始時差分なし、手動 `.venv` symlinkのみ未追跡。setup・OS・依存・設定の変更なし。全suite、独立static/probeは各初回実行。過去の65/15独立probeは再実行・今回件数への加算をしていない。

## 差分と互換性

- mainの共有接点を除く85パスはGit blobが候補と一致。全学習HTML、てこ28問、既存ID/正答/採点/キー/履歴アーカイブ、parent runtime、通知コード、教材生成・進捗を保持。
- 旧CONTENTの16パスはGit blobが一致。確認室HTML、合成fixture6、CONTENT仕様4、専用suite5を保持。旧source・新三角形・試し解き契約を変更していない。
- mainとの差は既存CONTENT23パスのみ。共有7パス中、check_all以外6パスは旧PR11と一致。check_allはmainの26suite順序を保持して既存content5suiteを追加した31suite。
- メモリ内確認室の固定SHA256 `b978ea0ebd725cbe0b0b45275ad19d7be4ee78e64fb5c7e40947fe05475560f4` と例外2箇所が一致。CSP/保存・通知境界は保持。
- 隔離archiveでsummary/design/parentの3生成器を再実行し元ファイルbyte不変。未知HTMLの親preflight拒否、改変CONTENTのpreflightとHTML書込前generator拒否を独立検査。

詳細は `static-result.json` と `static.py`。追加の採点変更・保存変更・外部OCR/LLM・実入力経路はない。

## 768×1024の独立接点probe

新規Chromium context、通知を遮断したloopbackプレビュー、合成のみ。

1. 現scienceの実入力・採点UIでlever-01へ合成回答し、学習event1件を保存。以降この既存記録と全localStorage bytesを比較。
2. 読める三角形SVGを表示し、原本の3本と転記の確認待ちを目視。転記とresolutionを実入力しrevision+2、元quote/candidates保持を確認。未解決/未確認では開始拒否。
3. triangleとtextの両方で、キーボードの明示確認→開始→入力→採点→終了。trial中editorを隠しinert、回答を保存せず、案/確認/unsavedが開始前と同一。終了でtrialとDOMを消去。
4. JSON出力はschemaVersion1の元案だけ。出力後unsaved=falseで再開始・終了しても不変。JSON再入力はdraft化し開始拒否。再確認後編集すると再び開始拒否。
5. CONTENT再読込ではproposal/trialが消える。既存science記録byte不変。scienceへ戻り再読込して同一event1件を確認。

probe観測範囲でCONTENT保存API書込0、非許可ブラウザー要求0、POST試行0、pageerror0。準備/読戻しのscienceで既存Google Fonts GET2件を遮断し別計数。全suiteには公開JS GETとmock通知があるため、全実行外部要求0とは述べない。実通知なし。

`triangle-source-768.png`、`triangle-graded-768x1024.png`、`text-graded-768x1024.png` をQAが目視。三角形と原本文、確認待ち転記、採点結果と登録答え/読み、解説、回答消去の終了操作が読める。source画像は768幅contextで要素全体を撮影した高さ1110px、採点2枚は768×1024。全画面のpixel一致や完全アクセシビリティ監査ではない。

## 既存suiteとの対応

| 条件 | 固定候補の具体的検証箇所 |
|---|---|
| 初期未解決/未確認、手動照合、3一致・4不一致、終了消去、案/確認/unsaved不変 | `tests/content_image_trial.py:80-128` と独立probe |
| schema1案JSON、再入力draft、任意source拒否、新旧画像/textの原本一致 | `tests/content_image_trial.py:84-150` と独立probe |
| text/choice実操作、全問確認、hint・採点、古いイベント拒否、非保存 | `tests/content_trial.py:52-84` |
| 編集失効、confirmed再入力拒否、pagehide/pageshow消去、pending入力拒否 | `tests/content_trial.py:85-126` |
| 非同期入力の編集/確認/出力保全、順序逆転/失敗/取消、draft復元 | `tests/content_import_guard.py:64-131` |
| 形式・意味的不足検出、編集時確認失効、安全な文字列表示 | `tests/content_review.py` |
| 修正先・確認先への案内、keyboard/focus、案内操作の非破壊性 | `tests/content_guidance.py` |
| 現mainのてこ段階別問題・履歴・mock通知、既存教材の回帰 | `tests/lever.py` と全main必須26suite |

## 限界

合成データとChromiumの固定候補検証。本人試用・学習効果・実写真OCR・実チャット/D02接続・Safari/WebKit/iPad・実BFCacheヒット・公開画面は未検証。全suite成功は外部Cloudflare build成功の証拠ではない。マージ・deploy・push・通知・私的データ・Secrets/権限/共有変更はQAから行っていない。

## 最終結果：受入可、blocking 0

全31suiteを初回で完走、全exit0。check_all計時326秒、外側の単調時計326.657秒。2026-11-22 14:09:49.075811 UTC開始、14:15:15.733001 UTC終了。詳細ログはローカル `check-all.log`、各suiteの結果は `check-all-summary.txt` / `check-all-result.json` に保存。

完走後もHEAD ee228caは同じ、追跡ファイル差分なし、diff --check exit0。試験直後は手動venv symlinkだけ未追跡であった（identity-after.json）。その後、手動作成したsymlinkだけを解除し、既存venv本体は保持。終了時は未追跡を含むstatusが空で完全clean（identity-final-clean.json）。試験時から完全cleanだったとは報告しない。結果は既存draft PR11の保存・CEO判断待ちへ受入可能であり、採用・本番merge・公開の承認ではない。

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 1 |
| `notifications/test/browser.py` | 0 | 11 |
| `tests/cloud_bootstrap.py` | 0 | 1 |
| `tests/adaptive_practice.py` | 0 | 3 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 8 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 16 |
| `tests/medaka.py` | 0 | 17 |
| `tests/lever.py` | 0 | 4 |
| `tests/microscope.py` | 0 | 22 |
| `tests/science_adaptive.py` | 0 | 10 |
| `tests/registered_answers.py` | 0 | 4 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 13 |
| `tests/parent_mode.py` | 0 | 21 |
| `tests/design_c.py` | 0 | 21 |
| `tests/responsive_subjects.py` | 0 | 118 |
| `tests/content_review.py` | 0 | 4 |
| `tests/content_guidance.py` | 0 | 3 |
| `tests/content_import_guard.py` | 0 | 3 |
| `tests/content_trial.py` | 0 | 4 |
| `tests/content_image_trial.py` | 0 | 2 |
