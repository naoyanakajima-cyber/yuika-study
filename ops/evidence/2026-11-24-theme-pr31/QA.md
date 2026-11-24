# PR12 / PR31互換同期 — 独立QA

判定 **PASS**。実装者と別担当の `qa_theme_pr31` が固定候補 `df7af2a205f44e8c76b50e96728685efcc7e57d8` を検証。製品マージ・公開・実通知の承認ではない。

## 固定候補と必須チェック

独立detached cloud checkout `/workspace/yuika-theme-pr31-qa`。親は旧PR12 `00c4ccb3b501223366a5f0a736567231ea9b8043` と観測main `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`。ignored `.venv/bin` linkで既存 `/workspace/yuika-study/.venv/bin` を手動再利用し、各テストshellで `source scripts/cloud/activate.sh`。自動snapshot引き継ぎ成功とはしない。

`bash scripts/check_all.sh` は今回 **1回のみ、29/29成功、exit 0、wall 368.253秒**。開始 `2026-11-24T12:11:49.035209+00:00`、終了 `2026-11-24T12:17:57.287878+00:00`。前後HEAD一致・status空。旧PR12の28本とmainの27本の厳密な和集合29本。個別exit/秒は下表と `summary.json`、全出力は `check-all-attempt1.log`。Engineerのdirty tree実行や以前の成功は今回へ算入しない。

独立補助試験も全て初回成功。製品失敗0、QAハーネス失敗0、無根拠な再試行0。source検証・生成はブラウザーと一部並行実行、各checkoutは不変。

## 固定差分とテーマ保持

`static-review.json` は鎌倉のテーマCSS・操作部・runtimeの各blockが旧PR12からbyte不変であることを確認。テーマ仕様/既存試験、science adapter・埋込元、prototype runtime、adaptive、履歴archive、lever試験、progress資産、preview CSP実装もbyte不変。6学習HTMLの問題定義はすべてbyte不変（応仁30・鎌倉38・平安75・理科112・模試46・江戸22）。7通知対象はparent/runtimeとreport blockが各1つで、親境界はreport開始markerより前。

模試generatorの除外は鎌倉固有の3blockだけを正規表現で各1件とassertして削除する。教材・採点・履歴や推薦機能を除外する変更ではない。鎌倉以外の6画面にはtheme controls/style/runtimeなし。固定候補の初回/2回目生成後も模試にテーマを持ち込まない。PR10の `scienceDailySources`、PR11のCONTENTページは含まない。

江戸/模試の旧「通知なし」assertはmain PR31の意図した通知契約に変わるため更新されている。親抑止・件数・重複の検証は保持・追加。`tests/study_reports.py` はplanned件数、キャンセル、未回答終了、親localStorage全体不変を追加。`git diff --check` 成功。固定差分は `diff-review.log`。

## 独立テーマ操作・図・理科記録

fresh Chromium通常/親の2context、768×1024で5問ずつ回答。text/choice入力、ヒント、採点後、結果の各段階で標準↔鎌倉を操作し、同じrun・問題列/index/results・入力値・学習DOM・学習データ/preferencesを比較して不変。通常はテーマkey以外、親は子localStorage全体が不変。テーマ操作由来のenqueue/通信0。鎌倉選択後のreloadで5回答とテーマが復元。実行18.864秒。

標準/鎌倉のscreen/printで階層SVG DOMは同一。将軍・執権（北条氏）の白13px文字と背景#8f4f3cはcontrast **6.2657:1**。printではテーマ操作を非表示にし、保存値を変えない。同一originで標準→鎌倉→標準を選んで理科へ移動しても、lever-01/27/28の図形・文字・位置は比較基準と同一、テーマDOMなし・横overflowなし。POST/pageerror0、既存外部font GET16件は遮断。`probe-result.json`。

別の通常/親2contextでlever-16の合成数値回答からanswerUnit/answerTagを保存し、reload→実JSON download→空の試作保存領域へfile input import→reloadで保持。unit/tagのない旧形式を受理。不正unit、不正tag、未知fieldは入力rawを保持して拒否し、既存eventsと保存内容は不変。親の子localStorage全体不変。POST/pageerror0、外部GET11件遮断。実行4.885秒。`science-probe-result.json`。

