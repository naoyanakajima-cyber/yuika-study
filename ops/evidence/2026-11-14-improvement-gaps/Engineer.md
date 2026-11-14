# Engineer技術調査：日次入口と既存PRの差分

2026-11-14。製品コード変更なし、ブラウザー・アプリ全テスト・実データ読込なし。指定commitのGitオブジェクトを読んだ調査と、抽出した純粋関数の合成試験のみ。機能完成・公開・統合可能の承認を意味しない。

## 固定対象と比較方法

- main: `86514eda054a5a2e09204df3a0668e40624c16de`
- PR #10: `ba829a1176ff1ead7d312526890afe8792178c99`
- PR #11: `3d2ed2f9a62673d2fb086a360ae841096f35b63e`
- PR #12: `57171ad9cab02fec6a080ecbe317fe11d3f51dcf`
- 各PRとmainのmerge-base: `edad8065c1f2b726e61c5cf405f8d9ff6d807480`

実行：各組に `git merge-base <main> <PR_HEAD>`、`git diff --stat <merge-base> <PR_HEAD>`、`git diff --name-status <main> <PR_HEAD>`、`git merge-tree --write-tree <main> <PR_HEAD>`。merge-treeはGitオブジェクトの仮想統合を計算し、checkout・index・branch・製品ファイルを変更しない。今回の書込みはその一時Gitオブジェクトと/tmpの成果だけ。merge/rebase/pushはしていない。

| PR | 三方向競合（exit 1） | 仮想tree |
| --- | --- | --- |
| #10 | `kamakura-review.html`, `onin-review.html` | `83b63b001aed73fd0ae5fa625cf28452c0edeb9c` |
| #11 | `scripts/cloud/serve.py` | `430b786448147fb7a6a58e918e398b0e7569043b` |
| #12 | `README.md`, `kamakura-review.html` | `b279155f42d17c88fc2cbbd66797a7fa29d455e5` |

endpoint比較では`assets/design.css`、`assets/progress.js`、`scripts/practice/*`等がDになるが、これは旧PRのsnapshotに現在mainの追加物がないという意味。PRがそのファイルを削除する変更を含むことや、実三方向mergeがその全てを削除することの証拠ではない。上表の競合と区別する。競合解消後の動作安全性も未検証。

## 機能照合・不足・統合ゲート

| 対象 | mainとの重複と残る価値 | PR固有変更（merge-base比較）・主な影響 | 保存・採用の必須ゲート |
| --- | --- | --- | --- |
| #10 復習 | mainには日次入口、期限到来→弱点→通常の選定、弱点の事実表示、再確認周期が存在。#10のrecommendedPlanによる「最後の誤答／24時間／ヒント正解」の候補と理由はmainの別仕様で、完全代替とはいえない | README、応仁・鎌倉HTML、`tests/recommended_review.py`、`tests/review_entry.py`。5 files / +483 -8。日次入口を二重にせず、残す理由表示をmainの選定段階へ対応付ける必要 | #10 HTMLは旧localStorage保存・旧キー。mainのYuikaParent.storage、prototype名前空間、問題版検証を維持。旧HTML全体の置換は不可。問題ID・variant・選定条件・開始だけで回答を書かない条件を確認 |
| #11 教材確認 | mainにcontent-review.htmlはない。全問確認・revision失効・次の作業案内・確認済みJSON出力が固有価値。試し解きはない | `content-review.html`、`docs/product/content-spec.md`、合成fixtures4件、tests2件、README、cloud文書、serve.py。11 files / +849 -3 | メモリ内proposalとJSON出力を維持。acceptProposalは読み込んだconfirmedをclearConfirmする(73行)、編集はrevision++と全確認解除(74行)、exportは現在revisionとissues再判定(171–174行)。本番教材導入・学習履歴書込とは分離。serve.py競合を既存CSP/配信制約を弱めず解消する必要 |
| #12 テーマ | mainの共通design.css/jsの教科表示は個人による標準/鎌倉選択と別。本人が選ぶテーマの価値は残る | 鎌倉HTMLだけ、README、theme-spec、theme_review。4 files / +408 -1。応仁はテーマ実装対象ではない | 専用キー`yuika-ui-theme-kamakura-v1`とdata-ui-themeのCSS。mainの親確認モード保存隔離に適合させ、design.cssの優先順位、フォーカス・コントラスト・問題採点不変を確認。学習キーへの流用不可 |

