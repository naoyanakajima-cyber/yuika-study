# Codex Cloud 開発環境

ローカルPCを使わず、クラウド内でセットアップ・ブラウザーテスト・プレビューを行う。
環境設定の保存と、アプリの公開・本番デプロイは別の操作。本番マージ・実通知・
Secrets変更・課金変更はこの手順に含めない。

## 現在の到達点と証拠の限界（2026-11-06 JST）

保存済み環境を編集する正規ツール、新規Codex Cloudタスクを作成するツール、
Browserの操作ツールは、この検証セッションには提供されていない。
そのため保存・Publish/Republish・Only meの画面確認・別タスクの作成は未実施。
**以下のInstall/Startの実装と同一インスタンス内での再構築は、自動適用成功の証拠ではない。**

前回の新規環境では初期checkoutが `work` / `d526d65` で、setupファイルと
`.venv` がなかった。前回の手動補完後の成功と、今回の継続作業の結果を区別する。
今回の作業開始時は前回と同じ環境ID・元設定バージョンで、既存のPR #6のHEADと
`.venv` が残っていた。別の新規タスクとして数えない。

| 調査対象 | 今回取得した事実と判断できない点 |
| --- | --- |
| 実行先 | `provider=cloud`、状態running、観測は最新 |
| 実行中設定 | 元設定ID・バージョンIDを取得。値は非公開のチャットへ記録 |
| 選択した保存済み環境との対応 | UI上の選択・名称・共有範囲は取得できず、対応の完全確認は不可 |
| 公開済み版と編集中の下書き | 実行元バージョンIDは取得したが、現在の公開版・下書き本文との比較は不可 |
| 新規作成と再開 | 今回は同じ論理環境の継続利用。起動履歴や新規タスク作成APIはなし |
| Install未実行と途中失敗 | 保持診断は`history_status=not_found`、recordsは空。Install本文・実行ログ未取得なので断定不可 |
| Start未適用と一覧非表示 | 環境側スキル一覧は空だったが、一覧だけでは適用有無を断定不可 |

`spec_revision=1` は実行中設定の観測番号であり、「古い設定」という証拠ではない。
初期mainにない `scripts/cloud/setup.sh` を直接呼ぶ設定なら失敗する構造だが、
実際に保存されたInstall本文を取得できていないため、今回の障害原因とは断定しない。

## mainにセットアップファイルがなくても動く構成

Installは初期checkoutに依存しない全文スクリプトとして登録する。
`scripts/cloud/render_config.py` が、レビューした固定40桁commitから
`install.sh` と `start-skill.md` を生成する。未コミットの作業ファイルは使わない。

```bash
# この手順を含むレビュー済みブランチで実行し、表示したHEADを記録する。
git status --short --branch
git rev-parse HEAD
python scripts/cloud/render_config.py --revision "$(git rev-parse HEAD)" --output /workspace/work/yuika-cloud-config
```

- **Install script**：生成した `install.sh` の全文を貼る。初期mainのファイルは呼ばない。
- **Start skill**：生成した `start-skill.md` の全文を貼る。Installと同じ要求commitが入る。
- **利用範囲**：Only meを維持。保存・Publish/Republish後の設定ID・版・時刻を非公開で記録。
- **ネットワーク**：restricted / package_managers、`unpkg.com`、
  `fonts.googleapis.com`、`fonts.gstatic.com`。今回この既存許可を変更していない。
  通知APIの `*.workers.dev`、`api.resend.com`、Chat APIは追加しない。
- **Secrets・追加runtime variables・外部クラウドID**：通知用のものは登録しない。
  今回の実行環境ではこれらは空で、ネットワーク制限はenforcedだった。

Installが作る作業先は `/workspace/yuika-study-cloud`。
プラットフォームが配置した `/workspace/yuika-study` のbranch・HEAD・未コミット変更には
触れず、Gitで取得したリポジトリだけを使う。私的ファイルのディレクトリコピーはしない。

新規作成時は、専用の一時Gitディレクトリで固定commitをfetch・照合し、
detached HEADへcheckoutしてから専用作業先へ移す。可変ブランチの先端へは追従しない。
既存の作業先がある場合はorigin・clean状態・要求commitの祖先関係を確認する。
要求commitを含む既存topic branchはそのまま再利用し、setupだけ再実行する。
dirty、別リポジトリ、要求commitを含まないHEADなら変更せず停止する。
`reset`・`clean`・強制checkoutは行わない。更新時は新しい作業先を明示して検証する。

セットアップは再実行可能。初回は固定依存を新しい `.venv` に入れ、
`pip check` と768×1024のChromium実起動を行う。OSパッケージは追加せず、
Python・Node.js・システムChromiumが不足していれば該当工程で停止する。
標準Playwrightブラウザーのダウンロードには依存しない。

## ログ・成功記録と自動準備の判定

ログは `/workspace/work/yuika-cloud-logs/` のinstall/setup別ファイルへ保存する。
各工程の時刻、失敗stage、終了コードを記録し、コマンド全文や環境変数一覧は出力しない。
失敗した一時checkoutを自動削除しない。個人データをログへ追加しない。

成功時だけ次の記録を生成する。再setup前に以前の成功記録を失効させるため、
失敗した再実行を「前回成功済み」と誤認しない。

- `.venv/yuika-cloud-install.json`：要求commit、実HEAD、作業先、依存定義のhash、時刻、Installログ
- `.venv/yuika-cloud-setup.json`：実HEAD、依存定義のhash、Python・Playwright・Chromium版、時刻、setupログ

