# 教材確認試作と算数文章題練習の互換性確認

2026-11-27、Engineer `engineer_content_pr32` が、教材確認 PR #11 の
`feada5947b237310923f0aa1956487ac8af501af` に、main の
`58b6d9e0a8e2761e5c446a11ceafa1afb1e832a5`（PR #32 算数文章題練習）を
専用 checkout 内で取り込んだ。競合はなく、main 自体の変更や push は行っていない。

## 保持した動作

- 教材確認 HTML、合成入力 fixture・仕様、教材関連の 5 テスト、PR #11 の runtime を保持した。
  `content-review.html`、`scripts/practice/science.js`、`scripts/prototype/runtime.js`、
  `docs/product` 配下、教材関連 5 テストの計 18 ファイルは取り込み前と byte 一致した。
- テキスト・合成画像からの教材確認、JSON 入力ガード、非保存の試用、保護者画面の隔離は既存実装を維持した。
- 算数文章題 24 問・5 段階の練習とホームの 22 カード構成を取り込んだ。
- Cloud preview は教材確認と算数文章題の両 HTML を許可し、`connect-src 'none'` を維持した。
- PR #10 の復習推薦・日次件数は今回取り込んでいない。PR #11 の「今日の5問」は従来仕様のままとした。

## Engineer が実施した検証

取り込み内容を index に登録した、commit 前の checkout で以下を各 1 回実施し、すべて成功メッセージを確認した。
連続実行した shell 全体の終了コードは 0。個別コマンドの終了コードや所要時間の独立記録は採取していない。

- `python tests/generator_preservation.py`: 12 段階の生成処理を 2 巡し、追加した算数 HTML を含む全 tracked file の byte 保持と再生成の安定性を確認。
- `python tests/cloud_preview.py`: preview 起動、private path 保護、API 遮断を確認。
- `python tests/math_passage.py`: 全 24 問の答えを独立計算し、段階表示と mock report を確認。
- `scripts/check_all.sh` の suite 名を機械比較し、PR #11 の 33 件と main の 28 件の和集合と完全一致する 34 件であることを確認。欠落・余分な suite はない。
- `git diff --check`: 成功。

環境準備は既存 `/workspace/yuika-study/.venv/bin` をこの checkout の ignored `.venv/bin` へ手動 link した。
これは自動 snapshot 引き継ぎの成功を示すものではない。

## 独立 QA への引き継ぎ

Engineer は全 suite の再実行をしていない。独立 Reviewer/QA が、この記録を含む固定 commit に対し
`bash scripts/check_all.sh` の全 34 suite を一度実施し、対象 SHA と結果を別途記録する。
教材確認の通常・保護者隔離、合成テキスト・画像、JSON ガード、非保存試用、768×1024 表示、
算数の入口と mock 通知を確認対象にする。既存 PR #11 の過去の QA 結果は新 commit の検証結果として流用しない。

本記録は合成データと mock 通知による検証のみを扱う。実回答・教材写真、実通知送信、
実機 Safari/iPad、公開・デプロイは検証していない。CEO 判断待ちの扱いと公開可否は統括の台帳で管理する。
