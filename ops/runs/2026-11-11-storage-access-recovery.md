# REV-STORAGE-RECOVERY: 理科の一時的な保存領域拒否からの復旧

run `cycle-20261110T1606Z`、2026-11-11 01:06 JST開始。
provider=cloud/running/connected/current observationsを確認。
正本 `0ca72a4b5b1e9aac8831d7ef8a20496e5189abac` の4文書を同一commitから取得。
既存PR #4〜#20を照合し、前回からの製品HEAD変更・新規PRなし。
通常pushでlease取得後、前回の未完了 `REV-STORAGE-RECOVERY` を進めた。

## 学習上の目的と対象

一時的な保存領域の読取拒否が解消した後、理科の「ブラウザーへの保存を再試行」から
未保存回答を失わず復旧できるようにする。元の保存先に既にある回答も保持する。
新規製品PRを作らず、既存draft #20の品質修正に限定。
基点 `408805b06092b9eec5971426a8a1c2cb45194620`。
独立checkout `/workspace/yuika-science-storage-recovery-20261111`。

PdM `pdm_storage_recovery` がコードと前回の独立再現を確認し、PrMが次を承認。

- S1: 読取拒否と既知破損raw（空文字を含む）を区別。破損rawは上書きしない。
- S2: 再試行時の最新diskを全検証して未保存回答と結合。重複排除し、旧集計・問題版を保持。
- S3: setItem成功後にだけstate/blocked/dirtyを確定し、保存成功表示と分析の復帰を確認。
- S4: 拒否継続・容量不足・不正raw・ID衝突ではdiskと未保存回答を保持し、JSON保全導線を残す。
- S5: 768×1024の合成コンテキストで実retryボタン→保存→再読込。旧KEY・他単元は不変。
- S6: 採点・選定・通知・既混在raw移行・自動再試行は変更しない。

Engineer `engineer_storage_recovery` が製品を担当し、別のReviewer/QA
`qa_storage_recovery` が最終SHAを検証する。子はこの3名、実装は1件、子pushなし。
既存クラウドvenvを無視対象 `.venv/bin` から参照して明示activate。
依存インストール・手動setup・公開環境設定変更なし。自動引継ぎの成功とは扱わない。

## 完了時の証拠

最終製品HEAD **`79d546891940b6f5e3030940f7c52c2ff7b3d36b`**。
製品差分は理科HTMLのpersist 2行、保存手順1行、既存science_adaptiveの回帰ケース追加。
Engineerの重点 `science_adaptive.py` と `prototype_storage.py` は初回終了0。

独立QA `qa_storage_recovery` が同じ最終SHAで以下を初回成功：

- `bash scripts/check_all.sh` 全17suite・終了0・108秒。Worker9/9、bootstrap13/13。
- `source scripts/cloud/activate.sh` 後の独立 `probe.py` は終了0。
  旧baseでの障害再現1ケース＋修正版の8ケースを確認。
- 実回答→記録画面→retryで未読disk・後から追加された回答・pendingの3件と旧集計/問題版を保持。
  実JSONダウンロードと再読込後の完全一致、再retryの重複なしを確認。
- 読取拒否継続、容量不足、空/不正raw/未知schema、既知破損raw保護継続、ID衝突で原データを保持。
  旧baseでは同じ実UI経路で復旧不可、修正版は復旧成功。旧版比較の終了0は障害再現成功を示す。
- 新規768×1024コンテキスト、合成データ、CSP維持。独立probeのPOST試行/到達・外部request・pageerrorは0。
  通知suiteは模擬APIのみ。既存assert/採点/通知/教材archiveを維持。
- 生成後も最終HEAD不変・作業ツリーclean、`git diff --check`成功。

[独立QA報告](../evidence/2026-11-11-storage-access-recovery/QA.md)、
[全suiteログ](../evidence/2026-11-11-storage-access-recovery/check_all.log)、
[再現probe](../evidence/2026-11-11-storage-access-recovery/probe.py)、
[比較結果](../evidence/2026-11-11-storage-access-recovery/probe-result.json)を保存。
QA報告SHA256 `f60432f83b5d2aa449bb57b20f681bea3af6336374110b5dfd729c7fd240d805`。
probeはこのrunのクラウド内ROOT/OUTを使うため、別のクラウド環境では同じSHAを取得してパスを合わせる。
合成画面はクラウド内 `/workspace/work/storage-recovery-qa-20261111/recovered-science-home.png`、QAが実閲覧済み。

統括がremote lease/期限・PR20の基点HEAD・候補cleanを再確認して通常push。
[draft PR #20](https://github.com/naoyanakajima-cyber/yuika-study/pull/20)のreadbackで
HEAD一致・open/draft・未マージを確認。新規PRは作成しない。

## 残る条件と次の行動

この既存障害はdraftで修正・独立QA済み。公開アプリへ反映されたとは扱わない。
複数タブのlocalStorage読取/結合/書込は原子的ではなく、既存の1タブ推奨を維持する。
Safari/iPad実機、CEO本人の試用、学習効果、既に混在した旧rawの修復は未検証。
次は朝夕チェックで既存試作品と追加系列の採用整理、具体的な操作フィードバックを確認する。
新しい根拠や独立した作業がなければ、同じテストの反復や追加機能の作成をせず終了する。

製品待ち#10/#11/#12の3件と、未採用追加draft #14〜#20の7件を引き続き明示する。
既存修正を新たな採用や追加待ち枠とは扱わない。CEOの新しい返答は取り込んでいない。
本番マージ・公開・デプロイ・実通知・私的データ接続・課金・Secrets/権限変更なし。
