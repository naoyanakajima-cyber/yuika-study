# THEME-MVP 現main互換性のPdM範囲提案

担当: pdm_theme_compatibility。cycle-20261115T000247Z。読み取り調査のみ。製品編集・ブラウザー試験・push・本番操作なし。

## 推奨

既存PR12を現mainへ同期し、テーマ機能を現行の保存隔離・親確認モード・共通デザインCに適合させる。新しいテーマや画面を増やさず、標準/鎌倉の2選択と現在の学習状態を保つ。目的は、最新の苦手復習や安全な合成試用を失わずに、好みの見た目で学習を始められる同一候補へ進めること。既存PR12内で完結し、新規製品PRを増やさない。

根拠は静的比較。PR12 `57171ad9cab02fec6a080ecbe317fe11d3f51dcf` は `edad8065c1f2b726e61c5cf405f8d9ff6d807480` に対する4ファイル差分（README、theme-spec、kamakura-review、theme_review）。現main `86514eda054a5a2e09204df3a0668e40624c16de` には69ファイルの追加/変更があり、鎌倉の保存隔離、YuikaParent境界、Design Cなどが存在する。過去57171adの成功を同期後候補の成功には使えない。

観測した差異:

- 旧theme IIFEは `localStorage.getItem/setItem` を直接呼ぶ。現mainのAGENTSは全アプリ保存に `window.YuikaParent.storage` を指定し、親モードはsessionStorage/一時メモリへ分離する。単純なテーマ差分追加ではこの境界を利用しない。
- 現mainは `assets/design.css` を旧inline styleの後に読み、背景やbutton等に `!important`、`--bg/--subject/--subject-text/--hero-ink` を使用する。旧テーマのpaper/green等だけで意図する配色が適用されるとは未検証。Design Cの標準表示は維持し、鎌倉選択時だけ必要な変数と限定CSSを適合させる。
- 現mainのDesign Cは保護者入口をfooterへ移す。古いテストの入口操作や旧学習保存キー期待値は、そのままでは現mainの操作/隔離仕様と一致しない可能性がある。学習機能を旧状態へ戻してテストを通さない。

上記は静的な非互換候補で、ユーザー操作の不具合を再現したとの主張ではない。Engineerは独立checkoutで同期差分を確認し、必要な変更だけ行う。

## 最小受入条件（既存T1〜T11を維持）

- C1: 既存PR12履歴を保持するtopic候補へ現mainを取り込み、mainを変更しない。mainとの差分は鎌倉テーマのUI/CSS/保存アダプタ、テーマ検証、必須suite登録、仕様/READMEの整合に限定。PR10/11やPR22の未マージ差分は取り込まない。
- C2: 標準は現mainのDesign Cを維持し、鎌倉は読める配色の違いが実computed styleで確認できる。main外の選択UI、aria-pressed/選択表示、キーボード、44px領域、8px間隔、標準復帰、printの白背景と濃文字を維持。共有design assetを他画面へ影響する形で変えない。
- C3: 通常モードでは既存テーマキー `yuika-ui-theme-kamakura-v1` / standard|kamakura を維持。初回/未知値の自動上書きなし、get失敗は標準、set失敗は画面内反映+専用status、回復成功でstatus解消。学習のnotice/blockedを変更しない。
- C4: themeの読書きは現mainのYuikaParent.storageを使用。親モードで通常localStorageのテーマ・学習履歴・他単元・通知設定を変更しない。親モードのセッション設定はそのモード内で復元し、終了後に通常値へ戻る。sessionStorage拒否時の既存一時メモリ境界でも通常領域にfallbackしない。現mainの親バナー/終了操作/通知抑止を保持。
- C5: 同じrunの入力中/選択/ヒント/採点後/結果で切替前後のrun ID、問題ID列、index/results、入力、学習DOM、採点、記録が不変。テーマ操作でrender/go/save/通知を呼ばず、テーマ以外の保存領域が不変。元記録と試作記録の隔離キー・schemaを維持。
- C6: 合成データのみで768x1024のhome/quiz/feedback/result/parent/recordsを確認。親入口は現UI経由。通常/親モード、未知値/保存例外の境界を分けて試す。可読性・長文/図・overflow/focus、文字4.5:1と必要UI3:1を実際の色で確認。CSS幅/DPRを実機zoomとは呼ばない。
- C7: `tests/theme_review.py` を現mainのfixture/入口/保存境界へ適合し、既存意味あるassertを弱めない。`scripts/check_all.sh` に登録し、固定候補HEADで全必須suiteを独立QAが実行。対象外HTML、既存問題/採点/選定/保存schema、親runtime・通知block・CSP等をmainと比較し、テーマ以外の退行を拒否。
- C8: 最終HEAD・独立担当・各試験結果/限界をPR12と台帳へ保存。新CEO返答0、D05方向性採用とmerge/公開承認を分ける。実Safari/iPad、本人の好み/学習効果、実データは未検証と明記。

## 対象外と停止条件

全画面テーマ展開、テーマ追加、固定sticky UI、キャラクター/外部画像、フォント変更、質問/正解変更、採点/選定/保存migration、親runtime改造、実保存先接続、通知設定、CI/deploy設定は対象外。本番merge/公開/実通知・課金・Secrets/共有変更は禁止。新PR作成なし。必要な変更がこの範囲を超える、同期で安全境界が不明、同原因2試行でも解決しない、時間内に固定HEAD独立QAを完了できない場合は未完候補と具体的再開手順を保存し、成功としない。

新たなCEO承認要求は不要。既存D05と今回の自律範囲内の互換性修正としてPrMが確認後に進める。本人試用・採用/公開判断は別途維持する。
