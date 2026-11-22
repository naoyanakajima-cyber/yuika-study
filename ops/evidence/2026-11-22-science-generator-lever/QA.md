# 理科生成元のてこ・回答記録保護 — 独立QA

担当 `qa_science_generator`。実装者とは別の担当が独立detached checkoutで直接検証した。

- 初回全suite・限定UIの実行候補: `f60f6b2bc7c8f0b21d0789b599edf5a13269f5e5`
- 説明文のみ訂正した中間候補: `15265078a71bb6540b8db90c89eaf351d7f8913d`
- 旧fixtureの定義を補完した最終配送・2回目全suite候補: `d26d10dea80b93cef7a47dbd814f76e3f69d3934`
- 基点の既存PR10: `804f9f648c8634ea26d4ca7fc26cf6b473029475`

f60→1526507は手順文書の1行（leverテスト実行順）の訂正だけ、1526507→d26d10はscience_daily_countの旧非てこoracle fixtureの定義・説明4行だけ。f60とd26の全製品byte一致、上記2ファイル以外の全追跡byte一致を確認した。限定UIはf60で実行し、最終候補で同じprobeを反復したとは主張しない。最終候補では全31suiteを2回目として実行し、全件成功した。中間候補1526507で追加実行した生成保存テストの成功も、そのHEADの証拠に限定して記録した。`identity-attempt2-before.json` / `delivery-equivalence.json`。

## 静的レビュー

初回の変更10pathsは生成元2、同生成元を埋め込む他4HTML、生成回帰テスト、lever追加検証、suite登録、手順文書。最終候補はscience_daily_countのfixture補完を加え11paths。理科HTMLは基点と完全byte一致（SHA256 `959f6de44c42f35b6ed3ecb39aed313d5e4129c4223df55bcd75bb6651d711af`）。science.jsが既存理科HTMLのSCIENCE_ADAPTIVE冒頭へ完全一致し、prototype/runtime.jsが既存PROTOTYPE blockへ完全一致することを独立照合した。教材28問・ID・正解・解説・図、採点・保存キー・問題版・現在の選定動作の変更はない。

応仁・鎌倉・平安・模試の4HTMLは、それぞれscience専用許可列にanswerUnit/answerTagを足す1行以外の全byteが基点と一致する。その分岐は `prototypeScience` が真のときだけ選ばれ、4画面にはbyId定義がなく（typeofガード参照のみ）、既存非理科許可列は不変。通常動作・親境界・保存/拒否の実行確認は全必須suiteに帰属させる。

新しいgeneratorテストは実際の7本（practice/embed, practice/embed_science, history/embed, prototype/embed, design/build_summary, design/embed, parent/embed）をtrackedファイルの隔離コピー内で実行。1回目を元の全hashと比較し、2回目も差分なしを要求するため、「既存動作が消えた後に安定」という退行も検出する。元checkoutの不変も確認しており、assert弱化・skipはない。

同一の新テストを基点804f9f6へ移した独立の負例確認は、1回目生成で `yuika-review-v2.html` が変わる期待通りのexit1になった。baseline生成は一時コピー内のみ、baseline追跡ファイルは不変。Engineer報告の転記ではなくQA自身の直接実行。`baseline-regression.log` / `delivery-equivalence.json` を参照。

## 限定UI — 初回成功

`probe.py` / `probe-result.json`。Chromium、768×1024、通常/親の各fresh context、合成回答のみ。通知遮断CSP付きPreviewHandlerで実POST到達を禁止、routeでも外部要求を遮断した。

両モードでlever-16の数値欄へ典型誤答を入力し、実際の答え合わせで `answerUnit=cm` と定義された `answerTag` を生成・保存。再読込で同じ回答を確認後、実JSONダウンロードを取得し、試作キーだけを空にしてfile inputから再取込みし、さらに再読込して全フィールド一致を確認した。

続いてunit/tag項目のない同じ形式の旧回答を合成の別IDでJSON取込みし、2回答として受理されることを確認。invalid unit、invalid tag、未知項目の3種類は全体を拒否し、rejectedImportRawが拒否した入力と一致し、メモリ上の回答・保存済みrawは不変であることを確認した。親モードでは本人localStorage全体が最初の合成sentinelを含めて不変。

probeのPOST要求0、pageerror0、既存外部font GET 11件を遮断。全通信0とは主張せず、全suite内の模擬APIテストとも区別する。

QAはnormal/parentの採点後PNG2枚を実際に開いて確認。単位付き回答・5段の解説・保存結果が読め、限定した採点領域で文字重なりは認めない。スクロール後の768×1024画面なので、全画面や全問題の可読性の証明ではない。親bannerも画像で確認した。

## 必須suite

初回f60f6b2で全31suiteを実行し30成功・1失敗、308秒、exit1。`science_daily_count.py` の旧非てこNode選定oracleが `LEVER_UNIT` を定義せず、source同期後の関数抽出でReferenceErrorになった。他30suiteと独立限定probeは成功。既存の選定順・乱数消費・件数assertを維持してfixtureを更新する差戻しとした。修正は元から非てこのq0..q19を用いるoracleへLEVER_UNIT実値とlocked challengeを明示する4行のみ。元の28ケースと全assertは不変、てこ実経路はlever suiteで維持する。修正後d26d10の全31suiteは2回目で全件成功、exit0、322秒。前後HEAD一致、status空。新生成回帰も最終HEADで成功。`check-all-attempt1-result.json` を参照。

## 準備・限界

管理クラウド内の別detached checkoutと、既存 `/workspace/yuika-study/.venv` をignored `.venv/bin` linkで手動再利用。開始時status空、自動snapshot引き継ぎの証明ではない。実機iPad/Safari/WebKit、本人の記録・嗜好・学習効果、公開環境、実通知は検証していない。通知suiteは既存mockのみ。main merge、push、公開、設定変更はQAでは実施していない。

## 最終確定結果

独立レビュー判定：合格。最終配送HEAD `d26d10dea80b93cef7a47dbd814f76e3f69d3934` の全31suiteが2回目に成功。初回失敗とその原因を隠さず、限定UIは製品byte同一のf60実行へ帰属させる。以後の追加全suiteやprobe反復なし。

| Suite | exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 1 |
| `notifications/test/worker.test.mjs` | 0 | 1 |
| `notifications/test/browser.py` | 0 | 10 |
| `tests/cloud_bootstrap.py` | 0 | 1 |
| `tests/generator_preservation.py` | 0 | 1 |
| `tests/adaptive_practice.py` | 0 | 2 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 7 |
| `tests/spaced_daily.py` | 0 | 5 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/edo.py` | 0 | 15 |
| `tests/medaka.py` | 0 | 16 |
| `tests/lever.py` | 0 | 5 |
| `tests/microscope.py` | 0 | 22 |
| `tests/science_adaptive.py` | 0 | 9 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 2 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 7 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 11 |
| `tests/parent_mode.py` | 0 | 25 |
| `tests/design_c.py` | 0 | 19 |
| `tests/responsive_subjects.py` | 0 | 116 |
| `tests/recommended_review.py` | 0 | 6 |
| `tests/review_entry.py` | 0 | 3 |
| `tests/daily_count.py` | 0 | 5 |
| `tests/science_daily_count.py` | 0 | 7 |

詳細 `final-result.json`。
