# REV-RECONCILE: 復習PRの照合と独立QA

run `cycle-20261110T1306Z`。2026-11-10 22:06 JST開始。
クラウドprovider/running/接続/最新観測を確認し、正本初期commit
`d47645c4cb624d1dfde706dad3e30e4c3092e772`の指定4文書を読んだ。
leaseは通常pushで取得。PdM `pdm_reconcile_adaptive` が既存PRと仕様を比較し、
PrMが既存差分の照合に範囲を限定。実装者とは別の `qa_reconcile_adaptive` が独立QAを行った。
新規製品実装はないためEngineerは起動していない。

## 対象と結果

- #15 `f98456fef3673d08ef226e5b0d9bddfa236c734f` を独立checkoutで検証。
- #10 `ba829a1176ff1ead7d312526890afe8792178c99` は互換性probeで当該HTMLを使用。
- #14 `ef70a502e36aeac871edb183bbf29b4e193b31b9` は静的比較のみ。#15の成功を#14そのものの検証に数えない。
- #13 `139c8b8b56bcd979068b61984120d9f312efe182` は運用指示差異のみ比較。採用なし。
- 22:16 JSTのGitHub再照合でも#10〜#15のHEADは上記および既存台帳のまま、open/draft。

```bash
cd /workspace/yuika-reconcile-adaptive-20261110
source /workspace/yuika-content-flow-20261110/scripts/cloud/activate.sh
python tests/adaptive_practice.py
python tests/adaptive_daily.py
python /workspace/work/reconcile-adaptive-qa-20261110/cross_version_probe.py
```

すべて初回・終了コード0。既存venvを利用し依存導入なし。768×1024の新規Chromium context、合成履歴のみ。
これは既存準備を利用した検証で、自動環境引き継ぎの再検証ではない。

| 試験 | 実行時刻 JST | 実施範囲 |
| --- | --- | --- |
| adaptive_practice | 22:08:58–22:09:00 | 応仁/鎌倉、派生ID、回答/採点/再読込、JSON検証、元問題数保持 |
| adaptive_daily | 22:09:17–22:09:20 | 3単元、難度、解説、ヒント保持、回復/再誤答、保護者集計、破損/拒否storage保護 |
| cross_version_probe | 22:11:55 | 同一originでPR15/PR10を切替えた保存互換性 |

## 再現した互換性障害

同じ保存キーの合成eventを用いた。PR15のvalidatorで作成した通常modeの元問題eventと
派生ID eventを注入し、ID差だけを切り分けた。製品コードの併合やvalidator変更はしていない。

| 起動ページと保存内容 | blocked | 読込件数 | 元データ |
| --- | --- | --- | --- |
| PR10・元問題だけ | false | 1 | 正常 |
| PR10・元問題＋派生ID | true | 0 | raw不変、broken保持 |
| PR15へ戻る・同じ記録 | false | 2 | 復元 |

**旧版へ戻ると履歴全体が読込休止する互換性の障害**。データ消失ではない。
READMEの逆インポート制限だけでなく通常ページ起動にも及ぶ。
probeは期待した障害と復元をassertしてexit0。製品統合の合格を意味しない。
probeでPOST試行0/サーバー到達0、外部要求0、JS例外0を測定した。
既存2テストはPreviewHandler/CSP・HTTPS遮断を確認したが、全POST計測までしたとは報告しない。

静的には#10の原問題ID別おすすめ判定と#15のoriginId合算判定も異なる。
単純統合後に追加練習で正答してもおすすめ候補が残る可能性はあるが、統合版の不具合としては未再現。
回答前に正解を表示する追加練習の説明欄も、既存仕様との区別が必要。

## 保存・次の一手

[比較仕様](../../docs/product/review-reconciliation.md)と台帳を運用draft PR #9へ保存する。
製品PR #10を既存の復習基準として維持し、#14/#15の差分採否・保存契約・旧版移行条件を定義してから
既存PRの修正範囲を決める。既存validatorを弱めたり未知eventを捨てたりしない。
3件の連携済み製品ceo_waitに加えて製品PR2件を観測したので、新規製品実装は増やさない。
#13の最大3回再試験は採用せず、CEOの同原因2回/35分/lease45分を維持する。

コード変更・PR作成/閉鎖・マージ・公開・実通知・実資料/Evernote接続なし。
D01採用、D02未決の状態を維持。全回帰の反復、統合版、#14単独HEAD、iPad実機Safariは未検証。
元checkoutと製品checkoutを保持し、製品checkoutは試験後clean。

## 証拠

クラウド内 `/workspace/work/reconcile-adaptive-qa-20261110/` にログとprobeを保存。
その継続保持は保証しないため、再現条件と観測値を本Git文書に記録する。

| ファイル | SHA256 |
| --- | --- |
| `QA.md` | `7f4d0593537639119ee55cfd603e6a36b2acee828171340ae6a4eb19b54a8613` |
| `adaptive_practice.log` | `9184f56701678875e8df08ae96e7c9fec2b6b77260a21598c6aabe6ac0d89d68` |
| `adaptive_daily.log` | `e2dbbc8ee160f70b49a52ba4c96b7b5a895d70ecb7bfa02a73cdc4e5d0ce9079` |
| `cross_version_probe.py` | `4e4d78d9c0f50ddbcacfa119c14d7f941683f1166ba73f41438abc01c98efdfe` |
| `cross_version_probe.log` | `b3160594d88916a2025c60d6ccf69b76ce6103cba71c78b2bb0f51d3cf318d45` |
