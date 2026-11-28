# PR10 / PR31互換同期 — 独立QA

判定: **PASS**。Reviewer `qa_rev_pr31` は実装者とは別担当。対象は固定候補 `0cd726f558d24999da80c37b1ecdbd2e6090c7bb` のみ。製品マージ・公開・実通知の承認ではない。

## 実行と固定

管理クラウド内の独立detached checkout `/workspace/qa-rev-pr31` を使用。親は既存PR10 `d26d10dea80b93cef7a47dbd814f76e3f69d3934` とmain `101c64ef9be86cb7c3502d3eeec498f16e93e7fd`。既存 `/workspace/yuika-study/.venv/bin` をignored `.venv/bin` linkで手動再利用し、各Python shellで `source scripts/cloud/activate.sh` を実行した。自動snapshot引き継ぎ成功とは扱わない。

`bash scripts/check_all.sh` は**今回1回のみ実行、32/32成功、exit 0、wall 393.749秒**。開始 `2026-11-24T10:13:03.825972+00:00`、終了 `2026-11-24T10:19:37.575412+00:00`。開始前・終了後ともHEAD一致、tracked/untracked status空。既存PR10 31 suiteとmain 27 suiteの厳密な和集合32件で重複なし。各suiteの結果は下表、コマンド・時刻・終了コードは `check-all-attempt1-execution.json`、完全ログは `check-all-attempt1.log`。失敗の再試行や追加の全suite反復はしていない。

## 差分レビューと製品保持

21変更pathを対象に、通知部分・生成元・suite変更を照合した。既存6単独HTMLの問題定義は全byte一致（応仁30、鎌倉38、平安75、理科112、模試46、江戸22問）。`scripts/practice/science.js`、`scripts/prototype/runtime.js`、問題版archive、`assets/progress.js` と理由付き復習・日次件数・理科日次・てこの既存テストは旧PR10と全byte一致。7対象ページで親境界と通知clientは各1個、親境界の終了が通知begin markerより前である。`git diff --check` 成功。`static-review.json`。

理由付き復習、実問数、理科てこの進行・再開、単位/tag、旧履歴の実行上の保持は、固定候補の全必須suite成功に帰属する。既存テストの結果を流用していない。通知対象を増やしたため、従来の「通知コードなし」assertをPR31で変更した箇所は意図した契約変更。親モード試験は模試にも通知抑止・終了後通常動作を適用し、study_reportsは4問の日次、キャンセル・未回答終了、親の通常storage不変を追加している。検証を弱める変更は認めなかった。

## 独立操作 — 8 fresh contexts、初回成功

`report-probe.py` を候補上で実行。Chromium、768×1024、touch、Asia/Tokyo。応仁・理科（実験器具）・江戸・模試算数を通常/親の各fresh contextで操作した。合成設定・合成回答だけを使用し、対象Worker POSTはルートinterceptで応答、その他の外部要求はabortした。

各contextで未回答終了は回答0・job0・送信0。1回答後の終了をキャンセルするとsession ID・回答を維持し、送信/jobは増えない。その後の承認終了は通常で回答1件のreportを1件だけ作る。受理後の同report再enqueueを2回行っても増えない。再読込で回答は同一。続いて実際の日次入口から完了し、応仁/江戸/模試は5問、理科は10問設定から実候補8問となり、画面表示・出題数・保存件数・通知件数が一致した。通常通知modeは「今日の復習」。完了画面のresultを2回呼び、再読込しても送信・job件数は増えない。

通常4contextで捕捉したmock reportは計8件。親4contextではpartial/full/empty/cancel後も送信・job生成0、sessionStorageにも通知jobなし、本人localStorage全体は開始前とbyte一致し、親終了後も同じ。親bannerは各contextで可視assert。予期しないPOST 0、pageerror 0、外部font等GET試行28件を遮断。所要20.471秒。`report-probe-result.json` / `report-probe-attempt1-execution.json`。

通常の理科ホームと親終了後の模試ホームのPNG2枚を実際に開き、該当viewport内の見出し・件数・操作欄に重なりがないことを確認した。PNGはホーム画面であり、全画面・全問題の可読性は主張しない。その他6枚は取得のみ。`visual-review.json`。

## 生成保持とself-templateの独立確認

候補の `generator_preservation.py` は従来7本を維持し、江戸・模試・通知・模試教科投影を含む12呼出し（practiceは2回）の順序を実行する。全tracked fileの初回生成前後と2回目のhash一致、元checkout不変を確認する。これは今回の全suite内で成功した。

さらに `generator-contract-probe.py` は候補tracked fileの使い捨てコピー内で、江戸questions.pyのbuild()出力の一問だけに合成の文章訂正を加えた。江戸buildがその定義をHTMLへ反映し、未登録版の通常history生成は期待どおりexit 1で拒否した。これは**意図した負例**であり、失敗からの再試行ではない。その後、同じ合成fixtureを明示的editorial版として登録すると、旧版を保持して版を1つ追加した。通知clientへ入れた合成markerも江戸へ再埋め込みされ、親境界は通知block全体より前で各1個。候補checkoutの全tracked hash不変。追加probe自体は初回exit 0、0.464秒。詳細コマンド・期待/実exitは `generator-contract-probe-result.json`。

江戸を自分自身のHTMLテンプレートから生成する変更は、理科のてこ専用処理の混入を避ける最小境界として妥当。共有history/notification/design/parentは再埋め込みされる一方、embed_scienceは理科のみ、prototype/embedは江戸を含まない。江戸内science/prototype adapterは将来の共通修正時に明示同期が必要である。READMEと `docs/pr31-compatibility.md` はこの制約を明記しており、全runtime自動同期とは解釈しない。

## 必須suiteの実測

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 5 |
| `tests/kamakura_review.py` | 0 | 4 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 1 |
| `notifications/test/browser.py` | 0 | 14 |
| `tests/study_reports.py` | 0 | 29 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/generator_preservation.py` | 0 | 1 |
| `tests/adaptive_practice.py` | 0 | 3 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 5 |
| `tests/flash_grading.py` | 0 | 9 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 17 |
| `tests/medaka.py` | 0 | 19 |
| `tests/lever.py` | 0 | 5 |
| `tests/microscope.py` | 0 | 24 |
| `tests/science_adaptive.py` | 0 | 10 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 4 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 8 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 13 |
| `tests/parent_mode.py` | 0 | 22 |
| `tests/design_c.py` | 0 | 23 |
| `tests/responsive_subjects.py` | 0 | 130 |
| `tests/recommended_review.py` | 0 | 7 |
| `tests/review_entry.py` | 0 | 3 |
| `tests/daily_count.py` | 0 | 6 |
| `tests/science_daily_count.py` | 0 | 8 |

## 限界・安全境界

実機iPad/Safari/WebKit、本人試用・学習効果、公開環境、実メール配送は未検証。必須suite内のstudy_reportsは16件をWorker validatorとstub deliveryで検証したが、実配送ではない。既存suiteは公開CDN資材をcurl取得するため、今回全体を完全オフラインとは呼ばない。独立probeの外部通信はintercept/abortに閉じた。

QAによる製品編集、board編集、push、設定変更、公開、実通知、子spawnは0件。合成の生成元変更は使い捨てコピーのみで削除済み。恒久成果はこの証拠ディレクトリに限定した。候補以後の変更はこの判定の対象外。
