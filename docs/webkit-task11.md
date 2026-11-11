# 開発タスク11：WebKit再実行（2026-11-11 JST）

対象: draft PR #22、`codex/ipad-webkit-tests`、検証コード `aaa7488d766955353f3ff5314d3361fba7fbcd91`。

## 導入結果

Playwright 1.62.0の公式コマンド `python -m playwright install webkit` は終了1。
WebKit 26.5 / build 2336の以下のURLがすべてHTTP 403、本文 `Domain forbidden` で拒否された。

- ホスト `cdn.playwright.dev`:
  - https://cdn.playwright.dev/dbazure/download/playwright/builds/webkit/2336/webkit-debian-13.zip
  - https://cdn.playwright.dev/builds/webkit/2336/webkit-debian-13.zip
- ホスト `playwright.download.prss.microsoft.com`:
  - https://playwright.download.prss.microsoft.com/dbazure/download/playwright/builds/webkit/2336/webkit-debian-13.zip

インストーラー自身の配布先切替・再試行後も失敗。別ブラウザー、別ミラー、TLS無効化には切り替えていない。
環境statusは最新観測、network policyはenforcedだったが、effective allowlistにも起動時の
`/etc/codex/network-policy.json`にも上記2ホストがなかった。ユーザーの公開操作の成否は断定せず、
このタスクに選択された実行環境へ許可が反映されていない事実として記録する。

OS依存は `python -m playwright install-deps webkit` を正式な昇格機構で実行したが、
rootへの切替で認証を要求され `su: Authentication failure`、終了1。
`cloud-agent-packages` と `sudo` は利用できなかった。パスワードや新Secretsは追加していない。
共有ライブラリの導入完了は未確認。

## 不具合と修正

アプリの不具合は今回未確認。ネットワークとOS権限が実行前のブロッカーであり、
原因のないコード変更やテスト弱体化は行っていない。この追加コミットは再実行の証拠を保存する。

## 検証結果

`python tests/ipad_webkit.py` はWebKit実行ファイル未導入で終了1。
24ケースは開始できず、成功件数は0。過去のChromium診断をWebKit成功として扱わない。

`bash scripts/check_all.sh` は53秒、全体終了1。既存17 suiteはすべて終了0、
追加WebKit suiteのみ終了1。Workerは9/9、bootstrapは13/13成功。

## 残る限界と再開条件

このタスクで実際に使う公開済み環境に2ホストを適用し、OS依存を導入可能にしたうえで、
WebKit導入、`python tests/ipad_webkit.py`、`bash scripts/check_all.sh` を再実行する必要がある。
WebKitの24ケースおよび全体チェック全成功の完了条件は未達。
実行可能になってもLinux WebKitのiPadエミュレーションであり、実機Safari・日本語IME・
ホーム画面起動等の検証とは区別する。

合成データとローカルCSPプレビューのみ使用。Cloudflareプレビュー失敗は既知の対象外。
mainマージ・公開・デプロイ・実通知・課金・Secrets変更は行っていない。
