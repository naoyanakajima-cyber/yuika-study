# Engineer — 日次件数の実UI調査

2026-11-14 18:11 UTC実行。cycle-20261114T180819Z。PrM確認済みA–Eの読み取り専用調査。

固定HEAD `86514eda054a5a2e09204df3a0668e40624c16de`。開始前・終了後とも `git status --porcelain` は空。製品、教材、既存テスト、boardは変更していない。独立QAが全22スイートを担当するため、本調査ではフルスイートを実行していない。

## 実UI結果

| Case | ページ／実際のUI設定 course・unit・variant | 候補 | 選択数 | 入口（正確な文言） | クリック直後 | 履歴 |
|---|---|---:|---:|---|---|---|
| A | onin-review.html / all・all・normal | 30 | 5 | 今日の5問をはじめる（今回は5問） | ← いったんおしまい / 1 / 5問 | 0→0 |
| B | onin-review.html / all・all・normal | 30 | 10 | 今日の5問をはじめる（今回は10問） | ← いったんおしまい / 1 / 10問 | 0→0 |
| C | onin-review.html / all・応仁の乱・kanji | 4 | 5 | 今日の5問をはじめる（今回は5問） | ← いったんおしまい / 1 / 4問 | 0→0 |
| D | onin-review.html / d2・将軍・normal | 0 | 5 | 今日の5問をはじめる（今回は5問） | この条件では候補がありません。（home維持、run=null） | 0→0 |
| E | heian-review.html / pairs・藤原氏と政治・normal | 2 | 10 | 今日の5問をはじめる（今回は10問） | ← いったんおしまい / 1 / 2問 | 0→0 |

全ケースで日次ボタンは `disabled=false`。各ケースを空の新規Chromium contextで実行し、選択はDOMの実在するselectと問題数ボタンだけを使った。開始は実際の `#daily-five` を各1回クリックし、画面の `1 / n問` と `run.qs.length` の一致を確認した。回答・採点・完了操作はしていない。全ケースで開始前後の履歴保存キーは `null`、メモリ内回答件数は0、run.resultsも0。UI操作によるpreferencesとlast-daily-unitの保存のみ発生。

Aは正常対照。Bは「今回は10問」と実10問が一致し、入口名「今日の5問」だけが不整合。C/Eは開始前に主張する「今回はn問」と実際の負担が一致しない実UI再現。Dは日次ボタンが有効に見えるが実行時に安全に拒否され、セッションは作られない。通常のチャレンジ開始ボタンは画像の通り無効。ゼロ問題セッションを開始したという結果ではない。

## 手順と有限探索

各ケースで localhost のページを開き、course→unit→variant→countをUI操作、開始前スナップショット、日次開始を1回、開始直後スナップショットと画像を採取。Cはぜんぶから／応仁の乱／漢字・正式名の確認／5問。Dは理由・比較（難度2）／将軍／通常練習／5問。Eはまぎらわしいペア／藤原氏と政治／通常練習／10問。

DOMで列挙された選択肢の組合せを順に選び、非乱数の `candidates('normal',prefs).length` を読み取った。応仁は70組合せまでで最初の不足・ゼロが得られた。平安は40組合せで不足が得られ、ゼロは観測しなかった。平安の漢字選択には画面側のコース自動変更があるため、探索ログscannedのcourseは操作要求値であり、その全組合せが同時状態として維持される証拠にはしない。正式ケースEのbefore.prefsは実際の状態を採取している。平安ゼロの不存在は主張しない。平安のDOM問題数選択肢は5/10、応仁は5/10/15で、UIに存在しない15を平安へ設定していない。

候補プール、QUESTIONS、prefsへの直接代入、関数差替え、時計・乱数シード固定はない。観測目的だけのdailyQuestions/scienceDaily呼出しはない。candidatesのnormal経路とgrouped/orderをソース確認し、RNGを使わないことを確認した上で読み取った。実開始後の抽選結果をそのまま記録し、再実行して良い結果を選んでいない。実行エラーは0で再試行0。

## 実測した隔離と通信

768×1024、system Chromium、fresh ephemeral context。localhost PreviewHandlerを127.0.0.1の空きportにbindし、CSP connect-src none/form-action noneを維持。全request routeで非ローカルとPOSTを遮断。サーバ受信GET 21件、非ローカルrequest遮断 7件、POST route遮断 0件、サーバPOST受信 0件、pageerror 0件。これは今回観測した件数であり、通知機能全経路の検証ではない。非ローカルrequestのURL内訳は採取していない。

runtimeは親エージェントが検証した既存.venvへの手動symlinkを利用し、実行shellでsource scripts/cloud/activate.sh。自動Install/Start成功とは主張しない。合成空履歴と静的公開教材だけを利用し、実ユーザー履歴・プロフィール・私的教材は未読。ブラウザーとpreviewサーバは終了済み。

## 根拠・成果物

- [生結果JSON](/tmp/yuika-daily-count-engineer/results.json)：before/after、実設定、DOM選択肢、出題ID、探索ログ、通信件数、HEAD。
- [実行ハーネス](/tmp/yuika-daily-count-engineer/probe.py)、[実行ログ](/tmp/yuika-daily-count-engineer/run.log)。
- 画像は768×1024のブラウザービューポートを直接保存。画像加工なし。C-before、D-after、E-afterを実際に開いて確認した。
- A：[開始前](/tmp/yuika-daily-count-engineer/A-before.png)／[設定](/tmp/yuika-daily-count-engineer/A-filters.png)／[開始直後](/tmp/yuika-daily-count-engineer/A-after.png)。
- B：[開始前](/tmp/yuika-daily-count-engineer/B-before.png)／[設定](/tmp/yuika-daily-count-engineer/B-filters.png)／[開始直後](/tmp/yuika-daily-count-engineer/B-after.png)。
- C：[開始前](/tmp/yuika-daily-count-engineer/C-before.png)／[設定](/tmp/yuika-daily-count-engineer/C-filters.png)／[開始直後](/tmp/yuika-daily-count-engineer/C-after.png)。
- D：[開始前](/tmp/yuika-daily-count-engineer/D-before.png)／[設定](/tmp/yuika-daily-count-engineer/D-filters.png)／[開始直後](/tmp/yuika-daily-count-engineer/D-after.png)。
- E：[開始前](/tmp/yuika-daily-count-engineer/E-before.png)／[設定](/tmp/yuika-daily-count-engineer/E-filters.png)／[開始直後](/tmp/yuika-daily-count-engineer/E-after.png)。

## ソースによる説明と未検証範囲

scripts/practice/adaptive.js:140–147の既存選定は期限到来→弱点→通常の重複排除をしてprefs.countで上限化する。空履歴のC/Eではフィルター後の通常候補だけなので4/2問となる。171行の入口文言は実候補数でなくprefs.countを使い、disabledはpracticeUnavailableだけを参照する。151行の空配列ガードはDの拒否と整合する。これは実測の説明であり、理科や重点復習に同じ実UI結果があると実証したものではない。

今回未検証：鎌倉の実UI、理科、重点復習、トップ入口、履歴あり・期限到来/弱点混在、親モード、保存拒否、複数タブ、時刻境界、採点→保存→再読込、Safari/WebKit/実iPad。追加の製品修正や新機能は未実装。次の仕様候補はPdM文書の「入口名と実件数の分離／0候補の事前説明／選定・履歴契約維持」を用い、PrMの別途実装範囲確定を待つ。
