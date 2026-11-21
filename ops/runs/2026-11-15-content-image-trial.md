# 2026-11-15 合成画像から確認・試し解きへの成功経路

CONTENT-MVPの既存draft [PR11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11) に、手作り三角形SVG1枚・短答1問の照合サンプルを追加した。目的②の「画像を見て転記を直す→問題を明示確認→保存しない試し解き」を通せる。判読不明画像の拒否だけだった従来例を保持し、読める原本の成功例を別に用意した。実写真処理・OCR・教材本体への登録や、人の照合結果の機械的な意味保証ではない。

## 実行と分担

cycle34 `cycle-20261115T100218Z`、開始2026-11-15 10:02:18 UTC。クラウド実行を確認し、正本 `07859fe627c8a42da28ed0837a932198cdc7d75b` の指定4文書を同一commitで読んだ。lease取得 `20348ba`、PdM→PrMの範囲確定を `bdceb98` に通常pushした後、独立checkoutで実装した。子は下記3名のみ、同時実装1件、子のpushなし。

- PdM: `pdm_content_trial_delivery`。原本・初期案・出典領域・人の確認手順と負例を具体化。
- PrM: `root/coordinator`。既存PR11内・合成例限定・記録非接続の範囲を採択し、統合と外部書込み前の実行権を確認。
- Engineer: `engineer_content_trial_delivery`。候補 `1678519f916471ba6e38044855de240bd6c4a807` を作成し、focused2suiteと静的照合。実装後は候補を固定。
- 独立Reviewer/QA: `qa_content_trial_delivery`。固定候補を直接読取り、全必須suite、追加15ケース、SVG/三つ組選択、改変content/未知HTML拒否と保存境界を検証。

既存の検証済venvを手動再利用し依存を照合。自動snapshot引継ぎの成功とは扱わない。Engineerのfile://プレビューが管理ポリシーで拒否されたため、既存の許可済loopback手順を使用した。権限・設定を変更していない。

## 変更と受入

新しい「画像・読める図形の例」は未解決・未確認のdraftで始まる。原本の「三角形の辺は3本です。」を見て転記と読み取りを修正し、問題案を明示確認すると開始できる。3は登録答えと一致、4は不一致。終了で試行回答を消し、元案・確認状態・未保存状態を保つ。

画像選択は既知のkind/sourceId/locator三つ組と信頼済み同梱assetの明示対応へ限定変更。JSON由来SVG/任意URLを表示しない。旧97files、学習HTML/ID/キー/recall/履歴/親runtime、CSP、試行採点・消去、案schemaを保持。変更HTMLの固定hash例外2箇所は独立memory-onlyレビューを経て確認した。

## 検証結果

`bash scripts/check_all.sh` 初回30/30成功、exit0、332秒。固定HEAD `1678519f916471ba6e38044855de240bd6c4a807`、前後clean。

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 5 |
| `tests/kamakura_review.py` | 0 | 4 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 1 |
| `notifications/test/browser.py` | 0 | 11 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 2 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 9 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 3 |
| `tests/edo.py` | 0 | 17 |
| `tests/medaka.py` | 0 | 18 |
| `tests/microscope.py` | 0 | 23 |
| `tests/science_adaptive.py` | 0 | 8 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 8 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 13 |
| `tests/parent_mode.py` | 0 | 21 |
| `tests/design_c.py` | 0 | 20 |
| `tests/responsive_subjects.py` | 0 | 125 |
| `tests/content_review.py` | 0 | 4 |
| `tests/content_guidance.py` | 0 | 2 |
| `tests/content_import_guard.py` | 0 | 4 |
| `tests/content_trial.py` | 0 | 4 |
| `tests/content_image_trial.py` | 0 | 3 |

独立15ケースは初回ハーネスのfocus期待誤りを診断し、製品を変更せず2回目に完走。trial-repair→issues-0とnext-step→resolution-0を別々に検証した。初回スクリプト/ログも保存し、初回の未到達ケースを成功扱いしていない。静的・隔離負例は初回PASS。Engineerの試験や過去65probeを今回の独立ケース数へ加算しない。

限定probeの観測範囲で保存API書込・非許可要求・pageerror 0。全体suiteには公開JS GETとmock通知試験があるため、全体外部要求0とは主張しない。実通知は送っていない。

[原本と確認待ち転記](../evidence/2026-11-15-content-image-trial/qa/source-and-transcription-768.png) / [試し解き採点](../evidence/2026-11-15-content-image-trial/qa/trial-match-768x1024.png)。Reviewerが768×1024で視認し、PrMも原本/転記PNGを確認。実写真・本人回答を含まない。

## 保存・外部check

2026-11-15 10:16:57 UTCにremote正本bdceb98の所有lease/期限・PR11旧HEAD d75a546・main60d1a94を再確認し、通常pushで既存branchを `1678519f916471ba6e38044855de240bd6c4a807` へ更新。HEAD一致・open/draft/unmerged・PR説明のreadbackを確認した。新規PRなし、既存PR11はこのタスクへattach済み。全30件表と残る制約をPR説明へ保存した。

同HEADの [Workers Builds: yuika-study](https://github.com/naoyanakajima-cyber/yuika-study/runs/132779047651) は10:17:24 UTCにfailure。取得情報はビルド参照のみで原因詳細なし、過去HEADと同一原因とは断定しない。combined statusはpending/登録0件。独立クラウドQA成功と区別し、再実行・設定変更・手動deployなし。新しい製品blockingは0、既知の外部プレビュー障害へ今回の観測を追加した。

最終台帳更新時刻：2026-11-15T10:20:53.144292+00:00。leaseはこの完了保存でnullにし、expected_sha付きref更新後にremote一致を確認する。

## 次の一手・判断境界

まず既存PR11の合成例を使い、「原本を見て直す箇所と、確認後の試し解きが分かるか」の具体的な試用判断へ進む。本人試用・学習効果・実機Safari/WebKit/iPad・実BFCache・公開画面は未確認。CEOの新返答実読0で、workerへ新判断伝達済みとは扱わない。試用の判断はこの運用を設定した元チャットへCONTENT-MVPを添えて返し、実際に読める担当が台帳へ記録する。

待ち枠は既存製品PR10/11/12の3件、旧4〜8と運用文書PRは別、外部draft22も別記。新規PRなし。次の独立候補はTHEME-MVPの現mainとの接点確認であり、同じ確認を反復せず具体的な互換性差分がある場合に既存PR12内で範囲を決める。D02実入力/保存先は未決。mainマージ・公開・手動deploy・実送信・課金・Secrets/権限/共有変更なし。通常報告は朝夕CEOチェックに集約し毎時通知なし。

仕様 [content-image-trial-spec](../../docs/product/content-image-trial-spec.md)、役割別報告と実行ログは `ops/evidence/2026-11-15-content-image-trial/`。終了時に台帳を保存しleaseを解放する。

保存時のdiff検査で失敗probeログの末尾空白1字を検出した。公開用コピーだけを正規化し、原本/保存後hashと変更理由をevidence-normalization.jsonへ記録。行や失敗内容を削除せず、/tmp原本は保持した。製品テストの再試行ではない。

最終保存前のGit ls-remoteで認証を利用できず停止（1回、Usernameを読めない）。クラウドはrunning/connected、GitHubコネクタの読取りは成功。認証情報・接続・設定を変更せず、既存接続のGitデータAPIとexpected_sha付きref更新で完了台帳を保存する。製品PR11への通常pushはこの障害前に成功・readback済み。
