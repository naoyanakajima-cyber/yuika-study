# REV-MVP：日次練習の開始前件数を既存UIで照合

2026-11-15 JST（ファイル名はUTC）。run `cycle-20261114T180819Z`。
クラウドrunning/connected/currentを確認。正本4文書は同じ `08515714845c62e3276cb53c4b498c31edcbe158` から取得し、leaseは通常push `707ef37` で保存した。
前回のnext_actionにある件数表示の合成再現調査をPdM→PrMで範囲確認した。

学習者が始める前に今回の問題数を判断できることが目的。「今日の5問」という入口名と「今回はn問」という実数の表示を分けて調べる。
対象は固定main `86514eda054a5a2e09204df3a0668e40624c16de` の既存UIで選べる条件。関数抽出試験の人工poolを画面で到達できる例と混同しない。
独立checkout `/workspace/yuika-daily-count-20261114` は読み取り調査用に手動準備。検証済みvenvをignored symlinkで再利用し、依存manifest SHA256一致とactivate/importを確認。自動snapshot引継ぎ成功とは扱わない。

## 分担と境界

PdM `pdm_daily_count_scope` が対照・名称・候補不足・ゼロ・平安の5ケースを定義し、PrMが文書/証拠限定の範囲を確認。Engineer `engineer_daily_count_probe` が固定mainで実UI観測を担当する。独立QA `qa_daily_count_investigation` がソース・画像・要件案を確認し、C/Dを独自ハーネスで実行した。
新日次アルゴリズム・新問数・教材・保存仕様・製品コード・既存テストは変更しない。非ローカル通信と実通知を遮断し、独立ブラウザーの空履歴と既存教材だけを使う。

旧PR10のHEAD `ba829a1176ff1ead7d312526890afe8792178c99` にはmainの `scripts/practice/adaptive.js` がなく、おすすめ方式・保存世代も異なる。日次件数の修正を旧PRの小修正としてそのまま投入しない。製品待ち#10/#11/#12の3件と追加既存#22を維持し、今回は運用draft PR9に文書・証拠を保存する。

新CEO返答取り込み0。D03〜D05は方向性採用済み、D02の実接続・保管先未決。main merge・公開/デプロイ・実メール/Chat・課金・Secrets/権限/共有変更なし。旧停止中自律更新は再開しない。

## 成果と実行証拠

[修正要件案](../../docs/product/daily-count-spec.md)に推奨文言と受入条件を保存。表示は候補全体でなく、選定・重複除去・上限適用後の実際に開始する総数に一致させる案。0件は事前に条件の見直しを案内し無効化する。今回の完成は調査・要件文書のみで、製品不具合は未修正。

Engineerは既存UIだけの5ケースを1回観測。応仁5→5の対照、10→10だが「今日の5問」という名称、応仁all/応仁の乱/kanjiの表示5→実4、d2/将軍/normalの0候補有効ボタン→開始拒否、平安pairs/藤原氏と政治/normalの表示10→実2。候補配列/設定/時計/RNG/関数の直接改変なし。履歴は全て0→0/raw null。設定保存はあるため全storage書込0とは主張しない。
独立QAはC/Dを各1回別ハーネスで再現、画像と実run・通知・home状態を確認。エラー/再試行0。UI観測は開始直後まで、回答・採点・完了をしていない。

- [PdM](../evidence/2026-11-14-daily-count-investigation/PdM.md)
- [Engineer](../evidence/2026-11-14-daily-count-investigation/Engineer.md) / [実測JSON](../evidence/2026-11-14-daily-count-investigation/engineer/results.json)
- [独立QA](../evidence/2026-11-14-daily-count-investigation/QA.md) / [独立再現](../evidence/2026-11-14-daily-count-investigation/qa/results.json)
- [既存22suiteログ](../evidence/2026-11-14-daily-count-investigation/qa-suite.log) / [開始終了](../evidence/2026-11-14-daily-count-investigation/qa-suite-meta.json)
- [証拠SHA256](../evidence/2026-11-14-daily-count-investigation/sha256.json)

必須 `bash scripts/check_all.sh` は固定mainで独立QAが1回、18:12:41.502994〜18:17:15.317519 UTC、22/22、exit0、274秒、前後clean。既存テスト成功でも今回の表示差は存在する。これは未実装修正の受入成功ではない。Engineer観測は非ローカル要求7件を遮断（種類未採取）、QA C/Dは公開font CSS GET2件を遮断、どちらもserver POST0・pageerror0。全体suiteは既存公開CDN GET・模擬通知・合成storageを使用し、全体通信/書込0とはしない。

レビュー指摘：当初の「候補の実数」を「実際に開始する総数」に訂正。候補30/選択5で30問と表示する誤仕様を避けた。旧通常候補labelは共通デザインで除去されており、候補値は内部の非乱数読み取り、可視の未回答4/0とは別の表示として説明。平安探索ログの要求courseを実際の同時到達状態と混同せず、正式Eのbefore.prefsを根拠にした。

## 外部状態と次の仕事

前回PR11 HEAD f1e84a7のWorkers Builds checkは2026-11-14T17:24:11Zにfailureで終了したことを今回読取り確認。以前からの外部preview失敗の最新観測であり、ローカル24suite成功とは別。原因ログ未取得・公開未確認。再実行/設定変更/デプロイなし。

次はPdM/PrMで、既存PR10に残すべき選定理由と現mainの日次・保存契約を両立させる修正範囲/基点/生成先を定め、日次件数修正を既存PR内で扱えるか具体化する。旧branchへの単純投入・新PR枠追加は行わない。D03の方向性採用を再要求せず、merge/公開は承認済みとしない。
鎌倉/理科/重点復習/トップのこの表示問題、履歴混在、親モード、保存拒否、別タブ/時刻境界、修正後の回答→採点→保存→再読込、実機Safari、本人試用は未検証。通常報告は朝夕CEOチェックへまとめる。
