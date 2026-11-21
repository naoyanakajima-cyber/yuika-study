# Engineer: 教材確認室の非同期JSON取込保護

候補: 62f34de238e9d1d62c796aac3a4b43418043d17f
基点: f1e84a7b998dfbcd71c6692974015bdd08e1877e
checkout: /workspace/yuika-content-trial-20261114
branch: codex/content-trial-20261114
2026-11-14 22:13 UTC 頃にcommitしclean freeze。以後変更停止、QA開始可能。

PdM /tmp/yuika-content-trial-pdm.md をPrM採択した範囲で実装。
- import世代と案作業世代を別に管理。編集・確認・出力・サンプル採用・案取消で後着取込を採用しない。
- 最新取込だけがpending/notice/input後始末を変更。新取込失敗時も旧取込を復活させない。
- 読込中表示 #import-status と明示取消 #cancel-import。空files changeでも取込取消。現在案保持、明示取消後は入力へfocus。
- 既存破棄確認、JSONschema/出典検査/確認リセット/CSPは維持。6既存学習HTMLはdiffなし。
- HTML固定SHAはscripts/parent/embed.py、tests/parent_mode.pyの2箇所だけ更新。親ガード条件は緩和していない。独立QAによるmemory-only再レビュー待ち。
- docs/product/content-import-guard-spec.md、README、tests/content_import_guard.py追加/更新。必須suiteは25件（新回帰登録）。試し解き本体は未実装。

## Engineer検証

合成データとfresh Chromium 768×1024、ループバックのみ。
- 修正前: deferred File.text＋実input選択→問題文編集→後着完了＋破棄確認承諾で編集値消失を再現。before.json/png。
- 修正後: 同じ手順でproposal/unsaved完全保持と再入力案内を観測。after.json/png。
- tests/content_import_guard.py PASS (exit0、初回): 編集/確認/出力/サンプル/取消、A/B両順、旧失敗、最新不正/読込失敗/サイズ超過、取消/空files、破棄拒否、通常入力、storageメソッド非書込/許可GET以外要求0/pageerror0。
- tests/content_review.py PASS (exit0、初回): C1-C11、external0、POST0、storage0。
- tests/content_guidance.py PASS (exit0、初回): 案内/keyboard/確認失効/外部storage副作用なし。
- git diff --check PASS。候補commit時git status --short空。
- 全25suiteはEngineer未実行、固定clean HEADで独立QAに引渡し。

## 証拠と制限

/tmp/yuika-content-import-engineer/{before.py,before.json,before.png,after.py,after.json,after.png,focused.log,content-review.log,content-guidance.log}
修正前harness初回はpage.evaluate末尾代入で返った関数をPlaywrightが呼び出し、deferred Promise待ちになった。harnessをvoid0終了へ修正し2回目に再現成功。製品失敗をpass扱いしていない。
既存検証済みvenv /workspace/yuika-pr26-fix-20261112/.venvを手動symlink再利用、自動snapshot引継ぎ成功とはしない。
OS速度による自然発生、native filepicker閉じ検出、Safari/WebKit/実iPadは未検証。native無change取消は明示取消で対応できるが自動検出保証なし。

push/PR/ops台帳/設定/通知/デプロイはEngineer未実施。次は独立QAの内容レビュー・25suite・追加競合分岐、その後PrMがlease再確認して既存PR11へ統合。
