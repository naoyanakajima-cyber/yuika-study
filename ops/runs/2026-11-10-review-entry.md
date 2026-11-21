# REV-MVP：おすすめ復習の入口改善

2026-11-10 JST。クラウド実行を確認し、運用正本 `c3a04e994f619329f65635dfe1fd9992a8e9b42f` から開始。
lease `cycle-20261109T2209Z` を通常pushで取得。CEOが取り込み済みD03で最優先とした試用・使い勝手改善を行った。
新しい方向性承認を推測しておらず、実データ・公開権限は拡張していない。

## 学習上の改善

応仁・鎌倉のホーム初期表示に、おすすめ復習の候補数・今回の問数と案内を追加した。
以前はおすすめ開始ボタンがy=1305.36pxにあり、スクロールして探す必要があった。
現在は上部案内がy=459.86pxにあり、768×1024の画面内からおすすめの存在を見つけられる。

- 候補あり：既存おすすめ欄へ移動し、見出しへフォーカス。次のTabで開始ボタンに進める。
- 候補0件：通常練習の設定へ案内する。習得済みとは判定しない。
- 記録読取不能：候補0件と区別し、記録の状態が分かるおすすめ欄へ案内する。
- 案内だけでは出題・採点・記録を始めない。設定再描画後のフォーカスも保持する。

## 担当と保存先

- PdM：`pdm_rev_discoverability`。既存条件の再確認、0件と読取不能の区別・設定追従を補足。
- PrM：`root/coordinator`。E1〜E6の範囲を確認し、同じPRでの変更として承認。
- Engineer：`engineer_rev_entry`。独立checkoutで実装、pushなし。
- 独立Reviewer/QA：`qa_rev_entry`。差分と5コマンド、追加ブラウザー確認を独立実施。
- 既存draft [PR #10](https://github.com/naoyanakajima-cyber/yuika-study/pull/10) を更新。新規PRなし。
- 製品commit：`ba829a1176ff1ead7d312526890afe8792178c99`。
- 再開元：`bd7a055a1169416dbdd82654ac19c228a739f9cf`。PR baseは#7の `edad8065c1f2b726e61c5cf405f8d9ff6d807480` のまま。
- 最新main `d526d65fbae116f834d14ad994a27bc50ca23b62`、既存#4〜#8と製品#10〜#12がdraft・未マージであることを照合。

変更は両単元HTML、README、新しい `tests/review_entry.py` の4ファイル。
新しい独立checkout `/workspace/yuika-rev-discoverability-20261110` を用意し、既存の検証済みsetupを手動実行した。
Python 3.12.14、Node 24.19.0、Playwright 1.62.0、Chromium 154.0.8037.57。
これは自動snapshot引き継ぎの検証ではない。依存定義・CIは変更していない。

## 今回の検証

同じシェルで `source scripts/cloud/activate.sh` 後、独立QAが最終commitに対して実行。

| コマンド | 結果 |
| --- | --- |
| `python tests/onin_review.py` | exit 0 |
| `python tests/kamakura_review.py` | exit 0 |
| `python tests/cloud_preview.py` | exit 0 |
| `python tests/recommended_review.py` | exit 0 |
| `python tests/review_entry.py` | exit 0 |

追加のfresh contextで両単元の候補あり・0件・読取不能、設定追従、キーボード/可視フォーカス、4つの既存復習入口を確認。
上部案内は読取不能時もy=552.36pxで初期表示内。外部要求0・POST到達0・JS例外0・横はみ出しなし。
教材、validator、選定以降の処理、通知ブロック、CSPは再開元と一致し、既存テストを変更していない。

Engineerの新テスト初回ではブラウザーが再読込時のスクロール位置を復元したため、位置のassertが失敗。
ホーム先頭を明示して幾何確認する前提を修正した。位置の条件・既存assertは緩めていない。
独立QAも修正を点検し、fresh contextの初期表示を別途確認した。

検証ログ・合成画面・再現スクリプト：`/workspace/work/rev-entry-qa-20261110/`。
独立QAのSHA256と親のpush直前照合は一致。開始・終了とも製品checkoutはclean。

| ファイル | SHA256 |
| --- | --- |
| onin-review.html | a399a53a464142d27d9a4a96c122588be3c961d1275dac29a31b8aadcf62c70b |
| kamakura-review.html | 8c57c22ec53e28a98f5ea491cb184b4d1bcc4c50eb131e685cc6297863330f63 |
| README.md | 9192d9ce3eb5eb52e58396019add74ad2381448dcd8ec793f689966cafe92f67 |
| tests/review_entry.py | 412b78e1b4e1a9e7cef5e5d46373fda0185fd241ea70e2c8ae0d6f8e4b504d4d |

## 次の一手と制約

REVの入口改善は独立QA済みで試作品の確認待ち。D03の方向性採用は維持し、同じ採用判断を再要求しない。
CEOが直接操作する共有ブラウザーへの引き渡し、実機iPad/Safari、学習効果は未検証。
共有ブラウザー用の正規操作機能がないことは別の制約であり、今回のコード改善や検証成功と混同しない。
具体的なREV修正依頼がなければ、次はCONTENT-MVPの合成確認画面の試用導線・次受入条件をPdM→PrMで整理する。
THEMEはその後。D01/D02の実入力経路・保存先はpendingのまま。

EXTERNAL-PREVIEW-01の旧HEADに対する外部ビルド失敗は未解決。今回その調査・再デプロイを行っていない。
PRへの必要なpushと説明更新のみ行い、マージ・公開/デプロイ操作・実通知・Secrets等の変更は行っていない。
定時実行プラットフォームの成功判定は取得していない。本記録は今回の実作業結果。
