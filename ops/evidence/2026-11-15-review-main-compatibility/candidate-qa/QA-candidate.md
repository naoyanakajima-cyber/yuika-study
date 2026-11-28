# Cycle32 independent QA: existing PR10 compatibility candidate

独立担当 qa_theme_compatibility。PrMの同サイクル継続条件を満たし、Engineerがfreezeした **6d01386dba0bb3cdafa7e8f431a6a17bc81e913f** を対象に、統括承認の読み取りQAを実施。親commitは旧PR10 `73fe2ee9d776b3e3360614752fb722ff4aee4f85` と観測main `60d1a946cc02ed8acea54c0d7af7d6451fcc30ec`。対象checkout `/workspace/yuika-review-main-compat-20261115` はEngineerが編集停止済みで、別担当QAが利用した。新QA checkoutを別途作成したとは報告しない。

## 判定：既存PR10互換性候補は独立QA合格

候補HEADの `bash scripts/check_all.sh` を初回実行し、**29/29成功・349秒・exit0**。完了UTC 2026-11-15T08:26:18.119691+00:00、実行前後HEAD一致・working tree clean。main段階の25suite/308秒成功とは別の実行であり、統合変更に対して必要な再検証。独立限定probeは初回成功（4recall＋3入口、計7fresh contexts）。実装者focused成功を独立全suite成功へ転用しない。

## 独立静的境界

- 6アプリの全問題オブジェクト・順序・IDが観測mainと一致。理科84、江戸22、応仁30、鎌倉38、平安75、重点46。既存保存キー定義も全一致。
- 理科/江戸HTMLはSCIENCE_ADAPTIVE領域を除いて観測mainとbyte一致。問題入力、採点、validator、保存schema、2段階回答runtime・元の説明/図を保持。
- history archive、history/prototype runtime、parent runtime、medaka runtime、CSS、江戸generatorはmainと同一。
- build_summaryはmainからdaily表示名だけが変わり、現行validator、recall読み取りprojection、実在unit guardを保持。
- 共通adaptive.jsは旧PR10にmainのrecall初回weak行を1行追加したものと完全一致。社会/重点4ページは旧PR10にこの1行とmain既存recallフィールド許可を反映したものと完全一致し、理由付きおすすめ・既存入口コードを落としていない。
- PR10のrecommended_review/review_entry/daily_countテストは旧候補とbyte一致。science_daily_countには新recallの保存正解と復習投影、日次件数/先頭問題を追加し、既存assertを維持。
- check_allの登録はmain25と旧PR10の26の完全な和集合29件。重複/削除なし。
- Generatorの再生成による書込みはQAでは実施していない。Engineerの2回生成一致は別担当の証拠。QAでは生成された理科/江戸の日次表示と実動作、生成前後の限定境界を直接確認した。

## 独立probe：混在履歴と日次

現在の合成データでメダカ07と江戸01を通常/親各1、4ケース。main段階と共通の境界を、統合で変更されたadapter/dailyの固定候補上で再検証した。代表1問のsessionを設定した後は実入力・選択・確定UIで操作。4ケースとも次を確認。

- 最初の誤答で選択肢が出ても保存イベント/rawは不変。再読込で未確定イベントを作らない。
- 選択肢正解の最終確定で1イベントだけ保存。保存correct=true/recallOutcome=assisted/最初の誤答/最後の正答/hintUsed=true。disabled確定ボタンとsubmit再呼出しguardで重複しない。
- 読み取りprojectionはcorrect=falseで弱点・日次優先、保存raw/stateを変更しない。理科通常では旧選択式の版番号なし正解と混在し、旧イベントを完全保持、新2項目を付与しない。
- 親2例では本人localStorage全体のbytesを維持。firstResponse欠落のvalidator拒否でも元保存raw不変。
- 実日次開始はメダカ通常/親・江戸通常で表示5/実5、江戸親で表示10/実10。4例とも選択肢正解だった代表問題が実セッションの先頭に残る。江戸も表示名「今日の復習」。表示/開始により回答イベントを追加しない。

追加3入口を独立fresh contextで確認した。

| 条件 | 要約total/normalCount | 表示/実日次 | 確認 |
|---|---:|---:|---|
| 実験器具、上限10 | 84/8 | 8/8 | 実8問全て実験器具 |
| 有効メダカURL、上限5 | 17/5 | 5/5 | 実5問全てmedaka ID |
| 未知unit URL、上限5 | 84/5 | 5/5 | allへfallback |

3入口とも動的badge「解説つき・理科全84問」。器具/未知入口の合成PNG2枚を独立目視し、選択単元、84問tag、日次8/5表示を確認した。全画像・全画面の目視とはしない。

7contextsすべてChromium768×1024、合成記録のみ。POST要求0/pageerror0、外部GETは遮断。上記probeは実ホームReactカードをクリックせず、同じ生成summary関数を対象アプリに読み込んで評価。ホームカード/自動入口/保護境界は全suiteの専用テストを利用する。上限10に切り替える前のsummary値と切替後の実日次件数はJSONで別フィールドとして記録し、同時刻同条件のtop10表示確認とはしない。

## 必須suiteの役割と残る限界

全suiteは公開JS GETとmock通知を含む。probeのPOST0を全suiteの通信0へ一般化しない。既存suiteの未利用/0候補・dirty/blocked・stale表示・乱数/選定oracle・通常/親top入口、recommended理由表示/開始、全新教材回答/履歴回帰を、候補の実行結果として確認する。0候補は合成防御境界で、通常UIに0問単元があるとはしない。

本人試用、学習効果、実機Safari/WebKit/iPad、公開ページ、他PR11/12との統合、全教材事実の再校閲、多タブ同時確定競合は未検証。旧版への新recall JSON逆互換性を追加保証しない。学習間隔1/3/7日は仮案のまま。

## 保存・権限

既存verified venvを手動再利用、requirements-dev一致、正規activateで実行。自動snapshot成功とは扱わない。QAは製品/ops編集、commit/push、merge、公開/デプロイ、実送信、設定変更、新子起動なし。統括が有効leaseとremote/main/PR10現在HEADを確認して通常pushするまで、候補提出済みとは扱わない。CEO承認・main反映・公開成功をQAから推論しない。

証拠 `/tmp/yuika-cycle32-candidate-qa/`。main段階は `/tmp/yuika-cycle32-QA-main.md` と別証拠。29suite完了後に前後HEAD/clean・実時間・SHA256SUMSを確定した。

## 候補HEADの実測全suite表

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 3 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 0 |
| `notifications/test/browser.py` | 0 | 12 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 2 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 9 |
| `tests/spaced_daily.py` | 0 | 7 |
| `tests/history_compat.py` | 0 | 5 |
| `tests/edo.py` | 0 | 15 |
| `tests/medaka.py` | 0 | 18 |
| `tests/microscope.py` | 0 | 23 |
| `tests/science_adaptive.py` | 0 | 8 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 3 |
| `tests/state_review_regression.py` | 0 | 6 |
| `tests/prototype_storage.py` | 0 | 9 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 13 |
| `tests/parent_mode.py` | 0 | 21 |
| `tests/design_c.py` | 0 | 23 |
| `tests/responsive_subjects.py` | 0 | 129 |
| `tests/recommended_review.py` | 0 | 6 |
| `tests/review_entry.py` | 0 | 4 |
| `tests/daily_count.py` | 0 | 5 |
| `tests/science_daily_count.py` | 0 | 9 |

全29項目は実行され、失敗・再試行なし。主結果は限定互換性候補の受入であり、CEO承認や公開完了ではない。
