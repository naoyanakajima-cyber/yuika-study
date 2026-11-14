# REV-MVP：現在の保存保護を保って理由付き復習を統合

2026-11-14。run `cycle-20261114T191016Z`。通常の報告は朝夕のCEOチェックへまとめる。

## 学習上の価値と範囲

応仁・鎌倉の「おすすめ復習」で、前の誤答、24時間以上、ヒントあり正解という具体的な理由を確認できる既存PR10を、現在の保存保護・親確認モード・日次練習と共存させる互換性修正。おすすめの選定規則を日次選定へ置換せず、新しい入口・新製品PRを増やさない。

前回確認した日次件数の不一致（応仁5表示→実4、平安10表示→実2、0候補でも開始ボタン有効）は今回未修正。統合受入後の次の既存PR内修正に残す。

## 根拠と分担

- 運用正本 `7c7ad83953a32ae459e9aafb272d5071957f40ac` の4文書を確認。leaseを `03b48689be5ee25f5e76df1ee6e63a4c1fdf8acd` で通常push、範囲を `eae453a` へ保存。
- 最新main `86514eda054a5a2e09204df3a0668e40624c16de`、元PR10 `ba829a1176ff1ead7d312526890afe8792178c99`。製品待ちは10/11/12の3件と追加既存22。4〜8・運用9/13は別枠。
- PdM `pdm_rev_current_scope` → PrM `root/coordinator` → Engineer `engineer_rev_current` → 独立QA `qa_rev_current`。子3名、同時実装1件。子pushなし。
- [範囲契約](../../docs/product/review-current-base.md)。未来日時の旧仕様は現mainの5分超停止を優先。新CEO返答・採用・公開承認は取り込んでいない。

## 候補と検証

候補 `132f9f59ebd23b6dab33e7d1e23bf4d077b8070d` は元PR10とmainを両親に持つtopic側の統合commit。mainへのマージではない。main相対は両HTML、推薦2テスト、全テスト登録、README、条件付き共通デザイン配置の7ファイルだけ。

mainの保存名前空間、親runtime、問題版検証、採点・保存経路、日次・弱点・期限選定、通知/CSPを維持。おすすめ開始時にも読取不能・未保存・5分超未来を停止し、正常0件と分ける。推薦先を他単元へ広げない。

Engineer重点試験は推薦・入口とも両単元成功。推薦の初回は合成fixtureの問題版が誤っていてvalidatorが拒否、fixtureだけ修正し2回目成功。独立QA開始前に候補をcommit・cleanへ固定し、その後製品編集を停止した。

独立QAは固定clean候補で必須24/24成功、exit0、runner300秒（2026-11-14T19:15:18.136339+00:00〜19:20:18.890176+00:00）。製品編集・試験中commitなし。両単元の通常保存/再読込/旧キー保持、親モード保存/退出、破損raw、未来日時、実quota例外の10ケースも受入。追加probeは2種類のハーネス不備を各1回修正し、2回目の応仁4ケースと3回目の未完了6ケースを合わせた結果。製品失敗0で、一発成功とは扱わない。

静的17項目のmain一致、両単元のrecommendedPlanが利用不能ガード以外一致、隔離archiveでpractice→design→parent生成後に全6HTML不変を独立確認。probeの外部font CSS GET24件は遮断、POST受信・ページ例外0。全suiteは公開CDN GET・模擬通知を含むので外部要求0とはしない。

統括がremote lease・main・元PR10 HEADを再確認し、通常pushで132f9f5を既存PR10へ反映。比較先をmainへ更新、open/draftを読戻し確認した。新製品PR・mainへのpush/mergeなし。

## 検証の限界と次の一手

旧validator試験は、現在の合成normal eventから任意questionVersionを除いた旧形状の確認。現在のJSON envelopeや保存先が旧HTMLとそのまま互換という意味ではなく、製品の自動移行は行わない。

クラウドrunning/connectedを確認。独立checkoutと検証済みvenvを手動準備し、依存hash一致を確認した。自動snapshot引継ぎ成功とは扱わない。合成データのみ。Chromiumでの結果をSafari・iPad実機・本人試用・学習効果・公開成功とはしない。

既知の外部Workers Builds失敗はローカルQAと別に扱う。再デプロイ・設定変更なし。日次件数修正は統合受入後に同じPR10で、共通adaptiveと4生成先、理科/トップの対象境界を確定して進める。D02の実資料保管・実接続は未決。

証拠は [evidence](../evidence/2026-11-14-rev-current-base/) に保存する。
