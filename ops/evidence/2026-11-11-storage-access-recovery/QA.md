# REV-STORAGE-RECOVERY 独立QA

Reviewer: `/root/qa_storage_recovery`（実装者とは別）。2026-11-11 01:12〜01:15 JSTに確認。
製品HEAD: `79d546891940b6f5e3030940f7c52c2ff7b3d36b`。
基点: `408805b06092b9eec5971426a8a1c2cb45194620`（既存draft PR #20）。
対象checkout: `/workspace/yuika-science-storage-recovery-20261111`。
QAは製品ファイル・台帳を編集せず、commit/push/外部投稿をしていない。

判定: **今回の一時的な理科storage読取拒否からの保存復旧について、S1〜S6を満たす。**
旧版の同じ実UI経路では復旧不可を再現し、候補では現在diskと未保存回答を保持して復旧した。
製品採用・本番承認・公開・既混在rawの修復・実機検証の完了を意味しない。

## 実行結果

- `bash scripts/check_all.sh`: 初回終了コード0、17/17suite、108秒。Worker 9/9、bootstrap 13/13。
  既存16suiteとprototype_storageを、凍結した最終HEADで全実行。追加のstorage回帰は既存science_adaptive内に含む。
- `source scripts/cloud/activate.sh` 後、`python /workspace/work/storage-recovery-qa-20261111/probe.py`:
  初回終了コード0。旧baseの不具合比較1ケースと候補8ケースを独立実行。
- 検証後HEADは同じ、`git status --short`は空、`git diff --check`終了0。
  必須suite内の生成確認後も製品差分は発生していない。
- 全ケースは新規768×1024 Chromiumコンテキスト、合成データ、loopback preview。
  PreviewHandlerのCSPを維持し、独立probeでは外部request・POST試行・POST到達・pageerrorはいずれも0。
  通知suiteは既存の模擬APIのみ。実通知を発生させていない。

## S1〜S6の確認

| 条件 | 独立した確認 |
| --- | --- |
| S1: 一時読取拒否と既知破損rawを区別 | 初期getItem拒否ではblocked=true/rawBroken=null。既知破損raw（空文字を含む）は、diskを有効JSONに置換後もretryで解除せず原文をダウンロードできた。 |
| S2: 最新diskと未保存回答の結合 | 初期diskの1回答/旧集計を読み取れない状態で実UIから回答。アクセス復旧前にdiskへ別回答を追加し、実retryで3回答をフィールド単位で完全一致させた。questionVersionと旧集計も保持。再retryで重複なし。 |
| S3: 成功後だけstate/flags確定 | 書込quota中は元disk・pending回答・blocked/dirtyを保持。setItem成功後だけblocked/dirtyがfalseとなり、実JSON書出し内容と再読込後stateが保存済み状態と完全一致。ホームの回答数と今日の5問への復帰を確認。 |
| S4: 失敗時保護 | 読取拒否継続、復旧後quota、空文字/不正JSON/不正schemaVersion、同じ回答IDの内容衝突でdiskとpendingが不変。保存成功メッセージを出さないことを実DOMで確認。 |
| S5: 実画面経路と他領域保持 | #start→数値入力または選択肢→#check→記録の引きつぎ→#retryを実操作。旧理科詳細/旧集計/社会別単元/旧前回単元のsentinelは不変。実ダウンロードとreloadも成功。 |
| S6: 範囲維持 | 差分はscienceのpersist2行、案内1行、science_adaptive回帰追加。保存キー・採点・選定・通知・教材archive・移行処理は変更していない。既存assertの削除/skip/弱体化なし。自動再試行タイマー等の追加なし。 |

## 比較の意味

旧base `408805b` のHTMLを同じCSP付きloopbackに配信し、初期読取拒否→実回答→アクセス復旧→
実retryでblocked=trueのままになることと、disk/pendingが保持されることを再現した。
これは旧版の成功ではなく、修正対象の再現証拠。候補側では同じ経路から成功する。

記録に既知の破損がある場合、保存先が別処理で有効に置換されても、この修正は保護を自動解除しない。
現存データを黙って移行・上書きする処理は追加していない。
localStorageの複数タブ間のread/modify/writeが原子的になったとは主張しない。既存の1タブ推奨は維持。

## 証拠

- `check_all.log`: SHA256 `d09fac753be36971b0c3aea08d9d3574e68355d6e623ce49c607341bcd5a3dc0`
- `probe-result.json`: SHA256 `2c87739145d42689a2a46d7622045fb60d3d2b044c754f8cacde4c18f7368f23`
- `probe.py`: SHA256 `ddf8c910d7ea90406e5d8dc8f6cdc5d49cb2167e86d372e15b3811667d8d53d1`
- `recovered-science-home.png`: SHA256 `bc4f6b4bef0f86bb63f52ed4a722b12610de036e04b847fa203ce9210ecfea1a`

画面PNGはQAが実際に閲覧した。合成3回答と復習案内が表示され、試作と旧記録の区別も維持されている。
probeのROOT/OUTはこのrunのクラウド内パスを固定している。別のクラウド環境での再現は、
同じ対象SHA/旧baseを取得し、ROOT/OUTをそのcheckoutと出力先へ合わせる。

## 制約

Safari/iPad実機、実回答・教材写真、私的Evernote/メール/Drive、CEO本人の試用、学習効果は未検証。
旧混在rawの復旧と製品PR群の採用整理は別課題。既存クラウドvenvを利用し、自動準備成功とは扱わない。
本番マージ・公開・デプロイ・実送信・課金・Secrets・権限変更は行っていない。
