# THEME-MVP 現main互換性 Engineer報告

担当: engineer_theme_compatibility。PrM採択済みC1〜C8を実装。最終候補 **c81fb6b3a7e9c5c6c5d42431afe1d13a73c780d3**、確認時刻 2026-11-15T00:11:24.989960+00:00、working tree clean。独立checkout `/workspace/yuika-theme-compatibility-20261115` / `codex/theme-compatibility-20261115`。push・本番merge・公開・実送信・Secrets等の変更なし。子起動なし。

## 基点と差分

既存PR12 HEAD57171adを第一親、観測main86514edを第二親に持つtopic merge。README/鎌倉HTMLの競合はmainを維持してテーマ追加部分だけを移植。main更新ではない。PR10/11/22の未merge差分は含めない。mainとの差分は5ファイル: README.md、docs/product/theme-spec.md、kamakura-review.html、scripts/check_all.sh、tests/theme_review.py。

テーマIIFEの読書きをwindow.YuikaParent.storageへ変更し、通常/親セッション/既存一時メモリを使用。直接localStorage fallbackなし。鎌倉限定でDesign Cのbg/subject/subject-text/radius等を設定し、見出しの白文字、必要surface・境界をCSSに適合。標準選択時の共通assetは変更しない。printは白背景と濃色へ。main外のUI、同一学習DOMを保つ操作を維持。

既存学習scriptの `<script>'use strict';` 以降はmainとbyte一致。parent/reports block、CSP、共有design.css/js、親runtime/embed、通知client、他5HTMLもbyte一致。static-result.jsonにassert結果。問題/採点/選定/保存schema・通知・共有デザインの改造なし。

## 手動準備

main requirementsと既存検証済みvenvの依存一覧一致を確認した前提で `/workspace/yuika-pr26-fix-20261112/.venv` を手動再利用。独立checkout内の無追跡.venv directoryにbin/lib/include/pyvenv.cfgのsymlinkを置いた。.venv自体のsymlinkはignoreされなかったためdirectory構成へ変更し、最終cleanを確認。各shellでactivate。自動snapshot引継ぎ成功とは報告しない。

## 実施した試験・2試行上限

`tests/theme_review.py` は旧通常保存キーを現prototype隔離キーへ、親入口を実footerリンクへ、15問選択を明示する現UIへ変更。共有デザインの既存public font GETは遮断して別計数し、それ以外の外部要求を失敗扱い。テーマ操作中のrequest/通知0assertと既存同一run/DOM/他保存不変assertを維持。テーマを必須check_allへ1回登録（main22suite+theme=23）。

- focused attempt1: exit1。15問入力/選択/ヒント/採点の各切替・状態/保存不変、色/キーボード/領域、実parent/records/home入口までは通過。JSON出力を旧直下eventsで読んでKeyError。現mainはenvelope/payload形式であり、製品不具合とは判断しない。
- focused attempt2: exit1。payloadへ適合したが、Engineerがformatを誤って `yuika-study-prototype-records` と記述したためassert失敗。実main定数は `yuika-review-prototype`。2試行後、実定数を読み正しく修正して保存した。**同原因上限を守り3回目は実行しない。最終format/payload assertは未実行。全theme検証成功ではない。**
- 未到達だった親/一時メモリ/printだけを扱う新しい独立focused probeを1回実行しexit0。export経路は呼ばず、失敗原因の再試行ではない。通常localStorage不変、親セッション内復元/終了時通常テーマ復元、sessionStorage拒否時メモリ適用と再読込消去、print UI非表示/白背景/濃文字/保存値維持を確認。`parent-print-probe.py` とlogに保存。
- 最終tests/theme_review.pyのpy_compileとgit diff --checkは成功。static比較assert成功。

試験は候補編集中の合成Chromium768×1024で実行し、最終固定HEADの独立QAではない。theme全体の後半（未知値/read-write障害/回復/他画面往復/最終外部要求集計等）は未到達。必須 `scripts/check_all.sh` はこのEngineer作業では未実行。PrM指示によりこのサイクルで同原因のtheme/fullsuite再実行は行わず、候補を未検証として保存・次runへ引継ぐ。実機Safari/iPad、本人嗜好、学習効果、ネイティブzoom、公開動作は未確認。

## 次の一手

独立QAは静的差分と今回未試行の境界だけを確認し、受入未完を維持する。次の許可されたサイクルで固定HEADから修正済みtheme検証と全必須23suiteを実行し、失敗を診断して証拠保存する。既存draft PR12を維持、新PRなし。D05方向性採用はmerge/公開承認ではない。
