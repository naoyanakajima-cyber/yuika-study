# Codex Cloud 開発環境

ローカルPCのプロセス・Docker・トンネル・保存領域を使わず、クラウド内で
セットアップ、ブラウザーテスト、プレビュー、子エージェント作業を行う。
本番へのマージ、GitHub Pages公開、Workerデプロイ、実通知は含めない。

## 構成と確認日

2026-11-05（日本時間）に `main` の `d526d65` を基準に確認。
既存の README 2件、テスト4件、通知クライアントと依存関係を調査した。
既存の AGENTS.md、Python依存定義、package.json、CI定義はなかった。
HTMLは静的配信でき、Node.jsは通知Workerの単体テストに使う。
旧学習帳は unpkg.com の React / ReactDOM / Babel に依存する。

| 項目 | 検証した環境 |
| --- | --- |
| OS | Debian GNU/Linux 13.6 (trixie), x86_64 |
| Python | 3.12.14（管理イメージに導入済み） |
| Node.js / npm | 24.19.0 / 11.9.0（管理イメージに導入済み） |
| Python Playwright | 1.62.0（リポジトリ内 `.venv` にインストール） |
| Chromium | `/usr/bin/chromium`, 154.0.8037.57（管理イメージに導入済み） |
| Python依存 | `requirements-dev.txt` に間接依存を含めバージョン固定 |
| システムライブラリ | `ldd /usr/lib/chromium/chromium` で欠落なし、実ブラウザー起動も成功 |

Playwright標準のブラウザーキャッシュは未導入だった。
`python -m playwright install chromium --only-shell` は
`cdn.playwright.dev` に対するネットワークポリシーの403で失敗した。
ポリシーを回避せず、導入済みのシステム版Chromiumを使用する。
2本の既存テストは `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` を指定できるようにした。
未指定時は従来どおりPlaywright標準のブラウザーを使う。
検証条件、問題数、採点・保存・再読込のassert、HTTPS遮断は変更していない。
PlaywrightとシステムChromiumの組合せはここに記載した版で検証済みだが、
管理イメージ更新後も同じバイナリになる保証はないため、毎回起動確認する。

## 新規タスクでの再利用

保存済みCodex Cloud環境の `yuika-study` を選び、この変更を含むブランチを
チェックアウトする。draft PRをマージする必要はない。`main` のみでは
今回追加した手順はまだ使えない。新しいチャットの作成・常時起動は自動では行わない。

```bash
cd /workspace/yuika-study
bash scripts/cloud/setup.sh
source scripts/cloud/activate.sh
python tests/onin_review.py
python tests/kamakura_review.py
python tests/cloud_preview.py
node --test notifications/test/worker.test.mjs
python notifications/test/browser.py
```

`setup.sh` は仮想環境の作成、固定した依存の導入、`pip check`、
Chromiumの実起動を行う。再実行可能。新しいシェルでは毎回
`source scripts/cloud/activate.sh` を実行する。セットアップ時の `export` が
次のタスクに引き継がれるとは仮定しない。

この管理イメージにPython・Node.js・Chromiumとそのシステム依存が揃っていたため、
OSパッケージの追加インストールは不要だった。別のイメージを選ぶ場合は、
これらのランタイムとChromiumのシステム依存を備えたものを選ぶ。
不足時はセットアップを停止する。未検証のOSインストール手順を
「この環境で検証済み」として扱わない。

実行ツールのサンドボックスがローカルソケットを禁止している場合は、
サポートされた追加ネットワーク実行権限を付ける（今回の実行では
`sandbox_permissions=with_additional_permissions`, `network.enabled=true`）。
クラウド側の送信先制限は維持される。テストサーバーは127.0.0.1の動的ポートを使う。

## 保存済み環境設定へ登録する内容

**このセッションには保存済み環境設定を更新するツールがなく、管理画面への保存は未実施。**
以下の検証済み設定をリポジトリに保存している。クラウド環境の設定画面で
セットアップコマンド／指示として登録する場合の内容は次のとおり。
実行中環境の設定と、一覧に表示される保存済み環境のIDは異なるため、
同一の設定リビジョンへ反映済みとは扱わない。

| 設定 | 内容 |
| --- | --- |
| リポジトリ | `naoyanakajima-cyber/yuika-study` |
| 作業ディレクトリ | `/workspace/yuika-study`（新規環境で異なる場合は実際のcheckout先） |
| セットアップ | `bash scripts/cloud/setup.sh` |
| 各シェルの初期化 | `source scripts/cloud/activate.sh` |
| プレビュー起動 | `python scripts/cloud/serve.py --port 8000`（初期化後） |
| エージェント指示 | ルート `AGENTS.md` を読む |
| ランタイム | 上記のPython・Node.js・システムChromiumを備えた管理イメージ |
| ネットワーク | restricted / package_managers、`unpkg.com`, `fonts.googleapis.com`, `fonts.gstatic.com` |
| 通知用Secrets | **登録しない**（メール・Chat・Cloudflare・Resend認証不要） |

