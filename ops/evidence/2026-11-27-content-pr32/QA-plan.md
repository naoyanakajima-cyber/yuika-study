# PR11 / PR32 independent QA plan

Reviewer qa_content_pr32。Engineerとは独立。固定候補通知までは準備のみ。
PR11 feada5947b237310923f0aa1956487ac8af501af とmain58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5の厳密suite union34を固定clean detached checkoutで一回実行する。
差分・content本体/fixtures/runtime保持、新算数HTMLと34suite/CSP両preview経路・生成保持を直接確認。独立content probeは前回スクリプトを読み直して再実行し、768×1024の通常/実際の親セッションでtext/imageの確認→正誤試行→編集失効→JSON再入力失効→再確認→終了/pagehide消去と通常記録不変/POST0を確認する。旧結果は流用しない。
既存venv手動再利用。合成のみ、mockのみ。製品編集/pushなし。同原因試行2回まで。実機Safari・公開・本人試用・実配送は対象外。
