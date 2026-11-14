# Reviewer/QA — 日次件数調査の独立検証

2026-11-14 UTC / cycle-20261114T180819Z。独立Reviewer/QA。製品未修正。

## 判定

**限定調査A–Eの証拠と修正要件案を受理する。製品修正の受入成功ではない。** Engineerのハーネス・生結果・ソースを読み、A/B/C/Eの開始前後画像とD拒否画像を実際に開いて照合した。独自の最小ハーネスでC/Dを各1回再現した。テスト失敗0、再試行0。製品コード・教材・生成物・既存テスト・台帳は編集せず、push・実通知・merge・公開を行っていない。

対象HEADは `86514eda054a5a2e09204df3a0668e40624c16de`。フルスイートと独立UIプローブの開始前・終了後ともclean。ソースSHA256は `qa/source-sha256.json` に記録。既存venvへの手動symlinkを使い各shellでactivateした。自動環境復元成功とは扱わない。

## 独立再現

18:17:20–18:17:23 UTC、Chromium、768×1024。各ケースで独立した空contextを新規作成し、初期storageKeys=[]、履歴0件・保存raw=nullを確認。course→unit→variant→5問を実UI操作し、日次ボタンを1回だけクリックした。

| ケース | 実UI設定 | 開始前 | 開始直後 |
| --- | --- | --- | --- |
| C | 応仁 / all・応仁の乱・kanji / 5問 | 「今日の5問をはじめる（今回は5問）」、有効。まだ答えていない問題4問、内部通常候補4 | 1 / 4問、run.qs.length=4、index=0、results=0 |
| D | 応仁 / d2・将軍・normal / 5問 | 同じ5問表示で有効。まだ答えていない問題0問、内部通常候補0。通常開始ボタンは無効 | 「この条件では候補がありません。」、screen=home、run=null |

両ケースで履歴は0→0、raw=null→null。設定操作によりpreferences/last-daily-unitの保存は発生しており、全storage無書込ではない。QAのC-count/C-after/D-count/D-after画像を実際に開いて確認した。

`assets/design.js` のunitHomeは通常練習card内のpを削除するため、旧「候補n問」ラベルは実画面に残らない。独立プローブで `.practice-card p` は0を確認した。候補数は非乱数の `candidates('normal',prefs).length` の読み取り値であり、画像中の「まだ答えていない問題」4/0は空履歴条件で対応する別の表示である。履歴ありでも両者が一致すると一般化しない。

QUESTIONS、候補プール、prefs、時計、RNG、選定関数の直接代入/差替えはない。日次抽選関数を観測目的で余分に呼んでいない。開始後runを読むだけで回答・採点・完了はしない。QAプローブはloopback以外と非GETを遮断し、公開Google Fonts CSS GETを2件遮断、server POST0件、pageerror0件。Engineerの非ローカル遮断7件はURL内訳未採取なので種類を推測しない。

## ソース・要件のレビュー

- `scripts/practice/adaptive.js:140–147` は期限到来→弱点→通常をoriginIdで重複除去し、選択上限でsliceする。151行は0件の開始拒否。171行はprefs.countの文言とpracticeUnavailableのみのdisabledで、C/D/Eの観測を説明する。
- Aは5→5、Bは「今回は10問」→実10で一致。Bの「今日の5問」という名前の不整合をC/Eの実数不一致と区別する。Eは平安pairs/藤原氏と政治/normalの10→2で、実UIの5/10のみを利用。平安の探索中の漢字選択はcourseをmemoryに変えるため、scannedの要求courseを同時到達状態の証拠にしない。正式Eのbefore.prefsは実状態として確認できる。
- `scripts/practice/embed.py` は応仁・鎌倉・平安・重点復習の4出力を持つ。理科は別実装。今回未観測画面へ実UI成功を拡張しない。
- `docs/product/daily-count-spec.md` の要件案をレビューし、条件1の「候補の実数」を、重複除去・選択上限適用後の「実際に開始する総数」へ修正するよう指摘。PrMの修正を読戻し確認した。候補30でも実5となるAを誤って30表示にする仕様を避ける。
- 追加された「今日の復習をはじめる（今回は4問）」と0件条件見直し案内の文言案を読戻し、CEO採用・製品反映未完了と明示した提案として受理した。
- 名称と今回総数、正常0候補と保存/読取停止、開始直前の状態変化、選定・ID・保存互換維持、4生成先と理科/トップの範囲確定を分離した要件案は妥当。旧PR10への単純投入・新製品PR追加・製品完成は承認しない。
- 運用checkoutにコピーされたEngineer成果物は/tmp原本とbyte一致を確認した。最終run/board更新・commit後のメタデータ確認は別途行う。

## 既存mainのベースライン

`source scripts/cloud/activate.sh` 後 `bash scripts/check_all.sh` を**1回のみ**実行。18:12:41–18:17:15 UTC、274秒、exit0、22/22スイート成功。既存テストは固定seed20261110や合成状態/模擬APIを用いる。これは上記UI再現の非乱数変更条件とは別の既存ベースラインである。既存テストの既知公開CDN GETはあり、全作業の外部通信ゼロとは主張しない。実通知は模擬APIのみ。

| Suite | Exit | 秒 |
| --- | ---: | ---: |
| tests/onin_review.py | 0 | 4 |
| tests/kamakura_review.py | 0 | 4 |
| tests/cloud_preview.py | 0 | 3 |
| notifications/test/worker.test.mjs | 0 | 0 |
| notifications/test/browser.py | 0 | 12 |
| tests/cloud_bootstrap.py | 0 | 2 |
| tests/adaptive_practice.py | 0 | 3 |
| tests/adaptive_daily.py | 0 | 4 |
| tests/adaptive_quality.py | 0 | 5 |
| tests/flash_grading.py | 0 | 9 |
| tests/spaced_daily.py | 0 | 6 |
| tests/history_compat.py | 0 | 4 |
| tests/science_adaptive.py | 0 | 8 |
| tests/registered_answers.py | 0 | 3 |
| tests/history_review_regression.py | 0 | 3 |
| tests/state_review_regression.py | 0 | 5 |
| tests/prototype_storage.py | 0 | 8 |
| tests/focus_data.py | 0 | 0 |
| tests/focus_practice.py | 0 | 14 |
| tests/parent_mode.py | 0 | 24 |
| tests/design_c.py | 0 | 23 |
| tests/responsive_subjects.py | 0 | 130 |

既存22スイートにはscience/focus/parent/history/timingの回帰があるが、未実装の日次件数修正の受入検証として流用しない。フルログは `qa-suite.log`、開始終了メタデータは `qa-suite-meta.json`、機械可読結果は `qa/suites.json`。

## 残る検証範囲

今回の件数問題について、鎌倉の実UI、理科、重点復習、トップ入口、履歴ありのdue/weak/normal混在、親モード、保存拒否/読取不能、別タブ更新、期限境界、回答→採点→保存→再読込、Safari/WebKit/実iPadは独立受入未実施。本人の使用感・学習効果も未検証。将来の実装設計と修正後QAに残す。製品は未修正のままで、今回の完成は調査文書と証拠のみ。