main根拠：`onin-review.html:781`は`LEGACY_KEY`と`KEY='yuika-prototype-v1:'+LEGACY_KEY`。`scripts/parent/runtime.js:23–28`は親確認時sessionStorage/一時メモリと通常localStorageを分ける。`scripts/prototype/runtime.js`は厳格な入力形式と問題版を検証する。旧仕様の「問題単位版なし」を現状の根拠にしない。

## P1：件数の技術的根拠と最小仕様

main `scripts/practice/adaptive.js:140–147`はdueReviews→additional→通常候補の順でoriginId重複を排除し、最後に`slice(0,p.count)`する。171行のラベルは結果長ではなく`prefs.count`。0件は151行で通知して開始しないが、171行の開始ボタン無効化条件はpracticeUnavailableだけ。候補0と利用不能は別状態である。

理科は`scripts/practice/science.js:28–36`で同じ種類の候補合流と上限処理、57行の表示はcount。理科設定は17行で5/10のみ。共通adaptiveは5/10/15。全教科へ15問を増やす仕様にしない。

トップ`index.html:1416–1421`は前回単元を読んで「今日の5問」と固定表示。内訳は`assets/progress.js:394–407`の読み取り専用projectionから来ており、設定数と候補数を加味する。`total`は教材全数なので日次件数として流用不可。生成元は`scripts/design/build_summary.py`。変更時は生成物だけ直接直さない。

最初の実装範囲候補：共通adaptive生成元と応仁・鎌倉・平安の3出力。`scripts/practice/embed.py`はmock-focusにも生成するため、生成器一括実行で意図せず4番目を変更しないか必ず確認する。mock-focusには教科別設定があり、全教科対応は別境界。理科・トップの共通名称調整は対象・受入条件を別途明示する。

最小表示案：入口名を「今日の練習」にし、選択上限とは別に実出題数を表示。候補不足は「今回は4問（設定は5問）」、0件は「この条件では候補がありません」と開始不可。利用不能は既存の保存/時刻の説明を優先。新しい問題数や選定法を追加しない。件数計算のための再抽選で出題順や乱数を余分に消費しない実装方針が必要。保存キー、問題ID、採点、期限到来→弱点→通常の順、JST日付、回答中の非再描画は維持する。

### 小さい合成試験（既存コード抽出、実装変更なし）

`/tmp/yuika-improvement-count-harness.js`をNodeで1回実行しexit 0。mainのdailyQuestions関数をそのまま抽出、周辺候補取得を合成stub、shuffleを恒等関数にした24ケース。選択5/10/15 × 一意候補0/1/4/5/9/10/14/15。due/weak/normalへ同一候補を重ねても結果は重複せず、`min(設定数,一意候補数)`件。例えば設定5・候補4→表示用設定値5/実結果4、設定10・候補0→表示用設定値10/実結果0を確認。

結果・抽出元commit・SHA256は`/tmp/yuika-improvement-count-results.json`。元ファイルSHA256 `aa82eca8636be227d3bcaf1f0004004d74b55ec8ec325e4cfd8300e74811eac9`。件数/重複の純粋ロジックだけを検証した。ブラウザー表示、実教材フィルタで候補不足へ到達する条件、storage、dueReviews/additional自体、理科、トップとの一致は実行未検証。したがって「実利用で再現済み不具合」とは報告しない。

## 次回の独立要件タスク（上限中も進められる）

P2「確認済み合成教材の試し解き」の採点・状態遷移契約を文書1件で確定する。対象は#11の現在revisionを明示確認したtext/choice。案内→確認→開始→回答→採点/解説→戻る→再編集で全確認失効、という状態表と、明示alias/readings・Unicode/空白/大小文字の許容範囲を10件程度の合成入出力表にする。読込confirmedだけでは開始不可、未解決画像は保留、全localStorage不変、再読込で試し解き回答消去を受入条件へ落とす。PdM作成→PrM範囲確認→独立QAで文書完了できる。実装・新製品PR・実教材取込は開始しない。この限定された未確定契約を次成果にすれば、同じPR待ちの無変更確認を繰り返さずに進められる。

3製品PR上限が継続する間、新規機能実装は停止。既存PRへの修正は親PrMが目的と最新mainとの統合範囲を確定してから。baseline上書き、rebase、close、merge、deploy、新PRは未実施。