保存PNG4枚を実際に開いて確認：通常/親の鎌倉入力+hintは質問・入力・主操作が読め、親banner/終了も見える。階層図のラベル/接続線、lever-28の45g/15g/未知値/長さ表示を識別でき、保存範囲で重なりなし。通常PNGの通知欄は画面下部の一部しか写らない。全画面・全状態の目視確認とはしない。`visual-review.json`。

## 独立通知ライフサイクル

応仁・理科てこ・江戸・模試算数を通常/親の8fresh context、768×1024・touchで操作。未回答終了はevents/job/report0。1回答後ホーム移動キャンセルではsession ID/回答保持、job/report0。その後途中終了は通常で回答1件のreport1件。再enqueue2回とreloadで件数不変。日次入口から5問完了し、events・正答数・report answersが一致、modeはPR12自身の「今日の5問」。result2回/reloadで再送なし。模試にテーマDOMなしも確認。

通常4context合計8mock report、親4contextはreport/job0かつsessionStorage通知jobなし。親bannerをassertし、子localStorage全体はbyte不変。予期しないPOST/pageerror0、外部GET28件遮断。実行19.915秒。`report-probe-result.json`。必須study_reportsの16reportはWorker validator/stub deliveryにも通るが実配送ではない。

てこ専用「今日はここまで」は既存の結果画面へ直ちに進む契約。キャンセルは実際のホーム移動を使い、終了後は結果のreturnを操作した。通常社会と同じ終了dialogを仮定していない。

## 生成保持・質問伝播・archive

必須suiteに加え、独立使い捨てtracked copyで12呼出し（practice2回）の実生成列を2pass実行。**初回全tracked byte保持・2回目不変**、元checkout不変。各commandのexitと時間は `generator-contract-probe-result.json`。

同じ使い捨てcopyで江戸questions.buildの1問へ合成文章訂正を加え、buildのHTML伝播を確認。版未登録history生成は期待どおりexit1で拒否し、明示editorial登録は旧版を維持して版を1つ追加。共有通知clientの合成markerが再埋込され、親境界はreport block全体より前に各1つ。意図した拒否exit1は製品失敗/再試行ではない。probe全体exit0、1.512秒。

江戸のself-templateはてこ固有コードの流入を防ぐ。science/prototype adapterの今後の共通変更は江戸への明示同期が必要で、全runtime自動同期ではない。READMEと実装文書はこの制約を明記している。模試のテーマblock構造変更時はcount assertで停止し、再レビューが必要。

## 必須suite実測

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 1 |
| `notifications/test/browser.py` | 0 | 13 |
| `tests/study_reports.py` | 0 | 31 |
| `tests/cloud_bootstrap.py` | 0 | 4 |
| `tests/generator_preservation.py` | 0 | 1 |
| `tests/adaptive_practice.py` | 0 | 4 |
| `tests/adaptive_daily.py` | 0 | 5 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 8 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 15 |
| `tests/medaka.py` | 0 | 17 |
| `tests/lever.py` | 0 | 5 |
| `tests/microscope.py` | 0 | 22 |
| `tests/science_adaptive.py` | 0 | 10 |
| `tests/registered_answers.py` | 0 | 2 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 5 |
| `tests/prototype_storage.py` | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 13 |
| `tests/parent_mode.py` | 0 | 20 |
| `tests/design_c.py` | 0 | 23 |
| `tests/responsive_subjects.py` | 0 | 124 |
| `tests/theme_review.py` | 0 | 13 |

## 限界と権限

実機iPad/Safari/WebKit、本人試用、嗜好、学習効果、公開画面、実メール配送、外部Workers build成功は未検証。必須suiteの一部は既存公開CDNをcurl取得するため完全offlineではない。独立probeはmock/外部abort、合成データのみ。

QAのproduct/board編集、push、設定変更、公開、実通知、private inputs、子spawnは0。合成生成元変更は削除済み使い捨てcopyのみ。恒久証拠はこのdirectoryのみ。候補以後の変更は判定対象外。完了 `2026-11-24T12:18:07.345277+00:00`。
