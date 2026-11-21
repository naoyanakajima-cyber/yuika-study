# CONTENT-MVP：確認作業の進み具合と次操作案内

2026-11-10 JST。クラウド実行を確認し、運用正本 `1b3edaf5b75196de315ca8cd05b79e1faf5d7514` から開始。
lease `cycle-20261109T2308Z` を通常pushで取得した。D04の方向性採用を維持し、D01/D02の実入力経路・私的資料保管先は未決のまま扱った。
REVには新しい人の修正依頼がなく、次優先の既存CONTENT-MVP・PR #11を進めた。

## 学習上の価値と変更

新教材の確認で、不明な文字や不足項目を残したまま「確認済み」と誤認しないよう、現在の進み具合と次に見る場所を作業上部へ表示する。
元の768×1024試用では、画像例の確認できない具体理由がy=2564px、JSON出力がy=2905pxにあった。
現在はサンプル/再入力後に進み具合へフォーカスし、確認済みn/全問を示して次の場所へ案内する。

1. 未解決の読み取りがあれば、その読み取り確認欄。
2. その他の修正が必要なら、該当問題の不足理由。
3. 形式上問題がない未確認問題なら、内容を読む見出し。
4. 全問確認後はJSON保存欄。

案内はfocusとscrollだけ。内容確認・revision変更・出力・保存を自動では行わない。
確認条件、編集時の全確認失効、再入力時の確認リセット、メモリのみの保持、CSPを維持した。
OCR、問題自動生成、実資料入力、学習アプリへの導入は追加していない。

## 担当・成果

- PdM：`pdm_content_flow`。コード上の負担を調査しG1〜G5を提案。
- PrM：`root/coordinator`。初期QAの実測と照合し、表示/案内だけの範囲を承認。
- Engineer：`engineer_content_guidance`。独立checkoutで実装、子のpushなし。
- 独立Reviewer/QA：`qa_content_flow`。変更前の試用と、変更後の差分/テスト/追加操作を実行。
- 既存draft [PR #11](https://github.com/naoyanakajima-cyber/yuika-study/pull/11)を更新。新規PRなし。
- 最終commit：`3d2ed2f9a62673d2fb086a360ae841096f35b63e`。
- 再開元：`1ea081b4b68b311fcd40c35d1f8bc972e3c60054`。PR baseは#7の `edad8065c1f2b726e61c5cf405f8d9ff6d807480` のまま。
- main `d526d65fbae116f834d14ad994a27bc50ca23b62` と既存PR #4〜#12を照合。重複実装・マージなし。

変更は `content-review.html`、README、`tests/content_guidance.py` の3ファイル。
独立checkout `/workspace/yuika-content-flow-20261110` で既存setupを手動実行した。
Python 3.12.14、Node 24.19.0、Playwright 1.62.0、Chromium 154.0.8037.57。依存定義・CIは変更なし。
手動準備であり、snapshotの自動引き継ぎ検証ではない。

## 検証結果

同じシェルで `source scripts/cloud/activate.sh` 後、独立QAが最終commitで実行。

| コマンド | 結果 |
| --- | --- |
| `python tests/onin_review.py` | exit 0 |
| `python tests/kamakura_review.py` | exit 0 |
| `python tests/cloud_preview.py` | exit 0 |
| `python tests/content_review.py` | exit 0 |
| `python tests/content_guidance.py` | exit 0 |

独立追加操作は合成text/image、複数問、複数不明箇所、各分岐、キーボードと可視フォーカスを含む。
誘導前後でproposal・revision・確認・unsaved・ダウンロード数が不変。編集入力中のフォーカスも保持。
編集で全確認失効、confirmed再入力のリセット、取消後の案内非表示を確認した。
外部要求0・POST到達0・storage書込0・JS例外0・横はみ出しなし。
validator、issues、changed、export、CSP、既存5教材HTMLは再開元と一致。既存テストは変更なし。

証拠は `/workspace/work/content-flow-qa-20261110/baseline/` と `final/` のログ、JSON、独立再現スクリプト、合成画面。
QAが未解決・全確認の画面を目視し、統括も上部案内の画像を確認した。
最終commitと以下のSHA256を親がpush直前に照合。開始・終了時とも製品checkoutはclean。

| ファイル | SHA256 |
| --- | --- |
| content-review.html | 586e626a6759a3c1000f2ec50785627081569df75a71178e6d17482f948b030d |
| README.md | e6ad8fb8677989c395dec612a9b9b237b200bc11a339e128141d4bb9de816923 |
| tests/content_guidance.py | 37380a5ddc875a64ab77449bd87f97305dac3cfa7b05746c69c3c7428edac2c6 |

## 次の一手・制約

CONTENTの案内改善は試作品確認待ち。D04採用済みの方向性を再要求しない。
REV/CONTENTに具体的な修正依頼がなければ、次はTHEME-MVPの読みやすさを既存の合成画面で確認し、必要な差分だけ扱う。
実機iPad/Safari・CEO本人の操作評価は未検証。共有ブラウザーへの引き渡し完了とも扱わない。
定時実行プラットフォームの成功判定は取得していない。

既知のEXTERNAL-PREVIEW-01は未解決。PR #10の更新後HEADにもbotがBuild Failedを報告し、プレビューURLはない。
今回もビルドログの新たな取得や再デプロイは行わず、アプリQAとは区別した。
実通知、マージ、公開/デプロイ操作、Secrets・権限・共有範囲・課金の変更なし。停止中の旧自律更新は再開していない。
