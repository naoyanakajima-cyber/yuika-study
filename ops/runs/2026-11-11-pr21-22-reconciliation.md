# PR21・22の差分照合（2026-11-11 JST）

## 目的・結果
学習時の押し間違い防止とiPad相当の使い勝手確認を進める既存PRを照合した。
PrMはPdMの提案を確認し、今回は照合記録と障害整理を行うと決定した。
製品の新規実装、同一QAの反復、ネットワーク設定変更は実施していない。

- 正本基点: `cdab302a499af15f558e6fbae8eabe2676050bd7`。同一commitの指定4文書を読取。
- cloud/running/connected、最新観測を確認。leaseを通常pushで取得後に分担。
- PdM: `pdm_pr21_22_triage`、PrM: `root/coordinator`、独立Reviewer: `qa_pr21_22_readonly`。
- Engineerは起動していない。レビューは静的照合であり、WebKit/製品テスト成功ではない。

## 対象
- [PR21](https://github.com/naoyanakajima-cyber/yuika-study/pull/21): `7608cf89b7d3ab35c541763f0f04c75043f76cba`、AGENTS.mdのみ。
- [PR22](https://github.com/naoyanakajima-cyber/yuika-study/pull/22): `aaa7488d766955353f3ff5314d3361fba7fbcd91`、10ファイル/280行追加。
- 両者ともbaseはPR20 `79d546891940b6f5e3030940f7c52c2ff7b3d36b`。PR22はPR21を含まない。両者open/draft、未マージ。
- PR4〜20のHEADは既存観測から変更なし。mainも `d526d65fbae116f834d14ad994a27bc50ca23b62` のまま。

## PdM/PrM判断
PR21の最大3修正サイクル・常に最新draft起点・毎回全suiteは、正本と今回の明示制限を置換しない。
同因2回まで、依存確認で基点選択、必要な検証を行う現行運用を維持する。
PR22のタップ領域拡大とWebKit確認には価値があるが、採用・実行完了とは扱わない。
製品待ち3件に加え未採用追加製品draft #14〜#20/#22の8件が存在する。#21は運用文書。
新規製品PRを増やさず、既存試作品の採用整理・具体的フィードバックを待つ。
D01/D03〜D05は既に記録済み。D02のEvernote候補に新たな採用・接続許可はない。

## 静的レビューと実行証拠の区別
PR22は既存17suiteを維持し18番目にWebKitを追加する。WebKit失敗は非0で、setupの成功記録作成より前に停止する。
製品差分は社会3ページ・理科のCSS各4行で、保存・採点・問題ID処理の変更はない。
WebKit成功をChromiumへ代替するコードやskipは見られない。今回の静的範囲で明確なコード不具合は見つからなかった。
PR作者は既存17suite成功、追加WebKit未導入による全体終了1、公式配布先403を報告している。
これらはPR本文の報告であり、今回再現していない。Chromium24ケース成功もWebKit成功とは扱わない。

現環境のeffective_allowed_hostsに `cdn.playwright.dev` / `playwright.download.prss.microsoft.com` は含まれない。
今回download/環境設定変更をせず、導入障害を `IPAD-WEBKIT-01` として記録した。
route監視が捕捉するのはネットワーク層へ渡った要求であり、CSPで通信前に止まった試行すべての不在は証明しない。
WebKitはLinuxでの端末エミュレーションであり、実機Safari・IME・実キーボードの検証ではない。

## 次の一手・受入条件
正規に許可された環境でWebKit導入と実起動を確認後、既存PR22の現HEADを独立QAする。
24ケースと既存17suiteの成功、旧保存/採点/問題IDの保持、監視範囲を明記した外部通信/POST遮断を確認する。
本サイクルは新規製品テストなし。台帳JSONと差分の整合確認だけを実施する。
本番マージ、アプリ公開、実通知、Secrets・権限・共有範囲・課金の変更は行っていない。
