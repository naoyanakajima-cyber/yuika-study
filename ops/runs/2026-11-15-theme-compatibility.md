# 2026-11-15 THEME-MVP：現行画面と保存境界への適合

**候補保存済み、製品受入は未完。** [既存draft PR12](https://github.com/naoyanakajima-cyber/yuika-study/pull/12)に c81fb6b3a7e9c5c6c5d42431afe1d13a73c780d3 を通常fast-forward pushした。本人の好みで標準/鎌倉を切り替えつつ、現在の学習処理と保護者の合成確認を同じ候補で使えるようにする。mainへのマージ・公開ではない。

## 基点・実際の分担

運用正本b7e142a3a3f50fdfa3033a92e778c2b37c3e0ee9の指定4文書を読取、managed cloud provider/running/connected/currentを確認。lease cycle-20261115T000247Zを通常push後、PdM pdm_theme_compatibility → PrM root/coordinator → Engineer engineer_theme_compatibility → 独立Reviewer/QA qa_theme_compatibility の順に進めた。子3名、同時実装1件、子pushなし。

前回教材試し解きは既存PR11 ee51e68へ保存済み。次の独立仕事として、旧テーマPR12 57171ad9cab02fec6a080ecbe317fe11d3f51dcf（base edad8065c1f2b726e61c5cf405f8d9ff6d807480）と現main86514eda054a5a2e09204df3a0668e40624c16deを照合した。旧テーマのlocalStorage直接利用と新しい保存境界/Design Cの差を静的に確認し、[C1〜C8の範囲](../../docs/product/theme-main-compatibility.md)を採択。静的差異の段階で操作不具合を再現済みとは呼ばない。

## 実装

独立checkoutで旧PR12履歴を第一親、mainを第二親とするtopic mergeを保存。README/鎌倉HTML競合はmainを残してテーマ部分だけを適合した。PR10/11/22の未マージ差分は取り込まない。mainとの差分はREADME、theme-spec、kamakura-review.html、check_all.sh、theme_review.pyの5ファイル。

テーマ専用キー/standard|kamakuraは維持し、読書きをYuikaParent.storageへ移した。通常モードは従来の専用キー、親モードはセッション、sessionStorage拒否時は既存一時メモリに分離。通常localStorageへのfallbackなし。鎌倉選択時のみbg/subject/subject-text等の色と限定CSSを現Design Cへ合わせる。標準の共有asset、問題・採点・選定・記録形式、既存学習script、親runtime、通知block、CSP、対象外5HTMLを維持した。

依存は検証済みvenvの手動再利用。main requirementsとの一致を確認し、ignoreされる.venv directory内にbin/lib/include/pyvenv.cfgのsymlinkを置いた。自動snapshot引継ぎ成功・platform定時実行完了とは扱わない。

## 2試行上限と未完の必須検証

Engineerのtheme試験は初回、JSON出力を旧直下eventsとして読んでKeyError。2回目はenvelope/payloadへ適合したがformatをyuika-study-prototype-recordsと誤記してassert失敗。現mainの定数yuika-review-prototype/formatVersion1/payload.eventsへ修正保存したが、同原因2試行上限に従い3回目は実行しない。製品の出力処理はmainと同一で、今回の原因はテスト移行の不整合。

両回とも15問の各切替/入力/選択/ヒント/採点・状態保持・色/操作領域・parent/records/home入口まで通過したが、全theme成功とは扱わない。最終format期待値、後半の未知値/read-write例外/回復/別画面往復等は未完。runnerには現main22suiteを保持してthemeを追加したが、同じ失敗caseを含む **全必須23suiteは今回未実行**。assertやsuiteを省略して成功にしない。

Engineerの別の未到達parent/一時メモリ/print probeは1回成功した。実装者の自己検証であり独立QAとは区別。export経路は実行しない。

## 限定独立レビュー・QA

固定clean c81fb6bで静的検査初回成功。旧PR12/mainの両祖先・5files限定、mainの既存embedded scripts4件/親runtime/通知/CSP/共有asset/他HTML一致を直接確認。最終export期待値は現main定数/packetと読み取り照合したが、動的成功の代わりにはしない。

限定probeは **14検査、文字色68組、最低contrast5.010**。通常標準の6要素のcomputed色/背景/font-size/line-heightがmainと一致し、鎌倉差分と標準復帰を確認。保護者モードのhome/quiz/feedback/result/保護者ノート/recordsを実UIで両テーマ遷移し、同じrun/入力/ヒント/結果/学習DOMを保持。親セッション内の5合成回答・テーマ復元、終了時通常テーマへ戻る操作、sessionStorage拒否時の1合成回答/テーマの一時メモリ保持とreload消去を確認。通常のテーマ・元記録・他単元・通知設定は不変。

独立probe初回はQAのevaluate式が登録したspy関数を返し、Playwrightがそれを実行して通知spyを1加算したため停止。返値のないcallbackに直した2回目で成功。製品編集なし。Engineerのexport期待値とは別原因で、両回ともexport0、同原因3回目なし。初回ログとscriptも保存した。

テーマ操作中のresource追加/再enqueue、POST到達、pageerrorは0。既存Google Fonts GETは遮断し別計数。外部要求全体0やwebfont読込み成功とはしない。768×1024の親モード6画面×両テーマ12画像を独立QAが目視。rootもhome2画像で色差と親バナーを確認したが、独立QAの追加件数には算入しない。通常画面全体のpixel一致、長図全体、focus/print全体の独立確認、実機Safari/iPad、本人嗜好・学習効果・公開動作は未確認。

判定はpartial_review_passed / required_checks_pending。限定範囲で新たな製品不具合は観測なしだが、必須検証未実施の受入blocker2件を維持。旧57171adの4suite成功を新候補へ転用しない。

## 保存する証拠と次の一手

[証拠](../evidence/2026-11-15-theme-compatibility)にPdM/PrM/Engineer/独立QA、実行ログ・script・結果JSON・合成画像・初回失敗とSHA256を保存。未実行準備probe、比較用checkout、pycacheは公開証拠外。次回は固定c81fb6b・remote leaseを照合し、修正済みthemeと全必須23suiteを優先して独立QAを完了する。これは新CEO承認待ちではなく、実装チームの検証残件。成功するまでCEO試用準備完了としない。

新規製品PRなし。#10/#11/#12の枠を維持（#12は検証継続中）、追加既存#22、旧#4〜#8/運用#9/#13は別枠。新CEO返答0、D05方向性採用を本番権限に拡張せず、D02未決。実データ取得、本番merge/公開/手動deploy/実通知/課金/Secrets/権限/共有変更なし。旧停止中の自律更新は再開しない。既存PR12/9 attachは空応答で成功未確認。通常の成果・障害・未検証事項は朝夕CEOチェックへ集約し、毎時通知は不要。

## 外部状態

現在候補c81fb6bのWorkers Builds: yuika-studyは2026-11-15T00:15:40Zにfailure（https://github.com/naoyanakajima-cyber/yuika-study/runs/132638525283）。原因未調査、手動再実行/デプロイなし。限定QA成功とは区別する。PR12を既存履歴のままmain基点へ更新し、PR12/9本文を検証継続中・必須検査未完へ更新。別読戻しで本文一致、open/draft/unmerged、PR12 HEAD c81fb6b/base mainを確認しpr-readback.jsonへ保存した。

## 終了保存

独立メタデータレビューqa_theme_compatibilityが旧133runs・他11ticket・権限/判断の保持、証拠とPR読戻しの一致を確認。新runのCEO待ち分類を[10,11]、予約済み製品PR枠[10,11,12]、検証待ち[12]に分離し再読確認した。メタデータ整合性passを製品受入成功と混同しない。THEME-MVPはblocked/required_checks_pendingのまま次回へ引き継ぐ。

最終保存時刻 2026-11-15T00:22:48.183464+00:00。この保存commitでleaseをnullへ戻す。製品固定候補c81fb6bは変更せず、次回は必須23suiteと未完QAを最優先する。通常通知はNO_UPDATE。