Startは、保存版の要求commitとInstall記録の一致、
`git merge-base --is-ancestor <要求commit> HEAD`、branch・変更状態を先に確認する。
既存作業branchを維持し、新しい作業でdetached HEADの場合だけ固有topic branchを作る。
ただし成功記録だけでは手動／自動を区別できない。新規タスクでは**手動setupの前に**
保存版ID・プラットフォームのInstall実行ログ・時刻と照合する。
取得できなければ自動準備は未確認とし、手動補完のコマンドと結果を別に記録する。

## 起動と全5テスト

```bash
cd /workspace/yuika-study-cloud
source scripts/cloud/activate.sh
python tests/onin_review.py
python tests/kamakura_review.py
python tests/cloud_preview.py
node --test notifications/test/worker.test.mjs
python notifications/test/browser.py
```

必ず同じシェルで有効化してから実行する。setupのexportが次のシェルへ持ち越されると
仮定しない。手動復旧が必要なら、branch・変更・取得元commitを確認したうえで
`bash scripts/cloud/setup.sh` を実行し、「手動準備」と記録する。

指定2単元のテストは768×1024で起動、15問の回答、14問正解の採点、15件の保存、
他単元記録の保持、再読込後の誤答表示、読み、保護者表を確認する。
iPad実機Safari/WebKitやホーム画面追加の検証ではない。
通知ブラウザーテストはPR #6の関数形式の待機を含む版を使用する。
CSPを緩めず、接続完了条件・assert・模擬APIは維持する。

ソケットやブラウザー起動が拒否された場合は、その実行ツールに正式に備わる権限機構だけを
使う。機能がなければ未検証として報告する。ネットワーク制限やTLS検証は回避しない。
失敗を隠すためのassert削除・skip・成功するまでの無根拠な再試行は行わない。

## プレビューとデータ保護

```bash
source scripts/cloud/activate.sh
python scripts/cloud/serve.py --port 8000
```

クラウド内のブラウザーで `http://127.0.0.1:8000/` を開く。停止はCtrl-C。
並行プレビューは別ポートを使う。127.0.0.1だけにbindし、5つの公開HTMLだけを配信する。
CSP `connect-src 'none'` と `form-action 'none'` で通知API・フォーム送信を遮断する。
安全性テストは非公開パス404、CSP違反、POST到達0件を確認する。

テストは新規ブラウザーコンテキスト、合成回答、架空宛先、模擬APIだけを使用する。
個人回答記録・教材写真・storage state・実ブラウザープロファイルは取り込まない。
`.venv`・キャッシュ・ログ・private-data・成果物はコミットしない。
`.gitignore`に頼らずステージするパスと差分を明示的に確認する。

## 今回の検証とPRの依存関係

PRの順序は、main → [PR #5](https://github.com/naoyanakajima-cyber/yuika-study/pull/5)
（環境基盤）→ [PR #6](https://github.com/naoyanakajima-cyber/yuika-study/pull/6)
（通知テスト待機）→ `codex/cloud-automatic-bootstrap`（この追加）。
この追加PRのbaseはPR #6のブランチとし、既存差分を重複させない。
すべてdraftで、環境利用のためにmainへマージする必要はない。

今回、合成Gitリポジトリによる `python tests/cloud_bootstrap.py` の12件が成功。
setupのないmain・元checkoutのdirty変更・既存topic branch・untrackedファイル・
想定外パス・固定SHA不正・fetch/setup失敗・成功後の再実行失敗を検証した。
設定と差分は、クラウド子エージェントの読み取り専用レビューも実施した。

今回の実コード検証commitは `931c5141225fa04233c0510a38d5b0ae4f6a3cba`。
2026-11-06 22:52〜22:57 JSTに、setupと`.venv`のない実際のmain相当checkout
（`d526d65`）を作り、そこから外部のInstall全文を手動実行した。
固定commitを実GitHubから取得し、別checkoutに新しい`.venv`を構築した。
元のmain・HEAD・clean状態は保持された。さらに専用checkoutにtopic branchを作って
Installを再実行し、branch・HEADを保持して成功した。

| 今回のコマンド・確認 | 結果 |
| --- | --- |
| Install → setup → pip check → Chromium実起動 | 成功。段階ログと2種類の成功記録を生成 |
| `python tests/onin_review.py` | 成功：all checks passed |
| `python tests/kamakura_review.py` | 成功：all checks passed |
| `python tests/cloud_preview.py` | 成功：非公開パス保護・API遮断 |
| `node --test notifications/test/worker.test.mjs` | 成功：9/9、skipなし、実API模擬 |
| `python notifications/test/browser.py` | 成功：接続・社会/理科/旧クイズ/カード・再送・重複防止・Workerスキーマ |
| `python tests/cloud_bootstrap.py` | 成功：12/12、合成ローカルGitのみ |

全5テストは再構築先の同じシェルでactivateしてから順番に実行した。
OS Debian 13.6、Python 3.12.14、Node.js 24.19.0、npm 11.9.0、
Playwright 1.62.0、Chromium 154.0.8037.57。
これは**同一インスタンス内の手動Install再構築**であり、保存済み環境からの
新規タスク自動適用成功ではない。過去の成功を今回の結果へ流用していない。

## 残る最少の管理操作

1. 対象の保存済み環境で、同じ固定commitから生成したInstall/Startの全文を登録する。
   Only meと既存の最小ネットワーク許可を確認し、保存・Publish/Republishする。
2. その環境を明示して新規タスクを開始し、手動補完前のInstall実行ログ・保存版ID・
   成功記録を確認する。全5テストと子エージェント実起動の結果まで確認する。

新規タスク作成機能がない今回のセッションでは、この2操作は代行できていない。
同一インスタンス内の別checkoutでの再構築を代替検証とし、その限界を維持する。
