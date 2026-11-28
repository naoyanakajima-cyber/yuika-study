# 理科・トップの日次表示修正 Engineer

担当 engineer_daily_residual。基点55435567d44f05dc35f3ea6d73c4ba9cac2dc496、候補73fe2ee9d776b3e3360614752fb722ff4aee4f85。独立checkout /workspace/yuika-daily-science-20261114、製品は候補commit後freeze、pushなし。

## 実施

PdM /tmp/yuika-daily-residual-pdm.md とPrM確認の範囲で実装。修正前、空の新規Chromium 768×1024で実験器具をUI選択・10問をクリックし、開始前10問／開始後8問を実測。baseline.jsonとbefore-home/quiz.pngを保存した。実回答や教材写真は使用していない。

理科scienceDailySourcesへ既存due→weak→normal候補を共有、scienceDailyCountはid重複除去・count上限のみで乱数を使わない。scienceDailyは元のFisher-Yates・優先順・id重複除去・上限を維持。home/startの各呼出しでは同一events/nowを渡し、0件・blocked/dirty/未来時計の説明をボタン下へ示す。件数変更は抽選前に再表示し再確認を求める。既存?daily=1は初回で開始する。永続daily値、記録・問題・採点・親境界を変えていない。

トップは見出し・aria・4教材注記の固定名称を今日の復習へ変更し、集計/導線は同一。summary生成器とprogressのMODES表示のみ整合。理科生成時に共通adaptive由来の時計警告も前回の今日の復習へ整合した。理科のSCIENCE_ADAPTIVE block外はbyte一致。4教材HTML/adaptive.js/design.jsもbyte一致。

12ファイル変更。既存flash_grading/focus_practice/responsive_subjects/science_adaptiveの4試験はPrM確認済みで旧top exact名称だけを新名称へ変更。アサートの意味・exact条件を維持。新science_daily_count.pyをcheck_allへ加え全26suite構成。

## 検証と限界

- 新回帰 python tests/science_daily_count.py は初回終了0。旧scienceDailyを基点から抽出し、候補数0/1/4/5/8/9/20 × 上限5/10 × 利用可否の28合成オラクルでID順序・乱数消費・件数一致、表示乱数0を確認。
- 実UI：全5/5、全10/10、実験器具10→8/8、水溶液と溶解10→9/9。homeの追加乱数・回答保存なし。
- stale表示、blocked/dirty、合成の存在しない単元による0候補停止、直接?daily=1、通常/親モードのtop→理科8問開始を確認。0件は通常UIに存在する条件ではなく防御境界。非dailyの選定を検証済みとはしない。
- 公開React/Babelをcurlで読み取り、テストへ返した。その他httpsは遮断。全外部要求0とは主張しない。ページ例外0、実通知なし。
- science→summary→design→parent生成、git diff --check成功。static.jsonに6対象外ファイルと理科block外の保持を記録。
- 全check_all・独立UI/保存/未来時刻の最終受入はReviewer/QAへ委譲し、Engineerは今回実行していない。実機Safari/iPad・本人試用・学習効果・公開未検証。

依存は親から指定された検証済みvenvをsymlinkで手動再利用し、各shellでactivateした。自動snapshot引き継ぎ成功とは扱わない。新依存/設定変更なし。同じ原因の再試行なし。mainマージ・公開/デプロイ・実メール/Chat・課金・Secrets/権限/共有変更なし。
