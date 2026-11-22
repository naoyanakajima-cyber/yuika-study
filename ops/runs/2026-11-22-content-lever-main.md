# 合成教材試作PR11とてこ追加mainの互換性

## 目的と範囲

画像・テキストの合成教材案を確認・編集し、保存しない試し解きで内容を確かめる既存PR11を、新mainのてこ教材と共存できる状態へ追従する。
元HEADは `1678519f916471ba6e38044855de240bd6c4a807`、観測mainは `58f8b53b4da69806d15a126fc525b65893a0bf35`。前回PR10互換性は完了済みで、今回はCONTENT-MVPの既存PRのみを対象とする。
外部PR30のmergeは観測事実であり、今回の本番操作や新CEO承認ではない。新CEO返答の実読・取り込み0。

PdM `pdm_content_lever` が仕様再作成不要と判断し、PrM `root` が範囲を受入。Engineer `engineer_content_lever` が独立checkoutへ実装し、別担当 `qa_content_lever` が固定候補を検証する。
既存 `content-spec.md` のC1–C11、`content-try-spec.md` のG/S契約、`content-image-trial-spec.md` の7条件を維持する。

## 受入条件

1. PR11の履歴と既存の教材案・画像照合・メモリ内試し解きを保持する。新機能やPR10/12固有改善を追加しない。
2. 新mainのてこを含む教材・共通assets・問題ID・採点・保存キー・recall履歴・親runtimeを巻き戻さない。
3. CONTENTのHTML・6fixture・schema・固定hashを旧PR11と照合する。CSP、未知HTMLの親preflight拒否、改変contentの親preflight/書込前generator拒否を維持する。
4. main26＋CONTENT5の全31suiteを独立QAで実行し、各終了コード・秒数と固定HEADを記録する。既存assertを弱めない。
5. 768×1024で合成text/三角形画像の確認→開始→採点→終了→JSON再入力、未解決/未確認/編集後の拒否、回答消去、案/確認/unsaved保持を検証する。既存suiteの該当assertと追加接点probeを対応付ける。
6. 合成データ・通知mockのみ。旧65/15probeは過去証拠であり、今回の成功へ転用しない。byte不変部分の無根拠な全面反復は行わない。

## 実行環境と限界

管理クラウドの起動を確認し、指定4文書を運用branchの同一最新commit `d1d3152ce0a0db18a0e73ddf9cf8ee68b3790b85` から読んだ。既存checkoutから作業用worktreeを手動準備した。自動snapshot引き継ぎ成功とは報告しない。
D02実入力/保存先、OCR、実教材・実回答の接続、本人試用、実機Safari/公開画面は今回対象外。本番merge・公開・実送信・課金・Secrets/権限変更なし。
製品判断待ちはPR10/11/12の3件を維持し、新規製品PRは作らない。次はTHEME-MVP/PR12の同main互換性を確認する。

## 実装候補

候補 `ee228ca0a1865d0a56f4302cd9342a4f66738561` は旧PR11と新mainを親とする通常のtopic merge。競合なし。mainへのmerge/pushではない。
Engineerは旧CONTENTのHTML・6fixture・仕様/schema・5suite・2hash guardの計18ファイル、および新mainの学習HTML/assets/history/practice/通知/親runtimeの保護31ファイルのbyte一致を確認した。
check_allは31 unique suite、mainとの差はCONTENT5行だけ。mainとの差23パスは既存CONTENT試作に由来する。
生成器build_summary・design/embed・parent/embedの再実行で追跡差分なし、bash構文/diffチェック成功。Engineerはvenvを使わず、全suiteは独立QAに委ねた。

PR9/11のタスク添付を各1回呼び出したが応答せず、待機を中断した。添付成功は未確認であり、GitHubへの保存結果と区別する。

## 独立検証の範囲

独立QAは固定ee228caで、新mainの85パス、旧CONTENTの16パスをbyte照合した。共有の既存6パスも旧PR11と一致し、check_allはmain26＋既存CONTENT5の和集合。
隔離コピー上の3生成器はbyte不変。未知HTMLは親preflightで拒否、改変CONTENTは親preflightとHTML書込前generatorで拒否することを初回確認した。
768×1024の新規Chromiumで、理科画面の実際の操作から合成lever-01回答を保存し、同じブラウザーで画像/textの明示確認→試し解き採点→終了→JSON再入力・再編集拒否→再読み込み→理科記録の読み戻しを確認した。5操作ケースが初回成功し、全localStorage bytesと合成回答は不変。
CONTENT画面の監視範囲で保存API呼出・非許可要求・pageerrorは0。前後の理科画面のGoogle Fonts GET2件は遮断して別計数し、全体で外部要求試行0とは報告しない。通知suiteはmock。
QAは合成画面3枚を目視し、統括も三角形原本と採点結果2枚を確認した。追加probeと既存CONTENT5suiteの受入条件の対応はQA.mdへ記録する。

## 最終QA結果

独立QA `qa_content_lever` は候補ee228caを受入、blocking指摘0。
全31suiteは初回成功、終了0、326秒（外側326.657秒）。開始2026-11-22 14:09:49 UTC、完了14:15:15 UTC。前後HEAD一致・追跡差分なし。実行中は手動venvリンクのみ未追跡であり、cleanなtracked treeと区別した。
[QA結果](../evidence/2026-11-22-content-lever-main/QA.md)に全31行の終了コード・秒数、各受入条件と既存suiteの対応を保存する。独立static/probe結果・実行スクリプト・合成画面も同じ証拠ディレクトリへ保存する。

14:16:06 UTCにQA checkoutの手動venvリンクを解除し、HEAD一致・status完全空を確認した。

独立QAは最終report/PR本文の全31行と結果JSONの一致、コピー12資料とSHA256SUMSの一致を確認した。拒否対象と今回の互換追従範囲を明確にする文言2箇所を統括が反映。