現在のネットワークポリシーは `enforced`、観測は最新で、通知用Secrets・
追加ランタイム変数・外部クラウドIDの設定はない。通知先の
`*.workers.dev` / `api.resend.com` やChat APIへの許可を追加しない。
セットアップが使うPyPIと既存アプリのCDNへのアクセスは許可されている。

## 起動・通知遮断・データ保護

```bash
source scripts/cloud/activate.sh
python scripts/cloud/serve.py --port 8000
```

クラウド内のブラウザーで `http://127.0.0.1:8000/` を開く。
対象単元は `/onin-review.html` と `/kamakura-review.html`。
停止は起動シェルでCtrl-C。別プロセスと並行する場合はポートを変える。
これは開発プレビューであり、常時稼働の本番サービスではない。

- プレビューは127.0.0.1だけにbindし、5つの公開HTML以外を配信しない。
- HTTPレスポンスのCSP `connect-src 'none'` でfetch/XHR/WebSocket/beacon等を
  遮断する。通知設定があってもAPI通信できない。フォーム送信も禁止する。
- 既存2テストは新規ブラウザーコンテキスト＋HTTPSルート遮断を使用する。
- 通知テストは架空の宛先と模擬APIのみ使用する。実メール・Chat送信は行わない。
- 実端末の回答記録、保留通知、browser storage state、教材写真を取り込まない。
  テスト中の回答は合成データで、ブラウザーコンテキストとともに破棄する。
- `.venv`、キャッシュ、private-data、ブラウザープロファイル、成果物ディレクトリは
  `.gitignore` で除外する。ただし、除外設定だけで個人情報の混入は防げないため、
  ステージするファイルを明示し差分を確認する。

## 複数エージェントとGitHub

このクラウド実行環境で子エージェント `cloud_agent_probe` を実際に起動し、
`pwd`、`git rev-parse --show-toplevel`、`git status --short` を実行できた。
親と同じ `/workspace/yuika-study` を参照する。ファイルを共有するため、
書き込み担当を分け、セットアップ・コミットは1エージェントが担当する。
別タスクの同時開発は別checkout・別ブランチを使う。
子エージェント機能の提供はタスクごとに確認する。

GitHubコネクターでリポジトリ読取に成功し、認証ユーザーの
`pull/push/admin` と collaborator permission `admin` を確認した。
クラウドシェルでも `git ls-remote origin HEAD` に成功した。
アカウント権限だけでは全APIの成功は保証できないため、実変更を含むdraft PRの
作成結果で書き込み能力を確認する。権限確認だけの空PRは作らない。

## 検証記録

| コマンド・操作 | 結果 |
| --- | --- |
| `python tests/onin_review.py` | 成功：all checks passed |
| `python tests/kamakura_review.py` | 成功：all checks passed |
| `node --test notifications/test/worker.test.mjs` | 成功：9/9（実APIは模擬） |
| `python notifications/test/browser.py` | 成功：接続、社会・理科・旧クイズ・暗記カード、再送、重複防止、Workerスキーマ |
| `python tests/cloud_preview.py` | 成功：768×1024で起動、非公開パス404、CSP違反を観測しPOST到達0件 |
| `bash scripts/cloud/setup.sh` | 成功：依存導入、pip check、Chromium実起動 |
| 空のcheckout・`.venv`から再構築 | 成功：固定依存を再インストールし、指定2テストとプレビュー安全性テストを実行 |
| `python scripts/cloud/serve.py --port 8000` | 起動成功 |
| `bash -n scripts/cloud/setup.sh scripts/cloud/activate.sh` | 成功 |
| `python -m compileall -q tests scripts/cloud` | 成功 |
| `git diff --check` | 成功 |

指定の2本は768×1024で、起動・15問への回答・14問正解の採点・15件の保存・
他単元の記録保持・再読込後の誤答表示・読みの確認・保護者表を検証する。
Chromiumでの画面幅検証であり、iPad実機Safari/WebKitやホーム画面追加の検証ではない。

初回の失敗は(1)実行サンドボックスのソケット禁止、(2)Playwright専用ブラウザー不在。
追加実行権限とシステムChromium指定で解消した。専用ブラウザーのCDN403は残るが、
検証済み手順はそのダウンロードに依存しない。
残る管理作業は、保存済み環境設定へのコマンド登録と、別の新規クラウドタスクでの
設定適用確認。ローカルPCの起動を前提とする手順はない。
空のcheckoutでの再構築は同じクラウドインスタンス内の一時ディレクトリで実施した。
新規クラウドタスクへの設定適用確認とは区別する。
