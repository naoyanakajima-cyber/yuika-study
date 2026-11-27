# 鎌倉テーマ試作とPR32算数教材の互換同期

THEME-MVP / 既存draft PR12。PdM pdm_theme_pr32 → PrM root/coordinator → Engineer engineer_theme_pr32 → 独立Reviewer/QA qa_theme_pr32。

旧PR12 `df7af2a205f44e8c76b50e96728685efcc7e57d8` と観測main `58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5` を専用topicへ競合なく統合。固定候補は `b4deb0df131b1280ab2cc0647851e1d345d06143`。mainへの変更ではない。

## 学習上の価値と保持

鎌倉画面で選んだ見た目と回答途中の学習状態を維持したまま、新しい算数24問・5段階を開ける組合せにする。鎌倉HTML、テーマ試験、共通デザイン、江戸/模試/親の生成修正は旧PR12とbyte一致。新算数HTMLと入口・preview・通知埋込はmainと一致。テーマの適用対象は鎌倉のみ。PR10/11の独自機能、新テーマ、全画面への展開は含まない。

## 検証

独立QAは固定HEADで旧29suiteとmain28suiteの厳密和集合30件を初回30/30 exit0、389秒で成功。開始・終了HEAD/clean一致、全100tracked bytes保持。通常/親のテーマ切替・記録隔離・算数往復、図contrast6.26572、独立math preview/CSPは初回成功。6合成画像をQA、2画像を統括が確認。結果は `ops/evidence/2026-11-27-theme-pr32/QA.md` と同ディレクトリに保存する。
Engineerの生成12段階×2、math24問/mock報告、preview/CSP初期確認はcommit前の焦点検証で、最終HEADの独立結果とは区別する。

## 制約と次の一手

既存クラウドvenvを手動利用。自動snapshot引き継ぎ成功とはしない。合成データ/mockのみ、実機Safari/WebKit/iPad・本人嗜好・学習効果・公開画面は未確認。Workers Buildsは独立QAと別扱い。新CEO返答取り込み0。
既存draft PR12を更新後、PR10/11/12の合成試用判断待ちを維持する。新差分・再現不具合・CEO試用所見がなければ同じ実装やQAを反復せず終了する。本番merge・公開・実通知なし。
