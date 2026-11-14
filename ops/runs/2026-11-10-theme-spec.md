# THEME-SPEC 開発サイクル（2026-11-10 JST）

## 成果と学習上の価値

好きな時代の見た目を選び、毎日の復習画面を開くきっかけを増やすため、
鎌倉単元の「標準／鎌倉」切替を仕様にした。途中の回答・出題順・採点・記録を保ち、
気が変わったときは同じ操作で標準へ戻せる。新しい問題や特定作品の画像は追加しない。

- 成果：`docs/product/theme-spec.md`、受入条件T1〜T11。
- commit：`62d9c20af5cacbc7f5174c28f4f26b84b0794150`。
- 保存先：[既存draft PR #9](https://github.com/naoyanakajima-cyber/yuika-study/pull/9)。新規PRは作成していない。
- THEME-SPECは文書成果として完了。製品のテーマ切替は未実装・未検証。
- 次はTHEME-MVPで、鎌倉画面のみの変更として実装・独立QA・draft PRへ進む。

## 実行権・既存作業・分担

2026-11-09 17:07 UTCにprovider=cloud、running/connected、最新観測、network enforcedを確認。
正本4ファイルを同一commit `c5e59bc2bd8ece358790ffb91649dbee7034b0d8` から読み、既存PR #4〜#11を照合。
mainは `d526d65fbae116f834d14ad994a27bc50ca23b62` のまま。PR #10と#11はdraft・未マージ、
新しいCEO判断は読み取っていない。途中チケットはなく、前回の次の仕事THEME-SPECを選んだ。

leaseを通常pushで取得し、独立checkout `/workspace/yuika-theme-spec-20261110` で仕様を作成。
統括が実行権を再確認して、仕様commitを運用branchへfast-forwardし保存した。
これは運用文書の統合であり、mainへの本番マージは行っていない。
本サイクルでは依存導入・手動Install・snapshot再診断は不要だった。
クラウド上での実行確認を、自動snapshot引き継ぎ成功やスケジュール完了の証明とは扱わない。

- PdM `pdm_theme_spec`：既存画面を読み、最小対象、状態、保存、見た目、受入条件を作成。
- 統括/PrM `root`：鎌倉画面限定とデータ分離を確認。権限内の仕様として承認し、最終状態・適用範囲を補足。
- Engineer `engineer_theme_feasibility`：読取専任で技術境界と配色を調査し、仕様の実装可能性を確認。ファイル編集なし。
- 独立Reviewer/QA `qa_theme_spec`：文書・実コードを直接照合し、独立の色計算と静的チェックを実施。ファイル編集なし。
- 子は3名、実装は0件。commit/pushは統括だけが実行。

## 確認した重要な設計判断

既存の `main.innerHTML` 再描画は未送信回答を消しうるため、テーマ操作をmain外に常設し、
root属性と選択状態だけを変更する。結果表示には通知enqueueの副作用があるので、
テーマ切替からrender/go/quiz/resultを呼ばない。

専用キー `yuika-ui-theme-kamakura-v1` に標準/鎌倉の値だけを保存する。
保存失敗は専用statusへ出し、学習記録の破損警告やblocked状態を上書きしない。
未知値は標準へfallbackするが、起動だけで既存値を削除・上書きしない。
PR #10のhome/quiz変更にテーマUIを混ぜず、後の統合時の衝突を抑える。

## 今回実施した検証

| 検証 | 結果 |
| --- | --- |
| EngineerのPythonによる候補色のsRGB contrast計算 | 成功 |
| 独立QAによる別計算と数値照合 | exit 0・一致 |
| T1〜T11一意、主要保護条件、対象コード・既存テスト不変の静的チェック | exit 0 |
| `git diff --cached --check` | exit 0 |
| 最終commitとレビュー済み文書の差分照合 | 状態1行とcontrast適用範囲の補足のみ |

通常背景4色上のmutedは最低4.975、白/primaryは8.020。gold上のmuted等は4.5未満、
line/whiteは1.67、rose/primaryは1.305であるため、使用禁止・装飾限定・focus間隔等の制約を仕様へ反映。
新テーマと新規操作領域に基準を適用し、未変更の標準画面全体の修正を今回の範囲へ広げない。
最終文書SHA256：`7891212ae5c3dab00da799529e209b5bea7fba402a22eda9008436b926edb372`。

配色計算は候補値の数値検証であり、実画面の可読性テストではない。
アプリ実装、ブラウザーテスト、実機iPad/Safari確認は今回未実施。
768×1024の画面確認、実際の配色、学習中切替、記録保持、通知遮断、印刷は次回実装の受入条件。
既存アプリ・依存・CI・既存assert・CSPは変更していない。

## 次の一手と判断待ち

THEME-MVPはこの仕様を基に、最新main・既存PR・台帳を再取得し、製品基点を記録して着手する。
現時点の候補基点は #7 の `edad8065c1f2b726e61c5cf405f8d9ff6d807480`。
#10/#11を未承認のまま統合しない。実装後は既存応仁・鎌倉・cloud_previewと新規themeテストを独立QAが検証する。

製品PRのCEO判断待ちは引き続き2件（#10、#11）。D01〜D04はpendingを維持。
THEME-MVPのdraft PRが追加されれば上限3件となるため、その後の新規製品実装は止め、
CEO判断または既存PRの必要な修正を待つ。仕様完了をマージ・公開の承認に読み替えない。
通常の成果報告は朝夕チェックへまとめ、今回は外部通知を出さない。

私的回答・教材写真・メール/Driveを取得せず、実通知、本番マージ・公開・デプロイ、
Secrets・課金・権限・共有範囲・スケジュールの変更は行っていない。旧自律更新は停止状態のまま。
