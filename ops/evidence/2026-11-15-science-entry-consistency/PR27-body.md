## 変更内容
理科に「顕微鏡の使い方」のオリジナル20問を追加します。理科一覧から新単元を開き、既存の選択式採点・回答記録・苦手復習・再確認・日次復習を利用できます。

- ピント合わせ4問、像とプレパラートの方向4問、レンズ名2問、取り付け理由1問、操作順3問、低倍率2問、倍率計算2問、範囲と明るさ2問。
- 操作順は既存の「次にすること」の選択式を使用。新しい採点規則は追加しません。
- 新問の専用ID・概念ID・根拠/解説とrevision1を登録。既存47問と保存キー・履歴の意味は保持します。学校プリントの転載・個人情報はありません。
- 単元URLの一覧要約と実際の開始範囲をそろえました。未知のunitは既存アプリと同様に無視し、空の合成履歴では全67問から5問を開始します。有効な顕微鏡指定は20問の範囲から5問です。
- 旧固定表示「47問」は、理科全体を示す動的表示「理科全67問」へ更新しました。顕微鏡20問と全体件数を区別します。

## 起点と範囲
baseはmain `86514eda054a5a2e09204df3a0668e40624c16de`。元の20問追加候補は `58c3fd4ba10ecfaa249cc3c808c3e8e5fcaf5359`、現在HEADは `69f77d671b66484b501f7a0f5c292bfa96a22273` です。

追加修正はgenerator・生成物・回帰テスト・HTMLのtag1箇所だけです。PR10の日次ラベル/実問数修正は取り込んでいません。PR10とは理科画面・ホーム集計などのファイルが重なるため、将来の統合候補では併せて検証が必要です。新しい製品PRは作成していません。再確認間隔1・3・7日は既存の仮案です。

## 独立レビューと検証
PdMによる受入条件 → 統括PrMの範囲確認 → Engineerの独立checkout実装 → 別担当 `qa_theme_compatibility` の検証で進めました。元の20問の事実関係レビューと23suite3連続成功は作者が58c3fd4で報告した結果です。今回の統括チームの成功回数とは区別します。

今回、独立QAが58c3fd4で必須23suiteを初回実行して全成功（264秒）。追加probeで未知unitの要約0/実出題5と旧47問表示を再現しました。最終HEADの結果は以下です。

同HEADで `bash scripts/check_all.sh` を初回実行し、23/23成功、skipなし、264秒。実行前後cleanを確認。

| Suite | Exit | 秒 |
|---|---:|---:|
| `tests/onin_review.py` | 0 | 4 |
| `tests/kamakura_review.py` | 0 | 4 |
| `tests/cloud_preview.py` | 0 | 2 |
| `notifications/test/worker.test.mjs` | 0 | 0 |
| `notifications/test/browser.py` | 0 | 11 |
| `tests/cloud_bootstrap.py` | 0 | 2 |
| `tests/adaptive_practice.py` | 0 | 2 |
| `tests/adaptive_daily.py` | 0 | 4 |
| `tests/adaptive_quality.py` | 0 | 4 |
| `tests/flash_grading.py` | 0 | 9 |
| `tests/spaced_daily.py` | 0 | 4 |
| `tests/history_compat.py` | 0 | 4 |
| `tests/microscope.py` | 0 | 25 |
| `tests/science_adaptive.py` | 0 | 8 |
| `tests/registered_answers.py` | 0 | 3 |
| `tests/history_review_regression.py` | 0 | 2 |
| `tests/state_review_regression.py` | 0 | 4 |
| `tests/prototype_storage.py` | 0 | 8 |
| `tests/focus_data.py` | 0 | 0 |
| `tests/focus_practice.py` | 0 | 12 |
| `tests/parent_mode.py` | 0 | 20 |
| `tests/design_c.py` | 0 | 20 |
| `tests/responsive_subjects.py` | 0 | 112 |

追加probeは有効/未指定/空/未知の4入口で、要約・選択単元・実際の通常/日次開始を照合。全4ケースで表示対象と開始範囲が一致し、POST要求/ページエラーは0件でした。既存の20問・60通りのタップ採点・保存/再読込・弱点→再確認→日次の回帰も保持しています。既存47問はmainと解析後オブジェクトが一致し、最小修正では問題データを変更していません。

クラウド内で既存venvを手動再利用しました。自動snapshot引き継ぎ成功ではありません。補足probeの初回はactivate未適用でブラウザ未検出となり製品到達前に停止。原因を特定して正規activate後の2回目で成功しました。必須suiteの再試行ではありません。

[仕様・担当・検証証拠・次の一手](https://github.com/naoyanakajima-cyber/yuika-study/blob/codex/agent-team-operations/ops/runs/2026-11-15-science-entry-consistency.md)

## 制約・公開状態
Chromiumと合成データ・模擬APIでの検証です。Safari/WebKit・iPad実機、全保存済み設定の組合せ、本人の学習効果、PR10との統合は未検証です。現在HEADの[Workers外部チェック](https://github.com/naoyanakajima-cyber/yuika-study/runs/132723386624)は2026-11-15 06:20:07 UTCにfailure。原因調査・設定変更・再実行は行っておらず、クラウド内23suite成功や公開成功とは区別します。

draftのまま判断待ちです。正本チャットの新たなCEO返答は今回取り込んでいません。本番マージ、公開・手動デプロイ、実通知、課金、Secrets・アクセス権変更は実施していません。
