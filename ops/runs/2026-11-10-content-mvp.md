# CONTENT-MVP 開発サイクル（2026-11-10 JST）

## 成果と学習上の価値

教材の誤読や未確認の正答を、そのまま学習に使わないための独立した「教材の確認室」を追加した。
同梱の合成テキスト・画像について原本、転記、不明箇所、問題案を比較し、編集、個別確認、
JSON出力・再入力ができる。内容編集はrevisionを増やして全確認を失効させる。
外部JSONのconfirmedを信用せず、未解決箇所や内容不備があれば確認済み出力を遮断する。

- [draft PR #11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11)
- 製品commit: `1ea081b4b68b311fcd40c35d1f8bc972e3c60054`
- branch: `codex/content-review-mvp`
- base: `codex/cloud-automatic-bootstrap` / `edad8065c1f2b726e61c5cf405f8d9ff6d807480`
- 依存: #5 → #6 → #7 → #11。苦手復習のPR #10とは独立。#8は含まない。
- CONTENT-MVPはCEO判断待ち。実OCR、自動問題生成、私的資料の入力経路、既存アプリへの教材導入は未実装。

## 実行権と分担

実行開始は2026-11-09 16:06 UTC。provider=cloud、running/connected、最新観測、
network enforcedを確認した。同じ最新運用commit `218e3d9b176ab773088dadc5b44fd8fd226ffd85`
から正本4ファイルを読み、既存PRとmainを照合した。mainは `d526d65`、
前回の仕様チケットは完了、PR #10への新しいCEO判断は未記録だった。
通常pushでleaseを取得してから、独立checkout `/workspace/yuika-content-mvp-20261110`で実装した。

- PdM `pdm_content_mvp_check`: レビュー済み仕様C1〜C11の適用を確認。構造不正の拒否と編集可能な内容不備の区別を整理。
- 統括/PrM `root`: 合成データ限定の範囲とD01/D02非依存を確認。README、プレビュー許可リスト、運用記録を担当。
- Engineer `engineer_content_mvp`: 新規HTMLとブラウザーテストを実装。
- 独立Reviewer/QA `qa_content_mvp`: 差分、4テスト、追加ブラウザー操作、画面、最終commitを確認。コード編集なし。
- 子はcommit/pushを行わず、統括がremote leaseの所有者と期限を再確認してcommit/push・draft PR作成を行った。
- 子3名、同時実装1件。前のcheckoutや既存venvは保持した。

必要な依存は既存手順 `bash scripts/cloud/setup.sh` で新しいcheckoutに手動準備した。
Python 3.12.14、Node.js 24.19.0、Playwright 1.62.0、Chromium実起動・pip checkが成功。
これは手動準備であり、公開snapshotの自動引き継ぎ成功とは扱わない。

## 検証と修正

独立QAは同じシェルで `source scripts/cloud/activate.sh` 後、以下を実行した。

| コマンド | 結果 |
| --- | --- |
| `python tests/onin_review.py` | exit 0 |
| `python tests/kamakura_review.py` | exit 0 |
| `python tests/cloud_preview.py` | exit 0 |
| `python tests/content_review.py` | exit 0 |

既存2復習テストで起動・回答・採点・記録・再読込を確認。新規テストは768×1024で
合成サンプル選択、編集、確認失効、未解決箇所、取消、出力・再入力、既存記録保持を検証した。
新規画面の外部要求・通知POST到達・storage書込みはいずれも0。再読込前後の両方を確認した。
通知コードは変更しておらず、Worker/通知ブラウザーテストは今回再実行していない。

独立した追加操作では、2問の片方のみ確認した場合の出力拒否、両方確認後の出力許可、
packageId・空出典参照・不明generatedFieldsの修正、長い参照文字列の768px幅内折返しを確認。
不明文字のID・quote・candidatesを明示修正し、確認を失効させて再確認できることも確認した。
画面スクリーンショットはクラウド内の `/workspace/work/content-mvp-qa/` に保存し目視確認した。

レビューで見つけた、内容不備を画面から直せない箇所、長い出典文字列の横はみ出し、
原文要約の編集後表示を修正した。テストのJSON読込待機も非同期完了に合わせた。
新規テストで旧HTML全体を固定hashに縛る過剰な検証を除き、今回の差分確認として
既存5画面・既存テストに変更がないことを確認した。既存assert・CSP・模擬APIは弱めていない。

全4テストの一括実行は、最後の原文要約同期2行修正の直前版。
その最終表示修正は独立QAが関連操作（表示同期、revision増加、確認失効・再確認、JS例外0）を再検証した。
以後の変更はCSS末尾空白1字除去のみで、最終commitとの一致をQAが読み取り確認した。
最終HTML SHA256: `6938912456d9496afbd2d5df6e42cf7ee723553d5b2632ce98bd1b96c510f443`。
`git diff --cached --check` と最終作業ツリーの検査も成功。
仕様・4 fixturesはレビュー済みcommit `c79197099537d9ef3a34badb4b7f0ff74cbc615a` と同一。

## 再開方法・次の一手

製品branchを取得したcheckoutで既存setup手順を適用し、次を使う。

```bash
source scripts/cloud/activate.sh
python scripts/cloud/serve.py
```

プレビューの `/content-review.html` を開く。新規画面はメモリ内状態だけを使用し、
必要な案をJSONで出力しなければ再読込で消える。実機iPad/Safariは未検証。
実教材の入力場所、非公開保管先、導入adapter・ID/履歴互換性は後続の判断・実装事項。

製品PRのCEO判断待ちは #10 と #11 の2件。新たなCEO承認は推定していない。
次は依存しないTHEME-SPECを進め、標準と鎌倉テーマの切替・可読性・学習記録分離を定義する。
CEOにはD04として合成教材確認試作の仕様・挙動の採用を朝夕に提示する。
採用判断は依存PRのマージ・公開や実データ接続の承認とは分離する。

私的回答・教材写真・メール/Driveを取得せず、公開成果は合成データだけを使用。
実通知、本番マージ・公開・デプロイ、Secrets・課金・権限・共有範囲変更は行っていない。
停止中の旧自律更新やスケジュールを変更していない。
