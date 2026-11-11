# 開発タスク13：新しい環境でのWebKit導入（2026-11-11 21:41 JST）

対象: draft PR #22、`codex/ipad-webkit-tests`。開始HEAD: `5059049575348cea7f99aa096da4a7b534835f18`。
Debian GNU/Linux 13.6 / Python 3.12.14 / Playwright 1.62.0。
今回の実行環境では最新観測のネットワークポリシーがenforcedで、
`cdn.playwright.dev` と `playwright.download.prss.microsoft.com` が許可されていた。
環境の公開・設定変更は行っていない。

## 取得：成功（終了0）

通常ユーザーで以下を実行。`--with-deps`なし、root操作なし。
キャッシュとログは作業用ディレクトリに置き、Gitには含めない。

```bash
source scripts/cloud/activate.sh
export PLAYWRIGHT_BROWSERS_PATH=/workspace/work/playwright-browsers
.venv/bin/python -m playwright install webkit
```

`https://cdn.playwright.dev/dbazure/download/playwright/builds/webkit/2336/webkit-debian-13.zip`
からWebKit 26.5 / build 2336（95.6 MiB）を取得できた。
FFmpeg build 1011（2.3 MiB）も取得成功。
保存先は `/workspace/work/playwright-browsers/webkit-2336` と `ffmpeg-1011`。
今回は最初のCDNで成功し、Microsoft配布先へのフォールバックは発生しなかった。

## 起動：不足ライブラリで失敗（終了1）

同じactivate・キャッシュ指定で `.venv/bin/python scripts/cloud/check_webkit.py` を実行。
これはWebKitを起動してiPad (gen 7)相当のページに
`<title>webkit-ready</title>` を設定・確認する最小テスト。
`BrowserType.launch` のホスト依存検証で停止し、ページ作成には到達しなかった。
ダウンロード成功時の依存警告と起動エラーは、同じ6ライブラリを報告した。

| 不足共有ライブラリ | Debian 13のOSパッケージ |
| --- | --- |
| `libgtk-4.so.1` | `libgtk-4-1` |
| `libgraphene-1.0.so.0` | `libgraphene-1.0-0` |
| `libharfbuzz-icu.so.0` | `libharfbuzz-icu0` |
| `libmanette-0.2.so.0` | `libmanette-0.2-0` |
| `libhyphen.so.0` | `libhyphen0` |
| `libGLESv2.so.2` | `libgles2` |

一覧はPlaywrightのホスト依存検証による実測。パッケージ名はDebianの対応名で、
Graphene以外は固定Playwright内のlib2package対応表も確認した。
apt-cacheのローカル候補情報は空であり、導入後の起動成功は未確認。
配布バイナリへの単独lddでは同梱ライブラリの検索パスも必要になるため、
その未解決名を追加のOS不足として数えていない。

## root権限のInstall工程へ入れるコマンド（今回は未実行）

Debian 13のroot工程で不足6パッケージとその依存を導入する場合：

```bash
apt-get update
apt-get install -y --no-install-recommends \
  libgtk-4-1 libgraphene-1.0-0 libharfbuzz-icu0 \
  libmanette-0.2-0 libhyphen0 libgles2
```

Playwrightが定義するWebKit依存一式を導入する公式の代替手順は、
固定版venvを準備したリポジトリルートで、root工程から以下を実行すること：

```bash
.venv/bin/python -m playwright install-deps webkit
```

ブラウザー本体の取得とテストは通常ユーザーで行う。OS依存導入後は、上記と同じ
`PLAYWRIGHT_BROWSERS_PATH` を指定して最小起動、`python tests/ipad_webkit.py`、
`bash scripts/check_all.sh` の順に再検証する。

## テスト結果と作業範囲

ユーザー指定の「ライブラリ不足で起動できない場合」の終了条件に従い、
iPad相当24ケースと `scripts/check_all.sh` は今回は未実行。
過去の17 suite成功・Chromiumによる24ケース診断を今回の成功に流用しない。
アプリ不具合の確認なし、コード修正0回。変更はこの検証記録のみ。
`git diff --check` を確認。生ログは `/workspace/work/webkit-task13/` に保持。

PRはdraft維持。マージ・公開・デプロイ・実通知・課金・新Secrets・OSパッケージ導入なし。
