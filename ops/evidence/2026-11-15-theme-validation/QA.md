# cycle25 独立QA：テーマ互換性と図の可読性

担当 qa_theme_compatibility、実装担当 engineer_theme_compatibilityとは別。**最終固定 b416d3c08a0d3952e5f0153fdc691d6fa0e492b7 は、合成試用候補として独立QA合格。** 本人試用・学習効果・実機互換性・マージ/公開の承認ではない。PR/台帳への保存と終了処理は統括が行う。

## 最終候補で実行した検証

別の独立checkout /workspace/yuika-theme-qa-final-20261115で、01:14:07.450947 UTC開始、01:18:34.202055 UTC終了。`bash scripts/check_all.sh` を初回1回、267秒、**全23suiteがexit0**。前後HEADはb416d3c、dirtyは空。suite別exit/秒数はfinal-result.json、完全stdout/stderrはcheck-all-attempt1.log。最後の独立図確認後01:20:08 UTCもHEAD/cleanを再確認した。

theme検査の全T1〜T11が完了し、前回未完だったJSON envelope（yuika-review-prototype、formatVersion1、payload.events一致、テーマキー非混入）、別画面往復、未知3値を起動時上書きしないこと、get例外の標準起動、set例外時の画面内適用・学習警告保持・保存回復も成功。15合成回答の入力/選択/ヒント/採点/結果で状態・DOM・保存不変、44px/8px・キーボード・focus3:1・本文4.5:1・reduced-motion・print・親セッション/一時メモリも通過した。

図の独立probeも初回成功。通常モード768×1024でstandard/kamakura×screen/printの4状態を確認し、4画像を目視した。「将軍」「執権（北条氏）」の13px白文字と新背景rgb(143,79,60)の実computed contrastは**6.265720821251096:1**。全10個の白文字ノードの最小値は4.977109637969801。対象2枠以外のfill、全ラベル、文字サイズ、図のDOM・幾何、標準復帰を維持。print時はテーマUI非表示・body白背景、画面へ戻す操作も成功。POST到達/pageerror0。これは画面上のprint mediaであり実プリンター試験ではない。

## 発見した問題と2候補の区別

最初のc81fb6bは01:05:55.806551〜01:11:07.194227 UTC、312秒で全23suite初回成功。その後、未確認のC6長図・長文だけを独立probeで追加確認した。親モード768×1024で組織図・仏教比較表・最長解説54025-38（81文字）の両テーマ/標準復帰、内容・寸法・行間・横overflow・切替操作到達を確認し、6画像を目視。最長問題は合成fixtureで選び実start/check/nextを用いたため、選定エンジン試験とは呼ばない。

そこで「将軍」「執権」の白13px文字/背景#b57c65が両テーマで**3.479281384346954:1**と判明。現mainを別fresh contextで表示して同じfill/fontとtree関数の完全一致を確認した。既存の問題だがC6未達として報告し、c81を受入済みにはしなかった。3状態×2ラベルの6観測は対象2箇所の問題である。

PrMはC6を維持し、C2の標準表示維持に「当該2枠の背景色改善のみ」の明示例外を採択。Engineerが別checkoutで修正して固定b416d3cを提出。新しい製品変更と実際の未達を根拠に、新HEADで23suiteを再実行した。無変更の成功検査の反復でも、旧HEAD成功の転用でもない。各固定HEADの全suite・各補足probeはそれぞれ初回1回で、今回ハーネス修正/再試行なし。

修正前の詳細は /tmp/yuika-cycle25-qa-baseline.md と /tmp/yuika-cycle25-qa/c81-QA.md。修正後の証拠は /tmp/yuika-cycle25-qa-final。旧候補のC6未達とログ・画像も保持する。

## 差分・受入条件の確認

b416d3cとc81との差分はREADME、theme-spec、鎌倉HTML、theme検査の4ファイル47行。HTMLはコメントと対象CSSの2行を除去するとc81と完全一致。既存図DOM/tree・白文字・位置・線・aria-label・学習scriptを変更せず、テスト39行は追加のみで既存assert削除なし。mainの4既存embedded scriptも完全一致。

| 条件 | 判定と証拠 |
| --- | --- |
| C1 | 範囲・既存履歴・main保全。旧候補の静的境界と今回の厳密差分確認。未マージPR10/11/22の取込みなし。 |
| C2 | 明示された2枠色の例外内で合格。共有asset/他画面/他fill不変、操作・標準復帰・print・実色確認。 |
| C3 | 新HEADのtheme全検査で通常保存、未知値、read/write例外、回復まで成功。 |
| C4 | 新HEADのparent/theme全検査で通常領域保護、親セッション・終了・一時メモリ。旧同挙動の限定証拠も参照。 |
| C5 | 新HEADで同run入力・ヒント・採点・結果・記録・DOM保持、通知spy0を確認。 |
| C6 | 合成Chromiumの対象範囲で合格。旧6画面＋今回長文/表/図と新候補の対象図修正を確認。全図や実機全体の保証はしない。 |
| C7 | 新固定clean HEADで必須23suite全成功。script/CSP/問題・採点/保存schema/共有境界を維持。 |
| C8 | この独立証拠は保存準備済み。統括のPR/台帳commit・push・読戻しが済むまでは運用完了としない。 |

cycle24のc81に対する限定14検査・文字色68組（最低5.010）・静的検査は、既存証拠として明示して参照する。今回の実行件数には加算しない。新HEADのHTML変更が2枠のCSSだけであることを独立に確認し、他の実行挙動を変える変更がないことを根拠に利用する。新HEADでも全必須検査は改めて実行した。

## 通信と限界

通知検査はmock、テーマ/補足は想定外通信を遮断。theme suiteではfont GET15件を遮断し、想定外外部要求/POST到達/pageerror0。全必須suiteには公開JS取得があるため全体通信0とはしない。フォントはfallback表示でwebfont成功ではない。依存は既存検証済みvenvの手動再利用で、自動snapshot引継ぎ成功とはしない。

Chromiumのみ。実機Safari/iPad、native zoom、本人の好み・学習効果、実データ、実プリンター、公開環境は未検証。すべての画面・教材状態のpixel一致や完全なアクセシビリティ監査を主張しない。実メール/Chat・本番merge/deploy・課金・Secrets/権限変更・pushはこのQA担当では実施していない。外部Workersの結果はクラウドQA成功と別に記録する。
