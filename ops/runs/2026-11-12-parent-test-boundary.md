# 保護者が復習を試す際の検証境界を安定させる（2026-11-12）

本人の学習記録や通知へ触れずに保護者が試用できることを確かめるため、前回未解決だった模擬通知テストを切り分けた。通常アプリ起動後にテストデータを投入すると、待機していた通常モードの送信処理がそのデータを拾う競合を再現した。準備ページを通知処理のない同一originのHTMLへ変更し、最初のアプリ起動から保護者モードにするテスト修正を保存した。

## 成果と保存先

- [候補commit df791c0](https://github.com/naoyanakajima-cyber/yuika-study/commit/df791c07c0071921e22ae667e5230f8fd99ed782)、branch `codex/parent-test-boundary-20261112`。変更は `tests/parent_mode.py` の15行追加/4行削除のみ。製品runtime・採点・出題・保存形式・CSPは変更なし。
- 正本4文書を同じ最新commit `fddf0a9a0f37cb931dcb22a7dcdf8dfee57ba11c` から確認。クラウドrunning/currentを確認し、lease通常push成功後に分担。PdM `pdm_parent_test_scope` → PrM `root` → Engineer `engineer_parent_test_boundary` → 別担当QA `qa_parent_test_boundary`。
- 独立checkoutで修正。統括がleaseを再確認し専用branchへ通常push。子のpushなし。既存準備済みvenv/Chromiumを手動参照し、setup/依存導入なし。自動引き継ぎ成功の主張なし。
- [運用draft PR #9](https://github.com/naoyanakajima-cyber/yuika-study/pull/9) の運用branchに、適用可能な `ops/evidence/2026-11-12-parent-test-boundary/parent-mode-fixture.patch` と仕様・検証証拠を保存。**製品用draft PRの作成・更新はしていない。**

## 検証と限界

独立QAは実際の同一origin Web Lockで通常起動のflushを待機させ、合成pending投入後に解放した。模擬要求1件のfetch時点は `YuikaParent.active=false`、保護者モード入場前だった。別の新規contextでは、通知処理のない準備ページ→保護者モード入場/再読込/online/visibility/保留登録/接続form/再送で要求0・本人raw不変を確認した。最初のprobeは閉じたdetails内の操作でtimeoutし、開いて操作する修正後の2回目が成功。3回目のprobe試行なし。

前回05:14の失敗には発生段階のログがなく、その一件の原因を遡って確定したとは扱わない。今回証明したのは同じ準備手順に存在する具体的な競合と、その除去である。callsを消したり要求を除外せず、既存assert・保留データの入場前存在・記録保持・終了後の通常模擬送信を維持した。診断にテスト段階と要求元URLも追加した。

Engineerは重点parent_modeを1回実行し成功。独立QAは固定候補 `df791c07c0071921e22ae667e5230f8fd99ed782` のclean状態で `bash scripts/check_all.sh` を1回実行し、**全21スイート成功、終了コード0、163秒**。parent_modeは25秒、Worker9/9、bootstrap13/13。実行前後HEAD不変・clean。全体再試行なし。前回8100285の20/21失敗記録は保持し、成功へ読み替えない。Chromium・合成データ・模擬APIのみ。実機iPad/Safari/WebKit・CEO本人の試用は未確認。

## 途中で変わったPR状態と次の一手

検証中の06:14:55 UTCに、別の操作で[PR #25](https://github.com/naoyanakajima-cyber/yuika-study/pull/25)がマージされたことをAPIで確認した。最終HEADは `042c55dd04a285277dc3dfa9dd296f161283e809`、mainは `25cad059f73cdca4cd805825c84e6619074b37c4`。両treeは `998f7dad2de007ce8bc70293388f88f3114b14d4` で一致。**今回のテスト修正df791c0はmainに含まれず、全21成功はその候補の結果。** 本運用はマージ・公開しておらず、外部mergeを新しいCEO返答/権限として取り込まない。

既存の製品承認待ちは#10/#11/#12の3件、追加open製品draftは#22。PR25をopen待ちに数えず、未提出の今回テスト修正1件も明示する。旧#4と運用#9/#13は上限外。閉じたPR25を変更せず、上限を迂回する新規製品PRを作らず、候補とpatchを既存運用draftへ保全する方針をPdM/PrMで確認した。

技術修正・独立QAは完了、製品用の提出経路は保留。既存待ちの整理で枠が空くか提出先が指定されたら、保存済みpatch/commitを対応draftへ載せる。新しい差分・具体的な不具合・CEO試用フィードバックがなければ同じQAを反復しない。学習上は苦手復習の使い勝手が最優先、合成教材追加が次、テーマ拡張は低優先を維持する。D02実資料/回答保存先は未決。

PR25と運用PR9のタスクattachを各1回呼び出したが応答せず中断、成功未確認。新規PR0、実通知/私的データ取得/本番操作/課金/Secrets・権限変更0。通常報告は朝夕CEOチェックへまとめる。判断はチケットID `REV-RECONCILE` を添えてこの運用を設定した元チャットへ返答し、担当が実際に読み台帳へ記録するまではworkerへ伝達済みと扱わない。
