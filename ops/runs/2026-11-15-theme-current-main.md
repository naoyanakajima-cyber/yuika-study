# 2026-11-15 THEME-MVP：現在の学習機能を保つテーマ試用候補

既存draft [PR12](https://github.com/naoyanakajima-cyber/yuika-study/pull/12) へ、現在mainの教材と回答記録の扱いを保持した標準/鎌倉テーマ候補を保存するサイクル。テーマは鎌倉画面だけで、新教材の全画面テーマ化ではない。目的③の好みの見た目と、目的①の最新の復習判定を両立した試用候補を整える。

## 再開・範囲・担当

cycle35 `cycle-20261115T110235Z`、開始11:02:35 UTC。クラウドrunning/connected/currentを確認し、正本 `35364fb8503b6e6cf2248f8c43c52e5be354d8fe` の指定4文書を同commitで読んだ。前回のPR11画像照合候補1678519と完了台帳・lease解放を照合し、重複実装しない。今回はGitアクセス成功、独立ops worktreeを正本commitから作成した。lease d050cecを通常push後、PdM→PrM範囲採択を3fc5bc7へ保存した。

PdM `pdm_theme_compatibility` が現mainとの接点を静的確認し、PrM `root/coordinator` が既存C1〜C8/T1〜T11と図枠2件の可読性例外を保持する限定同期を採択。Engineer `engineer_theme_compatibility` が独立checkout `/workspace/yuika-theme-current-main-20261115` で既存PR12の履歴を保って候補を作成し、別担当 `qa_theme_compatibility` が固定候補を直接検証。同時実装1件、子3名、子pushなし。

旧PR12 b416d3cは旧main86514ed基点。現在main60d1a94の鎌倉共通生成コードにはrecall初回誤答のweak化とrecall項目validatorの変更があり、新教材3suiteも追加された。これは確認したcommit差であり、テーマ不具合を再現したとの主張ではない。旧23suite成功を今回へ転用せず、現在の必須集合を使う。

## 候補と検証

候補HEAD `9fc4bbf3e6c72e09327b6610338f12937fc7aba5`。基点main `60d1a946cc02ed8acea54c0d7af7d6451fcc30ec`。PR10/11/22の未マージ差分、新テーマ、全画面展開、保存形式変更は含まない。

`bash scripts/check_all.sh` 初回26/26成功、exit0、319秒。検証対象HEAD `9fc4bbf3e6c72e09327b6610338f12937fc7aba5`。前後HEAD/cleanを独立QAで照合。

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 4 |
| `tests/cloud_preview.py` | 0 | 1 |
| `notifications/test/worker.test.mjs` | 0 | 1 |
| `notifications/test/browser.py` | 0 | 10 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 3 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 8 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 16 |
| `tests/medaka.py` | 0 | 17 |
| `tests/microscope.py` | 0 | 24 |
| `tests/science_adaptive.py` | 0 | 7 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 8 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 12 |
| `tests/parent_mode.py` | 0 | 21 |
| `tests/design_c.py` | 0 | 21 |
| `tests/responsive_subjects.py` | 0 | 120 |
| `tests/theme_review.py` | 0 | 13 |

独立静的レビューでは、現在mainとの差分はテーマ関連5filesに限定され、鎌倉の非テーマscriptと対象外の全tracked filesはmainとbyte一致、テーマ差分・既存theme検証は旧候補と一致しました。全必須登録はmain25＋theme1です。生成器再実行の整合はEngineerの証拠として分け、QAが再実行したとは扱いません。

追加UIは通常/親の合成5問runで入力・ヒント・採点・結果の切替、本人領域の不変、テーマ保存拒否中の学習継続と回復、親session拒否時の一時領域を確認。図の2ラベルは両テーマ・画面/printの各状態でcontrast6.265720821、実Tab/Space時のfocusはoffset3px・contrast5.509170074を実測しました。6枚の限定PNGをQAが目視し、PrMもhome2枚を確認しています。

追加probe初回は監視spyの評価式が戻り関数を呼んでしまうハーネス誤りで停止。空ページで初期値1/明示ブロック0/明示呼出1を再現し診断しました。2回目は通常run・図まで通過後、マウス由来focusをキーボードfocusとして測る別の誤りで停止。全probeを3回目に繰り返さず、実Tab/Spaceによる診断と未到達の親/保存障害/一時領域だけを各初回の限定補足で完了しました。製品変更・assert緩和なし。初回/2回目の失敗スクリプト・ログと到達範囲を保持し、「2回目に全probe成功」とは扱いません。

テーマ操作由来の通知呼出0、POST到達0、pageerror0を観測。既存font GETは遮断され、全suiteには公開JS GETとmock通知試験があるため、全通信0とは主張しません。代表シナリオの検証であり、全履歴・全図・全画面の完全なアクセシビリティ保証ではありません。

合成試用画面：[標準](https://github.com/naoyanakajima-cyber/yuika-study/blob/codex/agent-team-operations/ops/evidence/2026-11-15-theme-current-main/qa/standard-home.png) / [鎌倉](https://github.com/naoyanakajima-cyber/yuika-study/blob/codex/agent-team-operations/ops/evidence/2026-11-15-theme-current-main/qa/kamakura-home.png)。画像内の記録も合成です。


## 保存と外部状態

remote lease所有者/期限・既存PR12旧HEAD b416d3c・main60d1a94を照合し、11:15:09 UTCに統括が9fc4bbfを既存branchへ通常pushした。PR12説明に全26件表・担当・追加probe失敗と限定補足・制約を保存。別readbackでHEAD/説明一致、open/draft/unmergedを確認した。既存PR12のtask attachを呼び出し、新規PRは作成していない。

同HEADの [Workers Builds: yuika-study](https://github.com/naoyanakajima-cyber/yuika-study/runs/132793313794) は11:15:31 UTCにfailure。原因未特定、checkのoutput.textには診断詳細なし。旧HEADと同一原因とは断定しない。combined statusはpending/登録0件。クラウド内QAと区別し、外部ビルド再実行・設定変更・手動deployなし。既知の外部プレビュー障害へ観測を追加する。新たな製品blocking指摘は0。


## 次の一手と限界

既存PR12の標準/鎌倉切替、学習途中の見やすさ、標準復帰を合成試用で判断する。選択肢は「合成試用する／具体的な修正箇所を指定／保留」。返答はTHEME-MVPを添えてこの運用を設定した元チャットへ。返答を実際に読める担当が台帳へ記録するまではworker伝達済み・承認済みと扱わない。新CEO返答実読0、D05方向性と公開承認を区別する。

本人の嗜好・学習効果・実機iPad/Safari/WebKit・native zoom・実プリンター・公開画面は未確認。合成データとmock通知だけを使用し、実回答/実写真/メールDrive情報は取得しない。既存venvの手動再利用であり、自動snapshot引継ぎ成功ではない。

製品待ちは既存PR10/11/12の3件。外部22、旧4〜8、運用9/13は別記し、新PR枠を増やさない。3目標の既存候補を現在のmainに揃えた後は、具体的な試用フィードバック・再現不具合・新差分を待ち、同じQA/環境調査を反復しない。D02実入力/保存先は別判断。本番マージ・公開・手動deploy・実送信・課金・Secrets/権限/共有変更なし。停止中の旧自律更新は再開しない。通常成果・障害は朝夕CEOチェックへ集約し毎時通知なし。

[仕様](../../docs/product/theme-current-main-spec.md) / 証拠 `ops/evidence/2026-11-15-theme-current-main/`。終了時に台帳へ実施担当・結果・次の一手を保存しleaseを解除する。

最終台帳更新時刻：2026-11-15T11:17:29.566848+00:00。完了台帳のlease=nullを通常pushし、remote HEADと解除を確認する。

保存前のdiff検査では、証拠へ複製した全面patch内の空行コンテキストを末尾空白と検出した。重複する全面patch2件は公開証拠から除き、元hashと理由をevidence-selection.jsonへ保存。元/tmp patch・PR12のコード・重点差分・全テストログ/失敗証拠は保持した。製品変更や検証assertの緩和はない。
